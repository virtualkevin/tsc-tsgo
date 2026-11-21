"""Label the top-level TS source file whose checking triggered sampled CPU work."""
from pathlib import Path
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True,parents=True)
path = Path("packages/tsc-go/internal/checker/checker.go")
s = subprocess.check_output(["git","show",f"e1eeaab:{path}"],cwd=root,text=True)
if '"runtime/pprof"' not in s:
    s = s.replace('"context"', '"context"\n "runtime/pprof"',1)
marker = "func (c *Checker) checkSourceFile(ctx context.Context, sourceFile *ast.SourceFile, checkUnused bool) {"
assert s.count(marker)==1
s=s.replace(marker, marker+"""
    pprof.Do(ctx,pprof.Labels("ts-file",sourceFile.FileName()),func(_ context.Context){
        c.checkSourceFileLabelled(ctx,sourceFile,checkUnused)
    })
}

func (c *Checker) checkSourceFileLabelled(ctx context.Context, sourceFile *ast.SourceFile, checkUnused bool) {""")
target = out/"checker.go"
target.write_text(s)
(out/"overlay.json").write_text(json.dumps({"Replace":{str(root/path):str(target)}}))
