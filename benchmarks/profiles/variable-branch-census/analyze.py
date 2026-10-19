from pathlib import Path
import hashlib,json,re
from counts import BRANCHES,validate
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def summarize(census):
 totals=validate(census)
 cohorts={}
 rows=[dict(branch=name,calls=0,nonNil=0,errorResults=0,exclusiveNs=0,exclusiveInstantiations=0,activeContextCalls=0) for name in BRANCHES]
 for owner in census['Owners']:
  for record in owner['Rows']:
   key=tuple(record[k] for k in ['Branch','DeclarationKind','CheckMode','IncludeOptionality','ActiveContext'])
   group=cohorts.setdefault(key,dict(branch=BRANCHES[key[0]],declarationKind=key[1],checkMode=key[2],includeOptionality=key[3],activeContext=key[4],calls=0,exclusiveNs=0,exclusiveInstantiations=0))
   for dst,src in [('calls','Calls'),('exclusiveNs','ExclusiveNs'),('exclusiveInstantiations','ExclusiveInstantiations')]:group[dst]+=record[src]
   row=rows[record['Branch']]
   for dst,src in [('calls','Calls'),('nonNil','NonNil'),('errorResults','ErrorResults'),('exclusiveNs','ExclusiveNs'),('exclusiveInstantiations','ExclusiveInstantiations')]:row[dst]+=record[src]
   if record['ActiveContext']:row['activeContextCalls']+=record['Calls']
 assert [r['calls'] for r in rows]==totals['branchCalls']
 assert sum(r['exclusiveNs'] for r in rows)==totals['exclusiveNs']
 assert sum(r['exclusiveInstantiations'] for r in rows)==totals['exclusiveInstantiations']
 for field in ['calls','exclusiveNs','exclusiveInstantiations']:assert sum(g[field] for g in cohorts.values())==totals[field]
 return dict(totals=totals,branches=rows,cohorts=sorted(cohorts.values(),key=lambda g:g['exclusiveNs'],reverse=True))
def main():
 report=json.loads((HERE/'report-resumed.json').read_text());assert report['status']=='passed'
 verification=json.loads((HERE/'readback.json').read_text());assert verification['passed'] and verification['reportSha256']==sha(HERE/'report-resumed.json')
 kindfile=HERE.parents[2]/'packages/tsc-go/internal/ast/kind_stringer_generated.go'
 names={int(value):name for name,value in re.findall(r'_ = x\[(Kind\w+)-(\d+)\]',kindfile.read_text())}
 assert names[170]=='KindParameter'
 projects=[]
 for run in report['runs']:
  if run['mode']!='enabled':continue
  name=f"{run['checkers']}-census.json";file=HERE/run['project']/name
  assert sha(file)==run['artifacts'][name]['sha256']
  summary=summarize(json.loads(file.read_text()));assert summary['totals']==run['counts']
  for group in summary['cohorts']:group['declarationKindName']=names[group['declarationKind']]
  projects.append(dict(project=run['project'],checkers=run['checkers'],censusSha256=sha(file),**summary))
  print(run['project'],run['checkers'],'calls',summary['totals']['calls'])
  for row in sorted(summary['branches'],key=lambda r:r['exclusiveNs'],reverse=True)[:4]:print(row)
 result=dict(scope='All observed variable-like resolver calls, not only symbol misses. Uncapped branch totals. Exclusive instrumented elapsed intervals subtract nested observed calls, but include other callees and prior failed alternatives. Parallel checker intervals can overlap in wall time. These are not CPU percentages, safe-reuse proof, or speedup estimates.',kindSourceSha256=sha(kindfile),analyzerSha256=sha(Path(__file__)),captureSha256=sha(HERE/'report-resumed.json'),verificationSha256=sha(HERE/'readback.json'),projects=projects)
 (HERE/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
