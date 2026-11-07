from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parent;r=p.parents[2];base=r/'packages/tsc-go/internal/checker'
freeze=json.loads((p/'freeze.json').read_text());sha=lambda s:hashlib.sha256(s).hexdigest()
for name,h in freeze.items():
 assert sha((p/'staged'/name).read_bytes())==h['stagedSha256']
 if h['baselineSha256']:assert sha((base/name).read_bytes())==h['baselineSha256']
a=(base/'lazy_properties.go').read_text();b=(p/'staged/lazy_properties.go').read_text()
b=b[:b.index('// Scratch belongs exclusively')].rstrip()+'\n'
b=b.replace('\tscratch := c.acquireReductionScratch()\n\tbyName := scratch.byName\n\tnames := scratch.names\n\tdefer func() { c.releaseReductionScratch(scratch, names) }()', '\tbyName := make(map[string][]*ast.Symbol)\n\tvar names []string',1)
b=b.replace('\t\t\t\tindex := len(names)\n','',1)
b=b.replace('\t\t\t\tif index == len(scratch.buffers) {\n\t\t\t\t\tscratch.buffers = append(scratch.buffers, nil)\n\t\t\t\t}\n\t\t\t\tprops = scratch.buffers[index][:0]\n','',1)
assert b==a,'Unexpected algorithm change beyond scratch acquisition/buffer selection/release'
assert (p/'staged/checker.go').read_text().replace('\treductionScratch                            *reductionScratch\n','',1)==(base/'checker.go').read_text()
(p/'source-audit.json').write_text(json.dumps({'passed':True,'scope':'Exact inverse verifies original checker and reduction algorithm after removing declared scratch additions; helper ownership argument is separate.','files':freeze},indent=2)+'\n')
print('Exact inverse source audit passed')
