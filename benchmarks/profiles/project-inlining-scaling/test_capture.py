import importlib.util, json, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('scaling_capture',Path(__file__).with_name('capture.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ScalingEvidenceTests(unittest.TestCase):
    def test_balanced_order(self):
        self.assertEqual({tuple(sorted(row)) for row in m.ORDERS},{(1,2,4,8)})
        for column in zip(*m.ORDERS): self.assertEqual(set(column),{1,2,4,8})
        edges=[(a,b) for row in m.ORDERS for a,b in zip(row,row[1:])]
        self.assertEqual(len(set(edges)),12)
    def test_resources_fail_closed(self):
        valid={'userSeconds':1.25,'systemSeconds':0.5,'peakRssKiB':42,'exitStatus':0}
        self.assertEqual(m.parse_resources(json.dumps(valid)),valid)
        for key,value in [('userSeconds',float('nan')),('systemSeconds',float('inf')),('userSeconds',True),('peakRssKiB',0),('peakRssKiB',1.5),('exitStatus',1)]:
            with self.subTest(key=key,value=value),self.assertRaises(AssertionError): m.parse_resources(json.dumps(valid|{key:value}))
        with self.assertRaises(AssertionError):m.parse_resources(json.dumps(valid)[:-1]+',"exitStatus":0}')
    def test_summary_excludes_warmups_and_uses_even_median(self):
        rows=[]
        for workers in [1,2,4,8]:
            for phase,wall in [('warmup',1000),('timed',1),('timed',9),('timed',3),('timed',5)]:
                rows.append({'phase':phase,'workers':workers,'wallMs':wall,'resources':{'userSeconds':wall,'systemSeconds':2,'peakRssKiB':wall*10}})
        for summary in m.summarize(rows).values():
            self.assertEqual(summary,{'wallMedianMs':4,'cpuMedianSeconds':6,'rssMedianKiB':40})
        with self.assertRaises(AssertionError):m.summarize(rows[:-1])

if __name__=='__main__':unittest.main()
