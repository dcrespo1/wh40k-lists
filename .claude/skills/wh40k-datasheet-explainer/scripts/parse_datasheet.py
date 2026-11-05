#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pdfplumber>=0.11"]
# ///
"""Parse a 40k army-list PDF export into structured JSON.

Usage: uv run parse_datasheet.py <file.pdf> [out.json]

Handles browser print-to-PDF exports (e.g. warmind.online printed from Safari)
whose digits are drawn with Type 3 fonts that have no text mapping: digits are
recovered from their glyph names, which are stable across weights of Apple's
San Francisco font. Any glyph it can't decode becomes "?" and is reported, so
the output is never silently wrong.

Output: {"army": {...}, "units": [...], "rules_text": "...", "warnings": [...]}
Exit code 0 = clean, 2 = parsed with warnings (check those values against page
images), 1 = could not parse.
Needs pdfplumber (declared above, so `uv run` installs it).
"""
import sys, re, json, logging, collections

logging.disable(logging.WARNING)
try:
    import pdfplumber
    from pdfminer import pdffont
    from pdfminer.pdftypes import resolve1
except ImportError:
    sys.exit("Missing pdfplumber. Run this script with `uv run` (installs it automatically), or: pip install pdfplumber")

# Glyph names for digits in Apple's SF font as Safari embeds it (verified on two
# separate warmind.online exports). Extend this if another source uses other names.
GLYPHS = {"g529": "0", "g52B": "1", "g52D": "2", "g52E": "3", "g52F": "4",
          "g531": "5", "g532": "6", "g534": "7", "g535": "8", "g536": "9"}
UNKNOWN = collections.Counter()

_init = pdffont.PDFType3Font.__init__
def _patched_init(self, rsrcmgr, spec):
    _init(self, rsrcmgr, spec)
    self._gnames = {}
    enc = resolve1(spec.get("Encoding"))
    diffs = resolve1(enc.get("Differences", [])) if isinstance(enc, dict) else []
    code = 0
    for d in diffs or []:
        if isinstance(d, int):
            code = d
        else:
            self._gnames[code] = getattr(d, "name", str(d)); code += 1
pdffont.PDFType3Font.__init__ = _patched_init

_to_unichr = pdffont.PDFType3Font.to_unichr
def _patched_to_unichr(self, cid):
    try:
        u = _to_unichr(self, cid)
    except Exception:
        u = ""
    if u in ("", "\x00"):
        g = getattr(self, "_gnames", {}).get(cid, f"code{cid}")
        if g in GLYPHS:
            return GLYPHS[g]
        UNKNOWN[g] += 1
        return "?"
    return u
pdffont.PDFType3Font.to_unichr = _patched_to_unichr

FOOTER = re.compile(r"\| Battle reference|^\d+ of \d+ \d+/\d+/\d+|^https?://")
UNIT_HDR = re.compile(r"^(?P<name>.+?) (?P<pts>\d+) pts$")
PART_HDR = re.compile(r"^(?P<name>.+?) (?P<role>LEADER|BODYGUARD) (?P<pts>\d+) PTS$")
STAT_HDR = re.compile(r"^M T SV( INV)? W LD OC( FNP)?$")
WPN_HDR = re.compile(r"^(RANGED|MELEE) WEAPONS RANGE A (BS|WS) S AP D$")
VAL = r"[\dD?+\-▲▼*\"]+|-|N/A"
WPN_ROW = re.compile(
    rf"^(?P<name>.+?)×(?P<count>\d+)\s+(?P<range>Melee|[\d?]+\")\s+(?P<A>{VAL})\s+"
    rf"(?P<skill>{VAL})\s+(?P<S>{VAL})\s+(?P<AP>{VAL})\s+(?P<D>{VAL})$")
SECTION = ("ABILITIES", "KEYWORDS", "FACTION KEYWORDS", "WHAT EACH MODEL CARRIES",
           "CONFERRED WEAPON KEYWORDS", "BATTLEGEAR", "ENHANCEMENTS")


def lines_of(pdf):
    out = []
    for page in pdf.pages:
        for ln in (page.extract_text() or "").splitlines():
            ln = ln.strip()
            if ln and not FOOTER.search(ln):
                out.append(ln)
    return out


