"""Mock medical tool functions for the diagnostic pipeline.

EDUCATIONAL DEMO ONLY — NOT FOR CLINICAL USE.
All data is synthetic. No real medical databases are queried.
"""

import json


# ── Drug interaction lookup ───────────────────────────────────────────────────


def lookup_drug_interaction(drug_a: str, drug_b: str) -> str:
    """Look up the interaction between two medications.
    MOCK DATA — educational demo only. Not for clinical use.

    Args:
        drug_a: First medication name
        drug_b: Second medication name

    Returns:
        JSON with severity, description, clinical_significance, action_required.
    """
    INTERACTIONS = {
        ("warfarin", "aspirin"): {
            "severity": "MAJOR",
            "description": "Additive anticoagulant effect. Significantly increases bleeding risk.",
            "clinical_significance": "Monitor INR closely. Avoid combination if possible.",
            "action_required": True,
        },
        ("metformin", "contrast"): {
            "severity": "MAJOR",
            "description": "Iodinated contrast media may cause lactic acidosis in patients on metformin.",
            "clinical_significance": "Hold metformin 48h before/after contrast.",
            "action_required": True,
        },
        ("lisinopril", "potassium"): {
            "severity": "MODERATE",
            "description": "ACE inhibitor + potassium supplement may cause hyperkalemia.",
            "clinical_significance": "Monitor serum potassium.",
            "action_required": False,
        },
        ("ssri", "maoi"): {
            "severity": "CONTRAINDICATED",
            "description": "Risk of serotonin syndrome. Life-threatening.",
            "clinical_significance": "Do NOT combine. Allow 14-day washout.",
            "action_required": True,
        },
    }

    key = (drug_a.lower(), drug_b.lower())
    reverse_key = (drug_b.lower(), drug_a.lower())

    interaction = INTERACTIONS.get(key) or INTERACTIONS.get(reverse_key) or {
        "severity": "UNKNOWN",
        "description": f"No known interaction data for {drug_a} + {drug_b} in demo database.",
        "clinical_significance": "Consult a pharmacist for clinical decisions.",
        "action_required": False,
    }

    return json.dumps(
        {"drug_a": drug_a, "drug_b": drug_b, **interaction, "disclaimer": "MOCK DATA — not for clinical use"}
    )


# ── BMI calculator ────────────────────────────────────────────────────────────


def calculate_bmi(weight_kg: float, height_cm: float) -> str:
    """Calculate Body Mass Index (BMI) from weight and height.
    MOCK CALCULATION — educational demo only.

    Args:
        weight_kg: Patient weight in kilograms
        height_cm: Patient height in centimeters

    Returns:
        JSON with bmi, category, healthy_range.
    """
    if height_cm <= 0 or weight_kg <= 0:
        return json.dumps({"error": "Invalid measurements provided"})

    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m**2), 1)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25.0:
        category = "Normal weight"
    elif bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"

    return json.dumps(
        {
            "bmi": bmi,
            "category": category,
            "healthy_range": "18.5 - 24.9",
            "disclaimer": "MOCK CALCULATION — not for clinical use",
        }
    )


# ── eGFR calculator ──────────────────────────────────────────────────────────


def calculate_egfr(creatinine_mg_dl: float, age: int, sex: str) -> str:
    """Estimate glomerular filtration rate using simplified CKD-EPI formula.
    MOCK CALCULATION — educational demo only. Not for clinical use.

    Args:
        creatinine_mg_dl: Serum creatinine in mg/dL
        age: Patient age in years
        sex: "male" or "female"

    Returns:
        JSON with egfr, ckd_stage, interpretation.
    """
    if creatinine_mg_dl <= 0 or age <= 0:
        return json.dumps({"error": "Invalid parameters"})

    kappa = 0.7 if sex.lower() == "female" else 0.9
    alpha = -0.241 if sex.lower() == "female" else -0.302
    sex_factor = 1.012 if sex.lower() == "female" else 1.0

    ratio = creatinine_mg_dl / kappa
    if ratio < 1:
        egfr = 142 * (ratio**alpha) * (0.9938**age) * sex_factor
    else:
        egfr = 142 * (ratio**-1.200) * (0.9938**age) * sex_factor

    egfr = round(egfr, 1)

    if egfr >= 90:
        stage, interpretation = "G1 (Normal)", "Normal or high"
    elif egfr >= 60:
        stage, interpretation = "G2 (Mildly decreased)", "Mildly decreased"
    elif egfr >= 45:
        stage, interpretation = "G3a (Mild-moderate)", "Mild to moderately decreased"
    elif egfr >= 30:
        stage, interpretation = "G3b (Moderate-severe)", "Moderately to severely decreased"
    elif egfr >= 15:
        stage, interpretation = "G4 (Severely decreased)", "Severely decreased"
    else:
        stage, interpretation = "G5 (Kidney failure)", "Kidney failure"

    return json.dumps(
        {
            "egfr_ml_min_1_73m2": egfr,
            "ckd_stage": stage,
            "interpretation": interpretation,
            "disclaimer": "MOCK CALCULATION — not for clinical use",
        }
    )


