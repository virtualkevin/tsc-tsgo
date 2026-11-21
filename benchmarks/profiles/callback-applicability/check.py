"""Compare diagnostics and emitted declarations for object member storage paths."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

here=Path(__file__).resolve().parent
public, control, candidate, libs=sys.argv[1:]
source="""
declare const key: string, index: number, sym: symbol;
declare function same<T>(actual:unknown, expected:T): asserts actual is T;
export function checked(x: unknown) {
    same(x,{n:1, data:[2,3], m(s:string){return s}});
    return x;
}
declare const fixed: { a: number }, maybe: { a?: string };
export const plain = { a: 1, get b(){return this.a}, method(){return this.b} };
export const spread = { a:"error", ...fixed, ...maybe, c: 1 };
export const indexed = { z: false, [key]: 1, [index]: 2, [sym]: "k" };
export const segments = { a:"error", ...fixed, [key]:true, ...maybe, [sym]:5 };
export function destructure(obj:{a:number}) { let x: number; ({a:x} = obj); return x }
"""
report={}
for strict in ("true","false"):
    with tempfile.TemporaryDirectory() as tmp:
        cwd=Path(tmp)
        (cwd/"input.ts").write_text(source)
        runs=[]
        for binary in (public,control,candidate):
            r=subprocess.run([binary,"input.ts","--ignoreConfig","--target","es2022","--module","esnext","--declaration","--emitDeclarationOnly","--strict",strict,"--pretty","false"],cwd=cwd,env=dict(os.environ,TSC_TS_LIB_DIR=libs),text=True,capture_output=True,timeout=60)
            out=cwd/"input.d.ts"
            runs.append(dict(code=r.returncode,stdout=r.stdout,stderr=r.stderr,emit=out.read_text()))
            out.unlink()
        assert runs[0]==runs[1]==runs[2] and ("TS2783" in runs[0]["stdout"])==(strict=="true")
        report[strict]=runs[0]
(here/"checks.json").write_text(json.dumps(report,indent=2)+"\n")
