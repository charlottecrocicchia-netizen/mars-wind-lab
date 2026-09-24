"""Integrity of the scientific source trail and offline research deliverable."""
import csv
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from fastapi.testclient import TestClient
from marswind import server

ROOT=Path(__file__).resolve().parents[1]


def test_catalog_does_not_promote_discovery_to_reading_or_publish_abstracts():
    records=json.loads((ROOT/'research/catalog.json').read_text())
    summary=json.loads((ROOT/'research/summary.json').read_text())
    by_doi={r['doi']:r for r in records}
    assert len(by_doi)==len(records)==summary['records']
    assert dict(Counter(r['review_depth'] for r in records))==summary['review_depth_counts']
    assert sum(r['core'] for r in records)==summary['core_records']
    assert sum(r['review_depth']!='metadata' for r in records)==summary['source_consulted']
    for r in records:
        assert 'abstract' not in r
        assert r['url']=='https://doi.org/'+r['doi']
        if not r['core']:
            assert r['review_depth']=='metadata'
            assert r['review_status']=='Discovery candidate — not screened'
        else:
            assert r['finding'] and r['limitation'] and r['consulted_material']
        if r.get('correction_doi'):
            assert r['correction_doi'] in by_doi
    with (ROOT/'research/catalog.csv').open() as source:
        assert {r['doi'] for r in csv.DictReader(source)}==set(by_doi)
    ris=(ROOT/'research/library.ris').read_text()
    assert ris.count('ER  -')==len(records)
    assert all(not line or line[:6] in {'TY  - ','TI  - ','AU  - ','PY  - ','JO  - ','DO  - ','UR  - ','N1  - ','ER  - '} for line in ris.splitlines())
    assert (ROOT/'research/library.bib').read_text().count('\n  doi = {')==len(records)
    queue=json.loads((ROOT/'research/citation_queue.json').read_text())
    assert len(queue)==summary['citation_queue']
    assert not set(by_doi).intersection(r['doi'] for r in queue)


def test_research_is_available_without_the_atmospheric_model(monkeypatch):
    def unavailable():raise RuntimeError('No MCD installed')
    monkeypatch.setattr(server,'installation',unavailable)
    client=TestClient(server.app)
    assert client.get('/api/health').status_code==503
    assert client.get('/research').status_code==200
    response=client.get('/research/files/summary.json')
    assert response.status_code==200 and response.json()['core_records']>0


class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.links.extend(v for k,v in attrs if k=='href')


def test_reading_pages_keep_internal_links_navigable():
    client=TestClient(server.app)
    files=[*(ROOT/f'web/{name}.html' for name in ['research','home','ideas','data','tests','library']),*sorted((ROOT/'web/reading').glob('*.html'))]
    assert len(files)>5
    visited=set()
    for path in files:
        html=path.read_text();assert '<html lang="en">' in html
        parser=Links();parser.feed(html)
        for href in parser.links:
            url=href.split('#')[0]
            if url.startswith('/') and url not in visited:
                visited.add(url)
                assert client.get(url).status_code==200,(path,url)


def test_filtered_ris_is_a_real_attachment_and_matches_the_visible_filters():
    client=TestClient(server.app)
    response=client.get('/api/research/export',params={'scope':'all','fromYear':2026,'search':'dichotomy','depth':'sections'})
    assert response.status_code==200
    assert 'attachment;' in response.headers['content-disposition']
    assert response.text.count('ER  -')==1
    assert 'DO  - 10.1038/s41586-026-10893-x' in response.text
    assert client.get('/api/research/export',params={'search':'VERVELIDOU','topic':'Meteorite magnetism'}).text.count('ER  -')==1
    assert client.get('/api/research/export',params={'scope':'all','search':'not-a-real-Mars-title-unique'}).text==''
    summary=json.loads((ROOT/'research/summary.json').read_text())
    assert client.get('/api/research/export').text.count('ER  -')==summary['core_records']
