import copy
import unittest
from analyze import aggregate
from test_counts import fixture

class AggregateTests(unittest.TestCase):
    def test_empty(self):
        raw=fixture();raw['Owners'][0].update(Rows=[],TrackedRequests=0)
        result=aggregate(raw)
        self.assertEqual(result['groups'],{})
        self.assertEqual(result['totals']['Calls'],0)

    def test_cross_owner_and_kind_conservation(self):
        raw=fixture();owner=copy.deepcopy(raw['Owners'][0]);owner['CheckerID']=2
        owner['Rows'][0]['Kind']=2;owner['Rows'][0]['ActiveContext']=True
        raw['Owners'].append(owner)
        result=aggregate(raw)
        self.assertEqual(result['totals']['Calls'],6)
        self.assertEqual(result['totals']['Exclusive'],[6,10,14])
        self.assertEqual(set(result['groups']),{'kind=1/active=False','kind=2/active=True'})

if __name__=='__main__':
    unittest.main()
