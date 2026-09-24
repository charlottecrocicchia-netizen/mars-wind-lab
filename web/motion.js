'use strict';
let motionSequence=null,motionSnapshot=null,motionIndex=0,motionPlaying=false,motionPreparing=false,motionTimer=null,motionRequest=null,motionGeneration=0,controlTimer=null,profileTimer=null,movieWorking=false,movieURL=null;
function controlParameters(){return {...state,altitude:+$('altitude').value,ls:+$('ls').value,lt:+$('lt').value,azimuth:+$('azimuth').value,time_mode:$('time_mode').value,field:$('field').value};}
function syncControls(){
 $('altitudeValue').value=$('altitude').value;$('seasonValue').value=$('ls').value;updateLabels();
}
function motionButtons(){
 $('playMotion').textContent=motionPreparing?'■ Cancel':motionPlaying?'Ⅱ Pause':'▶ Play';
 const ready=!!motionSequence;
 for(const id of ['previousFrame','nextFrame','frameSlider'])$(id).disabled=!ready;
 $('downloadMovie').disabled=motionPreparing||movieWorking;
 document.body.dataset.motion=motionPreparing?'preparing':motionPlaying?'playing':'paused';
}
function sequenceDescription(){return $('sweepAxis').value==='season'?'24 seasonal slices, Ls 0–345°. Altitude and time convention stay fixed.':'20 altitude slices, 10–200 km above the areoid. Season and time convention stay fixed.';}
function clearMotion(){
 motionGeneration++;motionRequest?.abort();motionRequest=null;clearTimeout(motionTimer);clearTimeout(profileTimer);
 motionPlaying=false;motionPreparing=false;motionSequence=null;motionSnapshot=null;mapScale=null;
 $('motionProgress').hidden=true;
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
async function readSequence(response,onProgress){
 if(!response.ok){const problem=await response.json();throw new Error(problem.detail||'Could not prepare the animation.');}
 const reader=response.body.getReader(),decoder=new TextDecoder();let buffer='',sequence=null;
 try{
  while(true){
   const {value,done}=await reader.read();buffer+=decoder.decode(value||new Uint8Array(),{stream:!done});
   let boundary;
   while((boundary=buffer.indexOf('\n\n'))>=0){
    const block=buffer.slice(0,boundary);buffer=buffer.slice(boundary+2);
    if(!block.startsWith('data: '))continue;
    const event=JSON.parse(block.slice(6));
    if(event.event==='error')throw new Error(event.detail);
    if(event.event==='progress')onProgress(event);
    if(event.event==='complete')sequence=event.sequence;
   }
   if(done)break;
  }
 }finally{reader.releaseLock();}
 if(!sequence)throw new Error('The sequence was interrupted. Press Play to retry.');
 return sequence;
}
async function prepareMotion(){
 if(!motionSequence){
  clearTimeout(controlTimer);const snapshot=controlParameters(),generation=++motionGeneration;
  ++revision;refreshing=false;$('apply').disabled=false;
  motionPreparing=true;motionRequest=new AbortController();motionButtons();
  $('error').hidden=true;$('motionProgress').hidden=false;$('motionProgress').value=0;
  $('motionStatus').textContent='Preparing atmospheric frames… progress will appear below. Uncached calculations can take a few minutes.';
  try{
   const response=await fetch('/api/sequence/stream?'+new URLSearchParams({...snapshot,axis:$('sweepAxis').value}),{signal:motionRequest.signal});
   const sequence=await readSequence(response,event=>{
    if(generation!==motionGeneration)return;
    $('motionProgress').max=event.total;$('motionProgress').value=event.completed;
    $('frameCount').textContent=`${event.completed} / ${event.total}`;
    $('motionStatus').textContent=`Preparing ${event.completed} of ${event.total} frames. The colour scale is calculated from the complete sequence.`;
   });
   if(generation!==motionGeneration)return false;
   motionSequence=sequence;motionSnapshot=snapshot;$('frameSlider').max=sequence.frames.length-1;
   const target=sequence.axis==='season'?snapshot.ls:snapshot.altitude;
   motionIndex=sequence.values.reduce((best,value,i)=>Math.abs(value-target)<Math.abs(sequence.values[best]-target)?i:best,0);
   displayMotionFrame(motionIndex);
  }catch(e){if(generation===motionGeneration&&e.name!=='AbortError'){fail(e);$('motionStatus').textContent='Preparation failed. Adjust the controls or try again.';}return false;}
  finally{if(generation===motionGeneration){motionPreparing=false;motionRequest=null;$('motionProgress').hidden=true;motionButtons();}}
 }
 return !!motionSequence;
}
async function playMotion(){
 if(motionPreparing){clearMotion();$('motionStatus').textContent='Preparation cancelled. The last completed map is retained.';return;}
 if(motionPlaying){await pauseMotion(true);return;}
 if(!await prepareMotion()||currentTab!=='atlas')return;
 motionPlaying=true;motionButtons();displayMotionFrame(motionIndex);
 $('motionStatus').textContent=sequenceDescription()+(motionSequence.axis==='season'?' Playback repeats; equal Ls steps are not equal elapsed time.':' Playback repeats; this is a vertical scan, not atmospheric evolution.');
 motionTimer=setTimeout(advanceMotion,1000/+$('playRate').value);
}
for(const id of ['altitude','ls'])$(id).addEventListener('input',queueControls);
for(const [number,slider] of [['altitudeValue','altitude'],['seasonValue','ls']]){
 $(number).addEventListener('input',()=>{const input=$(number);if(!input.checkValidity())return;$(slider).value=input.value;queueControls();});
 $(number).addEventListener('change',()=>$(number).reportValidity());
}
for(const b of document.querySelectorAll('[data-season]'))b.onclick=()=>{$('ls').value=b.dataset.season;queueControls();};
$('apply').onclick=guarded(async()=>{clearTimeout(controlTimer);clearMotion();await refresh(controlParameters());});
$('field').onchange=queueControls;
$('sweepAxis').onchange=()=>{clearMotion();if(mapData)guarded(()=>refresh(controlParameters()))();};
$('playMotion').onclick=guarded(playMotion);
$('previousFrame').onclick=async()=>{await pauseMotion(false);displayMotionFrame(motionIndex-1);await syncFrameProfile();};
$('nextFrame').onclick=async()=>{await pauseMotion(false);displayMotionFrame(motionIndex+1);await syncFrameProfile();};
$('frameSlider').addEventListener('input',()=>{pauseMotion(false);displayMotionFrame(+$('frameSlider').value);clearTimeout(profileTimer);profileTimer=setTimeout(syncFrameProfile,250);});
$('playRate').onchange=()=>{if(motionPlaying){clearTimeout(motionTimer);motionTimer=setTimeout(advanceMotion,1000/+$('playRate').value);}};
$('downloadMovie').onclick=async()=>{
 if(movieWorking||motionPreparing)return;
 if(!await prepareMotion())return;
 const snapshot={...motionSnapshot,axis:motionSequence.axis,fps:+$('playRate').value},generation=motionGeneration;
 await pauseMotion(true);if(generation!==motionGeneration)return;
 movieWorking=true;motionButtons();$('downloadMovie').textContent='Encoding…';$('motionStatus').textContent='Rendering a labelled MP4. A video player and download link will appear here when it is ready.';
 try{
  const response=await fetch('/api/movie?'+new URLSearchParams(snapshot));
  if(!response.ok){const err=await response.json();throw new Error(typeof err.detail==='string'?err.detail:'Movie export failed.');}
  const blob=await response.blob();if(movieURL)URL.revokeObjectURL(movieURL);movieURL=URL.createObjectURL(blob);
  const player=$('moviePlayer');player.src=movieURL;player.load();
  const link=$('saveMovie');link.href=movieURL;link.download=`marswind_${snapshot.axis}_${snapshot.field}.mp4`;
  $('movieContext').textContent=`${labels[snapshot.field]} · ${snapshot.axis==='season'?snapshot.altitude+' km · seasonal sweep':'Ls '+snapshot.ls+'° · altitude sweep'} · ${snapshot.fps} frames/s`;
  $('moviePanel').hidden=false;
  $('motionStatus').textContent='Video ready below. Press the video player’s Play button, or choose Download MP4.';
 }catch(e){fail(e);$('motionStatus').textContent='Movie export failed. The interactive sequence is still available.';}
 finally{movieWorking=false;$('downloadMovie').textContent='Create video';motionButtons();}
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
