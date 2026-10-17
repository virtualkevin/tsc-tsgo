import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {hashFile,readBuildProvenance} from '/home/dev/tssss/tsc-tsgo/scripts/build-provenance.mjs';
export {hashFile};
export const root='/home/dev/tssss/tsc-tsgo';
export const library=join(root,'upstream/typescript-go/internal/bundled/libs');
export const expected={
 baseline:{path:join(root,'packages/tsc-go/dist/tsc-go-pointer-linkstore'),sha256:'b1a592d593d3415603062016bfd35b11b810f31f9a49b008ec2292e661a15322',source:'6beaa7324ec7dbf09a8b2776bda64b6d5b0d2e93ead3b27ccc4d3aabf5c43d3d',revisionLabel:'849d873'},
 candidate:{path:join(root,'packages/tsc-go/dist/tsc-go-numeric-relations'),sha256:'17436c0cc37d89adb39f10ca6fdbf734c67f407fc82dc68eb23302506c796f2b',source:'ba28763bee00738fc90a7f7c61dc87949860ba92d02e0dc9350bd1351b0a6f95',revisionLabel:'Numeric relation keys'},
};
export const groups=[{name:'small',projects:['typeorm','trpc'],runs:7},{name:'large',projects:['vscode','sentry'],runs:3}];
export const load=path=>JSON.parse(readFileSync(path,'utf8'));
export const median=xs=>[...xs].sort((a,b)=>a-b)[Math.floor(xs.length/2)];
const near=(a,b)=>assert.ok(Number.isFinite(a)&&Math.abs(a-b)<1e-8,`Numeric summary mismatch: ${a} / ${b}`);
export const support=['benchmarks/run.mjs','benchmarks/resource-run.mjs','benchmarks/cgroup.mjs','scripts/build-provenance.mjs','benchmarks/workloads.json'];
export function capture(){
 assert.match(expected.candidate.sha256,/^[a-f0-9]{64}$/,'Candidate binary not finalized; do not launch');
 assert.match(expected.candidate.source,/^[a-f0-9]{64}$/,'Final corrected source not provided; do not launch');
 const result={files:Object.fromEntries(support.map(p=>[p,hashFile(join(root,p))])),node:{path:process.execPath,sha256:hashFile(process.execPath)},wrapper:{path:'/usr/bin/time',sha256:hashFile('/usr/bin/time')},binaries:{}};
 for(const [name,e] of Object.entries(expected)){
  assert.equal(hashFile(e.path),e.sha256,`${name} binary mismatch`);
  const p=readBuildProvenance(e.path,e.sha256);assert.equal(p.status,'verified');assert.equal(p.metadata.source.sha256,e.source);
  result.binaries[name]={path:e.path,sha256:e.sha256,buildProvenance:p};
 }
 const a=result.binaries.baseline.buildProvenance.metadata,b=result.binaries.candidate.buildProvenance.metadata;
 assert.deepEqual(a.build,b.build,'Build settings differ');
 assert.equal(b.build.toolchain.GOVERSION,'go1.26.9');assert.equal(b.build.toolchain.GOOS,'linux');assert.equal(b.build.toolchain.GOARCH,'amd64');assert.equal(b.build.toolchain.GOAMD64,'v1');
 assert.deepEqual(b.build.arguments,['build','-trimpath','-o','<binary>','./cmd/tsgo']);assert.equal(b.build.extraFlagsPresent,false);assert.equal(b.build.profile,null);
 const before=new Map(a.source.files.map(f=>[f.path,f])),after=new Map(b.source.files.map(f=>[f.path,f]));
 const delta=[...new Set([...before.keys(),...after.keys()])].sort().filter(p=>JSON.stringify(before.get(p))!==JSON.stringify(after.get(p))).map(path=>({path,before:before.get(path)??null,after:after.get(path)??null}));
 assert.deepEqual(delta,[
  {
    "path": "packages/tsc-go/internal/checker/checker.go",
    "before": {
      "path": "packages/tsc-go/internal/checker/checker.go",
      "sha256": "5f4ea48686c739b07e5b9c54551cd35783884c26f047bcaba8209480776d2eb1",
      "executable": false
    },
    "after": {
      "path": "packages/tsc-go/internal/checker/checker.go",
      "sha256": "98fd8b6c7176f05f5fce39bd4af982685061d33e07ae38695d80efa5890d3373",
      "executable": false
    }
  },
  {
    "path": "packages/tsc-go/internal/checker/jsx_managed_attributes_errors_api_test.go",
    "before": null,
    "after": {
      "path": "packages/tsc-go/internal/checker/jsx_managed_attributes_errors_api_test.go",
      "sha256": "9db62d8a8fd00af674034a59a86d7d34b76e95d00766a986e9ac13802a929e99",
      "executable": false
    }
  },
  {
    "path": "packages/tsc-go/internal/checker/relater.go",
    "before": {
      "path": "packages/tsc-go/internal/checker/relater.go",
      "sha256": "5e4638c881b4371c828a4a71cd1b2204a90c0aa4b1da8c9a5c1759f0b4c58aae",
      "executable": false
    },
    "after": {
      "path": "packages/tsc-go/internal/checker/relater.go",
      "sha256": "1b8e4297a1ee8f484037373f06d5dd28d8caf0c3d72ffe2265cc275aec1ee88c",
      "executable": false
    }
  },
  {
    "path": "packages/tsc-go/internal/checker/relation_keys_api_test.go",
    "before": null,
    "after": {
      "path": "packages/tsc-go/internal/checker/relation_keys_api_test.go",
      "sha256": "e32a99d280fc626e4812705d21fe3f856ca9a7688777b91368d1c96a1dbae5ec",
      "executable": false
    }
  },
  {
    "path": "packages/tsc-go/internal/checker/relation_keys_test.go",
    "before": null,
    "after": {
      "path": "packages/tsc-go/internal/checker/relation_keys_test.go",
      "sha256": "954302420fe5e84fb5eb7eeaf7709ca7ac1077b8de5f2e55b302eb7dabb1a70e",
      "executable": false
    }
  }
],'Expected checker/relater key changes, two new relation tests, and added JSX regression only');
 assert.equal(b.source.files.length,5151);
 const transform='packages/tsc-go/internal/transformers/declarations/transform.go';assert.equal(before.get(transform).sha256,'3642d191e79150264e99afdadf9a832930c6f4ab2a39257d313e65498e9aa072');assert.deepEqual(after.get(transform),before.get(transform),'CommonJS prepass guard must be reverted');
 result.sourceDifference=delta;result.identicalBuildSettings=a.build;
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
