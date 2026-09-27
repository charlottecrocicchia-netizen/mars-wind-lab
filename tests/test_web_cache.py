"""Opening the local site must not silently reuse an outdated design."""
from fastapi.testclient import TestClient

from marswind.server import app


def test_pages_are_not_stored_in_the_http_cache():
    client = TestClient(app)
    for url in ['/', '/research/data', '/research/tests',
                '/assets/reading/executed_experiments.html']:
        response = client.get(url)
        assert response.status_code == 200
        assert response.headers['cache-control'] == 'no-store'


def test_assets_revalidate_and_unchanged_files_remain_conditional():
    client = TestClient(app)
    for url in ['/assets/workspace.css?v=20260927-design',
                '/assets/observations.js?v=design1',
                '/assets/meteorite-links.mjs?v=design1',
                '/research/files/data/results.json']:
        response = client.get(url)
        assert response.status_code == 200
        assert response.headers['cache-control'] == 'no-cache'
        unchanged = client.get(url, headers={'If-None-Match': response.headers['etag']})
        assert unchanged.status_code == 304
        assert unchanged.headers['cache-control'] == 'no-cache'
        assert not unchanged.content
        outdated = client.get(url, headers={'If-None-Match': '"previous-release"'})
        assert outdated.status_code == 200
        assert outdated.content == response.content


def test_direct_reading_page_keeps_its_policy_on_conditional_responses():
    client = TestClient(app)
    url = '/assets/reading/executed_experiments.html'
    original = client.get(url)
    response = client.get(url, headers={'If-None-Match': original.headers['etag']})
    assert response.status_code == 304
    assert response.headers['cache-control'] == 'no-store'
