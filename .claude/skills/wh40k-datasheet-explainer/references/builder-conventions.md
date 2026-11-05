# Army-builder export conventions

Exports from list builders (Warhammer 40,000 app, warmind.online, New Recruit,
Listforge, Wahapedia prints) share some conventions that change how numbers
and keywords should be read.

## Modified values are already applied
A stat shown **bold with a ▲ or ▼ marker**, with a footnote under the weapon or
model naming a source (e.g. "▲ Book of Salvation"), has ALREADY had that
modifier applied. Report the shown value as final and name the source; do not
add the bonus again. (Seen on warmind.online: Ezekiel's Traitor's Bane shows
A 5▲ with "▲ Book of Salvation".)

## Conferred keywords show up as duplicates
A Leader's buff can be added to its Bodyguard's weapon keywords, producing e.g.
`[SUSTAINED HITS 2] [SUSTAINED HITS 1]`. A "Conferred weapon keywords" block
usually names the source. Explain it as "Sustained Hits 2 (the better one
applies); Sustained Hits 1 comes from [Leader]" and flag it for the user to
confirm, since stacking rules depend on edition wording.

## "Full text under Rules and Stratagems"
Army and Detachment rules are repeated as stubs on every datasheet. Read the
full text once from the Rules section and explain it once (in the army
overview and the cheat sheet), not on every card.

## Points and order
Unit headers carry points ("330 pts"); combined Leader + Bodyguard headers show
the total, with each part listed separately. "squad A / squad B" or "A / B"
labels distinguish duplicate units: merge identical units into one card
("×2 (A & B)") unless their wargear differs.

## Format variants seen
- "Damaged 4" and "Damaged: 1-5 wounds remaining" are the same kind of rule;
  read the threshold from whichever form appears.
- Builders may already merge identical units into one sheet ("Cthonian Beserks ×2",
  points shown per unit). Keep the merge and say "each" next to the points.

## Browser print-to-PDF
Exports printed from a browser often draw numbers with unmapped fonts, so plain
text extraction keeps words but loses every stat (extract_datasheet.py reports
NUMBERS_MISSING). parse_datasheet.py recovers them from glyph names; its GLYPHS
table covers Safari's San Francisco font. If a new source shows undecoded-glyph
warnings, read a few known values from page images, add the glyph names to
GLYPHS, and re-run, instead of reading every number by eye.
