/** Pure display rules: unknown ages never become zero and bounds stay open. */
export const windows = {all:[0,4600], ancient:[3500,4600], middle:[0,1500], recent:[0,50]};
export function ageExtent(age) {
  if (age.kind === 'unknown') return null;
  if (age.kind === 'minimum') return [age.younger_ma, Infinity];
  if (age.kind === 'approximate') return [age.value_ma, age.value_ma];
  return [age.younger_ma, age.older_ma];
}
export function selectEvents(events, {sample='', type='', window='all'}={}) {
  const [young,old] = windows[window] || windows.all;
  const selected=events.filter(e=>(!sample||e.sample===sample)&&(!type||e.event_type===type));
  const dated=selected.filter(e=>{const x=ageExtent(e.age); return x&&x[1]>=young&&x[0]<=old;});
  dated.sort((a,b)=>ageExtent(b.age)[1]-ageExtent(a.age)[1]);
  return {dated,undated:selected.filter(e=>e.age.kind==='unknown'),excluded:selected.length-dated.length-selected.filter(e=>e.age.kind==='unknown').length};
}
export function clipAge(age, window='all') {
  const range=ageExtent(age); if(!range) return null;
  const [young,old]=windows[window]||windows.all;
  if(range[0]>old||range[1]<young) return null;
  return {left:(old-Math.min(old,range[1]))/(old-young)*1000,
    right:(old-Math.max(young,range[0]))/(old-young)*1000,
    clippedOld:range[1]>old,clippedYoung:range[0]<young};
}
