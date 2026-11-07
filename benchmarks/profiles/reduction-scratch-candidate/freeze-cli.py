from pathlib import Path
import hashlib,json,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2];sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
overlay=p/'overlay.json';out=p/'cli-freeze.json';assert not out.exists()
sources=json.loads(overlay.read_text())['Replace']
data={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'overlaySha256':sha(overlay),'sources':{k:sha(v) for k,v in sources.items()},'base':json.loads((p/'base-inputs.json').read_text())}
out.write_text(json.dumps(data,indent=2)+'\n')
print('Frozen CLI validation inputs at',data['head'])
