# Measuring EGO

`ego-resolve` appends one line per finding to `ego_rulings.jsonl`. These
numbers tell you whether the Owl earns its cost. Compare them against stock EGM
on the same documents.

Only a `REBUT` reaches the Owl. A `CONCEDE` settles the finding with no Owl
call (`"owl": null`, `"settled": "conceded"`). Compute every Owl measure over
lines where `goldfish == "REBUT"`. This filter also works on v0.1.0 files,
which recorded concessions as `"owl": "OVERRULE"`.

| Measure | How to compute | Warning sign |
|---|---|---|
| Overrule rate | OVERRULE / (SUSTAIN + OVERRULE + REFRAME), over `REBUT` lines | Near 0% or near 100%: the Owl is a rubber stamp. |
| Escalation rate | ESCALATE / `REBUT` lines | Above about a third: the Owl is dodging questions of fact. |
| Concession rate | CONCEDE / (CONCEDE + REBUT), from the `goldfish` field | Near 100%: the Goldfish accepts replies without testing them. Near 0%: the Elephant contests findings it should fix. |
| Re-litigation rate | findings dropped as "Already decided" in later rounds, plus findings that reopen a decision without the evidence its "Reopen only with" names | Rising: later Goldfish are not reading Decisions. |
| Hidden decisions | value calls the person made that no report surfaced (count by hand after a review) | Not lower than stock EGM: EGO is not paying for itself. |
| Cross-model agreement (optional) | for runs that pair a second model's independent Goldfish pass: findings both models raised, against findings only one raised (match by hand) | Low overlap: findings depend on the model, so one pass misses issues. |

For example, a run with 6 CONCEDE and 4 REBUT, where the Owl overrules 1 of
the 4, has an overrule rate of 1/4 and a concession rate of 6/10. Counting
concessions as Owl rulings would give 7/10.

## Position-bias check

The Owl should not care which letter it reads. `for_finding_letter` records
which letter the finding's side got. Over many `REBUT` lines, the SUSTAIN rate
should be about the same for A and for B. A gap means order bias.

## The comparison

Run 10 real design documents through `/egm:egm-review` and through
`/ego:ego-review`. Count hidden decisions by hand for both. Published results
on model debate are mixed, so only this comparison shows whether EGO helps.
