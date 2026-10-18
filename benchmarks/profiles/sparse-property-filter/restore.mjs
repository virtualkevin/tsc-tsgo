import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,copyFileSync,unlinkSync} from 'node:fs';
import {captureGoSources,hashFile} from '../../../scripts/build-provenance.mjs';
const root=process.cwd(),dir=root+'/benchmarks/profiles/sparse-property-filter';
const config=JSON.parse(readFileSync(dir+'/screen.json')),expected=config.expected;
for(const name of ['conformance','native','units','wide-v3']){
 const report=JSON.parse(readFileSync(`/tmp/tsc-sparse-property-filter/${name}/validation.json`));
 assert.equal(report.passed,true);assert.equal(report.sourceSha256,expected.candidate.source);
}
const before=captureGoSources(root+'/packages/tsc-go');assert.equal(before.sha256,expected.candidate.source);
for(const e of Object.values(expected)){assert.equal(hashFile(e.path),e.sha256);assert.equal(hashFile(e.path+'.provenance.json'),e.sidecarSha256);}
for(const p of ['internal/checker/sparse_property_filter.go','internal/checker/sparse_property_filter_test.go']) assert.equal(hashFile(root+'/packages/tsc-go/'+p),hashFile(dir+'/'+p.split('/').at(-1)));
const production='packages/tsc-go/internal/checker/relater.go';
const old=spawnSync('git',['show','0ac2b5f:'+production],{encoding:'utf8',maxBuffer:16*1024*1024});assert.equal(old.status,0);
writeFileSync(root+'/'+production,old.stdout);
for(const p of ['internal/checker/sparse_property_filter.go','internal/checker/sparse_property_filter_test.go'])unlinkSync(root+'/packages/tsc-go/'+p);

const after=captureGoSources(root+'/packages/tsc-go');assert.equal(after.sha256,expected.baseline.source);
for(const suffix of ['', '.provenance.json'])copyFileSync(expected.baseline.path+suffix,root+'/packages/tsc-go/dist/tsc-go'+suffix);
assert.equal(hashFile(root+'/packages/tsc-go/dist/tsc-go'),expected.baseline.sha256);
config.workspaceSource=expected.baseline.source;writeFileSync(dir+'/screen.json',JSON.stringify(config,null,2)+'\n');
writeFileSync(dir+'/restoration.json',JSON.stringify({status:'passed',before:before.sha256,after:after.sha256,binarySha256:hashFile(root+'/packages/tsc-go/dist/tsc-go'),sourceRevision:after.revision},null,2)+'\n',{flag:'wx'});
