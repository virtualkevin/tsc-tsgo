"""Exercise file-local member lookup and cross-file global interface merging."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[3]
binary = Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory() as tmp:
    cwd = Path(tmp)
    (cwd/'a.d.ts').write_text('interface MergedProbe { a: string } interface LocalProbe { x: string }')
    (cwd/'b.d.ts').write_text('interface MergedProbe { b(): number }')
    (cwd/'tsconfig.json').write_text(json.dumps({'compilerOptions': {'skipLibCheck': True, 'noEmit': True,
                                                                    'strict': True, 'types': []},
                                                'files':['a.d.ts','b.d.ts','main.ts']}))
    def check(text):
        (cwd/'main.ts').write_text(text)
        proc = subprocess.run([binary, '-p','.'], cwd=cwd, text=True, capture_output=True, check=True,
                              env=os.environ | {'TSC_TS_LIB_DIR':str(root/'upstream/typescript-go/internal/bundled/libs')})
        assert not proc.stdout
        return json.loads(proc.stderr)
    cold = check('')
    hot = check('declare let l: LocalProbe, m: MergedProbe; l.x; m.b();')
    assert sum(cold['MemberNodes']) == sum(hot['MemberNodes'])
    assert hot['Lists'][0] < cold['Lists'][0] and hot['Lists'][1] > cold['Lists'][1]
    assert hot['Lists'][3] >= cold['Lists'][3] + 2
    print('Member lookup and cross-file merging verified')
