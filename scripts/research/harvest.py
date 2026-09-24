"""Reproducible candidate discovery; metadata retrieval is NOT full-text review."""
import json,re,time,hashlib,html,urllib.request,urllib.parse
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/research_raw';OUT.mkdir(parents=True,exist_ok=True)
DEST=ROOT/'research';DEST.mkdir(exist_ok=True)
queries=json.loads((Path(__file__).with_name('queries.json')).read_text())
records={};log=[];rejected=[]
pattern=re.compile(r'\b(mars|martian|alh\s?84001|nwa\s?(7034|7533|817|998|8159)|shergottit\w*|nakhlit\w*|chassignit\w*|tissint|shergotty|nakhl[a-z]*|zagami|eeta\s?79001)\b',re.I)
def plain(t):return html.unescape(re.sub('<[^>]+>','',t))
for domain,q,rows in queries:
 params={'query.title':q,'rows':rows,'filter':'until-pub-date:2026-09-24','select':'DOI,title,author,published,container-title,type,URL,reference,abstract,link,license'}
 url='https://api.crossref.org/works?'+urllib.parse.urlencode(params)
 path=OUT/(hashlib.sha256(url.encode()).hexdigest()[:16]+'.json')
 started=datetime.now(timezone.utc).isoformat()
 try:
  if path.exists():raw=json.loads(path.read_text())
  else:
   for attempt in range(4):
    try:
     request=urllib.request.Request(url,headers={'User-Agent':'MarsDichotomyResearch/0.1 (public bibliographic research)'})
     with urllib.request.urlopen(request,timeout=60) as f:raw=json.load(f)
     path.write_text(json.dumps(raw));break
    except Exception:
     if attempt==3:raise
     time.sleep(3*(attempt+1))
  items=raw['message']['items'];kept=0
  for rank,item in enumerate(items,1):
   title=plain(' '.join(item.get('title',[])));doi=item.get('DOI','').lower()
   if not doi or not pattern.search(title):
    rejected.append({'doi':doi,'title':title,'query':q,'reason':'No Mars or named Martian meteorite title term'});continue
   kept+=1
   if doi not in records:
    authors=[' '.join([a.get('given',''),a.get('family',a.get('name',''))]).strip() for a in item.get('author',[])]
    date=item.get('published',{}).get('date-parts',[[]])[0]
    records[doi]={'doi':doi,'title':title,'authors':authors,'year':date[0] if date else None,'date':date,'journal':' '.join(item.get('container-title',[])),'type':item.get('type','unknown'),'url':'https://doi.org/'+doi,'domains':[],'queries':[],'review_status':'metadata only — not screened','references':[x['DOI'].lower() for x in item.get('reference',[]) if x.get('DOI')],'has_abstract':bool(item.get('abstract')),'abstract':plain(item.get('abstract','')),'metadata_source':'Crossref REST API','retrieved':started}
   r=records[doi]
   if domain not in r['domains']:r['domains'].append(domain)
   r['queries'].append({'query':q,'rank':rank})
  log.append({'query':q,'domain':domain,'url':url,'requested_rows':rows,'returned':len(items),'title_retained':kept,'total_results_reported':raw['message'].get('total-results'),'retrieved':started,'raw_cache':str(path.relative_to(ROOT)),'error':None})
  print(f'{q}: {kept}/{len(items)} retained; {len(records)} unique',flush=True)
 except Exception as exc:
  log.append({'query':q,'domain':domain,'url':url,'retrieved':started,'error':str(exc)});print(f'ERROR {q}: {exc}',flush=True)
 (DEST/'search_log.json').write_text(json.dumps(log,indent=2))
 (OUT/'candidates_with_abstracts.json').write_text(json.dumps(list(records.values()),indent=2,ensure_ascii=False))
 (OUT/'rejected.json').write_text(json.dumps(rejected,indent=2))
 time.sleep(.4)
print('DONE',len(records),flush=True)
