/* Saved, original synthetic calculations. No model is fitted in the browser. */
'use strict';
const byId = id => document.getElementById(id);
const scenarioSelect = byId('thermalScenario');
const carrierSelect = byId('thermalCarrier');
const windowSelect = byId('thermalWindow');
const transpose = matrix => matrix[0].map((_, j) => matrix.map(row => row[j]));
let experiment;

function plotLayout(caseData, candidate = false) {
  return {
    paper_bgcolor: '#1d1c1b', plot_bgcolor: '#1d1c1b', font: {color: '#d8d1ca', size: 11},
    margin: {l: 48, r: 52, t: 20, b: 56},
    xaxis: {title: {text: candidate ? 'Candidate recording time (Gyr elapsed)' : 'Time (Gyr elapsed)', font: {size: 11}}, range: windowSelect.value === 'event' ? [.999, 1.003] : [0, 4], tickformat: windowSelect.value === 'event' ? '.3f' : '.1f', fixedrange: true},
    yaxis: {title: {text: 'Depth (km)'}, range: [50, 0], fixedrange: true},
    shapes: caseData.pulses.map(p => ({type: 'line', x0: p.time_myr/1000, x1: p.time_myr/1000, y0: 0, y1: 50, line: {color: '#f0d7c4', dash: 'dash', width: 1}})),
    showlegend: false
  };
}

async function render() {
  const c = experiment.scenarios.find(item => item.id === scenarioSelect.value);
  const carrier = experiment.protocol.ordering_thresholds.find(item => item.id === carrierSelect.value);
  const x = c.time_myr.map(t => t/1000), y = c.depth_km;
  const temperature = transpose(c.temperature_k).map(row => row.map(k => k-273.15));
  const config = {responsive: true, displayModeBar: false};
  const temperaturePlot = Plotly.react('thermalTemperature', [
    {type: 'heatmap', x, y, z: temperature, colorscale: [[0,'#000004'],[.2,'#3b0f70'],[.4,'#8c2981'],[.6,'#de4968'],[.8,'#fe9f6d'],[1,'#fcfdbf']], zmin: -55, zmax: 725,
      colorbar: {title: {text: '°C', side: 'top'}, len: .95, thickness: 10, tickfont: {size: 10}},
      hovertemplate: '%{x:.3f} Gyr elapsed<br>%{y:.1f} km depth<br>%{z:.1f} °C<extra></extra>'},
    {type: 'contour', x, y, z: temperature, contours: {start: carrier.temperature_c, end: carrier.temperature_c, size: 1, coloring: 'none'},
      showscale: false, line: {color: 'white', width: 1.5}, hoverinfo: 'skip'}
  ], plotLayout(c), config);
  const gateData = transpose(c.gates[carrier.id]);
  const gatePlot = Plotly.react('thermalGate', [{
    type: 'heatmap', x, y, z: gateData, zmin: -.5, zmax: 2.5,
    colorscale: [[0, '#5eaca4'], [1/3, '#5eaca4'], [1/3, '#d7825b'], [2/3, '#d7825b'], [2/3, '#454c58'], [1, '#454c58']],
    showscale: false, text: gateData.map(row => row.map(code => ['No crossing; survival unresolved', 'Later ordering-temperature crossing', 'At or above ordering temperature'][code])),
    hovertemplate: '%{x:.3f} Gyr elapsed<br>%{y:.1f} km depth<br>%{text}<extra></extra>'
  }], plotLayout(c, true), config);
  const timeIndex = c.time_myr.indexOf(500), depthIndex = c.depth_km.indexOf(25);
  const now = c.temperature_k[timeIndex][depthIndex]-273.15;
  const peak = c.future_peak_k[timeIndex][depthIndex]-273.15;
  const code = c.gates[carrier.id][timeIndex][depthIndex];
  const outcome = ['This component passes only the ordering-temperature gate. Its acquisition and survival still need separate tests.',
    'This component is cool enough at the proposed recording time, but later heating excludes preservation of that original component under this thermal history.',
    'The selected carrier is already at or above its ordering temperature at the proposed recording time.'][code];
  byId('thermalExample').replaceChildren();
  const heading = document.createElement('h3'); heading.textContent = c.label;
  const values = document.createElement('p');
  values.textContent = `At recording: ${now.toFixed(1)} °C. Maximum from then to the end: ${peak.toFixed(1)} °C. Selected threshold: ${carrier.temperature_c} °C.`;
  const conclusion = document.createElement('p'); const strong = document.createElement('strong'); strong.textContent = outcome; conclusion.append(strong);
  byId('thermalExample').append(heading, values, conclusion);
  await Promise.all([temperaturePlot, gatePlot]);
  byId('thermalStatus').textContent = `${c.label} · ${carrier.label}, ${carrier.temperature_c} °C · saved synthetic run`;
  const url = new URL(location.href); url.searchParams.set('scenario', c.id); url.searchParams.set('carrier', carrier.id);
  history.replaceState(null, '', url);
}

function showValidation() {
  const v = experiment.validation;
  const rows = [
    ['Steady analytic geotherm', `${v.steady_max_error_k.toExponential(2)} K maximum error`, 'Constant basal flux and internal heating'],
    ['Exact transient solution', `${v.transient_max_error_k.toFixed(4)} K maximum error`, '100 K initial sinusoidal anomaly, after 50 Myr'],
    ...v.scenario_comparisons.map(c => [experiment.scenarios.find(s => s.id === c.id).label, `${c.max_temperature_difference_k.toFixed(3)} K maximum difference`, 'Twice the spatial resolution and half both time steps'])
  ];
  const table = document.createElement('table');
  const head = table.createTHead().insertRow();
  ['Check', 'Measured numerical discrepancy', 'Comparison'].forEach(text => {const th = document.createElement('th'); th.scope = 'col'; th.textContent = text; head.append(th);});
  const body = table.createTBody();
  rows.forEach(row => {const tr = body.insertRow(); row.forEach(text => {tr.insertCell().textContent = text;});});
  byId('thermalValidation').replaceChildren(table);
}

function fail(error) {
  byId('thermalStatus').textContent = 'The interactive view could not load. The scientific figure and downloadable results below remain available.';
  scenarioSelect.disabled = carrierSelect.disabled = windowSelect.disabled = true;
  console.error('Thermal experiment:', error);
}

async function start() {
  const response = await fetch('/research/files/thermal/results.json?v=1');
  if (!response.ok) throw new Error(`Saved results: HTTP ${response.status}`);
  experiment = await response.json();
  const params = new URLSearchParams(location.search);
  if (experiment.scenarios.some(s => s.id === params.get('scenario'))) scenarioSelect.value = params.get('scenario');
  if (experiment.protocol.ordering_thresholds.some(s => s.id === params.get('carrier'))) carrierSelect.value = params.get('carrier');
  showValidation(); await render();
  scenarioSelect.disabled = carrierSelect.disabled = windowSelect.disabled = false;
  scenarioSelect.addEventListener('change', () => render().catch(fail));
  carrierSelect.addEventListener('change', () => render().catch(fail));
  windowSelect.addEventListener('change', () => render().catch(fail));
}
start().catch(fail);
