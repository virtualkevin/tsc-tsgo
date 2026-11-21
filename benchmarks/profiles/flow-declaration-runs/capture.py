"""Measure the number of declaration comparisons saved on frozen projects."""
from pathlib import Path
import hashlib
import json
import sys

here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent))
from frozen_checks import observed_projects
binary=Path(sys.argv[1]).resolve()
report={"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"projects":{}}
for project, commit, counts in observed_projects(binary):
    runs, scanned, hits, inherited = counts
    assert runs >= hits and inherited >= hits
    report["projects"][project] = {"commit":commit,"nonemptyRuns":runs,"freshlySkippedDeclarations":scanned,
                                    "reusedRuns":hits,"skippedViaReuse":inherited}
    print(project, counts, flush=True)
(here/"counts.json").write_text(json.dumps(report,indent=2)+"\n")
