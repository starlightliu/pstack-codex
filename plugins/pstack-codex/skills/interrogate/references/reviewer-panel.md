# Codex reviewer setup

## Select the panel

Inspect the session's native subagent tool and the models enabled for it. Use explicit per-agent model selection or existing custom agents with known models. A reviewer may run on the coordinator's model. A cross-model panel requires at least two independent completed reviews with distinct, confirmed model IDs. Report whether the IDs represent different model families or different models within one family. A configured alias, requested model, or reviewer's self-identification alone cannot establish the actual model. Use host-visible agent metadata or tool events and record rejected or substituted assignments.

Apply the strongest mode that actually ran:

- **Cross-family panel.** At least two verified distinct model families. Use this when available. Report the actual model IDs and whether the original Claude and Grok roster was available.
- **Cross-model panel within one family.** Distinct confirmed IDs with independent reviewers. Label the family limitation.
- **Same-model or model-unconfirmed panel.** Independent subagents completed reviews, but cross-model execution could not be established. Label the mode as compatibility and say why. If the user required cross-model execution, report the requirement as blocked.
- **Single-agent compatibility.** With no usable independent panel, state that the original review is blocked. If the request allows a compatibility pass, conduct a single adversarial repro pass and report its evidence under that label. For an explicit cross-model-only request, stop at the blocker.

## Freeze and isolate the input

Record the Git base, HEAD, and working-tree scope. Preserve the staged and unstaged diff (including binary changes and deletions) and include relevant untracked files explicitly. Exclude credentials and unrelated local files. Give each reviewer a disposable copy of that snapshot or a detached worktree at HEAD with the same in-scope working changes applied. Use a uniquely named scratch directory inside an authorized writable root where both creation and cleanup are permitted. Check the scope in each copy before dispatching. Use separate scratch output paths and never let a reviewer edit the live workspace. For a design without a diff, share the same plan and baseline and give each reviewer its own prototype directory.

Dispatch in parallel where possible. Each reviewer gets the same scope and brief. Record completions and missing seats. Keep repro evidence available until the coordinator has rerun the findings, then remove only temporary worktrees and files created for this run.
