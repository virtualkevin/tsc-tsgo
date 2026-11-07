from pathlib import Path
import hashlib,json,subprocess,tarfile
root=Path(__file__).resolve().parents[3];here=Path(__file__).resolve().parent
prior=root/'benchmarks/profiles/project-inlining-normal';manifest=json.loads((prior/'manifest.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest();go=Path('/tmp/tsc-toolchains/go/bin/go');binary=root/'packages/tsc-go/dist/tsc-go'
assert sha(binary.read_bytes())=='9017fa9abe7add6cadf8cefffca2aea161938b63aeac46ed8d226d7dca916d2a'
assert sha((prior/'profiles.tar.gz').read_bytes())==manifest['archiveSha256']
records=[];work=Path('/tmp/tsc-heap-header-audit');work.mkdir(exist_ok=True)
with tarfile.open(prior/'profiles.tar.gz') as archive:
 for entry in manifest['files']:
  if not entry['path'].endswith('-cpuprofile.pb.gz'):continue
  data=archive.extractfile(entry['path']).read();assert sha(data)==entry['sha256']
  project=entry['path'].split('/')[0];p=work/(project+'.pb.gz');p.write_bytes(data)
  cmd=[str(go),'tool','pprof','-source_path=/tmp/tsc-toolchains/go/src','-list=heapSetTypeSmallHeader',str(binary),str(p)]
  result=subprocess.run(cmd,capture_output=True);assert result.returncode==0 and not result.stderr
  text=result.stdout.decode();assert 'Error:' not in text and '*header = typ' in text
  (here/(project+'.txt')).write_bytes(result.stdout)
  records.append({'project':project,'profileSha256':sha(data),'outputSha256':sha(result.stdout),'command':cmd})
runtime=Path('/tmp/tsc-toolchains/go/src/runtime')
report={'passed':True,'records':records,'toolchainSha256':sha(go.read_bytes()),'runtimeSources':{n:sha((runtime/n).read_bytes()) for n in ['mbitmap.go','malloc.go']},'binarySha256':sha(binary.read_bytes())}
(here/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('Verified source attribution for',len(records),'profiles')
