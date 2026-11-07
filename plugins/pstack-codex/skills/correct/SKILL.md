---
name: correct
description: "Use documented, repeated agent mistakes in the current repository to propose or implement a durable local guardrail. Verify it against a real past mistake and reconcile existing project rules."
---

# Correct

The operator keeps correcting agents in this repo for the same mistakes. Change the repo so the next agent can't make them.

Assume every contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Design the repo so a change that looks right from one file is right for the whole repo.

## Find the mistake classes

First, read the effective project `AGENTS.md` and any scoped instructions, then recent commits, reverts, accessible review comments, and corrections the user supplied. Cite two distinct occurrences before classifying a repeat. Report a single incident as such and preserve existing rules that already cover the behavior.

## Fix each class at the highest level that works

1. **Eliminate it with architecture.** Give each piece of state one owner and each task one supported way. Hide internals so the wrong import fails. Replace hand-synced lists with one source of truth. Delete old ways and dead code an agent would copy.
2. **Enforce it with types so the bad state can't be written.** If bad code still compiles, add a lint or CI check whose error names the file, type, or function to use instead. If the pattern is already common, fail only when a change adds more.
3. **Test the behavior.** Fix or delete any test that still passes when the behavior it checks breaks, or that fails when only the internals change.
4. **Write docs or agent rules last, only for judgment calls.** Nothing fails when an agent skips them.

## Fix and prove

Propose the smallest effective fix with its scope and impact. Implement only changes covered by the user's request. Prove each new check rejects a real past mistake and accepts the corrected behavior. Use the repo's existing check entry point and report local versus CI results separately. Commit only when authorized. Keep global rules and other projects outside scope unless separately confirmed.

## Keep the rule table

Use the repo's rule inventory where it has one. Pair each retained rule with its enforcement or with the judgment it still requires. Update a matching rule in place instead of duplicating it. Remove a redundant rule only after the replacement prevents the demonstrated mistake and the change is in scope.

**Reply:** each class with its evidence, the level you picked, and why a higher level didn't work.
