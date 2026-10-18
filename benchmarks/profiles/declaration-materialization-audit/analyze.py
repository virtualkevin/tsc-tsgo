from pathlib import Path
import importlib.util, hashlib, json, tarfile, sys
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'ast-arena-audit'
spec=importlib.util.spec_from_file_location('heap_parser',BASE/'analyze.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
PREFIX='github.com/microsoft/typescript-go/'
DECL=PREFIX+'internal/transformers/declarations.'
FACTORY=PREFIX+'internal/ast.(*NodeFactory).'
def classify(frames):
    # Stack membership includes callees; factory attribution is a subset.
    declaration=any(f.startswith(DECL) for f in frames)
    return declaration, declaration and any(f.startswith(FACTORY) for f in frames)
def analyze(raw):
    totals=[0]*4;decl=[0]*4;factory=[0]*4;owners={};declarationSamples=0;positiveDeclarationSamples=0
    for values,frames in parser.parse(raw):
        totals=[a+b for a,b in zip(totals,values)]
        yes,syntax=classify(frames)
        if yes:
            declarationSamples+=1
            positiveDeclarationSamples+=int(any(values))
            decl=[a+b for a,b in zip(decl,values)]
        if syntax:
            factory=[a+b for a,b in zip(factory,values)]
            owner=next(f for f in frames if f.startswith(FACTORY))
            owners[owner]=[a+b for a,b in zip(owners.get(owner,[0]*4),values)]
    assert all(0<=f<=d<=t for f,d,t in zip(factory,decl,totals))
    names=parser.METRICS
    return {'declarationStackSampleRecords':declarationSamples,'positiveDeclarationStackSampleRecords':positiveDeclarationSamples,'total':dict(zip(names,totals)),'declarationInclusive':dict(zip(names,decl)),'factoryUnderDeclaration':dict(zip(names,factory)),'declarationPercent':dict(zip(names,[100*d/t if t else 0 for d,t in zip(decl,totals)])),'factoryPercent':dict(zip(names,[100*f/t if t else 0 for f,t in zip(factory,totals)])),'factoryOwners':[{'name':k,**dict(zip(names,v))} for k,v in sorted(owners.items(),key=lambda kv:-kv[1][1])]}
def main():
    assert classify([FACTORY+'NewIdentifier',DECL+'visit'])==(True,True)
    assert classify([FACTORY+'NewIdentifier','parser'])==(False,False)
    assert classify(['runtime.mallocgc',DECL+'visit'])==(True,False)
    inputs=json.loads((BASE/'inputs.json').read_text());projects=[]
    with tarfile.open(BASE/'raw-heaps.tar.gz') as archive:
        for item in inputs:
            raw=archive.extractfile(item['project']+'.raw.txt').read();assert hashlib.sha256(raw).hexdigest()==item['rawSha256']
            projects.append({'project':item['project'],'rawSha256':item['rawSha256'],**analyze(raw.decode())})
    report={'scope':'Offline historical sampled allocations. Declaration stack membership includes semantic callees; factory subset includes callees and is not proven removable. Not operation counts, peak residency, CPU shares or speedup. Inuse is historical collection without forced final GC.','inputArchiveSha256':hashlib.sha256((BASE/'raw-heaps.tar.gz').read_bytes()).hexdigest(),'parserSha256':hashlib.sha256((BASE/'analyze.py').read_bytes()).hexdigest(),'projects':projects}
    text=json.dumps(report,indent=2)+'\n'
    if '--write' in sys.argv:(HERE/'report.json').write_text(text)
    else:assert (HERE/'report.json').read_text()==text
    for p in projects:print(p['project'],'declaration alloc %',round(p['declarationPercent']['allocBytes'],4),'factory subset alloc %',round(p['factoryPercent']['allocBytes'],4))
if __name__=='__main__':main()
