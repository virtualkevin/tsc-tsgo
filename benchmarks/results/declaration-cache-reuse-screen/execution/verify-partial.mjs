import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
import {load,capture,hashFile,validateReport,config} from '/home/dev/tssss/tsc-tsgo/benchmarks/profiles/declaration-cache-reuse/common-screen.mjs';
import {normalizeProject} from '/home/dev/tssss/tsc-tsgo/benchmarks/profiles/direct-member-confirmation/confirmation-stats.mjs';
const dir=process.argv[2],s=load(dir+'/summary.json');
assert.equal(s.status,'failed');assert.match(s.error,/cancellation=SIGTERM; leftoverMarkedProcesses=0/);
assert.deepEqual(capture(),s.snapshot);
for(const [p,h] of Object.entries(s.controllerFiles))assert.equal(hashFile(p),h);
const run=s.runs.find(r=>r.name==='small');assert.equal(run.status,'passed');assert.equal(hashFile(run.output),run.reportSha256);
const report=load(run.output),group=config.groups.find(g=>g.name==='small');assert.equal(report.repositoryCommit,s.repositoryStartingHead);
assert.deepEqual(validateReport(report,group,s.snapshot,s.unsetEnvironment),run.results);
const results=report.projects.map(p=>normalizeProject(p,{unchanged:'baseline',optimized:'candidate'},group.runs));

const result={status:'verified-partial',captureHead:s.repositoryStartingHead,summarySha256:hashFile(dir+'/summary.json'),reportSha256:run.reportSha256,results,decision:'Incomplete screen: completed small workload evidence only. No full-suite acceptance, aggregate, large-workload result or promotion claim.'};
writeFileSync(dir+'/partial-decision.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
