// Prepared during confirmation; execute only after both independent suites finish.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,copyFileSync,chmodSync,statSync,existsSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {captureGoSources,readBuildProvenance,hashFile} from '/home/dev/tssss/tsc-tsgo/scripts/build-provenance.mjs';
import {normalizeProject,evaluateResults} from '/home/dev/tssss/tsc-tsgo/benchmarks/profiles/node-pointer-confirmation/confirmation-stats.mjs';
const root='/home/dev/tssss/tsc-tsgo';
const load=p=>JSON.parse(readFileSync(p,'utf8'));
const output='/tmp/tsc-node-pointer-retention/retention.json';
assert.ok(!existsSync(output),'Retention report already exists');
const candidateDir=root+'/benchmarks/profiles/node-pointer-candidate';
const screen=load(candidateDir+'/screen.json');
const records=[];
for(const direction of ['forward','reverse']) {
 const base=root+'/benchmarks/results/node-pointer-confirm-'+direction;
 const configPath=root+'/benchmarks/profiles/node-pointer-confirmation/'+direction+'.json';
 const config=load(configPath), summary=load(base+'/summary.json'), proposal=load(base+'/recording/proposal.json');
 assert.equal(proposal.status,'passed');assert.equal(proposal.passesThisConfirmation,true);
 assert.equal(summary.status,'passed');
 assert.equal(hashFile(base+'/summary.json'),proposal.summarySha256);
 assert.equal(hashFile(configPath),proposal.configSha256);
 assert.equal(hashFile(candidateDir+'/COMPARISON_POLICY.md'),proposal.comparisonPolicySha256);
 assert.equal(hashFile(root+'/benchmarks/profiles/node-pointer-confirmation/confirmation-stats.mjs'),proposal.statsModuleSha256);
 const roles=direction==='forward'?{unchanged:'baseline',optimized:'candidate'}:{unchanged:'candidate',optimized:'baseline'};
 assert.deepEqual(config.canonicalRoles,roles);assert.deepEqual(proposal.canonicalRoles,roles);
 assert.equal(config.expected[roles.unchanged].sha256,screen.expected.baseline.sha256);
 assert.equal(config.expected[roles.optimized].sha256,screen.expected.candidate.sha256);
 const results=[];
 assert.equal(summary.runs.length,2);
 for(const run of summary.runs) {
  assert.equal(run.status,'passed');assert.equal(hashFile(run.output),run.reportSha256);
  const raw=load(run.output), count=run.name==='small'?19:11;
  assert.equal(run.runs,count);
  for(const project of raw.projects)results.push(normalizeProject(project,roles,count));
 }
 assert.deepEqual(results.map(r=>r.name),['typeorm','trpc','vscode','sentry']);
 assert.deepEqual(results,proposal.results);
 const computed=evaluateResults(results);
 assert.deepEqual(computed.aggregates,proposal.aggregates);assert.deepEqual(computed.gates,proposal.gates);
 assert.ok(Object.values(computed.gates).every(Boolean),'Each confirmation must pass independently');
 records.push({direction,summarySha256:hashFile(base+'/summary.json'),proposalSha256:hashFile(base+'/recording/proposal.json'),...computed});
}
const validations={};
for(const name of ['conformance','native']) {
 const p=root+'/benchmarks/validation/node-pointer-'+name+'.json';
 const report=load(p);assert.equal(report.passed,true);
 assert.equal(report.sourceSha256,screen.expected.candidate.source);
 if(name==='conformance')assert.equal(report.sourceAndPinsUnchanged,true);
 else {
  assert.equal(report.sourceAndBinariesUnchanged,true);
  assert.equal(report.binaryAndComparatorHashes[screen.expected.candidate.path],screen.expected.candidate.sha256);
  for(const [path,sha] of Object.entries(report.binaryAndComparatorHashes))assert.equal(hashFile(path),sha);
 }
 validations[name]=hashFile(p);
}
const before=captureGoSources(root+'/packages/tsc-go');
assert.equal(before.sha256,screen.expected.baseline.source);
const b=screen.expected.candidate;
assert.equal(hashFile(b.path),b.sha256);
const provenance=readBuildProvenance(b.path,b.sha256);
assert.equal(provenance.status,'verified');assert.equal(provenance.sidecarSha256,b.sidecarSha256);
const target=root+'/packages/tsc-go/dist/tsc-go';
assert.equal(hashFile(target),screen.expected.baseline.sha256);
for(const args of [['apply','--check',candidateDir+'/candidate.patch'],['apply',candidateDir+'/candidate.patch']]) {
 const r=spawnSync('git',args,{cwd:root,encoding:'utf8'});assert.equal(r.status,0,r.stderr);
}
const after=captureGoSources(root+'/packages/tsc-go');
assert.equal(after.sha256,b.source);assert.deepEqual(after.files,provenance.metadata.source.files);
copyFileSync(b.path,target);chmodSync(target,statSync(b.path).mode&0o777);
copyFileSync(b.path+'.provenance.json',target+'.provenance.json');
assert.equal(hashFile(target),b.sha256);
writeFileSync(output,JSON.stringify({status:'retained',beforeSource:before.sha256,afterSource:after.sha256,binarySha256:b.sha256,records,validations,patchSha256:hashFile(candidateDir+'/candidate.patch'),controllerSha256:hashFile(fileURLToPath(import.meta.url)),limitation:'Go/Go confirmation only; native-relative 10x remains unproven.'},null,2)+'\n',{flag:'wx'});
console.log(output);
