import unittest
from analyze import partition, PREFIX


def f(name, line=1):
    return PREFIX+name, 'jsx.go', line


class OwnershipTests(unittest.TestCase):
    def test_nested_call_excluded_from_outer_jsx(self):
        result = partition([(10, [f('work'), f('resolveCall'), f('inferJsxTypeArguments', 197), f('resolveCall')])], {'inferJsxTypeArguments:197':'parameter_type'})
        self.assertEqual(result['totalCpuNs'], 10)
        self.assertEqual(result['selectedCpuNs'], 0)

    def test_nearest_handler_and_recursive_function_counted_once(self):
        result = partition([(10, [f('work'), f('work'), f('inferJsxTypeArguments',197), f('checkApplicableSignatureForJsxCallLikeElement',598), f('resolveCall')])], {'inferJsxTypeArguments:197':'parameter_type'})
        self.assertEqual(result['stageNs'], {'parameter_type':10})
        self.assertEqual(result['inclusiveFunctionsByStage'], {'parameter_type':{PREFIX+'work':10}})
        self.assertEqual(result['flatFunctionsByStage'], {'parameter_type':{PREFIX+'work':10}})

    def test_unclassified_and_outside_calls(self):
        result = partition([(3,[f('inferJsxTypeArguments',999),f('resolveCall')]),(5,[f('inferJsxTypeArguments',197)]),(7,[f('ordinary'),f('resolveCall')])], {})
        self.assertEqual(result['totalCpuNs'],15)
        self.assertEqual(result['stageNs'], {'other':3})

    def test_source_line_distinguishes_parameter_and_attributes(self):
        result = partition([(3,[f('work'),f('inferJsxTypeArguments',197),f('resolveCall')]),(5,[f('work'),f('inferJsxTypeArguments',198),f('resolveCall')])], {'inferJsxTypeArguments:197':'parameter_type','inferJsxTypeArguments:198':'contextual_attributes'})
        self.assertEqual(result['stageNs'], {'contextual_attributes':5,'parameter_type':3})
        self.assertEqual(sum(result['stagePercentTotal'].values()),100)


if __name__ == '__main__':
    unittest.main()
