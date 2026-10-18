import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {performance} from 'node:perf_hooks';
import {captureGoSources,hashFile,readBuildProvenance} from '../../../scripts/build-provenance.mjs';
const root=process.cwd(),out=resolve(process.argv[2]);assert.ok(process.argv[2]);mkdirSync(out);
const dir=join(root,'benchmarks/profiles/merged-lookup-census');
const build=JSON.parse(readFileSync(join(dir,'build.json')));
const source='f757f9c9576fac6ff9c91391ba38be874a939260b832538fec98be48097ea868';
const baseline=join(root,'packages/tsc-go/dist/tsc-go-node-pointer'),candidate=join(root,'packages/tsc-go/dist/tsc-go-merged-lookup-census');
const hashes={baseline:'8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f',candidate:build.binarySha256};
assert.equal(hashFile(baseline),hashes.baseline);assert.equal(hashFile(candidate),hashes.candidate);assert.equal(hashFile(candidate+'.provenance.json'),build.sidecarSha256);
const before=captureGoSources(join(root,'packages/tsc-go'));assert.equal(before.sha256,source);
const validated=JSON.parse(readFileSync('/tmp/tsc-merged-lookup-census/units/validation.json'));assert.equal(validated.passed,true);assert.equal(validated.sourceSha256,source);
const bp=readBuildProvenance(baseline,hashes.baseline),cp=readBuildProvenance(candidate,hashes.candidate);assert.equal(bp.status,'verified');assert.equal(cp.status,'verified');assert.equal(cp.metadata.source.sha256,source);assert.equal(bp.metadata.source.sha256,'216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd');assert.deepEqual(bp.metadata.build,cp.metadata.build);
const env={...process.env};for(const k of Object.keys(env))if(/^(TSC_|TS_GO_|SCRIPTC_|GODEBUG_)/.test(k)||['GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOEXPERIMENT','NODE_OPTIONS','LD_PRELOAD'].includes(k))delete env[k];
env.TSC_TS_LIB_DIR=join(root,'upstream/typescript-go/internal/bundled/libs');
const report={status:'running',scope:'Single-run diagnostic control, observer-disabled and observer-enabled captures. Elapsed time includes observer serialization; not optimization performance evidence or causal overhead estimate. Unchanged lookups include nil-valued entries.',source:before,hashes,controllerSha256:hashFile(join(dir,'capture.mjs')),runs:[]};
const save=()=>writeFileSync(join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
const check=p=>{assert.equal(hashFile(resolve(p.cwd,p.args[1])),p.configSha256);for(const i of p.preflight.candidate.inputs)assert.equal(hashFile(resolve(p.cwd,i.file)),i.sha256);};
try{
 for(const group of ['small','large']){
  const reference=join(root,`benchmarks/results/native-node-pointer/${group}.json`),old=JSON.parse(readFileSync(reference));assert.equal(old.status,'passed');
  for(const p of old.projects){
   check(p);const work=join(out,p.name);mkdirSync(work);
   for(const mode of ['baseline','disabled','enabled']){
    const binary=mode==='baseline'?baseline:candidate,census=join(work,'census.json');
    const start=performance.now();const r=spawnSync(binary,p.args,{cwd:p.cwd,env:mode==='enabled'?{...env,TSC_GO_MERGED_LOOKUP_CENSUS:census}:env,encoding:'utf8',timeout:180000,maxBuffer:8*1024*1024});const elapsedMs=performance.now()-start;
    writeFileSync(join(work,mode+'.stdout'),r.stdout??'');writeFileSync(join(work,mode+'.stderr'),r.stderr??'');
    assert.ok(!r.error&&!r.signal);assert.equal(r.status,0);assert.equal(r.stdout,'');assert.equal(r.stderr,'');
    let counts=null;
    if(mode==='enabled'){
     counts=JSON.parse(readFileSync(census));assert.ok(counts.Owners.length>0);
     for(const s of counts.Owners){assert.equal(s.Lookups,s.Replacements+s.Unchanged);assert.equal(s.LookupSizeBuckets.reduce((a,b)=>a+b,0),s.Lookups);assert.equal(s.UnchangedSizeBuckets.reduce((a,b)=>a+b,0),s.Unchanged);assert.ok(s.PeakKeys<=s.Writes);}
    }
    report.runs.push({project:p.name,mode,command:[binary,...p.args],cwd:p.cwd,elapsedMs,reference,referenceSha256:hashFile(reference),inputCount:p.preflight.candidate.fileCount,exitStatus:r.status,stdoutSha256:hashFile(join(work,mode+'.stdout')),stderrSha256:hashFile(join(work,mode+'.stderr')),censusSha256:counts?hashFile(census):null,counts});save();
   }
   check(p);assert.equal(hashFile(baseline),hashes.baseline);assert.equal(hashFile(candidate),hashes.candidate);
  }
 }
 const after=captureGoSources(join(root,'packages/tsc-go'));assert.equal(after.sha256,source);assert.equal(after.revision,before.revision);report.status='passed';
}catch(e){report.status='failed';report.error=String(e);throw e;}finally{save();}
console.log(JSON.stringify({status:report.status,runs:report.runs.length}));
