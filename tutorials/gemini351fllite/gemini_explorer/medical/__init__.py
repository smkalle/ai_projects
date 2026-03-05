"""Medical Diagnostic Workbench — agentic AI demo using Google ADK.

EDUCATIONAL DEMO ONLY — NOT FOR CLINICAL USE.
"""

import os

# Bridge: ADK uses GOOGLE_API_KEY; existing project uses GEMINI_API_KEY.
# Move the key to GOOGLE_API_KEY (the standard name) and remove the duplicate
# to suppress the "Both keys are set" warning from google-genai.
_gemini_key = os.environ.get("GEMINI_API_KEY")
if _gemini_key:
    os.environ.setdefault("GOOGLE_API_KEY", _gemini_key)
    if os.environ.get("GOOGLE_API_KEY") == _gemini_key:
        os.environ.pop("GEMINI_API_KEY", None)
