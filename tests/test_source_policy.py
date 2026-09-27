import importlib.util
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from marswind.server import app
from marswind.source_policy import require_mcd_authorization, require_source_permission

ROOT = Path(__file__).resolve().parents[1]


def test_retired_private_archive_is_not_accessible(monkeypatch, tmp_path):
    monkeypatch.setenv('MARS_LEGACY_ROOT', str(tmp_path))
    client = TestClient(app)
    assert client.get('/api/legacy').status_code == 404
    page = client.get('/atmosphere')
    assert page.status_code == 200
    assert 'data-tab="legacy"' not in page.text
    assert 'id="legacy"' not in page.text


def test_mcd_requires_explicit_owner_authorization(tmp_path):
    for decision in [None, False, 'true']:
        (tmp_path / 'local_settings.json').write_text(json.dumps({'MCD_AUTHORIZED': decision}))
        with pytest.raises(RuntimeError, match='awaiting authorization'):
            require_mcd_authorization(tmp_path)
    (tmp_path / 'local_settings.json').write_text('{"MCD_AUTHORIZED": true}')
    require_mcd_authorization(tmp_path)


def test_unknown_permission_is_not_treated_as_permission():
    for decision in [None, False, 'true']:
        with pytest.raises(RuntimeError, match='excluded from new acquisition'):
            require_source_permission({'id': 'example', 'reuse_approved': decision})
    require_source_permission({'id': 'example', 'reuse_approved': True})


def test_uncleared_sources_do_not_start_network_requests(monkeypatch):
    import urllib.request
    def forbidden(*args, **kwargs):
        pytest.fail('A blocked source must not issue a request')
    monkeypatch.setattr(urllib.request, 'urlopen', forbidden)
    spec = importlib.util.spec_from_file_location('acquire_sources', ROOT / 'scripts/data/acquire.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = next(s for s in json.loads((ROOT / 'scripts/data/sources.json').read_text()) if s['id'] == 'aqueous_minerals')
    with pytest.raises(RuntimeError, match='excluded from new acquisition'):
        module.acquire(source, large=True)
    spec = importlib.util.spec_from_file_location('acquire_pilot', ROOT / 'scripts/data/acquire_pilot.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with pytest.raises(RuntimeError, match='excluded from new acquisition'):
        module.main()
