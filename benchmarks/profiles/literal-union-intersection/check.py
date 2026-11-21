"""Check optimized and fallback intersection cases against an independent set oracle."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

bins = [Path(a).resolve() for a in sys.argv[1:]]
assert len(bins) >= 2
root = Path(__file__).resolve().parents[3]
env = dict(os.environ, TSC_TS_LIB_DIR=str(root / "upstream/typescript-go/internal/bundled/libs"))

def union(keys):
    return " | ".join(f'"k{i:03}"' for i in sorted(keys))

a = set(range(0, 150, 2))
cases = [
    ("overlap", set(range(0, 150, 3))),
    ("none", set(range(1, 150, 2))),
    ("singleton", {0, *range(1, 150, 2)}),
    ("contained", set(range(0, 150, 4))),
]
lines = ["type Equal<A, B> = [A] extends [B] ? ([B] extends [A] ? true : false) : false;",
         "type Assert<T extends true> = T;", "type A = " + union(a) + ";"]
for name, b in cases:
    lines += [f"type B{name} = {union(b)};", f"type E{name} = {union(a & b) or 'never'};",
              f"type T{name} = Assert<Equal<A & B{name}, E{name}>>;",
              f"type R{name} = Assert<Equal<B{name} & A, E{name}>>;"]
lines += ["type W = Assert<Equal<A & (string | number), A>>;",
          "type M = Assert<Equal<(A | 7) & (Boverlap | 7), Eoverlap | 7>>;",
          "type N = Assert<Equal<(A | null) & (Bnone | null), null>>;",
          "type Three = Assert<Equal<A & Boverlap & Bcontained, " + union(a & cases[0][1] & cases[-1][1]) + ">>;"]
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "sets.ts"
    for bad in (False, True):
        source = lines + (['const bad: A & Boverlap = "k000";', 'const wrong: A & Boverlap = "k002";'] if bad else [])
        path.write_text("\n".join(source) + "\n")
        outputs = []
        for binary in bins:
            r = subprocess.run([binary, "--ignoreConfig", "--strict", "--noEmit", "--lib", "es5",
                                "--pretty", "false", path.name], cwd=tmp, env=env, capture_output=True, timeout=60)
            assert (r.returncode != 0) == bad and not r.stderr, (binary, r.stdout, r.stderr)
            if bad:
                assert r.stdout.count(b"error TS2322") == 1
            outputs.append(r.stdout)
        assert len(set(outputs)) == 1
        print("invalid" if bad else "valid", len(bins), "compilers agree")
