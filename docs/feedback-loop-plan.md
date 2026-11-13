# Feedback loop: mine session history for optimizations

Plan for issue #5. This doc plans. It builds nothing.

## Goal

Two goals, one data set.

1. **Estimate better.** Close the gap between the estimate posted on an issue and the actual measured after the PR.
2. **Spend fewer tokens.** Find where tokens go and change how we work to spend fewer.

The data set is one row per session, for every session on disk. Estimate fields stay blank where no estimate exists. Everything else is derived from the transcripts, with no new logging.

## What the first look shows

Data: 170 sessions with usage under `~/.claude-shared/projects/`, and 17 vault log entries with an estimate and an actual `all_total`.

**Estimates run high.** Actual divided by the midpoint of the estimate: median 0.73, range 0.42 to 1.59. Nine entries came in more than 25% under, six within 25%, two more than 25% over. Eight entries gave a range, and the actual fell inside it three times. The nine point estimates have a median ratio of 0.97, so point estimates are closer than ranges. The ranges are too wide to be useful.

**The spend is in a few long sessions.** The 170 sessions total about 1.73B processed tokens. The five largest hold 58% of it. One finances session ran 792 calls and 442M tokens, 26% of the total, at an average context of 558k per call. Sessions over 60 calls hold 93% of all tokens. The logged entries run 20 to 60 calls and 0.4M to 3M tokens. The estimate habit covers the cheap work. The cost sits where no estimate exists.

**Caveats.** The 17 entries are mostly finances work from two days. Per-issue actuals in the vault are slices of a session, so they cannot be checked against a whole-session total. Slicing needs call-index windows (slice 2).

## What to measure

`all_total` stays the headline. It is what the estimate rule predicts and what `usage.py` reports. Alongside it, per row:

| Field | Source |
|---|---|
| calls, input, cache write, cache read, output, `all_total`, fresh | `message.usage`, each message id once (same rule as `usage.py`) |
| average context, and its growth per call | `all_total / calls`, and a fit of context against call index |
| subagent tokens | the `subagents/` transcripts next to the session file |
| model | `message.model` |
| tool mix, tool errors | `tool_use` names, `tool_result` errors |
| compaction events | to be confirmed in the transcripts before slice 1 relies on it |
| active time | timestamps, with gaps over a threshold removed |
| human prompts | user lines with `origin.kind == "human"` |

Dollar cost is not in the first version. It needs a price table that goes stale. Add it once the token picture is clear.

**What "better" means, as numbers.**
- Estimate accuracy: median of actual over estimate between 0.9 and 1.1, and 80% of actuals inside the stated range. Today: 0.73, and 3 of 8.
- Spend: share of tokens in sessions over 60 calls, and `all_total` per merged PR. Today: 93% of tokens in sessions over 60 calls. A target waits for the baseline from slice 5.

## Joining sessions to issues

Each transcript line carries `gitBranch`, `cwd` and `timestamp`. Branches are `<issue#>-<slug>`, so the issue number comes from the branch name.

- Parse the issue number from every branch seen in the session. A session can touch several. Record all of them.
- Fallbacks, in order: `Closes #N` or `#N` in `gh pr create` and `gh issue` commands in `tool_use`; the first human prompt. Otherwise the row stays unlinked.
- Sessions on `main` or `HEAD` have no branch signal. Most non-finances work is like this. They stay unlinked and still count in the spend analysis.
- Slicing one session into per-issue tasks uses the call index where `gitBranch` changes. That is slice 2. Slice 1 stops at session level.

## Where things live

- **Script and docs:** this repo (`scripts/`, `docs/`).
- **The data set:** a generated file, gitignored, rebuilt on demand from the transcripts. Rows hold counts and ids, not prompt text. Project paths include customer names, so the file stays out of the repo. Confirm the repo's visibility before anything derived from the akka projects is committed.
- **Findings:** issue comments, per the workflow.
- **Log entries:** the vault note `Agent Work Estimation.md`, which is the one vault note Claude may write to from any project. Nothing else goes in the vault from this work.

## Estimate side

The vault entries are prose and tables with changing headers. Parsing them is lossy. Two steps:

1. Import the existing entries once, by hand-checked parse, into the same row file as estimate and actual fields keyed by issue number.
2. Change the logging rule so each new entry ends with one machine-readable line (issue, est and actual calls, `all_total`, fresh, output). That edit is a follow-up issue, since it changes `CLAUDE.md`.

Sessions from before the rule have actuals and no estimate: `26a6fe54` (the UI work), `2b8aea20` (#35 and #85), and the #99 plan inside `d1069352`. They stay in the set with blank estimate fields.

## Cadence

Start on demand: one command rebuilds the file and prints the summary. A scheduled weekly run waits until the output has proven useful. A per-PR hook is out. It would cost a call on every PR for a number that changes slowly.

## Decisions it can change

| Decision | Evidence needed |
|---|---|
| One issue per session, or `/clear` between issues | tokens per issue vs. call index, long sessions vs. short |
| Estimate constants (55k base, 1.2k per call, 1.6x design) | average context against call index, per session |
| Range width in estimates | ratio spread per work type |
| Subagent use | subagent share of tokens; review findings that held up |
| Plan depth and review rounds | design tasks vs. their revision cost |
| Model choice | rows by model, once more than one model has data |

## Slices

Each slice is one issue and one PR. Sizes are calls, and processed tokens, using the rule in `CLAUDE.md`.

1. **Session table.** `scripts/sessions.py` writes one row per session, with the fields above. Done when: every session on disk has a row; `all_total` matches `usage.py` on five sampled sessions; subagent tokens are included; compaction detection is confirmed or dropped. About 25 calls, 1.5 to 3M.
2. **Issue join and task slices.** Parse branches and fallbacks. Cut sessions into per-issue slices at branch changes. Done when: the 15 logged issues each get a slice and its `all_total` lands within 10% of the vault actual, or the gap is explained. About 30 calls, 2 to 4M.
3. **Estimate import.** Load the 17 vault entries into the row file. Done when: each logged issue has estimate and actual in one place. About 20 calls, 1.5 to 2.5M.
4. **Structured log line.** Add the machine-readable line to the logging rule and the vault note. About 10 calls.
5. **First analysis.** Estimate bias by work type, the long-session finding, constant fits. Posted as an issue comment, with proposed rule changes. About 25 calls, 2 to 4M.
6. **Automation.** Decide on cadence from what slice 5 shows.

Order: 1, 2, 3 in sequence. 4 can run anytime after 3. 5 needs 3. 6 last.

## Open risks

- The transcripts are the only source for actuals. If Claude Code changes the format, the script breaks. Slice 1 should fail loudly on unknown line types, not skip them.
- Subagent transcripts may not exist for every session. Slice 1 should count how many rows lack them.
- The sample is thin and finances-heavy. Treat the first analysis as a hypothesis list, not a verdict.
