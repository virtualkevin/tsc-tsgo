import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {captureGoSources,readBuildProvenance,hashFile} from '/home/dev/tssss/tsc-tsgo/scripts/build-provenance.mjs';
const root='/home/dev/tssss/tsc-tsgo';
const source=captureGoSources(root+'/packages/tsc-go');assert.equal(source.sha256,'78b76607d79c501f3c35fcbbec5a880561699244c7d65daab6f27f42b22f9337');
const p=readBuildProvenance(root+'/packages/tsc-go/dist/tsc-go-semantic-census','5f038b8c3ae8c7ac7b7003c9a41367a5dbcabfeaf3b24b45ad1b1f553c41c080');assert.equal(p.status,'verified');assert.equal(p.sidecarSha256,'ef3b70b962ca2931f926a99b816cdd550c2f4de96d560a3a1bb4fe8ac8631e89');
const delta=JSON.parse(readFileSync(root+'/benchmarks/profiles/semantic-census-validation/source-final.json')).files;
const reconstructed=new Map(source.files.map(f=>[f.path,f]));for(const f of delta){assert.equal(hashFile(root+'/benchmarks/profiles/semantic-census-validation/source/'+f.path),f.sha256);reconstructed.set(f.path,f);}
assert.deepEqual([...reconstructed.values()].sort((a,b)=>a.path<b.path?-1:a.path>b.path?1:0),p.metadata.source.files);
writeFileSync('/tmp/tsc-census-workloads/preflight.json',JSON.stringify({status:'passed',head:source.revision,workspace:source.sha256,diagnosticSource:p.metadata.source.sha256,sidecar:p.sidecarSha256})+'\n');
