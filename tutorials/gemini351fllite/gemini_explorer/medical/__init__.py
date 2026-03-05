"""Medical Diagnostic Workbench — agentic AI demo using Google ADK.

EDUCATIONAL DEMO ONLY — NOT FOR CLINICAL USE.
"""

import os

# Bridge: ADK uses GOOGLE_API_KEY; existing project uses GEMINI_API_KEY
if os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]
