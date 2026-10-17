import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
import {join,resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {root,load,hashFile,validateReport,capture,config,configPath,median} from './common-native.mjs';
assert.equal(config.name,'native-node-pointer');
assert.deepEqual(config.groups,[{name:'small',projects:['typeorm','trpc'],runs:9},{name:'large',projects:['vscode','sentry'],runs:5}]);
const dir=resolve(process.argv[2]),summary=load(join(dir,'summary.json'));
assert.equal(summary.status,'passed');assert.deepEqual(capture(),summary.snapshot);
for(const [path,h] of Object.entries(summary.controllerFiles))assert.equal(hashFile(path),h);
const results=[];
for(const run of summary.runs){
 assert.equal(run.status,'passed');assert.equal(hashFile(run.output),run.reportSha256);
 const report=load(run.output),group=config.groups.find(g=>g.name===run.name);
 assert.deepEqual(validateReport(report,group,summary.snapshot,summary.unsetEnvironment),run.results);
 for(const p of report.projects){
  const pairedRatios=p.pairs.map(pair=>pair.baseline/pair.candidate);
  results.push({...run.results.find(r=>r.name===p.name),pairedRatios,pairedMedian:median(pairedRatios),pairedMin:Math.min(...pairedRatios),pairedMax:Math.max(...pairedRatios),goFasterPairs:pairedRatios.filter(r=>r>1).length});
 }
}
assert.deepEqual(results.map(r=>r.name),['typeorm','trpc','vscode','sentry']);
const proposal={status:'passed',experiment:config.name,recorderSha256:hashFile(fileURLToPath(import.meta.url)),summarySha256:hashFile(join(dir,'summary.json')),configSha256:hashFile(configPath),ratioMeaning:'original native time / retained Go time',results,allMeasuredWorkloadsAtLeast10InBothSummaries:results.every(r=>r.baselineOverCandidate>=10&&r.pairedMedian>=10),limitations:['Finite fresh-process default-settings measurement; not a statistical-confidence claim.','Original native artifact is SHA-pinned but lacks a historical build provenance sidecar.','Native and Go default worker counts are not assumed equal.','These four clean workloads do not substitute for compiler correctness validation or establish universal performance.','No ratios multiplied across historical runs.']};
const out=join(dir,'recording');mkdirSync(out);writeFileSync(join(out,'proposal.json'),JSON.stringify(proposal,null,2)+'\n');
const labels={typeorm:'TypeORM source + tests; Node20 compatibility',trpc:'tRPC server',vscode:'VS Code client',sentry:'Sentry frontend'};
const rows=results.map(r=>`| Direct native milestone (${config.name}; capture ${summary.repositoryStartingHead.slice(0,7)}); default settings; GNU time wrapped | ${labels[r.name]} | Original native tsc-ts | ${r.baselineMedianMs.toFixed(2)} | ${r.candidateMedianMs.toFixed(2)} | ${r.baselineOverCandidate.toFixed(3)}× | ${r.runs} | Identical ${r.files.toLocaleString('en-US')} inputs; clean diagnostics; median peak RSS native/Go ${r.baselineMedianRssMiB.toFixed(1)}/${r.candidateMedianRssMiB.toFixed(1)} MiB; paired median ${r.pairedMedian.toFixed(3)}; native build sidecar absent; [samples](${relative(root,dir)}/${r.name==='typeorm'||r.name==='trpc'?'small':'large'}.json). |`).join('\n')+'\n';
writeFileSync(join(out,'PERF.rows.md'),rows);
console.log(JSON.stringify(proposal,null,2));
