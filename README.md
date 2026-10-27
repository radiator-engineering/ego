# EGO: Elephant, Goldfish, Owl

EGO adds a third role to Google's
[Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model)
(EGM). In EGM the Elephant drafts a design document and Goldfish reviewers,
who remember nothing, attack it. The Elephant then decides which attacks
stand, so it grades its own work.

EGO adds the **Owl**, a judge that remembers only the argument. It rules on
disputes blind: it never learns which side wrote the document. Questions of
value go to the person.

## What it changes

| EGM | EGO |
|---|---|
| The Elephant labels each finding CONTEST or PROPOSE FIX and that label stands. | The Elephant answers FIX, CONTEST or REFRAME. The Goldfish replies once. The Owl rules on each dispute. |
| Findings are deduplicated and sorted by severity. | `ego-tensions` finds pairs of findings that ask for opposite changes, and sends them to the person. |
| Two outcomes. | Four verdicts: SUSTAIN, OVERRULE, REFRAME, ESCALATE. |
| At the re-audit cap, leftovers become "accepted trade-offs". | Every leftover Blocker or Major ends as a fix, a recorded ruling, or a person's answer. |
| Settled arguments return each round. | Rulings go into the document's `## Decisions` section, which later Goldfish read. |

The Owl follows five rules: rule only after both sides speak, positions are
blind and in random order, a position wins only on quoted evidence, value calls
escalate, and the Owl never writes the fix.

## Install

EGO runs in the same harnesses as EGM: Claude Code, Claude Cowork, Codex,
Antigravity and ChatGPT. Install EGM first in the same harness. Claude Code:

```sh
claude plugin marketplace add google/elephant-goldfish-model
claude plugin install egm@egm
claude plugin marketplace add radiator-engineering/ego
claude plugin install ego@ego
```

Codex:

```sh
codex plugin marketplace add google/elephant-goldfish-model && codex plugin add egm@egm
codex plugin marketplace add radiator-engineering/ego && codex plugin add ego@ego
```

The others are in [docs/harnesses.md](docs/harnesses.md).

## Use

- `/ego:ego-review <doc>` (Claude; other harnesses pick the `ego-review` skill): EGM's staged review with the EGO changes. It reads
  EGM's own review skill from the installed EGM, so EGM updates carry over.
- `/ego:ego-resolve`: resolve any Goldfish report (for example one written by
  `/egm:egm-review`) with the Owl.
- Reviewing a document someone else owns: pass `Mode: suggest` and
  `Owner: <name>` to either skill. EGO leaves the document untouched. It
  writes `suggested_edits.md` and `proposed_decisions.md` for the owner and
  addresses the value calls to them.

Drafting and brainstorming stay in EGM: `/egm:egm-brainstorm`,
`/egm:egm-draft`.

## Layout

| Path | What it is |
|---|---|
| `agents/owl.md` | The Owl (`ego-owl`). |
| `agents/tensions.md` | The tension finder (`ego-tensions`). |
| `.claude-plugin/agents/` | Claude adapters: read-only tools, no `CLAUDE.md`. |
| `skills/ego-resolve/` | Resolution with the Owl; replaces `egm-resolve`. |
| `skills/ego-review/` | EGM's review plus four overrides. |
| `scripts/egm-root.sh` | Finds the installed EGM. |
| `scripts/blind-check.py` | Strips authorship leaks from Owl positions. |
| `docs/harnesses.md` | Install, roots and agent names per harness. |
| `docs/measures.md` | How to tell whether the Owl helps. |

## Limits

- `ego-review` follows EGM's `egm_review/SKILL.md` by reference. If EGM renames
  that file or the `egm-resolve` hand-off, the overrides need an update.
- Not yet built: an antithesis lens for brainstorming, and an Owl ruling when
  two instances of the same reviewer disagree.
- Not yet measured. See `docs/measures.md`.

## License

Apache-2.0. EGO contains no EGM source; it calls the installed EGM plugin.
