"""Sample the published compiler's symbolized native executable with GNU gprofng."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
frozen = json.loads(gzip.decompress((here.parent/"named-key-union/public.json.gz").read_bytes()))
release = json.loads((here.parent/"public-npm/releases.json").read_text())["releases"]["0.0.2"]
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_", "SCRIPTC_", "TS_GO_"))}
env.update(frozen["environment"]["compilerEnvironment"])
binary = Path(env["TSC_TS_LIB_DIR"])/"tsc-ts"
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert sha(binary)==release["linuxGnuBinarySha256"]
def cpu():
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime

report = {"release":"0.0.2", "nativeSha256":sha(binary), "projects":{}}
for project in sorted(frozen["projects"], key=lambda p:len(p["preflight"]["baseline"]["inputs"])):
    cwd = Path(project["cwd"])
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==project["commit"]
    inputs = project["preflight"]["baseline"]["inputs"]
    assert all(sha(cwd/entry["file"]) == entry["sha256"] for entry in inputs)
    args = project["compilerArgs"]["baseline"]
    with tempfile.TemporaryDirectory() as tmp:
        experiment = Path(tmp)/"public.er"
        before = cpu()
        run = subprocess.run(["gprofng", "collect","app","-p","10","-a","off","-j","off","-F","off",
                              "-o",experiment,binary,*args], cwd=cwd, env=env, capture_output=True, text=True, timeout=480)
        child_cpu = cpu()-before
        assert run.returncode==0 and all("Creating experiment directory " in line for line in (run.stdout+run.stderr).splitlines()), (run.stdout,run.stderr)
        table = subprocess.check_output(["gprofng","display","text","-limit","0","-functions",experiment],text=True)
        header = subprocess.check_output(["gprofng","display","text","-header",experiment],text=True)
        name = project["name"]
        (here/f"{name}-functions.txt.gz").write_bytes(gzip.compress(table.encode(),mtime=0))
        rows = re.findall(r"^\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(.+)$",table,re.M)
        assert rows and rows[0][-1].strip()=="<Total>", table[:1500]
        total = float(rows[0][0])
        native_rows = [(float(flat),func.strip()) for flat,_,_,_,func in rows[1:] if "sc_bf_" in func]
        report["projects"][name] = dict(commit=project["commit"],files=len(inputs),args=args,childCPUSeconds=child_cpu,
            sampledCPUSeconds=total,scriptcFunctionCount=len(native_rows),topScriptcFlat=native_rows[:15],
            header=header.replace(str(experiment),"<experiment>"),tableSha256=hashlib.sha256(table.encode()).hexdigest())
        (here/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
        print(name, child_cpu, total, native_rows[:3], flush=True)
