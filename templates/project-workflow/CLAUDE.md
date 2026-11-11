# <project>

Work is tracked in GitHub issues and the board at <board URL>. The full process is in `docs/process/workflow.md`.

## Rules for every session

- **Start from an issue.** Run `gh issue list` at the start. If the work has no issue, create one before changing code.
- **Branch per issue**, named `<issue#>-<slug>`, off an up-to-date default branch.
- **Never push to the default branch.** <Say here whether a merge deploys.> Changes reach it only through a pull request
  that Smitty merges.
- **Open the PR with `Closes #N`** and fill in the template. Run `/code-review` before asking Smitty to review.
- **Status lives on the board, not in docs.** Move the issue as work moves. Record findings as issue comments.
- **Bugs start with a test** that reproduces them.
