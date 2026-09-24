"""Local-only research interface. No external account, telemetry, or publication."""
from pathlib import Path
import json
import numpy as np
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse, Response, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field, model_validator
from typing import Annotated, Literal
from . import analysis
from .mcd import ROOT, installation
from .export import dataset, csv_bytes, png_bytes, LABELS

app=FastAPI(title='Mars Wind Lab',version='0.5.0')
app.add_middleware(GZipMiddleware,minimum_size=1000)
app.mount('/assets',StaticFiles(directory=ROOT/'web'),name='assets')
app.mount('/research/files',StaticFiles(directory=ROOT/'research'),name='research-files')

class Parameters(BaseModel):
    ls:float=Field(255,ge=0,le=360)
    lt:float=Field(12,ge=0,lt=24)
    altitude:float=Field(60,ge=1,le=200)
    azimuth:float=Field(90,ge=0,le=360)
    time_mode:Literal['universal','local']='universal'
    lon:float=Field(135.623,ge=-180,le=180)
    lat:float=Field(4.502,ge=-89.5,le=89.5)
    degree:int=Field(500,ge=1,le=500)
    field:Literal['speed','u','v','w','temperature','effective_speed','shear']='speed'
    format:Literal['csv','nc','png','json']='csv'


class ExperimentParameters(BaseModel):
    lon:float=Field(135.623,ge=-180,le=180)
    lat:float=Field(4.502,ge=-89.5,le=89.5)
    ls:float=Field(255,ge=0,le=360)
    compare_ls:float=Field(75,ge=0,le=360)
    lt:float=Field(12,ge=0,lt=24)
    azimuth:float=Field(90,ge=0,le=360)
    z_min:float=Field(20,ge=0,le=195)
    z_max:float=Field(160,ge=5,le=200)
    period_s:float=Field(100,ge=1,le=300)
    question:Literal['direction','season','scale']='direction'
    @model_validator(mode='after')
    def layer(self):
        if self.z_max-self.z_min<5:
            raise ValueError('The layer must be at least 5 km thick.')
        return self


