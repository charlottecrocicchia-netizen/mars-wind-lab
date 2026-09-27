/* Render saved, independently computed cases. No model is fitted in the browser. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const value = id => Number($(id).value);
  const views = ['crust', 'feedback', 'boundary', 'paleomagnetism'];
  const colors = {teal:'#79dace', blue:'#94bdf0', purple:'#c1a6eb', white:'#e1eaf2', muted:'#72889b'};
  let data;
  const format = (n,d=2) => Number(n).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
  const signed = (n,d=2) => `${n >= 0 ? '+' : '−'}${format(Math.abs(n),d)}`;
  const config = {responsive:true,displayModeBar:false,scrollZoom:false};
  function plot(id, traces, xTitle, yTitle, extra={}) {
    return Plotly.react(id,traces,{
      paper_bgcolor:'#101b28',plot_bgcolor:'#101b28',font:{family:'system-ui, sans-serif',color:'#becfdf',size:11},
      margin:{l:64,r:22,t:35,b:85},
      xaxis:{title:{text:xTitle,standoff:12},gridcolor:'#233647',zerolinecolor:'#486176',fixedrange:true},
      yaxis:{title:{text:yTitle,standoff:10},gridcolor:'#233647',zerolinecolor:'#486176',fixedrange:true},
      legend:{orientation:'h',x:0,y:-.28,font:{size:10}},hovermode:'closest',...extra
    },config);
  }
  function crust() {
    const r=data.crust.maps.find(r=>r.south_density_kg_m3===value('crustDensity')&&r.mantle_density_kg_m3===value('mantleDensity'));
    plot('crustPlot',[{type:'bar',x:['Thickness','Density','Total support'],y:[r.thickness_support_km,r.density_support_km,r.total_support_contrast_km],marker:{color:[colors.teal,colors.blue,colors.purple]},hovertemplate:'%{x}: %{y:.3f} km<extra></extra>'}],
      'Contribution to southern minus northern support','Support contrast (km)',{showlegend:false,shapes:[{type:'line',xref:'paper',x0:0,x1:1,y0:r.observed_relief_contrast_km,y1:r.observed_relief_contrast_km,line:{color:colors.white,dash:'dash',width:1}}],annotations:[{xref:'paper',x:1,y:r.observed_relief_contrast_km,xanchor:'right',yshift:11,text:`Observed MOLA contrast ${format(r.observed_relief_contrast_km)} km`,showarrow:false,font:{size:10,color:colors.white}}]});
    $('crustSummary').textContent=`For this published map, south − north thickness is ${signed(r.south_thickness_km-r.north_thickness_km)} km. The density term provides ${format(r.density_support_km)} km of support; the thickness term provides ${signed(r.thickness_support_km)} km. Together: ${format(r.total_support_contrast_km)} km.`;
    layer();
  }
  function layer() {
    const r=data.crust.layers.find(r=>r.basal_thickness_km===value('basalThickness')&&r.upper_grain_density_kg_m3===value('upperDensity')&&r.basal_density_kg_m3===value('basalDensity')&&r.upper_porosity===value('porosity'));
    $('layerSummary').textContent=`Bulk density: ${format(r.bulk_density_kg_m3,0)} kg/m³. Support above the common datum: ${format(r.support_km_at_mantle3500)} km. ${r.basal_thickness_km===0?'No basal material in this case.':r.basal_density_exceeds_mantle3500?'The basal layer is denser than this assumed mantle; detachment is not calculated.':'The basal layer is not denser than this assumed mantle.'}`;
  }
  function feedback() {
    const s=data.feedback.sets.find(s=>s.lid_km===value('lidThickness'));
    const h=s.histories.find(h=>h.spectrum===$('seedSpectrum').value&&h.degree_one_efolds===value('efolds'));
    plot('growthPlot',[{type:'scatter',mode:'lines',x:s.degree,y:s.relative_growth,line:{color:colors.teal,width:2.5},hovertemplate:'Degree %{x}<br>Relative rate %{y:.6f}<extra></extra>'}], 'Spherical harmonic degree','Rate / degree-one rate',{showlegend:false});
    plot('powerPlot',[{type:'bar',x:s.degree.slice(0,h.shares.length),y:h.shares.map(p=>100*p),marker:{color:h.shares.map((_,i)=>i===0?colors.teal:colors.blue)},hovertemplate:'Degree %{x}: %{y:.3f}% of power<extra></extra>'}], 'Spherical harmonic degree','Share of total power (%)',{showlegend:false});
    $('feedbackSummary').textContent=`Degree two grows at ${format(s.relative_growth[1]*100,3)}% of the degree-one rate. After ${h.degree_one_efolds} degree-one e-folds, degree one holds ${format(h.degree_one_share*100)}% of the selected modal power. A tenfold amplitude lead over degree two would take about ${format(s.degree1_vs_degree2_efolds_for_tenfold_amplitude_advantage,0)} e-folds from equal amplitudes—far beyond a credible linear extrapolation.`;
  }
  function boundary() {
    const p=data.boundary.profiles.find(p=>p.longitude_deg_e===value('longitude'));
    const amp=value('loadPeak');
    const r=p.scenarios.find(r=>r.peak_load_km===amp&&(amp===0||(r.elastic_km===value('elasticThickness')&&r.offset_km===value('loadOffset')&&r.width_km===value('loadWidth'))));
    for(const id of ['elasticThickness','loadOffset','loadWidth']) $(id).disabled=amp===0;
    const smoothing=$('smoothing').value, old=p.observed_proxies[smoothing], edge=r.edges[smoothing];
    const traces=[
      {type:'scatter',x:p.x_km,y:p.strip_q25_km,mode:'lines',line:{width:0},showlegend:false,hoverinfo:'skip'},
      {type:'scatter',x:p.x_km,y:p.strip_q75_km,mode:'lines',line:{width:0},fill:'tonexty',fillcolor:'#94bdf025',name:'Observed strip IQR',hoverinfo:'skip'},
      {type:'scatter',x:p.x_km,y:p.observed_km,mode:'lines',line:{color:colors.white,width:2},name:'Observed median',hovertemplate:'%{x:.1f} km<br>%{y:.3f} km elevation<extra>Observed</extra>'},
      {type:'scatter',x:p.x_km,y:r.restored_km,mode:'lines',line:{color:colors.teal,width:2,dash:'dot'},name:'Conditional earlier relief',hovertemplate:'%{x:.1f} km<br>%{y:.3f} km elevation<extra>Assumed history</extra>'},
      {type:'scatter',x:[old.x_km],y:[p.observed_km[old.index]],mode:'markers',marker:{color:colors.white,size:11,symbol:'circle-open',line:{width:2}},name:'Observed proxy',hovertemplate:'Observed proxy: %{x:.1f} km<extra></extra>'},
      {type:'scatter',x:[edge.x_km],y:[r.restored_km[edge.index]],mode:'markers',marker:{color:colors.teal,size:11,symbol:'diamond'},name:'Restored proxy',hovertemplate:'Restored proxy: %{x:.1f} km<extra></extra>'}
    ];
    plot('boundaryPlot',traces,'Distance north of 35°N (km)','Areoid-relative elevation (km)',{margin:{l:64,r:22,t:25,b:105},xaxis:{title:{text:'Distance north of 35°N (km)',standoff:10},range:[-800,800],gridcolor:'#233647',fixedrange:true},shapes:[{type:'rect',xref:'x',yref:'paper',x0:-10*3396*Math.PI/180,x1:10*3396*Math.PI/180,y0:0,y1:1,fillcolor:'#79dace07',line:{color:'#6d9497',width:1,dash:'dot'},layer:'below'}]});
    const shift=edge.x_km-old.x_km;
    $('boundarySummary').textContent=`${p.longitude_deg_e}°E · σ = ${smoothing} km: observed proxy ${signed(old.x_km,1)} km; conditional proxy ${signed(edge.x_km,1)} km north of 35°N. Difference: ${signed(shift,1)} km. ${Math.abs(shift)>100?'This large jump switches features; it is not measured tectonic motion.':Math.abs(shift)<.01?'No change at this sampling.':'Treat this as a grid-sampled sensitivity, not measured tectonic motion.'}`;
    $('boundaryCaution').textContent=`${edge.at_search_edge||old.at_search_edge?'SEARCH-EDGE FLAG: at least one proxy meets the search limit. ':''}${p.longitude_deg_e===56?'AMBIGUOUS PROFILE: smoothing alone can switch the picked feature by about 830 km. ':''}Dotted box: fixed 25–45°N search window. Shading: observed spatial interquartile spread, not uncertainty. The load center stays referenced to the observed 50 km-smoothed proxy when smoothing changes. No load age or history is inferred.`;
  }
  function paleomagnetism() {
    const r=data.paleomagnetism.cases.find(r=>r.efficiency_ratio===value('recordingEfficiency'));
    const reference=data.paleomagnetism.cases.find(r=>r.efficiency_ratio===1);
    plot('araiPlot',[{type:'scatter',x:reference.lab_ptrm_normalized,y:reference.nrm_remaining_normalized,mode:'lines',line:{color:colors.muted,width:2,dash:'dash'},name:'Equal-efficiency reference'},
      {type:'scatter',x:r.lab_ptrm_normalized,y:r.nrm_remaining_normalized,mode:'lines+markers',line:{color:colors.teal,width:2.5},marker:{size:7},name:`Selected ratio ${r.efficiency_ratio}`,hovertemplate:'pTRM gained %{x:.2f}<br>NRM remaining %{y:.2f}<extra>Normalized to initial NRM</extra>'}],
      'Laboratory pTRM gained / initial NRM','Natural NRM remaining / initial NRM',{xaxis:{title:{text:'Lab pTRM gained / initial NRM',standoff:10},range:[-.1,4.2],gridcolor:'#233647',fixedrange:true}});
    $('paleoSummary').textContent=`True input field: ${format(r.true_field_ut,1)} µT. Apparent field from the slope: ${format(r.apparent_field_ut,1)} µT. ${r.efficiency_ratio===1?'They agree because the prescribed efficiencies match.':'The line is perfectly straight, but the conversion is biased.'} Adding more exact points would not establish the unknown recording efficiency.`;
  }
  const renderers={crust,feedback,boundary,paleomagnetism};
  function show(view) {
    if(!views.includes(view)) view='crust';
    for(const name of views) $(`view-${name}`).hidden=name!==view;
    for(const link of document.querySelectorAll('[data-view]')) {
      if(link.dataset.view===view) link.setAttribute('aria-current','page'); else link.removeAttribute('aria-current');
    }
    if(data) renderers[view]();
  }
  function queryView() {return new URLSearchParams(location.search).get('view')||'crust';}
  document.querySelectorAll('[data-view]').forEach(link=>link.addEventListener('click',event=>{
    if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey) return;
    event.preventDefault();history.pushState({},'',link.getAttribute('href'));show(link.dataset.view);
  }));
  window.addEventListener('popstate',()=>show(queryView()));
  for(const [ids,fn] of [
    [['crustDensity','mantleDensity'],crust],
    [['basalThickness','upperDensity','basalDensity','porosity'],layer],
    [['lidThickness','seedSpectrum','efolds'],feedback],
    [['longitude','smoothing','loadPeak','elasticThickness','loadOffset','loadWidth'],boundary],
    [['recordingEfficiency'],paleomagnetism]
  ]) ids.forEach(id=>$(id).addEventListener('change',()=>{if(data) fn();}));
  document.querySelectorAll('.physics-view select').forEach(el=>el.disabled=true);
  show(queryView());
  Promise.all(views.map(async view=>{
    const response=await fetch(`/research/files/physics/${view}.json`);
    if(!response.ok) throw new Error(`Cannot load ${view} (${response.status})`);
    return [view,await response.json()];
  })).then(entries=>{
    if(typeof Plotly==='undefined') throw new Error('Chart library unavailable');
    data=Object.fromEntries(entries);
    document.querySelectorAll('.physics-view select').forEach(el=>el.disabled=false);
    $('physicsStatus').textContent='Saved calculations · change a control to explore an existing case · no archive download';
    show(queryView());
  }).catch(error=>{
    $('physicsStatus').textContent=`Interactive view unavailable: ${error.message}. The methods, static figures and downloads below remain available.`;
    console.error(error);
  });
})();
