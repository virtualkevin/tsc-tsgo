"""Cross-tabulate type access, named lookup, and whole-container exposure."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

here=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path[:0]=[str(here.parent),str(here.parent/"jsx-absent-discriminants")]
from frozen_checks import observed_projects
import scaling

binary=Path(sys.argv[1]).resolve()
scaling.bins={"observer":binary}
labels=("other","explicitStringKeys","keyofStringKeys")
def summarize(data):
    buckets=data["Cohorts"]
    assert len(buckets)==3 and all(len(b)==16 and all(v>=0 for v in b) for b in buckets)
    totals=[sum(v) for v in zip(*buckets,strict=True)]
    return {"dropped":data["Dropped"],"tracked":sum(totals),"noneOfFour":totals[0],
            "namedLookup":sum(n for i,n in enumerate(totals) if i&2),
            "typeAccessor":sum(n for i,n in enumerate(totals) if i&1),
            "ownerContainerExposed":sum(n for i,n in enumerate(totals) if i&12),
            "byMask":dict(zip(labels,buckets,strict=True))}
report={"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),
        "maskBits":["type accessor","named lookup returned symbol","owner Properties()","owner Members()"],
        "fixture":{},"projects":{}}
with tempfile.TemporaryDirectory() as tmp:
    cwd=Path(tmp)
    for width in (16,256,1024):
        names=[f"k{i}" for i in range(width)]
        cases={"unrelated":"v.count","one":"v.k0","all":"["+",".join("v."+n for n in names)+"]","spread":"({...v})"}
        report["fixture"][width]={}
        for case,expr in cases.items():
            text="type Keys="+"|".join(repr(n) for n in names)+";\n"
            text+="type Fields={ [K in Keys]: string };\nexport function read(v: Fields & {count:number}) {return "+expr+"}\n"
            (cwd/"case.tsx").write_text(text)
            result,_=scaling.invoke("observer",["--noEmit"],cwd)
            assert result.returncode==0 and not result.stdout
            row=summarize(json.loads(result.stderr))
            assert row["tracked"]==width and not row["dropped"]
            if case!="spread": assert row["typeAccessor"]=={"unrelated":0,"one":1,"all":width}[case]
            assert row["noneOfFour"] == {"unrelated":width,"one":width-1,"all":0,"spread":0}[case]
            report["fixture"][width][case]={**row,"sourceSha256":scaling.sha(text.encode())}
for name,commit,data in observed_projects(binary):
    row=summarize(data)
    report["projects"][name]={"commit":commit,**row}
    print(name,{k:v for k,v in row.items() if k!="byMask"},flush=True)
(here/"counts.json").write_text(json.dumps(report,indent=2)+"\n")
