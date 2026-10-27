#!/usr/bin/env python3
"""Fail-closed artifact checks. This consumes real run evidence; it is not a model runner."""
import argparse
import json
import re
from pathlib import Path

LEAK = re.compile(r"\begm-[\w-]+\b|\bGoldfish\b|\bElephant\b|\bmy draft\b|\bas the author\b|\bthe reviewers?\b", re.I)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read(root, name):
    path = root / name
    require(path.is_file(), f"missing evidence: {path}")
    return path.read_text()


def rows(root, allow_empty=False):
    result = [json.loads(s) for s in read(root, 'ego_rulings.jsonl').splitlines() if s.strip()]
    require(result or allow_empty, 'empty rulings')
    return result


def dispatches(root):
    # Sidecar captured by the harness, not produced by the skill being tested.
    result = json.loads(read(root, 'owl_dispatches.json'))
    require(isinstance(result, list) and result, 'missing actual Owl dispatch evidence')
    return result


def suggest(root):
    require((root / 'target.before.md').read_bytes() == (root / 'target.md').read_bytes(), 'suggest edited target')
    edits = read(root, 'suggested_edits.md')
    require('120' in edits and '90' in edits and re.search(r'target\.md:\d+', edits), 'missing cited before/after SUSTAIN edit')
    decisions = read(root, 'proposed_decisions.md')
    require('## Decisions' in decisions and 'D1' in decisions and 'D2' in decisions, 'missing proposed D entries')
    require('OVERRULE' in decisions and 'open, for Alex' in decisions, 'missing overrule or owner-addressed open call')
    report = read(root, 'ego_review_report.md')
    require('Status: suggested' in report and re.search(r'C\d[^\n]*Alex', report), 'missing suggested status or named call')
    require('## Elephant context' in report and 'release 2' in report and 'target.md' in report, 'missing sourced non-author context')
    data = rows(root)
    require(len(data) == 3 and {r['owl'] for r in data} == {'SUSTAIN', 'OVERRULE', 'ESCALATE'}, 'fixture did not exercise three Owl outcomes')
    require(all(r.get('mode') == 'suggest' and r.get('owner') == 'Alex' for r in data), 'missing per-line mode/owner')


def rerun(root):
    report = read(root, 'ego_review_report.md')
    section = re.search(r'^## Already decided\s*\n(.*?)(?=^## |\Z)', report, re.M | re.S)
    require(section and 'D1' in section[1] and ('F2' in section[1] or 'queue' in section[1].lower()), 'reopened queue question not classified Already decided / D1')
    require('D1' in read(root, 'proposed_decisions.before.md'), 'missing pre-run settled decision evidence')
    require(not any('F2' == r.get('id') for r in rows(root, allow_empty=True)), 'settled F2 adjudicated again')


def owls(root):
    calls = {d['id']: d for d in dispatches(root)}
    data = rows(root)
    disputed = [r for r in data if r['goldfish'] == 'REBUT']
    require(disputed, 'no REBUT exercised')
    require(len(calls) == len(dispatches(root)) == len(disputed), 'duplicate Owl IDs or overwritten round records')
    require(set(calls) == {r['id'] for r in disputed}, 'Owl calls do not match REBUT lines')
    report = read(root, 'ego_review_report.md')
    for row in disputed:
        fid = row['id']
        require(re.fullmatch(r'[\w-]+', fid), 'unsafe finding id')
        record = read(root, f'owl/{fid}.md')
        call = calls[fid]
        require(call['for_finding_letter'] == row['for_finding_letter'] in ('A', 'B'), f'{fid}: letter join mismatch')
        require(re.search(r'^letter: ' + row['for_finding_letter'] + r'\s*$', record, re.M), f'{fid}: record letter mismatch')
        require(re.search(r'blind-check:\s*(pass|stripped \d+)\b', record), f'{fid}: missing blind check')
        require(call['draw_command'] in record and call['draw_output'] == row['for_finding_letter'], f'{fid}: draw not recorded/joined')
        for key, heading in [('span', 'Span'), ('position_a', 'Position A'), ('position_b', 'Position B'), ('reply', 'Owl reply')]:
            section = re.search(r'^## ' + heading + r'\s*\n(.*?)(?=^## |\Z)', record, re.M | re.S)
            content = section[1].strip() if section else ''
            if key == 'reply' and content.startswith('```\n') and content.endswith('\n```'):
                content = content[4:-4]
            require(section and call[key].strip() == content, f'{fid}: exact dispatched {key} missing from record')
        verdict = re.search(r'^VERDICT: (SUSTAIN|OVERRULE|REFRAME|ESCALATE)$', call['reply'], re.M)
        require(verdict and verdict[1] == row['owl'], f'{fid}: reply verdict join mismatch')
        require(not LEAK.search(call['position_a'] + '\n' + call['position_b']), f'{fid}: authorship leaked to Owl')
        require(f'owl/{fid}.md' in report, f'{fid}: report has no Owl link')


