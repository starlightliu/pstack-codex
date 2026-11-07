---
name: pt-arena
description: "Compare independent candidates for the same task, score them against a shared rubric, and verify one synthesis. Use when asked to run an arena or compare distinct approaches before committing to one."
---

# Arena

Track Frame, Fan out, Cross-judge, Pick, Graft, and Verify with the available Codex planning tool.

## Phase A: Frame

Every candidate gets the same prompt, so the prompt is the contract.

1. State the artifact each candidate is producing.
2. Derive the rubric, 3-6 concrete gradeable criteria for what success looks like on *this* task. It is the picker's tool in Phase D. Candidates only see the task.
3. Pick at least two Codex subagents by default. Use available model choices or user-configured roles. Prefer distinct confirmed models for judgment-heavy work. Independent same-model runners can help with generation work. Record failed assignments, any fallback, and the actual model identities the host can confirm. Follow the model identity rules in [the reviewer setup](../pt-interrogate/references/reviewer-panel.md#select-the-panel). Honor explicit model and independence requirements.
4. Give each candidate an identical input snapshot and a distinct output location. For edits, use isolated Git worktrees or disposable copies under an authorized writable root. For prose, separate replies are enough. Keep candidates from reading one another's output until synthesis.

## Phase B: Fan out

Start the Codex subagents concurrently within the session's limits. Give each the same task and grounding, its own output location, and instructions to produce the artifact and a rationale naming alternatives and rejections.

Record missing candidates. If only one returns, report that the comparison could not run. Without delegation, proceed with a labeled serial comparison only when the user's scope allows it. Keep any requirement for independent or cross-model work open.

## Phase C: Cross-judge

Before launching a judge, verify that the session offers a model family different from the coordinator's. Distinct model variants in one family do not qualify. If only one family is available or the coordinator's family is unknown, skip Phase C and score the candidates yourself.

Once candidates finish, give an eligible read-only judge the rubric and candidates by anonymous label. It scores each criterion and recommends a base with reasons. Confirm the model family from the host's execution metadata. If the host cannot confirm it, report the review as unconfirmed and keep the cross-family step open.

## Phase D: Pick a base

Read every candidate end to end before picking. Score each against the rubric criterion by criterion, not on holistic feel, and compare with the cross-judge when Phase C ran one. Agreement on the base confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding.

Pick the base a future maintainer can extend most easily without breaking invariants. When candidates tie, prefer a clearer boundary or a smaller public API.

## Phase E: Graft

Read each losing candidate again for one or two ideas worth adapting. Integrate each idea into the chosen design and check that it preserves the base's invariants.

If the candidates converge on one shape, that is strong agreement. Note it and ship the consensus shape. No graft is needed. If they wildly diverge, Phase A was under-specified. Reframe and re-run rather than averaging the divergence.

## Phase F: Verify

Check the synthesized artifact against the rubric. Run relevant tests or replay an example through the real artifact. If verification fails, revisit the framing or the graft that introduced the failure. Keep only verified results and report any remaining gaps. Clean up only temporary candidate locations created for this run.

## Outputs

One synthesized artifact, with a short synthesis note alongside naming the base and why, the cross-judge's verdict or that Phase C skipped the judge, each graft with its source candidate, what was rejected and why, any convergence or dropouts, and the verification result.
