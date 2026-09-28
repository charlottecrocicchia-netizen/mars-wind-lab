"""Keep source Markdown readable on GitHub and links usable on the local site."""
from html import escape, unescape
from pathlib import Path
import re
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from reading_collection import PAGES

ROOT = Path(__file__).resolve().parents[2]
GITHUB = 'https://github.com/charlottecrocicchia-netizen/mars-wind-lab/blob/main/'
ROUTES = {
    'docs/SCIENTIFIC_METHOD.md': '/research/method',
    'research/NEXT_TEST_PROTOCOLS.md': '/research/method#next-tests',
    'research/data/README.md': '/research/data',
    'research/COMPARISON.md': '/research/comparison',
    'research/EXECUTED_EXPERIMENTS.md': '/research/experiments',
    'research/THERMAL_EXPERIMENT.md': '/research/thermal',
    'research/DICHOTOMY_PHYSICS.md': '/research/physics',
    'research/PILOT_STUDY.md': '/research/pilot',
    **{f'research/dossiers/{name}.md': f'/research/dossiers/{name}'
       for name in ['science', 'literature', 'experiments', 'interdisciplinary', 'audit']},
}


def site_url(href, source):
    url = urlsplit(href)
    if url.scheme or url.netloc or href.startswith(('/', '#')) or not url.path:
        return href
    target = (Path(source).parent/unquote(url.path)).resolve()
    relative = target.relative_to(ROOT).as_posix()
    fragment = url.fragment
    # Fragment links into reports should keep the corresponding report page.
    if relative in ROUTES and (not fragment or relative == 'docs/SCIENTIFIC_METHOD.md'):
        route = urlsplit(ROUTES[relative])
        if relative == 'docs/SCIENTIFIC_METHOD.md' and fragment == 'reading-a-verdict':
            fragment = 'verdicts'
        return urlunsplit(('', '', route.path, url.query, fragment or route.fragment))
    if target.parent == ROOT/'research' and target.stem in PAGES and target.suffix == '.md':
        path = '/assets/reading/'+target.stem.lower()+'.html'
        # Python-Markdown's TOC collapses separators left by punctuation.
        fragment = re.sub('-+', '-', fragment)
    elif relative.startswith('research/'):
        path = '/research/files/'+quote(relative[len('research/'):])
    else:
        path = GITHUB+quote(relative)
    return path+('?' + url.query if url.query else '')+('#' + fragment if fragment else '')


def rewrite_links(html, source):
    def replace(match):
        return match[1]+'="'+escape(site_url(unescape(match[2]), source), quote=True)+'"'
    return re.sub(r'(href|src)="([^"]+)"', replace, html)
