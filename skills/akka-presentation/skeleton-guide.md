# Presentation documents

The documents that accompany a presentation. Copy `skeleton/` into the presentation's folder and fill it in.

## The set

| File | Answers | Lifespan |
|---|---|---|
| `README.md` | What is this? Goal, audience, agenda and timing, slide map, sources of truth, where things live | Lasts as long as the deck |
| `SPEAKER-NOTES.md` | What do I say and show? One section per slide (or per agenda section when the presenter goes ad hoc): Cue, Script, Land, Sources | Lasts. Feeds the teleprompter |
| `PRESENTER-RUNBOOK.md` | How do I run it? Pre-flight, environment, dry runs, run-of-show pointer, recovery, cleanup | Lasts. Customer copies add timing and blockers |
| `BRIEF.md` | Where do we stand? Asks, decisions, blockers, open questions, facts to hold to, deliverables, status | Customer-specific and time-bound. Archive after the session. A generic deck has none |
| `demos/` | Click sheets, checks and resets, by beat ID | Lasts |
| `teleprompter/` | The script text alone, generated from SPEAKER-NOTES. Never edited by hand | Generated |
| `research/` | The material behind the claims: source pages, drafts, analyses | Lasts |
| `handouts/` | What the audience gets | Per session |

## Rules

1. One job per file. Status lives only in `BRIEF.md`. Mechanics live only in the runbook. Words live only in the speaker notes.
2. Uppercase names for the four standard documents. Lowercase for everything under `research/` and `handouts/`.
3. SPEAKER-NOTES format, per unit: `Cue` (what is on screen, when to click), `Script` (the exact words for a teleprompter, or `[bracketed]` cues only when the presenter goes ad hoc), `Land` (the points that must land), `Sources` (where the facts come from). A line `>>> ... <<<` marks a demo boundary. A line of three hyphens inside a script starts a new teleprompter page. A line that is entirely `[like this]` is an on-screen cue.
4. A customer copy lives outside any public repo. Customer names stay out of the generic deck.
5. When a slide and its source disagree, fix the slide and cite the source. The source is authoritative.
6. Numbers carry what they measure and where they came from.
7. `BRIEF.md` holds the do-not-overclaim list. Anything a customer can check goes there with the safe wording.

## Tooling this assumes

`builder/assemble.py` (akka-decks) builds the deck and a `runsheet.md` from SPEAKER-NOTES and the click sheets, and writes a teleprompter when a section has spoken script. For a deck built another way, keep the format and drop the tooling lines from the runbook.
