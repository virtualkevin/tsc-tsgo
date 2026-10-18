"""Conservative direct allocation-site attribution from preserved heap profiles."""
from pathlib import Path
import collections,hashlib,importlib.util,json,sys,tarfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PARSER=HERE.parent/'ast-arena-audit/analyze.py'
spec=importlib.util.spec_from_file_location('heap_parser',PARSER)
parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
TYPE='github.com/microsoft/typescript-go/internal/checker.Type'
METRICS=['allocObjects','allocBytes','inuseObjects','inuseBytes']

def direct_type_list(frame):
    # Explicitly exclude structures merely containing *Type, map allocations,
    # generic pointer shapes, and allocations in nested instantiator callees.
    return (frame.startswith(('slices.Insert[go.shape.[]*'+TYPE+',',
                              'slices.Clone[go.shape.[]*'+TYPE+',',
                              'slices.Grow[go.shape.[]*'+TYPE+','))
            or frame=='github.com/microsoft/typescript-go/internal/checker.instantiateList[go.shape.*'+TYPE+']'
            or frame=='github.com/microsoft/typescript-go/internal/core.AppendIfUnique[go.shape.*'+TYPE+']')

def analyze(raw):
    total=[0]*4; selected=[0]*4; sites=collections.defaultdict(lambda:[0]*4)
    for values,frames in parser.parse(raw):
        total=[a+b for a,b in zip(total,values)]
        if not frames or not direct_type_list(frames[0]):continue
        selected=[a+b for a,b in zip(selected,values)]
        sites[frames[0]]=[a+b for a,b in zip(sites[frames[0]],values)]
    return {'total':dict(zip(METRICS,total)),'selectedDirectSites':dict(zip(METRICS,selected)),
            'selectedPercent':{k:100*s/t if t else 0 for k,s,t in zip(METRICS,selected,total)},
            'sites':[{'name':k,**dict(zip(METRICS,v))} for k,v in sorted(sites.items())]}

def main():
    base=HERE.parent/'ast-arena-audit';inputs=json.loads((base/'inputs.json').read_text())
    archive=base/'raw-heaps.tar.gz'
    result={'scope':'Selected explicitly typed direct slice allocation frames only; not all type-list allocations, exact counts, live-after-final-GC data, CPU/RSS, removable budget, or speedup forecast. Generic pointer shapes and child allocations are excluded. Inuse samples reflect the old profile collection point without forced final GC.',
            'parserSha256':hashlib.sha256(PARSER.read_bytes()).hexdigest(),
            'rawArchiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'projects':[]}
    with tarfile.open(archive) as t:
        for item in inputs:
            data=t.extractfile(item['project']+'.raw.txt').read()
            assert hashlib.sha256(data).hexdigest()==item['rawSha256']
            r=analyze(data.decode());r.update(project=item['project'],rawSha256=item['rawSha256'])
            result['projects'].append(r)
    output=json.dumps(result,indent=2)+'\n'
    if '--write' in sys.argv:(HERE/'report.json').write_text(output)
    else:assert (HERE/'report.json').read_text()==output
    for r in result['projects']:print(r['project'],{k:round(v,3) for k,v in r['selectedPercent'].items()})

if __name__=='__main__':main()
