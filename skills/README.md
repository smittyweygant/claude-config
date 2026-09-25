# skills/

Slash-command skills, installed to `$CLAUDE_CONFIG_DIR/skills/`.

- `akka-pr-review` — independent, read-only pre-push review for akka-org
  repos. Self-gates on the repo's git remote, so it's only relevant when
  actually working in an akka-org checkout regardless of which profile
  installed it.

Add more `<skill-name>/SKILL.md` directories here as reusable workflows
emerge.
