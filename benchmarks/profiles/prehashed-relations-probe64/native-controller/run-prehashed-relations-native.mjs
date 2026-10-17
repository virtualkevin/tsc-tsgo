// Preparation only. Run after root confirms preserved candidate identities.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdirSync,writeFileSync,readdirSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {hashFile,captureGoSources,readBuildProvenance} from '/home/dev/tssss/tsc-tsgo/scripts/build-provenance.mjs';
import {root,expected,capture,clearNames,readRepositoryHead} from './prehashed-relations-ab-common.mjs';
assert.ok(process.argv[2],'Usage: node /tmp/run-prehashed-relations-native.mjs NEW_TMP_OUTPUT_DIRECTORY');
const output=resolve(process.argv[2]);assert.ok(output.startsWith('/tmp/'),'Output must be under /tmp');
mkdirSync(output); // No overwrites of previous validation evidence.
const candidate=expected.candidate.path,candidatePath=candidate.slice(root.length+1);
const runs=[];let child,signalReceived,error,source,after,snapshot,afterSnapshot,head,provenance,comparators;
const unset=[...new Set(['SHOW_FAILURES',...clearNames(process.env)])].sort();
const env={...process.env};for(const key of unset)delete env[key];
const environment={TSC_GO_CANDIDATE:candidate,TSC_GO_BASELINE:join(root,'packages/tsc-ts/dist/tsc-original'),TSC_TS_BIN:candidate};Object.assign(env,environment);
function signal(number){signalReceived=number;if(child?.pid)killGroup(child.pid);}
const onInt=()=>signal('SIGINT'),onTerm=()=>signal('SIGTERM');process.on('SIGINT',onInt);process.on('SIGTERM',onTerm);
function killGroup(pid){try{process.kill(-pid,'SIGKILL');}catch(e){if(e.code!=='ESRCH')throw e;}}
async function run(def){
 console.log('Starting '+def.name);
 let stdout='',stderr='',timedOut=false,spawnError;
 const result=await new Promise((done,reject)=>{
  child=spawn(process.execPath,def.args,{cwd:def.cwd,env,stdio:['ignore','pipe','pipe'],detached:true});
  const pid=child.pid;let timeout;
  const stop=()=>{if(pid)killGroup(pid);};
  timeout=setTimeout(()=>{timedOut=true;stop();},15*60*1000);
  const receive=(which,data)=>{if(which==='stdout')stdout+=data;else stderr+=data;if(stdout.length+stderr.length>64*1024*1024){spawnError=new Error('output limit exceeded');stop();}};
  child.stdout.on('data',data=>receive('stdout',data));child.stderr.on('data',data=>receive('stderr',data));
  child.once('error',e=>{spawnError=e;});
  child.once('close',(code,sig)=>{clearTimeout(timeout);if(pid)stop();child=null;done({status:code,signal:sig,error:spawnError?.message??null,timedOut});});
 });
 const log=join(output,def.name+'.log'),text=stdout+stderr;writeFileSync(log,text,{flag:'wx'});
 const counts={};for(const line of text.split('\n')){const match=line.replace(/\x1b\[[0-9;]*m/g,'').trim().match(/^(?:ℹ\s*)?(tests|suites|pass|fail|cancelled|skipped|todo|duration_ms)\s+([0-9.]+)$/);if(match)counts[match[1]]=Number(match[2]);}
 const passed=!signalReceived&&!result.error&&!result.timedOut&&result.status===0&&counts.tests===def.expected&&counts.pass===def.expected&&counts.fail===0&&counts.skipped===0&&counts.cancelled===0&&counts.todo===0;
 const record={name:def.name,cwd:def.cwd,command:[process.execPath,...def.args],exitCode:result.status,signal:result.signal,error:result.error,timedOut:result.timedOut,timeoutMs:15*60*1000,log,logSha256:hashFile(log),counts,expectedTests:def.expected,passed};runs.push(record);console.log(JSON.stringify(record));return passed;
}
try{
 snapshot=capture();head=readRepositoryHead();provenance=readBuildProvenance(candidate,expected.candidate.sha256);
 source=captureGoSources(join(root,'packages/tsc-go'));assert.equal(source.sha256,expected.candidate.source);assert.equal(source.files.length,5155);
 writeFileSync(join(output,'source-before.json'),JSON.stringify(source,null,2)+'\n',{flag:'wx'});
 const scriptcPackages=readdirSync(join(root,'node_modules/@scriptc')).filter(name=>name.startsWith('cli-'));assert.deepEqual(scriptcPackages,['cli-linux-x64-gnu'],'Unexpected scriptc oracle selection');
 const paths={nativeTypescript:'packages/tsc-ts/dist/tsc-original',pinnedGoOracle:'packages/tsgo/dist/tsgo',scriptcApiOracle:'node_modules/@scriptc/cli-linux-x64-gnu/dist/lib/typescript/lib/tsc'};
 comparators=Object.fromEntries(Object.entries(paths).map(([key,path])=>[key,{path,sha256:hashFile(join(root,path))}]));
 assert.equal(comparators.nativeTypescript.sha256,'525c0fe92b231e13ce225687929a606b1d7d47851216cc10d4e2b91dfdcd0bb4');
 assert.equal(comparators.pinnedGoOracle.sha256,'b7b9a43499f3b54a63d4901b2c5f05589ebbadb88c21bd8d174773be00502e1a');
 const definitions=[{name:'parity',cwd:root,args:['--test','--test-reporter=spec','packages/tsc-go/tests/parity.mjs'],expected:80},{name:'integration',cwd:join(root,'packages/tsc-ts'),args:['--test','--test-reporter=spec','tests/api.test.mjs','tests/parallel-emit.test.mjs','tests/projects.test.mjs','tests/tsc-project.test.mjs'],expected:12}];
 for(const def of definitions){if(signalReceived)throw new Error(signalReceived);if(!await run(def))break;assert.equal(readRepositoryHead(),head);assert.deepEqual(captureGoSources(join(root,'packages/tsc-go')),source);}
}catch(e){error=e.stack??String(e);console.error(error);}finally{
 if(child?.pid)killGroup(child.pid);
 let unchanged=false;
 try{if(source){after=captureGoSources(join(root,'packages/tsc-go'));writeFileSync(join(output,'source-after.json'),JSON.stringify(after,null,2)+'\n',{flag:'wx'});afterSnapshot=capture();unchanged=JSON.stringify(source)===JSON.stringify(after)&&JSON.stringify(snapshot)===JSON.stringify(afterSnapshot)&&readRepositoryHead()===head&&Object.values(comparators??{}).every(c=>hashFile(join(root,c.path))===c.sha256);}}catch(e){error??=e.stack??String(e);}
 const report={schemaVersion:1,node:{path:process.execPath,version:process.version},recordedAt:new Date().toISOString(),scope:'Default native differential parity and actual-Go API/emit/project integrations after replacing Relation.results with full-width prehashed storage and bounded-probe Go-map fallback.',nativeSuiteStatus:!error&&!signalReceived&&runs.length===2&&runs.every(r=>r.passed)&&unchanged?'passed':'failed',candidate:{path:candidatePath,sha256:expected.candidate.sha256},buildProvenance:provenance?{path:provenance.path,sha256:provenance.sidecarSha256,builtAt:provenance.metadata.builtAt,sourceSha256:provenance.metadata.source.sha256,buildTimeRevision:provenance.metadata.source.revision,sourceDirty:provenance.metadata.source.dirty,sourceFileCount:provenance.metadata.source.files.length,settings:provenance.metadata.build}:null,sourceDifference:snapshot?.sourceDifference,repositoryStartingHead:head,sourceBefore:source?{sha256:source.sha256,revision:source.revision,dirty:source.dirty,fileCount:source.files.length}:null,sourceAfter:after?{sha256:after.sha256,revision:after.revision,dirty:after.dirty,fileCount:after.files.length}:null,comparators,unsetEnvironment:unset,environment,runs,verifiedSourcesBinariesAndSidecarUnchanged:unchanged,error,signal:signalReceived,notes:['Exact candidate/source/sidecar identities, identical production build settings and three-file delta versus preserved saturated baseline are verified before suites. Full128-bit key equality and saturated key construction are retained.','SHOW_FAILURES is cleared so API mismatches cannot be masked.80 parity and12 actual-Go integrations are required, with no skipped/cancelled/todo tests.','Go units, race/checkptr and full pinned upstream conformance are separate; these normal CLI suites do not imply race-instrumented CLI validation.','Source and HEAD plus candidate/baseline/comparator binaries and sidecars are checked unchanged; external module contents and every JS fixture are not independently hashed.','Report and logs are written only under the fresh /tmp output directory. Validation durations are not performance measurements.']};
 writeFileSync(join(output,'prehashed-relations-native.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});console.log('Report '+report.nativeSuiteStatus);if(report.nativeSuiteStatus!=='passed')process.exitCode=signalReceived==='SIGINT'?130:signalReceived==='SIGTERM'?143:1;
 process.removeListener('SIGINT',onInt);process.removeListener('SIGTERM',onTerm);
}
