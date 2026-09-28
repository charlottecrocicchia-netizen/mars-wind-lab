"""Portable source links must also resolve in the locally rendered website."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/research'))
from site_links import site_url, rewrite_links


def test_portable_links_preserve_reading_targets_and_fragments():
    source = ROOT/'research/dossiers/audit.md'
    assert site_url('../RAPID_BODIES.md', source) == '/assets/reading/rapid_bodies.html'
    assert site_url('../DISCRIMINATING_TESTS.md#test-1--surface-age', source) == '/assets/reading/discriminating_tests.html#test-1-surface-age'
    assert site_url('../followup/bodies/stack.csv', source) == '/research/files/followup/bodies/stack.csv'
    assert site_url('../../docs/SCIENTIFIC_METHOD.md#reading-a-verdict', source) == '/research/method#verdicts'


def test_external_links_and_html_escaping_remain_valid():
    source = ROOT/'research/README.md'
    assert site_url('https://doi.org/10.1234/example', source) == 'https://doi.org/10.1234/example'
    assert site_url('#follow-up-results', source) == '#follow-up-results'
    assert site_url('../docs/USAGE.md', source).endswith('/blob/main/docs/USAGE.md')
    html = '<a href="EXECUTED_EXPERIMENTS.md?view=recording&amp;x=1">Read</a>'
    assert rewrite_links(html, source) == '<a href="/research/experiments?view=recording&amp;x=1">Read</a>'
