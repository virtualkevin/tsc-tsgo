from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[3]
for name in ['validate-native.py','validate-services.py','validate-instrumented.py']:
 code=subprocess.run([sys.executable,str(Path(__file__).parent/name)],cwd=root).returncode
 print(name,code,flush=True)
 if code:raise SystemExit(code)
