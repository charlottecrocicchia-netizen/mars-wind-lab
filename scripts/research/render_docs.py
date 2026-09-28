"""Render committed, project-authored Markdown research notes to static HTML."""
from pathlib import Path
from site_layout import navigation as main_navigation, context
from reading_collection import PAGES, dossier_for, dossier_navigation, note_context
from site_links import rewrite_links
from html import escape, unescape
import re
import markdown
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'web/reading';out.mkdir(exist_ok=True)
for stem,label in PAGES.items():
 source=(ROOT/f'research/{stem}.md').read_text()
 body=markdown.markdown(source,extensions=['tables','fenced_code','toc'])
 body=rewrite_links(body, ROOT/f'research/{stem}.md')
 navigation=dossier_navigation(dossier_for(stem))
 html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(label)} — Mars Dichotomy</title><link rel="stylesheet" href="/assets/research.css?v=design1"><link rel="stylesheet" href="/assets/workspace.css?v=20260927-design"></head><body class="workspace">
<a class="skip" href="#article">Skip to the article</a><header class="workspace-header"><a href="/" class="wordmark"><i></i><span>Martian dichotomy<small>CHARLOTTE CROCICCHIA</small></span></a>{main_navigation('/research/library')}</header>
<main class="reading-layout"><aside class="reading-nav" aria-label="Reading navigation"><p class="eyebrow">FIVE READING DOSSIERS</p>{navigation}</aside><article class="prose" id="article">{note_context(stem)}{body}<div class="reading-tools"><a href="/research/explore#dossiers">← Reading dossiers</a><a href="/research/files/{stem}.md" download>Download Markdown ↓</a><a href="https://github.com/charlottecrocicchia-netizen/mars-wind-lab/blob/main/research/{stem}.md">View on GitHub ↗</a></div></article></main>
<footer><span>Living research notes · Check each article’s date, sources and limitations.</span><span>Project research notes assembled with AI assistance. Reading depth and outstanding checks are documented in the method.</span></footer></body></html>'''
 (out/(stem.lower()+'.html')).write_text(html)
 print(out/(stem.lower()+'.html'))
