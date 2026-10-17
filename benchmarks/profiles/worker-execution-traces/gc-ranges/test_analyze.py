import unittest
from analyze import analyze,union_ns

def fixture():
 return '''M=1 P=0 G=1 Log Time=0 Task=1 Category="checker.index" Message="0"
M=1 P=0 G=1 RangeBegin Time=1 Name="GC mark assist" Scope=Goroutine(1)
M=1 P=0 G=1 RegionBegin Time=3 Task=1 Type="checker.files"
M=1 P=0 G=1 RangeActive Time=4 Name="GC mark assist" Scope=Goroutine(1)
M=1 P=0 G=1 RangeEnd Time=8 Name="GC mark assist" Scope=Goroutine(1) Attributes=[]
M=1 P=0 G=1 RegionEnd Time=10 Task=1 Type="checker.files"
'''
class Tests(unittest.TestCase):
 def test_generation_active_does_not_reset_start(self):
  r=analyze(fixture().splitlines());self.assertEqual(r['workerRanges'][0]['assistWallMs'],5/1e6)
 def test_phase_windows_cover_capture(self):
  r=analyze(fixture().splitlines());self.assertEqual(sum(v['wallMs'] for v in r['phaseWindows'].values()),r['totalTraceWallMs']);self.assertEqual(r['phaseWindows']['beforeWorkers']['wallMs'],3/1e6)
 def test_partial_worker_assist_rejected(self):
  with self.assertRaises(ValueError):analyze(fixture().replace('RangeBegin Time=1','RangeActive Time=1').splitlines())
 def test_unfinished_worker_rejected(self):
  with self.assertRaises(ValueError):analyze(fixture().splitlines()[:-1])
 def test_union_does_not_double_count(self):
  self.assertEqual(union_ns([(0,8),(2,3),(6,10),(12,15)]),13)
 def test_incomplete_background_gc_is_reported(self):
  text=fixture()+'M=1 P=0 G=1 RangeBegin Time=11 Name="GC concurrent mark phase" Scope=None\n'
  self.assertEqual(len(analyze(text.splitlines())['incompleteRanges']),1)
if __name__=='__main__':unittest.main()
