"""Record signal provenance while preserving cancellation of the supervised job.

Linux diagnostic launcher. No environment/command-line dumps, signal suppression,
background detachment from this launcher, or retries. Waits for SIGCHLD/signals;
performs no periodic polling during the job.
"""
import json,os,signal,subprocess,sys,time
from pathlib import Path

def main():
    if len(sys.argv)<4 or sys.argv[2]!='--':
        raise SystemExit('usage: supervise.py EXCLUSIVE_LOG -- COMMAND [ARGS...]')
    with open(sys.argv[1],'x') as log:
        def record(event,**fields):
            log.write(json.dumps({'event':event,'monotonicNs':time.monotonic_ns(),**fields})+'\n');log.flush()
        watched={signal.SIGTERM,signal.SIGINT,signal.SIGHUP,signal.SIGCHLD}
        oldmask=signal.pthread_sigmask(signal.SIG_BLOCK,watched)
        # This launcher has no threads. Restore the child's original signal mask
        # before exec, and supervise its separate group explicitly on cancellation.
        child=subprocess.Popen(sys.argv[3:],start_new_session=True,preexec_fn=lambda:signal.pthread_sigmask(signal.SIG_SETMASK,oldmask))
        record('started',supervisorPid=os.getpid(),childPid=child.pid)
        try:
            while True:
                code=child.poll()
                if code is not None:
                    record('exited',returnCode=code)
                    return code if code>=0 else 128-code
                info=signal.sigwaitinfo(watched)
                if info.si_signo==signal.SIGCHLD:continue
                comm=None
                if info.si_pid>0:
                    try:comm=Path(f'/proc/{info.si_pid}/comm').read_text().strip()
                    except OSError:pass
                record('signal',signal=info.si_signo,senderPid=info.si_pid,senderUid=info.si_uid,signalCode=info.si_code,senderComm=comm)
                try:child.send_signal(info.si_signo)
                except ProcessLookupError:pass
                record('forwarded',signal=info.si_signo,childPid=child.pid)
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK,oldmask)
if __name__=='__main__':raise SystemExit(main())
