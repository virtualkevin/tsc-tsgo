// Diagnostic rollback helper. Run only after both frozen confirmations are recorded.
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,unlinkSync,copyFileSync,chmodSync,statSync,existsSync} from 'node:fs';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {captureGoSources,readBuildProvenance,hashFile} from '/home/dev/tssss/tsc-tsgo/scripts/build-provenance.mjs';
const root='/home/dev/tssss/tsc-tsgo',packageRoot=join(root,'packages/tsc-go');
const baselineRevision='e94bc1f0dd96ac097f1941144df7fb46e6b86fb7';
const baselineBinary=join(packageRoot,'dist/tsc-go-keybuilder-saturated'),defaultBinary=join(packageRoot,'dist/tsc-go');
const baselineSha='2bdcca53f630535846054eada84cae8afaa32b4faab21de029eca41c79e26303',indexedSha='3c3b18fa41dfaad20ea334e4f425ebcbfada4d7cdd2547865007714ba55194a5';
const baselineSource='78b76607d79c501f3c35fcbbec5a880561699244c7d65daab6f27f42b22f9337',indexedSource='c8a7bd150f663db3b46e1262e5e39b0865da004e3aeced71f6ead8a9af96589e';
const load=p=>JSON.parse(readFileSync(p,'utf8'));
assert.ok(process.argv.length===2||(process.argv.length===3&&process.argv[2]==='--apply'));
const apply=process.argv[2]==='--apply';
const output=join(root,'benchmarks/validation/indexed-symbol-restoration.json');
if(apply)assert.ok(!existsSync(output),'Do not overwrite restoration evidence');
const configPath=join(root,'benchmarks/profiles/indexed-symbol-confirmation/indexed-confirm-forward.json'),config=load(configPath);
assert.equal(config.expected.baseline.sha256,baselineSha);assert.equal(config.expected.candidate.sha256,indexedSha);
assert.equal(hashFile(join(root,'benchmarks/results/indexed-symbol-aa/COMPARISON_POLICY.md')),config.comparisonPolicySha256);
const evidence=['forward','reverse'].map(direction=>{
 const path=join(root,`benchmarks/results/indexed-symbol-confirm-${direction}/recording/proposal.json`),p=load(path);
 assert.equal(p.status,'passed');assert.equal(p.experiment,`indexed-confirm-${direction}`);assert.equal(p.comparisonPolicySha256,config.comparisonPolicySha256);
 assert.deepEqual(Object.keys(p.gates).sort(),['allWorkloadMedianRssAtMost105','allWorkloadSummariesAtLeast098','bothAggregatesAtLeast101']);
 for(const value of Object.values(p.gates))assert.equal(typeof value,'boolean');
 assert.equal(p.passesThisConfirmation,Object.values(p.gates).every(Boolean));
 assert.deepEqual(p.results.map(r=>[r.name,r.runs]),[['typeorm',19],['trpc',19],['vscode',11],['sentry',11]]);
 const summary=join(root,`benchmarks/results/indexed-symbol-confirm-${direction}/summary.json`);
 assert.equal(hashFile(summary),p.summarySha256);assert.equal(load(summary).status,'passed');
 assert.equal(hashFile(join(root,`benchmarks/profiles/indexed-symbol-confirmation/indexed-confirm-${direction}.json`)),p.configSha256);
 return {path,sha256:hashFile(path),passes:p.passesThisConfirmation};
});
assert.ok(evidence.some(e=>!e.passes),'Only a failed confirmation authorizes this restoration');
assert.equal(hashFile(baselineBinary),baselineSha);assert.equal(hashFile(defaultBinary),indexedSha);
const baselineProvenance=readBuildProvenance(baselineBinary,baselineSha),defaultProvenance=readBuildProvenance(defaultBinary,indexedSha);
assert.equal(baselineProvenance.status,'verified');assert.equal(defaultProvenance.status,'verified');
assert.equal(baselineProvenance.sidecarSha256,config.expected.baseline.sidecarSha256);assert.equal(defaultProvenance.sidecarSha256,config.expected.candidate.sidecarSha256);
assert.equal(baselineProvenance.metadata.source.sha256,baselineSource);assert.equal(defaultProvenance.metadata.source.sha256,indexedSource);
const before=captureGoSources(packageRoot);assert.equal(before.sha256,indexedSource);
const current=new Map(before.files.map(f=>[f.path,f]));
const prepared=config.sourceDifference.map(delta=>{
 assert.ok(delta.path.startsWith('packages/tsc-go/internal/'));
 assert.deepEqual(current.get(delta.path),delta.after,'Unexpected user/source change; stop before writing');
 if(delta.before===null)return {path:delta.path,remove:true};
 const r=spawnSync('git',['show',`${baselineRevision}:${delta.path}`],{cwd:root,encoding:null,timeout:10000,maxBuffer:16*1024*1024});
 assert.equal(r.status,0);assert.ok(!r.error&&!r.signal);assert.equal(r.stderr.length,0);
 assert.equal(createHash('sha256').update(r.stdout).digest('hex'),delta.before.sha256);
 assert.equal(delta.before.executable,delta.after.executable);
 return {path:delta.path,remove:false,content:r.stdout};
});
assert.equal(prepared.length,9);assert.equal(prepared.filter(p=>p.remove).length,6);
const report={status:apply?'restoring':'preflight-passed',recordedAt:new Date().toISOString(),scriptSha256:hashFile(fileURLToPath(import.meta.url)),baselineRevision,evidence,before:{revision:before.revision,sha256:before.sha256,fileCount:before.files.length,binarySha256:indexedSha},operations:prepared.map(({path,remove})=>({path,operation:remove?'remove candidate-added file':'restore baseline bytes'}))};
if(apply){
 for(const item of prepared){const path=join(root,item.path);if(item.remove)unlinkSync(path);else writeFileSync(path,item.content);}
 const after=captureGoSources(packageRoot);assert.equal(after.sha256,baselineSource);assert.deepEqual(after.files,baselineProvenance.metadata.source.files);
 copyFileSync(baselineBinary,defaultBinary);chmodSync(defaultBinary,statSync(baselineBinary).mode&0o777);
 copyFileSync(baselineBinary+'.provenance.json',defaultBinary+'.provenance.json');
 assert.equal(hashFile(defaultBinary),baselineSha);assert.equal(hashFile(defaultBinary+'.provenance.json'),baselineProvenance.sidecarSha256);
 const restored=readBuildProvenance(defaultBinary,baselineSha);assert.equal(restored.status,'verified');assert.equal(restored.metadata.source.sha256,after.sha256);
 report.after={revision:after.revision,sha256:after.sha256,fileCount:after.files.length,binarySha256:baselineSha,sidecarSha256:restored.sidecarSha256};report.status='restored';
 writeFileSync(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
}
console.log(JSON.stringify(report,null,2));
