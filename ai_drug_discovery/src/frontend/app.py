"""
Streamlit Frontend for Rare Disease Drug Repurposing AI
Silicon Valley Style Interface
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Any
import asyncio

# Page configuration
st.set_page_config(
    page_title="RareDrug.AI | Drug Repurposing for Rare Diseases",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Silicon Valley style
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .main {
        padding: 0rem 1rem;
    }

    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .hero-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 3rem 2rem;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }

    .metric-card {
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        transition: transform 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
    }

    .drug-candidate-card {
        background: linear-gradient(145deg, #f8fafc, #e2e8f0);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }

    .confidence-high { border-left-color: #10b981; }
    .confidence-moderate { border-left-color: #f59e0b; }
    .confidence-low { border-left-color: #ef4444; }

    .sidebar-metric {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(5px);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255,255,255,0.2);
    }

    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }

    h1 {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    .stButton>button {
        background: linear-gradient(45deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
    }

    .citation-badge {
        background: #e0f2fe;
        color: #0277bd;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
        margin: 0.2rem;
    }

    .warning-box {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #f39c12;
    }

    .success-box {
        background: linear-gradient(135deg, #d1edff, #a7f3d0);
        border: 1px solid #a7f3d0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #10b981;
    }
</style>
""", unsafe_allow_html=True)

# Constants
API_BASE_URL = "http://localhost:8000/api/v1"

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

