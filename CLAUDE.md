# wh40k-lists

My Warhammer 40k army lists, plus a Claude skill that turns them into
reference packs (cheat sheet, game plan, unit cards).

## Layout
- `lists/<faction>/` — army list exports (mostly warmind.online PDFs).
- `.claude/skills/wh40k-datasheet-explainer/` — the skill. Rules
  interpretation, output formats and scripts live there, not here.
- `40k-output/` — generated files (gitignored). Safe to delete.

## Working on the skill
- When I report a mistake in a pack, fix the skill (the relevant reference
  file or SKILL.md), not just the output.
- After changing the skill, re-run it on the sample lists in `lists/` and
  compare against the previous output before calling it done.
- Keep SKILL.md under ~500 lines; push detail into `references/`.
- Don't paste Games Workshop rules text into the skill. Explain in our own
  words; the sheets are the source of truth.

## Tooling
- Setup is `./setup` (also `just setup`): Homebrew for poppler + pango, uv
  for Python and packages. `just doctor` checks it without installing.
  README.md lists every dependency.
- Python goes through uv: `uv run <script>` for skill scripts (they declare
  their deps inline), `uv run python` in the justfile. Not bare `python3`.
- Task runner is `just` (see justfile).
- Don't install dependencies yourself; tell me what's missing (the fix is
  usually `./setup`).

## My games
- 11th Edition, matched play.
- Default to newcomer-level explanations unless I ask for quick