"""Wait for the existing validation job, then build the verified candidate.

Never restart validation and never interpret an observation timeout as success.
This controller does not run performance measurements or alter Git HEAD.
"""
from pathlib import Path
import json, os, subprocess, sys, time
sys.dont_write_bytecode = True
PROFILE = Path(__file__).resolve().parent
ROOT = PROFILE.parents[2]
SUPERVISOR = Path('/tmp/tsc-reduction-scratch-cli-supervisor.jsonl')
REPORT = PROFILE / 'finish-validation.json'
assert not REPORT.exists()
report = {'status': 'waiting', 'steps': [], 'supervisor': str(SUPERVISOR)}
def save():
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
save()
try:
    deadline = time.monotonic() + 3600
    while True:
        events = [json.loads(line) for line in SUPERVISOR.read_text().splitlines()]
        assert events[0]['event'] == 'started'
        assert events[0]['supervisorPid'] == 564866 and events[0]['childPid'] == 564867
        terminal = [e for e in events if e['event'] == 'exited']
        if terminal:
            assert len(terminal) == 1 and terminal[0]['returnCode'] == 0, terminal
            break
        assert time.monotonic() < deadline, 'Observation deadline; original job not restarted or terminated'
        time.sleep(5)
    (PROFILE / 'cli-supervisor.jsonl').write_bytes(SUPERVISOR.read_bytes())
    report['status'] = 'running'
    save()
    for script in ['verify-cli.py', 'build-production.py', 'prepare-screen.py']:
        command = [sys.executable, '-B', str(PROFILE / script)]
        result = subprocess.run(command, cwd=ROOT)
        report['steps'].append({'command': command, 'exitCode': result.returncode})
        save()
        assert result.returncode == 0, script
    report['status'] = 'passed'
except BaseException as error:
    report['status'] = 'failed'
    report['error'] = repr(error)
    raise
finally:
    save()
