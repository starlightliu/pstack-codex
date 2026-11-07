---
name: interrogate
description: "Run an adversarial panel against a specific change or design and report only defects that reproduce. Identify the actual model diversity and review mode."
---

# Interrogate

Adversaries try to break a change or a design. A finding survives only when a run proves it. Report the findings. Do not apply fixes.

## Frame

Use the user's scope, or the branch diff from its merge base through the working tree. State intended behavior and relevant boundaries in your own words using the request, commits, and accessible PR description. Clarify material ambiguity before defining a failure.

## Fan out

Follow the [reviewer setup](references/reviewer-panel.md) to choose the mode and isolate the snapshot. Give every reviewer the same scope, intent, and brief without sharing other reviewers' findings:

> Break this change. Prove each finding with a run against the real code, such as a failing test, a repro script, or command output that shows the wrong behavior. For a design or plan, run a prototype or probe the current tree. Keep repros in your own worktree. Report each finding with a title, the exact command, the output it printed, and the output the intent requires. Leave out anything you did not run. That covers style, naming, structure, and risks that need a future change to matter. No findings is a valid result.

## Verify

Re-run each finding independently against the same snapshot with its repro in a separate scratch copy. Keep it if the observed output violates the stated intent. Drop unproven claims and merge findings with the same root cause. Keep every verified failure regardless of which reviewer found it.

## Output

- **Intent**: the restatement.
- **Mode and reviewers.** State completed mode, confirmed model IDs, unavailable seats, and any unmet diversity requirement. If blocked, name the prerequisite and leave the findings verdict open.
- **Findings**: for each verified finding, the command, its output, how it breaks the intent, and the adversaries that found it. Say "no verified findings" when none survive.
- **Dropped**: for each adversary, the count of dropped findings and why.
