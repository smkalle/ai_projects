"""Prompt templates for Memory Bridge generation and evaluation."""

TEXT_MODEL = "gemini-3-flash-preview"
IMAGE_MODEL = "gemini-3.1-flash-image-preview"

SAFETY_RULES = """
Use only caregiver-provided facts.
Do not infer family relationships, medical details, dates, or events.
Do not include diagnosis, treatment, prognosis, medication advice, or emergency guidance.
Use respectful adult language.
Avoid childlike, infantilizing, or sentimentalized wording.
Respect all privacy exclusions.
Mark uncertain details as caregiver-provided or needing confirmation.
""".strip()

IMAGE_SAFETY_RULES = """
Create print-friendly, high-contrast, large-type visual material.
Use minimal sections and no dense paragraphs.
Do not generate photorealistic depictions of real people.
Do not invent dates, places, family members, diagnoses, or care instructions.
Avoid childish graphics and busy backgrounds.
""".strip()
