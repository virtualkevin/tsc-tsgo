from pathlib import Path
import json,hashlib,re,subprocess
R=Path('/home/dev/tssss/tsc-tsgo');D=Path('/tmp/tsc-census-families');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'status':'checked-with-preserved-counter-mismatch','workloads':[],'limitations':['Single profiled samples are not performance comparisons.','TypeORM strict comparison failed on Symbols; baseline variability observed separately does not establish root cause.','Family aggregates cannot identify repeated equivalent work.']}
for name in ['trpc','typeorm','vscode','sentry']:
 p=D/name;s=json.loads((p/'summary.json').read_text())
 for path,h in s['immutable'].items():assert sha(path)==h
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==s['preflight']['head']
 for m in p.glob('*-inputs.json'):
  for path,h in json.loads(m.read_text()).items():assert sha(path)==h
 comparisons=[]
 for owners in [1,4]:
  def output(variant):
   n=f'{owners}-{variant}';run=next(r for r in s['runs'] if r['name']==n)
   assert run['stdoutSha256']==sha(p/(n+'.stdout')) and run['stderrSha256']==sha(p/(n+'.stderr'))
   assert (p/(n+'.stderr')).read_text()==''
   text=''.join(l for l in (p/(n+'.stdout')).read_text().splitlines(True) if not l.startswith(('CPU profile: ','Memory profile: ')))
   m=re.search(r'^Files:\s+\d+\s*$',text,re.M);assert m
   fields={l.split(':',1)[0]:l.split(':',1)[1].strip() for l in text[m.start():].splitlines()}
   return run['exit'],text[:m.start()],{k:int(fields[k]) for k in ['Files','Lines','Identifiers','Symbols','Types','Instantiations']}
  a=output('base')
  for variant in ['unlabeled','labeled']:
   b=output(variant);assert a[:2]==b[:2]
   differences={k:[a[2][k],b[2][k]] for k in a[2] if a[2][k]!=b[2][k]};assert not differences or (name=='typeorm' and owners==4 and variant=='labeled' and differences=={'Symbols':[461599,461595]})
   census=p/f'{owners}-{variant}.census.jsonl';header,*rows=[json.loads(l) for l in census.read_text().splitlines()]
   assert len(rows)==owners and len({r['checkerId'] for r in rows})==owners and header['semanticallyEquivalentResultsProven'] is False
   for row in rows:
    assert row['familyOnly'] is True and row['cpuLabels']==(variant=='labeled') and row['overflow']['Calls']==0 and len(row['records'])<=4
    for r in row['records']:
     assert 0<=r['ExclusiveNanoseconds']<=r['InclusiveNanoseconds'] and r['NestedSameRawKeyEntries']==0
     assert not any(r[k] for k in ['NodeAddress','SymbolAddress','TypeAddress','MapperAddress','AliasAddress'])
   comparisons.append({'owners':owners,'variant':variant,'counterDifferences':differences,'censusSha256':sha(census),'calls':sum(sum(r['Calls'] for r in row['records']) for row in rows),'records':sum(len(row['records']) for row in rows)})
 report['workloads'].append({'name':name,'originalStatus':s['status'],'comparisons':comparisons,'analysisSha256':sha(p/'analysis.json'),'summarySha256':sha(p/'summary.json')})
report['tests']={}
for name in ['normal-final','race-final']:
 events=[json.loads(l) for l in (D/(name+'.jsonl')).read_text().splitlines()];assert not any(e['Action'] in ['fail','skip'] for e in events)
 tests=[e for e in events if e['Action']=='pass' and 'Test' in e];assert len(tests)==11
 report['tests'][name]={'namedPasses':len(tests),'topLevelPasses':sum('/' not in e['Test'] for e in tests)}
cli=json.loads((D/'cli/summary.json').read_text());assert cli['status']=='passed' and len(cli['comparisons'])==8
report['cli']={'comparisons':8,'sha256':sha(D/'cli/summary.json')}
(D/'postcheck.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
