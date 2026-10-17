import {spawnSync} from 'node:child_process';
import {readFileSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {hashFile,captureGoSources,readBuildProvenance} from '/home/dev/tssss/tsc-tsgo/scripts/build-provenance.mjs';
const root='/home/dev/tssss/tsc-tsgo';
const candidatePath='packages/tsc-go/dist/tsc-go-numeric-relations';
const candidate=join(root,candidatePath);
const provenance=readBuildProvenance(candidate);
if(provenance.status!=='verified')throw new Error('Candidate provenance required');
const source=captureGoSources(join(root,'packages/tsc-go'));
if(source.sha256!==provenance.metadata.source.sha256)throw new Error('Source differs from candidate build');
const unset=['GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','TSC_GO_SCHEDULER','TSC_GO_SHARED_GLOBALS','TSC_TS_CHECKERS','TSC_TS_REGION','TSC_TS_RECYCLE','TSC_TS_SIDE_STATE','TSC_TS_CHECKERS_TRACE','PROJECTS_FILTER'];
const env={...process.env};for(const key of unset)delete env[key];
const environment={TSC_GO_CANDIDATE:candidate,TSC_GO_BASELINE:join(root,'packages/tsc-ts/dist/tsc-original'),TSC_TS_BIN:candidate};
Object.assign(env,environment);
const comparatorPaths={nativeTypescript:'packages/tsc-ts/dist/tsc-original',pinnedGoOracle:'packages/tsgo/dist/tsgo',scriptcApiOracle:'node_modules/@scriptc/cli-linux-x64-gnu/dist/lib/typescript/lib/tsc'};
const comparators=Object.fromEntries(Object.entries(comparatorPaths).map(([key,path])=>[key,{path,sha256:hashFile(join(root,path))}]));
const definitions=[{name:'parity',cwd:root,args:['--test','--test-reporter=spec','packages/tsc-go/tests/parity.mjs'],expected:80},{name:'integration',cwd:join(root,'packages/tsc-ts'),args:['--test','--test-reporter=spec','tests/api.test.mjs','tests/parallel-emit.test.mjs','tests/projects.test.mjs','tests/tsc-project.test.mjs'],expected:12}];
const runs=[];
for(const def of definitions){
 console.log('Starting '+def.name);
 const result=spawnSync(process.execPath,def.args,{cwd:def.cwd,env,encoding:'utf8',maxBuffer:64*1024*1024,timeout:15*60*1000});
 const log='/tmp/numeric-relations-'+def.name+'.log';
 const output=(result.stdout??'')+(result.stderr??'');writeFileSync(log,output);
 const counts={};for(const line of output.split('\n')){const match=line.replace(/\x1b\[[0-9;]*m/g,'').trim().match(/^(?:ℹ\s*)?(tests|suites|pass|fail|cancelled|skipped|todo|duration_ms)\s+([0-9.]+)$/);if(match)counts[match[1]]=Number(match[2]);}
 const passed=result.status===0 && counts.tests===def.expected && counts.pass===def.expected && counts.fail===0 && counts.skipped===0 && counts.cancelled===0 && counts.todo===0;
 runs.push({name:def.name,cwd:def.cwd,command:['node',...def.args],exitCode:result.status,error:result.error?.code??null,log,logSha256:hashFile(log),counts,expectedTests:def.expected,passed});
 console.log(JSON.stringify(runs.at(-1)));
 if(!passed)break;
}
const after=captureGoSources(join(root,'packages/tsc-go'));
const unchanged=source.sha256===after.sha256 && hashFile(candidate)===provenance.metadata.binary.sha256 && hashFile(provenance.path)===provenance.sidecarSha256 && Object.values(comparators).every(c=>hashFile(join(root,c.path))===c.sha256);
const report={schemaVersion:1,recordedAt:new Date().toISOString(),scope:'Default native differential parity and actual-Go API/emit/project integrations after packing ordinary type-relation keys into uint64 and interning complete exceptional hashes per checker.',nativeSuiteStatus:runs.length===2&&runs.every(r=>r.passed)&&unchanged?'passed':'failed',candidate:{path:candidatePath,sha256:provenance.metadata.binary.sha256},buildProvenance:{path:provenance.path.slice(root.length+1),sha256:provenance.sidecarSha256,builtAt:provenance.metadata.builtAt,sourceSha256:source.sha256,buildTimeRevision:provenance.metadata.source.revision,sourceDirty:provenance.metadata.source.dirty,sourceFileCount:source.files.length,settings:provenance.metadata.build},comparators,unsetEnvironment:unset,environment,runs,verifiedSourcesBinariesAndSidecarUnchanged:unchanged,notes:['The candidate changes relation result maps and transient maybe keys to uint64. Ordinary IDs/state are packed exactly; generic and exceptional keys retain the complete prior hash via a checker-local interner. The rejected CommonJS prepass guard is reverted. Focused normal/race/checkptr evidence is recorded separately; these CLI suites do not imply a race-instrumented CLI build.','These suites compare diagnostics, API results, emitted outputs and project behavior; correctness is not inferred from compiler exit status alone.','Go units and full pinned upstream conformance are recorded separately for this source digest.','Validation durations are not performance measurements.']};
writeFileSync(join(root,'benchmarks/validation/numeric-relations-native.json'),JSON.stringify(report,null,2)+'\n');
console.log('Report '+report.nativeSuiteStatus);
if(report.nativeSuiteStatus!=='passed')process.exitCode=1;
