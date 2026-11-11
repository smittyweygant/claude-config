# Workflow: from idea to deployed change

All planned work and every known problem lives in GitHub. An item gets an issue first. A pull request (PR) carries the
change to the default branch, and merging may deploy it.

## Pieces

| Piece | What it is |
|---|---|
| Issue | One thing to do or fix, with what, why and "Done when" |
| Story | An issue for a feature, written from the user's side |
| Task | A sub-issue of a story: one piece that ships alone |
| Milestone | A group of issues that finish one plan |
| Board | One view of every issue, by status: Backlog, Ready, In progress, In review, Done |
| Branch | A line of commits for one issue, off the default branch: `<issue#>-<slug>` |
| PR | A request to merge a branch. CI runs and the diff is reviewed here |

Labels sort issues: `type:bug`, `type:story`, `type:task`, `type:chore`, `type:docs`; `p1` now, `p2` next, `p3` someday;
and `area:*` labels this project adds for its own parts.

## Where writing goes

| Writing | Home |
|---|---|
| What to do, why, and when it's done | The issue |
| Status | The board, and only there |
| Design for a large piece of work | `docs/plans/NNNN-slug.md`, linked from its story |
| A settled choice not to reopen | `docs/decisions/` |
| What changed and how it was checked | The PR description, which becomes the commit |
| Findings while working | Comments on the issue |

## The loop

1. **Capture.** Anything to do becomes an issue in a minute or less, from a template. An open issue is not a promise to
   do it. It is a promise not to lose it.
2. **Triage.** Add type, area and priority. Close what won't be done with `gh issue close N --reason "not planned"`.
3. **Ready.** Someone could start without asking a question: it has the what, the why and checkable "Done when" boxes.
   Large work gets a design doc first, and its pieces become sub-issues of a story.
4. **Branch.** From an up-to-date default branch: `git switch -c N-slug`. Move the issue to In progress.
5. **Build.** Small commits that each make sense alone. For a bug, the first commit is a test that fails and shows it.
   Findings go in issue comments.
6. **Pull request.** Push and open a PR with `Closes #N`, what and why, how it was verified, and deploy notes. CI must
   be green. Move the issue to In review.
7. **Review and merge.** Read the diff on GitHub. Questions go in PR comments. Squash-merge with
   `gh pr merge --squash --delete-branch`.
8. **Deploy and verify.** If a deploy workflow runs on the default branch, watch it with
   `gh run watch --exit-status`, then check the live system and the change itself. To back a change out, revert the
   squash commit through a new PR. A database migration can't be reverted that way; restore from a dump.

## Rules

- **Never push to the default branch directly.** Every change goes through a PR, even a one-line doc fix.
- **One issue per PR.** A PR that fixes two things gets split.
- **Every PR closes or references an issue.** If there is none, make one first.
- **Done means verified in the running system,** not just merged.
- **Changing production data:** a named dump first, a dry run that shows the diff, apply only after the owner says go,
  and a record of what was replaced.

## Daily use

```sh
gh issue list --label p1                 # what's urgent
gh issue view 2 --comments               # read an issue and its notes
gh issue comment 2 --body "Found: ..."   # record a finding
gh pr status                             # your open PRs and their checks
```
