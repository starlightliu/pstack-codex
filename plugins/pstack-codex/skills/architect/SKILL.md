---
name: architect
description: "Design a code change before implementing it. Ground the design in existing code, compare distinct type and module sketches, then carry the chosen shape through implementation when requested."
---

# Architect

Sketch types, signatures, class shapes, and module boundaries with `not implemented` bodies and pseudocode. Compare candidate designs and synthesize one. Implement it when implementation is in scope.

## Start

Track one item per phase in the available Codex planning tool.

1. Ground
2. Sketch
3. Agree
4. Implement
5. Scrap

## Phase A: Ground the problem

Use [how](../how/SKILL.md) to trace each relevant subsystem, including callers, data flow, and boundaries. If the working tree differs from the committed baseline, say which one the design preserves and verify the usage examples against it. If the design redefines ownership or layering, use [why](../why/SKILL.md) to turn supported historical rationale into design constraints.

Skip Phase A only when the work is genuinely greenfield with no surrounding system to integrate.

## Phase B: Sketch

Follow [arena](../arena/SKILL.md) with the design task and the Phase A evidence. Give each runner the same [runner prompt](references/runner-prompt.md). Use available Codex subagents. If delegation is unavailable and independent candidates are optional, sketch two alternatives inline and label that mode.

Require at least two structurally distinct candidates before synthesis. Vary ownership, data flow, or the module boundary. Two adjustments inside the same shape count as one candidate.

Screen every candidate against [`references/design-red-flags.md`](references/design-red-flags.md) before synthesis. Assume the next contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Prefer the design where a change that looks right from one file is right for the whole repo.

Compare viable candidates on interface depth. Prefer the design that hides more complexity behind a smaller, simpler public surface. A rich interface can keep call chains short by concentrating capability instead of scattering it across layers.

Arena returns one synthesized design package. Its synthesis decision fills the rationale's "Synthesis decision" section.

## Phase C: Agree (opt-in)

When implementation is in scope, proceed with the synthesized design unless the user requests a checkpoint. For a design-only task, hand off the sketch and rationale.

If the user requests a checkpoint, present the synthesized design and wait for their decision before implementing.

Keep the sketch reviewable on its own. Commit it separately only when that fits the authorized workflow. Use [interrogate](../interrogate/SKILL.md) when the user requests an adversarial review of the chosen design.

If the human pushes back on the shape (in a checkpoint or after the fact), treat that as Phase A evidence. Re-ground and re-run Phase B before writing more code.

## Phase D: Implement against the sketch

Replace `not implemented` bodies with code, pseudocode with logic. The synthesized sketch is the contract. Deviations from it are signal to surface, not friction to absorb silently. If a function needs a parameter the sketch didn't anticipate, ask whether the sketch was wrong, the requirement was missed, or the implementation is overreaching.

## Phase E: Scrap when the architecture is wrong

If implementation repeatedly exposes a wrong boundary or state model, revise the architecture before adding workarounds.

The signal is a *pattern*, not single instances. Tells:

- The same shape of workaround appearing repeatedly across unrelated code.
- Multiple unrelated edge cases that all need special-case branches.
- Types that need escape hatches (`any`, casts, optional fields always set in practice) to compile.
- The "we need a lock" reflex when the sketch said the state wasn't shared.
- Callers having to know the abstraction's internal rules to use it.
- Two or more independent Phase D deviations of the same shape across the implementation.

Use judgment. A few edge cases don't condemn an architecture. Some problems are legitimately complex. Complexity in the data is not complexity in the design.

When you scrap:

1. Trace what has been built with [how](../how/SKILL.md).
2. Redesign with the new constraints in view.
3. Remove redundant parts before adding new ones.
4. Return to Phase B and compare the alternatives again.

## Outputs

The caller's usage is written first and the type sketch derived from it. One file with new types and signatures for small changes. Module map plus type definitions for larger work. The rationale ships alongside, shaped per `references/rationale-template.md`, including the usage sketch and the synthesis decision.
