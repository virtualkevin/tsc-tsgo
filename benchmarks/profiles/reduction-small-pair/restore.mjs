import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,copyFileSync,unlinkSync} from 'node:fs';
import {captureGoSources,hashFile} from '../../../scripts/build-provenance.mjs';
const root=process.cwd(),dir=root+'/benchmarks/profiles/reduction-small-pair';
const config=JSON.parse(readFileSync(dir+'/screen.json'));
const expected=config.expected;
for(const name of ['conformance','native','units']){
 const report=JSON.parse(readFileSync(`/tmp/tsc-reduction-small-pair/${name}/validation.json`));
 assert.equal(report.passed,true);assert.equal(report.sourceSha256,expected.candidate.source);
}
const current=captureGoSources(root+'/packages/tsc-go');assert.equal(current.sha256,expected.candidate.source);
for(const e of Object.values(expected)){assert.equal(hashFile(e.path),e.sha256);assert.equal(hashFile(e.path+'.provenance.json'),e.sidecarSha256);}
const production='packages/tsc-go/internal/checker/lazy_properties.go';
const test='packages/tsc-go/internal/checker/reduction_small_pair_test.go';
assert.equal(hashFile(root+'/'+test),hashFile(dir+'/reduction_small_pair_test.go'));
const old=spawnSync('git',['show','2a121e4:'+production],{encoding:'utf8',maxBuffer:4*1024*1024});assert.equal(old.status,0);
writeFileSync(root+'/'+production,old.stdout);unlinkSync(root+'/'+test);
const after=captureGoSources(root+'/packages/tsc-go');assert.equal(after.sha256,expected.baseline.source);
for(const suffix of ['', '.provenance.json'])copyFileSync(expected.baseline.path+suffix,root+'/packages/tsc-go/dist/tsc-go'+suffix);
assert.equal(hashFile(root+'/packages/tsc-go/dist/tsc-go'),expected.baseline.sha256);
config.workspaceSource=expected.baseline.source;
writeFileSync(dir+'/screen.json',JSON.stringify(config,null,2)+'\n');
writeFileSync(dir+'/restoration.json',JSON.stringify({status:'passed',before:current.sha256,after:after.sha256,binarySha256:hashFile(root+'/packages/tsc-go/dist/tsc-go'),sourceRevision:after.revision},null,2)+'\n',{flag:'wx'});
