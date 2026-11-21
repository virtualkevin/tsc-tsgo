"""Compare CLI exit status, diagnostic text and output files for noEmit edge cases."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_","TS_GO_","SCRIPTC_"))}
env["TSC_TS_LIB_DIR"] = str(here.parents[2]/"upstream/typescript-go/internal/bundled/libs")
cases = [
    ("declarations", "export const n: number = 1", {"declaration":True}, 0),
    ("semantic-error", "export const n: number = 'x'", {"declaration":True}, 1),
    ("declaration-error", "export function f(x: number) {return x+1}", {"isolatedDeclarations":True,"declaration":True}, 1),
    ("noEmitOnError", "export const n: number = 'x'", {"noEmitOnError":True}, 1),
    ("noEmitOnError-clean", "export const n: number = 1", {"noEmitOnError":True}, 0),
    ("incremental", "export const n: number = 1", {"declaration":True,"incremental":True,"tsBuildInfoFile":"out/cache.tsbuildinfo"}, 0),
    ("real-emit", "export const n: number = 1", {"noEmit":False,"declaration":True,"declarationMap":True}, 0),
    ("declaration-input","export declare const n: number",{"declaration":True},0),
    ("json-input",'{"n":1}',{"resolveJsonModule":True},0),
]
engines = dict(zip(("control","candidate"), (Path(arg).resolve() for arg in sys.argv[1:]), strict=True))
report = []
for label,source,opts,status in cases:
    expected = None
    for engine,binary in engines.items():
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            filename = {"declaration-input":"main.d.ts","json-input":"main.json"}.get(label,"main.ts")
            (cwd/filename).write_text(source)
            config = {"files":[filename],"compilerOptions":{"strict":True,"noEmit":True,"module":"node16","target":"es2022","outDir":"out",**opts}}
            (cwd/"tsconfig.json").write_text(json.dumps(config))
            history = []
            for step in range(2 if label=="incremental" else 1):
                proc = subprocess.run([binary,"-p",".","--pretty","false","--listEmittedFiles"],cwd=cwd,env=env,capture_output=True,text=True,timeout=90)
                files = {f.relative_to(cwd).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in (cwd/"out").rglob("*") if f.is_file()}
                assert proc.returncode==status and not proc.stderr,(label,engine,proc.stdout,proc.stderr)
                if label=="incremental":
                    assert set(files)=={"out/cache.tsbuildinfo"}
                elif label=="real-emit":
                    assert set(files)=={"out/main.js","out/main.d.ts","out/main.d.ts.map"}
                else:
                    assert not files
                history.append({"exit":proc.returncode,"stdout":proc.stdout.replace(str(cwd),"<cwd>"),"files":files})
            if expected is None:
                expected = history
            assert history==expected,(label,engine,history,expected)
    report.append(dict(case=label,steps=expected))
(here/"noemit-checks.json").write_text(json.dumps(report,indent=2)+"\n")
