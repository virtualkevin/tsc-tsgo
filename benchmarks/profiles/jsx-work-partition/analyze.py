"""Source-scoped, disjoint partition of archived normal-build JSX CPU samples."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tarfile

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PREVIOUS = P.parent / 'call-resolution-partition'
spec = importlib.util.spec_from_file_location('call_partition', PREVIOUS / 'analyze.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
PREFIX = previous.PREFIX
HANDLERS = {'inferJsxTypeArguments', 'checkApplicableSignatureForJsxCallLikeElement'}


def partition(samples, sites):
    total = selected = 0
    stages = collections.Counter()
    lines = collections.Counter()
    functions = collections.defaultdict(collections.Counter)
    flat = collections.defaultdict(collections.Counter)
    for cpu, frames in samples:
        total += cpu
        names = [f[0].removeprefix(PREFIX) if f[0].startswith(PREFIX) else '' for f in frames]
        boundary = next((i for i, n in enumerate(names) if n in previous.BOUNDARIES), len(names))
        if boundary == len(names):
            continue
        handler = next((i for i, n in enumerate(names[:boundary]) if n in HANDLERS), None)
        if handler is None:
            continue
        selected += cpu
        key = f'{names[handler]}:{frames[handler][2]}'
        stage = sites.get(key, 'other')
        stages[stage] += cpu
        lines[key] += cpu
        flat[stage][frames[0][0]] += cpu
        for function in {f[0] for f in frames[:handler]}:
            functions[stage][function] += cpu
    assert sum(stages.values()) == sum(lines.values()) == selected
    assert sum(sum(v.values()) for v in flat.values()) == selected
    return dict(totalCpuNs=total, selectedCpuNs=selected, stageNs=dict(sorted(stages.items())),
                stagePercentTotal={k: 100*v/total for k,v in sorted(stages.items())},
                handlerLineNs=dict(sorted(lines.items())),
                inclusiveFunctionsByStage={k:dict(sorted(v.items())) for k,v in sorted(functions.items())},
                flatFunctionsByStage={k:dict(sorted(v.items())) for k,v in sorted(flat.items())})


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    prior = json.loads((PREVIOUS / 'report.json').read_text())
    jsx = ROOT / 'packages/tsc-go/internal/checker/jsx.go'
    checker = ROOT / 'packages/tsc-go/internal/checker/checker.go'
    assert sha(jsx) == prior['jsxSourceSha256']
    assert sha(checker) == prior['sourceSha256']
    assert sha(PREVIOUS / 'analyze.py') == prior['analyzerSha256']
    sites = {}
    handler = None
    for line, text in enumerate(jsx.read_text().splitlines(), 1):
        if text.startswith('func '):
            handler = next((h for h in HANDLERS if f') {h}(' in text), None)
        if handler is None:
            continue
        stage = None
        if text.strip().startswith('paramType := c.getEffectiveFirstArgumentForJsxSignature('):
            stage = 'parameter_type'
        elif 'c.checkExpressionWithContextualType(node.Attributes(),' in text:
            stage = 'contextual_attributes'
        elif 'attributesType = c.createJsxAttributesTypeFromAttributesProperty(' in text:
            stage = 'fragment_attributes'
        elif text.strip().startswith('c.inferTypes(context.inferences,'):
            stage = 'infer_types'
        elif text.strip() == 'return c.getInferredTypes(context)':
            stage = 'inferred_results'
        elif text.strip().startswith('return c.checkTypeRelatedToAndOptionallyElaborate('):
            stage = 'attribute_relation'
        if stage:
            sites[f'{handler}:{line}'] = stage
    assert collections.Counter(sites.values()) == collections.Counter(parameter_type=2, contextual_attributes=2, fragment_attributes=1, infer_types=1, inferred_results=1, attribute_relation=1)
    base = P.parent / 'normal-map-attribution'
    archive = base / 'raw-profiles.tar.gz'
    assert sha(archive) == prior['archiveSha256']
    assert sha(base / 'inputs.json') == prior['inputsSha256']
    inputs = json.loads((base / 'inputs.json').read_text())
    rows = []
    with tarfile.open(archive) as tar:
        for entry, old in zip(inputs, prior['projects'], strict=True):
            assert entry['project'] == old['project']
            raw = tar.extractfile(entry['project'] + '.raw.txt').read()
            assert hashlib.sha256(raw).hexdigest() == entry['rawSha256'] == old['rawSha256']
            result = partition(previous.decode(raw.decode()), sites)
            assert result['totalCpuNs'] == old['totalCpuNs']
            assert result['selectedCpuNs'] == sum(old['phaseSourceLineNs'].get(k, 0) for k in ('isSignatureApplicable:9237', 'inferTypeArguments:9371'))
            rows.append(dict(project=entry['project'], rawSha256=entry['rawSha256'], **result))
    report = dict(scope='Historical CPU, not wall time, repeated-work counts or removable work. Innermost call boundary excludes nested call resolution from outer JSX handlers. Nearest JSX handler owns each selected sample once. Stage follows the handler source line; inclusive function subrows overlap and must not be added. All unclassified samples remain other. No compiler changes or new workload execution.',
                  sourceSha256=sha(jsx), checkerSha256=sha(checker), analyzerSha256=sha(__file__),
                  parserSha256=sha(PREVIOUS/'analyze.py'), priorSha256=sha(PREVIOUS/'report.json'),
                  archiveSha256=sha(archive), sites=sites, projects=rows)
    encoded = json.dumps(report, indent=2) + '\n'
    if '--write' in sys.argv:
        (P / 'report.json').write_text(encoded)
    else:
        assert (P / 'report.json').read_text() == encoded
    for row in rows:
        print(row['project'], json.dumps(row['stagePercentTotal']))


if __name__ == '__main__':
    main()
