# skills/

Slash-command skills, installed to `$CLAUDE_CONFIG_DIR/skills/`.

- `akka-pr-review` — independent, read-only pre-push review for akka-org
  repos. Self-gates on the repo's git remote, so it's only relevant when
  actually working in an akka-org checkout regardless of which profile
  installed it.
- `hemingway` — full Hemingway-style rewrite/draft with an "Iceberg Analysis".
  On demand only; the always-on voice lives in `CLAUDE.md`.

- `akka-presentation` — the method, language rules and document set for
  building any deck or talk. Adapted from Tyler Jewell's skill. Ships a
  `skeleton/` of companion docs. Design: `docs/presentation-skill-plan.md`.

Add more `<skill-name>/SKILL.md` directories here as reusable workflows
emerge.
