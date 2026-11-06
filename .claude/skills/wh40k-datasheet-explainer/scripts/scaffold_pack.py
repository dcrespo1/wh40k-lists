#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Turn parse_datasheet.py output into a pack JSON for build_cards.py, with
every stat and weapon prefilled. Claude then fills only the prose fields
marked "TODO" (role, abilities, watch, plan, reminders, phases) and never
retypes numbers. The plan's matchup table (mission names for each opponent
disposition) is prefilled from assets/disposition-matrix.json.

Usage: uv run scaffold_pack.py parsed.json pack.json
Identical duplicate units (e.g. Intercessor Squad A and B) are merged into one
card with "×2 (A & B)".
"""
import json, sys

import os

STAT_ORDER = ["M", "T", "SV", "INV", "W", "LD", "OC"]
MATRIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "disposition-matrix.json")


def scaffold_plan(army):
    """Game plan skeleton with the matchup table prefilled from the disposition
    matrix: for each disposition the user might pick, what both players play
    against each opponent disposition. Only the tips are left as TODO."""
    m = json.load(open(MATRIX))
    known = m["missions"]
    opts = army.get("disposition_options") or [army.get("disposition", "")]
    opts = [o for o in opts if o]
    plan = {
        "disposition": army.get("disposition", "") or "TODO ask the user",
        "summary": "TODO one line: how this list wins",
        "sections": "TODO Deployment + Scoring tips from references/strategy-guide.md",
        "note": "Mission names from the disposition matrix; exact scoring is on your mission card. Share it for tailored tips.",
    }
    if len(opts) > 1:
        plan["choice"] = ["TODO which disposition to pick and why (strategy-guide.md section 8)"]
    matchups = []
    for mine in opts:
        if mine not in known:
            continue  # unknown disposition name: no matrix row, say so in the plan
        matchups.append({"yours": mine, "rows": [
            {"opponent": opp, "you_play": known[mine][opp], "they_play": known[opp][mine],
             "tip": "TODO tip vs this opponent (strategy-guide.md section 8)"} for opp in known]})
    if matchups:
        plan["matchups"] = matchups
    return plan


def card_stats(part):
    rows = []
    for m in part["models"]:
        other = f"FNP {m['FNP']}" if m.get("FNP") else ""
        rows.append([m["name"]] + [m.get(k, "—") for k in STAT_ORDER] + [other])
    return rows


def card_weapons(unit):
    rows = []
    multi = len(unit["parts"]) > 1
    for p in unit["parts"]:
        for w in p["weapons"]:
            name = w["name"] + (f" ×{w['count']}" if w["count"] > 1 else "")
            if multi and p["role"] == "leader":
                name += f" ({p['name'].split()[0]})"
            kw = ", ".join(k.title() for k in w["keywords"])
            if w["notes"]:
                kw += (" · " if kw else "") + "; ".join(w["notes"])
            rows.append([name, w["range"], w["A"], w.get("BS") or w.get("WS"),
                         w["S"], w["AP"], w["D"], kw, "TODO good vs"])
    return rows


def signature(u):
    return json.dumps(u["parts"], sort_keys=True)


def main():
    parsed = json.load(open(sys.argv[1]))
    army = parsed["army"]
    groups = []
    for u in parsed["units"]:
        for g in groups:
            if g[0]["name"] == u["name"] and signature(g[0]) == signature(u):
                g.append(u); break
        else:
            groups.append([u])

    units = []
    for g in groups:
        u = g[0]
        name, pts = u["name"], f"{u['points']} pts"
        if len(g) > 1:
            labels = [x.get("label", "").replace("squad ", "") for x in g]
            name += f" ×{len(g)}" + (f" ({' & '.join(labels)})" if all(labels) else "")
            pts += " each"
        units.append({
            "name": name, "pts": pts, "role": "TODO one line: what it's for",
            "stats": [r for p in u["parts"] for r in card_stats(p)],
            "weapons": card_weapons(u),
            "abilities": [["TODO", "TODO plain-language ability"]],
            "watch": "TODO", "footer": "TODO key keywords",
            "_source": {"abilities_text": u["abilities_text"], "keywords": u["keywords"],
                        "other": u.get("other", {})},
        })

    pack = {
        "title": army.get("name", ""),
        "subtitle": " · ".join(x for x in [" + ".join(army.get("detachments", [])),
                                           army.get("points", ""),
                                           army.get("disposition", "")] if x),
        "edition": "11th Edition",
        "sequence": "TODO from references/game-sequence.md",
        "plan": scaffold_plan(army),
        "reminders": "TODO",
        "phases": "TODO",
        "units": units,
        "_army": army,
        "_rules_text": parsed.get("rules_text", ""),
        "_warnings": parsed.get("warnings", []),
    }
    json.dump(pack, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
    todo = json.dumps(pack).count("TODO")
    print(f"{len(units)} cards scaffolded ({len(parsed['units'])} units) -> {sys.argv[2]}; {todo} TODO fields to fill")


if __name__ == "__main__":
    main()
