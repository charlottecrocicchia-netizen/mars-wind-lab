const $ = id => document.getElementById(id);
const fmt = (v, digits=2) => v == null ? '—' : Number(v).toFixed(digits);
const pct = v => `${fmt(100*v,1)}%`;
const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const table = (headers, rows, caption) => `<table><caption>${escape(caption)}</caption><thead><tr>${headers.map(h=>`<th scope="col">${escape(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map(c=>`<td>${escape(c)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
const names = {steady:'Steady',absent:'Always absent',shutdown:'Shutdown at 500 Myr',intermittent:'Intermittent',periodic:'Periodic reversals',poisson:'Poisson reversals'};
const label = h => `${names[h.kind]}${h.chron_myr ? ` · ${h.chron_myr} Myr chron` : ''}`;
const config = {responsive:true,displayModeBar:false};
const base = {paper_bgcolor:'#11161d',plot_bgcolor:'#11161d',font:{color:'#c5ced8',family:'system-ui',size:12},margin:{l:66,r:22,t:22,b:70},height:400,legend:{orientation:'h',y:1.15},colorway:['#6ed8cc','#88b8d2','#b6bc81','#af97c4']};
function plot(id, traces, layout={}) {
  const element=$(id), options={...base,...layout};
  options.width=element.clientWidth || Math.max(240,document.querySelector('main').clientWidth-56);
  element.style.height=`${options.height}px`;
  return Plotly.react(element,traces,options,config);
}
function plotLabel(h) {
  if(window.innerWidth>=650) return label(h);
  if(h.chron_myr) return `${h.kind==='periodic'?'Periodic':'Poisson'} · ${h.chron_myr} Myr`;
  return h.kind==='shutdown'?'Shutdown · 500 Myr':names[h.kind];
}
let recording, maps, laboratory, view;
function selectView(next, updateUrl=true) {
  view = ['recording','detection','maps','laboratory'].includes(next) ? next : 'recording';
  document.querySelectorAll('[data-panel]').forEach(p=>{p.hidden=p.dataset.panel!==view;});
  document.querySelectorAll('[data-view]').forEach(a=>{if(a.dataset.view===view)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
  if(updateUrl) history.replaceState(null,'',`/research/experiments?view=${view}`);
  if (recording) ({recording:renderRecording,detection:renderDetection,maps:renderMaps,laboratory:renderLab})[view]();
}
function selectedBatch() { return recording.batches.find(b=>b.thermal===$('recordThermal').value && b.band_c.join(',')===$('recordBand').value); }
function renderRecording() {
  const b=selectedBatch(), height=$('recordHeight').value, i=recording.heights_km.indexOf(Number(height));
  $('recordFractions').innerHTML=`<span><b>${pct(b.known_acquired_fraction)}</b> acquired in the supplied history</span><span><b>${pct(b.unknown_initial_fraction)}</b> initial record unresolved</span><span><b>${pct(b.hot_final_fraction)}</b> still unblocked</span>`;
  $('initialBound').textContent=`Unknown initial remanence could add or subtract up to ${fmt(b.initial_field_bound_nt[i])} nT at ${height} km, assuming its magnitude is bounded by 10 A/m. The plot shows only the known new contribution.`;
  const values=b.histories.map(h=>h.absolute_field_q05_q50_q95_nt[height]);
  plot('recordPlot',[{type:'bar',orientation:'h',y:b.histories.map(plotLabel),x:values.map(q=>q[1]),marker:{color:'#6ed8cc'},error_x:{type:'data',symmetric:false,array:values.map(q=>q[2]-q[1]),arrayminus:values.map(q=>q[1]-q[0]),color:'#c0e9e4'},hovertemplate:'%{y}<br>Median known |Bz|: %{x:.3f} nT<extra></extra>'}],{height:500,margin:{l:window.innerWidth<650?130:220,r:24,t:20,b:55},xaxis:{title:{text:`Known |Bz| at ${height} km (nT)`},gridcolor:'#253142'},yaxis:{autorange:'reversed',tickfont:{size:window.innerWidth<650?10:12}}});
  const steady=b.histories.find(h=>h.id==='steady'), intermittent=b.histories.find(h=>h.id==='intermittent');
  const same=Math.abs(steady.absolute_field_q05_q50_q95_nt[height][1]-intermittent.absolute_field_q05_q50_q95_nt[height][1])<1e-9;
  $('recordFinding').innerHTML=`<h3>${same?'Two different histories leave the same known record.':'Recording conditions change the contrast.'}</h3><p>${same?'For this band and thermal history, the steady and intermittent fields give identical known contributions: their differences occur outside the surviving acquisition window. This is a conditional degeneracy, not evidence that Mars followed either history.':'Changing the acquisition band changes how much cancellation, resetting and unknown prehistory matter. Compare both thermal histories before interpreting a weak signal as a shutdown.'}</p>`;
  plot('kernelPlot',[{x:b.period_myr,y:b.temporal_gain,type:'scatter',mode:'lines',line:{color:'#88b8d2'},hovertemplate:'Period %{x:.2f} Myr<br>Gain %{y:.4f}<extra></extra>'}],{xaxis:{type:'log',title:{text:'Sinusoidal period (Myr)'}},yaxis:{range:[0,1.05],title:{text:'Normalized known-kernel gain'}}});
  const check=recording.refinement.find(r=>r.thermal===b.thermal && r.band_c.join(',')===b.band_c.join(','));
  $('recordChecks').textContent=`Doubling the thermal spatial/time resolution changes the signed recording fraction by at most ${fmt(check.thermal_refinement_max_signed_fraction_difference,6)} in 16 tested phases at each of the 5, 20 and 100 Myr chron durations. A 1,024-point threshold approximation differs from exact interval integration by up to ${fmt(check.midpoint_quadrature_max_difference_from_exact,6)}. These are numerical checks, not geological uncertainty bounds.`;
}
function renderDetection() {
  const points=recording.injection_recovery;
  plot('detectionPlot',[{x:points.map(r=>r.snr),y:points.map(r=>r.analytic_power),mode:'lines',name:'Analytic known-template test'},{x:points.map(r=>r.snr),y:points.map(r=>r.recovered_fraction),mode:'markers',name:'Injected trials',error_y:{type:'data',array:points.map(r=>2*r.monte_carlo_standard_error),visible:true}}],{xaxis:{title:{text:'Template signal-to-noise ratio'}},yaxis:{title:{text:'Detection probability'},range:[0,1.04]}});
  const b=recording.batches.find(b=>b.thermal==='reheating' && b.band_c.join(',')==='250,550');
  $('detectionTable').innerHTML=table(['History','Median ideal detection probability','Median residual after fitting amplitude (σ norm)'],b.histories.map(h=>[label(h),pct(h.known_template_detection_power_q05_q50_q95[1]),fmt(h.distance_to_scaled_steady_sigma_q05_q50_q95[1],3)]),'Conditional detection and shape comparison · no real data fitted');
  const transfer=recording.harmonic_transfer;
  plot('altitudePlot',Object.entries(transfer.amplitude_by_height).map(([height,values])=>({x:transfer.degrees,y:values,mode:'lines+markers',name:`${height} km`})),{xaxis:{title:{text:'Spherical harmonic degree'}},yaxis:{type:'log',title:{text:'Amplitude / surface amplitude'}}});
}
function renderMaps() {
  const altitude=Number($('mapHeight').value),density=Number($('mapDensity').value),offset=Number($('mapOffset').value);
  const models=['location','structure','combined'];
  const subset=maps.results.filter(r=>r.altitude_km===altitude && r.density_kg_m3===density);
  const pick=(model,split)=>subset.find(r=>r.model===model && r.split===split && (split==='random'||r.wedge_offset_deg===offset));
  plot('mapPlot',['random','regional'].map(split=>({x:['Location','Structure','Combined'],y:models.map(m=>pick(m,split).skill_over_training_mean),type:'bar',name:split==='random'?'Dispersed test points':'Held-out regions'})),{barmode:'group',yaxis:{title:{text:'Skill over training-only mean'},zerolinecolor:'#a9b0b9'},xaxis:{title:{text:'Fixed feature set'}}});
  $('mapFinding').innerHTML=`<h3>Combined model: ${fmt(pick('combined','random').skill_over_training_mean,3)} → ${fmt(pick('combined','regional').skill_over_training_mean,3)} skill.</h3><p>The first value tests dispersed points; the second tests regional transfer with the selected wedge rotation. Try the other rotation: the result depends on which regions are omitted. This does not establish that crust thickness or geology causes the magnetic contrast.</p>`;
  $('shiftTable').innerHTML=table(['Shift of magnetic target','Regional skill','RMSE in log field'],maps.longitude_shift_controls.filter(r=>r.altitude_km===altitude).map(r=>[`${r.target_shift_deg}°`,fmt(r.skill_over_training_mean,3),fmt(r.weighted_rmse_log1p_nt,3)]),'Spatial alignment controls · fixed 2,900 kg/m³ and 0° wedge rotation');
  const oof=maps.oof_example, lats=[...new Set(oof.latitude)],lons=[...new Set(oof.longitude)];
  const grid=lats.map(()=>lons.map(()=>null));const iy=new Map(lats.map((v,i)=>[v,i])),ix=new Map(lons.map((v,i)=>[v,i]));
  oof.residual_log1p_nt.forEach((v,i)=>{grid[iy.get(oof.latitude[i])][ix.get(oof.longitude[i])]=v;});
  plot('residualPlot',[{type:'heatmap',x:lons,y:lats,z:grid,zmid:0,colorscale:'RdBu',reversescale:true,colorbar:{title:{text:'Δ log field'},thickness:12},hovertemplate:'%{y}° latitude<br>%{x}° E<br>Residual %{z:.2f}<extra></extra>'}],{xaxis:{title:{text:'Longitude (° E)'}},yaxis:{title:{text:'Latitude (°)'}},margin:{l:55,r:65,t:20,b:55}});
}
function populateSpecimens() {
  const dataset=$('labDataset').value;
  const eligible=laboratory.inventory.filter(r=>r.dataset===dataset && r.eligible_natural_measurements>0);
  $('labSpecimen').innerHTML=eligible.map(r=>`<option value="${escape(r.specimen)}">${escape(r.specimen)}</option>`).join('');
}
function renderLab() {
  const dataset=$('labDataset').value, specimen=$('labSpecimen').value;
  const source=laboratory.inventory.find(r=>r.dataset===dataset && r.specimen===specimen);
  $('labContext').textContent=`${specimen} · ${source.parent_sample} · ${source.eligible_natural_measurements} eligible natural-remanence measurements. ${dataset==='NWA_control'?'This archived suite is reported as contaminated by terrestrial hand magnets.':'Age and geological origin cannot be assigned from these automatic candidate fits.'}`;
  const series=laboratory.treatment_series.find(r=>r.dataset===dataset && r.specimen===specimen);
  const norm=Math.max(...series.mean_vectors_a_m2.map(v=>Math.hypot(...v)));
  plot('labPlot',[{x:series.mean_vectors_a_m2.map(v=>v[0]/norm),y:series.mean_vectors_a_m2.map(v=>v[1]/norm),text:series.levels,mode:'lines+markers',name:'X–Y projection',hovertemplate:'X %{x:.3f}, Y %{y:.3f}<br>Treatment %{text}<extra></extra>'},{x:series.mean_vectors_a_m2.map(v=>v[0]/norm),y:series.mean_vectors_a_m2.map(v=>v[2]/norm),text:series.levels,mode:'lines+markers',name:'X–Z projection',hovertemplate:'X %{x:.3f}, Z %{y:.3f}<br>Treatment %{text}<extra></extra>'}],{xaxis:{title:{text:'Normalized X moment'},zerolinecolor:'#666'},yaxis:{title:{text:'Normalized Y or Z moment'},scaleanchor:'x',scaleratio:1,zerolinecolor:'#666'}});
  const rows=laboratory.candidate_fits.filter(r=>r.dataset===dataset && r.specimen===specimen);
  $('labTable').innerHTML=table(['Candidate window','Distinct treatments','MAD','Forced-origin change','Leave-one-out max','Last-repeat change'],rows.map(r=>[`${r.window_low}–${r.window_high} ${r.unit}`,r.unique_treatments,fmt(r.mad_deg),fmt(r.anchored_axis_difference_deg),fmt(r.leave_one_treatment_out_max_axis_change_deg),fmt(r.repeat_aggregation_axis_difference_deg)]),'Sensitivity angles in degrees · — means insufficient or degenerate data');
  const control=laboratory.candidate_fits.filter(r=>r.dataset==='NWA_control' && r.mad_deg!=null), regular=control.filter(r=>r.mad_deg<5).length;
  $('labFinding').innerHTML=`<h3>${regular} of ${control.length} control windows have MAD below 5°.</h3><p>These windows belong to the known-contaminated suite. They demonstrate that a regular line alone is not a test of ancient origin. Windows overlap and specimens share parent stones; these counts are descriptive, not independent statistical trials.</p>`;
  $('chronologyTable').innerHTML=table(['Contextual event','Range (Ma before present)','Age association'],laboratory.alh_chronology_context.map(r=>[r.event,`${r.younger_ma}–${r.older_ma}`,r.basis]),'Published ALH 84001 context · not ages assigned to our fits');
}
try {
  [recording,maps,laboratory]=await Promise.all(['recording','maps','laboratory'].map(async name=>{const response=await fetch(`/research/files/experiments/${name}.json`);if(!response.ok)throw new Error(`Cannot load ${name}`);return response.json();}));
  populateSpecimens();selectView(new URLSearchParams(location.search).get('view'),false);
  $('experimentStatus').textContent='Saved calculations loaded · original code, explicit assumptions, no history selected.';
  document.querySelectorAll('[data-view]').forEach(a=>a.addEventListener('click',event=>{event.preventDefault();selectView(a.dataset.view);}));
  ['recordThermal','recordBand','recordHeight'].forEach(id=>$(id).addEventListener('change',renderRecording));
  ['mapHeight','mapDensity','mapOffset'].forEach(id=>$(id).addEventListener('change',renderMaps));
  $('labDataset').addEventListener('change',()=>{populateSpecimens();renderLab();});$('labSpecimen').addEventListener('change',renderLab);
  // Plots initially inside collapsed drawers need a resize when made visible.
  document.querySelectorAll('details').forEach(d=>d.addEventListener('toggle',()=>{if(d.open)d.querySelectorAll('.js-plotly-plot').forEach(p=>Plotly.relayout(p,{width:p.clientWidth}));}));
  window.addEventListener('resize',()=>{requestAnimationFrame(()=>selectView(view,false));});
} catch(error) { $('experimentStatus').textContent=`Results could not be loaded. Open the methods note or downloadable files below. ${error.message}`; }
