"""Group uncapped diagnostic rows; never extrapolate the bounded key history."""
from pathlib import Path
import collections
import hashlib
import json
import sys
from counts import validate, SCALARS, ARRAYS

P = Path(__file__).resolve().parent

def aggregate(raw):
    totals = validate(raw)
    groups = {}
    for owner in raw['Owners']:
        for row in owner['Rows']:
            key = f"kind={row['Kind']}/active={row['ActiveContext']}"
            if key not in groups:
                groups[key] = {k:0 for k in SCALARS}
                groups[key].update({k:[0,0,0] for k in ARRAYS})
            g = groups[key]
            for k in SCALARS:
                g[k] += row[k]
            for k in ARRAYS:
                for i in range(3):
                    g[k][i] += row[k][i]
    for k in SCALARS:
        assert sum(g[k] for g in groups.values()) == totals[k]
    for k in ARRAYS:
        for i in range(3):
            assert sum(g[k][i] for g in groups.values()) == totals[k][i]
    return {'totals':totals, 'groups':dict(sorted(groups.items()))}

def main():
    control = json.loads((P/'report.json').read_text())
    assert control['status'] == 'passed'
    rows = []
    for project in ['typeorm','trpc','vscode','sentry']:
        path = P/project/'4-census.json'
        raw = json.loads(path.read_text())
        run = next(r for r in control['runs'] if r['project']==project and r['mode']=='enabled')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == run['artifacts'][path.name]['sha256']
        result = aggregate(raw)
        assert result['totals'] == run['counts']
        rows.append({'project':project,'rawSha256':digest,'saturatedOwners':sum(o['TrackedRequests']==o['RequestLimit'] for o in raw['Owners']),**result})
    report = {'scope':'Uncapped query totals grouped by discriminator kind and coarse active context. Kind 1 type discriminator; kind 2 JSX or object-literal discriminator, not JSX alone. First/repeat/change counts apply only to tracked early type/name keys and omit mutable context. Not a reuse proof or speedup.',
              'analyzerSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'projects':rows}
    encoded = json.dumps(report,indent=2)+'\n'
    if '--write' in sys.argv:
        (P/'analysis.json').write_text(encoded)
    else:
        assert (P/'analysis.json').read_text()==encoded
    for r in rows:
        print(r['project'],r['saturatedOwners'],json.dumps(r['totals']))

if __name__=='__main__':
    main()
