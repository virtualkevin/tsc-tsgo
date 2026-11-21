"""Verify repeated, changed and restored attribute shapes, including semantic children."""
import json
from pathlib import Path
import sys
import tempfile

here = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0,str(here.parent/"jsx-absent-discriminants"))
import scaling

scaling.bins = dict(zip(("native","ordinary","candidate"), map(lambda s:Path(s).resolve(),sys.argv[1:]),strict=True))
keys = " | ".join(f'"k{i}"' for i in range(64))
base = f'''
type Key = {keys};
type A = {{[P in Key]?: 0}} & {{ value: string; mode?: "a"; children?: string }};
type B = {{[P in Key]?: 1}} & {{ value: number; mode: "b"; children?: number }};
declare global {{ namespace JSX {{
    interface Element {{}} interface ElementChildrenAttribute {{children: {{}}}}
    interface IntrinsicElements {{ box: A | B }}
}} }}
export const items = [
    <box value="one" />, <box value="two" />, <box value="three">{{/* empty */}}</box>,
    <box value="four">{{"text"}}</box>, <box mode="b" value={{2}}>{{3}}</box>,
    <box value="five" k1={{0}}/>, <box value="six" k2={{0}}/>, <box value="seven" k1={{0}}/>,
    <box value="eight" />, <box value="nine" />,
];
'''
report = {"binaries":{name:scaling.sha(path.read_bytes()) for name,path in scaling.bins.items()},
          "flags":[*scaling.flags,"--declaration","--emitDeclarationOnly"]}
with tempfile.TemporaryDirectory() as tmp:
    for label, text in (("clean",base),("error",base+'export const bad = <box mode="b" value="wrong"/>;\n')):
        records = []
        for engine in scaling.bins:
            cwd=Path(tmp)/label/engine
            cwd.mkdir(parents=True)
            (cwd/"case.tsx").write_text(text)
            result,_=scaling.invoke(engine,["--declaration","--emitDeclarationOnly"],cwd)
            assert result.returncode == (0 if label == "clean" else 2), (engine,label,result.stdout,result.stderr)
            if label == "error": assert b"TS2322" in result.stdout
            records.append((result.returncode,result.stdout,result.stderr,(cwd/"case.d.ts").read_bytes()))
        assert records[0] == records[1] == records[2]
        report[label]={"sourceSha256":scaling.sha(text.encode()),"exit":records[0][0],
                       "stdoutSha256":scaling.sha(records[0][1]),"declarationSha256":scaling.sha(records[0][3])}
(here/"history.json").write_text(json.dumps(report,indent=2)+"\n")