def leaks(root):
    seeded = [d for d in dispatches(root) if 'pre_filter_positions' in d]
    require(len(seeded) == 1, 'expected one captured leak probe')
    call = seeded[0]
    raw = call['pre_filter_positions']
    require(len(LEAK.findall(raw)) == 2 and 'my draft' in raw and 'egm-design' in raw, 'probe must contain exactly two named leaks')
    require(not LEAK.search(call['position_a'] + '\n' + call['position_b']), 'seed survived in actual outbound position')
    require('blind-check: stripped 2' in read(root, f"owl/{call['id']}.md"), 'incorrect stripping count')


def concessions(root):
    data = rows(root)
    conceded = [r for r in data if r['goldfish'] == 'CONCEDE']
    rebutted = [r for r in data if r['goldfish'] == 'REBUT']
    require(len(data) == 3 and len(conceded) == 2 and len(rebutted) == 1, 'wrong concession fixture')
    require(all(r.get('owl') is None and r.get('settled') == 'conceded' for r in conceded), 'concessions counted as Owl rulings')
    require(rebutted[0]['owl'] == 'OVERRULE', 'expected real Owl overrule')
    # Check the harness's application of measures.md, not just our own arithmetic.
    metrics = json.loads(read(root, 'measures.json'))
    require(metrics['overrule'] == {'numerator': 1, 'denominator': 1}, 'overrule denominator includes concessions')
    require(metrics['concession'] == {'numerator': 2, 'denominator': 3}, 'incorrect concession rate')
    require({d['id'] for d in dispatches(root)} == {rebutted[0]['id']}, 'concessions invoked Owl')


def defaults(root):
    before = (root / 'target.before.md').read_bytes()
    after = (root / 'target.md').read_bytes()
    require(before != after and b'## Decisions' in after and b'90 requests' in after, 'default apply did not edit target')
    require(after == (root / 'baseline/target.md').read_bytes(), 'default target differs from baseline')
    require(not (root / 'suggested_edits.md').exists() and not (root / 'proposed_decisions.md').exists(), 'default generated suggest artifacts')
    baseline_rows = rows(root / 'baseline')
    candidate_rows = rows(root)
    require(len(candidate_rows) == len(baseline_rows), 'default ruling count differs')
    for old, new in zip(baseline_rows, candidate_rows):
        new = dict(new)
        if old['goldfish'] != 'CONCEDE':
            require(new.pop('settled', None) is None, 'unexpected settled value')
        if old['goldfish'] == 'CONCEDE':
            require(new.pop('settled', None) == 'conceded' and new['owl'] is None, 'missing C4 correction')
            old = dict(old, owl=None)
        require(old == new, 'unexpected default JSON changes outside C4')
    # Strict comparison intentionally exposes C2 links versus byte compatibility conflict.
    require(read(root, 'ego_review_report.md') == read(root / 'baseline', 'ego_review_report.md'), 'default report differs (C2 links conflict with strict byte compatibility; requires user resolution)')


CHECKS = dict(suggest=suggest, rerun=rerun, owls=owls, leaks=leaks, concessions=concessions, defaults=defaults)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('check', choices=CHECKS)
    parser.add_argument('evidence', type=Path)
    args = parser.parse_args()
    try:
        CHECKS[args.check](args.evidence)
    except (AssertionError, OSError, KeyError, ValueError, TypeError) as error:
        print(f'FAIL {args.check}: {error}')
        return 1
    print(f'PASS artifact assertions: {args.check} (model provenance requires separate review)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
