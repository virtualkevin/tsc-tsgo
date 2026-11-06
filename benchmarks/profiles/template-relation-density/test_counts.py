import copy,unittest
from counts import validate
class Counts(unittest.TestCase):
 def fixture(self):
  rows=[]
  for kind in range(5):
   row=dict(Relation=kind,Writes=0,NonPlain=0,Unpackable=0,Recorded=0,Repeated=0,Dropped=0,Unique=0,Tiles=0,Occupancy=[0]*257);rows.append(row)
  rows[0].update(Writes=5,NonPlain=1,Recorded=3,Repeated=1,Dropped=1,Unique=2,Tiles=1);rows[0]['Occupancy'][2]=1
  return dict(SchemaVersion=1,Owners=[dict(CheckerID=1,TileLimit=131072,Tiles=1,Rows=rows)])
 def test_valid(self):self.assertEqual(validate(self.fixture())['totals']['Unique'],2)
 def test_corrupt_counts(self):
  for key,value in [('Writes',6),('Repeated',2),('Unique',1),('Tiles',2)]:
   f=self.fixture();f['Owners'][0]['Rows'][0][key]=value
   with self.assertRaises(AssertionError):validate(f)
 def test_corrupt_histogram(self):
  f=self.fixture();f['Owners'][0]['Rows'][0]['Occupancy'][2]=0
  with self.assertRaises(AssertionError):validate(f)
 def test_duplicate_owner(self):
  f=self.fixture();f['Owners'].append(copy.deepcopy(f['Owners'][0]))
  with self.assertRaises(AssertionError):validate(f)
if __name__=='__main__':unittest.main()
