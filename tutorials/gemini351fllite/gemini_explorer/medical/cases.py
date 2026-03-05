"""Sample patient cases for the medical diagnostic pipeline.

EDUCATIONAL DEMO ONLY — NOT FOR CLINICAL USE.
All cases are fictional with synthetic data for developer education.
"""

from .schemas import PatientIntake, Vitals


# ── Case 1: Cardiac — Chest Pain ─────────────────────────────────────────────

CASE_CHEST_PAIN = PatientIntake(
    patient_id="demo_001",
    age=58,
    sex="male",
    case_name="Chest Pain — Cardiac Workup",
    chief_complaint=(
        "Severe crushing chest pain radiating to the left arm, started 45 minutes ago. "
        "Accompanied by shortness of breath, diaphoresis, and nausea. "
        "Pain rated 9/10. No relief with antacids."
    ),
    symptoms=["chest pain", "dyspnea", "diaphoresis", "nausea", "left arm radiation"],
    symptom_duration_days=0,
    medical_history=["hypertension", "hyperlipidemia", "type 2 diabetes", "former smoker"],
    current_medications=["lisinopril 10mg", "atorvastatin 40mg", "metformin 500mg"],
    allergies=["penicillin"],
    vitals=Vitals(
        temperature_c=37.1,
        heart_rate_bpm=102,
        blood_pressure_systolic=158,
        blood_pressure_diastolic=94,
        respiratory_rate=22,
        oxygen_saturation_pct=95.0,
        weight_kg=92,
        height_cm=178,
    ),
    lab_values={
        "troponin_ng_ml": 0.8,
        "ck_mb_ng_ml": 12.4,
        "bnp_pg_ml": 180,
        "creatinine_mg_dl": 1.1,
        "glucose_mg_dl": 210,
        "wbc_k_ul": 12.1,
    },
    has_image=False,
    has_audio=False,
)
# Expected: EMERGENT triage, Cardiology specialist
# Demonstrates: Red flag detection, TIMI score, drug interactions


# ── Case 2: Dermatology — Skin Lesion with Image ─────────────────────────────

CASE_SKIN_LESION = PatientIntake(
    patient_id="demo_002",
    age=42,
    sex="female",
    case_name="Skin Lesion — Dermatology (with Image)",
    chief_complaint=(
        "Noticed a changing mole on my upper back over the past 3 months. "
        "It has grown from about 4mm to what feels like 8-9mm. The border looks uneven "
        "and it seems to have become darker on one side. No itching or bleeding yet."
    ),
    symptoms=["skin lesion", "changing mole", "asymmetric borders", "color variation", "growth"],
    symptom_duration_days=90,
    medical_history=["fair skin", "multiple sunburns in childhood", "blistering sunburn age 22"],
    current_medications=[],
    allergies=[],
    vitals=Vitals(
        temperature_c=36.8,
        heart_rate_bpm=72,
        blood_pressure_systolic=118,
        blood_pressure_diastolic=76,
        respiratory_rate=14,
        oxygen_saturation_pct=99.0,
        weight_kg=65,
        height_cm=168,
    ),
    lab_values={},
    has_image=True,  # Pipeline uses vision capability
    has_audio=False,
)
# Expected: SEMI-URGENT triage, Dermatology specialist
# Demonstrates: Vision capability, ABCDE criteria


# ── Case 3: Pediatrics — Fever with Rash ─────────────────────────────────────

CASE_PEDIATRIC_FEVER = PatientIntake(
    patient_id="demo_003",
    age=4,
    sex="female",
    case_name="Pediatric Fever with Rash — Infectious Disease",
    chief_complaint=(
        "My 4-year-old daughter has had a fever of 39.8C for 3 days. "
        "Yesterday a pink spotty rash appeared on her trunk and is spreading to her face. "
        "She has been irritable, not eating well, and has some eye redness. "
        "Runny nose and cough started before the fever."
    ),
    symptoms=["fever", "rash", "irritability", "conjunctivitis", "rhinorrhea", "cough", "poor appetite"],
    symptom_duration_days=3,
    medical_history=["up to date on vaccinations", "no significant past medical history"],
    current_medications=["children's ibuprofen PRN"],
    allergies=[],
    vitals=Vitals(
        temperature_c=39.8,
        heart_rate_bpm=128,
        blood_pressure_systolic=92,
        blood_pressure_diastolic=58,
        respiratory_rate=28,
        oxygen_saturation_pct=97.5,
        weight_kg=16,
        height_cm=102,
    ),
    lab_values={
        "wbc_k_ul": 14.2,
        "crp_mg_l": 28.0,
        "lymphocyte_pct": 62,
        "platelet_k_ul": 380,
    },
    has_image=False,
    has_audio=False,
)
# Expected: URGENT triage, Pediatrics specialist
# Demonstrates: Broad differential (viral exanthem), loop runs 2+ iterations


# ── Case 4: Complex — Chronic Fatigue ─────────────────────────────────────────

CASE_CHRONIC_FATIGUE = PatientIntake(
    patient_id="demo_004",
    age=35,
    sex="female",
    case_name="Chronic Fatigue — Multi-System Deep Reasoning",
    chief_complaint=(
        "Extreme fatigue for 8 months. I wake up unrefreshed even after 10 hours of sleep. "
        "I have brain fog, difficulty concentrating, widespread muscle aches, and occasional "
        "low-grade fevers. Exercise makes everything worse for days. I've also had recurrent "
        "sore throats. Had a flu-like illness in November that I never fully recovered from. "
        "I've seen three doctors and nothing abnormal has been found."
    ),
    symptoms=[
        "chronic fatigue",
        "unrefreshing sleep",
        "brain fog",
        "cognitive impairment",
        "myalgia",
        "post-exertional malaise",
        "recurrent sore throat",
        "low-grade fever",
        "tender lymph nodes",
    ],
    symptom_duration_days=240,
    medical_history=["anxiety (resolved)", "IBS", "post-viral syndrome suspected"],
    current_medications=["vitamin D 1000IU", "magnesium 400mg"],
    allergies=["sulfa drugs"],
    vitals=Vitals(
        temperature_c=37.3,
        heart_rate_bpm=88,
        blood_pressure_systolic=108,
        blood_pressure_diastolic=70,
        respiratory_rate=16,
        oxygen_saturation_pct=98.5,
        weight_kg=62,
        height_cm=165,
    ),
    lab_values={
        "tsh_mu_l": 2.1,
        "ferritin_ng_ml": 14.0,
        "b12_pg_ml": 280,
        "crp_mg_l": 2.8,
        "wbc_k_ul": 5.8,
        "creatinine_mg_dl": 0.8,
    },
    has_image=False,
    has_audio=True,  # Demo: audio transcription capability
)
# Expected: NON-URGENT triage, General Medicine specialist
# Demonstrates: HIGH thinking (complex differential), loop runs all 3 iterations


# ── Case registry ─────────────────────────────────────────────────────────────

SAMPLE_CASES: dict[str, PatientIntake] = {
    "chest_pain": CASE_CHEST_PAIN,
    "skin_lesion": CASE_SKIN_LESION,
    "pediatric_fever": CASE_PEDIATRIC_FEVER,
    "chronic_fatigue": CASE_CHRONIC_FATIGUE,
}
