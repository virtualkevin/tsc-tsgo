"""Check tuple spread types, diagnostic locations and declaration emit against public npm."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
public, control, candidate, libs = sys.argv[1:]
common = """
declare function both<T extends readonly unknown[], U extends readonly unknown[]>(x: T, y: U): [...T, ...U];
declare const source: readonly [first: string, second: number];
declare const optional: [name?: string];
declare const variadic: [id: number, ...tags: boolean[]];
declare const union: [x: 1] | [y: 2, z: 3];
export const middle = both(both([true] as const, source), ['end'] as const);
export const empty = both([] as const, source);
export const optionalBeforeRequired = both(optional, source);
export const restBeforeRequired = both(variadic, source);
export const requiredBeforeOptional = both(source, optional);
export const alternatives = both(source, union);
"""
large = "type Double<T extends unknown[]> = [...T, ...T];\ntype T0 = [0];\n"
large += "\n".join(f"type T{i} = Double<T{i-1}>;" for i in range(1,14))
cases = {"labels": (common, None),
         "invalid": (common + "export const bad: number = middle[1];", "TS2322"),
         "tooLarge": (large + "\nexport type TooLarge = Double<T13>;", "TS2799")}
report = {}
for case, (source, error) in cases.items():
    results = []
    for binary in (public, control, candidate):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / "input.ts").write_text(source)
            r = subprocess.run([binary, "input.ts", "--ignoreConfig", "--strict", "--skipLibCheck", "--pretty", "false",
                                "--declaration", "--emitDeclarationOnly"], cwd=cwd, env=dict(os.environ,TSC_TS_LIB_DIR=libs),
                               capture_output=True, timeout=120)
            decl = (cwd/"input.d.ts").read_bytes()
            assert not r.stderr and bool(r.returncode) == bool(error)
            assert error in r.stdout.decode() if error else not r.stdout
            results.append((r.returncode, r.stdout.decode(), hashlib.sha256(decl).hexdigest()))
    assert results[0] == results[1] == results[2], (case,results)
    report[case] = results[0]
(here/"checks.json").write_text(json.dumps(report,indent=2)+"\n")
