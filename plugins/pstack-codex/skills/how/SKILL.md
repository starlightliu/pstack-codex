---
name: how
description: "Trace how existing code works, where ownership lies, and which layer should own a change. Explain runtime flow with source references. Use why for historical intent."
---

# How

Explore the codebase to answer "how does X work?" questions. Produce architectural explanations at the level of a senior engineer onboarding onto a subsystem, enough to build a working mental model, not so much that it reads like annotated source code.

Give explorers and explainers read-only instructions. Use Codex subagents when the session allows delegation. Use the session default unless the user or a configured agent role selects an available model. If delegation is unavailable, trace the same angles and synthesize inline. Use [why](../why/SKILL.md) when the question is about historical intent.

## 1. Assess complexity

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

- **Simple** (one module, utility, or narrow question). Trace and explain in one pass using the [explainer prompt](references/explainer-prompt.md) without the explorer-findings section. Go to step 4.
- **Complex** (a subsystem spanning multiple files or services, a cross-cutting feature, a full architectural overview): go to step 2.

When in doubt, take the simple path.

## 2. Explore (complex only)

Decompose the question into 2 to 4 angles, each a distinct slice of the subsystem. Dispatch explorers concurrently within the session's limits. Give each the [explorer prompt](references/explorer-prompt.md) and its angle.

## 3. Synthesize (complex only)

Once the exploration is complete, reconcile the findings using the [explainer prompt](references/explainer-prompt.md). Verify disputed paths against the source. A separate explainer can do this when delegation is available.

## 4. Present

Present the synthesis with source references. For ownership or placement questions, cite the conventions and nearby callers that support the answer. Flag runtime paths or external behavior you could not verify.

## Output format

The explanation uses the sections defined in `references/explainer-prompt.md`, dropping any that do not apply: Overview, Key Concepts, How It Works, Where Things Live, Gotchas.
