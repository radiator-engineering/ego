#!/usr/bin/env python3
"""Run the fixed blinding script and verify its skill command. Static script check, not a model run."""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile


def check(source):
    text = source.read_text()
    command = r"^python3 EGO_ROOT/scripts/blind-check\.py <position-file>[ \t]*$"
    assert re.search(command, text, re.M), 'skill does not name the fixed leak-check command'
    script = source.resolve().parents[2] / 'scripts' / 'blind-check.py'
    assert script.is_file(), f'missing fixed leak-check script: {script}'
    with tempfile.TemporaryDirectory() as directory:
        position = Path(directory) / 'position.txt'
        position.write_text('my draft egm-design Capacity is 100 requests per second.\n')
        outputs = []
        for _ in range(2):
            result = subprocess.run(['python3', str(script), str(position)], text=True, capture_output=True, check=True, timeout=10)
            outputs.append(result.stdout.strip())
        assert outputs == ['2', '0'], f'wrong strip/recheck counts: {outputs}'
        assert not re.search(r'my draft|egm-design', position.read_text(), re.I), 'seed remains'
        assert 'Capacity is 100 requests per second.' in position.read_text(), 'evidence destroyed'
    print('PASS static executable script: stripped 2; recheck 0; evidence retained (not model acceptance)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    try:
        check(args.source)
    except (AssertionError, OSError, subprocess.SubprocessError) as error:
        print(f'FAIL static executable script: {error}')
        raise SystemExit(1)
