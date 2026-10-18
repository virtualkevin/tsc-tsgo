import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {join} from 'node:path';
import {captureGoSources,hashFile} from '../../../scripts/build-provenance.mjs';
const root=process.cwd(),out='/tmp/tsc-sparse-property-helper/wide';mkdirSync(out);
const source='e2b806c1578b85f998691163441813314bf3e84a295f17fe439115fba28dc0b2';
const before=captureGoSources(join(root,'packages/tsc-go'));assert.equal(before.sha256,source);
const build=JSON.parse(readFileSync(join(root,'benchmarks/profiles/sparse-property-helper/build.json')));
const binaries={candidate:join(root,'packages/tsc-go/dist/tsc-go-sparse-property-helper'),retained:join(root,'packages/tsc-go/dist/tsc-go-node-pointer'),oracle:join(root,'packages/tsgo/dist/tsgo')};
const hashes=Object.fromEntries(Object.entries(binaries).map(([k,v])=>[k,hashFile(v)]));assert.equal(hashes.candidate,build.binarySha256);assert.equal(hashes.retained,'8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f');assert.equal(hashes.oracle,'b7b9a43499f3b54a63d4901b2c5f05589ebbadb88c21bd8d174773be00502e1a');
const env={...process.env};for(const k of Object.keys(env))if(/^(TSC_|TS_GO_)/.test(k)||['GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOFLAGS','GOEXPERIMENT','NODE_OPTIONS','LD_PRELOAD'].includes(k))delete env[k];
env.TSC_TS_LIB_DIR=join(root,'upstream/typescript-go/internal/bundled/libs');
const cases=[
 ['small-source','','declare const source: {anchor:number};',false],
 ['wrong-late-property','','declare const source: {anchor:number; LAST:number};',true],
 ['global-augmentation','toString?:()=>number;','declare const source: {anchor:number};',true],
 ['override-augmentation','toString?:()=>number;','declare const source: {anchor:number;toString:()=>number};',false],
 ['recursive','next?:Wide;','interface Source {anchor:number;next?:Source}; declare const source:Source;',false],
 ['recursive-mismatch','next?:Wide;','interface Source {anchor:number;next?:{anchor:string}}; declare const source:Source;',true],
 ['callable-fallback','','declare const source: (()=>void)&{anchor:number};',false],
 ['mapped-source','','type Source<T> = {[K in keyof T]:T[K]};declare const source:Source<{anchor:number}>;',false],
];
const report={passed:false,sourceSha256:source,head:before.revision,hashes,controllerSha256:hashFile(import.meta.filename),runs:[]};
try{
 for(const width of [255,256,511])for(const exact of [false,true])for(const [name,extra,decl,error] of cases){
  const id=`${name}-${width}-${exact}`,file=join(out,id+'.ts');const extras=extra?(extra.match(/\?:/g)||[]).length:0;
  const fields=Array.from({length:width-1-extras},(_,i)=>`p${i}?: string;`).join('\n');
  writeFileSync(file,`interface Wide { anchor:number; ${extra}\n${fields}\n}\n${decl.replace('LAST','p'+(width-2-extras))}\nconst target:Wide=source;\n`);
  const args=['--ignoreConfig','--noEmit','--pretty','false','--strict','--skipLibCheck','--target','esnext','--module','nodenext','--moduleResolution','nodenext','--exactOptionalPropertyTypes',String(exact),file];
  let expected=null;const results={};
  for(const [role,binary] of Object.entries(binaries)){
   const r=spawnSync(binary,args,{cwd:root,env,encoding:'utf8',timeout:120000,maxBuffer:4*1024*1024});writeFileSync(join(out,id+'.'+role+'.stdout'),r.stdout??'');writeFileSync(join(out,id+'.'+role+'.stderr'),r.stderr??'');assert.ok(!r.error&&!r.signal);assert.equal(r.stderr,'');assert.equal(r.status,error?1:0,id+' '+role);if(error)assert.ok(r.stdout.includes('error TS'));else assert.equal(r.stdout,'');
   const value={status:r.status,stdout:r.stdout,stderr:r.stderr};if(expected)assert.deepEqual(value,expected,id+' '+role);else expected=value;
   writeFileSync(join(out,id+'.'+role+'.stdout'),r.stdout);results[role]={status:r.status,stdoutSha256:hashFile(join(out,id+'.'+role+'.stdout'))};
  }
  report.runs.push({id,fileSha256:hashFile(file),args,results});
 }
 assert.equal(report.runs.length,48);const after=captureGoSources(join(root,'packages/tsc-go'));assert.equal(after.sha256,source);assert.equal(after.revision,before.revision);for(const [k,v] of Object.entries(binaries))assert.equal(hashFile(v),hashes[k]);report.passed=true;
}catch(e){report.error=String(e);throw e;}finally{writeFileSync(join(out,'validation.json'),JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify({passed:report.passed,cases:report.runs.length}));
