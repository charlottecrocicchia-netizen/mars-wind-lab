"""Publish metadata and original notes only; raw abstracts/PDFs stay private.
Run harvest.py and enrich.py first, or pass --input to rebuild from a public catalog.
"""
from pathlib import Path
import csv, json, re, hashlib, argparse, html
from collections import Counter, defaultdict
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,default=ROOT/'output/research_raw/enriched.json');args=parser.parse_args()
records=json.loads(args.input.read_text())
annotations={r['doi']:r for r in csv.DictReader((Path(__file__).with_name('annotations.tsv')).open(),delimiter='\t')}
seeds=json.loads(Path(__file__).with_name('core_dois.json').read_text())
seed_domains={d:topic for topic,dois in seeds.items() for d in dois}
labels={'metadata':'Metadata / preview only','abstract':'Abstract consulted','sections':'Selected full-text sections consulted'}
allowed=['doi','title','authors','year','date','dates','journal','type','url','domains','discovery_domains','queries','references','metadata_source','retrieved','volume','pages','relations']
public=[]
for raw in records:
 r={k:raw[k] for k in allowed if k in raw};doi=r['doi'];r['core']=doi in seed_domains
 # Publisher line breaks must not become untagged continuation lines in RIS.
 for key in ['title','journal']:r[key]=' '.join(html.unescape(r.get(key,'')).split())
 r['authors']=[' '.join(html.unescape(author).split()) for author in r.get('authors',[])]
 r['review_depth']='metadata';r['review_status']='Discovery candidate — not screened';r['domain_basis']='Search query, not verified classification'
 if doi in annotations:
  r.setdefault('discovery_domains',r['domains']);r['domains']=[seed_domains[doi]]
  note=annotations[doi];r.update({k:note[k] for k in ['finding','dichotomy_use','limitation']});r['review_depth']=note['depth'];r['review_status']=labels[note['depth']];r['assessment_date']='2026-09-24';r['primary_domain']=seed_domains[doi];r['domain_basis']='Core topic assigned after source check';r['consulted_source']=r['url']
  if note['depth']=='abstract':r['consulted_material']='Publisher or author-hosted abstract; sometimes publisher-supplied Crossref abstract. Full methods not audited.'
  elif note['depth']=='sections':r['consulted_material']='Selected relevant full-text passages, plus abstract. Not a complete independent replication.'
  else:r['consulted_material']='Bibliographic record or limited publisher preview. No substantive results extraction claimed.'
 if doi=='10.1038/s41586-025-09361-9':r['correction_doi']='10.1038/s41586-025-09981-1'
 public.append(r)
public.sort(key=lambda r:(-(r['year'] or 0),r['doi']))
assert len({r['doi'] for r in public})==len(public)
assert set(annotations)<=set(r['doi'] for r in public)
out=ROOT/'research';out.mkdir(exist_ok=True)
(out/'catalog.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
# Metadata-only candidates are deliberately retained with their actual Crossref type.
fields=['doi','title','authors','year','journal','type','core','review_status','domains','finding','dichotomy_use','limitation','url']
with (out/'catalog.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader()
 for r in public:w.writerow({k:'; '.join(r.get(k,[])) if k in ['authors','domains'] else r.get(k,'') for k in fields})
def tex(s):
 return str(s).replace('\\',r'\textbackslash{}').replace('&',r'\&').replace('%',r'\%').replace('_',r'\_').replace('#',r'\#').replace('{','').replace('}','')
def bib(r):
 key='mars'+hashlib.sha256(r['doi'].encode()).hexdigest()[:12]
 kind={'journal-article':'article','proceedings-article':'inproceedings','book':'book','book-chapter':'incollection'}.get(r['type'],'misc')
 fields={'title':'{'+tex(r['title'])+'}','author':' and '.join(tex(a) for a in r['authors']),'year':r['year'] or '', 'journal':tex(r['journal']),'doi':r['doi'],'url':r['url'],'note':tex(r['review_status'])}
 return '@'+kind+'{'+key+',\n'+',\n'.join('  '+k+' = {'+str(v)+'}' for k,v in fields.items() if v)+'\n}\n'
(out/'library.bib').write_text('\n'.join(bib(r) for r in public))
(out/'core.bib').write_text('\n'.join(bib(r) for r in public if r['core']))
ris=[]
for r in public:
 ris.extend(['TY  - '+('JOUR' if r['type']=='journal-article' else 'GEN'),'TI  - '+r['title'],*['AU  - '+a for a in r['authors']],'PY  - '+str(r['year'] or ''),'JO  - '+r['journal'],'DO  - '+r['doi'],'UR  - '+r['url'],'N1  - '+r['review_status'],'ER  - ',''])
(out/'library.ris').write_text('\n'.join(ris))
known={r['doi'] for r in public};queue=defaultdict(set)
for r in public:
 if r['core']:
  for ref in r.get('references',[]):
   if ref not in known:queue[ref].add(r['doi'])
(out/'citation_queue.json').write_text(json.dumps([{'doi':d,'cited_by_core':sorted(parents),'status':'Not retrieved or screened; may be non-Mars background'} for d,parents in sorted(queue.items(),key=lambda x:(-len(x[1]),x[0]))],indent=2)+'\n')
log=json.loads((out/'search_log.json').read_text())
summary={'as_of':'2026-09-24','records':len(public),'core_records':sum(r['core'] for r in public),'source_consulted':sum(r['review_depth']!='metadata' for r in public),'review_depth_counts':dict(Counter(r['review_depth'] for r in public)),'types':dict(Counter(r['type'] for r in public)),'queries':len(log),'failed_queries':sum(bool(q['error']) for q in log),'citation_queue':len(queue),'complete_full_text_audits':0,'scope':'Broad evidence inventory and selective source assessment; not an exhaustive systematic review.'}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
