---
name: wh40k-datasheet-explainer
description: Turn Warhammer 40,000 datasheets and army lists (PDFs, pasted text, or exports from the Warhammer 40,000 app, warmind.online, Wahapedia, New Recruit, BattleScribe, Listforge, etc.) into plain-language explanations, phase reminders, a game-sequence card, deployment and scoring tips, printable reference cards, and turn-by-turn phase cheat sheets. Use this whenever the user shares a 40k datasheet, unit card, roster, or army list, asks what a unit does or how its abilities work, wants a cheat sheet, reference card, or game plan, asks how to deploy or score with their army or Force Disposition, or is learning a new army — even if they never say "datasheet" or "explain."
compatibility: Best with uv (scripts declare their own Python packages, so `uv run` installs them); otherwise python3 with pdfplumber. Needs poppler (pdftotext, pdftoppm, pdfinfo) for the image fallback, and optionally WeasyPrint + pango for PDF output.
---

# Warhammer 40k Datasheet Explainer

The goal is to take dense rules text and make it usable at the table: what each
unit is for, what its numbers mean in practice, and exactly when each ability
matters during a turn.

## Where things go

- `<skill-dir>` is this skill's folder (in the wh40k-lists repo:
  `.claude/skills/wh40k-datasheet-explainer`). Run scripts by that path.
- Write everything to `40k-output/` in the current working directory: the JSON,
  extracted text, page images (`40k-output/work/<army-name>/`) and the final
  `.html`/`.pdf`. Create the folder if it doesn't exist. Name files after the
  army, lowercase with hyphens (e.g. `dark-angels-reference.pdf`).
- Run scripts with `uv run <skill-dir>/scripts/<script>.py`. Each script lists
  its Python packages in a header, so uv fetches them automatically and it works
  from any folder. If `uv` isn't available, use `python3` instead.
- If a script reports a missing dependency, tell the user the install command
  it printed rather than installing anything yourself. In the wh40k-lists repo
  the answer is always `./setup`.

## Step 1: Get structured data (don't retype numbers)

**PDF:** parse it first. This is the fast path, and it usually needs no images:

```bash
uv run <skill-dir>/scripts/parse_datasheet.py <file.pdf> 40k-output/<army-name>.parsed.json
uv run <skill-dir>/scripts/scaffold_pack.py 40k-output/<army-name>.parsed.json 40k-output/<army-name>.json
```

`parse_datasheet.py` emits every unit's stat lines and weapon profiles as JSON,
plus ability text, keywords and the army rules. It decodes the "missing digits"
in browser print-to-PDF exports from their font glyphs, and it never guesses:

- **Exit 0:** clean. Trust the numbers; don't render page images.
- **Exit 2:** parsed with warnings. Each warning names the unit and weapon
  with a value it couldn't read. Render only those pages
  (`extract_datasheet.py <pdf> <dir> --pages N`) and fix just those values.
- **Exit 1:** couldn't parse (unfamiliar layout). Fall back to
  `extract_datasheet.py`: use TEXT_OK text directly, or for NUMBERS_MISSING /
  IMAGE_ONLY read numbers from page images.

`scaffold_pack.py` turns the parsed data into the pack JSON with every stat and
weapon already filled in and identical duplicate units merged. Edit that file:
fill only the "TODO" fields (role, "good vs", abilities, watch, footer, and the
army-level sequence, plan, reminders and phases), using `_source` and
`_rules_text` for the rule wording. Never rewrite the stat or weapon numbers.
`build_cards.py` refuses to render while any TODO remains.

**Pasted text** (or a file already in your context as text): use it directly,
check the stat lines contain real numbers, and write the pack JSON by hand.

Before explaining anything in an army list, identify every unit, its Leader
attachment, any Enhancements, and the Detachment(s).

## Step 2: Read the conventions, edition, and detail level

**Builder conventions.** Read `references/builder-conventions.md`. Exports
mark already-applied modifiers (▲/▼), duplicate conferred keywords, and
repeat army rules as stubs on every sheet. Misreading these is the most common
way to give a wrong number.

**Edition.** 11th Edition launched in June 2026, and 10th Edition codexes stay
valid in it, so sheets can mix eras. The rule text on the sheet is the
authority. For keywords the sheet names without defining, use
`references/keyword-glossary.md`, which separates confirmed 11th Edition
changes, 10th-era meanings (state these with a "check current Core Rules"
note when exactness matters), and keywords you must not explain because their
meaning isn't confirmed. For those, say the sheet doesn't define it rather
than guessing.

