"""Build lab and aqueous-mineral views after acquire.py and build.py.

The water product retains occupied 2-degree cells, not raster colours or an
invented survey mask. Every nonzero pixel is considered: nearest-neighbour
downsampling would lose small deposits. Empty compressed tiles are skipped only
after their exact bytes have been decoded and verified to contain zeros.
"""
from pathlib import Path
import hashlib
import json
import sys
import zipfile
import math
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'src'))
from marswind.paleomagnetism import magic_tables, read_rockpy_nrm, detection_cells
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'data/observations/raw'
OUT=ROOT/'research/data'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n')
    print('Saved', name, flush=True)


def labs():
    series=[]
    for path in sorted((RAW/'mil03346').glob('*.nrm')):
        rows=read_rockpy_nrm(path.read_text())
        series.append({'id':path.stem,'file':path.name,'rows':rows,'input_sha256':sha(path),
                       'context':'Fusion crust present' if path.stem in ['MIL1.1','MIL2.1','MIL3'] else 'Interior / see allocation in paper'})
    with zipfile.ZipFile(RAW/'alh84001/magic_contribution_19859.zip') as archive:
        text=archive.read('MagIC_final/magic_contribution_19859.txt').decode('utf-8')
    tables=magic_tables(text)
    save('laboratory_extended.json', {'mil':{'source':'https://doi.org/10.7910/DVN/S0R98P','license':'CC0 1.0','series':series,
         'note':'Natural-remanence files parsed; an appended laboratory TRM acquisition is retained in the download but excluded from the NRM plot. ARM, IRM, anisotropy and hysteresis files are archived separately. Export units are not explicit; curves use measurement order and relative magnitude.'},
         'alh':{'source':'https://earthref.org/MagIC/19859','license':'CC BY 4.0','specimens':tables.get('specimens',[]),'measurements':tables.get('measurements',[]),
         'note':'MagIC measurements grouped by specimen and experiment. Laboratory-imparted remanence must not be interpreted as an ancient field.'},
         'pipeline_sha256':sha(Path(__file__)),'module_sha256':sha(ROOT/'src/marswind/paleomagnetism.py'),
         'inputs':{'alh84001_contribution_sha256':hashlib.sha256(text.encode()).hexdigest()}})


CLASSES={'RED':('Fe/Mg clays','#e3a080'),'GREEN':('Polyhydrated / hydroxylated sulfates; locally zeolites','#c9b593'),
         'BLUE':('Monohydrated sulfates','#a899cd'),'ORANGE':('Carbonates; locally serpentine','#efba67'),
         'CYAN':('Al clays / hydrated silica','#87aebe')}


def water():
    import tifffile
    import rasterio
    folder=RAW/'aqueous_minerals/rasters'
    folder.mkdir(exist_ok=True)
    with zipfile.ZipFile(RAW/'aqueous_minerals/MOCAAS_2023-11-15_v2.zip') as archive:
        for info in archive.infolist():
            path=folder/Path(info.filename).name
            if not path.exists():path.write_bytes(archive.read(info))
    products=[]
    for path in sorted(folder.glob('*.tiff')):
        instrument=path.name.split('_')[2];kind=path.name.split('_')[3]
        with rasterio.open(path) as ds:
            transform=ds.transform
            assert 'Mars' in ds.crs.to_wkt() and 'Equirectangular' in ds.crs.to_wkt()
            assert transform.b==0 and transform.d==0
        occupied=set();pixels=0;nonempty_tiles=0
        with tifffile.TiffFile(path) as tif:
            pg=tif.pages[0];radius=pg.geotiff_tags['GeogSemiMajorAxisGeoKey']
            assert pg.samplesperpixel==3 and pg.predictor==1
            tile_cols=math.ceil(pg.imagewidth/pg.tilewidth)
            blank=set();raw=path.read_bytes()
            for idx,(offset,nbytes) in enumerate(zip(pg.dataoffsets,pg.databytecounts)):
                compressed=raw[offset:offset+nbytes]
                if compressed in blank:continue
                data,_,_=pg.decode(compressed,idx)
                if not np.any(data):blank.add(compressed);continue
                y,x=np.where(np.any(data[0]!=0,axis=-1))
                row=(idx//tile_cols)*pg.tilelength+y;col=(idx%tile_cols)*pg.tilewidth+x
                valid=(row<pg.imagelength)&(col<pg.imagewidth)
                row,col=row[valid],col[valid]
                if not len(row):continue
                lat=np.rad2deg((transform.f+transform.e*(row+.5))/radius)
                lon=np.rad2deg((transform.c+transform.a*(col+.5))/radius)
                occupied.update(map(tuple,detection_cells(lon,lat)))
                pixels+=len(row);nonempty_tiles+=1
        cells=[[int(i),int(j)] for i,j in sorted(occupied)]
        products.append({'instrument':instrument,'class':kind,'label':CLASSES[kind][0],'color':CLASSES[kind][1],
                         'cells':cells,'detected_pixels':pixels,'nonempty_tiles':nonempty_tiles,
                         'file':path.name,'input_sha256':sha(path)})
        print(instrument,kind,len(cells),'occupied cells;',pixels,'pixels',flush=True)
    atlas=json.loads((OUT/'atlas.json').read_text())
    # Descriptive overlap only: no null samples without a valid coverage mask.
    joined=[]
    for kind in CLASSES:
        cells=set(tuple(c) for p in products if p['class']==kind for c in p['cells'])
        fields=[atlas['magnetic_nT']['150'][i][j] for i,j in cells]
        joined.append({'class':kind,'occupied_cells':len(cells),
                       'field_min_nT':min(fields) if fields else None,
                       'field_median_nT':float(np.median(fields)) if fields else None,
                       'field_max_nT':max(fields) if fields else None})
    save('water.json',{'source':'https://www.ias.u-psud.fr/moccas/','paper':'https://doi.org/10.1016/j.icarus.2022.115164',
        'version':'November 2023','latitude':atlas['latitude'],'longitude':atlas['longitude'],
        'products':products,'overlap_diagnostic':joined,
        'status':'Presence-only screening; no mineral–magnetism association or origin test',
        'license':'No explicit raster reuse license stated on the project page. Original rasters remain local; this is a coarse, project-computed numerical occupancy summary.',
        'notes':['A marked 2-degree cell contains at least one detection; it is not all altered.',
                 'A blank cell is unknown, not dry or unaltered. A survey/exposure mask is not supplied.',
                 'These are surface spectral classes, not measured water volume, age, magnetic carrier abundance or deep alteration.',
                 'The same deposit may be observed by both instruments. Union cells, not summed observations, are used in the overlap diagnostic.',
                 'Model field values are sampled at occupied display-cell centers, not at each native pixel. No area fraction or p-value is inferred.'],
        'pipeline_sha256':sha(Path(__file__)),'module_sha256':sha(ROOT/'src/marswind/paleomagnetism.py'),
        'atlas_sha256':sha(OUT/'atlas.json'),'archive_sha256':sha(RAW/'aqueous_minerals/MOCAAS_2023-11-15_v2.zip')})


if __name__=='__main__':
    if '--water-only' not in sys.argv:labs()
    if '--lab-only' not in sys.argv:water()
