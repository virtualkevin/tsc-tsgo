"""Run the ordinary project discovery commands; verify files and compact per-file counts."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
scratch = Path(sys.argv[1])
binary = scratch/"census"
types = json.loads((scratch/"types.json").read_text())
reference = json.loads(gzip.decompress((here.parent/"template-union-compaction/native.json.gz").read_bytes()))
def sha(data):
    return hashlib.sha256(data).hexdigest()

manifest={"revision":"50291d2", "observerSha256":sha(binary.read_bytes()), "types":types, "projects":{}}
for project in reference["projects"]:
    name=project["name"]
    cwd=Path(project["cwd"])
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==project["commit"]
    files={str((cwd/f["file"]).resolve()):f for f in project["preflight"]["candidate"]["inputs"]}
    for path,f in files.items():
        assert sha(Path(path).read_bytes())==f["sha256"]
    env={k:v for k,v in os.environ.items() if not k.startswith(("TSC_","TS_GO_","SCRIPTC_"))}
    env.update(reference["environment"]["compilerEnvironment"])
    run=subprocess.run([binary,*project["fileDiscoveryArgs"]["candidate"]],cwd=cwd,env=env,
                       timeout=300,capture_output=True,text=True,check=True)
    assert sorted(str((cwd/f).resolve()) for f in run.stdout.splitlines())==sorted(files)
    lines=run.stderr.splitlines()
    sizes=json.loads(lines[0])
    assert len(sizes)==len(types)
    assert manifest.setdefault("elementBytes",sizes)==sizes
    rows=[]
    for line in lines[1:]:
        path,size,counts=json.loads(line)
        assert len(counts)==len(types) and min(counts)>=0
        resolved=str((cwd/path).resolve())
        # The loader may also parse config or package files outside final source inputs.
        rows.append([files[resolved]["file"] if resolved in files else path,size,counts,resolved in files])
    assert sorted(r[0] for r in rows if r[3])==sorted(f["file"] for f in files.values())
    rows.sort()
    raw=json.dumps(rows,separators=(",",":")).encode()
    (here/f"{name}.json.gz").write_bytes(gzip.compress(raw,mtime=0))
    manifest["projects"][name]=dict(commit=project["commit"],rawSha256=sha(raw),parses=len(rows),
                                    finalInputParses=sum(r[3] for r in rows),finalInputs=len(files))
    print(name,manifest["projects"][name],flush=True)
(here/"inventory.json").write_text(json.dumps(manifest,indent=2)+"\n")
