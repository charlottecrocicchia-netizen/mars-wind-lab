"""Shared navigation used by generated scientific reading pages."""
from html import escape

DESTINATIONS=[('/', 'Overview'),('/research/data', 'Atlas'),('/research/tests', 'Results'),('/research/comparison', 'Hypotheses'),('/research/library', 'Sources')]

def navigation(active=''):
    if active=='/research/pilot':active='/research/tests'
    links=''.join('<a href="'+url+'"'+(' aria-current="page"' if url==active else '')+'>'+label+'</a>' for url,label in DESTINATIONS)
    return '<nav aria-label="Main navigation" lang="en">'+links+'</nav>'

def context(parent, label, description):
    return '<div class="route-context" lang="en"><a href="'+parent+'">← '+escape(label)+'</a><span>'+escape(description)+'</span></div>'
