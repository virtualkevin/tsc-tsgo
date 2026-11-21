"""Size the transient symbol table from the last finalized instance of this source."""
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
repo = here.parents[2]
file = "packages/tsc-go/internal/checker/pending_members.go"
source = subprocess.check_output(["git", "show", "bd1baea:" + file], cwd=repo, text=True)
site = "table := make(ast.SymbolTable, len(p.source.entries))"
assert source.count(site) == 1
source = source.replace(site, """// Instantiations of the same declaration often inherit the same property
	// names. The prior completed layout supplies only a capacity hint.
	capacity := len(p.source.entries)
	if previous := p.source.lastMemberNames; previous != nil && p.hasBases && !p.resolving {
		capacity = max(capacity, min(4096, len(previous.names)))
	}
	table := make(ast.SymbolTable, capacity)""")
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
dest = out / "pending_members.go"
dest.write_text(source)
(out / "overlay.json").write_text(json.dumps({"Replace": {str(repo / file): str(dest)}}))
