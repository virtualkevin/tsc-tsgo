import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {load,hashFile,median,validateReport,capture,config,configPath} from './common.mjs';
const dir=resolve(process.argv[2]),summary=load(join(dir,'summary.json'));
assert.equal(summary.status,'passed');assert.equal(config.name,'same-binary-aa');assert.deepEqual(capture(),summary.snapshot);
for(const [path,h] of Object.entries(summary.controllerFiles))assert.equal(hashFile(path),h);
const results=[];
for(const run of summary.runs){assert.equal(run.status,'passed');assert.equal(hashFile(run.output),run.reportSha256);const report=load(run.output);const group=config.groups.find(g=>g.name===run.name);assert.deepEqual(validateReport(report,group,summary.snapshot,summary.unsetEnvironment),run.results);
 for(const p of report.projects){const ratios=p.pairs.map(x=>x.baseline/x.candidate);const logRatios=ratios.map(Math.log);const m=median(logRatios);results.push({...run.results.find(x=>x.name===p.name),pairedRatios:ratios,pairedMedian:median(ratios),pairedMin:Math.min(...ratios),pairedMax:Math.max(...ratios),medianAbsoluteLogDeviation:median(logRatios.map(x=>Math.abs(x-m))),pairOrders:p.pairs.map(x=>x.order),secondLabelFasterPairs:ratios.filter(x=>x>1).length});}}
assert.deepEqual(results.map(x=>x.name),['typeorm','trpc','vscode','sentry']);
const out=join(dir,'recording');mkdirSync(out);
const proposal={status:'passed',kind:'same-binary calibration, not a candidate speedup',summarySha256:hashFile(join(dir,'summary.json')),configSha256:hashFile(configPath),results,limitations:['Both labels execute the identical binary; any non-unit ratio is measurement variation.','Fixed finite within-session sample; no confidence/independence/stationarity claim.','All samples retained; no inference from correctness durations or historical timings.']};
writeFileSync(join(out,'proposal.json'),JSON.stringify(proposal,null,2)+'\n');
const labels={typeorm:'TypeORM source + tests; Node20 compatibility',trpc:'tRPC server',vscode:'VS Code client',sentry:'Sentry frontend'};
const rows=results.map(r=>`| Same-binary A/A calibration (capture ${summary.repositoryStartingHead.slice(0,7)}); default settings; GNU time wrapped | ${labels[r.name]} | Saturated Go; same binary both labels | ${r.baselineMedianMs.toFixed(2)} | ${r.candidateMedianMs.toFixed(2)} | ${r.baselineOverCandidate.toFixed(3)}× | ${r.runs} | Calibration only, not an optimization; identical ${r.files.toLocaleString('en-US')} inputs; clean diagnostics; median peak RSS labels A/B ${r.baselineMedianRssMiB.toFixed(1)}/${r.candidateMedianRssMiB.toFixed(1)} MiB; paired median ${r.pairedMedian.toFixed(3)}; [samples](benchmarks/results/indexed-symbol-aa/${r.name==='typeorm'||r.name==='trpc'?'small':'large'}.json). |`).join('\n')+'\n';
writeFileSync(join(out,'PERF.rows.md'),rows);
console.log(JSON.stringify(results.map(r=>({workload:r.name,ratioOfMedians:r.baselineOverCandidate,pairedMedian:r.pairedMedian,pairRange:[r.pairedMin,r.pairedMax],rss:[r.baselineMedianRssMiB,r.candidateMedianRssMiB]})),null,2));
