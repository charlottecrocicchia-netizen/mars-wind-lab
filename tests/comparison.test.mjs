import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {ageExtent, selectEvents, clipAge} from '../web/comparison-model.mjs';
const data=JSON.parse(readFileSync(new URL('../research/comparison/evidence.json',import.meta.url)));
const event=id=>data.events.find(e=>e.id===id);

test('recent zoom excludes ancient formation and never places unknown dates at zero',()=>{
 const r=selectEvents(data.events,{window:'recent'});
 assert.deepEqual(new Set(r.dated.map(e=>e.id)),new Set(['laf_ejection','nwa_ejection']));
 assert.deepEqual(new Set(r.undated.map(e=>e.id)),new Set(['global_dichotomy','laf_remanence']));
 assert.equal(clipAge(event('laf_remanence').age,'recent'),null);
 assert.equal(clipAge(event('nwa_crystal').age,'recent'),null);
});
test('sample and event filters intersect without borrowing another meteorite’s shock age',()=>{
 const r=selectEvents(data.events,{sample:'Lafayette',type:'Shock'});
 assert.deepEqual(r.dated,[]);assert.deepEqual(r.undated,[]);
 const m=selectEvents(data.events,{sample:'Lafayette',type:'Magnetization'});
 assert.equal(m.dated.length,0);assert.deepEqual(m.undated.map(e=>e.id),['laf_remanence']);
 assert.equal(selectEvents(data.events,{sample:'Lafayette'}).dated.length,3);
});
test('a minimum age stays open toward older time and is only clipped for display',()=>{
 const age=event('nwa_reservoir').age;
 assert.deepEqual(ageExtent(age),[4547,Infinity]);
 const p=clipAge(age,'ancient');assert.equal(p.left,0);assert.equal(p.clippedOld,true);
 assert.ok(Math.abs(p.right-53/1100*1000)<1e-9);
 assert.equal(clipAge(age,'middle'),null);
 assert.equal(age.older_ma,null);
});
test('linear coordinates preserve Ma and reported intervals rather than symbol widths',()=>{
 const range=clipAge(event('nwa_ejection').age,'recent');
 assert.deepEqual(range,{left:800,right:900,clippedOld:false,clippedYoung:false});
 const water=event('laf_water').age;
 assert.deepEqual(ageExtent(water),[727,757]);
 assert.equal(clipAge({kind:'range',younger_ma:20,older_ma:100},'recent').left,0);
 assert.equal(clipAge({kind:'approximate',value_ma:0},'recent').left,1000);
 assert.equal(clipAge({kind:'range',younger_ma:50,older_ma:60},'recent').right,0);
});
