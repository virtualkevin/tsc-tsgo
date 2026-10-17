import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {hashFile,readBuildProvenance,captureGoSources} from '/home/dev/tssss/tsc-tsgo/scripts/build-provenance.mjs';
export {hashFile};
export const root='/home/dev/tssss/tsc-tsgo';
export const library=join(root,'upstream/typescript-go/internal/bundled/libs');
export const configPath=resolve(process.argv[3]);
export const config=JSON.parse(readFileSync(configPath,'utf8'));
export const expected=config.expected;
export const groups=config.groups;
export const load=path=>JSON.parse(readFileSync(path,'utf8'));
export const median=xs=>[...xs].sort((a,b)=>a-b)[Math.floor(xs.length/2)];
const near=(a,b)=>assert.ok(Number.isFinite(a)&&Math.abs(a-b)<1e-8,`Numeric summary mismatch: ${a} / ${b}`);
export const support=['benchmarks/run.mjs','benchmarks/resource-run.mjs','benchmarks/cgroup.mjs','scripts/build-provenance.mjs','benchmarks/workloads.json','benchmarks/profiles/node-pointer-candidate/COMPARISON_POLICY.md'];
export function capture(){
 assert.equal(expected.baseline.sha256,'525c0fe92b231e13ce225687929a606b1d7d47851216cc10d4e2b91dfdcd0bb4');
 assert.equal(hashFile(join(root,'benchmarks/profiles/node-pointer-candidate/COMPARISON_POLICY.md')),config.comparisonPolicySha256);
 const result={files:Object.fromEntries(support.map(p=>[p,hashFile(join(root,p))])),node:{path:process.execPath,sha256:hashFile(process.execPath)},wrapper:{path:'/usr/bin/time',sha256:hashFile('/usr/bin/time')},binaries:{}};
 for(const [name,e] of Object.entries(expected)){
  assert.equal(hashFile(e.path),e.sha256,`${name} binary mismatch`);
  const p=readBuildProvenance(e.path,e.sha256);
  if(name==='baseline')assert.equal(p.status,'absent','Historical native artifact has no build sidecar; do not invent provenance');
  else {
   assert.equal(p.status,'verified');assert.equal(p.sidecarSha256,e.sidecarSha256);assert.equal(p.metadata.source.sha256,e.source);
   const b=p.metadata.build;
   assert.equal(b.toolchain.GOVERSION,'go1.26.9');assert.equal(b.toolchain.GOOS,'linux');assert.equal(b.toolchain.GOARCH,'amd64');assert.equal(b.toolchain.GOAMD64,'v1');
   assert.deepEqual(b.arguments,['build','-trimpath','-o','<binary>','./cmd/tsgo']);assert.equal(b.extraFlagsPresent,false);assert.equal(b.profile,null);
  }
  result.binaries[name]={path:e.path,sha256:e.sha256,buildProvenance:p};
 }
 const confirmations=['forward','reverse'].map(direction=>{
  const path=join(root,`benchmarks/results/node-pointer-confirm-${direction}/recording/proposal.json`),p=load(path);
  assert.equal(p.status,'passed');assert.equal(p.experiment,`node-pointer-confirm-${direction}`);
  assert.equal(p.comparisonPolicySha256,config.comparisonPolicySha256);
  assert.deepEqual(Object.keys(p.gates).sort(),['allWorkloadMedianRssAtMost105','allWorkloadSummariesAtLeast098','bothAggregatesAtLeast101']);
  for(const value of Object.values(p.gates))assert.equal(typeof value,'boolean');
  assert.equal(typeof p.passesThisConfirmation,'boolean');assert.equal(p.passesThisConfirmation,Object.values(p.gates).every(Boolean));
  assert.deepEqual(p.results.map(r=>[r.name,r.runs]),[['typeorm',19],['trpc',19],['vscode',11],['sentry',11]]);
  const summaryPath=join(root,`benchmarks/results/node-pointer-confirm-${direction}/summary.json`);
  assert.equal(hashFile(summaryPath),p.summarySha256);assert.equal(load(summaryPath).status,'passed');
  const frozenConfig=join(root,`benchmarks/profiles/node-pointer-confirmation/${direction}.json`);
  assert.equal(hashFile(frozenConfig),p.configSha256);
  return {path,sha256:hashFile(path),summaryPath,summarySha256:p.summarySha256,passes:p.passesThisConfirmation};
 });
 assert.ok(confirmations.every(x=>x.passes),'Both independent confirmations must pass before native milestone');
 assert.equal(config.name,'native-node-pointer');
 assert.equal(expected.candidate.sha256,'8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f');
 result.retentionEvidence=confirmations;
 const current=captureGoSources(join(root,'packages/tsc-go'));
 assert.equal(current.sha256,config.workspaceSource);assert.equal(current.sha256,expected.candidate.source);
 result.workspaceSource={sha256:current.sha256,revision:current.revision,fileCount:current.files.length};
 // Hash current tracked native source separately: this does not reconstruct historical build provenance.
 const r=spawnSync('git',['ls-files','-z','--','packages/tsc-ts/src'],{cwd:root,encoding:'utf8',timeout:10000});
 assert.equal(r.status,0);assert.ok(!r.error&&!r.signal&&!r.stderr);
 const files=r.stdout.split('\0').filter(Boolean).sort().map(path=>({path,sha256:hashFile(join(root,path))}));assert.ok(files.length>0);
 result.currentNativeSources={files,sha256:createHash('sha256').update(JSON.stringify(files)).digest('hex'),scope:'Current tracked source only; not historical binary build provenance'};
 assert.equal(result.currentNativeSources.sha256,config.currentNativeSourceSha256);
 return result;
}
export function readRepositoryHead(){const r=spawnSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8',timeout:10000});assert.equal(r.status,0);assert.ok(!r.error&&!r.signal&&!r.stderr);const head=r.stdout.trim();assert.match(head,/^[a-f0-9]{40}$/);return head;}
export function clearNames(env){return [...new Set([
 'GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOEXPERIMENT','NODE_OPTIONS','GOCOVERDIR','GOTRACEBACK','TS_GO_DEBUG_STACK_LIMIT','TS_WATCH_DEBUG',
 'LLVM_PROFILE_FILE','CPUPROFILE','HEAPPROFILE','HEAPCHECK','PPROF_PATH','MALLOC_CONF','MALLOC_ARENA_MAX','MALLOC_TRIM_THRESHOLD_','GLIBC_TUNABLES','LD_PRELOAD',
 'TSC_GO_SCHEDULER','TSC_GO_SHARED_GLOBALS','TSC_GO_WATCH_PARENT_PID','TSC_GO_WATCH_TEST_DIR','TSC_TS_BUNDLED_LIBS','TSC_TS_CHECKERS','TSC_TS_CHECKERS_TRACE','TSC_TS_ID_ORDER','TSC_TS_RECYCLE','TSC_TS_REGION','TSC_TS_SIDE_STATE','TSC_TS_SMAPS','TSC_TS_TIMELINE','TSC_TS_WATCH_MEMORY','TSC_TS_WATCH_PROCESS','PROJECTS_FILTER',
 ...Object.keys(env).filter(k=>k.startsWith('TSC_')||k.startsWith('TS_GO_')||k.startsWith('SCRIPTC_')||k.startsWith('MIMALLOC_')||k.startsWith('MI_')||k.startsWith('GODEBUG_')),
])].filter(k=>k!=='TSC_TS_LIB_DIR').sort();}
export function validateReport(report,group,snapshot,cleared){
 assert.equal(report.status,'passed');assert.equal(report.runs,group.runs);assert.equal(report.warmups,1);assert.equal(report.timeoutMs,180000);assert.equal(report.candidateCheckers,null);
 assert.equal(report.manifestSha256,snapshot.files['benchmarks/workloads.json']);assert.deepEqual(report.binaries,snapshot.binaries);
 assert.equal(report.resourceMeasurement.enabled,true);assert.equal(report.resourceMeasurement.timingComparableToUnwrapped,false);
 assert.equal(report.resourceMeasurement.wrapper.sha256,snapshot.wrapper.sha256);assert.equal(report.resourceMeasurement.wrapper.path,snapshot.wrapper.path);
 const env={TSC_TS_LIB_DIR:library};assert.deepEqual(report.environment.compilerEnvironment,env);assert.deepEqual(report.environment.compilerEnvironments,{baseline:env,candidate:env});assert.deepEqual(report.environment.candidateEnvironmentOverrides,{});assert.deepEqual(report.environment.unsetEnvironment,cleared);
 assert.deepEqual(report.projects.map(p=>p.name).sort(),[...group.projects].sort());
 const manifest=load(join(root,'benchmarks/workloads.json'));
 const resource=r=>{assert.equal(r.exitStatus,0);assert.ok(Number.isSafeInteger(r.peakRssKiB)&&r.peakRssKiB>0);};
 return report.projects.map(p=>{
  const input=manifest.projects.find(x=>x.name===p.name);assert.ok(input);assert.equal(p.commit,input.commit);assert.equal(p.status,'passed');assert.equal(p.expectedExit,0);assert.equal(p.diagnosticCount,0);assert.equal(p.diagnosticsSha256,null);
  assert.equal(p.cwd,resolve(root,input.directory));assert.equal(p.configSha256,hashFile(resolve(p.cwd,input.project)));assert.equal(p.lockfileSha256,hashFile(resolve(p.cwd,input.lockfile)));
  const args=['-p',input.project,...(input.args??[]),'--noEmit','--incremental','false','--composite','false','--noCheck','false','--pretty','false'];
  assert.ok(!args.some(a=>/^--(?:checkers|cpuProfile|generateTrace)(?:=|$)/i.test(a)));assert.deepEqual(p.compilerArgs,{baseline:args,candidate:args});assert.deepEqual(p.args,args);
  assert.deepEqual(p.fileDiscoveryArgs.baseline,p.fileDiscoveryArgs.candidate);assert.deepEqual(p.fileDiscoveryArgs.baseline,[...args,'--listFilesOnly']);
  assert.equal(p.pairs.length,group.runs);assert.equal(p.warmupResources.length,1);assert.equal(p.resourceWrapperVerifiedAfter,true);
  assert.deepEqual(p.preflight.baseline.inputs,p.preflight.candidate.inputs);assert.equal(p.preflight.baseline.fileListSha256,p.preflight.candidate.fileListSha256);assert.equal(p.preflight.baseline.outputSha256,p.preflight.candidate.outputSha256);assert.equal(p.preflight.baseline.outputSha256,createHash('sha256').update(JSON.stringify(['',''])).digest('hex'),'Expected clean diagnostics');
  assert.ok(p.preflight.baseline.fileCount>0);assert.equal(p.preflight.baseline.fileCount,p.preflight.baseline.inputs.length);assert.equal(p.preflight.candidate.fileCount,p.preflight.baseline.fileCount);
  for(const i of p.preflight.baseline.inputs)assert.equal(hashFile(resolve(p.cwd,i.file)),i.sha256,'Input changed after report');
  for(const side of ['baseline','candidate']){
   assert.equal(p.preflight[side].status,0);resource(p.preflight[side].resources.discovery);resource(p.preflight[side].resources.check);resource(p.warmupResources[0][side]);
   assert.equal(p.execution[side].executable,snapshot.wrapper.path);
   assert.deepEqual(p.execution[side].arguments,['--quiet','--output','<unique-resource-output>','--format',report.resourceMeasurement.wrapper.format,'--',expected[side].path,...args]);
   assert.deepEqual(p.execution[side].fileDiscoveryArguments,['--quiet','--output','<unique-resource-output>','--format',report.resourceMeasurement.wrapper.format,'--',expected[side].path,...p.fileDiscoveryArgs[side]]);
  }
  p.pairs.forEach((pair,i)=>{assert.deepEqual(pair.order,i%2?['candidate','baseline']:['baseline','candidate']);for(const side of ['baseline','candidate']){assert.ok(Number.isFinite(pair[side])&&pair[side]>0);resource(pair.resources[side]);assert.ok(pair.cgroupCpu[side].before&&pair.cgroupCpu[side].after);}});
  for(const side of ['baseline','candidate']){
   const times=p.pairs.map(x=>x[side]),rss=p.pairs.map(x=>x.resources[side].peakRssKiB);
   assert.deepEqual(p[side].samplesMs,times);near(p[side].medianMs,median(times));assert.deepEqual(p.resources[side].peakRssKiB.samples,rss);near(p.resources[side].peakRssKiB.median,median(rss));near(p.resources[side].peakRssKiB.min,Math.min(...rss));near(p.resources[side].peakRssKiB.max,Math.max(...rss));
  }
  near(p.speedup,p.baseline.medianMs/p.candidate.medianMs);
  return {name:p.name,runs:group.runs,files:p.preflight.baseline.fileCount,baselineMedianMs:p.baseline.medianMs,candidateMedianMs:p.candidate.medianMs,baselineOverCandidate:p.speedup,baselineMedianRssMiB:p.resources.baseline.peakRssKiB.median/1024,candidateMedianRssMiB:p.resources.candidate.peakRssKiB.median/1024};
 });
}
