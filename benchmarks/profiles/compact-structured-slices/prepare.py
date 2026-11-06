from pathlib import Path
import hashlib,json,re,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2];m=r/'packages/tsc-go';st=p/'staged';paths={};base={};changes=[]
def stage(name,s):
 f=st/name;f.write_text(s);subprocess.run(['/tmp/tsc-toolchains/go/bin/gofmt','-w',str(f)],check=True);paths[str(m/'internal/checker'/name)]=str(f)
for name in ['types.go','checker.go','pending_members.go','lazy_properties.go','nodebuilderimpl.go','relater.go']:
 src=m/'internal/checker'/name;s=src.read_text();base[str(src.relative_to(m))]=hashlib.sha256(src.read_bytes()).hexdigest()
 if name=='types.go':
  for field,elem in [('properties','ast.Symbol'),('signatures','Signature'),('indexInfos','IndexInfo')]:
   s,n=re.subn(r'(\b'+field+r'\s+)\[\]\*'+re.escape(elem)+r'\b',r'\1compactSlice[*'+elem+']',s,count=1);assert n==1
 lines=[]
 for line in s.splitlines(keepends=True):
  # These are different structs and remain ordinary slices.
  protected=line.replace('.composite.signatures','.composite.__ordinarySignatures').replace('base.properties','base.__ordinaryProperties')
  write=re.match(r'^(\s*)(.+\.(?:properties|signatures|indexInfos)) = (.*)\n$',protected)
  if write:
   ws,lhs,rhs=write.groups();rhs=re.sub(r'\.(properties|signatures|indexInfos)\b',r'.\1.Values()',rhs)
   updated=ws+lhs+' = compactSliceFrom('+rhs+')\n'
   if rhs=='nil':
    assert lhs.endswith('.signatures');updated=ws+lhs+' = compactSliceFrom([]*Signature(nil))\n'
  else:updated=re.sub(r'\.(properties|signatures|indexInfos)\b',r'.\1.Values()',protected)
  updated=updated.replace('.composite.__ordinarySignatures','.composite.signatures').replace('base.__ordinaryProperties','base.properties')
  if updated!=line:changes.append({'file':name,'before':line.rstrip(),'after':updated.rstrip()})
  lines.append(updated)
 stage(name,''.join(lines))
s=(p.parent/'compact-slice-header/prototype/slice.go').read_text().replace('package compactslice','package checker')
s=re.sub(r'\bSlice\[','compactSlice[',s)
for old,new in [('From','compactSliceFrom'),('pack','packCompactSlice'),('indirectShape','compactSliceIndirectShape'),('indirect','indirectCompactSlice')]:s=re.sub(r'\b'+old+r'\b',new,s)
stage('compact_slice.go',s)
stage('compact_structured_slices_test.go',(st/'compact_structured_slices_test.go').read_text())
(p/'overlay.json').write_text(json.dumps({'Replace':paths},indent=2)+'\n');(p/'base.json').write_text(json.dumps(base,indent=2)+'\n');(p/'changes.json').write_text(json.dumps(changes,indent=2)+'\n')
print('Staged',len(paths),'files;',len(changes),'access/write lines')