def parse(path):
    with pdfplumber.open(path) as pdf:
        lines = lines_of(pdf)
    warnings = []
    # The header can wrap over several lines before "ARMY LIST"
    stop = lines.index("ARMY LIST") if "ARMY LIST" in lines else 2
    army = {"name": lines[0] if lines else "", "header": " ".join(lines[1:stop])}
    parts = [p.strip() for p in army["header"].split("·")]
    for p in parts:
        if re.search(r"\d+/\d+ pts", p): army["points"] = p
        elif "DP" in p: army["detachment_points"] = p
        elif p.startswith(("Mustered", "Battle-legal")): continue
    if len(parts) >= 2:
        army["faction"] = parts[0]
        army["detachments"] = [d.strip() for d in parts[1].split("+")]
        if len(parts) >= 3: army["battle_size"] = parts[2]
        disp = [p for p in parts[3:] if not re.search(r"pts|DP|Battle-legal|Mustered|^\d", p)]
        if disp:
            army["disposition"] = disp[0]
            army["disposition_options"] = [d.strip() for d in disp[0].split(" or ")]

    try:
        start = lines.index("DATASHEETS") + 1
    except ValueError:
        return army, [], "", ["No DATASHEETS section found"]
    end = lines.index("RULES AND STRATAGEMS") if "RULES AND STRATAGEMS" in lines else len(lines)
    body, rules_text = lines[start:end], "\n".join(lines[end + 1:])

    units, unit, part = [], None, None
    stat_cols, wpn_kind, section, last_wpn = None, None, None, None

    def new_part(name, role=None, pts=None):
        p = {"name": name, "role": role, "points": pts, "models": [], "weapons": []}
        unit["parts"].append(p)
        return p

    for ln in body:
        m = UNIT_HDR.match(ln)
        if m and not PART_HDR.match(ln):
            unit = {"name": m["name"], "points": int(m["pts"]), "parts": [],
                    "abilities": [], "keywords": "", "faction_keywords": "", "other": {}}
            units.append(unit)
            part, stat_cols, wpn_kind, section = None, None, None, None
            continue
        if unit is None:
            continue
        if re.fullmatch(r"(squad )?[A-Z]", ln) and part is None:   # "squad A" / "A" label
            unit["label"] = ln; continue
        m = PART_HDR.match(ln)
        if m:
            part = new_part(m["name"], m["role"].lower(), int(m["pts"]))
            stat_cols, wpn_kind, section = None, None, None
            continue
        if STAT_HDR.match(ln):
            stat_cols = ln.split()
            if part is None: part = new_part(unit["name"])
            section, wpn_kind = "stats", None
            continue
        m = WPN_HDR.match(ln)
        if m:
            wpn_kind, section = m[1].lower(), "weapons"
            continue
        if ln in SECTION:
            section, wpn_kind = ln, None
            continue

        if section == "stats" and stat_cols:
            toks = ln.split()
            vals = toks[-len(stat_cols):]
            name = " ".join(toks[:-len(stat_cols)])
            if len(toks) <= len(stat_cols) or not re.match(r"[\d?]", vals[0]):
                warnings.append(f"{unit['name']}: stat row not parsed: {ln!r}")
            else:
                part["models"].append({"name": name, **dict(zip(stat_cols, vals))})
            continue
        if section == "weapons" and wpn_kind:
            m = WPN_ROW.match(ln)
            if m:
                w = {"name": m["name"].lstrip("➤ ").strip(), "type": wpn_kind,
                     "count": int(m["count"]), "range": m["range"], "A": m["A"],
                     ("BS" if wpn_kind == "ranged" else "WS"): m["skill"],
                     "S": m["S"], "AP": m["AP"], "D": m["D"], "keywords": [], "notes": []}
                w["profile_of"] = w["name"].split(" - ")[0] if " - " in w["name"] else None
                part["weapons"].append(w); last_wpn = w
            elif ln.startswith("[") and last_wpn is not None:
                last_wpn["keywords"] += re.findall(r"\[([^\]]+)\]", ln)
            elif ln.startswith(("▲", "▼")) and last_wpn is not None:
                last_wpn["notes"].append(f"{ln} (modifier already applied to marked value)")
            elif re.search(r"×\d+", ln):
                warnings.append(f"{unit['name']}: weapon row not parsed: {ln!r}")
            continue
        if section == "ABILITIES":
            unit["abilities"].append(ln)
        elif section == "KEYWORDS":
            unit["keywords"] += (" " if unit["keywords"] else "") + ln
        elif section == "FACTION KEYWORDS":
            unit["faction_keywords"] += (" " if unit["faction_keywords"] else "") + ln
        elif section:
            unit["other"].setdefault(section.lower(), []).append(ln)

    for u in units:
        u["abilities_text"] = "\n".join(u.pop("abilities"))
        if not u["parts"]:
            warnings.append(f"{u['name']}: no stat lines or weapons parsed at all")
        for p in u["parts"]:
            if not p["models"]:
                warnings.append(f"{u['name']}: no stat line found for {p['name']}")
            for row in p["models"] + p["weapons"]:
                if any("?" in str(v) for k, v in row.items() if k not in ("name", "notes", "keywords")):
                    warnings.append(f"{u['name']}: undecoded value in {row['name']}")
    if UNKNOWN:
        warnings.append(f"Undecoded glyphs {dict(UNKNOWN)}: read those values from page images")
    return army, units, rules_text, warnings


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    try:
        army, units, rules_text, warnings = parse(sys.argv[1])
    except Exception as e:
        sys.exit(f"Can't parse {sys.argv[1]}: {e}")
    data = {"army": army, "units": units, "rules_text": rules_text, "warnings": warnings}
    out = json.dumps(data, ensure_ascii=False, indent=1)
    if len(sys.argv) > 2:
        import os
        os.makedirs(os.path.dirname(os.path.abspath(sys.argv[2])), exist_ok=True)
        open(sys.argv[2], "w").write(out)
        n_w = sum(len(p["weapons"]) for u in units for p in u["parts"])
        n_m = sum(len(p["models"]) for u in units for p in u["parts"])
        print(f"{len(units)} units, {n_m} stat lines, {n_w} weapon profiles -> {sys.argv[2]}")
        for w in warnings:
            print("WARNING:", w)
    else:
        print(out)
    sys.exit(1 if not units else 2 if warnings else 0)


if __name__ == "__main__":
    main()
