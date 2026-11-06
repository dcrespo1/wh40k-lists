# wh40k-lists

Warhammer 40,000 army lists, plus a Claude skill that turns a list into a
printable reference pack: a game-sequence card, a game plan, a matchups card,
a phase-by-phase cheat sheet and a card for every unit.

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

## Example output

[`output-example/`](output-example/) holds a finished pack for
`lists/dark-angels.pdf` (2000 pts, Wrath of the Rock + Assault Brethren, Take
and Hold). **[View it online](https://dcrespo1.github.io/wh40k-lists/)**, or
open [`dark-angels-reference.pdf`](output-example/dark-angels-reference.pdf)
to see what you'll get. It runs to 10 pages:

| Pages | What's on them |
|-------|----------------|
| 1 | **Game sequence**: pre-game steps and turn order, with this army's own steps slotted in (Teleport Homer, reserves, embarking Rhinos), and **Game plan**: deployment and scoring tips for Take and Hold, built from these units |
| 2 | **Matchups**: for each disposition your opponent might pick, the mission you play, the mission they play, and a tip for playing into them |
| 3–4 | **Turn cheat sheet**: a "Don't forget" box, then every ability and stratagem sorted by the phase it happens in |
| 5–10 | **Unit cards**: stats and weapons as printed on the sheet, what each weapon is good against, abilities tagged by timing, and a "Check" box for anything uncertain |

The other files show the steps in between:

| File | What it is |
|------|------------|
| `dark-angels.parsed.json` | Output of `just parse`: every stat line, weapon, ability and army rule read from the PDF |
| `dark-angels.json` | The pack JSON after Claude filled in the explanations. `just render` turns it into the HTML and PDF |
| `dark-angels-reference.html` | The same pack as a web page. It prints fine from a browser |

Your own packs go to `40k-output/`, which is gitignored. The example folder is
committed, so regenerate it by hand if the skill's output changes.

### Publishing the example

[`.github/workflows/pages.yml`](.github/workflows/pages.yml) publishes
`output-example/` to GitHub Pages:

- **When it runs:** only on a push to `main` that changes something in
  `output-example/` (or the workflow file). Any other push leaves the site as
  it is. To re-publish by hand, use **Actions → Publish example pack → Run
  workflow**.
- **What gets published:** every `*-reference.html` and `*-reference.pdf` in
  the folder, plus an index page that lists them. To show off a new feature,
  copy a pack in (for example, from a local eval) and push. It appears on the
  index without any other edits. The JSON files stay in the repo and aren't
  published, because they carry the export's rules text.
- **One-time setup:** in the repo, go to **Settings → Pages** and set
  **Source** to **GitHub Actions**.

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

```text
wh40k-lists/
├── lists/                            army list exports (mostly warmind.online PDFs)
├── .claude/skills/
│   └── wh40k-datasheet-explainer/
│       ├── SKILL.md                  what Claude follows
│       ├── references/               rules guidance, output formats
│       ├── scripts/                  PDF parsing and card rendering
│       └── assets/                   card template, disposition matrix
├── .github/workflows/pages.yml       publishes output-example/ to GitHub Pages
├── 40k-output/                       your generated packs (gitignored, safe to delete)
├── output-example/                   a finished Dark Angels pack (committed)
├── setup                             one-step install
├── justfile                          shortcut commands
├── pyproject.toml                    Python packages
└── uv.lock                           locked package versions
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
