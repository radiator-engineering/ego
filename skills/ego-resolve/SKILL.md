---
name: ego-resolve
disable-model-invocation: true
description: >-
  Resolve Goldfish review findings with a blind judge. The Elephant answers
  each finding with FIX, CONTEST or REFRAME; the Goldfish replies once; the Owl
  rules on each dispute; value calls go to the person; rulings are recorded in
  the document's Decisions section.
---

# EGO: Resolve

Read `../../docs/harnesses.md` first. It says how to find EGO's root
(`EGO_ROOT`) and EGM's root (`EGM_ROOT`), and how to dispatch a named agent in
your harness. In Claude Code, `EGO_ROOT` is `${CLAUDE_PLUGIN_ROOT}`.

This skill replaces EGM's `egm-resolve`. It takes the same inputs and writes
the same kind of report, with one change in who decides: the Elephant answers
findings but never rules on critiques of its own draft. The Owl rules. The
person decides value calls.

Run it in the Elephant's thread: the conversation that wrote the document.

## Inputs

- **`TargetFile`**: path to the document.
- **`LineRange`**: line numbers, or `full file`.
- **`FindingsList`**: findings from a Goldfish review report (for example
  `critic_report.md` or `goldfish_review_report.md`).
- **`Tensions`** (optional): the `## Tensions` block from `ego-tensions`.

If inputs are missing, ask for them one at a time, then show the setup and
confirm before you start.

Write artifacts where EGM writes them: the working directory, or the folder
named by an `EGM artifact directory: <path>` line in the prompt, `CLAUDE.md`
or `AGENTS.md`.

## Step 1: Read

Read `TargetFile` at `LineRange` and its `## Decisions` section, if it has one.
Parse the findings. Keep each finding's reviewer lens (for example
`egm-design`) and its line span.

Drop a finding that only repeats a recorded decision without new evidence.
List it in the report under "Already decided", with the decision's ID.

## Step 2: The Elephant answers

Answer every finding with one of three words. Base each answer on quoted text
from the document or the code, with `path:line`.

- **FIX**: the critique holds. Write the exact edit.
- **CONTEST**: the critique is wrong. Quote the evidence that shows it.
- **REFRAME**: the critique is partly right, but asks for the wrong change.
  State the requirement change you would make instead.

Do not inflate CONTEST to save work, and do not FIX a finding you think is
wrong to avoid a dispute. The Owl sees the evidence either way.

A FIX goes straight to the report. It costs no further calls.

## Step 3: The Goldfish replies once

For each CONTEST or REFRAME, dispatch a fresh instance of the lens that raised
the finding (for example `egm-design`; see `docs/harnesses.md` for the name in
your harness). If the lens has no EGM persona, use a general subagent told to
review from that lens. Send:

> You are replying to a response to a finding raised in a review of
> `<TargetFile>`. Read the span you need. Answer in at most 150 words.
> Start with `CONCEDE` if the response is right, or `REBUT` if the finding
> still holds. A rebuttal must quote the document or code with `path:line`.
> Do not raise new findings.
>
> Finding: `<finding as raised>`
> Span: `<path:lines>`
> Response: `<the Elephant's answer and evidence>`

On `CONCEDE`, the finding is settled against the critique. Record it as
OVERRULE with the reason "conceded"; no Owl call.

Run replies for all disputes in parallel.

## Step 4: The Owl rules, blind

For each `REBUT`, build two positions:

- **For the finding**: the finding as raised, plus the rebuttal.
- **Against the finding**: the Elephant's answer and evidence.

Make them blind:

1. Remove words that name an author or a reviewer ("my draft", "as the
   author", "the reviewer missed", lens names). Keep every quote and citation.
2. Cut each position to at most 200 words. Cut prose before you cut quotes.
3. Pick the order at random. Run
   `python3 -c "import secrets; print(secrets.choice('AB'))"` and give that
   letter to the position for the finding.

Dispatch the Owl (`ego-owl`, persona `EGO_ROOT/agents/owl.md`) once per dispute, in parallel, with: the span as quoted
text with `path:lines`, the finding, Position A, Position B, and the document's
Decisions section. Parse its block. Map `HOLDS` back to the sides with the
letter you drew.

Never tell the Owl which side wrote the document.

## Step 5: Report

Write `ego_review_report.md`:

```markdown
# EGO Review Report

**Target:** `<TargetFile>` (`<LineRange>`)

## Your calls
<!-- Tensions and ESCALATE rulings. Each one line of trade-off and the
     options. Empty: "None." -->

### C1: <name> (tension | escalation)
* **Trade-off:** <X against Y>
* **Options:** <option 1> / <option 2>

## Rulings

### <Issue name> - Severity: <Blocker | Major | Nit> - `<lens>`
* **Scope:** <path#Lstart-Lend>
* **Finding:** <as raised>
* **Elephant:** FIX | CONTEST | REFRAME - <one line>
* **Goldfish:** CONCEDE | REBUT | (none: FIX) - <one line>
* **Owl:** SUSTAIN | OVERRULE | REFRAME | ESCALATE | (none) - <reason>
* **Edit:** <the edit that will be applied, or "none: document stays">

## Already decided
<!-- Findings dropped in Step 1, with the decision ID. -->
```

Order rulings by severity. A SUSTAIN means the Elephant writes the edit the
finding asks for; put that edit under **Edit**. A REFRAME means the Elephant
writes the edit for the requirement the Owl named.

## Step 6: The person decides

Tell the person, in one short message, the report path, the count of each
verdict, and the number of calls waiting for them. Offer:

- **Apply**: apply every edit, record the rulings, and answer the calls in
  chat (for example `C1: option 2`).
- **Override**: name a ruling to reverse, with a reason. A person's override
  is final and is recorded as theirs.
- **Walk through**: go through the rulings one at a time.
- **No changes**: continue without editing.

Then stop. Call no tools this turn, and wait for the reply.

## Step 7: Apply and record

1. Apply the approved edits to `TargetFile`.
2. Add or extend a `## Decisions` section at the end of `TargetFile`. Add one
   entry per OVERRULE, REFRAME, answered call and override. A SUSTAIN needs no
   entry: the edit is the record.

   ```markdown
   ### D<n>: <short question> (<YYYY-MM-DD>)
   * **Ruling:** <OVERRULE | REFRAME | person: option chosen>
   * **Reason:** <one or two sentences>
   * **Reopen only with:** <the evidence that would change this>
   ```

   Later Goldfish read this section. "Reopen only with" tells them what a new
   finding must cite.
3. Append one JSON line per finding to `ego_rulings.jsonl` beside the report:
   `{"date", "target", "finding", "lens", "severity", "elephant",
   "goldfish", "owl", "for_finding_letter", "person_override"}`. Use `null`
   for steps that did not run. `docs/measures.md` reads this file.
4. Re-read `TargetFile` and check it is still valid Markdown.
5. Add `Status: resolved` at the top of the report.

## Handoff

Return to the caller with the counts: edits applied, rulings recorded, calls
answered, calls still open.
