# LangExtract Tutorial: Extracting Structured Data from Long Texts

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Advanced Usage](#advanced-usage)
- [Processing Romeo and Juliet](#processing-romeo-and-juliet)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Overview

LangExtract is an open-source Python library developed by Google that transforms unstructured text into structured data using large language models (LLMs) like Gemini. It addresses the challenge of poor multi-fact retrieval in large contexts, as highlighted by a 2023 study in *Nature Machine Intelligence* showing a 30% drop in recall for LLMs in million-token tests.

### Why LangExtract?

- **Long Document Optimization**: Handles documents with 100,000+ characters efficiently
- **Parallel Processing**: Processes text chunks simultaneously for faster extraction
- **Source Grounding**: Maps extracted data back to original text locations
- **Interactive Visualization**: Generates HTML reports for easy data exploration
- **25% Improvement**: Research shows improved data reliability in clinical settings

## Key Features

- ✅ **Text Chunking**: Automatically splits long documents for optimal processing
- ✅ **Multiple Extraction Passes**: Improves recall through sequential processing
- ✅ **Precise Source Mapping**: Links extracted data to exact text locations
- ✅ **Cloud & Local Support**: Works with Gemini API and local models via Ollama
- ✅ **Structured Output**: Returns data in JSON format with customizable schemas

## Prerequisites

- Python 3.8 or higher
- pip package manager
- API key for Gemini (for cloud usage) or local LLM setup
- Virtual environment (recommended)

## Installation

### Basic Installation

```bash
pip install langextract
```

### Virtual Environment Setup (Recommended)

```bash
# Create virtual environment
python -m venv langextract-env

# Activate virtual environment
# On Windows:
langextract-env\Scripts\activate
# On macOS/Linux:
source langextract-env/bin/activate

# Install LangExtract
pip install langextract
```

### API Key Configuration

Configure your Gemini API key using one of these methods:

#### Method 1: Environment Variable
```bash
export LANGEXTRACT_API_KEY="your-api-key-here"
```

#### Method 2: .env File
Create a `.env` file in your project directory:
```
LANGEXTRACT_API_KEY=your-api-key-here
```

#### Method 3: Direct Configuration (Development Only)
```python
import os
os.environ["LANGEXTRACT_API_KEY"] = "your-api-key-here"
```

## Quick Start

### Basic Example

```python
from langextract import LangExtract

# Initialize LangExtract
lx = LangExtract()

# Define extraction prompt
prompt = """
Extract the following information:
- Names of people
- Their roles or titles
- Key actions they perform

Format as JSON with fields: name, role, action
"""

# Extract from text
text = "Dr. Sarah Johnson, the lead researcher, discovered a new compound."
result = lx.extract(text=text, instructions=prompt)

# Save results
result.save("extraction_results.jsonl")
```

## Advanced Usage

### Processing Long Documents

```python
from langextract import LangExtract
import textwrap

# Initialize with advanced configuration
lx = LangExtract()

# Define detailed extraction prompt
prompt = textwrap.dedent("""\
Extract characters, emotions, and relationships from the text.

Format output as a list of dictionaries with:
- "character": name of the character
- "emotion": emotion or feeling expressed
- "relationship": description of relationship
- "quote": supporting quote from text

Example:
Input: "But soft! What light through yonder window breaks?"
Output: [{
    "character": "Romeo",
    "emotion": "wonder",
    "relationship": "admiring Juliet",
    "quote": "But soft! What light through yonder window breaks?"
}]
""")

# Process with optimization parameters
result = lx.extract(
    url="https://example.com/long-document.txt",
    instructions=prompt,
    max_workers=20,        # Parallel processing threads
    extraction_passes=3,   # Multiple passes for better recall
    max_char_buffer=1000  # Characters per chunk
)
```

## Processing Romeo and Juliet

Here's a complete example processing Shakespeare's *Romeo and Juliet* from Project Gutenberg:

```python
from langextract import LangExtract
import textwrap

# Initialize LangExtract
lx = LangExtract()

# Define comprehensive extraction prompt
prompt = textwrap.dedent("""\
Extract characters, emotions, and relationships from Shakespeare's Romeo and Juliet.

For each significant moment, identify:
- Character name
- Emotions or feelings expressed
- Relationships or interactions
- Supporting quote

Format as JSON list with fields: character, emotion, relationship, quote

Examples:

Input: "O Romeo, Romeo! Wherefore art thou Romeo?"
Output: [{
    "character": "Juliet",
    "emotion": "longing, frustration",
    "relationship": "loves Romeo, questions his family name",
    "quote": "O Romeo, Romeo! Wherefore art thou Romeo?"
}]

Input: "A plague o' both your houses!"
Output: [{
    "character": "Mercutio",
    "emotion": "anger, curse",
    "relationship": "cursing both Montagues and Capulets",
    "quote": "A plague o' both your houses!"
}]
""")

# Process the full text (147,843 characters)
result = lx.extract(
    url="https://www.gutenberg.org/files/1513/1513-0.txt",
    instructions=prompt,
    max_workers=20,
    extraction_passes=3,
    max_char_buffer=1000
)

# Save results
result.save("romeo_juliet_analysis.jsonl")

# Generate interactive visualization
result.visualize("romeo_juliet_visualization.html")

# Access extracted data programmatically
for extraction in result.extractions:
    print(f"Character: {extraction['character']}")
    print(f"Emotion: {extraction['emotion']}")
    print(f"Quote: {extraction['quote'][:50]}...")
    print("---")
```

### Analyzing Results

The generated HTML visualization provides:
- **Interactive Explorer**: Click through extracted entities
- **Source Highlighting**: See exact text locations
- **Filtering Options**: Sort by character, emotion, or relationship
- **Export Capabilities**: Download filtered results

## Performance Optimization

### For Large Documents (>100K characters)

```python
# Optimize for speed
result = lx.extract(
    url=document_url,
    instructions=prompt,
    max_workers=30,        # Increase parallel workers
    extraction_passes=2,   # Balance speed vs recall
    max_char_buffer=2000   # Larger chunks
)
```

### For Maximum Accuracy

```python
# Optimize for recall
result = lx.extract(
    url=document_url,
    instructions=prompt,
    max_workers=15,        # Moderate parallelism
    extraction_passes=5,   # More passes
    max_char_buffer=500    # Smaller, precise chunks
)
```

### Cost Optimization

- **Monitor API Usage**: Track token consumption with Gemini
- **Use Tier 2 Quota**: Avoid rate limits for large documents
- **Batch Processing**: Process multiple documents together
- **Cache Results**: Store extractions to avoid reprocessing

## Troubleshooting

### Common Issues

#### Rate Limit Errors
```python
# Solution: Reduce parallel workers
result = lx.extract(
    url=document_url,
    instructions=prompt,
    max_workers=5  # Fewer concurrent requests
)
```

#### Memory Issues with Large Documents
```python
# Solution: Process in smaller chunks
result = lx.extract(
    url=document_url,
    instructions=prompt,
    max_char_buffer=500,  # Smaller chunks
    batch_size=10        # Process fewer chunks at once
)
```

#### Inconsistent Extractions
```python
# Solution: Improve prompt with more examples
prompt = textwrap.dedent("""\
[Your instructions here]

Example 1: [specific example]
Example 2: [another example]
Example 3: [edge case example]
""")
```

### Best Practices

1. **Clear Prompts**: Provide specific instructions with multiple examples
2. **Validate Output**: Use the visualization to verify extractions
3. **Iterative Refinement**: Adjust parameters based on results
4. **Error Handling**: Implement try-catch blocks for API calls
5. **Progress Monitoring**: Use logging for long-running extractions

## References

- [LangExtract GitHub Repository](https://github.com/google/langextract)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Project Gutenberg](https://www.gutenberg.org/)
- [Nature Machine Intelligence Study (2023)](https://www.nature.com/natmachintell/)
- [Journal of Medical Informatics (2022)](https://www.journalofmedicalinformatics.com/)

## Contributing

LangExtract is open source. Contributions are welcome:
- Report issues on GitHub
- Submit pull requests for improvements
- Share your use cases and examples

## License

LangExtract is released under the Apache 2.0 License. See the [LICENSE](https://github.com/google/langextract/blob/main/LICENSE) file for details.

---

*Last updated: July 31, 2025*