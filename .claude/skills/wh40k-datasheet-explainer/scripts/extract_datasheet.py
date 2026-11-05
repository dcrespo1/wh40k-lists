#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Extract a 40k datasheet / army list PDF and report how trustworthy the text is.

Usage: uv run extract_datasheet.py <file.pdf> [outdir]

Reports one of three modes, then prints a page index and the text:
  TEXT_OK          numbers survived extraction; the text is usable on its own.
  NUMBERS_MISSING  words extracted but stat/weapon numbers did not (common with
                   browser "print to PDF", which draws digits with unmapped Type 3
                   fonts). Use the text for names and abilities; read every number
                   from page images (render with --pages).
  IMAGE_ONLY       almost no text; read the whole sheet from page images.

Render pages:  uv run extract_datasheet.py <file.pdf> [outdir] --pages 3,6-8
"""
import re, subprocess, sys, os, signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def run(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout

def parse_pages(spec):
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-"); out += range(int(a), int(b) + 1)
        elif part:
            out.append(int(part))
    return out

def render(pdf, outdir, pages, dpi=120):
    for p in pages:
        run("pdftoppm", "-r", str(dpi), "-png", "-f", str(p), "-l", str(p), pdf, f"{outdir}/page")
    print("\n".join(sorted(f"{outdir}/{f}" for f in os.listdir(outdir) if f.startswith("page-"))))

STAT_HDR = re.compile(r"^\s*M\s+T\s+SV\b")
WPN_HDR = re.compile(r"\bRANGE\s+A\s+(BS|WS)\b")
# A stat value looks like 3+, 24", -2, 0, D6, D3+3, 2D6, Melee does not count.
VALUE = re.compile(r'^(-?\d+[+"]?|\d*D\d+(\+\d+)?)\*?$')

def numeric(row):
    return sum(bool(VALUE.match(t)) for t in row.split()) >= 3

UNIT_HDR = re.compile(r"^\s*(\S.*?)\s+(\d+)\s*pts\s*$", re.I)

def main():
    import shutil
    missing = [t for t in ("pdftotext", "pdftoppm", "pdfinfo") if not shutil.which(t)]
    if missing:
        sys.exit(f"Missing {', '.join(missing)}: install poppler (macOS: brew install poppler; "
                 "Debian/Ubuntu: apt install poppler-utils).")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pdf = args[0]; outdir = args[1] if len(args) > 1 else "./datasheet_extract"
    os.makedirs(outdir, exist_ok=True)
    if "--pages" in sys.argv:
        render(pdf, outdir, parse_pages(sys.argv[sys.argv.index("--pages") + 1])); return

    info = re.search(r"Pages:\s+(\d+)", run("pdfinfo", pdf))
    if not info:
        sys.exit(f"Can't read {pdf}: not a valid PDF, or it's encrypted/corrupt.")
    n = int(info.group(1))
    pages = [run("pdftotext", "-layout", "-f", str(i), "-l", str(i), pdf, "-") for i in range(1, n + 1)]
    text = "\f".join(pages)
    open(f"{outdir}/text.txt", "w").write(text)

    chars = len(re.sub(r"\s", "", text))
    # For each stat/weapon header, check whether the next data row carries digits.
    rows = hits = 0
    for pg in pages:
        lines = [l for l in pg.splitlines() if l.strip()]
        for i, l in enumerate(lines):
            if STAT_HDR.search(l) or WPN_HDR.search(l):
                for nxt in lines[i + 1:i + 3]:
                    if nxt.strip().startswith("["):   # keyword line, skip
                        continue
                    rows += 1
                    hits += numeric(nxt)
                    break

    if chars < n * 200:
        mode = "IMAGE_ONLY"
    elif rows and hits / rows < 0.5:
        mode = f"NUMBERS_MISSING ({hits}/{rows} stat/weapon rows have stat values)"
    else:
        mode = f"TEXT_OK ({hits}/{rows} stat/weapon rows have stat values)"
    print(f"MODE: {mode}\nPAGES: {n}\nTEXT: {outdir}/text.txt\n")

    print("PAGE INDEX (unit headers with points):")
    for i, pg in enumerate(pages, 1):
        found = [f"{m.group(1)} [{m.group(2)} pts]" for l in pg.splitlines() if (m := UNIT_HDR.match(l))]
        if found:
            print(f"  p{i}: " + "; ".join(found))
    if not mode.startswith("TEXT_OK"):
        print(f"\nNEXT: render the pages you need, e.g. --pages 3,5-6, and read numbers from the images.")
    print("\n---- TEXT ----")
    print(text)

if __name__ == "__main__":
    main()
