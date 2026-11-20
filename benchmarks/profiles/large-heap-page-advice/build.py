"""Build the size-aware Linux executable in the Go package's dist directory."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
package = here.parents[2] / "packages/tsc-go"
go = os.environ.get("GO", "go")
goroot, goos = subprocess.check_output([go,"env","GOROOT","GOOS"],cwd=package,text=True).splitlines()
if goos != "linux":
    sys.exit("The size-aware heap mapping experiment targets Linux.")
output = package / "dist/tsc-go-large-heap-pages"
output.parent.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    overlay = Path(tmp)
    subprocess.run([sys.executable,here/"overlay.py",goroot,overlay],check=True)
    subprocess.run([go,"build","-buildvcs=false","-trimpath","-gcflags=github.com/microsoft/typescript-go/...=-l=4",
                    "-overlay="+str(overlay/"overlay.json"),"-o",output,"./cmd/tsgo"],cwd=package,check=True)
print(output)
