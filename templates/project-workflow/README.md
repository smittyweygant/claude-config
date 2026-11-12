# project-workflow

The issues, PR and deploy workflow Smitty uses in every project. The rules are in the shared `CLAUDE.md` ("Project
Workflow") and apply to every session. This directory holds the files a repo needs so the rules have something to
stand on.

| File | Goes to | What it is |
|---|---|---|
| `.github/ISSUE_TEMPLATE/{bug,story,task}.yml`, `config.yml` | the repo root | Issue forms |
| `.github/pull_request_template.md` | the repo root | PR template: `Closes #`, what and why, verification, deploy notes |
| `docs/process/workflow.md` | the repo | The loop in full |
| `CLAUDE.md` | the repo root | Project rules. Fill in the `<...>` blanks; merge by hand if the repo has one |
| `labels.sh` | run once | Creates the standard `type:*` and priority labels |

## Adopt it in a repo

```sh
P=~/development/<project>
T=~/development/claude-config/templates/project-workflow
mkdir -p "$P/.github" "$P/docs/process"
cp -R "$T/.github/." "$P/.github/"
cp "$T/docs/process/workflow.md" "$P/docs/process/"
[ -e "$P/CLAUDE.md" ] || cp "$T/CLAUDE.md" "$P/CLAUDE.md"
(cd "$P" && bash "$T/labels.sh" && gh repo edit --delete-branch-on-merge)
```

Then, in the repo's own issue and PR:

1. Fill in the blanks in `CLAUDE.md`, and say whether a merge deploys.
2. Add `area:*` labels for the project's parts.
3. Create a GitHub Project board with the columns Backlog, Ready, In progress, In review, Done, and link it in
   `CLAUDE.md`.
4. Open the change as a PR. Never push it straight to the default branch.

A repo that already has its own scaffolding keeps it. Compare, and adopt only what is missing.
