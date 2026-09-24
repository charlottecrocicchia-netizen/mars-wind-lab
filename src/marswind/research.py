"""Serve a filtered bibliography as a normal HTTP attachment, without MCD."""
import json
import unicodedata
from .mcd import ROOT


def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFKD',str(value or '')) if not unicodedata.combining(c)).lower()


def filtered_ris(search='',scope='core',topic='',depth='',kind='',from_year=0):
    records=json.loads((ROOT/'research/catalog.json').read_text())
    words=normalize(search).split();output=[]
    for p in records:
        if scope=='core' and not p['core']:continue
        if topic and topic not in p['domains']:continue
        if depth and p['review_depth']!=depth:continue
        if kind and p['type']!=kind:continue
        if from_year and (p['year'] or 0)<from_year:continue
        text=normalize(' '.join([p['title'],*p['authors'],p['doi'],p.get('finding',''),p.get('dichotomy_use',''),p.get('limitation','')]))
        if not all(word in text for word in words):continue
        output.extend(['TY  - '+('JOUR' if p['type']=='journal-article' else 'GEN'),'TI  - '+p['title'],*['AU  - '+a for a in p['authors']],'PY  - '+str(p['year'] or ''),'JO  - '+p['journal'],'DO  - '+p['doi'],'UR  - '+p['url'],'N1  - '+p['review_status'],'ER  - ',''])
    return '\n'.join(output)
