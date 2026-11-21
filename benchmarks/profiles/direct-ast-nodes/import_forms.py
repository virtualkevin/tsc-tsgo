"""Compare import parsing, diagnostics and emitted output for two CLI builds."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

binaries = [Path(arg).resolve() for arg in sys.argv[1:]]
assert len(binaries) == 2
files = {
    "lib.ts": "export default 1; export const x = 2; export type T = { x: number };",
    "check.ts": """import d, {x, type T} from './lib';
import type * as Types from './lib';
import './lib';
import ns = require('./lib');
export const v: Types.T = {x: d + x + ns.x};
export type A = T;
""",
    "doc.js": """/** @import { T } from "./lib" */
/** @type {T} */
export const obj = { x: 1 };
""",
}
with tempfile.TemporaryDirectory() as tmp:
    cwd = Path(tmp)
    for name, source in files.items():
        (cwd / name).write_text(source)
    for malformed in (False, True):
        if malformed:
            (cwd / "check.ts").write_text("import type { T as } from './lib';\n" + files["check.ts"])
        comparisons = []
        for index, binary in enumerate(binaries):
            output = cwd / f"out-{malformed}-{index}"
            args = ["--pretty", "false", "--allowJs", "--checkJs", "--strict", "--declaration",
                    "--module", "commonjs", "--target", "es2022", "--outDir", str(output), *files]
            run = subprocess.run([binary, *args], cwd=cwd, capture_output=True, timeout=60)
            artifacts = {p.relative_to(output).as_posix(): p.read_bytes() for p in output.rglob("*") if p.is_file()}
            assert bool(run.returncode) == malformed, (binary, run.stdout, run.stderr)
            assert "doc.d.ts" in artifacts and "check.js" in artifacts
            comparisons.append((run.returncode, run.stdout, run.stderr, artifacts))
        assert comparisons[0] == comparisons[1], malformed
        print(json.dumps({"malformed": malformed, "exit": comparisons[0][0],
                          "emitted": sorted(comparisons[0][3]), "diagnostics": comparisons[0][1].decode()}))
