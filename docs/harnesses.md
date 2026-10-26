# Harnesses

EGO runs in the same harnesses as EGM, from one set of skills and personas.
Install EGM first in the same harness; EGO calls it.

## Install

| Harness | Install EGM, then EGO |
| --- | --- |
| Claude Code | `claude plugin marketplace add google/elephant-goldfish-model && claude plugin install egm@egm`<br>`claude plugin marketplace add radiator-engineering/ego && claude plugin install ego@ego` |
| Claude Cowork | Add marketplaces `google/elephant-goldfish-model` and `radiator-engineering/ego` in the plugin panel. |
| Codex | `codex plugin marketplace add google/elephant-goldfish-model && codex plugin add egm@egm`<br>`codex plugin marketplace add radiator-engineering/ego && codex plugin add ego@ego` |
| Antigravity | `agy plugin install https://github.com/google/elephant-goldfish-model`<br>`agy plugin install https://github.com/radiator-engineering/ego` |
| ChatGPT | Workspace import: Admin > Plugins > Add > Import marketplace, repo `https://github.com/radiator-engineering/ego`, path `.agents/plugins` (after EGM). |

Install the whole plugin. EGO's skills read `agents/` and `docs/` at run time.

## Manifests

| Harness | Manifest |
| --- | --- |
| Antigravity | `plugin.json` (scans `skills/` and `agents/`) |
| Claude Code, Cowork | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`; agent adapters in `.claude-plugin/agents/` |
| Codex, ChatGPT | `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json` |

`plugin.json` holds the shared name, version and description. Keep the other
manifests in step with it.

## Finding the roots

- **`EGO_ROOT`**: in Claude Code, `${CLAUDE_PLUGIN_ROOT}`. Elsewhere, three
  directories above the running `skills/<skill>/SKILL.md`.
- **`EGM_ROOT`**: run `EGO_ROOT/scripts/egm-root.sh`. It asks Claude Code and
  Codex where EGM is installed. If it fails, or the harness has no shell, use
  the installed path of EGM's `egm-review` skill from the skill inventory; the
  root is three directories above its `SKILL.md`. Do not guess a cache path.

## Dispatching agents

| Harness | EGO's agents | EGM's reviewers |
| --- | --- | --- |
| Claude Code | `ego:ego-owl`, `ego:ego-tensions` | `egm:egm-design` and the rest |
| Antigravity | `invoke_subagent` with `ego-owl`, `ego-tensions` | `egm-design` and the rest |
| Codex, ChatGPT | a general subagent told to read `EGO_ROOT/agents/owl.md` or `tensions.md` first | a general subagent told to read the persona file EGM names |

Every agent needs a fresh context. If the harness has no subagent tool, stop:
the Owl cannot be blind in the Elephant's own context.
