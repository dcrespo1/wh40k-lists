# wh40k-lists

Warhammer 40,000 army lists, plus a Claude skill that turns a list into a
printable reference pack: a game-sequence card, a game plan, a phase-by-phase
cheat sheet and a card for every unit.

## Quick start

```bash
git clone <this repo> && cd wh40k-lists
./setup
```

That's the whole setup. `./setup` installs only what's missing, so you can run
it again at any time, for example after pulling changes. Then:

```bash
claude        # open Claude Code in this folder, then ask:
              # "make me a pack for lists/dark-angels.pdf"
```

Claude picks up the skill automatically. The finished pack lands in
`40k-output/` as HTML and PDF.

Supported: macOS (tested) and Debian/Ubuntu Linux. On Windows, use WSL.

## What gets installed

| What | Why this repo needs it | How `./setup` installs it |
|------|------------------------|---------------------------|
| **Homebrew** (macOS only) | Installs the two system libraries below | Asks first, then runs the official installer. Skipped if you already have it. |
| **poppler** | Command-line PDF tools (`pdftotext`, `pdftoppm`, `pdfinfo`). Used to render page images when a PDF's numbers can't be read as text. | `brew install poppler` / `apt install poppler-utils` |
| **pango** | Text layout library that WeasyPrint uses to draw the PDF. Without it you still get HTML packs, which print fine from a browser. | `brew install pango` / `apt install libpango-1.0-0 libpangoft2-1.0-0` |
| **uv** | Manages Python: downloads the right version, creates `.venv/`, installs the packages from `uv.lock` exactly. | `brew install uv` / official install script. Skipped if already on your PATH. |
| **just** | Task runner for the shortcut commands below. | `brew install just` / `uv tool install rust-just`. Skipped if already on your PATH. |
| **Python 3.12** | Runs the skill's scripts. Pinned in `.python-version`. | Downloaded by uv into its own folder. Your system Python isn't touched. |
| **pdfplumber** (+ pdfminer.six) | Reads stats and weapon profiles out of the army-list PDFs. | `uv sync`, into `.venv/` |
| **WeasyPrint** | Turns the HTML pack into a PDF. | `uv sync`, into `.venv/` |

All the Python packages live in `.venv/` inside this folder. Delete that folder
and run `./setup` again to get a clean one.

To check your setup without installing anything, run `just doctor`.

## Everyday commands

Run `just` on its own to see every command. The main ones:

| Command | What it does |
|---------|--------------|
| `just doctor` | Checks that everything is installed and working |
| `just parse lists/dark-angels.pdf` | Reads a list into JSON, with the numbers prefilled |
| `just render 40k-output/dark-angels.json` | Builds the HTML + PDF pack from a filled-in JSON |
| `just check` | Smoke test: every list in `lists/` parses, and every pack renders |
| `just package` | Zips the skill into a `.skill` file for Claude.ai |
| `just clean` | Deletes generated files |

You don't need these to make a pack, because Claude runs the same scripts
itself. They're for checking and debugging the skill.

## Layout

```
lists/<faction>/                       army list exports (mostly warmind.online PDFs)
.claude/skills/wh40k-datasheet-explainer/
  SKILL.md                             what Claude follows
  references/                          rules guidance, output formats
  scripts/                             PDF parsing and card rendering
  assets/                              card template
40k-output/                            generated packs (gitignored, safe to delete)
setup                                  one-step install
justfile                               shortcut commands
pyproject.toml, uv.lock                Python packages, locked versions
```

## How the Python setup works

- Commands in the `justfile` run through `uv run`, which uses the locked `.venv/`.
  If `pyproject.toml` or `uv.lock` changed since your last `./setup`, uv updates
  `.venv/` before running.
- Each skill script also lists its own packages in a short header at the top
  ([PEP 723](https://peps.python.org/pep-0723/) inline metadata). That's why
  Claude can run `uv run .claude/skills/.../parse_datasheet.py` from any folder,
  including when the skill is installed outside this repo.
- To add a package, run `uv add <package>`. If a skill script imports it, add
  it to that script's header too.

## Troubleshooting

**"PDF skipped: WeasyPrint can't load its system libraries" (macOS).** Python
from uv doesn't look in Homebrew's library folder. `build_cards.py` fixes this
on its own by relaunching itself with `DYLD_FALLBACK_LIBRARY_PATH` set. If you
call WeasyPrint some other way, set that variable yourself:
`export DYLD_FALLBACK_LIBRARY_PATH=$(brew --prefix)/lib`. Run `just doctor` to
confirm. The HTML pack is always written, and printing it from a browser works
too.

**Something else is missing.** Run `./setup` again, then `just doctor`.

## Why uv (and not something else)

These are the options we weighed for the lowest-friction setup:

- **uv + Homebrew + a setup script (chosen).** uv handles everything on the
  Python side, including the Python version, quickly and from a lockfile.
  Homebrew covers the two C libraries, which no Python tool can install. The
  setup script ties them together and needs nothing installed first.
- **pixi (conda-forge).** One tool could install Python, poppler and pango, with
  no Homebrew and no library-path workaround. It's the better choice if people
  on Linux or Windows start using this repo heavily. The downsides are a larger
  environment, a tool most people haven't met, and Claude would need `pixi run`
  for every script.
- **mise.** Good for pinning tool versions, but it can't install pango or
  poppler. On top of Homebrew and uv it would be a third tool doing a job they
  already do.
- **Dev container / Nix.** Fully reproducible, but heavy for a repo of a few
  scripts. A container also can't open PDFs in your browser or easily share your
  Claude Code login.
