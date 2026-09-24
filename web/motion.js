'use strict';
let motionSequence=null,motionSnapshot=null,motionIndex=0,motionPlaying=false,motionPreparing=false,motionTimer=null,motionRequest=null,motionGeneration=0,controlTimer=null,profileTimer=null,movieWorking=false;
function controlParameters(){return {...state,altitude:+$('altitude').value,ls:+$('ls').value,lt:+$('lt').value,azimuth:+$('azimuth').value,time_mode:$('time_mode').value,field:$('field').value};}
function syncControls(){
 $('altitudeValue').value=$('altitude').value;$('seasonValue').value=$('ls').value;updateLabels();
}
function motionButtons(){
 $('playMotion').textContent=motionPreparing?'■ Cancel':motionPlaying?'Ⅱ Pause':'▶ Play';
 const ready=!!motionSequence;
 for(const id of ['previousFrame','nextFrame','frameSlider'])$(id).disabled=!ready;
 $('downloadMovie').disabled=!ready||movieWorking;
 document.body.dataset.motion=motionPreparing?'preparing':motionPlaying?'playing':'paused';
}
function sequenceDescription(){return $('sweepAxis').value==='season'?'24 seasonal slices, Ls 0–345°. Altitude and time convention stay fixed.':'20 altitude slices, 10–200 km above the areoid. Season and time convention stay fixed.';}
function clearMotion(){
 motionGeneration++;motionRequest?.abort();motionRequest=null;clearTimeout(motionTimer);clearTimeout(profileTimer);
 motionPlaying=false;motionPreparing=false;motionSequence=null;motionSnapshot=null;mapScale=null;
 $('scaleNote').textContent='Scale for this map';$('motionStatus').textContent=sequenceDescription()+' Press Play to prepare.';
 $('frameSlider').value=0;$('frameCount').textContent='— / '+($('sweepAxis').value==='season'?24:20);motionButtons();
}
function queueControls(){
 clearMotion();clearTimeout(controlTimer);syncControls();
 $('liveState').textContent='Updating… the map label identifies the last completed calculation.';
 controlTimer=setTimeout(async()=>{try{await refresh(controlParameters());}catch(e){fail(e);$('liveState').textContent='Calculation failed. Last completed map remains visible.';}},350);
}
async function syncFrameProfile(){
 if(!motionSequence||motionPlaying)return;
 const token=++revision;
 try{const p=await api('profile');if(token!==revision)return;profileData=p;renderProfiles();loaded={};await ensureTab();}
 catch(e){if(token===revision)fail(e);}
}
async function pauseMotion(sync=true){
 if(motionPreparing){clearMotion();return;}
 motionPlaying=false;clearTimeout(motionTimer);motionButtons();
 if(motionSequence)$('motionStatus').textContent='Paused. Drag the timeline or step between frames. Colours use the same scale throughout.';
 if(sync&&motionSequence)await syncFrameProfile();
}
function displayMotionFrame(index){
 if(!motionSequence)return;
 motionIndex=(index+motionSequence.frames.length)%motionSequence.frames.length;
 const frame=motionSequence.frames[motionIndex],axis=motionSequence.axis;
 // Atomically commit the frame and its context. No interpolation between physical samples.
 ++revision;refreshing=false;$('apply').disabled=false;loaded={};
 state={...motionSnapshot,lon:state.lon,lat:state.lat,[axis==='season'?'ls':'altitude']:frame.value};
 mapData={...frame,longitude:motionSequence.longitude,latitude:motionSequence.latitude};mapScale=motionSequence.scale;
 $('altitude').value=state.altitude;$('ls').value=state.ls;syncControls();
 renderStats();drawMap();$('provenance').textContent=JSON.stringify(frame.provenance,null,2);
 $('frameSlider').value=motionIndex;$('frameCount').textContent=`${String(motionIndex+1).padStart(2,'0')} / ${motionSequence.frames.length}`;
 $('scaleNote').textContent=`Fixed scale · all ${motionSequence.frames.length} frames`;
 $('liveState').textContent=`Showing ${state.altitude} km · Ls ${state.ls}°`;
 // Column plots are refreshed when playback pauses, not silently reused as current data.
 document.querySelector('.two-col').hidden=true;
}
function advanceMotion(){
 if(!motionPlaying)return;
 displayMotionFrame(motionIndex+1);
 motionTimer=setTimeout(advanceMotion,1000/+$('playRate').value);
}
async function playMotion(){
 if(motionPreparing){clearMotion();$('motionStatus').textContent='Preparation cancelled. The last completed map is retained.';return;}
 if(motionPlaying){await pauseMotion(true);return;}
 if(!motionSequence){
  clearTimeout(controlTimer);const snapshot=controlParameters(),generation=++motionGeneration;
  ++revision;refreshing=false;$('apply').disabled=false;
  motionPreparing=true;motionRequest=new AbortController();motionButtons();
  $('motionStatus').textContent='Preparing the complete sequence and a shared colour scale… the first run may take a minute.';
  try{
   const response=await fetch('/api/sequence?'+new URLSearchParams({...snapshot,axis:$('sweepAxis').value}),{signal:motionRequest.signal});
   const sequence=await response.json();if(!response.ok)throw new Error(typeof sequence.detail==='string'?sequence.detail:'Could not prepare the animation.');
   if(generation!==motionGeneration)return;
   motionSequence=sequence;motionSnapshot=snapshot;$('frameSlider').max=sequence.frames.length-1;
   const target=sequence.axis==='season'?snapshot.ls:snapshot.altitude;
   motionIndex=sequence.values.reduce((best,value,i)=>Math.abs(value-target)<Math.abs(sequence.values[best]-target)?i:best,0);
  }catch(e){if(e.name!=='AbortError'){fail(e);$('motionStatus').textContent='Preparation failed. Adjust the controls or try again.';}return;}
  finally{if(generation===motionGeneration){motionPreparing=false;motionRequest=null;motionButtons();}}
 }
 if(currentTab!=='atlas'||!motionSequence)return;
 motionPlaying=true;motionButtons();displayMotionFrame(motionIndex);
 $('motionStatus').textContent=sequenceDescription()+(motionSequence.axis==='season'?' Playback repeats; equal Ls steps are not equal elapsed time.':' Playback repeats; this is a vertical scan, not atmospheric evolution.');
 motionTimer=setTimeout(advanceMotion,1000/+$('playRate').value);
}
for(const id of ['altitude','ls'])$(id).addEventListener('input',queueControls);
for(const [number,slider] of [['altitudeValue','altitude'],['seasonValue','ls']])$(number).addEventListener('change',()=>{
 const input=$(number);if(!input.reportValidity())return;$(slider).value=input.value;queueControls();
});
for(const b of document.querySelectorAll('[data-season]'))b.onclick=()=>{$('ls').value=b.dataset.season;queueControls();};
$('apply').onclick=guarded(async()=>{clearTimeout(controlTimer);clearMotion();await refresh(controlParameters());});
$('field').onchange=queueControls;
$('sweepAxis').onchange=()=>{clearMotion();if(mapData)guarded(()=>refresh(controlParameters()))();};
$('playMotion').onclick=playMotion;
$('previousFrame').onclick=async()=>{await pauseMotion(false);displayMotionFrame(motionIndex-1);await syncFrameProfile();};
$('nextFrame').onclick=async()=>{await pauseMotion(false);displayMotionFrame(motionIndex+1);await syncFrameProfile();};
$('frameSlider').addEventListener('input',()=>{pauseMotion(false);displayMotionFrame(+$('frameSlider').value);clearTimeout(profileTimer);profileTimer=setTimeout(syncFrameProfile,250);});
$('playRate').onchange=()=>{if(motionPlaying){clearTimeout(motionTimer);motionTimer=setTimeout(advanceMotion,1000/+$('playRate').value);}};
$('downloadMovie').onclick=async()=>{
 if(!motionSnapshot||movieWorking)return;
 const snapshot={...motionSnapshot,axis:motionSequence.axis,fps:+$('playRate').value},generation=motionGeneration;
 await pauseMotion(true);if(generation!==motionGeneration)return;
 movieWorking=true;motionButtons();$('downloadMovie').textContent='Encoding…';$('motionStatus').textContent='Rendering a labelled MP4 with the same fixed colour scale. Your download will start when it is ready.';
 try{
  const response=await fetch('/api/movie?'+new URLSearchParams(snapshot));
  if(!response.ok){const err=await response.json();throw new Error(typeof err.detail==='string'?err.detail:'Movie export failed.');}
  const url=URL.createObjectURL(await response.blob()),a=document.createElement('a');a.href=url;a.download=`marswind_${snapshot.axis}_${snapshot.field}.mp4`;a.click();setTimeout(()=>URL.revokeObjectURL(url),60000);
  $('motionStatus').textContent='MP4 ready. The video includes frame parameters, units, the time convention and model credits.';
 }catch(e){fail(e);$('motionStatus').textContent='Movie export failed. The interactive sequence is still available.';}
 finally{movieWorking=false;$('downloadMovie').textContent='↓ MP4';motionButtons();}
};
document.addEventListener('marswind:updated',()=>{
 clearMotion();
 $('altitude').value=state.altitude;$('ls').value=state.ls;syncControls();
 $('liveState').textContent=`Showing ${state.altitude} km · Ls ${state.ls}° · auto-update on`;
 document.querySelector('.two-col').hidden=false;
});
// Pausing restores the column for exactly the visible map frame.
const originalRenderProfiles=renderProfiles;
renderProfiles=function(){originalRenderProfiles();if(profileData&&!motionPlaying)document.querySelector('.two-col').hidden=false;};
// A hidden page must not keep playing or silently jump the user's visible map.
document.addEventListener('visibilitychange',()=>{if(document.hidden&&motionPlaying)pauseMotion(true);});
$('map').addEventListener('click',()=>{if(motionPlaying)pauseMotion(false);},true);
syncControls();motionButtons();
