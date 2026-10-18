import json,os,signal,subprocess,sys,tempfile,time,unittest
from pathlib import Path
SCRIPT=Path(__file__).with_name('supervise.py')
class SupervisorTests(unittest.TestCase):
 def test_natural_exit(self):
  with tempfile.TemporaryDirectory() as d:
   log=Path(d)/'events';r=subprocess.run([sys.executable,str(SCRIPT),str(log),'--',sys.executable,'-c','raise SystemExit(7)'],timeout=10)
   self.assertEqual(r.returncode,7);events=[json.loads(x) for x in log.read_text().splitlines()];self.assertEqual([e['event'] for e in events],['started','exited'])
 def test_term_forwarding_and_sender(self):
  with tempfile.TemporaryDirectory() as d:
   log=Path(d)/'events';ready=Path(d)/'ready'
   childcode='import signal,time,pathlib,sys; signal.signal(signal.SIGTERM,lambda s,f:sys.exit(42)); pathlib.Path(sys.argv[1]).touch(); time.sleep(30)'
   p=subprocess.Popen([sys.executable,str(SCRIPT),str(log),'--',sys.executable,'-c',childcode,str(ready)])
   try:
    deadline=time.monotonic()+10
    while not ready.exists() and time.monotonic()<deadline:time.sleep(.01)
    self.assertTrue(ready.exists());p.send_signal(signal.SIGTERM);self.assertEqual(p.wait(timeout=10),42)
    events=[json.loads(x) for x in log.read_text().splitlines()];s=next(e for e in events if e['event']=='signal');self.assertEqual(s['senderPid'],os.getpid());self.assertEqual(s['signal'],signal.SIGTERM);self.assertEqual(events[-1]['returnCode'],42)
   finally:
    if p.poll() is None:p.kill();p.wait()
 def test_exclusive_log(self):
  with tempfile.TemporaryDirectory() as d:
   log=Path(d)/'events';log.write_text('retained')
   r=subprocess.run([sys.executable,str(SCRIPT),str(log),'--',sys.executable,'-c','raise SystemExit(0)'],capture_output=True,timeout=10)
   self.assertNotEqual(r.returncode,0);self.assertEqual(log.read_text(),'retained')
if __name__=='__main__':unittest.main()
