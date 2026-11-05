# wh40k-lists — helpers for the wh40k-datasheet-explainer skill.
# Generating a pack still needs Claude (it reads the page images);
# these recipes cover the scripted steps on either side of that.
# New here? Run ./setup (or `just setup`) once, then `just` to see the commands.

set shell := ["bash", "-euo", "pipefail", "-c"]
set positional-arguments := false

skill := ".claude/skills/wh40k-datasheet-explainer"
scripts := skill / "scripts"
out := "40k-output"
# All Python goes through uv: it uses the locked .venv and re-syncs it if
# pyproject.toml or uv.lock changed, so nobody has to remember to.
python := "uv run --quiet python"

# List recipes
default:
    @just --list --unsorted

# Turn a file path into a slug: "lists/votann/2000 Mosquitos.pdf" -> "2000-mosquitos"
[private]
slug path:
    @basename "{{path}}" | sed -E 's/\.[^.]+$//; s/[^A-Za-z0-9]+/-/g; s/^-+|-+$//g' | tr '[:upper:]' '[:lower:]'

# Install everything this repo needs (same as ./setup; safe to re-run)
setup:
    ./setup

alias install-deps := setup

# Check that everything is installed and working (installs nothing)
doctor:
    #!/usr/bin/env bash
    ok=1
    for t in uv pdftotext pdftoppm pdfinfo; do
      if command -v "$t" >/dev/null; then echo "✓ $t"; else echo "✗ $t missing: run ./setup"; ok=0; fi
    done
    if [ ! -x .venv/bin/python ]; then
      echo "✗ no .venv yet: run ./setup"; exit 1
    fi
    # macOS: uv's Python doesn't look in Homebrew's lib folder, so WeasyPrint can't
    # find pango unless we point it there. (It has to be set in here: macOS strips
    # DYLD_* variables when it starts bash. build_cards.py handles this itself.)
    [ "$(uname)" = Darwin ] && export DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix 2>/dev/null || echo /opt/homebrew)/lib:/usr/local/lib:/usr/lib"
    py="uv run --no-sync --quiet python"
    echo "  python: $($py --version 2>&1)"
    if $py -c "import pdfplumber" 2>/dev/null; then echo "✓ pdfplumber (reads the PDFs)"
    else echo "✗ pdfplumber missing: run ./setup"; ok=0; fi
    if $py -c "import weasyprint" >/dev/null 2>&1; then echo "✓ weasyprint + pango (PDF output)"
    else echo "! weasyprint can't load: PDFs skipped, HTML still works. Run ./setup"; fi
    [ "$ok" = 1 ] || exit 1

alias deps := doctor

# Parse a list PDF to structured JSON, then scaffold the pack JSON (numbers prefilled)
parse pdf:
    #!/usr/bin/env bash
    set -uo pipefail
    s=$(just slug "{{pdf}}")
    mkdir -p {{out}}
    {{python}} {{scripts}}/parse_datasheet.py "{{pdf}}" "{{out}}/$s.parsed.json"; rc=$?
    [ $rc -eq 1 ] && { echo "Parse failed: fall back to 'just extract'"; exit 1; }
    if [ -e "{{out}}/$s.json" ]; then
      echo "{{out}}/$s.json already exists: not overwriting (delete it to re-scaffold)"
    else
      {{python}} {{scripts}}/scaffold_pack.py "{{out}}/$s.parsed.json" "{{out}}/$s.json"
    fi
    exit $rc

# Extract a list PDF (image fallback): prints MODE, page index and text; saves to 40k-output/work/<slug>
extract pdf:
    #!/usr/bin/env bash
    set -euo pipefail
    s=$(just slug "{{pdf}}")
    {{python}} {{scripts}}/extract_datasheet.py "{{pdf}}" "{{out}}/work/$s"

# Render page images, e.g. `just pages lists/votann/list.pdf 2-12`
pages pdf range:
    #!/usr/bin/env bash
    set -euo pipefail
    s=$(just slug "{{pdf}}")
    {{python}} {{scripts}}/extract_datasheet.py "{{pdf}}" "{{out}}/work/$s" --pages "{{range}}"

# Render one pack JSON to HTML + PDF (refuses while TODO fields remain)
render json:
    #!/usr/bin/env bash
    set -euo pipefail
    s=$(just slug "{{json}}")
    {{python}} {{scripts}}/build_cards.py "{{json}}" "{{out}}/$s-reference"

# Re-render every pack JSON in 40k-output/ (after changing the template or builder)
render-all:
    #!/usr/bin/env bash
    set -euo pipefail
    shopt -s nullglob
    files=()
    for f in {{out}}/*.json; do [[ "$f" == *.parsed.json ]] || files+=("$f"); done
    [ ${#files[@]} -gt 0 ] || { echo "No JSON in {{out}}/ yet"; exit 0; }
    for f in "${files[@]}"; do
      if grep -q TODO "$f"; then echo "skip $f (TODO fields not filled yet)"; else just render "$f"; fi
    done

# Smoke test: every list in lists/ extracts, and every JSON renders
check: doctor
    #!/usr/bin/env bash
    set -uo pipefail
    shopt -s nullglob   # (no globstar: macOS ships bash 3.2)
    fail=0
    while IFS= read -r pdf; do
      s=$(just slug "$pdf")
      res=$({{python}} {{scripts}}/parse_datasheet.py "$pdf" "{{out}}/work/$s.parsed.json" 2>&1); rc=$?
      case $rc in
        0) echo "✓ $pdf  [$(head -1 <<<"$res")]";;
        2) echo "! $pdf  [$(head -1 <<<"$res")]"; grep '^WARNING' <<<"$res" | sed 's/^/    /';;
        *) echo "✗ $pdf: parse failed: $(tail -1 <<<"$res")"; fail=1;;
      esac
    done < <(find lists -name '*.pdf' | sort)
    for f in {{out}}/*.json; do
      [[ "$f" == *.parsed.json ]] && continue
      grep -q TODO "$f" && { echo "- $f has TODO fields (not filled yet)"; continue; }
      if {{python}} {{scripts}}/build_cards.py "$f" "{{out}}/work/check-$(just slug "$f")" --no-pdf >/dev/null; then
        echo "✓ $f renders"
      else echo "✗ $f failed to render"; fail=1; fi
    done
    exit $fail

# Package the skill as a .skill file (zip) for Claude.ai
package:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p {{out}}
    rm -f {{out}}/wh40k-datasheet-explainer.skill
    (cd .claude/skills && zip -qr "$OLDPWD/{{out}}/wh40k-datasheet-explainer.skill" wh40k-datasheet-explainer -x '*/__pycache__/*' '*.DS_Store')
    echo "{{out}}/wh40k-datasheet-explainer.skill"

# Open a rendered pack, e.g. `just open dark-angels-army`
open name:
    open "{{out}}/{{name}}-reference.pdf" 2>/dev/null || open "{{out}}/{{name}}-reference.html"

# Delete generated files (keeps pack JSON unless you pass all=true)
clean all="false":
    #!/usr/bin/env bash
    set -euo pipefail
    rm -rf {{out}}/work {{out}}/*-reference.html {{out}}/*-reference.pdf {{out}}/*.skill
    if [ "{{all}}" = "true" ]; then rm -rf {{out}}; fi
    echo "cleaned"
