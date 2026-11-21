"""Vary mapped type width while reading one fixed property of an intersection."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

here=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(here.parent/"jsx-absent-discriminants"))
import scaling

binary=Path(sys.argv[1]).resolve()
scaling.bins={"observer":binary}
report={"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"cases":{}}
with tempfile.TemporaryDirectory() as tmp:
    cwd=Path(tmp)
    for family in ("literalKeys","keyof"):
        report["cases"][family]={}
        for width in (16,256,1024):
            names=[f"key{i}" for i in range(width)]
            if family=="literalKeys":
                definition="type Key = "+" | ".join(f'"{n}"' for n in names)+";\n"
                definition+="type Fields = { [K in Key]: string };\n"
            else:
                definition="interface Model { "+"; ".join(f"{n}: string" for n in names)+" }\n"
                definition+="type Copy<T> = { [K in keyof T]?: T[K] };\ntype Fields = Copy<Model>;\n"
            report["cases"][family][width]={}
            for demand in ("unrelated","oneMapped","allMapped"):
                expression={"unrelated":"input.count","oneMapped":"input.key0",
                            "allMapped":"["+",".join("input."+n for n in names)+"]"}[demand]
                text=definition+"export function read(input: Fields & {count: number}) {return "+expression+"}\n"
                (cwd/"case.tsx").write_text(text)
                result,_=scaling.invoke("observer",["--noEmit"],cwd)
                assert result.returncode==0 and not result.stdout
                counts=json.loads(result.stderr)
                expected={"unrelated":0,"oneMapped":1,"allMapped":width}[demand]
                assert len(counts)==47 and counts[34:38]==[width,0,0,expected]
                assert counts[41 if family=="literalKeys" else 44]==width
                report["cases"][family][width][demand]={
                    "sourceSha256":scaling.sha(text.encode()),"newMappedSymbolsRecorded":counts[34],
                    "explicitStringKeysRecorded":counts[41],"keyofStringKeysRecorded":counts[44],
                    "dropped":counts[35],"firstAccessorInside":counts[36],"firstAccessorOutside":counts[37],
                    "mappedResolutionCalls":counts[18],"symbolsCreatedDuringMappedResolution":counts[21]}
(here/"heuristic-fixture.json").write_text(json.dumps(report,indent=2)+"\n")
