import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {groupKey,sampleGroup,candidateRelations} from '../web/meteorite-links.mjs';
const data=JSON.parse(readFileSync(new URL('../research/data/meteorites.json',import.meta.url)));
const group=name=>data.groups.find(g=>g.group===name);
test('all sample records connect to an existing group, including whitespace and split groups',()=>{
  const groups=new Set(data.groups.map(g=>g.group));
  for(const sample of data.samples)assert.ok(groups.has(sampleGroup(sample)),sample.name);
  assert.equal(groupKey(' 5-2'),'5-2');
});
test('preferred sources and conditional alternatives retain their different status',()=>{
  const links=candidateRelations(group('group 2'),data.craters);
  assert.equal(links.find(r=>r.crater.name==='Tooting').kind,'preferred');
  const alternative=links.find(r=>r.crater.name==='Zunil');
  assert.equal(alternative.kind,'alternative');
  assert.match(alternative.condition,/if.*older lava flows/);
  assert.equal(links.some(r=>r.crater.name==='Unnamed'),false);
});
test('a separately linked breccia source is not promoted to a preferred source in the group table',()=>{
  const links=candidateRelations(group('group 5-2'),data.craters);
  assert.equal(group('group 5-2').preferred_candidate,null);
  assert.equal(links.find(r=>r.crater.name==='Karratha').kind,'linked');
});
test('unlocated ALH 84001 remains unlocated and inputs are not mutated',()=>{
  const before=JSON.stringify(data);
  const sample=data.samples.find(s=>s.name==='ALH 84001');
  assert.deepEqual(candidateRelations(group(sampleGroup(sample)),data.craters),[]);
  assert.deepEqual(candidateRelations(undefined,data.craters),[]);
  assert.equal(JSON.stringify(data),before);
});
