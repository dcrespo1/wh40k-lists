# Deployment and scoring tips (the "Game plan" card)

These are suggestions built from the user's own list. Label them as tips, not
rules, and keep them specific to these units: "Put Intercessors on your home
objective, since Bolter Discipline wants an objective in range anyway" beats
"hold objectives with troops".

## 1. Know what's being scored
- Find the **Force Disposition** (export header, or ask). In 11th Edition the
  mission comes from BOTH players' dispositions, so exact VP scoring depends on
  the opponent too.
- If the user gives the mission card or the opponent's disposition, tailor the
  scoring tips to it. If not, base tips on what the user's disposition is about,
  and end the card with: "Exact scoring depends on your mission card. Share it
  for tailored tips."
- If the export lists more than one disposition ("Purge the Foe or Priority
  Assets"), the user hasn't chosen yet. Recommend one (section 8), label which
  tip belongs to which, and ask them to confirm before the game.
- What each disposition is about (themes from the mission decks; the full list
  and matrix are in `assets/disposition-matrix.json`):
  - **Take and Hold:** holding more objectives than the enemy, everywhere.
  - **Purge the Foe:** destroying enemy units.
  - **Disruption:** spoiling the enemy's plan and denying them ground.
  - **Reconnaissance:** scouting and taking key positions.
  - **Priority Assets:** capturing and holding high-value assets around the
    battlefield.
  These are themes, not scoring. Don't state VP, timings or actions for any
  mission unless the user gives you the card.

## 2. Sort the units into jobs
Work out each unit's job from its stats and abilities:
- **Holders:** high total OC (OC × models), durable, abilities tied to
  objectives (e.g. bonuses within range of an objective).
- **Action-doers:** cheap units, or units with rules about actions (e.g. can act
  while engaged or battle-shocked).
- **Hammers:** melee or shooting that removes key enemy units.
- **Long-range support:** 36"+ guns, Heavy weapons; want firing lanes and to
  stand still.
- **Reserves and redeployers:** Deep Strike, strategic reserves, teleport
  tokens, abilities that move units into reserves mid-game.
- **Transports and screens:** taxis, cheap bodies, Smoke units.

## 3. Deployment tips: draw from these, where the list supports them
- Holders start on or next to home objectives. Total each holder's OC and say it.
- Long-range units get the longest firing lanes, and support characters (e.g.
  repair or aura units) start within their range of effect.
- Deep strikers: note the 8" rule and what they threaten when they arrive.
  Placed tokens (e.g. a Teleport Homer) go where you want to arrive later and
  where enemies can't easily reach them.
- Units with conditional protection (Lone Operative while near friends, auras)
  start near the units that switch it on.
- Name which units ride which transport, and check the transport's limits.
- Fragile key pieces (psykers, buff characters) start out of sight.

## 4. Scoring tips: draw from these
- Name the list's biggest OC units and how to keep them scoring: battle-shock
  now sets OC to "–" and lasts until the unit passes a test, so save
  auto-pass tools (e.g. Insane Bravery) for a key holder.
- Point out every rule in the list that adds OC, secures objectives, or scores
  when a unit dies, and when to use it.
- Name the best unit for actions and why.
- Note round-by-round timing: reserves can't arrive in round 1 via Rapid
  Ingress, and ingress before round 3 can't enter the enemy deployment zone.
- Note doctrine or once-per-battle timing worth saving for the turns that
  matter (e.g. the turn you charge onto the midfield).

## 5. Faction resources and army states
Many armies run on a resource or a switching state (e.g. Leagues of Votann
Yield Points, which flip the army between Hostile Acquisition and Fortify
Takeover at 7+ YP). When the list has one:
- Spell out exactly when it's earned (including on the OPPONENT's turn, if so),
  when it's spent, and when thresholds are checked, in the right order.
- Give one tip on the spend-or-save choice, tied to the disposition: which state
  helps this plan, and which spends are worth falling below a threshold for.
- Name the units that earn or convert the resource.

## 6. Check every tip before writing it
Tips are where rules get combined, and combinations are where mistakes happen.
For each tip that combines two or more rules, or claims a timing:
- **Look for exclusivity and limit clauses** in the army rules, Detachment rules
  and core rules, e.g. "a unit can have only one combat doctrine active at a
  time", "once per battle", "one stratagem per unit per phase", "cannot be used
  in the first battle round". If one applies, the tip must respect it. Things
  only stack when a rule says so explicitly ("on top of any other").
- **Quote the clause that permits the combo** to yourself. If you can't point to
  one, drop the tip or reword it as a question for the user.
- **Express timing in battle rounds**, not "your turn 2", and account for who goes
  first. Don't add sequencing detail the rules don't state (e.g. "the last step
  before reinforcements").
- **Read bullet lists literally.** Two bullets after "pick one model" give that
  model both effects unless the text says "choose one".

## 7. Keep it short
Four to six deployment tips, four to six scoring tips, one closing line about the
mission card. These go on one card; the chat overview gets the top two or three.

## 8. Disposition choice and matchups
The two players' dispositions pick the missions, and **each player plays the
mission from their own row** of the matrix: you play `missions[yours][theirs]`
and your opponent plays `missions[theirs][yours]`, so you usually score
different things. `scaffold_pack.py` fills these names into
`plan.matchups`. Never retype or guess a mission name, and never infer scoring
from a name ("Meatgrinder" tells you nothing reliable about its VP).

**Choosing (the export lists several options).** Compare the list's unit jobs
(section 2) with each option's theme and recommend one, with two or three
reasons tied to named units. Examples:
- Lots of OC and durable holders → Take and Hold.
- Several hammers, deep strikers, kill-based resources (e.g. gaining a resource
  when a unit is destroyed) → Purge the Foe.
- Cheap, fast or infiltrating units, units that act while engaged or
  battle-shocked → Disruption or Reconnaissance.
- Units that can sit on far-flung objectives and survive → Priority Assets.
Then name what would change the answer: "if you expect a gunline, pick X".
Give one line of reasoning per option, not a full plan for each. Put it in
`plan.choice` (it prints under "Which disposition?").

**Playing into each opponent (every pack, one or several options).** For each
row of `plan.matchups`, write one short tip (about 15 words) about what the
OPPONENT's disposition theme means for this list:
- vs **Take and Hold**: they will fight hard for objective markers. Plan OC
  trades, and name your stickiest holder.
- vs **Purge the Foe**: they want kills. Hide or screen cheap, easy-to-kill
  units and characters, and keep reserves safe.
- vs **Disruption**: they want to spoil your plan in your territory. Keep a
  screen or reserve at home.
- vs **Reconnaissance**: they will spread out to take positions. Name the fast
  units or long guns that punish lone scouts.
- vs **Priority Assets**: they will commit to specific high-value points. Name
  the hammer that hits whatever they commit.
Ground each tip in a unit or rule from the list. Keep it about their theme, not
their mission's scoring. When it's a mirror (same disposition), say you're
racing them for the same thing.

In chat, the overview gets the recommendation (if there's a choice) and one
line saying the Matchups card has a row per opponent disposition.
