"""Check that resolving a nested property marks its enclosing annotation once."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[3]
binary = Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory() as temp:
    cwd = Path(temp)
    (cwd/'defs.d.ts').write_text('export interface Model { used: string; idle: { nested: boolean }; }')
    (cwd/'tsconfig.json').write_text(json.dumps({'compilerOptions': {'skipLibCheck': True, 'noEmit': True,
                                                                    'strict': True, 'types': []},
                                                'files': ['index.ts','defs.d.ts']}))
    base = 'import type {Model} from "./defs"; declare const model: Model; export const used: string = model.used;'
    reports = []
    for extra in ['', 'export const value: boolean = model.idle.nested;']:
        (cwd/'index.ts').write_text(base + extra)
        run = subprocess.run([binary, '-p','.'], cwd=cwd, capture_output=True, text=True, check=True,
                             env=os.environ | {'TSC_TS_LIB_DIR': str(root/'upstream/typescript-go/internal/bundled/libs')})
        assert not run.stdout, run.stdout
        reports.append(json.loads(run.stderr))
    a, b = reports
    assert a['AnnotationNodes'] == b['AnnotationNodes'] and a['OutermostAnnotations'] == b['OutermostAnnotations']
    assert b['RequestedTrees'] == a['RequestedTrees'] + 1
    assert b['RequestedTreeNodes'] > a['RequestedTreeNodes'] + 1
    print('Nested property demand verified')
