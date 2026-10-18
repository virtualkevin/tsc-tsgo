import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,copyFileSync} from 'node:fs';
import {captureGoSources,hashFile} from '../../../scripts/build-provenance.mjs';
const root=process.cwd(),dir=root+'/benchmarks/profiles/runtime-small-string';
const config=JSON.parse(readFileSync(dir+'/screen.json')),source=config.expected.baseline.source;
for(const name of ['conformance','native','units']){
 const r=JSON.parse(readFileSync(`/tmp/tsc-runtime-small-string/${name}/validation.json`));
 assert.equal(r.passed,true);assert.equal(r.sourceSha256,source);
}
assert.equal(JSON.parse(readFileSync('/tmp/tsc-runtime-small-string/validation/report.json')).passed,true);
assert.equal(captureGoSources(root+'/packages/tsc-go').sha256,source);
for(const e of Object.values(config.expected)){assert.equal(hashFile(e.path),e.sha256);assert.equal(hashFile(e.path+'.provenance.json'),e.sidecarSha256);}
assert.equal(hashFile(config.runtimeInputs.runtimeSource),config.runtimeInputs.beforeSha256);
assert.equal(hashFile(dir+'/runtime_faststr.go.txt'),config.runtimeInputs.afterSha256);
assert.equal(hashFile(dir+'/overlay.json'),config.overlaySha256);
for(const suffix of ['', '.provenance.json'])copyFileSync(config.expected.baseline.path+suffix,root+'/packages/tsc-go/dist/tsc-go'+suffix);
assert.equal(hashFile(root+'/packages/tsc-go/dist/tsc-go'),config.expected.baseline.sha256);
writeFileSync(dir+'/restoration.json',JSON.stringify({status:'passed',compilerSourceUnchanged:source,installedRuntimeSourceUnchanged:config.runtimeInputs.beforeSha256,binarySha256:hashFile(root+'/packages/tsc-go/dist/tsc-go')},null,2)+'\n',{flag:'wx'});
