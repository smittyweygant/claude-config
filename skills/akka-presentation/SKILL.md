---
name: akka-presentation
description: Standard method for building any presentation, deck, briefing, customer session or talk. Use when asked to design, build, restyle or review slides, a deck, a talk or a demo walkthrough. Sets the order of work (sources, storyboard, build, look at every frame), the language rules, the document set that travels with a deck, and the Akka visual defaults. Adapted from Tyler Jewell's akka-presentation skill.
---

# Presentation standard

Follow the steps in order. A deck fails when the storyboard is skipped or a frame is crammed.

## 1. Understand before designing

- Read the sources first: meeting notes, requirements, the audience, what they asked for.
- Sort what the audience may see from what is internal. Internal means pricing, competitors,
  other customers' names, roadmap dates, politics. Internal material goes in `BRIEF.md`.
  It never goes in the deck, the speaker notes or the deck's file name.
- Check every technical claim against the product docs and cite the source in the notes.
  Managed-platform figures never stand in for self-managed ones. Label laptop measurements as such.
- Ask only what is the user's call: audience, length, purpose, due date, live or rendered.

## 2. Storyboard before any build

Write `storyboard.md` and show it before building anything.

- **One spine.** One idea carries the whole piece. Everything else serves it.
- **One idea per scene.** Each scene gets a visual, the words to say, and a duration.
  Count about 2.5 spoken words a second. A scene that needs two ideas is two scenes.
- **Show, don't list.** A component list is not an architecture. Show flows, sequences,
  what moves where. Define each term in one plain sentence the first time it appears.
- **Say what went in.** If something was "built from a specification", show what the specification held.

## 3. The document set

Copy `skeleton/` (beside this file) into the presentation's folder. `skeleton-guide.md`
explains each file and the rules for them. One job per file:

| File | Holds |
|---|---|
| `README.md` | Goal, audience, agenda, slide map, sources of truth |
| `SPEAKER-NOTES.md` | Cue, Script, Land, Sources, per slide or section |
| `PRESENTER-RUNBOOK.md` | Pre-flight, environment, dry runs, recovery, cleanup |
| `BRIEF.md` | Status, decisions, blockers, facts to hold to. Customer-specific. Archive after the session |

A customer copy lives outside any public repo. Customer names stay out of a generic deck.

## 4. Build

- Use the tool the user already has for the deck. Do not invent a build system for one talk.
- Make each scene a pure function of time or of slide state, with nothing carried between
  frames. Then it scrubs, prints and captures.

## 5. Visual defaults (Akka decks)

These are defaults. A customer's template wins.

- Black ground, one yellow `#FFCE4A`, Instrument Sans 700 for titles, uppercase eyebrows.
- Hairline cards with even borders. Never a one-sided accent border. No rule bars beside words.
- Status colours only for status: cyan `#00DBDD`, green `#72D35B`, red-orange `#FF5400`.
- Mono type only for code and identifiers.
- Few, large elements per frame. The subject of the current sentence stands out. The rest steps back.
- Sizes on 1920×1080 with 150 px gutters: headlines 64–84 px, body 26–36 px, labels 20–26 px.
  Nothing overlaps. Nothing runs off the stage.

## 6. Language

- Every title, subtitle, panel sentence and bullet is a complete sentence. Labels, chips,
  table cells and captions may be short.
- Plain engineering statements. No selling words ("fast", "best", "under control", "prove").
  No claim the evidence does not carry.
- Say what is, not what is not. Rewrite "no cloud stack" as what the system does run on.
- Do not set the customer's dates. Offer milestones "to target with you" and "to discuss together".
- A customer-facing opening is personal: greet the named people, say what we appreciate, then give the overview.
- Match the audience's spelling (Canadian or British: cheque, centre).
- Never write "event store" or "design target".

## 7. Look at every frame

Render every slide to an image or PDF and look at it. Check for overlaps, text under lines,
cards on titles, anything clipped. Fix and re-render until each frame is clean.
Never hand over a frame you have not seen.

## 8. Corrections become rules

When Smitty corrects something, fix it everywhere it applies. Then add the rule to this file,
or to the deck's `README.md` if it holds for that deck only.
