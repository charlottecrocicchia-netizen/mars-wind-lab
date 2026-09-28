"""Check repository-relative links in the GitHub-facing Markdown collection.

External URLs are not fetched. Frozen pre-correction report snapshots are not
rewritten or treated as current documentation.
"""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def check():
    files = sorted({*ROOT.glob('*.md'), *(ROOT/'docs').rglob('*.md'),
                    *(ROOT/'research').glob('*.md'), *(ROOT/'research/dossiers').glob('*.md'),
                    ROOT/'research/data/README.md', ROOT/'research/followup/README.md'})
    errors, checked = [], 0
    for path in files:
        source = re.sub(r'^```.*?^```[^\n]*$', '', path.read_text(), flags=re.M | re.S)
        for href in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', source):
            url = urlsplit(href)
            if url.scheme or url.netloc or not url.path:
                continue
            checked += 1
            if url.path.startswith('/'):
                errors.append(f'{path.relative_to(ROOT)}: site-only link {href}')
                continue
            target = (path.parent/unquote(url.path)).resolve()
            if not target.is_relative_to(ROOT) or not target.exists():
                errors.append(f'{path.relative_to(ROOT)}: missing target {href}')
    print(f'Checked {checked} repository links in {len(files)} Markdown files.')
    for error in errors:
        print(error, file=sys.stderr)
    return not errors


if __name__ == '__main__':
    raise SystemExit(0 if check() else 1)
