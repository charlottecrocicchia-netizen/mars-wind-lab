"""Shared navigation used by generated scientific reading pages."""
from html import escape

DESTINATIONS=[('/', 'Questions & answers'),('/research/method', 'How we work'),('/research/tests', 'Results'),('/research/explore', 'Explore')]

def navigation(active=''):
    if active and active not in dict(DESTINATIONS):active='/research/explore'
    links=''.join('<a href="'+url+'"'+(' aria-current="page"' if url==active else '')+'>'+escape(label)+'</a>' for url,label in DESTINATIONS)
    return '<nav aria-label="Main navigation" lang="en">'+links+'</nav>'

def context(parent, label, description):
    return '<div class="route-context" lang="en"><a href="'+parent+'">← '+escape(label)+'</a><span>'+escape(description)+'</span></div>'
