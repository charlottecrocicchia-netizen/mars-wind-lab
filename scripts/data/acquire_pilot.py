"""Fetch the additional public sources used in the regional pilot.

Raw sources stay local. Pin the author catalog by commit; subsequent builds
record byte hashes. The archive has no explicit license in its README.
"""
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/observations/raw/pilot'
SOURCES={
    'newton.html':'https://planetarynames.wr.usgs.gov/Feature/4236',
    'copernicus.html':'https://planetarynames.wr.usgs.gov/Feature/1297',
    'huygens.html':'https://planetarynames.wr.usgs.gov/Feature/2596',
    'schiaparelli.html':'https://planetarynames.wr.usgs.gov/Feature/5366',
    'mocaas.html':'https://www.ias.u-psud.fr/moccas/',
    'lagain_db.json.zip':'https://raw.githubusercontent.com/alagain/martian_crater_database/ccd5de7bbc6525d25d746332b4a1e58ba1f72680/Global/lagain_db.json.zip',
}

def main():
    OUT.mkdir(exist_ok=True,parents=True)
    records=[]
    for name,url in SOURCES.items():
        path=OUT/name
        if not path.exists():
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 Mars research data retrieval'})
            with urllib.request.urlopen(req,timeout=60) as response:
                data=response.read()
            if name.endswith('.zip') and not data.startswith(b'PK'):
                raise ValueError('Expected a ZIP archive')
            path.write_bytes(data)
        records.append({'file':name,'url':url,'bytes':path.stat().st_size,
                        'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        print(name,path.stat().st_size,flush=True)
    (ROOT/'research/pilot/sources.json').write_text(json.dumps(records,indent=2)+'\n')

if __name__=='__main__':main()
