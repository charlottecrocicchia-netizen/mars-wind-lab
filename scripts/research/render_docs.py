"""Render committed, project-authored Markdown research notes to static HTML."""
from pathlib import Path
from html import escape, unescape
import re
import markdown
ROOT=Path(__file__).resolve().parents[2]
PAGES={'SYNTHESIS':'Scientific synthesis','METEORITES':'Meteorite magnetism','MISSIONS':'Missions & data','RESEARCH_PLAN':'Research programme','METHOD':'Search & reading method','COMMUNITY':'Community leads','README':'About this collection'}
out=ROOT/'web/reading';out.mkdir(exist_ok=True)
for stem,label in PAGES.items():
 source=(ROOT/f'research/{stem}.md').read_text()
 body=markdown.markdown(source,extensions=['tables','fenced_code','toc'])
 def links(match):
  href=unescape(match[1])
  if href.endswith('.md') and href[:-3] in PAGES:href='/assets/reading/'+href[:-3].lower()+'.html'
  elif not href.startswith(('http:','https:','/','#')):href='/research/files/'+href
  return 'href="'+escape(href,quote=True)+'"'
 body=re.sub(r'href="([^"]+)"',links,body)
 navigation=''.join(f'<a class="{"current" if name==stem else ""}" href="/assets/reading/{name.lower()}.html">{escape(title)}</a>' for name,title in PAGES.items())
 html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(label)} — Mars Dichotomy</title><link rel="stylesheet" href="/assets/research.css"></head><body>
<a class="skip" href="#article">Skip to the article</a><header class="research-header"><a href="/research" class="brand"><span class="planet-icon"></span><span>MARS DICHOTOMY<small>CHARLOTTE CROCICCHIA · EVIDENCE ATLAS</small></span></a><nav aria-label="Main navigation"><a href="/">Wind atlas ↗</a><a href="/research#library">Research library ↗</a></nav></header>
<main class="reading-layout"><aside class="reading-nav" aria-label="Reading navigation"><p class="eyebrow">READING ROOM</p>{navigation}</aside><article class="prose" id="article">{body}<div class="reading-tools"><a href="/research#library">← Browse the library</a><a href="/research/files/{stem}.md" download>Download Markdown ↓</a><a href="https://github.com/charlottecrocicchia-netizen/mars-wind-lab/blob/main/research/{stem}.md">View on GitHub ↗</a></div></article></main>
<footer><span>Research snapshot · 24 September 2026 · Read the source and its limitations together.</span><span>Project research notes assembled with AI assistance. Reading depth and outstanding checks are documented in the method.</span></footer></body></html>'''
 (out/(stem.lower()+'.html')).write_text(html)
 print(out/(stem.lower()+'.html'))
