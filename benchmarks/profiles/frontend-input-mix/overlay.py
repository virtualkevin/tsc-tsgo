"""Apply pprof labels to file-loader requests, preserving parser inputs and outputs."""
import json
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[3]
out=Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
p=root/"packages/tsc-go/internal/compiler/fileloader.go"
s=subprocess.check_output(["git","show","a261586:"+str(p.relative_to(root))],cwd=root,text=True)
s=s.replace('import (','import (\n "context"\n "os"\n "runtime/pprof"',1)
site="func (p *fileLoader) parseSourceFile(t *parseTask) *ast.SourceFile {"
assert s.count(site)==1
s=s.replace(site,"""var profiledLibDirectory = strings.TrimRight(os.Getenv("TSC_TS_LIB_DIR"), "/") + "/"

func sourceInputClass(path string) string {
    if profiledLibDirectory != "/" && strings.HasPrefix(path, profiledLibDirectory) { return "compiler library" }
    category := "project or workspace"
    if strings.Contains(path, "/node_modules/") { category = "node_modules" }
    if strings.HasSuffix(path,".d.ts") || strings.HasSuffix(path,".d.cts") || strings.HasSuffix(path,".d.mts") {
        return category+" / declaration"
    }
    return category+" / other input"
}
"""+site+"""
    var file *ast.SourceFile
    pprof.Do(context.Background(), pprof.Labels("source-input",sourceInputClass(t.normalizedFilePath)), func(context.Context) {
        file = p.profiledParseSourceFile(t)
    })
    return file
}
func (p *fileLoader) profiledParseSourceFile(t *parseTask) *ast.SourceFile {""")
(out/p.name).write_text(s)
checker=root/"packages/tsc-go/internal/checker/checker.go"
(out/checker.name).write_bytes(subprocess.check_output(["git","show","a261586:"+str(checker.relative_to(root))],cwd=root))
(out/"overlay.json").write_text(json.dumps({"Replace":{str(f):str(out/f.name) for f in (p,checker)}}))
