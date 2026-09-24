/* Saved scientific products only. No model inference is triggered by this UI. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt = n => n == null ? 'Unavailable' : Number(n).toFixed(2);
  const pct = n => `${Math.round(n*100)}%`;
  const config = {responsive:true,displaylogo:false,scrollZoom:false,
    modeBarButtonsToRemove:['sendDataToCloud','sendChartToCloud','lasso2d','select2d']};
  const base = {paper_bgcolor:'#1b1a19',plot_bgcolor:'#1b1a19',font:{family:'Inter, Arial, sans-serif',color:'#cfc3b8',size:12},
    margin:{l:62,r:30,t:25,b:58},hovermode:'closest',legend:{orientation:'h',y:1.17,x:0,font:{size:11}}};
  const fieldColors = [[0,'#100e22'],[.2,'#452052'],[.4,'#853956'],[.6,'#c36550'],[.8,'#e9a16a'],[1,'#fae4b7']];
  const topoColors = [[0,'#454b61'],[.25,'#929093'],[.45,'#c1ab96'],[.65,'#a46648'],[.85,'#d39d71'],[1,'#f1dcc0']];
  const minerals = {RED:['Fe/Mg clays','#efb38c'],GREEN:['Hydrated sulfate / zeolite class','#d8cba5'],
    BLUE:['Monohydrated sulfates','#b3a0d0'],ORANGE:['Carbonate / serpentine class','#e9b557'],CYAN:['Al clay / silica class','#8db7cb']};
  let data, current, renderVersion=0;

  function circle(site, factor) {
    const p = site.lat*Math.PI/180, l = site.lon*Math.PI/180;
    const d = site.diameter_km/2*factor/3393.5, lat=[], lon=[];
    for(let angle=0;angle<=360;angle+=3) {
      const b=angle*Math.PI/180;
      const p2=Math.asin(Math.sin(p)*Math.cos(d)+Math.cos(p)*Math.sin(d)*Math.cos(b));
      const l2=l+Math.atan2(Math.sin(b)*Math.sin(d)*Math.cos(p),Math.cos(d)-Math.sin(p)*Math.sin(p2));
      lat.push(p2*180/Math.PI);lon.push(l2*180/Math.PI);
    }
    return {x:lon,y:lat,type:'scatter',mode:'lines',line:{color:'#f6e9d9',width:factor===.8?2:1,dash:factor===.8?'solid':factor===1?'dot':'dash'},
      hoverinfo:'skip',showlegend:false};
  }

  function restore() {
    const q=new URLSearchParams(location.search);
    for(const [key,id] of [['region','pilotRegion'],['altitude','pilotAltitude'],['layer','pilotLayer']]) {
      const value=q.get(key); if([...$(id).options].some(o=>o.value===value)) $(id).value=value;
    }
    $('pilotMinerals').checked=q.get('minerals')==='1';
  }

  async function render() {
    const version=++renderVersion;
    const id=$('pilotRegion').value, h=$('pilotAltitude').value, layer=$('pilotLayer').value;
    current=data.cases.find(c=>c.site.id===id);
    const c=current,s=c.site,m=c.map,b=c.baseline[h];
    $('pilotAltitude').disabled=layer==='topography';
    const q=new URLSearchParams({region:id,altitude:h,layer});
    if($('pilotMinerals').checked) q.set('minerals','1');
    history.replaceState(null,'',`${location.pathname}?${q}`);
    $('pilotStatus').textContent=`${s.name} · ${s.role} · Saved calculation`;
    $('pilotCaution').textContent=s.caution || 'The reference ring is nearby terrain, not a proven unaltered control. Surface map units are not deep magnetic lithologies or exact impact ages.';
    $('pilotMetrics').innerHTML=`<span class="study-kicker">${esc(s.region.toUpperCase())}</span><h2>${esc(s.name)}</h2><dl>
      <div><dt>Inside / reference field · ${h} km</dt><dd>${fmt(b.ratio)}<small>${fmt(b.inside_nT)} / ${fmt(b.outside_nT)} nT</small></dd></div>
      <div><dt>After surface-unit standardization</dt><dd>${fmt(b.matched_ratio)}<small>${pct(b.common_support_fraction)} of interior retained</small></dd></div>
      <div><dt>All altitude & geometry choices</dt><dd>${fmt(c.summary.ratio_min)}–${fmt(c.summary.ratio_max)}<small>Raw ratio range · not a confidence interval</small></dd></div></dl>
      <p>Below 1: lower mean orbital field inside. Above 1: higher. Neither measures the fraction of ancient remanence preserved.</p><a class="study-source" href="${esc(s.geometry_source)}">Geometry source ↗</a>`;
    const z=layer==='field'?m.field_nT[h].map(row=>row.map(v=>Math.log10(Math.max(v,1e-9)))):m.topography_km;
    const trace={type:'heatmap',x:m.lon,y:m.lat,z,zmin:layer==='field'?0:-8,zmax:layer==='field'?3:10,
      colorscale:layer==='field'?fieldColors:topoColors,
      customdata:layer==='field'?m.field_nT[h]:m.topography_km,
      hovertemplate:`%{y:.2f}° N, %{x:.2f}° E<br>%{customdata:.2f} ${layer==='field'?'nT':'km'}<extra></extra>`,
      colorbar:layer==='field'?{title:{text:'|B| · nT'},tickvals:[0,1,2,3],ticktext:['1','10','100','1000'],thickness:12}:{title:{text:'km'},thickness:12}};
    const traces=[trace,...[.8,1,1.2,2].map(f=>circle(s,f))];
    const legend=[];
    if($('pilotMinerals').checked) {
      for(const [key,[label,color]] of Object.entries(minerals)) {
        const pts=m.mineral_points.filter(p=>p.class===key);if(!pts.length)continue;
        legend.push(`<span><i style="color:${color}">◆</i> ${esc(label)}</span>`);
        traces.push({type:'scatter',mode:'markers',x:pts.map(p=>p.lon),y:pts.map(p=>p.lat),name:label,
          marker:{symbol:'diamond-open',size:9,color,line:{width:1.5}},showlegend:false,
          hovertemplate:`${esc(label)}<br>Occupied 2° cell; presence only<extra></extra>`});
      }
    }
    $('pilotMapLegend').innerHTML=legend.join('');
    $('pilotMapLegend').hidden=!legend.length;
    const extent=2.13*s.diameter_km/2/3393.5*180/Math.PI;
    await Plotly.react('pilotMap',traces,{...base,margin:{l:55,r:30,t:20,b:48},
      xaxis:{title:{text:'East longitude (°)'},range:[s.lon-extent/Math.cos(s.lat*Math.PI/180),s.lon+extent/Math.cos(s.lat*Math.PI/180)],gridcolor:'#39322d',zeroline:false,constrain:'domain'},
      yaxis:{title:{text:'Latitude (°)'},range:[s.lat-extent,s.lat+extent],gridcolor:'#39322d',zeroline:false,scaleanchor:'x',scaleratio:1/Math.cos(s.lat*Math.PI/180),constrain:'domain'}},config);
    if(version!==renderVersion)return;
    const profileTraces=Object.entries(c.profiles).map(([alt,rows],i)=>({type:'scatter',mode:'lines+markers',
      x:rows.map(p=>p.radius_R),y:rows.map(p=>p.mean),name:alt+' km',
      line:{color:['#e3a077','#879db7','#b998a5'][i],width:alt===h?3:1.5},marker:{size:alt===h?5:3},
      hovertemplate:'%{x:.2f} R · %{y:.2f} nT<extra>'+alt+' km</extra>'}));
    await Plotly.react('pilotProfile',profileTraces,{...base,xaxis:{title:{text:'Distance / catalog radius R'},range:[0,2.5],gridcolor:'#332e29',zeroline:false},
      yaxis:{title:{text:'Mean orbital |B| (nT)'},gridcolor:'#332e29',rangemode:'tozero'},
      shapes:[{type:'line',xref:'x',yref:'paper',x0:1,x1:1,y0:0,y1:1,line:{dash:'dot',color:'#8e8175'}}]},config);
    if(version!==renderVersion)return;
    $('pilotGeology').innerHTML=`<p>Retained interior: <strong>${pct(b.common_support_fraction)}</strong>. Raw ratio: ${fmt(b.ratio)}. Standardized ratio: ${fmt(b.matched_ratio)}.</p>
      ${b.common_support_fraction<.5?'<p class="notice">More than half the interior has no matching surface unit in the reference ring. The standardized value cannot describe the whole crater.</p>':''}
      <div class="table-scroll"><table><thead><tr><th>Common surface unit</th><th>Inside area</th><th>Reference area</th><th>Inside mean · nT</th><th>Reference mean · nT</th></tr></thead><tbody>${b.strata.map(row=>`<tr><td>${esc(data.units[row.unit_index].code)}<br><small>${esc(data.units[row.unit_index].description)}</small></td><td>${pct(row.inside_area_fraction)}</td><td>${pct(row.outside_area_fraction)}</td><td>${fmt(row.inside_nT)}</td><td>${fmt(row.outside_nT)}</td></tr>`).join('')}</tbody></table></div><p>Percentages use each full baseline area before common-unit filtering. They need not sum to 100% when units are unmatched.</p>`;
    $('pilotMineralTable').innerHTML=`<div class="table-scroll"><table><thead><tr><th>Spectral class</th><th>Occupied 2° cells within 2 R</th></tr></thead><tbody>${c.mineral_counts.map(p=>`<tr><td>${esc(p.label)}</td><td>${p.occupied_2deg_cells_within_2R}</td></tr>`).join('')}</tbody></table></div>`;
    if($('morphDrawer').open) await renderMorphology();
  }

  async function renderMorphology() {
    if(!current)return;
    const m=current.morphology;
    const traces=[{x:m.normalized_radius,y:m.azimuth_q25_km,type:'scatter',mode:'lines',line:{width:0},showlegend:false,hoverinfo:'skip'},
      {x:m.normalized_radius,y:m.azimuth_q75_km,type:'scatter',mode:'lines',line:{width:0},fill:'tonexty',fillcolor:'#d7996e25',name:'Azimuthal 25–75% range',hoverinfo:'skip'},
      {x:m.normalized_radius,y:m.median_elevation_km,type:'scatter',mode:'lines',line:{color:'#e3a077',width:2},name:'Median elevation',hovertemplate:'%{x:.2f} R · %{y:.2f} km<extra></extra>'}];
    await Plotly.react('pilotMorphology',traces,{...base,xaxis:{title:{text:'Distance / catalog radius R'},gridcolor:'#332e29'},yaxis:{title:{text:'Elevation above areoid (km)'},gridcolor:'#332e29'},legend:{...base.legend,y:1.2}},config);
    $('pilotMorphNote').textContent=`Fixed-rim depth: ${fmt(m.depth_km)} km. Depth / diameter: ${m.depth_diameter.toFixed(4)}. ${m.rays} radial rays. These descriptive values are not a hydrothermal classification.`;
  }

  async function start() {
    try {
      const response=await fetch('/research/files/pilot/results.json');
      if(!response.ok)throw new Error(`HTTP ${response.status}`);
      data=await response.json();restore();await render();
      for(const id of ['pilotRegion','pilotLayer','pilotAltitude','pilotMinerals']) $(id).addEventListener('change',()=>render().catch(fail));
      $('morphDrawer').addEventListener('toggle',()=>{if($('morphDrawer').open)renderMorphology().catch(fail);});
    } catch(error) {fail(error);}
  }
  function fail(error) {
    $('pilotStatus').textContent='The saved plots could not be displayed. Reload this page, or use the downloadable results on the Results page.';
    console.error('Regional study rendering failed',error);
  }
  start();
})();
