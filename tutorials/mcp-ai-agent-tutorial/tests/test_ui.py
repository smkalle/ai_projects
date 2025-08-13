"""Tests for Streamlit UI components."""

import pytest
from unittest.mock import Mock, patch
from src.ui.utils import format_timestamp, truncate_text

class TestUIUtils:
    """Test suite for UI utility functions."""

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        timestamp = "2025-01-01T12:00:00Z"
        formatted = format_timestamp(timestamp)
        assert "2025-01-01" in formatted
        assert "12:00:00" in formatted

    def test_truncate_text_short(self):
        """Test truncating short text."""
        text = "Short text"
        result = truncate_text(text, 100)
        assert result == text

    def test_truncate_text_long(self):
        """Test truncating long text."""
        text = "This is a very long text that should be truncated"
        result = truncate_text(text, 20)
        assert len(result) <= 20
        assert result.endswith("...")
