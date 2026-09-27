import {windows, selectEvents, clipAge} from './comparison-model.mjs';
const $=id=>document.getElementById(id);
const el=(tag,text,className)=>{const e=document.createElement(tag); if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;};
let data,returnFocus;
function citations(ids){const p=el('p',undefined,'citations'); [...new Set(ids)].forEach((id,i)=>{if(i)p.append(' · '); const s=data.sources[id],a=el('a',s.label+' ↗');a.href=s.url;p.append(a);});return p;}
function options(id,items){items.forEach(([value,label])=>{const o=el('option',label);o.value=value;$(id).append(o);});}
function closeDetail(){ $('cellDetail').hidden=true; document.querySelectorAll('.matrix-cell').forEach(b=>b.setAttribute('aria-expanded','false')); }
function detail(observation,hypothesis,cell,button){
  closeDetail();returnFocus=button;button.setAttribute('aria-expanded','true');
  $('detailContext').textContent=observation.label+' / '+hypothesis.label;
  $('detailTitle').textContent=data.statuses[cell.status].label;
  const box=$('detailBody');box.replaceChildren();
  const parts=[['What is observed',observation.observation],['Evidence type and epoch',observation.kind+' · '+observation.epoch],['Observation limits',observation.uncertainty],['What this scenario must explain',cell.requirement],['Proposed test — not yet performed',cell.next_test],['Shared inputs to account for',observation.shared_inputs.join(' ; ')]];
  const dl=el('dl');parts.forEach(([title,text])=>{dl.append(el('dt',title),el('dd',text));});box.append(dl,citations([...observation.sources,...cell.sources]));
  $('cellDetail').hidden=false;$('detailTitle').focus();
}
function renderMatrix(){
 closeDetail(); const hs=data.hypotheses.filter(h=>!$('scenarioFilter').value||h.id===$('scenarioFilter').value);
 const obs=data.observations.filter(o=>!$('evidenceFilter').value||o.family===$('evidenceFilter').value);
 const head=$('matrix').querySelector('thead'),body=$('matrix').querySelector('tbody');head.replaceChildren();body.replaceChildren();
 const row=el('tr'); const first=el('th','Evidence to explain');first.scope='col';row.append(first);hs.forEach(h=>{const th=el('th',h.label);th.scope='col';row.append(th);});head.append(row);
 obs.forEach(o=>{const tr=el('tr'),th=el('th');th.scope='row';th.append(el('strong',o.label),el('small',o.family));tr.append(th);
  hs.forEach(h=>{const c=o.cells[h.id],td=el('td'),b=el('button',undefined,'matrix-cell '+c.status);b.type='button';b.setAttribute('aria-controls','cellDetail');b.setAttribute('aria-expanded','false');b.setAttribute('aria-label',o.label+' — '+h.label+' — '+data.statuses[c.status].label+': open details');b.append(el('span',data.statuses[c.status].label,'status-label'),el('span',c.summary),el('small','Condition and source →'));b.addEventListener('click',()=>detail(o,h,c,b));td.append(b);tr.append(td);});body.append(tr);
 });
 $('matrixCount').textContent=`${obs.length} observation${obs.length>1?'s':''} · ${hs.length} scenario${hs.length>1?'s':''}`;
 $('matrix').classList.toggle('single-scenario',hs.length===1);
}
function svgElement(tag,attrs){const e=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);return e;}
function eventCard(e,window){
 const article=el('article',undefined,'event-card '+(window?'dated':'undated'));article.dataset.event=e.id;
 const head=el('div',undefined,'event-heading');head.append(el('span',e.event_type+' · '+e.sample,'event-type'),el('h3',e.label),el('p',e.age.label,'event-age'));article.append(head);
 if(window){const p=clipAge(e.age,window),svg=svgElement('svg',{viewBox:'-12 0 1024 42',preserveAspectRatio:'none','aria-hidden':'true',class:'event-track '+e.age.kind});
  svg.append(svgElement('line',{x1:0,x2:1000,y1:21,y2:21,class:'track-line'}));
  if(p.right>p.left)svg.append(svgElement('line',{x1:p.left,x2:p.right,y1:21,y2:21,class:'age-bar'}));
  if(e.age.kind==='minimum')svg.append(svgElement('path',{d:`M ${p.left+9} 15 L ${p.left} 21 L ${p.left+9} 27`,class:'bound-arrow'}));
  else if(e.age.kind==='approximate')svg.append(svgElement('path',{d:`M ${p.left} 14 L ${p.left+5} 21 L ${p.left} 28 L ${p.left-5} 21 Z`,class:'age-dot'}));
  else {svg.append(svgElement('line',{x1:p.left,x2:p.left,y1:15,y2:27,class:'age-cap'}),svgElement('line',{x1:p.right,x2:p.right,y1:15,y2:27,class:'age-cap'}));}
  article.append(svg);
 }
 const more=el('details');more.append(el('summary','What this age means'));more.append(el('p',e.method),el('p',e.caveat),el('p',e.age.uncertainty),citations(e.sources));article.append(more);return article;
}
function renderTimeline(){
 const window=$('windowFilter').value,{dated,undated,excluded}=selectEvents(data.events,{sample:$('sampleFilter').value,type:$('eventFilter').value,window});
 const chart=$('timelineChart');chart.replaceChildren();const [young,old]=windows[window];
 const axis=el('div',undefined,'timeline-axis'),ticks=el('div',undefined,'axis-ticks');axis.append(el('span','Age before present · Ma'));[0,.25,.5,.75,1].forEach(t=>ticks.append(el('span',new Intl.NumberFormat('en-US',{maximumFractionDigits:1}).format(old-t*(old-young)))));axis.append(ticks);chart.append(axis);
 dated.forEach(e=>chart.append(eventCard(e,window)));
 if(!dated.length)chart.append(el('p','No dated events match these filters. Try another time window or reset.','empty-state'));
 $('undatedEvents').replaceChildren(...undated.map(e=>eventCard(e)));
 if(!undated.length)$('undatedEvents').append(el('p','No undated events in this selection.','reading-help'));
 $('timelineCount').textContent=`${dated.length} event(s) on the axis · ${undated.length} undated · ${excluded} outside the time window`;
}
function switchView(){
 const view=new URLSearchParams(location.search).get('view')==='timeline'?'timeline':'matrix';
 $('matrixView').hidden=view!=='matrix';$('timelineView').hidden=view!=='timeline';
 document.querySelectorAll('[data-view]').forEach(a=>{if(a.dataset.view===view)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
 document.title=(view==='timeline'?'Chronology':'Compare')+' · Martian dichotomy';
}
async function start(){
 try{const response=await fetch('/research/files/comparison/evidence.json?v=20260927-en');if(!response.ok)throw Error(response.status);data=await response.json();
  options('evidenceFilter',[...new Set(data.observations.map(o=>o.family))].map(x=>[x,x]));options('scenarioFilter',data.hypotheses.map(h=>[h.id,h.label]));options('sampleFilter',[...new Set(data.events.map(e=>e.sample))].map(x=>[x,x]));options('eventFilter',[...new Set(data.events.map(e=>e.event_type))].map(x=>[x,x]));
  data.hypotheses.forEach(h=>{const card=el('article');card.append(el('h3',h.label),el('p',h.description),citations(h.sources));$('scenarioCards').append(card);});
  Object.entries(data.statuses).forEach(([key,s])=>{const d=el('details',undefined,key);d.append(el('summary',s.label),el('p',s.meaning));$('statusLegend').append(d);});
  Object.values(data.sources).forEach(s=>{const li=el('li'),a=el('a',s.label+' ↗');a.href=s.url;li.append(a,el('p',s.consulted_material));$('references').append(li);});
  ['evidenceFilter','scenarioFilter'].forEach(id=>$(id).addEventListener('change',renderMatrix));['sampleFilter','eventFilter','windowFilter'].forEach(id=>$(id).addEventListener('change',renderTimeline));
  $('resetMatrix').addEventListener('click',()=>{$('evidenceFilter').value='';$('scenarioFilter').value='';renderMatrix();});
  $('resetTimeline').addEventListener('click',()=>{$('sampleFilter').value='';$('eventFilter').value='';$('windowFilter').value='all';renderTimeline();});
  $('closeDetail').addEventListener('click',()=>{closeDetail();returnFocus?.focus();});
  document.querySelectorAll('[data-view]').forEach(a=>a.addEventListener('click',event=>{if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;event.preventDefault();history.pushState({},'',a.href);switchView();}));window.addEventListener('popstate',switchView);
  renderMatrix();renderTimeline();switchView();$('loadStatus').hidden=true;
 }catch(error){$('loadStatus').textContent='The notes could not be loaded. Reload the page or open the downloads and method below.';$('loadStatus').setAttribute('role','alert');console.error(error);}
}
start();
