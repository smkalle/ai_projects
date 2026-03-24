"""Tests for utils.py."""
import pytest
from utils import (
    extract_code_block,
    extract_explanation,
    score_color,
    score_emoji,
    ScoreBreakdown,
    EvalResult,
)


class TestExtractCodeBlock:
    def test_extracts_python_code_block(self):
        text = 'Here is the code:\n```python\ndef add(a, b):\n    return a + b\n```\nDone.'
        assert extract_code_block(text) == 'def add(a, b):\n    return a + b'

    def test_extracts_plain_code_block(self):
        text = '```\ndef add(a, b):\n    return a + b\n```'
        assert extract_code_block(text) == 'def add(a, b):\n    return a + b'

    def test_strips_fences_and_trims(self):
        text = '```python\n  def foo():\n    pass\n  ```'
        assert extract_code_block(text) == 'def foo():\n    pass'

    def test_no_code_block_returns_stripped_text(self):
        text = '  just plain text  '
        assert extract_code_block(text) == 'just plain text'

    def test_empty_input(self):
        assert extract_code_block('') == ''
        assert extract_code_block('   ') == ''

    def test_uses_first_code_block(self):
        text = '```python\ndef one(): pass\n```\n```python\ndef two(): pass\n```'
        assert extract_code_block(text) == 'def one(): pass'


class TestExtractExplanation:
    def test_extracts_explanation_after_code_block(self):
        text = (
            '```python\ndef add(a, b): return a + b\n```\n'
            'Explanation: Changed minus to plus to fix the bug.'
        )
        assert 'Changed minus to plus' in extract_explanation(text)

    def test_no_explanation_returns_empty(self):
        assert extract_explanation('no explanation here') == ''

    def test_empty_input(self):
        assert extract_explanation('') == ''


class TestScoreColor:
    def test_green_for_high_scores(self):
        assert score_color(0.8) == 'green'
        assert score_color(1.0) == 'green'

    def test_yellow_for_medium_scores(self):
        assert score_color(0.6) == 'yellow'
        assert score_color(0.79) == 'yellow'

    def test_orange_for_low_medium_scores(self):
        assert score_color(0.4) == 'orange3'
        assert score_color(0.59) == 'orange3'

    def test_red_for_low_scores(self):
        assert score_color(0.0) == 'red'
        assert score_color(0.39) == 'red'


class TestScoreEmoji:
    def test_high_score(self):
        assert score_emoji(0.8) == '✅'
        assert score_emoji(1.0) == '✅'

    def test_medium_score(self):
        assert score_emoji(0.6) == '🟡'
        assert score_emoji(0.79) == '🟡'

    def test_low_medium_score(self):
        assert score_emoji(0.4) == '🟠'
        assert score_emoji(0.59) == '🟠'

    def test_low_score(self):
        assert score_emoji(0.0) == '❌'
        assert score_emoji(0.39) == '❌'


class TestResultModels:
    def test_score_breakdown_defaults(self):
        sb = ScoreBreakdown()
        assert sb.llm_judge is None
        assert sb.programmatic is None
        assert sb.levenshtein is None
        assert sb.composite == 0.0

    def test_eval_result_timestamp_auto_set(self):
        ev = EvalResult(id='bug_001', category='arith', difficulty='easy', output='', scores=ScoreBreakdown())
        assert ev.timestamp != ''

    def test_eval_result_full(self):
        sb = ScoreBreakdown(llm_judge=0.9, programmatic=1.0, levenshtein=0.85, composite=0.91)
        ev = EvalResult(
            id='bug_001',
            category='arith',
            difficulty='easy',
            output='fixed code',
            scores=sb,
            reasoning='looks good',
            passed_tests=4,
            total_tests=4,
        )
        assert ev.scores.composite == 0.91
        assert ev.passed_tests == 4
