"""Summarize verified contextual JSX requests; do not infer cache purity."""
from pathlib import Path
import hashlib,json,sys
from counts import validate,SCALARS,ARRAYS
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
def add(total,row):
 for k in SCALARS:total[k]+=row[k]
 for k in ARRAYS:
  for i,x in enumerate(row[k]):total[k][i]+=x

def analyze(report):
 total=validate(report);groups={}
 for owner in report['Owners']:
  for row in owner['Rows']:
   key=(row['Mode'],row['HasInference'],row['ActiveContext'])
   if key not in groups:groups[key]={**{k:0 for k in SCALARS},**{k:[0,0,0] for k in ARRAYS}}
   add(groups[key],row)
 rows=[{'mode':k[0],'hasInference':k[1],'activeContext':k[2],**v} for k,v in sorted(groups.items())]
 combined={**{k:0 for k in SCALARS},**{k:[0,0,0] for k in ARRAYS}}
 for row in rows:add(combined,row)
 assert combined==total
 return {'totals':total,'owners':len(report['Owners']),'saturatedOwners':sum(o['TrackedRequests']==o['RequestLimit'] for o in report['Owners']),'cohorts':rows,'recordedHistoryComplete':total['Dropped']==0}

def main():
 readback=json.loads((p/'readback.json').read_text());assert readback['passed']
 assert all(sha(p/k)==v for k,v in readback['files'].items())
 capture=json.loads((p/'report.json').read_text());rows=[]
 for run in capture['runs']:
  if run['mode']!='enabled':continue
  f=p/run['project']/'4-census.json';assert sha(f)==run['artifacts'][f.name]['sha256']
  row=analyze(json.loads(f.read_text()));assert row['totals']==run['counts']
  rows.append({'project':run['project'],'rawSha256':sha(f),**row})
 result={'scope':'Verified observer counts/cohorts, not compiler performance. Keys omit mutable inference/flow/diagnostic state. Changed TypeID is identity difference, not proved semantic difference. Zero relation-size or construction change is not absence of effects. Early capped histories are biased and cannot be extrapolated. Instrumented exclusive elapsed time excludes only nested observed JSX calls.','captureSha256':sha(p/'report.json'),'readbackSha256':sha(p/'readback.json'),'analyzerSha256':sha(__file__),'projects':rows}
 text=json.dumps(result,indent=2)+'\n'
 if '--write' in sys.argv:(p/'analysis.json').write_text(text)
 else:assert (p/'analysis.json').read_text()==text
 for row in rows:
  t=row['totals'];print(row['project'],{k:t[k] for k in ['Calls','TrackedFirst','TrackedRepeat','Dropped','ChangedResult','Exclusive','RepeatExclusive']})
if __name__=='__main__':main()
