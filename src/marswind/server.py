"""Local research site. The website does not import or expose the MCD engine."""
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Query, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[2]
app = FastAPI(title='Martian dichotomy research', version='0.6.0')
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.mount('/assets', StaticFiles(directory=ROOT / 'web'), name='assets')
app.mount('/research/files', StaticFiles(directory=ROOT / 'research'), name='research-files')


@app.middleware('http')
async def refresh_local_snapshot(request: Request, call_next):
    """Keep evolving pages fresh while retaining conditional asset downloads."""
    response = await call_next(request)
    is_page = (response.headers.get('content-type', '').startswith('text/html')
               or request.url.path.endswith('.html'))
    response.headers['Cache-Control'] = 'no-store' if is_page else 'no-cache'
    return response


@app.get('/')
def index():
    return FileResponse(ROOT / 'web/home.html')


@app.get('/atmosphere', include_in_schema=False)
def retired_atmosphere():
    """Old bookmarks return to the current project without invoking a model."""
    return RedirectResponse('/', status_code=308)


@app.get('/research/comparison')
def comparison_index():
    return FileResponse(ROOT / 'web/comparison.html')


@app.get('/research/dynamo')
def dynamo_index():
    return FileResponse(ROOT / 'web/dynamo.html')


@app.get('/research/hypotheses')
def ideas_index():
    return FileResponse(ROOT / 'web/ideas.html')


@app.get('/research/data')
def observations_index():
    return FileResponse(ROOT / 'web/data.html')


@app.get('/research/tests')
def tests_index():
    return FileResponse(ROOT / 'web/tests.html')


@app.get('/research/experiments')
def experiments_index():
    return FileResponse(ROOT / 'web/experiments.html')


@app.get('/research/thermal')
def thermal_index():
    return FileResponse(ROOT / 'web/thermal.html')


@app.get('/research/library')
def library_index():
    return FileResponse(ROOT / 'web/library.html')


@app.get('/research/pilot')
def pilot_index():
    return FileResponse(ROOT / 'web/pilot/start.html')


@app.get('/research/pilot/{page}')
def pilot_page(page: Literal['regions', 'hypotheses', 'method', 'results']):
    return FileResponse(ROOT / f'web/pilot/{page}.html')


@app.get('/research', include_in_schema=False)
def research_index():
    return RedirectResponse('/research/library', status_code=308)


@app.get('/api/research/export')
def research_export(search: str = '', scope: Literal['core', 'all'] = 'core', topic: str = '',
                    depth: Literal['', 'metadata', 'abstract', 'sections'] = '', kind: str = '',
                    from_year: int = Query(0, alias='fromYear', ge=0)):
    from .research import filtered_ris
    data = filtered_ris(search, scope, topic, depth, kind, from_year)
    return Response(data, media_type='application/x-research-info-systems; charset=utf-8',
                    headers={'Content-Disposition': 'attachment; filename="mars-dichotomy-filtered.ris"'})


@app.get('/api/health')
def health():
    return {'status': 'ready', 'service': 'dichotomy-research', 'requires_mcd': False}
