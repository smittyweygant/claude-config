# Presentation skill and rails

Plan for issue #25. The skill is `skills/akka-presentation/`.

## Goal

Build every presentation the same way: sources, storyboard, build, look at every frame. Keep the files that travel with a deck in one fixed set.

## Design

**One skill, one skeleton, both profiles.** `install.sh` copies `skills/<name>/*` into the shared dir, and both profiles link to it. `templates/` is not installed. The skeleton lives inside the skill so Claude can read it at run time on either profile.

```
skills/akka-presentation/
  SKILL.md           the method, language rules, visual defaults
  skeleton-guide.md  the document set and the rules for it
  skeleton/          README, SPEAKER-NOTES, PRESENTER-RUNBOOK, BRIEF, research/, handouts/
```

**Source.** Tyler Jewell's `akka-presentation` skill supplies the method, the audience split, the language rules and the corrections rule. An earlier customer-session draft supplies the document set and the speaker-notes format. The reference review is in the issue comments.

## Decisions

- **Draft files: move, keep the content.** `templates/presentation-docs/README.md` becomes `skeleton-guide.md`. `skeleton/` moves unchanged. The line added to `templates/README.md` is dropped, since `templates/` no longer holds them.
- **Tyler's machine-specific parts: left out.** His paths, deck engine, render script, ElevenLabs voice ID, loudness targets and Edge delivery do not apply here.
- **Narrated film: out of scope.** Add a section when a film is built.
- **Visual language: kept as a default.** A customer's template overrides it.
- **No hook.** Nothing here needs to be enforced by the harness. Revisit if the confidential-material rule is broken in practice.
- **Name.** `akka-presentation`, matching Tyler's, so the command is the same across the team.

## Known gap

`skeleton-guide.md` mentions `builder/assemble.py` (akka-decks), which is not in this repo. The guide says what to do for a deck built another way. Not changed here.

## Done when

See the checklist on issue #25. The last box, one real presentation, needs a deck from Smitty.
