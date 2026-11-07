# Architect runner prompt

The orchestrator passes this file through to every parallel candidate runner during Phase B and fills in the variable inputs around it: the task, the Phase A grounding artifacts, the isolated working directory, and the path to write outputs. The working directory is a git worktree when available, otherwise a per-runner subdirectory under the sketch dir. What matters is independence between candidates.

You are producing one candidate for [pt-architect](../SKILL.md). Deliver a type sketch, function signatures, module map, and rationale following the [rationale template](rationale-template.md).

Apply the following discipline. The orchestrator compares candidates on these axes to pick a base.

- Caller's usage first. Write the README-style usage and two or three real call sites before the types, then derive the type sketch from them. The usage is the spec. The two must agree, so reconcile the sketch to the usage, not the reverse.
- Data structures first. Get the core types right and the code becomes obvious. Trace each dominant access pattern through the proposed structure. If the answer is "we'll add a map / index / cache later," the structure is wrong.
- Interface depth. Compare the capability hidden behind the public surface relative to the size of that surface. Prefer a simple interface that pulls complexity into the callee, even when the implementation becomes less simple. Do not put transport or wire types on the public API. Parse into domain types behind the interface.
- If two actors can write the same state, trace the result. Prefer separate state with a merge at the read boundary where it avoids shared mutation.
- Make boundaries visible. `not implemented` errors for bodies, `// TODO` pseudocode for tricky logic, doc comments stating intent and invariants. A reader should trace data from input to output by reading types and signatures alone.
- Encode invariants in types where possible, then use runtime checks or prose where needed.
- Validate at boundaries and trust the parsed types inside. Keep business logic in pure functions and the shell thin.
- Single source of truth per invariant. Derive instead of sync.
- Where state transitions can be retried, trace what happens if an operation runs twice or crashes halfway.
- Keep call chains short. Flatten layers that add navigation without hiding useful complexity.

Develop your design independently from the shared evidence. The coordinator will compare candidates and decide which ideas to combine.
