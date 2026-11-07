import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdirSync,readdirSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {captureGoSources,hashFile,readBuildProvenance} from '../../../scripts/build-provenance.mjs';
const root=process.cwd(),out=resolve(process.argv[2]);
assert.ok(process.argv[2],'Supply a new output directory');mkdirSync(out);
const binary=join(root,'packages/tsc-go/dist/tsc-go');
const expected='9017fa9abe7add6cadf8cefffca2aea161938b63aeac46ed8d226d7dca916d2a';
const source='b50f489f20634bf3570a18d0fcc5cf811036fbcefe2a5ea481b193f848768445';
const go='/tmp/tsc-toolchains/go/bin/go';
const env={...process.env};
const unset=['GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOEXPERIMENT','NODE_OPTIONS','GOCOVERDIR','LD_PRELOAD','CPUPROFILE','HEAPPROFILE'];
for(const k of Object.keys(env))if(unset.includes(k)||/^(TSC_|TS_GO_|SCRIPTC_|GODEBUG_)/.test(k))delete env[k];
env.TSC_TS_LIB_DIR=join(root,'upstream/typescript-go/internal/bundled/libs');
const report={status:'running',scope:'Single adopted-project-inlining diagnostic profiles; not performance measurements. Allocation samples may omit recent allocations; no forced final GC.',binary:{path:binary,sha256:hashFile(binary),sidecarSha256:hashFile(binary+'.provenance.json')},source:captureGoSources(join(root,'packages/tsc-go')),go:{path:go,sha256:hashFile(go)},runs:[]};
const provenance=readBuildProvenance(binary,expected);assert.equal(provenance.status,'verified');assert.equal(provenance.sidecarSha256,'5164f58805236585d39258604fb12e274475039d04fd3efd5b8572d84c2cf287');assert.equal(provenance.metadata.source.sha256,source);assert.deepEqual(provenance.metadata.build.arguments,['build','-gcflags=github.com/microsoft/typescript-go/...=-l=4','-trimpath','-o','<binary>','./cmd/tsgo']);
assert.equal(report.binary.sha256,expected);assert.equal(report.source.sha256,source);
report.controllerSha256=hashFile(new URL(import.meta.url));
const save=()=>writeFileSync(join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
const inputs=[];
for(const group of ['small','large']){
 const path=join(root,`benchmarks/results/native-project-inlining/${group}.json`);
 const prior=JSON.parse(readFileSync(path));assert.equal(prior.status,'passed');
 for(const p of prior.projects)inputs.push({p,reference:{path,sha256:hashFile(path)}});
}
const check=p=>{
 assert.equal(hashFile(resolve(p.cwd,p.args[1])),p.configSha256);
 for(const i of p.preflight.candidate.inputs)assert.equal(hashFile(resolve(p.cwd,i.file)),i.sha256,i.file);
};
save();
try{
 for(const {p,reference} of inputs){
  check(p);const dir=join(out,p.name);mkdirSync(dir);
  const cmd=[...p.args,'--pprofDir',dir];assert.ok(!cmd.includes('--extendedDiagnostics')&&!cmd.includes('--diagnostics'));
  const r=spawnSync(binary,cmd,{cwd:p.cwd,env,encoding:'utf8',timeout:180000,maxBuffer:8*1024*1024});
  writeFileSync(join(dir,'stdout'),r.stdout??'');writeFileSync(join(dir,'stderr'),r.stderr??'');
  assert.ok(!r.error&&!r.signal);assert.equal(r.status,0);assert.equal(r.stderr,'');
  assert.match(r.stdout,/^Memory profile: [^\n]+\nCPU profile: [^\n]+\n$/);
  check(p);assert.equal(hashFile(binary),expected);
  const profiles=readdirSync(dir).filter(x=>x.endsWith('.pb.gz'));assert.equal(profiles.length,2);
  report.runs.push({name:p.name,reference,inputCount:p.preflight.candidate.fileCount,command:[binary,...cmd],cwd:p.cwd,status:r.status,files:Object.fromEntries(readdirSync(dir).map(f=>[f,hashFile(join(dir,f))]))});save();
 }
 // Decode only after all compiler captures finish, avoiding competing reader work.
 for(const run of report.runs){
  const dir=join(out,run.name),cpu=Object.keys(run.files).find(f=>f.endsWith('-cpuprofile.pb.gz')),mem=Object.keys(run.files).find(f=>f.endsWith('-memprofile.pb.gz'));
  for(const [name,flags,profile] of [['cpu-flat',[],cpu],['cpu-cum',['-cum'],cpu],['alloc-objects-flat',['-alloc_objects'],mem],['alloc-space-flat',['-alloc_space'],mem]]){
   const r=spawnSync(go,['tool','pprof','-top','-nodecount=80',...flags,binary,join(dir,profile)],{env,encoding:'utf8',timeout:60000,maxBuffer:8*1024*1024});assert.equal(r.status,0);assert.ok(!r.error&&!r.signal);writeFileSync(join(dir,name+'.txt'),r.stdout);writeFileSync(join(dir,name+'.stderr'),r.stderr);
  }
 }
 assert.equal(captureGoSources(join(root,'packages/tsc-go')).sha256,source);report.status='passed';
}catch(e){report.status='failed';report.error=String(e);throw e;}finally{save();}
console.log(JSON.stringify({status:report.status,workloads:report.runs.map(r=>r.name)}));