# ── ICD-10 lookup ─────────────────────────────────────────────────────────────


def lookup_icd_code(condition: str) -> str:
    """Look up ICD-10 code for a medical condition.
    MOCK DATA — educational demo only. Limited condition set.

    Args:
        condition: Medical condition name (e.g. "pneumonia", "stroke")

    Returns:
        JSON with icd_10_code, description, category.
    """
    ICD_CODES = {
        "acute myocardial infarction": ("I21.9", "Acute myocardial infarction, unspecified", "Cardiovascular"),
        "unstable angina": ("I20.0", "Unstable angina", "Cardiovascular"),
        "heart failure": ("I50.9", "Heart failure, unspecified", "Cardiovascular"),
        "pneumonia": ("J18.9", "Pneumonia, unspecified organism", "Respiratory"),
        "pulmonary embolism": ("I26.99", "Other pulmonary embolism", "Cardiovascular"),
        "appendicitis": ("K37", "Unspecified appendicitis", "Gastrointestinal"),
        "migraine": ("G43.909", "Migraine, unspecified, not intractable", "Neurological"),
        "stroke": ("I63.9", "Cerebral infarction, unspecified", "Neurological"),
        "diabetes type 2": ("E11.9", "Type 2 diabetes mellitus without complications", "Endocrine"),
        "hypertension": ("I10", "Essential (primary) hypertension", "Cardiovascular"),
        "urinary tract infection": ("N39.0", "Urinary tract infection, site not specified", "Genitourinary"),
        "cellulitis": ("L03.90", "Cellulitis, unspecified", "Dermatological"),
        "melanoma": ("C43.9", "Malignant melanoma of skin, unspecified", "Oncological"),
        "basal cell carcinoma": ("C44.91", "Basal cell carcinoma of skin, unspecified", "Oncological"),
        "sepsis": ("A41.9", "Sepsis, unspecified organism", "Infectious"),
        "chronic fatigue syndrome": ("R53.82", "Chronic fatigue, unspecified", "General"),
        "fibromyalgia": ("M79.7", "Fibromyalgia", "Musculoskeletal"),
        "measles": ("B05.9", "Measles without complication", "Infectious"),
    }

    condition_lower = condition.lower()
    for key, (code, desc, category) in ICD_CODES.items():
        if key in condition_lower or condition_lower in key:
            return json.dumps(
                {
                    "condition": condition,
                    "icd_10_code": code,
                    "description": desc,
                    "category": category,
                    "disclaimer": "MOCK DATA — not for clinical use",
                }
            )

    return json.dumps(
        {
            "condition": condition,
            "icd_10_code": "Z00.00",
            "description": f"Condition not in demo database: {condition}",
            "category": "Unspecified",
            "disclaimer": "MOCK DATA — not for clinical use",
        }
    )


# ── Contraindication check ────────────────────────────────────────────────────


def check_contraindication(medication: str, condition: str) -> str:
    """Check whether a medication is contraindicated in a given condition.
    MOCK DATA — educational demo only. Not for clinical use.

    Args:
        medication: Medication name or class
        condition: Medical condition to check against

    Returns:
        JSON with is_contraindicated, severity, reason, alternatives.
    """
    CONTRAINDICATIONS = {
        ("beta_blocker", "asthma"): (True, "ABSOLUTE", "Beta-blockers can cause bronchospasm in asthma", ["CCB", "ACE inhibitor"]),
        ("nsaid", "ckd"): (True, "RELATIVE", "NSAIDs reduce renal blood flow and worsen CKD", ["acetaminophen", "tramadol"]),
        ("metformin", "renal_failure"): (True, "ABSOLUTE", "Risk of lactic acidosis when eGFR < 30", ["insulin", "GLP-1 agonist"]),
        ("warfarin", "pregnancy"): (True, "ABSOLUTE", "Teratogenic — causes warfarin embryopathy", ["heparin", "LMWH"]),
        ("aspirin", "peptic_ulcer"): (True, "RELATIVE", "Inhibits prostaglandins, worsens mucosal protection", ["PPI co-prescribing"]),
    }

    key = (medication.lower().replace(" ", "_"), condition.lower().replace(" ", "_"))
    result = CONTRAINDICATIONS.get(key)

    if result:
        is_contra, severity, reason, alternatives = result
        return json.dumps(
            {
                "medication": medication,
                "condition": condition,
                "is_contraindicated": is_contra,
                "severity": severity,
                "reason": reason,
                "alternative_options": alternatives,
                "disclaimer": "MOCK DATA — not for clinical use",
            }
        )

    return json.dumps(
        {
            "medication": medication,
            "condition": condition,
            "is_contraindicated": False,
            "severity": "NONE_KNOWN",
            "reason": "No known contraindication in demo database",
            "alternative_options": [],
            "disclaimer": "MOCK DATA — not for clinical use",
        }
    )


