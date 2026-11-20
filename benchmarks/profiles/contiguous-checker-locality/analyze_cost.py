"""Describe work concentration inside each observed checker batch."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

directory = Path(sys.argv[1])
for run in json.loads((directory / 'report.json').read_text())['runs']:
    project, mode = run['project'], run['scheduler']
    raw = gzip.decompress((directory / f'{project}-{mode}.jsonl.gz').read_bytes())
    assert hashlib.sha256(raw).hexdigest() == run['logSha256']
    for line in raw.splitlines():
        rows = json.loads(line)
        total = sum(r['ElapsedNS'] for r in rows)
        workers = [sum(r['ElapsedNS'] for r in rows if r['Checker'] == w) for w in range(4)]
        checked = [r for r in rows if r['Checked']]
        if not checked or not total:
            continue
        top = sorted(checked, key=lambda r: r['ElapsedNS'], reverse=True)
        half_files, elapsed = 0, 0
        for r in top:
            half_files += 1
            elapsed += r['ElapsedNS']
            if elapsed * 2 >= total:
                break
        skipped_nodes = sum(r['Nodes'] for r in rows if not r['Checked'])
        all_nodes = sum(r['Nodes'] for r in rows)
        print(project, mode, 'AST nodes in files skipped by the checker (%)', round(100 * skipped_nodes / all_nodes, 1))
        shares = [round(w / total * 100, 1) for w in workers]
        print(project, mode, len(checked), 'checked files;', half_files, 'cover half of callback time;',
              'worker shares (%)', shares, 'largest file (%)', round(top[0]['ElapsedNS'] / total * 100, 1))
