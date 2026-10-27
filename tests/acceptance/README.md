# Independent acceptance lane

I wrote these checks from the change request before reading the implementation changes. The checks read artifacts. They do not run the prose skills or generate model replies. `test_validators.py` uses synthetic records to test the validators. Passing unit tests do not establish that EGO passes acceptance.

Run validator unit tests:

```sh
python3 -B -m unittest discover -s tests/acceptance -v
```

Check that the skill names `scripts/blind-check.py`, then run that script without a model:

```sh
python3 -B tests/acceptance/check_blinding_script.py skills/ego-resolve/SKILL.md
```

The checker finds the script relative to the supplied skill’s repository root. The script must be present, as added in implementation PR #1. The frozen baseline fails because it has neither the script nor its command. The candidate must remove two seeded leaks and report 2. A second check must report 0, and the evidence text must remain. This script test does not show what a model sends to the Owl.

## Evidence required from a real run

Use `fixtures/target.md` and `fixtures/scenarios.json` in an isolated scratch directory, never this checkout's implementation files. Record the harness and model names, exact source hashes, date, prompts, tool calls, replies, and the turns that request and grant approval. Keep the frozen baseline and candidate inputs separate. Load the actual skill under test, not a rewritten implementation in a test prompt. All testing must leave `agents/owl.md` unchanged.

Run these cases with the baseline and candidate:

1. Suggest: pass `Owner: Alex`, `Mode: suggest`, all three findings and non-author context. Preserve the original bytes as `target.before.md`. Inspect the actual outcomes. If the fixture does not produce SUSTAIN, OVERRULE and ESCALATE, report the result without changing the labels. Save the pre-filter leak probe and actual outbound dispatch. After Step 6 ends the turn, reply in a new turn to approve suggestions while leaving the rollout call open. Check that the exact proposed SUSTAIN edit is `120` to `90`, the queue overrule is D1, and the rollout is D2. This order identifies which decision the rerun must respect. A model may answer FIX to the alert finding and skip the Owl. To test all three verdicts with fixed inputs, supply controlled Elephant and Goldfish replies. Label that run as a controlled integration test. Do not describe those replies as observed model choices.
2. Rerun: preserve the original `proposed_decisions.md` as `proposed_decisions.before.md`, and submit F2 with no new evidence. Save this invocation’s report and JSONL separately from earlier rounds. An empty invocation JSONL is valid if the only finding is dropped. Check that a real Goldfish received the prior decisions, not merely that the resolver dropped F2 later. The validator checks whether the resolver dropped F2. Use the dispatch transcript to check what the Goldfish received.
3. Owl records: retain every actual outbound packet, random-draw tool command/output and full reply independently of the skill's own record. Run `owls` on the suggest bundle. Compare exact sections and letter joins; a record claiming `blind-check: pass` alone is insufficient.
4. Leak probe: introduce `my draft` and `egm-design` once each into one pre-filter position, with no other leaked names in either pre-filter position. Capture the actual filtered packet and run `leaks`. Do not edit a record afterward to make the probe pass.
5. Concessions: use the controlled reply inputs in the scenario to exercise two concessions plus one actual Owl dispute. Label this a controlled integration test, not spontaneous Goldfish behavior. Apply the tested `docs/measures.md` instructions and save resulting integer counts in `measures.json`. Check that the harness made no Owl calls for concessions. `1/1` and `3/3` are both 100%; percentages alone cannot detect the denominator error.
6. Defaults: omit both optional inputs. Execute baseline and candidate with identical findings, context, approval, date and random draws. Keep all raw outputs; save baseline artifacts under `baseline/`. Confirm Step 6 ends the turn before any edit and Step 7 subsequently edits the target. Run the strict byte comparisons. Uncontrolled phrasing and random draws can change the output bytes. Record such comparisons as inconclusive. Keep the differences in the evidence.

For each case, first demonstrate a failing **real baseline run**, or rerun a version with the corresponding protocol change reverted in scratch. Save the failure and passing candidate evidence. The unit-test mutations are not substitutes for this requirement. They show only that the validator rejects the corresponding corrupt artifacts.

No live-run harness is available. Do not claim six accepted requirements based on this package. The baseline instruction audit in `baseline_assessment.md` establishes missing protocol instructions, not model outcomes.

## Artifact validator interface

```sh
python3 -B tests/acceptance/check_artifacts.py suggest /absolute/path/to/suggest
python3 -B tests/acceptance/check_artifacts.py rerun /absolute/path/to/rerun
python3 -B tests/acceptance/check_artifacts.py owls /absolute/path/to/suggest
python3 -B tests/acceptance/check_artifacts.py leaks /absolute/path/to/suggest
python3 -B tests/acceptance/check_artifacts.py concessions /absolute/path/to/concessions
python3 -B tests/acceptance/check_artifacts.py defaults /absolute/path/to/default
```

Missing evidence fails, never skips. Exit zero means the artifact assertions passed. Separately review the model identity and transcript. The checker does not verify model identity, whether evidence is true, whether draws are random, which sources the harness loaded, turn boundaries, Markdown validity, full EGM stop-rule execution, or whether a reported context block faithfully lists all sources read. Review those directly in the preserved transcript. `proposed_decisions.md` may acquire other entries on reruns; the checker does not demand byte identity there.

Use the actual `id` on each ruling to join `owl/F<n>.md`. `finding` contains finding prose, not necessarily an identifier. Save this separate harness record as `owl_dispatches.json`:

```json
[
  {
    "id": "F1",
    "for_finding_letter": "A",
    "draw_command": "exact executed random draw command",
    "draw_output": "A",
    "span": "exact span as dispatched",
    "position_a": "exact outbound Position A",
    "position_b": "exact outbound Position B",
    "reply": "full actual Owl reply block",
    "pre_filter_positions": "optional; raw combined positions for the single leak probe"
  }
]
```

Build this record from the harness’s actual tool and dispatch trace. Copying the final Owl record would make the comparison circular. Values must equal the corresponding Markdown section content, excluding surrounding blank lines and the optional enclosing reply code fence. Duplicate IDs across appended rounds fail. `pre_filter_positions` is absent except on the seeded probe. Draw letters and full record contents must match independently captured evidence.

Use the tested documentation to compute the raw counts in `measures.json`:

```json
{"overrule": {"numerator": 1, "denominator": 1}, "concession": {"numerator": 2, "denominator": 3}}
```

## Compatibility conflict remains explicit

The request permits only C2 new `owl/` files and C4 JSON fields as default artifact differences. C2 also requires a new report link and a stable record join (the implementation proposes an `id` field). Those exceed the literal exception. The strict default check intentionally flags them; it does not silently strip them. C4 permits `settled` and the concession `owl` correction, including `settled: null` on other lines. The default check rejects extra `mode`/`owner` fields.

The changed measures documentation is a required C4 source change, not itself a generated default-run artifact. A changed reported measure would be a further artifact difference if a run emits it. Resolve the allowed exception list with the user before marking requirement 6 accepted.