def clean(value):
    if isinstance(value,np.ndarray):return clean(value.tolist())
    if isinstance(value,dict):return {k:clean(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [clean(v) for v in value]
    if isinstance(value,(np.floating,float)):return float(value) if np.isfinite(value) else None
    if isinstance(value,np.integer):return int(value)
    return value


def options(p,geo=False):
    out={k:getattr(p,k) for k in ('ls','lt','time_mode','azimuth')}
    if geo:out.update(lon=p.lon,lat=p.lat)
    return out

@app.exception_handler(RuntimeError)
async def model_error(request,exc):
    return JSONResponse(status_code=503,content={'detail':str(exc)})

@app.get('/')
def index():return FileResponse(ROOT/'web/home.html')

@app.get('/atmosphere')
def atmosphere_index():return FileResponse(ROOT/'web/index.html')

@app.get('/research/hypotheses')
def ideas_index():return FileResponse(ROOT/'web/ideas.html')

@app.get('/research/data')
def observations_index():return FileResponse(ROOT/'web/data.html')

@app.get('/research/tests')
def tests_index():return FileResponse(ROOT/'web/tests.html')

@app.get('/research/library')
def library_index():return FileResponse(ROOT/'web/library.html')

@app.get('/research')
def research_index():return FileResponse(ROOT/'web/research.html')

@app.get('/api/research/export')
def research_export(search:str='',scope:Literal['core','all']='core',topic:str='',
                    depth:Literal['','metadata','abstract','sections']='',kind:str='',
                    from_year:int=Query(0,alias='fromYear',ge=0)):
    from .research import filtered_ris
    data=filtered_ris(search,scope,topic,depth,kind,from_year)
    return Response(data,media_type='application/x-research-info-systems; charset=utf-8',
                    headers={'Content-Disposition':'attachment; filename="mars-dichotomy-filtered.ris"'})

@app.get('/api/health')
def health():
    _,m,f=installation()
    return {'status':'ready','model':'MCD 6.1','source_sha256':m['source_sha256'],'data_fingerprint':f,'scenarios':[1]}

@app.get('/api/map')
def map_data(p:Annotated[Parameters,Query()]):
    return clean(analysis.map_product(altitude=p.altitude,**options(p)))

@app.get('/api/profile')
def profile(p:Annotated[Parameters,Query()]):
    return clean(analysis.profile_product(**options(p,True)))

@app.get('/api/section')
def section(p:Annotated[Parameters,Query()]):
    return clean(analysis.section_product(lon=p.lon,**options(p)))

@app.get('/api/seasonal')
def seasonal(p:Annotated[Parameters,Query()]):
    opts=options(p,True);opts.pop('ls')
    return clean(analysis.seasonal_product(altitude=p.altitude,**opts))

@app.get('/api/modes')
def modes(p:Annotated[Parameters,Query()]):
    return clean(analysis.modal_product(degree=p.degree,**options(p,True)))

@app.get('/api/export')
def export(p:Annotated[Parameters,Query()]):
    product=analysis.map_product(altitude=p.altitude,**options(p))
    filename=f'marswind_Ls{p.ls:g}_z{p.altitude:g}km_{p.time_mode}_{p.lt:g}h'
    if p.format=='csv':data=csv_bytes(product);mime='text/csv; charset=utf-8'
    elif p.format=='json':data=json.dumps(clean(product),ensure_ascii=False,indent=2);mime='application/json'
    elif p.format=='nc':data=bytes(dataset(product).to_netcdf(engine='scipy'));mime='application/x-netcdf'
    else:data=png_bytes(product,p.field);mime='image/png'
    return Response(data,media_type=mime,headers={'Content-Disposition':f'attachment; filename="{filename}.{p.format}"'})

@app.get('/api/legacy')
def legacy():
    from .legacy import load_archived_modes
    return clean(load_archived_modes())


@app.get('/api/experiment')
def experiment(p:Annotated[ExperimentParameters,Query()]):
    from .experiments import experiment_product
    try:
        return clean(experiment_product(**p.model_dump(exclude={'question'})))
    except ValueError as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc


@app.get('/api/study-note')
def note(p:Annotated[ExperimentParameters,Query()]):
    from .experiments import experiment_product,study_note
    try:
        result=experiment_product(**p.model_dump(exclude={'question'}))
    except ValueError as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc
    return Response(study_note(result,p.question),media_type='text/markdown; charset=utf-8',
                    headers={'Content-Disposition':'attachment; filename="marswind-study.md"'})


class MotionParameters(Parameters):
    axis:Literal['season','altitude']='season'
    fps:int=Field(2,ge=1,le=4)
    @model_validator(mode='after')
    def playback_rate(self):
        if self.fps not in (1,2,4):
            raise ValueError('Playback must be 1, 2 or 4 frames per second.')
        return self

@app.get('/api/sequence')
def sequence(p:Annotated[MotionParameters,Query()]):
    from .motion import sequence_product
    return clean(sequence_product(axis=p.axis,field=p.field,altitude=p.altitude,**options(p)))

@app.get('/api/sequence/stream')
def sequence_stream(p:Annotated[MotionParameters,Query()]):
    from .motion import sequence_events
    def events():
        try:
            for event in sequence_events(axis=p.axis,field=p.field,altitude=p.altitude,**options(p)):
                yield 'data: '+json.dumps(clean(event),separators=(',',':'))+'\n\n'
        except Exception as exc:
            yield 'data: '+json.dumps({'event':'error','detail':str(exc)})+'\n\n'
    # Event streams are excluded from GZip buffering, so progress arrives promptly.
    return StreamingResponse(events(),media_type='text/event-stream',headers={'Cache-Control':'no-cache'})

@app.get('/api/movie')
def movie(p:Annotated[MotionParameters,Query()]):
    from .motion import sequence_product,movie_bytes
    sequence=sequence_product(axis=p.axis,field=p.field,altitude=p.altitude,**options(p))
    return Response(movie_bytes(sequence,p.fps),media_type='video/mp4',
        headers={'Content-Disposition':f'attachment; filename="marswind_{p.axis}_{p.field}.mp4"'})
