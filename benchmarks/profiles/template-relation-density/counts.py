def validate(report):
 assert report['SchemaVersion']==1 and report['Owners']
 totals={k:0 for k in ['Writes','NonPlain','Unpackable','Recorded','Repeated','Dropped','Unique','Tiles']}
 histogram=[0]*257;ids=set()
 for owner in report['Owners']:
  assert owner['CheckerID'] not in ids;ids.add(owner['CheckerID'])
  assert owner['TileLimit']==131072 and 0<=owner['Tiles']<=owner['TileLimit']
  assert len(owner['Rows'])==5
  tiles=0
  for kind,row in enumerate(owner['Rows']):
   assert row['Relation']==kind
   for key in totals:
    assert type(row[key]) is int and row[key]>=0
    totals[key]+=row[key]
   assert row['Writes']==row['NonPlain']+row['Unpackable']+row['Recorded']+row['Dropped']
   assert row['Recorded']==row['Repeated']+row['Unique']
   h=row['Occupancy'];assert len(h)==257 and h[0]==0 and all(type(v) is int and v>=0 for v in h)
   assert sum(h)==row['Tiles'] and sum(i*n for i,n in enumerate(h))==row['Unique']
   for i,n in enumerate(h):histogram[i]+=n
   tiles+=row['Tiles']
  assert tiles==owner['Tiles']
 return {'totals':totals,'occupancy':histogram}
