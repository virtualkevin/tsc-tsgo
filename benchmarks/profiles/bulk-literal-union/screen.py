"""Time fresh compiler processes on deterministic, fully checked literal unions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import tempfile
import time

parser = argparse.ArgumentParser(description=__doc__)
for name in ("native", "control", "candidate", "output"):
    parser.add_argument("--" + name, type=Path, required=True)
parser.add_argument("--grouped", action="store_true", help="measure merging sorted constituent unions")
parser.add_argument("--class-keys", action="store_true", help="measure keyof with a private member among public string keys")
args = parser.parse_args()
root = Path(__file__).resolve().parents[3]
binaries = {name: getattr(args, name).resolve() for name in ("native", "control", "candidate")}
env = {**os.environ, "TSC_TS_LIB_DIR": str(root / "upstream/typescript-go/internal/bundled/libs")}
def digest(data):
    return hashlib.sha256(data).hexdigest()

def check(name, cwd):
    start = time.perf_counter_ns()
    proc = subprocess.run([binaries[name], "-p", ".", "--pretty", "false"], cwd=cwd,
                          env=env, capture_output=True, timeout=180)
    return (time.perf_counter_ns() - start) / 1e6, proc

report = {"binarySha256": {k: digest(v.read_bytes()) for k, v in binaries.items()}, "projects": []}
with tempfile.TemporaryDirectory() as tmp:
    cwd = Path(tmp)
    (cwd / "tsconfig.json").write_text(json.dumps({"compilerOptions": {
        "noEmit": True, "strict": True, "types": [], "skipLibCheck": True,
        "incremental": False}, "files": ["main.ts"]}))
    cases = [(4096, "descending"), (32768, "ascending"), (32768, "descending"),
             (131072, "descending"), (32768, "keyof-permuted")]
    if args.grouped:
        cases = [(4096, "interleaved"), (32768, "interleaved"), (131072, "interleaved"),
                 (32768, "overlapping"), (32768, "disjoint")]
    if args.class_keys:
        assert not args.grouped
        cases = [(4096, "private-key"), (32768, "private-key"), (131072, "private-key")]
    for count, order_name in cases:
        members = [f'"k{i:06d}"' for i in range(count)]
        if order_name == "descending":
            members.reverse()
        source = "type Key = " + " | ".join(members) + ';\nconst valid: Key = "k000000";\n'
        if order_name == "keyof-permuted":
            # The odd stride visits each key exactly once at this power-of-two size.
            fields = [f"{members[i * 8191 % count]}: number;" for i in range(count)]
            source = "interface Model {\n" + "\n".join(fields) + '\n}\ntype Key = keyof Model;\nconst valid: Key = "k000000";\n'
        if order_name == "private-key":
            fields = [f"{name}: number;" for name in reversed(members)]
            source = "declare class Model {\nprivate hidden: number;\n" + "\n".join(fields) + '\n}\ntype Key = keyof Model;\nconst valid: Key = "k000000";\n'
        if args.grouped:
            if order_name == "interleaved":
                left, right = members[::2], members[1::2]
            elif order_name == "overlapping":
                left, right = members[:3*count//4], members[count//4:]
            else:
                left, right = members[count//2:], members[:count//2]
            source = ("type Left = " + " | ".join(left) + ";\n"
                      + "type Right = " + " | ".join(right) + ";\n"
                      + 'type Key = Left | Right;\nconst valid: Key = "k000000";\n')
        path = cwd / "main.ts"
        invalid = "hidden" if order_name == "private-key" else "absent"
        path.write_text(source + f'const invalid: Key = "{invalid}";\n')
        outputs = []
        for name in binaries:
            _, proc = check(name, cwd)
            assert proc.returncode and not proc.stderr and b"error TS2322:" in proc.stdout, proc
            outputs.append((proc.returncode, proc.stdout))
        assert len(set(outputs)) == 1
        path.write_text(source)
        timings = []
        for block in range(-1, 3):
            order = list(binaries)
            rotate = max(0, block)
            order = order[rotate:] + order[:rotate]
            sample = {}
            for name in order:
                ms, proc = check(name, cwd)
                assert (proc.returncode, proc.stdout, proc.stderr) == (0, b"", b""), proc
                sample[name] = ms
            if block >= 0:
                timings.append(sample)
        result = dict(members=count, order=order_name, sourceSha256=digest(path.read_bytes()),
                      diagnosticsSha256=digest(outputs[0][1]), blocksMs=timings,
                      medianMs={k: statistics.median(t[k] for t in timings) for k in binaries})
        report["projects"].append(result)
        print(count, order_name, result["medianMs"], flush=True)
args.output.write_text(json.dumps(report, indent=2) + "\n")
