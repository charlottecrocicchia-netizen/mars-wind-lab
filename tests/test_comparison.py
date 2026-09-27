"""Scientific qualifiers must survive display and portable export."""
import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from html.parser import HTMLParser
from fastapi.testclient import TestClient
from marswind.server import app

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'research/comparison/evidence.json').read_text())


def test_every_comparison_has_explicit_scope_and_traceable_sources():
    assert DATA['language']=='en'
    source_ids=set(DATA['sources'])
    hypotheses={h['id'] for h in DATA['hypotheses']}
    assert len(hypotheses)==4 and len(DATA['observations'])==5
    for o in DATA['observations']:
        assert set(o['cells'])==hypotheses
        assert o['uncertainty'] and o['epoch'] and o['shared_inputs']
        assert set(o['sources'])<=source_ids
        for c in o['cells'].values():
            assert c['status'] in DATA['statuses']
            assert c['requirement'] and c['next_test'] and c['sources']
            assert set(c['sources'])<=source_ids
            assert not {'score','probability','posterior'} & c.keys()
    for e in DATA['events']:
        assert e['caveat'] and e['method'] and e['sources']
        assert set(e['sources'])<=source_ids
        a=e['age']
        if a['kind']=='unknown':
            assert all(a[k] is None for k in ['value_ma','younger_ma','older_ma'])
        elif a['kind']=='minimum':
            assert a['younger_ma']>0 and a['older_ma'] is None
        elif a['kind'] in ['range','estimate']:
            assert 0<=a['younger_ma']<=a['older_ma']
    events={e['id']:e for e in DATA['events']}
    assert len(events)==len(DATA['events'])
    assert events['laf_water']['age']['uncertainty']=='Reported ±15 Ma, 2σ.'
    assert events['nakhla_shock']['sample']=='Nakhla'
    for relation in DATA['relations']:
        older,younger=events[relation['older']],events[relation['younger']]
        assert older['sample']==younger['sample']
        old_min=older['age']['younger_ma'] or older['age']['value_ma']
        young_max=younger['age']['older_ma'] or younger['age']['value_ma']
        assert old_min>young_max


def test_csv_exports_are_current_and_preserve_nulls_bounds_and_caveats():
    spec=importlib.util.spec_from_file_location('export_comparison',ROOT/'scripts/research/export_comparison.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    for filename,rows in module.tables(DATA).items():
        assert (ROOT/'research/comparison'/filename).read_text()==module.render(rows)
    with (ROOT/'research/comparison/events.csv').open() as f:
        events={r['event_id']:r for r in csv.DictReader(f)}
    for id in ['global_dichotomy','laf_remanence']:
        assert all(events[id][k]=='' for k in ['value_ma','younger_ma','older_ma'])
        assert events[id]['caveat'] and events[id]['sources']
    assert events['nwa_reservoir']['older_ma']==''
    assert events['nwa_crystal']['kind']=='range'
    assert events['laf_water']['age_unit']=='Ma before present'


def test_site_starts_without_importing_atmospheric_modules():
    subprocess.run([sys.executable,'-c',
        "import sys; from fastapi.testclient import TestClient; from marswind.server import app; "
        "assert TestClient(app).get('/api/research/export').status_code == 200; "
        "assert not {'marswind.mcd','marswind.analysis','marswind.motion'} & sys.modules.keys()"],
        cwd=ROOT,check=True)
    launcher=(ROOT/'Launch Mars Wind.command').read_text()
    assert 'build_mcd' not in launcher
    client=TestClient(app)
    for path in ['/research/comparison','/research/files/comparison/evidence.json',
                 '/research/files/comparison/matrix.csv','/research/files/comparison/events.csv']:
        assert client.get(path).status_code==200


class Navigation(HTMLParser):
    def __init__(self):super().__init__();self.inside=False;self.links=[];self.current=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='nav' and attrs.get('aria-label')=='Main navigation':self.inside=True
        if tag=='a' and self.inside:
            self.links.append(attrs['href'])
            if attrs.get('aria-current')=='page':self.current.append(attrs['href'])
    def handle_endtag(self,tag):
        if tag=='nav':self.inside=False


def test_navigation_has_the_same_five_destinations_on_all_pages():
    expected=['/','/research/comparison','/research/data','/research/pilot','/research/library']
    for path in (ROOT/'web').rglob('*.html'):
        parser=Navigation();parser.feed(path.read_text())
        assert parser.links==expected,path
        assert len(parser.current)==1,path
        assert 'href="/atmosphere"' not in path.read_text()
