// Draft: execute only after the coordinator releases a quiet benchmark window.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import {mkdirSync,readFileSync,writeFileSync,readdirSync,existsSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {root,library,expected,groups,load,hashFile,capture,clearNames,validateReport} from './pointer-scheduler-ab-common.mjs';
const directory=process.argv[2]?resolve(process.argv[2]):join(root,'benchmarks/results',`pointer-scheduler-ab-rss-${new Date().toISOString().replaceAll(':','-')}-${process.pid}`);
mkdirSync(directory); // Must be a new directory; do not overwrite partial or completed evidence.
const summaryPath=join(directory,'summary.json');
const ownerKey='_TSC_BENCH_OWNER',owner=randomUUID();
const cleared=clearNames(process.env);
const summary={schemaVersion:1,startedAt:new Date().toISOString(),status:'running',expected,unsetEnvironment:cleared,compilerEnvironments:{baseline:{TSC_TS_LIB_DIR:library},candidate:{TSC_TS_LIB_DIR:library,TSC_GO_SCHEDULER:'dependency'}},cleanup:{ownerEnvironmentName:ownerKey,ownerToken:owner,policy:'Forward SIGTERM to runner; runner kills detached GNU-time/compiler groups. After failure/exit scan only processes carrying this unique marker and kill surviving marked process groups, checking PID start times. No /proc polling inside measurements.'},totalTimeoutMs:30*60*1000,perInvocationTimeoutMs:180000,methodology:'Same preserved PointerLinkStore Go binary on both sides; explicit four checkers and default GC. Baseline unset/default round-robin scheduler versus candidate dependency scheduler. GNU time wraps both. Three alternating pairs and one warmup for each of four pinned workloads. >1 favors dependency scheduling. This is a Go-to-Go scheduling experiment, not the native target comparison; wrapped timing cannot compare with historical unwrapped timing. RSS is command peak, not aggregate process-tree or Go heap.',runs:[]};
const save=()=>writeFileSync(summaryPath,JSON.stringify(summary,null,2)+'\n');
let child,cancelled,grace,totalTimer;
function identity(pid){try{const text=readFileSync(`/proc/${pid}/stat`,'utf8');return text.slice(text.lastIndexOf(')')+2).split(' ')[19];}catch{return null;}}
function marked(){
 const result=[];
 for(const name of readdirSync('/proc')){
  if(!/^\d+$/.test(name))continue;
  try{const pid=Number(name),before=identity(pid);if(!before)continue;const values=readFileSync(`/proc/${pid}/environ`).toString().split('\0');if(values.includes(`${ownerKey}=${owner}`)&&identity(pid)===before)result.push({pid,start:before});}catch(error){if(!['ENOENT','ESRCH','EACCES','EPERM'].includes(error.code))throw error;}
 }
 return result;
}
function sweep(){
 const processes=marked();
 for(const p of processes){if(identity(p.pid)!==p.start)continue;try{process.kill(-p.pid,'SIGKILL');}catch(error){if(!['ESRCH','EPERM'].includes(error.code))throw error;}try{if(identity(p.pid)===p.start)process.kill(p.pid,'SIGKILL');}catch(error){if(error.code!=='ESRCH')throw error;}}
 return processes;
}
function cancel(reason){
 cancelled??=reason;
 if(child){child.kill('SIGTERM');grace??=setTimeout(()=>{summary.forcedCleanup=sweep();},5000);}else sweep();
}
const interrupt=()=>cancel('SIGINT'),terminate=()=>cancel('SIGTERM');process.on('SIGINT',interrupt);process.on('SIGTERM',terminate);
async function execute(args,env){
 await new Promise((resolvePromise,reject)=>{
  child=spawn(process.execPath,args,{cwd:root,env,detached:true,stdio:['ignore','inherit','inherit']});
  let spawnError;
  child.once('error',e=>{spawnError=e;});
  child.once('close',(code,signal)=>{
   clearTimeout(grace);grace=undefined;child=undefined;
   const remaining=sweep();
   if(spawnError||cancelled||signal||code!==0||remaining.length)reject(spawnError??new Error(`Runner failed: code=${code}; signal=${signal}; cancellation=${cancelled}; leftoverMarkedProcesses=${remaining.length}`));else resolvePromise();
  });
 });
}
try{
 assert.equal(process.platform,'linux','Cleanup and GNU time mode require Linux');
 summary.snapshot=capture();summary.controllerFiles=Object.fromEntries(['/tmp/run-pointer-scheduler-ab.mjs','/tmp/pointer-scheduler-ab-common.mjs'].map(p=>[p,hashFile(p)]));
 const manifest=load(join(root,'benchmarks/workloads.json'));assert.deepEqual(manifest.projects.map(p=>p.name).sort(),groups.flatMap(g=>g.projects).sort());
 for(const p of manifest.projects)assert.ok(!(p.args??[]).some(a=>/^--checkers(?:=|$)/.test(a)));
 const names=groups[0].projects;
 manifest.projects.sort((a,b)=>names.indexOf(a.name)-names.indexOf(b.name));
 for(const p of manifest.projects)p.args=[...(p.args??[]),'--checkers','4'];
 manifest.provenance+=' Scheduler experiment overlay: explicit --checkers 4 for both sides; same preserved PointerLinkStore binary. Baseline unset round-robin, candidate dependency scheduling only.';
 const manifestPath=join(directory,'workloads-default4.json');writeFileSync(manifestPath,JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
 summary.measurementManifest={path:manifestPath,sha256:hashFile(manifestPath)};
 // Verify the preserved binary's scheduler source, rather than assuming current main implements its policy.
 const scheduler=summary.snapshot.binaries.baseline.buildProvenance.metadata.source.files.find(f=>f.path==='packages/tsc-go/internal/compiler/checkerpool.go');assert.ok(scheduler);
 const schedulerPath='/tmp/pointer-scheduler-checkerpool.go';assert.equal(hashFile(schedulerPath),scheduler.sha256);
 const schedulerText=readFileSync(schedulerPath,'utf8');assert.match(schedulerText,/case "dependency":\s*assignments = dependencyCheckerAssignments/);assert.match(schedulerText,/owner := i % checkerCount/);assert.doesNotMatch(schedulerText,/case "roundrobin":/);
 const savedScheduler=join(directory,'checkerpool.go.txt');writeFileSync(savedScheduler,schedulerText,{flag:'wx'});summary.schedulerSource={path:savedScheduler,sha256:scheduler.sha256};
 const env={...process.env};for(const key of cleared)delete env[key];env.TSC_TS_LIB_DIR=library;env[ownerKey]=owner;
 totalTimer=setTimeout(()=>cancel('overall deadline'),summary.totalTimeoutMs);save();
 for(const group of groups){
  if(cancelled)throw new Error(cancelled);
  assert.deepEqual(capture(),summary.snapshot,'Immutable executables, provenance or harness changed');
  const output=join(directory,`${group.name}.json`);assert.ok(!existsSync(output));
  const args=['benchmarks/run.mjs','--baseline',expected.baseline.path,'--candidate',expected.candidate.path,'--manifest',manifestPath,'--candidate-env','TSC_GO_SCHEDULER=dependency','--projects',group.projects.join(','),'--runs',String(group.runs),'--warmups','1','--timeout','180000','--measure-rss','--output',output,...cleared.flatMap(k=>['--unset-env',k])];
  const run={name:group.name,status:'running',output,command:[process.execPath,...args],projects:group.projects,runs:group.runs};summary.runs.push(run);save();
  await execute(args,env);
  run.results=validateReport(load(output),group,summary.snapshot,cleared,manifestPath);assert.deepEqual(capture(),summary.snapshot);assert.equal(hashFile(manifestPath),summary.measurementManifest.sha256);assert.equal(hashFile(summary.schedulerSource.path),summary.schedulerSource.sha256);run.reportSha256=hashFile(output);run.status='passed';save();
 }
 for(const [path,sha] of Object.entries(summary.controllerFiles))assert.equal(hashFile(path),sha);
 summary.status='passed';
}catch(error){summary.status='failed';summary.error=error.stack??error.message;const run=summary.runs.at(-1);if(run?.status==='running')run.status='failed';process.exitCode=cancelled==='SIGINT'?130:cancelled==='SIGTERM'?143:1;console.error(error.message);
}finally{
 clearTimeout(totalTimer);clearTimeout(grace);const remaining=sweep();if(remaining.length){summary.status='failed';summary.finalCleanup=remaining;process.exitCode=1;}summary.completedAt=new Date().toISOString();save();process.removeListener('SIGINT',interrupt);process.removeListener('SIGTERM',terminate);console.log(`PointerLinkStore scheduler A/B ${summary.status}: ${summaryPath}`);
}
