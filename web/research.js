'use strict';
const byId=id=>document.getElementById(id),pageSize=12;
let papers=[],filtered=[],page=0;
const depthLabels={metadata:'Metadata / preview only',abstract:'Abstract consulted',sections:'Selected full-text sections'};
const typeLabels={'journal-article':'Journal article','posted-content':'Posted content / preprint','proceedings-article':'Proceedings','book-chapter':'Book chapter','book':'Book','dataset':'Dataset'};
function element(tag,text,className){const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(className)el.className=className;return el;}
function externalLink(text,url){const a=element('a',text);a.href=url;a.target='_blank';a.rel='noopener';return a;}
function addOptions(id,values,labels={}){for(const value of [...new Set(values)].sort()){const o=element('option',labels[value]||value);o.value=value;byId(id).append(o);}}
function normalize(s){return String(s||'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase();}
function filterPapers(){
 const query=normalize(byId('search').value).trim().split(/\s+/).filter(Boolean),topic=byId('topic').value,scope=byId('scope').value,depth=byId('depth').value,kind=byId('kind').value,year=Number(byId('fromYear').value)||0;
 filtered=papers.filter(p=>(scope==='all'||p.core)&&(!topic||p.domains.includes(topic))&&(!depth||p.review_depth===depth)&&(!kind||p.type===kind)&&(!year||p.year>=year)&&query.every(word=>p.searchText.includes(word)));
 page=0;render();
 const url=new URL(location.href);
 for(const id of ['search','scope','topic','depth','kind','fromYear']){const value=byId(id).value;if(value&&(id!=='scope'||value!=='core'))url.searchParams.set(id,value);else url.searchParams.delete(id);}
 history.replaceState(null,'',url);
 const download=byId('exportFiltered');download.setAttribute('aria-disabled',String(!filtered.length));
 if(filtered.length)download.href='/api/research/export?'+url.searchParams;
 else download.removeAttribute('href');
}
function paperCard(p){
 const card=element('article',undefined,'paper'),top=element('div',undefined,'paper-top');
 top.append(element('span',String(p.year||'Undated'),'paper-year'),element('span',depthLabels[p.review_depth],'badge '+p.review_depth));
 if(p.core)top.append(element('span',p.primary_domain,'badge'));
 card.append(top);
 const title=element('h3');title.append(externalLink(p.title,p.url));card.append(title);
 const authors=p.authors.slice(0,4).join(', ')+(p.authors.length>4?' et al.':'');
 card.append(element('p',`${authors||'Author metadata unavailable'} · ${p.journal||'Venue not supplied'} · ${typeLabels[p.type]||p.type}`,'paper-meta'));
 const doi=externalLink(p.doi,p.url);doi.className='paper-doi';card.append(doi);
 if(p.finding){
  const notes=element('div',undefined,'paper-notes');
  for(const [label,body] of [['SOURCE FINDING / SCOPE',p.finding],['WHY IT MATTERS HERE',p.dichotomy_use]]){const group=element('div');group.append(element('strong',label),element('span',body));notes.append(group);}
  card.append(notes);
  const details=element('details');details.append(element('summary','Limits & reading record'),element('p',p.limitation),element('p',p.consulted_material));
  if(p.dates){const dates=Object.entries(p.dates).filter(([,d])=>d.length).map(([k,d])=>`${k.replace('published','Publication')}: ${d.join('-')}`).join(' · ');details.append(element('p',dates));}
  if(p.correction_doi)details.append(externalLink('Author correction ↗','https://doi.org/'+p.correction_doi));
  card.append(details);
 }else card.append(element('p','Discovery candidate. Relevance, publication status and scientific claims have not been assessed.','candidate-note'));
 return card;
}
function render(){
 const count=filtered.length,pages=Math.max(1,Math.ceil(count/pageSize)),start=page*pageSize;
 byId('resultCount').textContent=`${count.toLocaleString('en-US')} result${count===1?'':'s'} · ${byId('scope').value==='core'?'core reading route':'discovery catalog'}`;
 byId('papers').replaceChildren(...filtered.slice(start,start+pageSize).map(paperCard));
 if(!count)byId('papers').append(element('p','No matches. Try a broader term, clear a filter, or switch to all discovery candidates.','empty'));
 byId('pageCount').textContent=count?`${start+1}–${Math.min(start+pageSize,count)} of ${count.toLocaleString('en-US')}`:'No results';
 byId('previousPage').disabled=page===0;byId('nextPage').disabled=page>=pages-1;
}
function turnPage(delta){page+=delta;render();byId('library').scrollIntoView({block:'start'});}
async function loadLibrary(){
 try{
  const [catalogResponse,summaryResponse]=await Promise.all([fetch('/research/files/catalog.json'),fetch('/research/files/summary.json')]);
  if(!catalogResponse.ok||!summaryResponse.ok)throw new Error('The research files could not be loaded. Reload the page or consult the repository.');
  const [catalog,summary]=await Promise.all([catalogResponse.json(),summaryResponse.json()]);papers=catalog;
  byId('totalCount').textContent=summary.records.toLocaleString('en-US');byId('coreCount').textContent=summary.core_records;byId('readCount').textContent=summary.source_consulted;
  // A discovery-topic label must not make an unrelated title match a keyword.
  for(const p of papers)p.searchText=normalize([p.title,...p.authors,p.doi,p.finding,p.dichotomy_use,p.limitation].join(' '));
  addOptions('topic',papers.flatMap(p=>p.domains));addOptions('kind',papers.map(p=>p.type),typeLabels);
  const params=new URLSearchParams(location.search);
  for(const id of ['search','scope','topic','depth','kind','fromYear'])if(params.has(id)){byId(id).value=params.get(id);if(id==='scope'&&!byId(id).value)byId(id).value='core';}
  filterPapers();
 }catch(error){byId('libraryError').textContent=error.message;byId('libraryError').hidden=false;byId('resultCount').textContent='Catalog unavailable';}
}
byId('libraryFilters').addEventListener('submit',e=>e.preventDefault());
byId('libraryFilters').addEventListener('input',filterPapers);
byId('libraryFilters').addEventListener('reset',()=>setTimeout(filterPapers,0));
byId('previousPage').onclick=()=>turnPage(-1);byId('nextPage').onclick=()=>turnPage(1);
loadLibrary();
