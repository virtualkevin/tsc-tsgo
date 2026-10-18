import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,copyFileSync,unlinkSync} from 'node:fs';
import {captureGoSources,hashFile} from '../../../scripts/build-provenance.mjs';

const root=process.cwd(),dir=root+'/benchmarks/profiles/lazy-identifier-names';
const config=JSON.parse(readFileSync(dir+'/screen.json')),expected=config.expected;
for(const name of ['conformance','native','units','instrumented','services']) {
 const report=JSON.parse(readFileSync(`/tmp/tsc-lazy-identifier-names/${name}/validation.json`));
 assert.equal(report.passed,true);assert.equal(report.sourceSha256,expected.candidate.source);
}
const before=captureGoSources(root+'/packages/tsc-go');assert.equal(before.sha256,expected.candidate.source);
assert.equal(config.sourceDifference.length,5);
const added=config.sourceDifference.filter(d=>!d.before).map(d=>d.path);
assert.deepEqual(added,['packages/tsc-go/internal/ast/lazy_identifier_names_test.go','packages/tsc-go/internal/parser/lazy_identifier_names_test.go']);
for(const e of Object.values(expected)) {
 assert.equal(hashFile(e.path),e.sha256);assert.equal(hashFile(e.path+'.provenance.json'),e.sidecarSha256);
}
// Validate and stage every restore byte before mutating any file.
const changes=[];
for(const delta of config.sourceDifference) {
 assert.ok(delta.path.startsWith('packages/tsc-go/internal/'));assert.ok(!delta.path.includes('..'));
 assert.ok(delta.after);assert.equal(hashFile(root+'/'+delta.path),delta.after.sha256);
 if(delta.before) {
  const old=spawnSync('git',['show','1a3c459:'+delta.path],{maxBuffer:32*1024*1024});
  assert.equal(old.status,0);assert.ok(!old.error);
  const {createHash}=await import('node:crypto');
  assert.equal(createHash('sha256').update(old.stdout).digest('hex'),delta.before.sha256);
  changes.push({path:root+'/'+delta.path,data:old.stdout});
 } else {
  assert.equal(hashFile(root+'/'+delta.path),hashFile(dir+'/candidate-source/'+delta.path.slice('packages/tsc-go/internal/'.length)));
  changes.push({path:root+'/'+delta.path,data:null});
 }
}
for(const change of changes) {
 if(change.data===null)unlinkSync(change.path);else writeFileSync(change.path,change.data);
}
const after=captureGoSources(root+'/packages/tsc-go');assert.equal(after.sha256,expected.baseline.source);
for(const suffix of ['', '.provenance.json'])copyFileSync(expected.baseline.path+suffix,root+'/packages/tsc-go/dist/tsc-go'+suffix);
assert.equal(hashFile(root+'/packages/tsc-go/dist/tsc-go'),expected.baseline.sha256);
config.workspaceSource=expected.baseline.source;writeFileSync(dir+'/screen.json',JSON.stringify(config,null,2)+'\n');
writeFileSync(dir+'/restoration.json',JSON.stringify({status:'passed',before:before.sha256,after:after.sha256,binarySha256:hashFile(root+'/packages/tsc-go/dist/tsc-go'),sourceRevision:after.revision},null,2)+'\n',{flag:'wx'});
