"""Medical-specific extractor with pre-built templates."""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import textwrap

from .base_extractor import BaseExtractor, ExtractionResult
from config.settings import settings


logger = logging.getLogger(__name__)


class MedicalExtractor(BaseExtractor):
    """Extractor specialized for medical research documents."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.templates = self._load_medical_templates()
    
    def _load_medical_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load pre-configured medical extraction templates."""
        templates = {}
        
        # Clinical Trial Template
        templates["clinical_trial"] = {
            "name": "Clinical Trial Data",
            "prompt": textwrap.dedent("""\
                Extract clinical trial information from the text.
                
                For each clinical trial or study mentioned, extract:
                - Trial ID or study name
                - Patient demographics (age, gender, ethnicity)
                - Inclusion/exclusion criteria
                - Interventions (drug name, dosage, duration)
                - Primary and secondary outcomes
                - Adverse events
                - Statistical results (p-values, confidence intervals)
                
                Format as JSON with fields: trial_id, demographics, criteria, intervention, outcomes, adverse_events, statistics
                
                Example:
                Input: "In the RECOVERY trial (NCT04381936), 2104 patients (mean age 65.3 years, 64% male) 
                were randomized to receive dexamethasone 6mg daily for 10 days. Primary outcome was 28-day 
                mortality: 22.9% in dexamethasone group vs 25.7% in control (RR 0.83, 95% CI 0.75-0.93, p<0.001)."
                
                Output: [{
                    "trial_id": "RECOVERY (NCT04381936)",
                    "demographics": {"n": 2104, "mean_age": 65.3, "male_percent": 64},
                    "intervention": {"drug": "dexamethasone", "dose": "6mg daily", "duration": "10 days"},
                    "outcomes": {"primary": "28-day mortality", "results": "22.9% vs 25.7%"},
                    "statistics": {"RR": 0.83, "CI": "0.75-0.93", "p_value": "<0.001"}
                }]
            """),
            "fields": ["trial_id", "demographics", "criteria", "intervention", "outcomes", "adverse_events", "statistics"]
        }
        
        # Case Report Template
        templates["case_report"] = {
            "name": "Case Report",
            "prompt": textwrap.dedent("""\
                Extract case report information from medical text.
                
                For each patient case, extract:
                - Patient demographics (age, sex, medical history)
                - Presenting symptoms
                - Physical examination findings
                - Laboratory/imaging results
                - Diagnosis
                - Treatment plan
                - Follow-up and outcome
                
                Format as JSON with fields: demographics, symptoms, examination, investigations, diagnosis, treatment, outcome
                
                Example:
                Input: "A 45-year-old male presented with chest pain and dyspnea. ECG showed ST elevation 
                in leads V1-V4. Troponin I was 15.2 ng/mL. Diagnosed with anterior STEMI. Underwent 
                emergency PCI with stent placement to LAD. Discharged on dual antiplatelet therapy."
                
                Output: [{
                    "demographics": {"age": 45, "sex": "male"},
                    "symptoms": ["chest pain", "dyspnea"],
                    "investigations": {"ECG": "ST elevation V1-V4", "troponin_I": "15.2 ng/mL"},
                    "diagnosis": "anterior STEMI",
                    "treatment": ["emergency PCI", "stent to LAD", "dual antiplatelet therapy"]
                }]
            """),
            "fields": ["demographics", "symptoms", "examination", "investigations", "diagnosis", "treatment", "outcome"]
        }
        
        # Drug Information Template
        templates["drug_information"] = {
            "name": "Drug Information",
            "prompt": textwrap.dedent("""\
                Extract drug and medication information from the text.
                
                For each drug mentioned, extract:
                - Drug name (generic and brand)
                - Drug class
                - Indication
                - Dosage and administration
                - Side effects
                - Contraindications
                - Drug interactions
                
                Format as JSON with fields: drug_name, drug_class, indication, dosage, side_effects, contraindications, interactions
                
                Example:
                Input: "Metformin (Glucophage) is a biguanide antidiabetic agent indicated for type 2 diabetes. 
                Starting dose is 500mg twice daily with meals. Common side effects include GI upset and diarrhea. 
                Contraindicated in severe renal impairment (eGFR <30). May interact with contrast dye."
                
                Output: [{
                    "drug_name": {"generic": "Metformin", "brand": "Glucophage"},
                    "drug_class": "biguanide antidiabetic",
                    "indication": "type 2 diabetes",
                    "dosage": "500mg twice daily with meals",
                    "side_effects": ["GI upset", "diarrhea"],
                    "contraindications": ["severe renal impairment (eGFR <30)"],
                    "interactions": ["contrast dye"]
                }]
            """),
            "fields": ["drug_name", "drug_class", "indication", "dosage", "side_effects", "contraindications", "interactions"]
        }
        
        # Research Findings Template
        templates["research_findings"] = {
            "name": "Research Findings",
            "prompt": textwrap.dedent("""\
                Extract research findings and conclusions from scientific text.
                
                For each study or research finding, extract:
                - Research question or hypothesis
                - Study design and methodology
                - Sample size and characteristics
                - Key results and findings
                - Statistical significance
                - Conclusions
                - Limitations
                - Clinical implications
                
                Format as JSON with fields: hypothesis, methodology, sample, results, statistics, conclusions, limitations, implications
                
                Example:
                Input: "We hypothesized that early mobilization reduces ICU length of stay. In this RCT, 
                300 mechanically ventilated patients were randomized to early mobilization (n=150) or 
                standard care (n=150). ICU LOS was 7.5 days vs 11.6 days (p<0.001). We conclude that 
                early mobilization significantly reduces ICU stay. Limitations include single-center design."
                
                Output: [{
                    "hypothesis": "early mobilization reduces ICU length of stay",
                    "methodology": "RCT",
                    "sample": {"total": 300, "intervention": 150, "control": 150},
                    "results": {"ICU_LOS": "7.5 days vs 11.6 days"},
                    "statistics": {"p_value": "<0.001"},
                    "conclusions": "early mobilization significantly reduces ICU stay",
                    "limitations": ["single-center design"]
                }]
            """),
            "fields": ["hypothesis", "methodology", "sample", "results", "statistics", "conclusions", "limitations", "implications"]
        }
        
        # Patient Records Template
        templates["patient_records"] = {
            "name": "Patient Records",
            "prompt": textwrap.dedent("""\
                Extract patient information from medical records.
                
                For each patient encounter, extract:
                - Chief complaint
                - History of present illness
                - Past medical history
                - Current medications
                - Vital signs
                - Physical exam findings
                - Assessment and diagnosis
                - Treatment plan
                
                Format as JSON with fields: chief_complaint, hpi, pmh, medications, vitals, exam, diagnosis, plan
                
                Example:
                Input: "CC: Shortness of breath x 3 days. HPI: 68yo M with CHF, worsening dyspnea and 
                leg edema. PMH: CHF, HTN, DM2. Meds: Lisinopril 10mg, Metformin 1000mg BID. 
                VS: BP 150/90, HR 95, RR 22, O2 88% RA. Exam: Bilateral crackles, 2+ pitting edema. 
                A/P: CHF exacerbation. Admit for IV diuretics."
                
                Output: [{
                    "chief_complaint": "Shortness of breath x 3 days",
                    "hpi": "68yo M with CHF, worsening dyspnea and leg edema",
                    "pmh": ["CHF", "HTN", "DM2"],
                    "medications": ["Lisinopril 10mg", "Metformin 1000mg BID"],
                    "vitals": {"BP": "150/90", "HR": 95, "RR": 22, "O2": "88% RA"},
                    "exam": ["Bilateral crackles", "2+ pitting edema"],
                    "diagnosis": "CHF exacerbation",
                    "plan": "Admit for IV diuretics"
                }]
            """),
            "fields": ["chief_complaint", "hpi", "pmh", "medications", "vitals", "exam", "diagnosis", "plan"]
        }
        
        # Literature Review Template
        templates["literature_review"] = {
            "name": "Literature Review",
            "prompt": textwrap.dedent("""\
                Extract key information from literature reviews and meta-analyses.
                
                For each study or paper referenced, extract:
                - Study title and authors
                - Year of publication
                - Study type (RCT, cohort, case-control, etc.)
                - Key findings
                - Effect sizes or risk ratios
                - Quality assessment
                - Citations
                
                Format as JSON with fields: title, authors, year, study_type, findings, effect_size, quality, citation
                
                Example:
                Input: "Smith et al. (2023) conducted a systematic review of 15 RCTs (n=3,456) examining 
                beta-blocker efficacy in heart failure. They found a 35% reduction in mortality 
                (RR 0.65, 95% CI 0.55-0.75). The studies were rated as high quality with low risk of bias."
                
                Output: [{
                    "authors": "Smith et al.",
                    "year": 2023,
                    "study_type": "systematic review of 15 RCTs",
                    "sample_size": 3456,
                    "findings": "35% reduction in mortality with beta-blockers in heart failure",
                    "effect_size": {"RR": 0.65, "CI": "0.55-0.75"},
                    "quality": "high quality with low risk of bias"
                }]
            """),
            "fields": ["title", "authors", "year", "study_type", "findings", "effect_size", "quality", "citation"]
        }
        
        return templates
    
    def extract_with_template(self,
                            text: str,
                            template_name: str,
                            source_name: str = "direct_input",
                            **kwargs) -> ExtractionResult:
        """Extract information using a pre-configured medical template."""
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = self.templates[template_name]
        prompt = template["prompt"]
        
        logger.info(f"Using medical template: {template_name}")
        
        # Call parent extract method
        result = self.extract_from_text(
            text=text,
            prompt=prompt,
            source_name=source_name,
            **kwargs
        )
        
        # Update template used
        result.template_used = template_name
        
        return result
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """Return available medical templates with descriptions."""
        return {
            name: {
                "name": template["name"],
                "fields": template["fields"],
                "description": template["prompt"].split("\n")[1].strip()
            }
            for name, template in self.templates.items()
        }
    
    def create_custom_template(self,
                             name: str,
                             description: str,
                             fields: List[str],
                             examples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a custom extraction template."""
        # Build prompt from description and examples
        prompt_parts = [
            f"Extract {description} from the text.",
            "",
            "Extract the following fields:"
        ]
        
        for field in fields:
            prompt_parts.append(f"- {field}")
        
        prompt_parts.extend([
            "",
            f"Format as JSON with fields: {', '.join(fields)}",
            ""
        ])
        
        # Add examples
        for i, example in enumerate(examples, 1):
            prompt_parts.append(f"Example {i}:")
            prompt_parts.append(f"Input: {example.get('input', '')}")
            prompt_parts.append(f"Output: {example.get('output', '')}")
            prompt_parts.append("")
        
        prompt = "\n".join(prompt_parts)
        
        # Create template
        template = {
            "name": name,
            "prompt": prompt,
            "fields": fields,
            "custom": True
        }
        
        # Add to templates
        self.templates[name] = template
        
        return template