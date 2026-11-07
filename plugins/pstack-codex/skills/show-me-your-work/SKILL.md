---
name: show-me-your-work
description: "Produce an auditable decision and verification trail for a specific run using actual actions, command results, and retained evidence."
---

# Show me your work

Keep one canonical log.

## The format

A single TSV file, one row per decision. Cells stay single-line. Evidence is a pointer, not prose.

Copy `references/decision-log-template.tsv` (the header row) to start a clean log. Columns:

- **ts.** ISO8601 timestamp.
- **phase.** The phase or workstream.
- **decision.** What was chosen or done, one line.
- **why.** The reason in plain words. If a principle drove it, say it plainly, not as a jargon tag.
- **evidence.** A link or path that proves it: commit SHA, PR number, `file:line`, or an artifact, trace, or screenshot path. Never a paragraph.
- **result.** The outcome or predicate state: `tests green`, `reverted`, `pixel-diff 0`, `INCONCLUSIVE`, `open`.

An example, plain-spoken so a reviewer reads it at a glance.

```
ts	phase	decision	why	evidence	result
2026-05-24T09:02:00Z	frame	counted the work first, about 100 components and roughly 75 hours	wanted to know the size before starting a long run	commit 3a9f1c2	found 5 things to sort out before starting
2026-05-24T09:40:00Z	harness	took screenshots of the old version before changing anything	so we can compare old against new and catch any visual change	scripts/snapshot.sh, baseline/	saved 120 reference screenshots
2026-05-24T11:15:00Z	widget	moved the widget styles over without changing how it looks	keep the change small and the result identical	commit 7c21e0a, pixel-diff 0	looks identical, tests pass
2026-05-24T12:30:00Z	widget	threw out a helper's work because its screenshots were blank	checked the real files instead of trusting its summary	worktree reset	reverted, tightened the instructions for next time
```

## Logging a row

Write each entry the way you'd tell a teammate what you did. Use concrete actions and outcomes. Use [unslop](../unslop/SKILL.md) on the prose while preserving command output and evidence.

Resolve helpers from this skill directory. Use [log.sh](scripts/log.sh) as `bash <skill-dir>/scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>`. In PowerShell 7, call [log.ps1](scripts/log.ps1) from the current shell using `& (Join-Path $skillDir 'scripts/log.ps1') $log $phase $decision $why $evidence $result`. Pass values as individual arguments. Both helpers stamp UTC time, write the header on first use, flatten tabs and line breaks, and neutralize cells beginning with `=`, `+`, `-`, or `@`. After an interrupted or failed append, check the last rows before retrying.

Log decision points and checkpoints, not every action: a fork chosen, a unit completed with its verification result, a pivot or revert with its trigger, a blocker surfaced, a gate fixed. For loop runs, one row per iteration. Skip the trivial and self-evident.

A run is one agent conversation, including its later turns and any summary of it. A pickup, a replacement agent, or a new chat starts a new run. When a run adds to a log that already has rows, its first row has phase `start`, and so does its first row after another run's `start` row. So a run that comes back to a log in a later turn first reads the log's last rows to see whether another run wrote since. A `start` row names the `ts` range of the rows before it that this run did not write, and its evidence names this run, such as its agent id. Use phase `start` for nothing else.

## Where it lives

By default the log is a working artifact, not committed. Keep it at `decisions.tsv` in the work dir, or `.audit/<task-slug>.tsv` when several efforts run at once, and leave it out of git.

Include the log in a commit only when authorized and when the evidence is safe to share with that audience.

## Rules

- Append-only. A wrong call gets a new row that supersedes it. Never edit or delete history.
- Prefer evidence produced by maintained project scripts and tests. Give one writer responsibility for the canonical log.

## Audit the log against the transcript

Audit the log against the active conversation's visible tool calls and results, Git changes, and saved artifacts. When a Codex session ID and its authorized export are available, use that specific session only. A supplied `codex exec --json` event log also works. Avoid searching other session histories. Name which evidence sources were actually available and mark planned and unverified checks separately. Walk the rows in each stretch of this run:

- Check that every row maps to a real decision or action.
- Check that each row's evidence resolves and shows what the row claims.
- A fork, pivot, or abandoned approach that shaped the work but isn't logged is a gap. Add it.

Correct the log, not the story. The audit never edits or removes a row, even an invented one. When a row records neither a real decision nor a real action, or its claim or evidence is wrong, add a row that supersedes it with what actually happened and a pointer that resolves. This audit does not check rows outside this run's stretches. If this run's own work shows one of them is wrong, supersede it like any wrong call.

## Cross-model review of the trail

When the runtime supports it, ask an independent subagent on a confirmed different model family to audit the trail and its accessible run evidence. Give it the log and permitted evidence excerpts. If only a same-family reviewer runs, label the review accordingly. If no independent reviewer runs, state that and report the coordinator's evidence audit separately.

- Decisions logged with weak or absent evidence.
- Verification steps skipped or claimed without proof in the transcript.
- Choices that look risky in hindsight (premature, scope-creeping, papering over a symptom).
- Gaps the user would otherwise miss on a casual skim.

Summarize the objective, decisions, changed files, commands actually run, evidence and outcomes, any failures and recovery, and open checks or risks. Keep the details in the log. End with an "Attention" section giving the review mode and confirmed reviewer model if available, followed by flags linked to specific rows or evidence.

## Reviewing the trail

Read top to bottom, follow the evidence pointers, spot-check. GitHub renders a committed TSV as a table. `column -s$'\t' -t decisions.tsv` renders it in a terminal.

## Composing this skill

Other skills route their audit trail here instead of inventing one. Reference it by name and let it own the format. Don't restate the columns.
