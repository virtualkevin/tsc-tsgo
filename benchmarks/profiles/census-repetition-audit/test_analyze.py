import unittest
from analyze import analyze, category, parse_samples, repeats


def record(index=0, calls=1, nested=0, **changes):
    result = dict(ID=index, Family='instantiation', Calls=calls,
                  NestedSameRawKeyEntries=nested, ReturnedNormally=calls,
                  ErrorResults=0, DeferredResults=0, DiagnosticSpans=0,
                  File='', Pos=0, Mode=0, Candidates=False, Resolving=False,
                  AliasAddress='0x0', FlowDepth=0, InstantiationDepth=0)
    result.update(changes)
    return result


def owner(identity, records):
    return dict(checkerId=identity, cpuLabels=True, records=records,
                overflow=dict(Calls=7, Family='overflow-family'))


def sample(cpu, identity=None, index='0', family='instantiation'):
    return dict(cpu=cpu, labels={} if identity is None else dict(
        census_checker=str(identity), census_record=index, census_family=family))


class AuditTests(unittest.TestCase):
    def test_owner_scoping_and_disjoint_cpu(self):
        result = analyze([owner(1, [record(calls=2)]), owner(2, [record()])],
                         [sample(10, 1), sample(20, 2), sample(30),
                          sample(40, 1, 'overflow', 'overflow-family')])
        self.assertEqual(result['totalCpuNs'], 100)
        self.assertEqual(result['sampledCpuBucketsNs'], {
            'nonnested-repeat-record-unflagged': 10, 'single-entry-record': 20,
            'unlabeled': 30, 'overflow': 40})
        self.assertEqual(result['overflowCalls'], 14)
        self.assertEqual(result['topRepeatedRecordsByAllEntriesCpu'][0]['allEntriesSampledCpuNs'], 10)

    def test_nested_calls_are_not_sequential_reentries(self):
        self.assertEqual(repeats(record(calls=4, nested=2)), 1)
        self.assertEqual(category(record(calls=3, nested=2)), 'nested-only-repeat-record')
        with self.assertRaises(AssertionError):
            repeats(record(calls=2, nested=2))

    def test_each_incomplete_or_diagnostic_flag(self):
        for change in [dict(ReturnedNormally=1), dict(ErrorResults=1),
                       dict(DeferredResults=1), dict(DiagnosticSpans=1)]:
            with self.subTest(change=change):
                self.assertEqual(category(record(calls=2, **change)),
                                 'nonnested-repeat-record-flagged')

    def test_parser_preserves_cpu_not_sample_count(self):
        raw = ('Samples:\nsamples/count cpu/nanoseconds\n'
               '  2 20000000: 1 2\n'
               '                census_checker:[1] census_family:[instantiation] census_record:[0]\n'
               '  3 30000000: 2\nLocations\n')
        self.assertEqual(parse_samples(raw), [sample(20000000, 1), sample(30000000)])
        with self.assertRaises(AssertionError):
            parse_samples(raw.replace(' census_record:[0]', ''))

    def test_mismatched_label_and_duplicate_owner_rejected(self):
        with self.assertRaises(AssertionError):
            analyze([owner(1, [record()])], [sample(10, 1, family='other')])
        with self.assertRaises(AssertionError):
            analyze([owner(1, [record()]), owner(1, [record()])], [sample(10)])

    def test_record_indices_must_match(self):
        with self.assertRaises(AssertionError):
            analyze([owner(1, [record(index=1)])], [sample(10)])


if __name__ == '__main__':
    unittest.main()