**Faction resources.** Look in the army rules for resources or army-wide
states (points earned and spent, modes that switch on thresholds). They drive
the reminders, the sequence card and the game plan; see
`references/strategy-guide.md`.

**Force Disposition and mission.** In 11th Edition each player picks a Force
Disposition (exports often show it in the header, e.g. "Take and Hold"), and the
mission comes from both players' dispositions: each player plays the mission
in their own row of the matrix (`assets/disposition-matrix.json`), so the two
sides usually score different missions. Note the user's disposition. If the
export lists several, recommend one. Either way, give a matchup row for each
opponent disposition (strategy-guide.md section 8; the scaffold prefills the
mission names). Ask about the opponent's disposition or the mission card only
if the user wants tailored scoring tips; otherwise proceed and say the tips
are general. Mission names don't tell you scoring, so don't infer it.

**Detail level.** Support two modes, switchable any time:
- **Newcomer** (user is new, or asks basic questions): explain every keyword
  the first time, put stats in context ("Toughness 10 means most small arms
  need a 6 to wound it"), and lead with the unit's job.
- **Veteran** (user is experienced or asks for "quick", "tl;dr", "just the
  card"): skip common definitions; focus on interactions and timing traps.

If unsure, use newcomer level in chat and veteran density on the cards.

## Step 3: Produce the outputs

Read `references/output-formats.md` first. If the user didn't specify, give
the chat summary and offer the cards and cheat sheet.

1. **Plain-language summary (chat).** It opens with a **Reminders** checklist
   (what to actively do at the start of Command, in Movement, when shooting,
   and so on), then the army overview. Scale to army size: a big list gets
   one-liners in chat, with full detail on the cards.
2. **Printable pack**: fill in the scaffolded JSON and render it with
   `<skill-dir>/scripts/build_cards.py` (HTML + PDF). In order, it contains:
   - **Game sequence card**: the order of operations for a game, from
     `references/game-sequence.md`, with this army's pre-game items slotted in.
   - **Game plan card**: deployment and scoring tips built from this list and
     its Force Disposition, following `references/strategy-guide.md`. If the
     export lists several dispositions, it opens with a recommended pick.
   - **Matchups card**: for each opponent disposition, the mission you play,
     the mission they play, and one tip for playing into them.
   - **Phase cheat sheet**, with the Reminders box at the top. It re-sorts
     every ability and stratagem by when it happens. Players usually forget
     abilities through timing, not misunderstanding, so this is the core output.
   - **Unit reference cards**.

Before delivering, spot-check any values you fixed by hand (exit-2 warnings or
the image fallback) against the page images.

## How to explain things well

- **Translate, don't paraphrase.** "Each time this model makes an attack,
  re-roll a Hit roll of 1" becomes "Re-roll 1s to hit." Keep the meaning exact.
- **Give numbers context.** Say what a stat beats and what beats it.
- **Call out timing and conditions:** "only while leading", "once per battle",
  "in your Movement phase, not Command". This is where players misplay.
- **Flag interactions** between Leaders and Bodyguards, Detachment rules and
  unit abilities, and transports and who can ride, when the sheets show them.
  Do the transport math: capacity, plus any models that take extra slots.
- **Hunt for "ignore modifiers" rules.** They quietly cancel penalties elsewhere
  on the sheet: Damaged, cover, Stealth. Say so on the card.
- **Check prerequisites.** If an ability or stratagem needs wargear, a keyword
  or an ability the unit doesn't have on this list (e.g. "its mole grenade
  launcher" on a unit with no such weapon, or a stratagem for units "that have
  Deep Strike"), flag it as probably inactive instead of explaining it as usable.
- **Report stats as printed**, even if they look surprising.
- **Be honest about uncertainty.** Name anything ambiguous and put it in the
  card's "flag" field.
- **Strategy is advice, not rules.** Ground every tip in a specific unit or rule
  from the list, and never state mission scoring you haven't been given.
- **Check combinations against restrictions.** Before any tip or reminder that
  combines rules ("Azrael gives them a second doctrine"), find the army or
  core rule that limits it (e.g. one doctrine per unit at a time) and follow
  `references/strategy-guide.md` section 6. A confident wrong combo is the worst
  error this skill can make, because the player will build a turn around it.
- **Don't reproduce lore or large blocks of rules text verbatim.** The user has
  the sheet; the value is the explanation.
