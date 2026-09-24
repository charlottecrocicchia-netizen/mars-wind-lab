'use strict';
const $=id=>document.getElementById(id);
let state={ls:255,lt:12,altitude:60,azimuth:90,time_mode:'universal',lon:135.623,lat:4.502,field:'speed',degree:500};
let mapData=null,profileData=null,projection='flat',currentTab='guide',revision=0,loaded={},busy=0,refreshing=false;
const fmt=(v,d=1)=>v==null||!Number.isFinite(v)?'—':v.toLocaleString('en-GB',{minimumFractionDigits:d,maximumFractionDigits:d});
const units={speed:'m/s',u:'m/s',v:'m/s',w:'m/s',temperature:'K',effective_speed:'m/s',shear:'m/s/km'};
const labels={speed:'Horizontal speed',u:'Zonal wind',v:'Meridional wind',w:'Vertical wind',temperature:'Temperature',effective_speed:'Effective sound speed',shear:'Vertical shear'};
const palette=['#142c48','#25637a','#4c918d','#a2b885','#e2c37d','#f2a766'];
const diverging=['#265273','#629699','#c5d5c1','#f7f4df','#dfa170','#bd5539','#762e34'];
const titles={guide:['From winds to waves,<br><em>understand what changes.</em>','Choose a question, compare two hypotheses, and understand what the physics tells you.'],legacy:['Recover the modes,<br><em>question the results.</em>','Original eigenfunctions read from local archives, with explicit normalization diagnostics.'],atlas:['The Martian atmosphere,<br><em>in motion.</em>','From surface winds to upper atmospheric jets. An atlas sampled from the Mars Climate Database.'],structure:['Read the atmosphere,<br><em>through its layers.</em>','Local profiles and geometric sections: temperature, circulation and shear from the surface to 200 km.'],season:['One planet,<br><em>many seasons.</em>','Isolate seasonal changes at a fixed location, altitude and time convention.'],acoustic:['When wind<br><em>meets sound.</em>','Directional diagnostics and sensitivity kernels: steps towards studying acoustic coupling.'],method:['Readable results.<br><em>A verifiable method.</em>','Sources, assumptions, conventions and limitations: each calculation should be reproducible.']};
async function api(path,override={}){
 const params=new URLSearchParams({...state,...override});
 busy++;$('status').textContent='MCD calculation · interpolating atmospheric fields…';
 try{const r=await fetch('/api/'+path+'?'+params);if(!r.ok){const j=await r.json();throw new Error(typeof j.detail==='string'?j.detail:JSON.stringify(j.detail));}return await r.json();}
 finally{busy--;if(!busy)$('status').textContent='Local engine · fields sampled with CALL_MCD · results cached';}
}
function fail(e){$('error').textContent=e.message;$('error').hidden=false;$('status').textContent='Calculation failed. Visible parameters may differ from the last successful results.';}
function guarded(fn){return async()=>{try{$('error').hidden=true;await fn();}catch(e){fail(e);}};}
function updateLabels(){
 $('lsLabel').textContent='Ls '+$('ls').value+'°';$('altLabel').textContent=$('altitude').value+' km';$('ltLabel').textContent=$('lt').value+' h';
 const a=+$('azimuth').value;$('azLabel').textContent=a+'°'+({0:' · north',90:' · east',180:' · south',270:' · west',360:' · north'}[a]||'');
}
function summary(){return `Ls ${state.ls}° · ${state.altitude} km · ${state.lt} h ${state.time_mode==='universal'?'at 0° E':'local'}`;}
async function refresh(overrides={}){
 const token=++revision;loaded={};$('apply').disabled=true;refreshing=true;
 const candidate={...state};
 $('error').hidden=true;
 for(const key of ['ls','lt','altitude','azimuth'])candidate[key]=+$(key).value;
 candidate.time_mode=$('time_mode').value;Object.assign(candidate,overrides);
 try{
  const [m,p]=await Promise.all([api('map',candidate),api('profile',candidate)]);
  if(token!==revision)return;state={...candidate,field:state.field};mapData=m;profileData=p;renderStats();drawMap();renderProfiles();
  $('provenance').textContent=JSON.stringify(m.provenance,null,2);
  refreshing=false;await ensureTab();
 }finally{$('apply').disabled=false;refreshing=false;}
}
function renderStats(){
 const s=mapData.stats;$('meanSpeed').innerHTML=fmt(s.mean_speed)+'<i>m/s</i>';$('maxSpeed').innerHTML=fmt(s.max_speed)+'<i>m/s</i>';$('meanTemp').innerHTML=fmt(s.mean_temperature)+'<i>K</i>';
 $('seasonName').textContent=['Northern spring','Northern summer','Northern autumn','Northern winter'][Math.floor((state.ls%360)/90)];
 $('stateSummary').textContent=summary();$('mapTag').textContent='MCD 6.1 / '+summary();
 $('timeExplanation').textContent=state.time_mode==='universal'?'The same instant around Mars: local solar time varies with longitude.':'The same local solar hour at every longitude: this map is not a global snapshot.';
 $('insightText').textContent=`At ${state.altitude} km, mean horizontal speed is ${fmt(s.mean_speed)} m/s. The maximum of ${fmt(s.max_speed)} m/s depends on the query grid. ${s.valid_fraction<1?'Some points are below terrain and are masked.':''}`;
}
function color(t,colors){t=Math.max(0,Math.min(1,t));const n=t*(colors.length-1),i=Math.min(colors.length-2,Math.floor(n)),f=n-i;const rgb=c=>[1,3,5].map(x=>parseInt(c.slice(x,x+2),16));const a=rgb(colors[i]),b=rgb(colors[i+1]);return a.map((v,j)=>Math.round(v+(b[j]-v)*f));}
function range(){let a=mapData.fields[state.field].flat().filter(Number.isFinite);let min=Math.min(...a),max=Math.max(...a);const signed=['u','v','w'].includes(state.field)||min<0;if(signed){max=Math.max(Math.abs(min),Math.abs(max));min=-max;}else if(state.field!=='temperature')min=0;return {min,max,colors:signed?diverging:palette};}
function valueAt(lon,lat){const i=((Math.round((lon+177.5)/5)%72)+72)%72,j=Math.max(0,Math.min(35,Math.round((lat+87.5)/5)));return {i,j,lon:mapData.longitude[i],lat:mapData.latitude[j]};}
let geom=null;
function project(lon,lat,g=geom){if(g.type==='flat')return [g.x+(lon+180)/360*g.w,g.y+(90-lat)/180*g.h,true];const rad=Math.PI/180,l=(lon-g.center)*rad,p=lat*rad;return [g.cx+g.r*Math.cos(p)*Math.sin(l),g.cy-g.r*Math.sin(p),Math.cos(p)*Math.cos(l)>0];}
function invert(x,y){const g=geom;if(!g)return null;if(g.type==='flat'){const lon=(x-g.x)/g.w*360-180,lat=90-(y-g.y)/g.h*180;return Math.abs(lon)<=180&&Math.abs(lat)<=90?[lon,lat]:null;}const X=(x-g.cx)/g.r,Y=(g.cy-y)/g.r;if(X*X+Y*Y>1)return null;const lat=Math.asin(Y),lon=g.center+Math.atan2(X,Math.sqrt(Math.max(0,1-X*X-Y*Y)))*180/Math.PI;return [((lon+540)%360)-180,lat*180/Math.PI];}
function drawMap(){
 if(!mapData)return;const canvas=$('map'),ctx=canvas.getContext('2d'),dpr=window.devicePixelRatio||1;
 const W=canvas.clientWidth,H=canvas.clientHeight;if(!W||!H)return;canvas.width=W*dpr;canvas.height=H*dpr;ctx.scale(dpr,dpr);ctx.fillStyle='#15262d';ctx.fillRect(0,0,W,H);
 geom=projection==='flat'?{type:'flat',x:43,y:40,w:W-67,h:H-88}:{type:'globe',cx:W/2,cy:H/2-2,r:H*.405,center:state.lon};
 const {min,max,colors}=range();$('legendMin').textContent=fmt(min,state.field==='w'?2:0);$('legendMax').textContent=fmt(max,state.field==='w'?2:0)+' '+units[state.field];$('colorbar').style.background='linear-gradient(90deg,'+colors.join(',')+')';$('mapTitle').textContent=labels[state.field];
 // Pixel colours are sampled from the nearest 5-degree MCD consultation cell, never smoothed into invented detail.
 const small=document.createElement('canvas');small.width=W;small.height=H;const sc=small.getContext('2d'),im=sc.createImageData(W,H);
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){const ll=invert(x,y);if(!ll)continue;const q=valueAt(...ll),v=mapData.fields[state.field][q.j][q.i];if(v==null)continue;const rgb=color((v-min)/(max-min||1),colors);let shade=1;const p=(y*W+x)*4;im.data[p]=rgb[0]*shade;im.data[p+1]=rgb[1]*shade;im.data[p+2]=rgb[2]*shade;im.data[p+3]=255;}
 sc.putImageData(im,0,0);ctx.drawImage(small,0,0);
 ctx.lineWidth=.6;ctx.strokeStyle='#e4ecdf28';
 function line(points){ctx.beginPath();let on=false;for(const [lon,lat]of points){const [x,y,v]=project(lon,lat);if(!v){on=false;continue;}if(on)ctx.lineTo(x,y);else ctx.moveTo(x,y);on=true;}ctx.stroke();}
 for(let l=-180;l<=180;l+=30)line(Array.from({length:91},(_,i)=>[l,-90+i*2]));
 for(let p=-60;p<=60;p+=30)line(Array.from({length:181},(_,i)=>[-180+i*2,p]));
 if(projection==='flat'){ctx.font='8px monospace';ctx.fillStyle='#a5b7b9';ctx.textAlign='center';for(let l=-180;l<=180;l+=60){const [x]=project(l,0);ctx.fillText(l+'°',x,H-33);}ctx.textAlign='right';for(let p=-60;p<=60;p+=30){const [,y]=project(0,p);ctx.fillText(p+'°',34,y+3);}}
 if($('vectors').checked){ctx.strokeStyle='#f5fae2a6';ctx.lineWidth=.8;for(let j=2;j<34;j+=3)for(let i=1;i<72;i+=3){const lat=mapData.latitude[j],lon=mapData.longitude[i],u=mapData.fields.u[j][i],v=mapData.fields.v[j][i];if(u==null||Math.hypot(u,v)<1)continue;const [x,y,visible]=project(lon,lat);if(!visible)continue;const epsilon=.05,sp=Math.hypot(u,v);const [xx,yy,vv]=project(lon+epsilon*u/sp/Math.cos(lat*Math.PI/180),lat+epsilon*v/sp);if(!vv)continue;const a=Math.atan2(yy-y,xx-x),len=8;ctx.beginPath();ctx.moveTo(x-Math.cos(a)*len/2,y-Math.sin(a)*len/2);const ex=x+Math.cos(a)*len/2,ey=y+Math.sin(a)*len/2;ctx.lineTo(ex,ey);ctx.moveTo(ex-3*Math.cos(a-.5),ey-3*Math.sin(a-.5));ctx.lineTo(ex,ey);ctx.lineTo(ex-3*Math.cos(a+.5),ey-3*Math.sin(a+.5));ctx.stroke();}}
 const [px,py,vis]=project(state.lon,state.lat);if(vis){ctx.beginPath();ctx.arc(px,py,6,0,2*Math.PI);ctx.strokeStyle='#fff5d6';ctx.lineWidth=1.5;ctx.stroke();ctx.beginPath();ctx.arc(px,py,2,0,2*Math.PI);ctx.fillStyle='#fff5d6';ctx.fill();ctx.fillStyle='#fff5d6';ctx.font='9px monospace';ctx.textAlign='left';ctx.fillText('PROBE',px+10,py+3);}
 $('mapConvention').textContent=projection==='flat'?'Equidistant projection · normalized arrows':'Orthographic projection · centred on the probe';
}
const config={responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d','sendChartToCloud'],toImageButtonOptions:{format:'png',scale:2}};
function layout(extra={}){return {paper_bgcolor:'#fffef9',plot_bgcolor:'#fffef9',font:{family:'Arial, sans-serif',color:'#657462',size:10},margin:{l:65,r:25,t:20,b:52},showlegend:true,legend:{orientation:'h',x:0,y:1.12,font:{size:10}},xaxis:{gridcolor:'#e5e8dc',zerolinecolor:'#adb6a4',title:{font:{size:10}}},yaxis:{gridcolor:'#e5e8dc',zerolinecolor:'#adb6a4',title:{text:'Altitude / areoid (km)',font:{size:10}}},hovermode:'closest',...extra};}
function lineTrace(x,y,name,color,extra={}){return {x,y,name,type:'scatter',mode:'lines',line:{color,width:2},...extra};}
function renderProfiles(){if(!profileData)return;const f=profileData.fields,z=profileData.altitude_km;
 $('probeTitle').textContent=Math.abs(state.lon-135.623)<.001&&Math.abs(state.lat-4.502)<.001?'InSight column':'Selected column';
 $('probeDetails').textContent=`${fmt(state.lon,2)}° E · ${fmt(state.lat,2)}° N · local time ${fmt(f.local_time[0],2)} h`;
 $('probeLon').value=state.lon;$('probeLat').value=state.lat;
 Plotly.react('miniProfile',[lineTrace(f.u,z,'u · east','#bd7049'),lineTrace(f.v,z,'v · north','#49796c')],layout({margin:{l:52,r:20,t:30,b:42},xaxis:{title:{text:'Wind (m/s)'},gridcolor:'#e7e9df'},yaxis:{title:{text:'Altitude (km)'},gridcolor:'#e7e9df'}}),config);
 const traces=[lineTrace(f.u.map((v,i)=>v-f.u_rms[i]),z,'u − RMS','#e9ccb8',{line:{width:0},showlegend:false}),lineTrace(f.u.map((v,i)=>v+f.u_rms[i]),z,'u ± RMS','#e9ccb8',{line:{width:0},fill:'tonextx',fillcolor:'#c1855430'}),lineTrace(f.u,z,'u · east','#b8683c'),lineTrace(f.v,z,'v · north','#528879'),lineTrace(f.temperature,z,'T (K)','#4d617e',{xaxis:'x2',yaxis:'y2'}),lineTrace(f.shear,z,'Shear','#906e8d',{xaxis:'x3',yaxis:'y3'})];
 Plotly.react('profileChart',traces,layout({xaxis:{domain:[0,.43],title:{text:'Wind (m/s)'},gridcolor:'#e7e9df'},xaxis2:{domain:[.52,.73],title:{text:'Temperature (K)'},gridcolor:'#e7e9df'},xaxis3:{domain:[.82,1],title:{text:'Shear (m/s/km)'},gridcolor:'#e7e9df'},yaxis2:{anchor:'x2',matches:'y',showticklabels:false,gridcolor:'#e7e9df'},yaxis3:{anchor:'x3',matches:'y',showticklabels:false,gridcolor:'#e7e9df'}}),config);
 Plotly.react('acousticChart',[lineTrace(f.sound_speed,z,'c at rest','#4e657f'),lineTrace(f.effective_speed,z,'c effective','#bd7049'),lineTrace(f.along_wind,z,'Projected wind','#5a8870')],layout({xaxis:{title:{text:'Speed (m/s)'},gridcolor:'#e7e9df'},shapes:[{type:'line',x0:0,x1:0,y0:0,y1:1,yref:'paper',line:{dash:'dot',color:'#b48565',width:1}}]}),config);
}
async function ensureTab(){
 if(!mapData||refreshing)return;const token=revision;
 if(currentTab==='legacy'&&!loaded.legacy){const a=await api('legacy');if(token!==revision)return;const traces=[];a.modes.forEach((m,i)=>{const c=palette[i%palette.length];traces.push(lineTrace(m.U.real.map(v=>v+i*2.5),m.altitude_km,'n = '+i,c,{showlegend:false}));traces.push(lineTrace(m.V.real.map(v=>v+i*2.5),m.altitude_km,'n = '+i,c,{showlegend:false,xaxis:'x2',yaxis:'y2'}));});const ticks=a.modes.map((m,i)=>i*2.5),names=a.modes.map(m=>'n'+m.n);Plotly.react('legacyChart',traces,layout({showlegend:false,xaxis:{domain:[0,.45],title:{text:'Radial component √ρ U'},tickvals:ticks,ticktext:names,gridcolor:'#e7e9df'},xaxis2:{domain:[.55,1],title:{text:'Horizontal component √ρ V'},tickvals:ticks,ticktext:names,gridcolor:'#e7e9df'},yaxis:{title:{text:'Archived-model altitude (km)'},gridcolor:'#e7e9df'},yaxis2:{anchor:'x2',matches:'y',showticklabels:false,gridcolor:'#e7e9df'}}),config);$('legacyTable').querySelector('tbody').innerHTML=a.modes.map(m=>`<tr><td>${m.n}</td><td>${m.max_sqrt_rho_U.toExponential(3)}</td><td>${m.max_sqrt_rho_V.toExponential(3)}</td><td>${fmt(m.normalization_integral_ratio,0)}</td><td>${fmt(m.atmospheric_inertia_fraction*100,2)} %</td><td>${fmt(m.lower_10km_fraction_of_atmosphere*100,3)} %</td></tr>`).join('');loaded.legacy=true;}
 if(currentTab==='structure'&&!loaded.structure){const s=await api('section');if(token!==revision)return;Plotly.react('sectionChart',[{type:'heatmap',x:s.latitude,y:s.altitude_km,z:s.fields.u,colorscale:diverging.map((c,i)=>[i/(diverging.length-1),c]),zmid:0,colorbar:{title:{text:'u (m/s)'},thickness:10},hovertemplate:'%{x}° N<br>%{y:.1f} km<br>u %{z:.1f} m/s<extra></extra>'}],layout({showlegend:false,xaxis:{title:{text:'North latitude (°)'}}}),config);$('sectionTitle').textContent='Jets at '+fmt(state.lon,2)+'° E';loaded.structure=true;}
 if(currentTab==='season'&&!loaded.season){const s=await api('seasonal');if(token!==revision)return;Plotly.react('seasonChart',[lineTrace(s.Ls,s.fields.u,'u · east','#b8683c'),lineTrace(s.Ls,s.fields.v,'v · north','#528879'),lineTrace(s.Ls,s.fields.speed,'Horizontal speed','#4d617e')],layout({xaxis:{title:{text:'Solar longitude Ls (°)'},dtick:45,range:[0,360],gridcolor:'#e7e9df'},yaxis:{title:{text:'Wind (m/s)'},gridcolor:'#e7e9df'}}),config);$('seasonLocation').textContent=`${fmt(state.lon,2)}° E · ${fmt(state.lat,2)}° N · ${state.altitude} km`;await compare();loaded.season=true;}
 if(currentTab==='acoustic'&&!loaded.acoustic){$('modesChart').hidden=true;$('modesTable').hidden=true;$('modesStatus').textContent='Run the calculation to evaluate wind-sensitivity kernels.';loaded.acoustic=true;}
 setTimeout(()=>document.querySelectorAll('.tab.active .plot').forEach(p=>{if(p.data)Plotly.Plots.resize(p);}),50);
}
async function compare(){const token=revision;const b=await api('map',{ls:+$('compareLs').value});if(token!==revision)return;const delta=b.fields.u.map((row,j)=>row.map((v,i)=>v==null||mapData.fields.u[j][i]==null?null:v-mapData.fields.u[j][i]));const max=Math.max(...delta.flat().filter(Number.isFinite).map(Math.abs));Plotly.react('differenceChart',[{type:'heatmap',x:b.longitude,y:b.latitude,z:delta,zmin:-max,zmax:max,colorscale:diverging.map((c,i)=>[i/(diverging.length-1),c]),colorbar:{title:{text:'Δu (m/s)'},thickness:10}}],layout({showlegend:false,xaxis:{title:{text:'East longitude (°)'}},yaxis:{title:{text:'North latitude (°)'}}}),config);}
async function setProbe(lon,lat){if(refreshing)return;if(!Number.isFinite(lon)||!Number.isFinite(lat)||Math.abs(lon)>180||Math.abs(lat)>89.5)throw new Error('Required coordinates: longitude between −180° and 180°, latitude between −89.5° and 89.5°.');const token=++revision;const p=await api('profile',{lon,lat});if(token!==revision)return;state.lon=lon;state.lat=lat;loaded={};profileData=p;renderProfiles();drawMap();await ensureTab();}
async function modes(){const degree=+$('degree').value;if(!Number.isInteger(degree)||degree<1||degree>500)throw new Error('Horizontal degree must be an integer from 1 to 500.');const token=revision;state.degree=degree;$('modesBtn').disabled=true;$('modesStatus').textContent='Computing modes and comparing two grids…';try{const m=await api('modes');if(token!==revision)return;$('modesChart').hidden=false;$('modesTable').hidden=false;const traces=m.weights.map((w,i)=>lineTrace(w,m.altitude_km,'j = '+i,palette[i]));Plotly.react('modesChart',traces,layout({xaxis:{title:{text:'Normalized nodal weight (sum = 1)'},gridcolor:'#e7e9df'}}),config);$('modesTable').querySelector('tbody').innerHTML=m.frequency_mhz.map((f,i)=>`<tr><td>${i}</td><td>${fmt(f,3)}</td><td>${fmt(m.period_s[i],1)}</td><td>${fmt(m.effective_wind[i],1)}</td><td>${fmt(m.delta_frequency_mhz[i],3)}</td><td class="${m.grid_difference_pct[i]>1?'warn':''}">${fmt(m.grid_difference_pct[i],2)} %</td><td class="${Math.abs(m.relative_shift[i])>.1?'warn':''}">${fmt(Math.abs(m.relative_shift[i])*100,1)} %</td></tr>`).join('');const strong=m.relative_shift.some(v=>Math.abs(v)>.1);$('modesStatus').textContent=strong?'The shift exceeds 10% for at least one mode: examine the perturbative approximation. These frequencies depend on the rigid upper boundary at 200 km.':'First-order shifts. Small amplitudes do not validate boundary conditions or omitted physics.';}finally{$('modesBtn').disabled=false;}}
$('map').addEventListener('mousemove',e=>{if(!mapData)return;const box=e.currentTarget.getBoundingClientRect(),ll=invert(e.clientX-box.left,e.clientY-box.top);if(!ll){$('tooltip').hidden=true;return;}const q=valueAt(...ll),f=mapData.fields;const tip=$('tooltip');tip.innerHTML=`<b>${fmt(q.lon,1)}° E · ${fmt(q.lat,1)}° N</b><br>${labels[state.field]} : ${fmt(f[state.field][q.j][q.i],2)} ${units[state.field]}<br>u ${fmt(f.u[q.j][q.i])} · v ${fmt(f.v[q.j][q.i])} m/s<br>T ${fmt(f.temperature[q.j][q.i])} K · LT ${fmt(f.local_time[q.j][q.i],2)} h`;tip.hidden=false;tip.style.left=Math.max(5,Math.min(e.clientX-box.left+14,box.width-250))+'px';tip.style.top=Math.max(5,Math.min(e.clientY-box.top+14,box.height-112))+'px';});
$('map').addEventListener('mouseleave',()=>$('tooltip').hidden=true);
$('map').addEventListener('click',e=>{const b=e.currentTarget.getBoundingClientRect(),ll=invert(e.clientX-b.left,e.clientY-b.top);if(ll){const q=valueAt(...ll);guarded(()=>setProbe(q.lon,q.lat))();}});
for(const id of ['ls','lt','altitude','azimuth'])$(id).addEventListener('input',()=>{updateLabels();$('status').textContent='Parameters changed · click Update fields to calculate.';});
$('time_mode').addEventListener('change',()=>$('status').textContent='Time convention changed · click Update fields.');
$('apply').onclick=guarded(()=>refresh());$('field').onchange=()=>{state.field=$('field').value;drawMap();};$('vectors').onchange=drawMap;
$('flatBtn').onclick=()=>{projection='flat';$('flatBtn').classList.add('selected');$('globeBtn').classList.remove('selected');drawMap();};$('globeBtn').onclick=()=>{projection='globe';$('globeBtn').classList.add('selected');$('flatBtn').classList.remove('selected');drawMap();};
$('setProbe').onclick=guarded(()=>setProbe(+$('probeLon').value,+$('probeLat').value));$('resetProbe').onclick=guarded(()=>setProbe(135.623,4.502));$('compareBtn').onclick=guarded(compare);$('modesBtn').onclick=guarded(modes);
async function navigateTo(name){
 if(!titles[name])return;
 currentTab=name;document.body.dataset.view=name;
 document.querySelectorAll('.nav').forEach(x=>x.classList.toggle('active',x.dataset.tab===name));
 document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x.id===name));
 if(['acoustic','legacy','method'].includes(name))document.querySelector('.advanced-nav').open=true;
 document.querySelector('.atlas-settings').open=name!=='guide';
 $('pageTitle').innerHTML=titles[name][0];$('pageSubtitle').textContent=titles[name][1];
 if(name==='atlas')drawMap();
 await ensureTab();
 if(name==='guide'&&$('studyChart').data)Plotly.Plots.resize('studyChart');
 document.querySelector('.intro').scrollIntoView({behavior:'smooth',block:'start'});
}
for(const button of document.querySelectorAll('.nav'))button.onclick=guarded(()=>navigateTo(button.dataset.tab));
for(const button of document.querySelectorAll('[data-open]'))button.onclick=guarded(()=>navigateTo(button.dataset.open));
$('goToJet').onclick=guarded(async()=>{
 if(!mapData)return;
 let best={speed:-Infinity};
 mapData.fields.speed.forEach((row,j)=>row.forEach((speed,i)=>{if(Number.isFinite(speed)&&speed>best.speed)best={speed,i,j};}));
 if(!Number.isFinite(best.speed))throw new Error('No valid atmospheric samples at this altitude.');
 await setProbe(mapData.longitude[best.i],mapData.latitude[best.j]);await navigateTo('structure');
});
$('exportToggle').onclick=()=>{$('exportMenu').hidden=!$('exportMenu').hidden;document.querySelectorAll('[data-format]').forEach(a=>a.href='/api/export?'+new URLSearchParams({...state,format:a.dataset.format}));};document.addEventListener('click',e=>{if(!e.target.closest('.header-right'))$('exportMenu').hidden=true;});
let resize;window.addEventListener('resize',()=>{clearTimeout(resize);resize=setTimeout(drawMap,120);});
(async()=>{try{await api('health');$('engine').textContent='MCD engine ready';await refresh();}catch(e){$('engine').textContent='Engine needs configuration';fail(e);}})();
