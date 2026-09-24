import json,urllib.request,urllib.parse,time,re,html
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];raw=ROOT/'output/research_raw'
records={r['doi']:r for r in json.loads((raw/'candidates_with_abstracts.json').read_text())}
seeds=json.loads(Path(__file__).with_name('core_dois.json').read_text());read=[]
for domain,dois in seeds.items():
 for doi in dois:
  doi=doi.lower();path=raw/('doi_'+re.sub('[^a-z0-9]','_',doi)+'.json')
  try:
   if path.exists():item=json.loads(path.read_text())
   else:
    url='https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='')
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MarsDichotomyResearch/0.1'}),timeout=40) as f:item=json.load(f)['message']
    path.write_text(json.dumps(item));time.sleep(.25)
   plain=lambda t:html.unescape(re.sub('<[^>]+>','',t))
   dates={k:item.get(k,{}).get('date-parts',[[]])[0] for k in ['published','published-print','published-online']}
   r=records.setdefault(doi,{'doi':doi,'domains':[],'queries':[],'review_status':'metadata only — not screened','metadata_source':'Crossref DOI lookup','retrieved':datetime.now(timezone.utc).isoformat()})
   r.update(title=plain(' '.join(item.get('title',[]))),authors=[' '.join([a.get('given',''),a.get('family',a.get('name',''))]).strip() for a in item.get('author',[])],year=dates['published'][0] if dates['published'] else None,date=dates['published'],dates=dates,journal=' '.join(item.get('container-title',[])),type=item.get('type','unknown'),url='https://doi.org/'+doi,abstract=plain(item.get('abstract','')),has_abstract=bool(item.get('abstract')),references=[x['DOI'].lower() for x in item.get('reference',[]) if x.get('DOI')],relations=item.get('relation',{}),volume=item.get('volume',''),pages=item.get('page',item.get('article-number','')))
   if domain not in r['domains']:r['domains'].append(domain)
   r['seed']=True
   read.append(f"\n### {r['year']} | {doi}\n{r['title']}\n{r['abstract'] or 'ABSTRACT MISSING — consult primary source'}\n")
   print(doi,flush=True)
  except Exception as e:print('FAILED',doi,str(e),flush=True)
(raw/'enriched.json').write_text(json.dumps(list(records.values()),indent=2,ensure_ascii=False))
(raw/'core_reading.txt').write_text('\n'.join(read))
print('DONE',len(read),len(records),flush=True)
