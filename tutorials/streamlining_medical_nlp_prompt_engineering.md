
# 🧠 Streamlining Medical NLP with Prompt Engineering: A GitHub Tutorial

This notebook guides AI engineers through using the `promptify` Python library to solve a real-world **medical NLP** classification task with **structured outputs** using LLMs.

📈 *2023 JBI Study*: NLP tools improved clinical decision-making by **15–20%** when they generated structured data.  
📊 *2024 NIH Report*: LLM-based medical research saw a **30% rise** since 2022.

---

## 🔧 Step 1: Setup & Installation

Install the required libraries:

```bash
pip install promptify openai
```

---

## 🔑 Step 2: Configure API Key

Use an environment variable to securely set your OpenAI API key.

```python
import os

# Set your OpenAI API key (you should ideally store this securely)
api_key = 'your-api-key-here'
os.environ['OPENAI_API_KEY'] = api_key
```

---

## 🏥 Step 3: Define the Medical NLP Task

We'll classify the patient's condition into one of:  
`Neurological`, `Cardiovascular`, `Infectious Disease`, or `Other`.

**Patient Scenario**:  
> Age: 93  
> Symptoms: "The patient presents with sudden onset of severe headache, dizziness, and unilateral weakness in the left arm. They also report blurred vision and difficulty speaking."

---

## 🧱 Step 4: Build the Prompt with `promptify`

We define a structured prompt template to instruct the LLM.

```python
prompt_template = {
    "domain": "medical",
    "task_type": "classification",
    "model": "gpt-3.5-turbo",
    "prompt": {
        "role": "You are a medical expert system designed to assist healthcare professionals.",
        "instruction": "Analyze the provided patient symptoms and classify the potential medical condition into one of the following categories: Neurological, Cardiovascular, Infectious Disease, or Other. Provide the classification and a brief rationale.",
        "examples": [
            {
                "symptoms": "Fever, cough, and shortness of breath.",
                "output": {
                    "classification": "Infectious Disease",
                    "rationale": "The combination of fever, cough, and shortness of breath are classic symptoms of a respiratory infection."
                }
            }
        ],
        "input": {
            "symptoms": "{text_input}"
        },
        "output_format": {
            "classification": "string",
            "rationale": "string"
        }
    }
}
```

---

## 🚀 Step 5: Execute the Pipeline

```python
from promptify import OpenAI
from promptify.prompts import NLPipeline
import json

# Ensure API key is available
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OpenAI API key not set. Please set the 'OPENAI_API_KEY' environment variable.")

# Initialize model
model = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Create NLP pipeline
nlp_pipeline = NLPipeline(
    prompt_template=prompt_template,
    model=model
)

# Input patient symptoms
patient_symptoms = "The patient presents with sudden onset of severe headache, dizziness, and unilateral weakness in the left arm. They also report blurred vision and difficulty speaking."

# Run the prompt
result = nlp_pipeline.run(patient_symptoms)

# Output result
print(json.dumps(result, indent=2))
```

---

## 🩺 Expected Output

```json
{
  "classification": "Neurological",
  "rationale": "The combination of sudden severe headache, unilateral weakness, dizziness, blurred vision, and difficulty speaking are highly indicative of a potential neurological event, such as a stroke."
}
```

---

## 🧩 Step 6: Integrate into Clinical Systems

Structured outputs like the above can be used to:

- 🏥 **Update EHRs** with potential diagnoses.
- 🚨 **Trigger CDSS** alerts for urgent follow-up (e.g., order a CT scan).
- 📄 **Auto-generate reports** for physician review.

---

## ✅ Conclusion

Prompt engineering with `promptify` helps move LLMs beyond simple text generation—into **clinically actionable, reliable, and structured AI tools**.

---

## 📎 Resources

- [`promptify` GitHub](https://github.com/promptslab/Promptify)
- [OpenAI API](https://platform.openai.com/)
- Journal of Biomedical Informatics, 2023
- NIH Medical AI Report, 2024
