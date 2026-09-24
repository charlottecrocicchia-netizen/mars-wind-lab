"""Fetch versioned scientific products and preserve a checksum manifest.
Raw products stay in ignored data/observations/raw; only metadata is published.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,urllib.request,concurrent.futures,zipfile
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'data/observations/raw';RAW.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'research/data';OUT.mkdir(exist_ok=True)
REGISTRY=ROOT/'scripts/data/sources.json'

def request(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MarsResearch/0.5 (public scientific data)'}),timeout=90)

def digest(path):
    sha=hashlib.sha256();md5=hashlib.md5()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):sha.update(b);md5.update(b)
    return sha.hexdigest(),md5.hexdigest()

def validate_payload(path,name):
    with path.open('rb') as f:header=f.read(100)
    if name.endswith(('.zip','.xlsx','.docx')) and not zipfile.is_zipfile(path):raise ValueError('Expected ZIP-based scientific product, received an invalid response')
    if name.endswith('.pdf') and not header.startswith(b'%PDF'):raise ValueError('Expected PDF, received an invalid response')
    if name.endswith('.gz') and not header.startswith(b'\x1f\x8b'):raise ValueError('Expected gzip, received an invalid response')
    if name.endswith(('.csv','.dat','.txt')) and b'<html' in header.lower():raise ValueError('Expected tabular data, received HTML')
    if name.endswith(('.csv','.dat','.txt')) and header.startswith(b'PK\x03\x04'):raise ValueError('Expected tabular data, received ZIP; inspect and register the actual archive format')
    if name.endswith('.json'):
        data=json.loads(path.read_text())
        if isinstance(data,dict) and ('error' in data or data.get('exceededTransferLimit')):raise ValueError('API error or incomplete transfer')

def acquire(source,large=False):
    result=dict(source,checked_at=datetime.now(timezone.utc).isoformat(),files=[])
    try:
        if source.get('api'):
            with request(source['api']) as f:meta=json.load(f)
            folder=RAW/source['id'];folder.mkdir(exist_ok=True)
            (folder/'metadata.json').write_text(json.dumps(meta,indent=2))
            result['metadata_sha256']=digest(folder/'metadata.json')[0]
            if source['provider']=='zenodo':
                result['license']=meta['metadata'].get('license',{}).get('id','not specified')
                files=[{'name':x['key'],'url':x['links']['self'],'size':x['size'],'md5':x['checksum'].removeprefix('md5:')} for x in meta['files']]
            else:
                result['license']=meta.get('license',{}).get('name','not specified')
                files=[{'name':x['name'],'url':x['download_url'],'size':x['size'],'md5':x.get('computed_md5')} for x in meta['files']]
        else:files=source['products'];folder=RAW/source['id'];folder.mkdir(exist_ok=True)
        for spec in files:
            if Path(spec['name']).name!=spec['name']:raise ValueError('Product name must be a basename')
            f=dict(spec);path=folder/spec['name'];f['local_path']=str(path.relative_to(ROOT))
            if spec.get('size',0)>500_000_000 and not large:
                f['status']='available; use --large';result['files'].append(f);continue
            try:
                valid=False
                if path.exists():
                    sha,md5=digest(path)
                    try:validate_payload(path,spec['name'])
                    except ValueError:md5='invalid'
                    valid=md5==spec['md5'] if spec.get('md5') else md5!='invalid' and path.stat().st_size>0
                if not valid:
                    partial=path.with_name(path.name+'.part')
                    with request(spec['url']) as response,partial.open('wb') as dest:
                        for chunk in iter(lambda:response.read(2**20),b''):dest.write(chunk)
                    validate_payload(partial,spec['name'])
                    sha,md5=digest(partial)
                    if spec.get('md5') and md5!=spec['md5']:raise ValueError('Provider MD5 mismatch')
                    if spec.get('size') and partial.stat().st_size!=spec['size']:raise ValueError('Size mismatch')
                    partial.replace(path)
                f.update(status='downloaded',sha256=sha,bytes=path.stat().st_size,provider_checksum_verified=bool(spec.get('md5')))
                print(source['id'],spec['name'],f['bytes'],flush=True)
            except Exception as exc:f.update(status='unavailable',error=str(exc));print(source['id'],spec['name'],str(exc),flush=True)
            result['files'].append(f)
        states={f['status'] for f in result['files']}
        result['status']='downloaded' if states=={'downloaded'} else 'partial or unavailable'
    except Exception as exc:result.update(status='unavailable',error=str(exc))
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--only',nargs='*');p.add_argument('--large',action='store_true');args=p.parse_args()
    sources=json.loads(REGISTRY.read_text());chosen=[s for s in sources if not args.only or s['id'] in args.only]
    output=OUT/'manifest.json';previous={s['id']:s for s in json.loads(output.read_text())} if output.exists() else {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(acquire,s,args.large) for s in chosen]
        for future in concurrent.futures.as_completed(futures):
            record=future.result()
            if output.exists():previous.update({s['id']:s for s in json.loads(output.read_text())})
            previous[record['id']]=record
            pending=output.with_suffix('.tmp')
            pending.write_text(json.dumps(list(previous.values()),indent=2)+'\n');pending.replace(output)
    print('Saved',output,flush=True)
if __name__=='__main__':main()