def make_api_request(endpoint: str, method: str = "GET", data: dict = None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            response = requests.get(url, timeout=30)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("🔴 Cannot connect to backend API. Please ensure the FastAPI server is running.")
        return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

def display_hero_section():
    """Display the hero section with branding"""
    st.markdown("""
    <div class="hero-container">
        <h1>🧬 RareDrug.AI</h1>
        <div class="subtitle">
            AI-Powered Drug Repurposing for Rare Diseases<br>
            <em>Accelerating hope through computational discovery</em>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar_metrics():
    """Display system metrics in sidebar"""
    st.sidebar.markdown("### 📊 System Status")

    # Get system stats
    stats = make_api_request("/stats/system")
    if stats:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Analyses", stats.get('analyses_completed', 0))
        with col2:
            st.metric("Active Jobs", stats.get('active_jobs', 0))

    # Health check
    health = make_api_request("/health")
    if health:
        status = health.get('status', 'unknown')
        if status == 'healthy':
            st.sidebar.success("🟢 System Healthy")
        else:
            st.sidebar.error("🔴 System Issues")

def create_disease_input_form():
    """Create the disease input form"""
    with st.container():
        st.markdown("### 🔬 Disease Analysis Setup")

        col1, col2 = st.columns([2, 1])

        with col1:
            disease_name = st.text_input(
                "Disease Name",
                placeholder="e.g., Hutchinson-Gilford Progeria Syndrome",
                help="Enter the name of the rare disease to analyze"
            )

            disease_description = st.text_area(
                "Disease Description (Optional)",
                placeholder="Brief description of the disease symptoms and characteristics",
                height=100
            )

        with col2:
            omim_id = st.text_input(
                "OMIM ID (Optional)",
                placeholder="e.g., 176670",
                help="Online Mendelian Inheritance in Man identifier"
            )

            orphanet_id = st.text_input(
                "Orphanet ID (Optional)",
                placeholder="e.g., 740",
                help="Orphanet rare disease identifier"
            )

        return {
            "name": disease_name,
            "description": disease_description,
            "omim_id": omim_id if omim_id else None,
            "orphanet_id": orphanet_id if orphanet_id else None
        }

def create_patient_profile_form():
    """Create patient profile input form"""
    with st.expander("👤 Patient Profile (Optional)", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=None)
            sex = st.selectbox("Sex", ["", "male", "female", "other"])

        with col2:
            weight = st.number_input("Weight (kg)", min_value=0.0, value=None)

        with col3:
            st.markdown("**Genetic Variants**")
            genetic_variants = st.text_area(
                "genetic_variants",
                placeholder="e.g., LMNA:c.1824C>T",
                height=60,
                label_visibility="collapsed"
            )

        symptoms = st.text_area(
            "Symptoms",
            placeholder="Enter symptoms separated by commas",
            help="List the main symptoms observed"
        )

        medications = st.text_area(
            "Current Medications",
            placeholder="Enter current medications separated by commas"
        )

        allergies = st.text_area(
            "Known Allergies",
            placeholder="Enter known drug allergies separated by commas"
        )

        return {
            "age": int(age) if age else None,
            "sex": sex if sex else None,
            "weight_kg": weight if weight else None,
            "genetic_variants": [v.strip() for v in genetic_variants.split(',') if v.strip()] if genetic_variants else [],
            "symptoms": [s.strip() for s in symptoms.split(',') if s.strip()] if symptoms else [],
            "current_medications": [m.strip() for m in medications.split(',') if m.strip()] if medications else [],
            "allergies": [a.strip() for a in allergies.split(',') if a.strip()] if allergies else []
        }

def create_analysis_parameters():
    """Create analysis parameters form"""
    with st.expander("⚙️ Analysis Parameters", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            confidence_threshold = st.slider(
                "Confidence Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Minimum confidence score for drug candidates"
            )

            max_results = st.number_input(
                "Max Results",
                min_value=1,
                max_value=50,
                value=10,
                help="Maximum number of drug candidates to return"
            )

        with col2:
            include_experimental = st.checkbox(
                "Include Experimental Drugs",
                value=False,
                help="Include drugs not yet approved by regulatory agencies"
            )

            prioritize_safety = st.checkbox(
                "Prioritize Safety",
                value=True,
                help="Prioritize drugs with better safety profiles"
            )

        return {
            "confidence_threshold": confidence_threshold,
            "max_results": max_results,
            "include_experimental": include_experimental,
            "prioritize_safety": prioritize_safety
        }

def display_drug_candidates(results):
    """Display drug candidates in an attractive format"""
    if not results or 'drug_candidates' not in results:
        return

    candidates = results['drug_candidates']

    st.markdown("### 💊 Drug Candidates")

    for i, candidate in enumerate(candidates):
        drug = candidate['drug']
        analysis = candidate['repurposing_analysis']
        safety = candidate['safety_profile']
        citations = candidate.get('citations', [])

        confidence_class = f"confidence-{analysis['confidence_level']}"

        st.markdown(f"""
        <div class="drug-candidate-card {confidence_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #1e293b;">{drug['name']}</h4>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="background: #3b82f6; color: white; padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.8rem;">
                        {analysis['confidence_score']:.2f} confidence
                    </span>
                    <span style="background: #10b981; color: white; padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.8rem;">
                        {len(citations)} citations
                    </span>
                </div>
            </div>

            <p style="color: #64748b; margin: 0.5rem 0;"><strong>Mechanism:</strong> {analysis['mechanism_of_action']}</p>
            <p style="color: #64748b; margin: 0.5rem 0;"><strong>Expected Benefit:</strong> {analysis['expected_benefit']}</p>

            {f"<p style='color: #64748b; margin: 0.5rem 0;'><strong>Generic Name:</strong> {drug['generic_name']}</p>" if drug.get('generic_name') else ""}
            {f"<p style='color: #64748b; margin: 0.5rem 0;'><strong>Brand Names:</strong> {', '.join(drug['brand_names'])}</p>" if drug.get('brand_names') else ""}
        </div>
        """, unsafe_allow_html=True)

        # Expandable details
        with st.expander(f"🔍 Detailed Analysis - {drug['name']}", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Safety Profile:**")
                if safety.get('known_side_effects'):
                    st.write("• Side Effects:", ", ".join(safety['known_side_effects'][:5]))
                if safety.get('contraindications'):
                    st.write("• Contraindications:", ", ".join(safety['contraindications'][:3]))

            with col2:
                st.markdown("**Drug Information:**")
                if drug.get('atc_code'):
                    st.write("• ATC Code:", drug['atc_code'])
                if drug.get('molecular_weight'):
                    st.write("• Molecular Weight:", drug['molecular_weight'])

            # Citations
            if citations:
                st.markdown("**Key Citations:**")
                for j, citation in enumerate(citations[:3]):
                    st.markdown(f"""
                    <div class="citation-badge">
                        {citation['journal']} ({citation['year']}) - Evidence Level {citation['evidence_level']}
                    </div>
                    """, unsafe_allow_html=True)

def display_analysis_summary(results):
    """Display analysis summary with metrics"""
    if not results:
        return

    summary = results.get('summary', {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Candidates",
            summary.get('total_candidates', 0),
            help="Total number of drug candidates found"
        )

    with col2:
        st.metric(
            "High Confidence",
            summary.get('high_confidence', 0),
            help="Number of high-confidence candidates"
        )

    with col3:
        st.metric(
            "Citations",
            results.get('citations', {}).get('total_sources', 0),
            help="Total number of scientific citations"
        )

    with col4:
        st.metric(
            "Quality Score",
            f"{results.get('citations', {}).get('quality_score', 0):.1f}/10",
            help="Overall quality score of evidence"
        )

def main():
    """Main application function"""
    display_hero_section()
    display_sidebar_metrics()

    # Main analysis form
    with st.form("drug_analysis_form"):
        st.markdown("---")

        # Disease input
        disease_data = create_disease_input_form()

        # Patient profile (optional)
        patient_data = create_patient_profile_form()

        # Analysis parameters
        analysis_params = create_analysis_parameters()

        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "🚀 Analyze Drug Repurposing Opportunities",
                use_container_width=True
            )

    # Process form submission
    if submitted and disease_data['name']:
        with st.spinner("🔬 Analyzing drug repurposing opportunities..."):
            # Prepare request data
            request_data = {
                "disease": disease_data,
                "patient_profile": patient_data if any(patient_data.values()) else None,
                "analysis_parameters": analysis_params
            }

            # Make API request
            results = make_api_request("/analyze/repurposing", "POST", request_data)

            if results:
                st.session_state.analysis_results = results['results']
                st.session_state.analysis_history.append({
                    'disease': disease_data['name'],
                    'timestamp': datetime.now(),
                    'results': results['results']
                })

                # Success message
                st.markdown("""
                <div class="success-box">
                    <strong>✅ Analysis Complete!</strong><br>
                    Found drug repurposing opportunities with citation-verified evidence.
                </div>
                """, unsafe_allow_html=True)

                st.rerun()

    elif submitted and not disease_data['name']:
        st.error("Please enter a disease name to analyze.")

    # Display results if available
    if st.session_state.analysis_results:
        st.markdown("---")
        display_analysis_summary(st.session_state.analysis_results)
        st.markdown("---")
        display_drug_candidates(st.session_state.analysis_results)

        # Research gaps
        if st.session_state.analysis_results.get('research_gaps'):
            with st.expander("🔬 Research Gaps Identified", expanded=False):
                for gap in st.session_state.analysis_results['research_gaps']:
                    st.write(f"• {gap}")

    # Medical disclaimer
    st.markdown("---")
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ Medical Disclaimer:</strong><br>
        This system is for research purposes only and should not be used as a substitute 
        for professional medical advice, diagnosis, or treatment. Always consult qualified 
        healthcare professionals for medical decisions.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()