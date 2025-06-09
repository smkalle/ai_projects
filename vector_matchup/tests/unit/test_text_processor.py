import pytest
from text_processor import TextProcessor

@pytest.fixture
def text_processor():
    return TextProcessor()

def test_smart_chunk_text(text_processor):
    # Test with a simple text
    text = "This is a test sentence. This is another test sentence."
    chunks = text_processor.smart_chunk_text(text)
    assert len(chunks) > 0
    assert all(len(chunk) <= text_processor.chunk_size for chunk in chunks)

def test_clean_text(text_processor):
    # Test with text containing excessive whitespace and control characters
    text = "Hello!   This is a test...   With some   extra   spaces"
    cleaned_text = text_processor.clean_text(text)
    # The clean_text method normalizes whitespace, not special characters
    assert "   " not in cleaned_text  # Multiple spaces should be normalized
    assert cleaned_text == "Hello! This is a test... With some extra spaces"

def test_process_text(text_processor):
    # Test the complete text processing pipeline
    text = "This is a test document. It has multiple sentences. Each sentence should be processed."
    processed_chunks = text_processor.process_text(text)
    assert len(processed_chunks) > 0
    assert all(isinstance(chunk, str) for chunk in processed_chunks)

def test_validate_text(text_processor):
    # Test text validation
    assert text_processor.validate_text("Valid text") is True
    assert text_processor.validate_text("") is False
    assert text_processor.validate_text("   ") is False 