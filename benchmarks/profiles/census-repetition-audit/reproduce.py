"""Recompute from archived evidence; no compiler execution or performance timing."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

base = Path(__file__).resolve().parent
root = base.parents[2]
archive = root / 'benchmarks/profiles/semantic-census-trpc-pilot/evidence.tar.gz'
report = json.loads((base / 'report.json').read_text())
members = []
with tempfile.TemporaryDirectory() as directory, tarfile.open(archive) as tar:
    for run in report['runs']:
        name = run['name']
        for member, local, field in [
            (f'trpc/{name}.census.jsonl', name+'.census.jsonl', 'censusSha256'),
            (f'trpc/{name}-profiles/cpu.raw.txt', name+'.cpu.raw.txt', 'rawCpuSha256'),
        ]:
            data = tar.extractfile(member).read()
            digest = hashlib.sha256(data).hexdigest()
            assert digest == run[field], member
            (Path(directory) / local).write_bytes(data)
            members.append(dict(member=member, sha256=digest, bytes=len(data)))
    output = Path(directory) / 'report.json'
    subprocess.run([sys.executable, str(base/'analyze.py'), directory, str(output)],
                   check=True, stdout=subprocess.DEVNULL)
    assert json.loads(output.read_text()) == report
manifest = dict(archive=str(archive.relative_to(root)),
                sha256=hashlib.sha256(archive.read_bytes()).hexdigest(), members=members)
(base/'inputs.json').write_text(json.dumps(manifest, indent=2)+'\n')
print('All four archived inputs verified; report reproduces exactly')
