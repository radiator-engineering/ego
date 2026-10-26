# Measuring EGO

`ego-resolve` appends one line per finding to `ego_rulings.jsonl`. These four
numbers tell you whether the Owl earns its cost. Compare them against stock EGM
on the same documents.

| Measure | How to compute | Warning sign |
|---|---|---|
| Overrule rate | OVERRULE / (SUSTAIN + OVERRULE + REFRAME) over Owl rulings | Near 0% or near 100%: the Owl is a rubber stamp. |
| Escalation rate | ESCALATE / all Owl rulings | Above about a third: the Owl is dodging questions of fact. |
| Re-litigation rate | findings dropped as "Already decided" in later rounds, plus findings that reopen a decision without the evidence its "Reopen only with" names | Rising: later Goldfish are not reading Decisions. |
| Hidden decisions | value calls the person made that no report surfaced (count by hand after a review) | Not lower than stock EGM: EGO is not paying for itself. |

## Position-bias check

The Owl should not care which letter it reads. `for_finding_letter` records
which letter the finding's side got. Over many rulings, the SUSTAIN rate should
be about the same for A and for B. A gap means order bias.

## The comparison

Run 10 real design documents through `/egm:egm-review` and through
`/ego:ego-review`. Count hidden decisions by hand for both. Published results
on model debate are mixed, so only this comparison shows whether EGO helps.
