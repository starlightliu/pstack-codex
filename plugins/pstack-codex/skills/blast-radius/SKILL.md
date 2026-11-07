---
name: blast-radius
description: "Assess the downstream impact of a specific code diff or compatibility change. Use when asked what a change could break in callers, APIs, schemas, or shared types, and prove the main safety assumption by running real code."
---

# Blast radius

Find what a change breaks somewhere else, before it ships. Use for "blast radius of X", "what could this break", or reviewing a small diff you don't trust yet.

Use [why](../why/SKILL.md) when the history behind a change affects its risk.

Listing the callers is not the job. The agent can grep those in a second. The job is the breakage grep won't show you.

## Don't trust your own writeup

A blast-radius writeup that sounds right is worthless. It reads as convincing whether or not it's true. So don't hand back the writeup. Find the one or two facts the whole thing depends on and prove them by running code.

### How sure are you

For each fact the change's safety depends on, get it as far down this list as is cheap, and say where it stopped.

1. You said so. Worthless on its own.
2. You pointed at the line. A real `file:line`, or the library's own source.
3. You showed the bad case can't happen. You walked the failure step by step and it doesn't reach.
4. You ran it. A script or test that calls the real code and fails loud if you're wrong.
5. You reproduced it in the running app.

Step 4 is usually one small script that imports the same library the app ships and calls the exact function you're worried about.

## Steps

1. Read the change. Establish the base and target, and include staged, unstaged, or untracked changes when the user put them in scope. Identify the changed contracts, symbols, and behavior. Use [why's code anchor](../why/SKILL.md#step-2-establish-the-code-anchor) for relevant commits and PRs.
2. Find the one fact it's safe because of. Most changes that look risky are safe because of a single fact, like "this call only drops already-dead cache entries and does nothing else". Find that fact. If it holds, most risky cases are cleared at once. Spend your time here, not on a long list of maybes.
3. Look where grep stops. Read the source of the library you call, and check its pinned version and any local patch. Work out when things run: microtasks, unmount and teardown, Solid versus React. Follow what a symbol search misses: the JSON an API returns, a DB column, a wire format, another language reading the same bytes, a feature flag, code three hops downstream.
4. Trace compatibility across request and response schemas, persisted data, and shared types to actual consumers. Cite `file:line` and distinguish confirmed, cleared, and unresolved paths. Record dynamic registration, external consumers, or generated clients you could not inspect. Text search helps find candidates, while tracing execution or testing establishes impact.
5. Prove the one fact. Write a script or test that runs the real code, run it, and paste what happened.
6. For a wide change, use the read-only review setup in [interrogate](../interrogate/SKILL.md#fan-out). Give each independent reviewer the same impact question and merge evidence. Report the actual reviewer mode or any skipped review.

## What to hand back

- **What it does.** What changed, including the part that isn't obvious.
- **The one fact it's safe because of.** State it, say which step you got it to, and show the proof. If you couldn't prove it, write unproven.
- **Risks.** Each names how it breaks, the `file:line`, how likely and how bad, and how to check. Paste the proof for the ones that matter.
- **Cleared.** What you checked and why it's fine.
- **Before you merge.** The cheapest test or repro that catches the real bug, including the script you wrote.

Use [unslop](../unslop/SKILL.md) to edit the final prose. Keep concrete findings and cite real code. Strip private material before any authorized public handoff.

**Reply:** the writeup above, with the one safety fact either proven or marked unproven.
