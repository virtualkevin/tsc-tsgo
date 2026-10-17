// Validate completed reports and write proposed documentation ONLY under /tmp.
import assert from 'node:assert/strict';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {join,resolve,relative} from 'node:path';
import {root,expected,groups,load,hashFile,capture,validateReport,clearNames} from './cjs-prepass-ab-common.mjs';
assert.ok(process.argv[2],'Usage: node /tmp/record-cjs-prepass-ab.mjs COMPLETED_RESULTS_DIRECTORY [NEW_TMP_PROPOSAL_DIRECTORY]');
const directory=resolve(process.argv[2]),output=resolve(process.argv[3]??`/tmp/cjs-prepass-ab-proposed-${Date.now()}-${process.pid}`);
assert.ok(output.startsWith('/tmp/')&&output!=='/tmp/','Recorder may write only a new directory under /tmp');
const summaryPath=join(directory,'summary.json'),summary=load(summaryPath),summarySha=hashFile(summaryPath);
assert.equal(summary.status,'passed');assert.deepEqual(summary.expected,expected);assert.deepEqual(summary.snapshot,capture(),'Binary/sidecar/harness/manifest changed since measurement');
assert.deepEqual(Object.keys(summary.controllerFiles).sort(),['/tmp/cjs-prepass-ab-common.mjs','/tmp/run-cjs-prepass-ab.mjs']);
assert.deepEqual(summary.unsetEnvironment,[...new Set(summary.unsetEnvironment)].sort());
for(const key of clearNames({}))assert.ok(summary.unsetEnvironment.includes(key),`Missing runtime/profile clear: ${key}`);
for(const [p,sha] of Object.entries(summary.controllerFiles))assert.equal(hashFile(p),sha,'Controller source changed');
assert.equal(summary.runs.length,groups.length);assert.equal(summary.totalTimeoutMs,1800000);assert.equal(summary.perInvocationTimeoutMs,180000);
const perfPath=join(root,'PERF.md'),notesPath=join(root,'NOTES.md');
const perf=readFileSync(perfPath,'utf8'),notes=readFileSync(notesPath,'utf8');
const lines=perf.trim().split('\n');assert.equal(lines[0].split('|').length-2,8);assert.ok(lines.every(l=>l.startsWith('|')&&l.endsWith('|')));
const labels={typeorm:'TypeORM source + tests; Node20 compatibility',trpc:'tRPC server',vscode:'VS Code client',sentry:'Sentry frontend'};
assert.match(summary.repositoryStartingHead,/^[a-f0-9]{40}$/);
const stage=`CJS assignment prepass guard (capture ${summary.repositoryStartingHead.slice(0,7)}); default GC/scheduler/checkers; GNU time wrapped`;
const marker='CJS assignment prepass guard direct Go/Go wrapped A/B (binary a6da693d)';
assert.ok(!perf.includes(stage),'Duplicate PERF stage');assert.ok(!notes.includes(marker),'Duplicate NOTES marker');
const link=p=>{const rel=relative(root,p);return encodeURI(rel.startsWith('benchmarks/')?rel:p).replaceAll('(','%28').replaceAll(')','%29');};
const rows=[],results=[],reportHashes=[];
for(const [index,group] of groups.entries()){
 const run=summary.runs[index],reportPath=join(directory,`${group.name}.json`);
 assert.equal(run.name,group.name);assert.equal(run.status,'passed');assert.equal(resolve(run.output),reportPath);assert.equal(run.runs,group.runs);assert.deepEqual(run.projects,group.projects);assert.equal(hashFile(reportPath),run.reportSha256);
 const expectedCommand=[process.execPath,'benchmarks/run.mjs','--baseline',expected.baseline.path,'--candidate',expected.candidate.path,'--projects',group.projects.join(','),'--runs',String(group.runs),'--warmups','1','--timeout','180000','--measure-rss','--output',reportPath,...summary.unsetEnvironment.flatMap(k=>['--unset-env',k])];
 assert.deepEqual(run.command,expectedCommand);
 const report=load(reportPath);assert.equal(report.repositoryCommit,summary.repositoryStartingHead);const verified=validateReport(report,group,summary.snapshot,summary.unsetEnvironment);assert.deepEqual(run.results,verified);reportHashes.push({path:reportPath,sha256:run.reportSha256});
 for(const p of verified){
  results.push(p);
  const evidence=`Identical ${p.files.toLocaleString('en-US')} inputs; clean diagnostics; median peak RSS baseline/candidate ${p.baselineMedianRssMiB.toFixed(1)}/${p.candidateMedianRssMiB.toFixed(1)} MiB; direct Go/Go only; wrapped timing not comparable with historical unwrapped; [samples](${link(reportPath)}).`;
  const cells=[stage,labels[p.name],'Go PointerLinkStore (`849d873`)',p.baselineMedianMs.toFixed(2),p.candidateMedianMs.toFixed(2),`${p.baselineOverCandidate.toFixed(3)}×`,String(group.runs),evidence];assert.equal(cells.length,8);assert.ok(cells.every(s=>!s.includes('|')&&!s.includes('\n')));rows.push(`| ${cells.join(' | ')} |`);
 }
}
assert.equal(rows.length,4);assert.deepEqual(results.map(p=>p.name).sort(),Object.keys(labels).sort());
const note=`- ${marker}: preserved PointerLinkStore Go SHA256 ${expected.baseline.sha256} versus CJS prepass guard SHA256 ${expected.candidate.sha256}, source ${expected.candidate.source}; capture repository HEAD ${summary.repositoryStartingHead}. The sole production source difference gates the module.exports assignment prepass on CommonJSModuleIndicator; expando-member collection remains unconditional. The only other source-manifest change is an added JSX diagnostic regression test. Build/toolchain settings match; seven alternating pairs for TypeORM/tRPC and three for VS Code/Sentry, one warmup each, default GC/scheduler/checkers on both sides. ${results.map(p=>`${p.name} ${p.baselineOverCandidate.toFixed(3)}×`).join(', ')}. Ratios above one favor the candidate. Both sides were measured under the same GNU time wrapper; these timings cannot be compared with historical unwrapped values. RSS is command peak resident memory, not aggregate tree memory or Go heap. Input/content, clean diagnostic, actual argument/environment, alternating-order, binary/sidecar, wrapper and sample-summary integrity gates passed. This direct Go/Go experiment does not measure the original native target or establish 10× performance, and timing gates do not replace separate compiler conformance/API/race validation. [Summary](${link(summaryPath)}).\n`;
assert.equal(hashFile(summaryPath),summarySha);assert.equal(readFileSync(perfPath,'utf8'),perf);assert.equal(readFileSync(notesPath,'utf8'),notes);
mkdirSync(output); // Refuse overwrites, including earlier proposals.
writeFileSync(join(output,'PERF.rows.md'),rows.join('\n')+'\n',{flag:'wx'});writeFileSync(join(output,'NOTES.entry.md'),note,{flag:'wx'});
writeFileSync(join(output,'proposal.json'),JSON.stringify({status:'validated-proposal-only',summaryPath,summarySha256:summarySha,reportHashes,expected,results,repositoryStartingHead:summary.repositoryStartingHead,sourceDifference:summary.snapshot.sourceDifference,buildSettings:summary.snapshot.identicalBuildSettings,currentDocumentation:{perfSha256:hashFile(perfPath),notesSha256:hashFile(notesPath)},limitations:['No repository files were written.','Direct Go/Go A/B; not native target comparison.','GNU-time-wrapped timings cannot compare with historical unwrapped timings.','Timed invocation output/exit parity is enforced by the hashed runner; raw per-sample diagnostic text is not separately retained in the report.','Report links outside benchmarks/ need relocation before committing proposed documentation.']},null,2)+'\n',{flag:'wx'});
console.log(`Prepared four PERF rows and one NOTES entry in ${output}; repository untouched.`);
