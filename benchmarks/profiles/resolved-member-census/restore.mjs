import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,copyFileSync,unlinkSync} from 'node:fs';
import {captureGoSources,hashFile} from '../../../scripts/build-provenance.mjs';
const root=process.cwd(),dir=root+'/benchmarks/profiles/resolved-member-census';
const source='6ec99f9289783f1dfa77d1d732f26a591ae0276327a62ad348ff70d10dc9eb34';
const baseline='216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd';
const units=JSON.parse(readFileSync('/tmp/tsc-resolved-member-census/units/validation.json'));
const capture=JSON.parse(readFileSync('/tmp/tsc-resolved-member-census/capture/report.json'));
assert.equal(units.passed,true);assert.equal(units.sourceSha256,source);assert.equal(capture.status,'passed');assert.equal(capture.source.sha256,source);
assert.equal(captureGoSources(root+'/packages/tsc-go').sha256,source);
for(const name of ['resolved_member_census.go','resolved_member_census_test.go'])assert.equal(hashFile(root+'/packages/tsc-go/internal/checker/'+name),hashFile(dir+'/'+name));
const original=new Map();
for(const p of ['packages/tsc-go/internal/checker/checker.go','packages/tsc-go/cmd/tsgo/main.go','packages/tsc-go/internal/checker/pending_members.go']){
 const r=spawnSync('git',['show','f81de0e:'+p],{encoding:'utf8',maxBuffer:16*1024*1024});assert.equal(r.status,0);original.set(p,r.stdout);
}
const bin=root+'/packages/tsc-go/dist/tsc-go-node-pointer';assert.equal(hashFile(bin),'8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f');assert.equal(hashFile(bin+'.provenance.json'),'76e6c4f05d244f4f3f1cd562950bbc3388716b139176ee3583ecc912e3a2bca2');
for(const [p,data] of original)writeFileSync(root+'/'+p,data);
for(const name of ['resolved_member_census.go','resolved_member_census_test.go'])unlinkSync(root+'/packages/tsc-go/internal/checker/'+name);
assert.equal(captureGoSources(root+'/packages/tsc-go').sha256,baseline);
for(const suffix of ['', '.provenance.json'])copyFileSync(bin+suffix,root+'/packages/tsc-go/dist/tsc-go'+suffix);
writeFileSync(dir+'/restoration.json',JSON.stringify({status:'passed',before:source,after:baseline,binarySha256:hashFile(root+'/packages/tsc-go/dist/tsc-go')},null,2)+'\n',{flag:'wx'});
