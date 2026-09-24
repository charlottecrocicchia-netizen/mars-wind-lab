'use strict';
let studyQuestion='direction',studyResult=null,studySnapshot=null,studyRevision=0,studyDirty=false;
const compass={0:'north',90:'east',180:'south',270:'west'};
const signed=(v,d=1)=>(v>0?'+':'')+fmt(v,d);
function studyParameters(){const [z_min,z_max]=$('studyLayer').value.split(',').map(Number);return {lon:+$('studyLon').value,lat:+$('studyLat').value,ls:+$('studySeason').value,compare_ls:+$('studySeasonB').value,lt:+$('studyHour').value,azimuth:+$('studyDirection').value,z_min,z_max,period_s:+$('studyPeriod').value};}
function studyChanged(){
 studyDirty=!studySnapshot||JSON.stringify(studyParameters())!==JSON.stringify(studySnapshot);
 $('studyPending').hidden=!studyDirty;$('studyExport').disabled=studyDirty||!studyResult;
 $('studyPeriodValue').textContent=$('studyPeriod').value+' s';
}
function studyKpis(items){$('studyKpis').replaceChildren(...items.map(([value,label])=>{const el=document.createElement('div'),strong=document.createElement('strong'),small=document.createElement('span');strong.textContent=value;small.textContent=label;el.append(strong,small);return el;}));}
function renderStudy(){
 if(!studyResult)return;
 const r=studyResult,c=r.context,p=r.impact_peak,s=r.season_peak,q=r.scale_peak,z=r.altitude_km,f=r.fields;
 const direction=compass[c.azimuth_deg],opposite=compass[(c.azimuth_deg+180)%360];
 const chartLayout=layout({font:{family:'Arial, sans-serif',color:'#52655c',size:12},margin:{l:58,r:18,t:65,b:55},legend:{orientation:'h',x:0,y:1.19,font:{size:11}},xaxis:{title:{text:'Effective sound speed (m/s)'},gridcolor:'#e5e8dc'},yaxis:{title:{text:'Altitude / areoid (km)'},gridcolor:'#e5e8dc',range:[c.altitude_min_km,c.altitude_max_km]}});
 const trace=(x,name,color,extra={})=>lineTrace(x,z,name,color,{hovertemplate:'%{y:.1f} km<br>%{x:.2f}<extra>%{fullData.name}</extra>',connectgaps:false,...extra});
 let traces;
 $('studyStamp').textContent=`Ls ${c.Ls}° · ${c.local_solar_hour} h local · ${c.altitude_min_km}–${c.altitude_max_km} km`;
 $('studyPlace').textContent=`Displayed result: ${fmt(c.latitude,2)}° N, ${fmt(c.longitude,2)}° E · ${c.local_solar_hour} h local`;
 $('studyReverse').hidden=studyQuestion!=='direction';
 if(studyQuestion==='direction'){
  const verb=p.projected_wind>=0?'increases':'reduces';
  $('studyHeadline').textContent=Math.abs(p.projected_wind)<1e-8?'Projected wind is zero throughout this column.':p.effective_speed<=0?`At ${fmt(p.altitude_km,0)} km, the opposing wind exceeds the sound speed at rest.`:`At ${fmt(p.altitude_km,0)} km, wind ${verb} the ${direction}ward speed by ${fmt(Math.abs(p.wind_effect_pct),0)}%.`;
  $('studyMeaning').textContent=`This is the largest relative effect in the selected layer. Here, the diagnostic changes from ${fmt(p.sound_speed,0)} m/s at rest to ${fmt(p.effective_speed,0)} m/s ${direction}ward, and ${fmt(p.opposite_effective_speed,0)} m/s in the opposite direction. Temperature and composition are held fixed.`;
  studyKpis([[signed(p.wind_effect_pct)+' %','largest absolute relative effect'],[signed(p.projected_wind)+' m/s','projected wind at this altitude'],[fmt(p.altitude_km,0)+' km','altitude identified on the grid']]);
  $('studyChartTitle').textContent='A direction and its opposite';
  traces=[trace(f.sound_speed,'At rest','#8b958d',{line:{color:'#8b958d',width:2,dash:'dot'}}),trace(f.effective_speed,direction+'ward','#28735a'),trace(f.opposite_effective_speed,opposite+'ward','#bd7049')];
  chartLayout.shapes=[{type:'line',xref:'paper',x0:0,x1:1,y0:p.altitude_km,y1:p.altitude_km,line:{color:'#7d8e8370',dash:'dot',width:1}}];
  $('studyReading').textContent='At a fixed altitude, a curve further right has a higher effective speed. Its separation from the grey curve isolates wind advection. The horizontal line marks the largest sampled relative effect.';
  $('studyActionTitle').textContent='Identify where neglecting wind changes the answer.';
  $('studyAction').textContent=`Start with the layer around ${fmt(p.altitude_km,0)} km, then reverse the direction. This test identifies where advection matters for propagation. A profile alone establishes neither an acoustic path nor the sensitivity of a global mode.`;
  $('studyEquation').textContent='c₀ = √(γRT) · W∥ = u sin α + v cos α · c_eff = c₀ + W∥ · opposite direction: c₀ − W∥';
 }else if(studyQuestion==='season'){
  const dw=s.season_wind_delta,dc=s.season_thermodynamic_delta,dt=s.season_total_delta;
  const cancel=dw*dc<0,zero=Math.abs(dw)+Math.abs(dc)<1e-8;
  $('studyHeadline').textContent=zero?'The two atmospheric states are identical.':cancel?'Wind and thermodynamics partly offset each other.':`At ${fmt(s.altitude_km,0)} km, ${Math.abs(dw)>Math.abs(dc)?'wind':'thermodynamics'} dominates the change.`;
  $('studyMeaning').textContent=`Between Ls ${c.Ls}° (A) and Ls ${c.comparison_Ls}° (B), the largest absolute change is ${signed(dt)} m/s at ${fmt(s.altitude_km,0)} km ${direction}ward. Location, geometric altitudes and local time are fixed. Thermodynamics includes temperature, composition and heat capacities.`;
  studyKpis([[signed(dt)+' m/s','total change B − A'],[signed(dw)+' m/s','wind contribution'],[signed(dc)+' m/s','thermodynamic contribution']]);
  $('studyChartTitle').textContent=`Ls ${c.Ls}° to Ls ${c.comparison_Ls}° · ${direction}ward`;
  traces=[trace(f.season_total_delta,'Total change','#283f35',{line:{color:'#283f35',width:3}}),trace(f.season_wind_delta,'Wind','#bd7049'),trace(f.season_thermodynamic_delta,'Thermodynamics','#608bab')];
  chartLayout.xaxis.title.text='Change B − A (m/s)';
  chartLayout.shapes=[{type:'line',x0:0,x1:0,y0:0,y1:1,yref:'paper',line:{color:'#8b958d',dash:'dot',width:1}}];
  $('studyReading').textContent='At each altitude, the total is the sum of the two contributions. Contributions of opposite sign cancel: a small total can conceal two substantial changes.';
  $('studyActionTitle').textContent='Identify which contribution to investigate.';
  $('studyAction').textContent='Use this decomposition to choose which fields to examine before a seasonal propagation study. It separates terms in effective sound speed; it does not identify the dynamical causes of circulation changes or provide observational validation.';
  $('studyEquation').textContent='Δc_eff = (c₀,B − c₀,A) + (W∥,B − W∥,A) · Δ = season B − season A, at the same local solar time';
 }else{
  $('studyHeadline').textContent=q?`At ${fmt(q.altitude_km,0)} km, the wavelength is ${fmt(q.wavelength_density_scale_ratio,2)} times the density scale.`:'The density gradient cannot be evaluated.';
  $('studyMeaning').textContent=q?`For a reference period of ${c.reference_period_s} s, this is the largest ratio in the layer. ${q.wavelength_density_scale_ratio>=1?'The wavelength is therefore not small relative to this scale throughout the layer: the locally short-wave assumption is not satisfied everywhere.':'This ratio is below 1, but this criterion alone does not justify a ray description.'} Velocity gradients, winds, turning points and losses also need examination.`:'This diagnostic requires at least three consecutive valid altitude samples.';
  studyKpis([[q?fmt(q.wavelength_density_scale_ratio,2):'—','maximum λ₀ / Hρ'],[q?fmt(q.reference_wavelength_km,1)+' km':'—','wavelength at the selected point'],[c.reference_period_s+' s','period in the resting medium']]);
  $('studyChartTitle').textContent='Wavelength versus stratification';
  traces=[trace(f.wavelength_density_scale_ratio.map(v=>v>0?v:null),'λ₀ / Hρ','#28735a')];
  chartLayout.showlegend=false;chartLayout.margin.t=30;
  chartLayout.xaxis={type:'log',title:{text:'λ₀ / Hρ · logarithmic scale'},gridcolor:'#e5e8dc'};
  chartLayout.shapes=[{type:'line',x0:1,x1:1,y0:0,y1:1,yref:'paper',line:{color:'#bd7049',dash:'dot',width:2}}];
  chartLayout.annotations=[{x:0,xref:'x',y:1,yref:'paper',text:'λ₀ = Hρ',showarrow:false,xanchor:'left',yanchor:'bottom',font:{size:11,color:'#a46c45'}}];
  $('studyReading').textContent='The dotted line marks equal scales. To its right, wavelength exceeds the local density scale. Being to the left is not sufficient: a short-wave approximation requires a ratio much smaller than 1. Zero ratios cannot be displayed on this logarithmic axis.';
  $('studyActionTitle').textContent='Test the assumptions before choosing a model.';
  $('studyAction').textContent='Change from 100 s to 10 s: in the same atmosphere, the ratio decreases by exactly a factor of ten. This helps identify periods and layers that require a full-wave calculation. λ₀ = c₀T is a reference wavelength at rest, not the vertical wavelength of a computed mode.';
  $('studyEquation').textContent='λ₀ = c₀ T_ref · Hρ = |d ln ρ / dz|⁻¹ · indicator: λ₀ / Hρ · T_ref is defined in the resting medium';
 }
 if(r.nonpositive_effective_samples&&studyQuestion==='direction')$('studyMeaning').textContent+=' Some effective speeds are zero or negative: this diagnostic cannot then be interpreted as a travel-time prediction.';
 $('studyLimits').replaceChildren(...r.limits.map(text=>{const p=document.createElement('p');p.textContent=text;return p;}));
 Plotly.react('studyChart',traces,chartLayout,config);
 $('studyExport').disabled=studyDirty;
}
async function runStudy(){
 if(!$('studyForm').reportValidity())return;
 const params=studyParameters(),token=++studyRevision;
 $('runStudy').disabled=true;$('runStudy').textContent='Calculating…';$('studyError').hidden=true;
 document.querySelector('.study-results').classList.add('is-loading');
 try{
  const response=await fetch('/api/experiment?'+new URLSearchParams(params));
  const result=await response.json();
  if(!response.ok)throw new Error(typeof result.detail==='string'?result.detail:'Invalid parameters. Check the coordinates and altitude layer.');
  if(token!==studyRevision)return;
  studyResult=result;studySnapshot=params;studyChanged();renderStudy();
 }catch(e){$('studyError').textContent='Calculation failed: '+e.message;$('studyError').hidden=false;if(!studyResult)$('studyHeadline').textContent='The engine needs a valid configuration.';}
 finally{if(token===studyRevision){$('runStudy').disabled=false;$('runStudy').innerHTML='Run experiment <span>→</span>';document.querySelector('.study-results').classList.remove('is-loading');}}
}
for(const button of document.querySelectorAll('[data-question]'))button.onclick=()=>{
 studyQuestion=button.dataset.question;
 document.querySelectorAll('[data-question]').forEach(b=>{const on=b.dataset.question===studyQuestion;b.classList.toggle('selected',on);b.setAttribute('aria-pressed',on);});
 $('studySeasonBGroup').hidden=studyQuestion!=='season';$('studyPeriodGroup').hidden=studyQuestion!=='scale';$('studyDirectionGroup').hidden=studyQuestion==='scale';
 renderStudy();
};
$('studyForm').onsubmit=e=>{e.preventDefault();runStudy();};
for(const input of $('studyForm').querySelectorAll('input,select'))input.addEventListener('input',studyChanged);
$('studyResetPlace').onclick=()=>{$('studyLon').value=135.623;$('studyLat').value=4.502;$('studyHour').value=12;studyChanged();};
$('studyReverse').onclick=()=>{$('studyDirection').value=(+$('studyDirection').value+180)%360;studyChanged();runStudy();};
$('studyExport').onclick=()=>{if(!studySnapshot||studyDirty)return;const a=document.createElement('a');a.href='/api/study-note?'+new URLSearchParams({...studySnapshot,question:studyQuestion});a.download='marswind-study.md';a.click();};
$('studyInspect').onclick=guarded(async()=>{
 if(!studySnapshot)return;const p=studySnapshot;
 // Transfer the displayed result, never the uncomputed form values.
 for(const key of ['ls','lt','azimuth'])$(key).value=p[key];$('time_mode').value='local';updateLabels();
 await refresh({lon:p.lon,lat:p.lat,ls:p.ls,lt:p.lt,azimuth:p.azimuth,time_mode:'local'});await navigateTo('structure');
});
runStudy();
