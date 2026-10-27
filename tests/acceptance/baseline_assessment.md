# Frozen baseline assessment

I captured the baseline on 2026-10-27 at 17:05:53.209610 UTC, then notified the implementer that work could start. The implementer confirmed receipt. A separate local evidence directory holds the frozen copies and SHA-256 manifest. This audit uses those copies.

| File | SHA-256 |
|---|---|
| `skills/ego-resolve/SKILL.md` | `0cb1c26a04a9cd6e485ad28a70480619f29e327d1a6888eee5ae0db0a265add6` |
| `skills/ego-review/SKILL.md` | `9d4826aa9b7106e20310aa63299e9f1f950812e64a72cdd7f5a93aa524b8ecfa` |
| `docs/measures.md` | `61879a792984419f8a68ff74e6696ee18de2d1d29da52147c0e6797ec6472a10` |
| `agents/owl.md` | `1896540f5f5106cc2f69cab4e2a4b2e2dd02d2679095c22aadfe96ed8387e9cf` |

## Baseline instructions and evidence limits

| Acceptance requirement | Actual baseline instructions | What this establishes |
|---|---|---|
| 1: suggest / owner | Resolve Inputs has no Owner or Mode. Step 7.1 applies edits to TargetFile; Step 7.2 appends Decisions there; Step 7.5 says resolved. No suggested/proposed artifact instructions. Step 2 has no non-author context disclosure. | Baseline lacks C1/C3 protocol. Does not prove a model will mutate the target when explicitly told suggest. |
| 2: rerun proposed decisions | Resolve Step 1 reads TargetFile Decisions. Review Override 3 dispatches only document Decisions. Neither reads proposed_decisions.md. | Baseline lacks proposed-decision handoff. Does not prove a particular model reopens D1. |
| 3: auditable Owl | Resolve Step 4 strips names and draws A/B but does not save exact packets, replies or commands. Step 5 report has no Owl record link. | Baseline lacks record protocol. Does not provide actual missing-record run evidence. |
| 4: leak check | Resolve Step 4.1 already says remove authorship and lens names, including my draft. It does not require a fixed check, recheck or strip count. | Removal alone is not a new capability. The new requirements add an audit record and recheck. The baseline instructions do not prove that a model will send leaked names. |
| 5: concessions | Resolve Step 3 records CONCEDE as OVERRULE, no Owl call. JSON schema lacks settled. Measures says over Owl rulings without an explicit REBUT line filter. | A consumer can miscount concessions with this schema. No runtime evidence establishes a 3/3 count. |
| 6: defaults | Resolve Step 7 applies edits and records Decisions. | Baseline is the comparator and should pass its own default behavior. Requirement 6 needs a feature-reverted candidate or corrupt-output negative control, not a claimed baseline failure. |

## Results at checkpoint

Seven synthetic validator unit tests pass. They reject corrupt artifacts, including mismatched letters, incorrect strip counts and wrong denominators. Their source labels these controls as synthetic. The frozen baseline failed the original inline-script check because it had no fixed executable check. After the implementation moved the check to `scripts/blind-check.py`, I updated the validator to verify the skill command and run that file. The frozen baseline also fails this updated check because it has no script command. The candidate script removes both seeded leaks, reports 2, then reports 0 on recheck. It retains the evidence text. This comparison tests the script without a model. I ran no real model tests and have not accepted the candidate behavior. All six behavioral requirements remain **NOT RUN**; requirement 6 also has the unresolved exception-list contradiction described in README.

I changed no implementation files or Owl persona. I published nothing and left the version unchanged.

Candidate instruction review found that repeated F1 IDs could overwrite earlier Owl records while JSONL appended across rounds. The implementer reported amending Step 1 to continue from the highest existing ID and forbid overwrite. The validator rejects duplicate IDs in test artifacts. A real run has not yet verified that earlier records survive later rounds.
