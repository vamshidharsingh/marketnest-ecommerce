"""Check the exact delivered source inventory and SHA-256 contents."""
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {'__pycache__', '.git', '.venv', 'runtime', '.pytest_cache', 'build', 'dist'}

def verify():
    manifest = json.loads((ROOT / 'PROJECT_MANIFEST.json').read_text())
    actual = {str(p.relative_to(ROOT)).replace('\\', '/') for p in ROOT.rglob('*') if p.is_file() and (not any((x in EXCLUDE for x in p.relative_to(ROOT).parts))) and (not p.name.endswith('.pyc'))}
    expected = {item['path'] for item in manifest['files']}
    assert len(actual) == 160, f'Expected 160 source files, found {len(actual)}'
    assert actual == expected, f'Missing: {expected - actual}; extra: {actual - expected}'
    for item in manifest['files']:
        if item['sha256'] is not None:
            assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], f"Changed: {item['path']}"
    print('PASS: exactly 160 source files; all payload hashes match')
if __name__ == '__main__':
    verify()
