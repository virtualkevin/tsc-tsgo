"""Partition retained samples by the innermost single-element arena source line."""
from collections import Counter
from pathlib import Path
import gzip
import hashlib
import json
import re

here = Path(__file__).resolve().parent
archive = here.parent/'avx-opportunity-audit'
report = {}
for entry in json.loads((archive/'report.json').read_text())['projects']:
    project = entry['workload']
    raw = gzip.decompress((archive/(project+'.raw.gz')).read_bytes())
    assert hashlib.sha256(raw).hexdigest() == entry['rawSha256']
    samples, locations = raw.decode().split('Locations\n',1)
    lines = {}
    for line in locations.split('Mappings\n')[0].splitlines():
        location = re.match(r'^\s*(\d+):\s+0x[\da-f]+',line)
        if location:
            addr = int(location[1])
            lines[addr] = None
        frame = re.search(r'/core\.\(\*Arena\[.*\]\)\.New\s+\S*/core/arena\.go:(\d+):',line)
        if frame and lines[addr] is None:
            lines[addr] = int(frame[1])
    ns = Counter()
    for line in samples.splitlines():
        sample = re.match(r'^\s+\d+\s+(\d+):\s*(.*)$',line)
        if sample:
            source = next((lines[i] for i in map(int,sample[2].split()) if lines[i] is not None),0)
            ns[source] += int(sample[1])
    assert sum(ns.values()) == entry['totalCpuNs'] and ns[17]>0
    report[project] = {'totalCpuNs':sum(ns.values()), 'arenaNewLineCpuNs':{k:v for k,v in sorted(ns.items()) if k}}
    print(project,round(100*(sum(ns.values())-ns[0])/sum(ns.values()),2),round(100*ns[17]/sum(ns.values()),2))
(here/'line-budget.json').write_text(json.dumps(report,indent=2)+'\n')
