from pathlib import Path
import hashlib,json
from counts import validate
p=Path(__file__).resolve().parent
r=json.loads((p/'report.json').read_text());assert r['status']=='passed'
rows=[]
for name in ('typeorm','trpc','vscode','sentry'):
 f=p/name/'census.json';run=next(x for x in r['runs'] if x['project']==name and x['mode']=='enabled')
 assert hashlib.sha256(f.read_bytes()).hexdigest()==run['artifacts']['census.json']['sha256']
 current=validate(json.loads(f.read_text()));assert current==run['counts'];c=current['counts']
 repeats=c['FinishedRepeated'];desc=c['RepeatedDescendantInstantiations']
 rows.append({'project':name,'requests':c['Requests'],'selected':c['Selected'],'firstInWindow':c['FirstInWindow'],'completedRepeats':repeats,'sameResult':c['SameResult'],'changedResult':c['ChangedResult'],'sameStateAndResult':c['SameStateAndResult'],'nestedPending':c['NestedPending'],'evictions':c['Evictions'],'repeatedDescendantInstantiations':desc,'minimumZeroDescendantRepeats':max(0,repeats-desc),'controlElapsedSeconds':{x['mode']:x['controlElapsedSeconds'] for x in r['runs'] if x['project']==name}})
result={'captureHead':r['baseHead'],'binarySha256':r['candidateSha256'],'rows':rows,'decision':'No wider cache justified. Identify request/type/mapper families and semantic invalidation before any implementation.','limitations':['Weak bounded hash selection is not proven random; no population extrapolation.','Eviction loses recurrence history.','Equal pointer and partial state are not context-complete cache identity.','Descendant counts overlap and exclude direct work; zero descendants does not imply cheap execution.','Single fixed-order control durations are not speedup measurements.']}
encoded=json.dumps(result,indent=2)+'\n';target=p/'summary.json'
if target.exists():assert target.read_text()==encoded
else:target.write_text(encoded)
print(encoded,end='')
