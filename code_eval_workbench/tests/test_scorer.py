"""Tests for scorer.py."""
import pytest
from scorer import (
    COMPOSITE_WEIGHTS,
    levenshtein_score,
    programmatic_score,
    composite_score,
)


class TestLevenshteinScore:
    def test_identical_code_gives_score_of_1(self):
        code = 'def add(a, b):\n    return a + b'
        assert levenshtein_score(code, code) == 1.0

    def test_whitespace_normalized(self):
        # Normalizes spaces and removes comments before comparing
        out = 'def add(a,b):return a+b'
        ref = 'def add(a, b):\n    return a + b'
        score = levenshtein_score(out, ref)
        assert score > 0.8

    def test_completely_different_code_gives_low_score(self):
        out = 'def add(a, b):\n    return a + b'
        ref = 'def multiply(a, b):\n    return a * b'
        score = levenshtein_score(out, ref)
        assert score < 0.5

    def test_empty_output_and_reference_gives_1(self):
        assert levenshtein_score('', '') == 1.0

    def test_empty_output_gives_0(self):
        score = levenshtein_score('', 'def add(a, b): return a + b')
        assert score == 0.0

    def test_empty_reference_gives_0(self):
        score = levenshtein_score('def add(a, b): return a + b', '')
        assert score == 0.0

    def test_extracts_code_block_before_comparing(self):
        out = '```python\ndef add(a, b): return a + b\n```'
        ref = 'def add(a, b): return a + b'
        # Should extract the code block from output before comparing
        assert levenshtein_score(out, ref) == 1.0

    def test_handles_plain_code_block_fence(self):
        out = '```\ndef add(a, b): return a + b\n```'
        ref = 'def add(a, b): return a + b'
        assert levenshtein_score(out, ref) == 1.0


class TestProgrammaticScore:
    def test_no_test_code_returns_05(self):
        score, pt, tt = programmatic_score('def add(a, b): return a + b', '')
        assert score == 0.5
        assert pt is None
        assert tt is None

    def test_no_test_code_whitespace_returns_05(self):
        score, pt, tt = programmatic_score('def add(a, b): return a + b', '   ')
        assert score == 0.5

    def test_no_code_block_in_output_returns_0(self):
        score, pt, tt = programmatic_score('no code here', 'def test_add(): assert add(2, 3) == 5')
        assert score == 0.0
        assert pt == 0
        assert tt == 0

    def test_passing_tests_returns_1(self):
        output = '```python\ndef add(a, b):\n    return a + b\n```'
        test = 'def test_add():\n    assert add(2, 3) == 5\n    assert add(0, 0) == 0'
        score, pt, tt = programmatic_score(output, test)
        assert score == 1.0
        assert pt == 2
        assert tt == 2

    def test_failing_tests_returns_0(self):
        output = '```python\ndef add(a, b):\n    return a - b  # still buggy\n```'
        test = 'def test_add():\n    assert add(2, 3) == 5'
        score, pt, tt = programmatic_score(output, test)
        assert score == 0.0
        assert pt == 0
        assert tt == 1

    def test_mixed_tests(self):
        output = '```python\ndef add(a, b):\n    return a + b\n```'
        test = 'def test_pass(): assert True\ndef test_fail(): assert False'
        score, pt, tt = programmatic_score(output, test)
        assert score == 0.5
        assert pt == 1
        assert tt == 2


class TestCompositeScore:
    def test_weights_sum_to_1(self):
        total = sum(COMPOSITE_WEIGHTS.values())
        assert total == 1.0

    def test_all_scorers_enabled(self):
        output = '```python\ndef add(a, b): return a + b\n```'
        input_dict = {'buggy_code': 'def add(a, b): return a - b', 'bug_description': 'should add'}
        reference = 'def add(a, b): return a + b'
        test = 'def test_add(): assert add(2, 3) == 5'

        result = composite_score(output, input_dict, reference, test,
                                 use_llm_judge=True, use_programmatic=True, use_levenshtein=True)

        assert 'llm_judge' in result
        assert 'programmatic' in result
        assert 'levenshtein' in result
        assert 'composite' in result
        assert 0.0 <= result['composite'] <= 1.0

    def test_llm_judge_skipped_when_disabled(self):
        output = '```python\ndef add(a, b): return a + b\n```'
        input_dict = {'buggy_code': 'def add(a, b): return a - b', 'bug_description': 'should add'}
        reference = 'def add(a, b): return a + b'
        test = 'def test_add(): assert add(2, 3) == 5'

        result = composite_score(output, input_dict, reference, test,
                                 use_llm_judge=False, use_programmatic=True, use_levenshtein=True)

        assert result['llm_judge'] is None
        assert result['programmatic'] == 1.0
        assert result['levenshtein'] == 1.0

    def test_programmatic_skipped_when_disabled(self):
        output = '```python\ndef add(a, b): return a + b\n```'
        input_dict = {'buggy_code': 'def add(a, b): return a - b', 'bug_description': 'should add'}
        reference = 'def add(a, b): return a + b'
        test = 'def test_add(): assert add(2, 3) == 5'

        result = composite_score(output, input_dict, reference, test,
                                 use_llm_judge=False, use_programmatic=False, use_levenshtein=True)

        assert result['llm_judge'] is None
        assert result['programmatic'] is None
        assert result['levenshtein'] == 1.0

    def test_levenshtein_skipped_when_disabled(self):
        output = '```python\ndef add(a, b): return a + b\n```'
        input_dict = {'buggy_code': 'def add(a, b): return a - b', 'bug_description': 'should add'}
        reference = 'def add(a, b): return a + b'
        test = 'def test_add(): assert add(2, 3) == 5'

        result = composite_score(output, input_dict, reference, test,
                                 use_llm_judge=False, use_programmatic=True, use_levenshtein=False)

        assert result['llm_judge'] is None
        assert result['programmatic'] == 1.0
        assert result['levenshtein'] is None

    def test_composite_recomputes_when_only_two_scorers(self):
        # Composite of only programmatic (30%) + levenshtein (20%) = weighted avg
        # But weights are renormalized over enabled scorers
        output = '```python\ndef add(a, b): return a + b\n```'
        input_dict = {'buggy_code': 'def add(a, b): return a - b', 'bug_description': 'should add'}
        reference = 'def add(a, b): return a + b'
        test = 'def test_add(): assert add(2, 3) == 5'

        result = composite_score(output, input_dict, reference, test,
                                 use_llm_judge=False, use_programmatic=True, use_levenshtein=True)

        # composite should be renormalized: 0.3/(0.3+0.2)*prog + 0.2/(0.3+0.2)*lev
        # Both prog and lev are 1.0 here, so composite = 1.0
        assert result['composite'] == 1.0

    def test_returns_passed_and_total_tests(self):
        output = '```python\ndef add(a, b): return a + b\n```'
        reference = 'def add(a, b): return a + b'
        input_dict = {'buggy_code': 'x', 'bug_description': 'x'}
        test = 'def test_add(): assert add(2, 3) == 5'

        result = composite_score(output, input_dict, reference, test,
                                 use_llm_judge=False, use_programmatic=True, use_levenshtein=False)

        assert result['passed_tests'] == 1
        assert result['total_tests'] == 1
