#!/usr/bin/env python3
"""Execute the skill's fixed blinding snippet. Static script check, not a model run."""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile


def check(source):
    text = source.read_text()
    snippets = re.findall(r"python3 - <position-file> <<'EOF'\n(.*?)\nEOF", text, re.S)
    assert len(snippets) == 1, 'expected exactly one fixed executable leak check'
    with tempfile.TemporaryDirectory() as directory:
        position = Path(directory) / 'position.txt'
        position.write_text('my draft egm-design Capacity is 100 requests per second.\n')
        outputs = []
        for _ in range(2):
            result = subprocess.run(['python3', '-', str(position)], input=snippets[0], text=True, capture_output=True, check=True, timeout=10)
            outputs.append(result.stdout.strip())
        assert outputs == ['2', '0'], f'wrong strip/recheck counts: {outputs}'
        assert not re.search(r'my draft|egm-design', position.read_text(), re.I), 'seed remains'
        assert 'Capacity is 100 requests per second.' in position.read_text(), 'evidence destroyed'
    print('PASS static executable snippet: stripped 2; recheck 0; evidence retained (not model acceptance)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    try:
        check(args.source)
    except (AssertionError, OSError, subprocess.SubprocessError) as error:
        print(f'FAIL static executable snippet: {error}')
        raise SystemExit(1)
