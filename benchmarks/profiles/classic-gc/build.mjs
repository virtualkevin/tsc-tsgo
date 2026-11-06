import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {existsSync,mkdirSync,openSync,closeSync,writeFileSync,readFileSync} from 'node:fs';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureGoSources,assertSameGoSources,describeGoBuild,publishBuildProvenance,hashFile} from '../../../scripts/build-provenance.mjs';
const p=dirname(fileURLToPath(import.meta.url)),root=resolve(p,'../../..'),module=join(root,'packages/tsc-go'),go='/tmp/tsc-toolchains/go/bin/go';
for(const k of Object.keys(process.env))if(/^(?:TSC_|TS_GO_|SCRIPTC_)/.test(k)||['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE','GOOS','GOARCH','GOAMD64','GOCOVERDIR','LD_PRELOAD'].includes(k))delete process.env[k];
process.env.GOEXPERIMENT='nogreenteagc';process.env.GOTOOLCHAIN='local';process.env.GOCACHE='/home/dev/.cache/go-build';
const out='/tmp/tsc-classic-gc-validation';mkdirSync(out);const binary=join(out,'tsc-go-classic-gc');
assert(!existsSync(join(p,'build.json')));
const source=captureGoSources(module);assert.equal(source.sha256,'216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd');
const retained=join(module,'dist/tsc-go');assert.equal(hashFile(retained),'8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f');
const args=['build','-trimpath','-o',binary,'./cmd/tsgo'],build=describeGoBuild(go,args,module);
assert.equal(build.toolchain.GOEXPERIMENT,'nogreenteagc');assert.equal(build.toolchain.GOVERSION,'go1.26.9');assert.equal(build.extraFlagsPresent,false);
assert.equal(hashFile(retained+'.provenance.json'),'76e6c4f05d244f4f3f1cd562950bbc3388716b139176ee3583ecc912e3a2bca2');
const normalized=structuredClone(build);normalized.toolchain.GOEXPERIMENT='';assert.deepEqual(normalized,JSON.parse(readFileSync(retained+'.provenance.json','utf8')).build);
const files=['internal/buildcfg/exp.go','internal/goexperiment/flags.go','internal/goexperiment/exp_greenteagc_off.go','runtime/mgc.go','runtime/mgcmark.go'];
const runtimeSources=Object.fromEntries(files.map(f=>[f,hashFile('/tmp/tsc-toolchains/go/src/'+f)]));
const report={passed:false,controllerSha256:hashFile(fileURLToPath(import.meta.url)),toolchainSha256:hashFile(go),runtimeSources,sourceSha256:source.sha256,command:[go,...args],experiment:'nogreenteagc',scope:'Isolated normal compiler build; identical compiler source, different collector implementation. No correctness or performance claim.'};
const stdout=openSync(join(p,'build.stdout'),'wx'),stderr=openSync(join(p,'build.stderr'),'wx');
try{
 const result=spawnSync(go,args,{cwd:module,stdio:['ignore',stdout,stderr],timeout:1200000});report.exitCode=result.status;report.signal=result.signal;
 if(result.error)throw result.error;assert.equal(result.status,0);
 assertSameGoSources(source,captureGoSources(module));assert.deepEqual(build,describeGoBuild(go,args,module));
 const metadata=publishBuildProvenance(binary,source,build);report.binary=binary;report.binarySha256=metadata.binary.sha256;report.sidecarSha256=hashFile(binary+'.provenance.json');report.passed=true;
}catch(e){report.error=String(e);throw e;}finally{
 closeSync(stdout);closeSync(stderr);report.stdoutSha256=hashFile(join(p,'build.stdout'));report.stderrSha256=hashFile(join(p,'build.stderr'));
 assert.equal(hashFile(retained),'8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f');
 writeFileSync(join(p,'build.json'),JSON.stringify(report,null,2)+'\n');
}
console.log(JSON.stringify(report,null,2));
