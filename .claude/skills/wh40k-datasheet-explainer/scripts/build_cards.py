#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["weasyprint>=62"]
# ///
"""Render a phase cheat sheet + unit reference cards from JSON to HTML (and PDF).

Usage: uv run build_cards.py army.json out_basename [--no-pdf]
Writes out_basename.html and out_basename.pdf. Styling comes from
assets/card-template.html. See references/output-formats.md for the JSON shape.
"""
import json, sys, os, html
E = lambda x: html.escape(str(x))
HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    src, base = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.dirname(os.path.abspath(base)), exist_ok=True)
    d = json.load(open(src))
    todos = [k for k, v in d.items() if not k.startswith("_") and "TODO" in json.dumps(v)]
    if todos:
        sys.exit(f"Unfilled TODO fields in: {', '.join(todos)}. Fill them before rendering.")
    tpl = open(os.path.join(HERE, "..", "assets", "card-template.html")).read()
    css = tpl.split("<style>")[1].split("</style>")[0]
    out = [f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>{E(d['title'])}</title><style>{css}</style></head><body>"]

    def listsec(sections, cls=""):
        h = ""
        for sec in sections:
            items = sec.get("items", [])
            if items:
                h += f"<h3 class='{cls}'>{E(sec['name'])}</h3><ul>" + "".join(f"<li>{E(i)}</li>" for i in items) + "</ul>"
        return h

    # 1. Game sequence card (order of operations)
    if d.get("sequence"):
        out.append(f"<div class='card seq'><div class='head'><h2>Game sequence</h2><span>{E(d.get('edition',''))}</span></div>")
        out.append(listsec(d["sequence"]))
        if d.get("sequence_note"):
            out.append(f"<div class='foot'>{E(d['sequence_note'])}</div>")
        out.append("</div>")

    # 2. Game plan card (deployment + scoring tips)
    if d.get("plan"):
        pl = d["plan"]
        out.append(f"<div class='card plan'><div class='head'><h2>Game plan</h2><span>{E(pl.get('disposition',''))}</span></div>")
        if pl.get("summary"):
            out.append(f"<p class='role'>{E(pl['summary'])}</p>")
        out.append(listsec(pl.get("sections", [])))
        if pl.get("note"):
            out.append(f"<div class='watch'>{E(pl['note'])}</div>")
        out.append("</div>")

    # 3. Cheat sheet, with reminders boxed at the top
    if d.get("phases") or d.get("reminders"):
        out.append(f"<div class='cheat'><h1>{E(d['title'])} — Turn Cheat Sheet</h1>")
        if d.get("subtitle"):
            out.append(f"<p class='role'>{E(d['subtitle'])}</p>")
        if d.get("reminders"):
            out.append("<div class='remind'><h2>Don't forget</h2>")
            for r in d["reminders"]:
                out.append(f"<p><strong>{E(r['when'])}:</strong> " + " · ".join(E(i) for i in r["items"]) + "</p>")
            out.append("</div>")
        out.append(listsec(d.get("phases", [])))
        out.append("</div>")

    for u in d.get("units", []):
        st = "<tr><th class='l'>Model</th><th>M</th><th>T</th><th>Sv</th><th>Inv</th><th>W</th><th>Ld</th><th>OC</th><th class='l'>Other</th></tr>"
        for r in u["stats"]:
            r = list(r) + [""] * (9 - len(r))
            st += f"<tr><td class='l'>{E(r[0])}</td>" + "".join(f"<td>{E(x)}</td>" for x in r[1:8]) + f"<td class='l sm'>{E(r[8])}</td></tr>"
        wp = "<tr><th class='l'>Weapon</th><th>Rng</th><th>A</th><th>BS/WS</th><th>S</th><th>AP</th><th>D</th><th class='l'>Keywords</th><th class='l'>Good vs</th></tr>"
        for r in u["weapons"]:
            r = list(r) + [""] * (9 - len(r))
            wp += f"<tr><td class='l'>{E(r[0])}</td>" + "".join(f"<td>{E(x)}</td>" for x in r[1:7]) + f"<td class='l sm'>{E(r[7])}</td><td class='l sm'>{E(r[8])}</td></tr>"
        ab = "".join(f"<li><span class='tag'>{E(t)}</span>{E(x)}</li>" for t, x in u.get("abilities", []))
        watch = f"<div class='watch'><strong>Don't forget:</strong> {E(u['watch'])}</div>" if u.get("watch") else ""
        flag = f"<div class='flag'><strong>Check:</strong> {E(u['flag'])}</div>" if u.get("flag") else ""
        out.append(f"<div class='card'><div class='head'><h2>{E(u['name'])}</h2><span>{E(u.get('pts',''))}</span></div>"
                   f"<p class='role'>{E(u.get('role',''))}</p><table>{st}</table><table>{wp}</table>"
                   f"<ul class='abil'>{ab}</ul>{watch}{flag}<div class='foot'>{E(u.get('footer',''))}</div></div>")
    out.append("</body></html>")
    open(base + ".html", "w").write("".join(out))
    print(base + ".html")

    if "--no-pdf" not in sys.argv:
        try:
            import weasyprint
        except (ImportError, OSError) as e:
            # macOS: Python often can't find Homebrew's pango/glib libraries. Re-run
            # once with Homebrew's lib folder on the library path before giving up.
            if sys.platform == "darwin" and not os.environ.get("_WH40K_REEXEC"):
                for lib in ("/opt/homebrew/lib", "/usr/local/lib"):
                    if os.path.exists(os.path.join(lib, "libgobject-2.0.0.dylib")) or \
                       os.path.exists(os.path.join(lib, "libgobject-2.0.dylib")):
                        env = dict(os.environ, _WH40K_REEXEC="1")
                        env["DYLD_FALLBACK_LIBRARY_PATH"] = ":".join(
                            x for x in (lib, env.get("DYLD_FALLBACK_LIBRARY_PATH")) if x)
                        os.execve(sys.executable, [sys.executable] + sys.argv, env)
            kind = "isn't installed" if isinstance(e, ImportError) else "can't load its system libraries"
            print(f"PDF skipped: WeasyPrint {kind}. HTML written; it prints fine from a browser.\n"
                  "Fix: run this script with `uv run` (installs WeasyPrint), and install pango\n"
                  "(macOS: brew install pango; Debian/Ubuntu: apt install libpango-1.0-0).\n"
                  "In the wh40k-lists repo, ./setup does all of this.",
                  file=sys.stderr)
            return
        weasyprint.HTML(base + ".html").write_pdf(base + ".pdf")
        print(base + ".pdf")

if __name__ == "__main__":
    main()
