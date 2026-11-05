# Output Formats

## 1. Plain-language summary (chat)

**Scale to army size.** For one to four units, write each unit in full (below).
For a larger army, the chat gets an army overview plus the short "what it's for"
line and one notable thing per unit; the full detail goes on the cards. A full
per-unit write-up of a 2000-point list is too long to use.

### Army overview (any list with more than one unit)
Open the overview with a **Reminders** section: a short checklist of things the
player must actively DO, grouped by when (e.g. "Start of your Command phase:
pick a doctrine; pick the Lion's two Primarch abilities"). Include only active
choices and triggers that are easy to miss: not passive always-on effects, and
not everything on the cheat sheet. Aim for 6 to 10 items in total. If the army has a resource or switching state
(points, tokens, army-wide modes), the reminders MUST show when it's earned,
spent and checked, including on the opponent's turn. Add a "Start of battle"
entry when the army begins in a particular state.

Then:
- What the army is trying to do, in two or three sentences.
- Army rule and Detachment rule(s) in plain language, explained once here.
- The top two or three game plan tips (see strategy-guide.md), with a pointer to
  the full Game plan card.

### Per unit (full form)
```
## [Unit name] ([points])
**What it's for:** its battlefield job in one or two sentences.
**Stats in context:** what's notable in the stat line. Newcomer: explain each
stat. Veteran: only what's unusual.
**Weapons:** what each one is good against and why.
**Abilities:** each in plain English, with *when* it applies in bold.
**Watch out for:** one to three timing traps or common misplays.
```

## 2 and 3. Cards and cheat sheet: build from JSON

For PDFs, start from the scaffolded JSON (SKILL.md Step 1) and fill the TODO
fields; for pasted text, write the JSON yourself. Then render:

```bash
uv run <skill-dir>/scripts/build_cards.py 40k-output/<army-name>.json 40k-output/<army-name>-reference
```

This writes `.html` and `.pdf`. Order in the file: Game sequence card →
Game plan card → cheat sheet (with the Reminders box on top) → unit cards.
Use `--no-pdf` to skip the PDF.

```json
{
  "title": "Dark Angels",
  "subtitle": "Detachment(s) · points · Warlord",
  "edition": "11th Edition",
  "sequence": [
    {"name": "Pre-game", "items": ["1. Muster armies: choose Force Disposition (this list: Take and Hold)"]},
    {"name": "Each turn", "items": ["1. Start of turn step: ..."]}
  ],
  "sequence_note": "Steps from the core rules; follow your mission pack where noted.",
  "plan": {
    "disposition": "Take and Hold",
    "summary": "One line: how this list wins.",
    "sections": [
      {"name": "Deployment", "items": ["tip"]},
      {"name": "Scoring", "items": ["tip"]}
    ],
    "note": "Exact scoring depends on your mission card. Share it for tailored tips."
  },
  "reminders": [
    {"when": "Start of your Command phase", "items": ["Pick a combat doctrine"]}
  ],
  "phases": [
    {"name": "Command phase", "items": ["Unit — effect (condition)"]}
  ],
  "units": [{
    "name": "Azrael + Inner Circle Companions",
    "pts": "330 pts",
    "role": "One line: what it's for.",
    "stats": [["Azrael", "6\"", "5", "2+", "4+", "6", "6+", "1", "other e.g. FNP"]],
    "weapons": [["Lion's Wrath", "24\"", "2", "2+", "8", "-3", "2", "keywords", "Good vs"]],
    "abilities": [["MOVE", "Plain-language effect"]],
    "watch": "The one thing most likely to be forgotten.",
    "flag": "Optional: anything uncertain the user should check.",
    "footer": "Key keywords · Leader/transport notes"
  }]
}
```

Card rules:
- Stats and weapons exactly as on the sheet (use "—" for no invulnerable save).
- "Good vs": a short judgment from Strength, AP, Damage and keywords
  (e.g. "Hordes", "Elite infantry", "Vehicles & monsters", "Characters").
- Ability tags: BEFORE, START, CMD, MOVE, SHOOT, CHARGE, FIGHT, REACT,
  ALWAYS, ONCE. One line each, effect first, condition after.
- Army-wide rules (doctrines, Detachment rules) go on the cheat sheet, not on
  every card. Only mention them on a card where they interact with that unit.
- Use "flag" for anything you aren't sure of; it prints as a dashed box.
- Merge identical duplicate units into one card ("×2 (A & B)").

## Cheat sheet sections (in this order; skip empty ones)
Before the battle · Start of each battle round · Command phase · Movement phase ·
Shooting phase · Charge phase · Fight phase · Opponent's turn (reactive) ·
Always on.

Within a phase, order by when things trigger (start, then during, then end).
Each item reads `[Unit] — [effect] ([condition])`. Stratagems from the sheet go
in the phase where they're used, prefixed "Strat:" with their CP cost. Add
edition-wide reminders that change play (e.g. the 11th Edition one stratagem per
unit per phase) under "Always on".

## Game sequence card
Build it from `references/game-sequence.md`: pre-game steps, the turn sequence
with the sub-steps that matter, and the planning rules. Then add this army's own
pre-game items in the right step (e.g. "place Teleport Homer token", "declare
Deep Strike reserves", "choose Force Disposition: Take and Hold").

## Game plan card
Build it from `references/strategy-guide.md`.
