"""Synthetic validator unit tests only. None of these are model acceptance runs."""
import json
from pathlib import Path
import tempfile
import unittest
import check_artifacts as checks


class Validators(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write('target.before.md', '# Target\n120 requests\n## Decisions\n')
        self.write('target.md', self.read('target.before.md'))
        self.write('suggested_edits.md', 'target.md:2\nBefore: 120\nAfter: 90\n')
        self.write('proposed_decisions.md', '## Decisions\n### D1: queue\nOVERRULE\n### D2: rollout\nopen, for Alex\n')
        self.write('proposed_decisions.before.md', self.read('proposed_decisions.md'))
        self.report = 'Status: suggested\n## Elephant context\nSources: target.md; release 2 shipped the relay and queue.\n## Your calls\n### C1: rollout, for Alex\n## Rulings\n'
        self.data = [dict(id=f'F{i}', finding=f'issue {i}', goldfish='REBUT', owl=v, for_finding_letter='A', mode='suggest', owner='Alex') for i, v in enumerate(['SUSTAIN', 'OVERRULE', 'ESCALATE'], 1)]
        self.calls = []
        for row in self.data:
            call = dict(id=row['id'], for_finding_letter='A', draw_command='python3 random-draw.py', draw_output='A', span='target.md:2: 120 requests', position_a='Capacity is 100.', position_b='Threshold is 120.', reply=f"VERDICT: {row['owl']}\nHOLDS: A\nEVIDENCE: target.md:2\nREASON: Synthetic unit data.")
            self.calls.append(call)
            self.record(call)
            self.report += f"[owl/{row['id']}.md](owl/{row['id']}.md)\n"
        self.write('ego_review_report.md', self.report)
        self.save()

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def read(self, name):
        return (self.root / name).read_text()

    def record(self, c, blind='pass'):
        self.write(f"owl/{c['id']}.md", f"letter: A\nletter-command: {c['draw_command']}\nblind-check: {blind}\n" + '\n'.join(f'## {h}\n{c[k]}\n' for k, h in [('span', 'Span'), ('position_a', 'Position A'), ('position_b', 'Position B'), ('reply', 'Owl reply')]))

    def save(self):
        self.write('ego_rulings.jsonl', ''.join(json.dumps(r) + '\n' for r in self.data))
        self.write('owl_dispatches.json', json.dumps(self.calls))

    def test_1_suggest_rejects_target_mutation(self):
        checks.suggest(self.root)
        self.write('target.md', self.read('target.md') + 'accidental edit')
        with self.assertRaisesRegex(AssertionError, 'suggest edited target'):
            checks.suggest(self.root)

    def test_2_rerun_rejects_reopened_decision(self):
        self.write('ego_review_report.md', self.report + '\n## Already decided\nF2 queue: D1\n')
        self.data = []
        self.save()
        checks.rerun(self.root)
        self.write('ego_review_report.md', self.report)
        with self.assertRaisesRegex(AssertionError, 'not classified'):
            checks.rerun(self.root)

    def test_3_owl_rejects_missing_record_and_letter_mismatch(self):
        checks.owls(self.root)
        path = self.root / 'owl/F1.md'
        text = path.read_text()
        path.unlink()
        with self.assertRaisesRegex(AssertionError, 'missing evidence'):
            checks.owls(self.root)
        path.write_text(text.replace('letter: A', 'letter: B'))
        with self.assertRaisesRegex(AssertionError, 'record letter mismatch'):
            checks.owls(self.root)

    def test_owl_accepts_verbatim_reply_fence_and_rejects_reused_round_id(self):
        path = self.root / 'owl/F1.md'
        path.write_text(path.read_text().replace('## Owl reply\n', '## Owl reply\n```\n') + '```\n')
        checks.owls(self.root)
        self.calls.append(dict(self.calls[0]))
        self.data.append(dict(self.data[0]))
        self.save()
        with self.assertRaisesRegex(AssertionError, 'duplicate Owl IDs'):
            checks.owls(self.root)

    def test_4_leak_rejects_unstripped_dispatch_and_bad_count(self):
        call = self.calls[0]
        call['pre_filter_positions'] = 'my draft egm-design Capacity is 100.'
        self.record(call, 'stripped 2')
        self.save()
        checks.leaks(self.root)
        self.record(call, 'stripped 1')
        with self.assertRaisesRegex(AssertionError, 'incorrect stripping count'):
            checks.leaks(self.root)
        self.record(call, 'stripped 2')
        call['position_a'] += ' my draft'
        self.save()
        with self.assertRaisesRegex(AssertionError, 'seed survived'):
            checks.leaks(self.root)

    def test_5_concessions_reject_legacy_owl_and_wrong_denominator(self):
        for row in self.data[:2]:
            row.update(goldfish='CONCEDE', owl=None, settled='conceded')
        self.data[2]['owl'] = 'OVERRULE'
        self.calls = [self.calls[2]]
        self.write('measures.json', json.dumps(dict(overrule=dict(numerator=1, denominator=1), concession=dict(numerator=2, denominator=3))))
        self.save()
        checks.concessions(self.root)
        self.data[0]['owl'] = 'OVERRULE'
        self.save()
        with self.assertRaisesRegex(AssertionError, 'concessions counted'):
            checks.concessions(self.root)
        self.data[0]['owl'] = None
        self.save()
        self.write('measures.json', json.dumps(dict(overrule=dict(numerator=3, denominator=3), concession=dict(numerator=2, denominator=3))))
        with self.assertRaisesRegex(AssertionError, 'denominator includes'):
            checks.concessions(self.root)

    def test_6_defaults_reject_no_apply_and_unapproved_compatibility_exceptions(self):
        self.write('target.md', '# Target\n90 requests\n## Decisions\n')
        self.write('baseline/target.md', self.read('target.md'))
        (self.root / 'suggested_edits.md').unlink()
        (self.root / 'proposed_decisions.md').unlink()
        for row in self.data:
            row.pop('mode'); row.pop('owner')
        self.save()
        self.write('baseline/ego_rulings.jsonl', self.read('ego_rulings.jsonl'))
        self.write('baseline/ego_review_report.md', self.report)
        checks.defaults(self.root)
        self.write('target.md', self.read('target.before.md'))
        with self.assertRaisesRegex(AssertionError, 'did not edit'):
            checks.defaults(self.root)
        self.write('target.md', self.read('baseline/target.md'))
        self.write('ego_review_report.md', self.report + 'new Owl link')
        with self.assertRaisesRegex(AssertionError, 'default report differs'):
            checks.defaults(self.root)


if __name__ == '__main__':
    unittest.main()
