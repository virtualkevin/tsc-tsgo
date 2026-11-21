"""Compare callback diagnostics and declaration bytes against the two compiler controls."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
public, control, candidate, libs = sys.argv[1:5]
observer = sys.argv[5:6]
env = dict(os.environ, TSC_TS_LIB_DIR=libs)
cases = {
    "constrained-generics": """
declare function use<F extends (v: string) => void>(f: F): F;
export const captured = use(text => ({ tag: "value" as const, size: text.length }));
export const size: number = captured("x").size;
export const same = use(<T extends string>(text: T) => ({text}));
""",
    "satisfies-and-overloads": """
type Handler = (value: string) => void;
export const handler = ((value) => value.length) satisfies Handler;
declare function choose(f: (x: string) => number): 1;
declare function choose(f: Handler): 2;
export const n = choose(handler);
export const callbacks = { done(value) { return { value }; } } satisfies { done: Handler };
export const v: string = callbacks.done("a").value;
""",
    "contextual-async-and-generator": """
type Handler = (value: number) => void;
export const asyncCallback = (async v => ({v})) satisfies Handler;
export const generator = (function* (v) { yield v; return [v] as const; }) satisfies Handler;
export const promised: Promise<{v:number}> = asyncCallback(4);
""",
    "recursive-and-conditional": """
type Handler = (value: number) => void;
export const handlers = {
  walk: (n => n > 0 ? handlers.walk(n-1) : 0) satisfies Handler,
  mixed: ((v) => v ? { value: v } : undefined) satisfies Handler
};
export const result = handlers.mixed(1);
""",
    "diagnostic-inside-context": """
declare function listen(callback: (row: {name:string}) => void): void;
listen(row => ({name: row.missing}));
listen(row => { const wrong: number = row.name; return wrong; });
""",
    "discarded-and-retained": """
declare function store<T extends (v: number) => void>(cb: T): T;
export const tuple = store(v => [v, 1] as const);
export const value = tuple(2)[0];
export const impossible: string = value;
""",
    "flow-and-generic-inference": """
declare function forward<T>(value: T, fn: (item: T) => void): T;
export function run<T extends {id:string}>(arg: T | undefined) {
  if (arg) return forward(arg, item => item.id);
}
export function runAgain() {
  let value: string | undefined = "text";
  const cb = ((n: number) => value?.slice(n)) satisfies (n:number) => void;
  value = undefined;
  return cb(2);
}
""",
}
rows = {}
for label, source in cases.items():
    with tempfile.TemporaryDirectory() as directory:
        cwd = Path(directory)
        (cwd/"input.ts").write_text(source.strip()+"\n")
        outputs = []
        for index, binary in enumerate((public, control, candidate, *observer)):
            dest = f"out{index}"
            args = ["input.ts", "--ignoreConfig", "--pretty", "false", "--strict", "--target", "es2022",
                    "--module", "esnext", "--declaration", "--emitDeclarationOnly", "--outDir", dest]
            r = subprocess.run([binary, *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=60)
            if index == 3:
                observed = json.loads(r.stderr)
            else:
                assert not r.stderr, (label,r.stderr)
            outputs.append(dict(status=r.returncode, diagnostics=r.stdout,
                                declaration=(cwd/dest/"input.d.ts").read_text()))
        rows[label] = dict(public=outputs[0], goMatchesPublic=outputs[0]==outputs[1], candidateMatchesGo=outputs[1]==outputs[2])
        if observer:
            assert outputs[3] == outputs[2]
            rows[label]["deferrals"] = sum(r["New"] for r in observed or [])
        if outputs[0] != outputs[1]: rows[label]["control"] = outputs[1]
        if outputs[1] != outputs[2]: rows[label]["candidate"] = outputs[2]
        print(label, rows[label]["goMatchesPublic"], rows[label]["candidateMatchesGo"], flush=True)
(here/"checks.json").write_text(json.dumps(rows, indent=2)+"\n")
assert all(r["goMatchesPublic"] and r["candidateMatchesGo"] for r in rows.values())
