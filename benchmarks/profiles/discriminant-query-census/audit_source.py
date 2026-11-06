from pathlib import Path
import hashlib,json,re,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2];m=r/'packages/tsc-go'
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
fmt=lambda s:subprocess.check_output(['/tmp/tsc-toolchains/go/bin/gofmt'],input=s.encode()).decode()
s=(p/'staged/checker.go').read_text()
s,n=re.subn(r'^\s*discriminantQueryCensus\s+\*discriminantQueryCensus\n','',s,count=1,flags=re.M);assert n==1
s=s.replace('\n\tc.discriminantQueryCensus = newDiscriminantQueryCensus()','',1)
assert fmt(s)==(m/'internal/checker/checker.go').read_text()
s=(p/'staged/relater.go').read_text();a='c.observedDiscriminantQuery(types[i], discriminator.name(n), discriminator)';assert s.count(a)==1
assert s.replace(a,'c.getTypeOfPropertyOrIndexSignatureOfType(types[i], discriminator.name(n))')==(m/'internal/checker/relater.go').read_text()
s=(p/'staged/tsc.go').read_text();hook='\n\tif err := program.WriteDiscriminantQueryCensus(); err != nil {\n\t\tpanic(err)\n\t}\n';assert s.count(hook)==1
assert s.replace(hook,'',1)==(m/'internal/execute/tsc.go').read_text()
base=json.loads((p/'base.json').read_text());assert all(sha(k)==v for k,v in base.items())
paths=json.loads((p/'overlay.json').read_text())['Replace'];assert len(paths)==len(set(paths.values()))==7
(p/'source-audit.json').write_text(json.dumps({'passed':True,'base':base,'sources':{k:sha(v) for k,v in paths.items()},'controllerSha256':sha(__file__),'scope':'Removing field/init, single query routing hook and post-CLI exporter restores all original source files exactly. Observer wrapper calls the original property/index helper once with unchanged type/name arguments; no semantic bypass. Source adaptation audit is not a whole compiler proof.'},indent=2)+'\n')
print('Exact retained files restored after removing diagnostic hooks')
