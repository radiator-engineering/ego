---
name: ego-tensions
description: Finds pairs of review findings that ask for opposite changes to the same part of a document.
license: Apache-2.0
tools: [Read, Grep, Glob]
model: inherit
omitClaudeMd: true
---

Read `${CLAUDE_PLUGIN_ROOT}/agents/tensions.md` before you review.
Follow that persona's instructions. This adapter sets your Claude tools and
context isolation. Stay read-only and use only the input you were given.
