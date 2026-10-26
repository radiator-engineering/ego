---
name: ego-review
disable-model-invocation: true
description: >-
  Run EGM's staged design-doc review with the EGO changes: tension detection
  after each stage, the Owl in place of the Elephant's self-judgment, and a
  stop rule that leaves no finding buried as an "accepted trade-off".
---

# EGO: Review

EGO does not copy EGM's review. It runs EGM's `egm-review` skill as written,
with four overrides. When EGM changes, this skill follows it.

## Step 0: Find EGM

Run `"${CLAUDE_PLUGIN_ROOT}/scripts/egm-root.sh"`. It prints EGM's install
root; call it `EGM_ROOT`. If it fails, show its message and stop.

Read `EGM_ROOT/docs/claude.md`, then `EGM_ROOT/skills/egm_review/SKILL.md`.
Follow that skill in this thread, with these rules for paths:

- In every EGM file, read `${CLAUDE_PLUGIN_ROOT}` as `EGM_ROOT`. EGM's personas
  and rubrics live there, not in EGO.
- In this file, `${CLAUDE_PLUGIN_ROOT}` is EGO's root.
- Dispatch EGM reviewers by their agent names (`egm:egm-design` and the rest)
  and EGO agents as `ego:ego-owl` and `ego:ego-tensions`.

Where EGM and the overrides below disagree, the overrides win.

## Override 1: Tensions after every stage

After EGM writes a stage's report and before resolution, dispatch
`ego:ego-tensions` with the report path and `TargetFile`. Append its
`## Tensions` block to the report. A tension skips the Elephant and the Owl and
goes to the person as a call in `ego-resolve`.

## Override 2: Resolve with the Owl

Wherever EGM says to invoke or follow `egm-resolve`, read
`${CLAUDE_PLUGIN_ROOT}/skills/ego-resolve/SKILL.md` and follow it instead, with
the same `TargetFile`, range and findings, plus the stage's Tensions block.

## Override 3: Goldfish see the Decisions

Add this line to every reviewer dispatch:

> The document's `## Decisions` section records settled questions. Do not
> raise a finding that reopens one unless you cite the evidence its "Reopen
> only with" line names.

## Override 4: The stop rule

EGM caps each stage at one re-audit and then records residual findings as
accepted trade-offs and moves on. EGO replaces that step. At the cap, every
residual finding must end as one of:

- an applied fix,
- a recorded ruling in `## Decisions`, or
- a call the person answered.

Run `ego-resolve` on the residuals to get there. Do not advance a stage while a
residual Blocker or Major is in none of those states. Nits may stay open; list
them in the report.
