"""Vary trailing service tuple length in the pinned VS Code constructor signature."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
public,control,candidate,libs = sys.argv[1:5]
observer = sys.argv[5:6]
trace = {}
ref=json.loads(gzip.decompress((here.parent/"named-key-union/public.json.gz").read_bytes()))
vs=next(p for p in ref["projects"] if p["name"]=="vscode")
source=Path(vs["cwd"])/"src/vs/platform/instantiation/common/instantiation.ts"
expected=next(r["sha256"] for r in vs["preflight"]["candidate"]["inputs"] if r["file"]==str(source.relative_to(vs["cwd"])))
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
code=source.read_text()
trim,=re.findall(r"export type GetLeadingNonServiceArgs[^;]+;",code)
service,=re.findall(r"export type BrandedService = .*?;",code)
make,=re.findall(r"createInstance<Ctor extends new [^;]+;",code)
env=dict(os.environ,TSC_TS_LIB_DIR=libs)
report=dict(sourceSha256=expected,commit=vs["commit"],trials={})
for count,depth in [(1,0),(128,0),(128,1),(128,4),(128,12)]:
    # Keep call count, class distinctness and number of caller-supplied arguments fixed.
    text=[service,trim,"interface Factory {"+make+"}","declare const factory:Factory;"]
    for i in range(count):
        params=[f"x: {i}"]+[f"s{j}:BrandedService & {{ readonly tag:{j} }}" for j in range(depth)]
        text.extend([f"declare class C{i} {{ readonly marker:{i}; constructor({', '.join(params)}); }}",
                     f"export const x{i}=factory.createInstance(C{i},{i});"])
    text.append("export const invalid=factory.createInstance(C0,'wrong');")
    with tempfile.TemporaryDirectory() as tmp:
        cwd=Path(tmp)
        (cwd/"input.ts").write_text("\n".join(text))
        outputs=[]
        metrics={}
        binaries = [("public",public),("go",control),("candidate",candidate)]
        if observer:
            binaries.append(("observer",observer[0]))
        for e,binary in binaries:
            r=subprocess.run([binary,"input.ts","--ignoreConfig","--strict","--skipLibCheck","--pretty","false",
                "--target","es2022","--module","esnext","--declaration","--emitDeclarationOnly","--extendedDiagnostics"],
                env=env,cwd=cwd,text=True,capture_output=True,timeout=90)
            assert r.returncode!=0
            if e=="observer":
                observations=json.loads(r.stderr)
                rows=[v for k,v in observations.items() if k.endswith(" createInstance")]
                assert len(rows)==1
                trace[f"{count}-classes-{depth}-services"]={k.replace(str(cwd)+"/","").replace(libs+"/",""):v for k,v in rows[0].items()}
            else:
                assert not r.stderr
            diag=[l for l in r.stdout.splitlines() if "error TS" in l]
            assert len(diag)==1 and ("TS2345" in diag[0] or "TS2769" in diag[0]),diag
            decl=(cwd/"input.d.ts").read_text()
            assert all(f"export declare const x{i}: C{i};" in decl for i in range(count))
            outputs.append((diag,decl))
            metrics[e]={k:int(v.replace(",","")) for k,v in re.findall(r"^(Types|Instantiations):\s*([\d,]+)",r.stdout,re.M)}
            assert metrics[e].keys()=={"Types","Instantiations"}
            (cwd/"input.d.ts").unlink()
        assert all(o==outputs[0] for o in outputs)
        if observer:
            assert metrics.pop("observer")==metrics["go"]
        report["trials"][f"{count}-classes-{depth}-services"]=dict(metrics=metrics,diagnostic=outputs[0][0],declarationSha256=hashlib.sha256(outputs[0][1].encode()).hexdigest())
        print(count,depth,metrics,flush=True)
(here/"constructors.json").write_text(json.dumps(report,indent=2)+"\n")

if observer:
    (here/"constructor-conditionals.json").write_text(json.dumps(trace,indent=2,sort_keys=True)+"\n")
