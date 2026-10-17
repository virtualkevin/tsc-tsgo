import unittest
import re
from analyze import analyze


def fixture():
    return '''M=1 P=0 G=1 StateTransition Time=0 GoID=1 Undetermined->Running Reason=""
M=1 P=0 G=1 TaskBegin Time=1 ID=1 Parent=0 Type="checker.batch"
M=1 P=0 G=1 Log Time=2 Task=1 Category="file.count" Message="7"
M=1 P=0 G=1 RegionBegin Time=3 Task=1 Type="checker.initialize"
M=1 P=0 G=1 RegionEnd Time=4 Task=1 Type="checker.initialize"
M=2 P=1 G=2 StateTransition Time=5 GoID=2 Undetermined->Running Reason=""
M=2 P=1 G=2 TaskBegin Time=6 ID=2 Parent=1 Type="checker.group"
M=2 P=1 G=2 Log Time=7 Task=2 Category="checker.index" Message="0"
M=2 P=1 G=2 RegionBegin Time=8 Task=2 Type="checker.lock"
M=2 P=1 G=2 RegionEnd Time=9 Task=2 Type="checker.lock"
M=2 P=1 G=2 RegionBegin Time=10 Task=2 Type="checker.files"
M=2 P=1 G=2 StateTransition Time=15 GoID=2 Running->Waiting Reason="sync"
M=1 P=0 G=1 StateTransition Time=18 GoID=2 Waiting->Runnable Reason=""
M=2 P=1 G=2 StateTransition Time=20 GoID=2 Runnable->Running Reason=""
M=2 P=1 G=2 RegionEnd Time=30 Task=2 Type="checker.files"
M=2 P=1 G=2 TaskEnd Time=31 ID=2 Parent=1 Type="checker.group"
M=1 P=0 G=1 TaskEnd Time=32 ID=1 Parent=0 Type="checker.batch"
'''


class AnalysisTests(unittest.TestCase):
    def test_cross_goroutine_wakeup_accounting(self):
        r = analyze(fixture().splitlines(True))
        b = r['batches'][0]
        self.assertEqual(b['fileCount'], 7)
        self.assertEqual(b['durationMs'], 31 / 1e6)
        self.assertIsNone(b['lastWorkerOnlyMs'])
        self.assertEqual(b['workers'][0]['stateMs'],
                         {'Running': 15/1e6, 'Waiting': 3/1e6, 'Runnable': 2/1e6})
        self.assertEqual(b['workers'][0]['filesMs'], 20/1e6)

    def test_two_worker_tail_and_ownership(self):
        extra = """M=3 P=2 G=3 StateTransition Time=10 GoID=3 Undetermined->Running Reason=""
M=3 P=2 G=3 TaskBegin Time=10 ID=3 Parent=1 Type="checker.group"
M=3 P=2 G=3 Log Time=11 Task=3 Category="checker.index" Message="1"
M=3 P=2 G=3 RegionBegin Time=11 Task=3 Type="checker.lock"
M=3 P=2 G=3 RegionEnd Time=11 Task=3 Type="checker.lock"
M=3 P=2 G=3 RegionBegin Time=12 Task=3 Type="checker.files"
M=3 P=2 G=3 RegionEnd Time=24 Task=3 Type="checker.files"
M=3 P=2 G=3 TaskEnd Time=25 ID=3 Parent=1 Type="checker.group"
"""
        lines = (fixture()+extra).splitlines(True)
        lines.sort(key=lambda line: int(re.search(r'Time=(\d+)', line).group(1)))
        b = analyze(lines)['batches'][0]
        self.assertEqual(b['lastWorkerOnlyMs'], 6/1e6)
        self.assertEqual(b['finishSpreadMs'], 6/1e6)
        self.assertEqual(b['startSkewMs'], 2/1e6)
        self.assertEqual(b['workers'][1]['stateMs'], {'Running': 12/1e6})

    def test_missing_task_end_rejected(self):
        with self.assertRaises(ValueError):
            analyze(fixture().splitlines(True)[:-1])

    def test_invalid_state_transition_rejected(self):
        with self.assertRaises(ValueError):
            analyze(fixture().replace('Waiting->Runnable', 'Running->Runnable').splitlines(True))

    def test_missing_worker_index_rejected(self):
        with self.assertRaises(ValueError):
            analyze(fixture().replace('Message="0"', 'Message="1"').splitlines(True))

    def test_missing_region_end_rejected(self):
        lines = [line for line in fixture().splitlines(True)
                 if 'RegionEnd Time=30' not in line]
        with self.assertRaises(ValueError):
            analyze(lines)

    def test_regressing_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            analyze(fixture().replace('Time=20', 'Time=17').splitlines(True))


if __name__ == '__main__':
    unittest.main()