# ── Risk score calculator ─────────────────────────────────────────────────────


def calculate_risk_score(score_type: str, parameters: str) -> str:
    """Calculate a clinical risk score.
    MOCK CALCULATION — educational demo only. Not for clinical use.

    Args:
        score_type: One of "wells_pe", "chads_vasc", "curb65", "timi"
        parameters: JSON string of score-specific boolean/numeric inputs

    Returns:
        JSON with score_type, total_score, risk_category, recommendation.
    """
    SCORE_INTERPRETATIONS = {
        "wells_pe": [
            (0, 1, "Low", "Unlikely PE — consider D-dimer"),
            (2, 6, "Moderate", "Possible PE — consider CTPA"),
            (7, 99, "High", "Likely PE — proceed to CTPA/treatment"),
        ],
        "chads_vasc": [
            (0, 0, "Low", "No anticoagulation needed"),
            (1, 1, "Low-Moderate", "Consider anticoagulation"),
            (2, 9, "High", "Anticoagulation recommended"),
        ],
        "curb65": [
            (0, 1, "Low", "Home treatment appropriate"),
            (2, 2, "Moderate", "Consider hospital admission"),
            (3, 5, "High", "Hospital/ICU admission"),
        ],
        "timi": [
            (0, 2, "Low", "Low risk — outpatient management possible"),
            (3, 4, "Intermediate", "Intermediate risk — consider admission"),
            (5, 7, "High", "High risk — early invasive strategy"),
        ],
    }

    if score_type not in SCORE_INTERPRETATIONS:
        return json.dumps({"error": f"Unknown score type: {score_type}. Supported: {list(SCORE_INTERPRETATIONS)}"})

    try:
        params = json.loads(parameters) if isinstance(parameters, str) else parameters
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON in parameters"})

    total_score = sum(int(bool(v)) for v in params.values() if isinstance(v, (bool, int, float)))

    risk_category = "Unknown"
    recommendation = "Consult clinical guidelines"

    for low, high, category, rec in SCORE_INTERPRETATIONS[score_type]:
        if low <= total_score <= high:
            risk_category = category
            recommendation = rec
            break

    return json.dumps(
        {
            "score_type": score_type,
            "total_score": total_score,
            "risk_category": risk_category,
            "recommendation": recommendation,
            "disclaimer": "MOCK CALCULATION — not for clinical use",
        }
    )


# ── Hardcoded red flag detection (pre-AI, deterministic) ─────────────────────


EMERGENCY_COMBINATIONS = [
    ({"chest pain", "shortness of breath", "diaphoresis"}, "POTENTIAL CARDIAC EMERGENCY — Call 911 immediately"),
    ({"chest pain", "left arm", "jaw"}, "POTENTIAL CARDIAC EMERGENCY — Call 911 immediately"),
    ({"sudden severe headache", "worst headache"}, "POTENTIAL SUBARACHNOID HEMORRHAGE — Call 911 immediately"),
    ({"facial droop", "arm weakness", "speech"}, "POTENTIAL STROKE — Call 911 immediately"),
    ({"difficulty breathing", "throat closing"}, "POTENTIAL ANAPHYLAXIS — Call 911 immediately"),
    ({"unresponsive", "not breathing"}, "CARDIAC ARREST — Call 911 immediately. Begin CPR."),
]


def check_hardcoded_red_flags(symptoms: list[str], chief_complaint: str) -> list[dict]:
    """Rule-based (no AI) red flag detection. Always runs BEFORE any LLM call.

    Args:
        symptoms: List of symptom strings
        chief_complaint: Free-text chief complaint

    Returns:
        List of emergency alert dicts with type, message, action.
    """
    text = " ".join(symptoms + [chief_complaint]).lower()
    alerts = []
    for keywords, message in EMERGENCY_COMBINATIONS:
        if sum(1 for kw in keywords if kw in text) >= 2:
            alerts.append({"type": "HARDCODED_RED_FLAG", "message": message, "action": "CALL 911"})
    return alerts
