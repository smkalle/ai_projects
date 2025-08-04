"""Enhanced analysis results page with Silicon Valley design."""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app.components.design_system import apply_design_system, create_card, create_metric_card
    from app.components.responsive_layout import create_responsive_header, create_responsive_card_grid
    from app.components.animations import get_animation_css
    from app.components.theme_system import get_theme_css, create_theme_toggle
except ImportError:
    # Fallback functions
    def apply_design_system(): pass
    def create_card(content): return f"<div style='padding: 20px; background: white; border-radius: 10px; margin: 10px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>{content}</div>"
    def create_metric_card(title, value, icon=""): return create_card(f"<div style='text-align: center;'><div style='font-size: 2rem;'>{icon}</div><h3>{title}</h3><p style='font-size: 1.5rem; font-weight: bold; color: #6366f1;'>{value}</p></div>")
    def create_responsive_header(title, subtitle=""): return f"<div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border-radius: 20px; margin-bottom: 30px;'><h1>{title}</h1><p>{subtitle}</p></div>"
    def create_responsive_card_grid(cards): return "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;'>" + "".join(cards) + "</div>"
    def get_animation_css(): return "<style>.animate-fade-in-up { animation: fadeInUp 0.6s ease-out; } @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }</style>"
    def get_theme_css(): return "<style>:root { --primary: #6366f1; --secondary: #8b5cf6; --success: #10b981; --warning: #f59e0b; --error: #ef4444; }</style>"
    def create_theme_toggle(): return "<div style='position: fixed; top: 20px; right: 20px; background: white; border: 1px solid #ccc; border-radius: 50%; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; cursor: pointer;'>🌙</div>"

st.set_page_config(
    page_title="Contract Analysis Results",
    page_icon="📊",
    layout="wide"
)

# Apply design system
apply_design_system()
st.markdown(get_theme_css(), unsafe_allow_html=True)
st.markdown(get_animation_css(), unsafe_allow_html=True)
st.markdown(create_theme_toggle(), unsafe_allow_html=True)

# Mock analysis results for demonstration
mock_results = {
    "document_name": "Employment_Agreement_Sample.txt",
    "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "contract_type": "Employment Agreement",
    "overall_risk_score": 3.2,
    "compliance_status": "Mostly Compliant",
    "parties": ["ABC Corporation", "John Doe"],
    "key_terms": {
        "salary": "$120,000 per year",
        "position": "Software Engineer",
        "start_date": "January 1, 2024",
        "notice_period": "30 days"
    },
    "clauses_found": [
        {"type": "confidentiality", "risk": "low", "text": "Employee agrees to maintain confidentiality..."},
        {"type": "termination", "risk": "medium", "text": "Either party may terminate with 30 days notice..."},
        {"type": "compensation", "risk": "low", "text": "Salary of $120,000 per year..."}
    ],
    "risks": [
        {"type": "Termination Risk", "severity": "medium", "description": "At-will termination clause present"},
        {"type": "IP Assignment", "severity": "low", "description": "Standard IP assignment terms"}
    ],
    "obligations": [
        {"party": "Employee", "description": "Maintain confidentiality", "due_date": "Ongoing"},
        {"party": "Company", "description": "Pay salary bi-weekly", "due_date": "Bi-weekly"}
    ],
    "compliance_checks": {
        "GDPR": "Compliant",
        "Employment Law": "Needs Review"
    }
}

# Header
header_content = create_responsive_header(
    title="📊 Contract Analysis Results",
    subtitle=f"Complete AI-powered analysis of {mock_results['document_name']}"
)
st.markdown(header_content, unsafe_allow_html=True)

# Summary metrics
st.markdown("<h3 style='color: var(--primary); margin: 30px 0 20px 0;'>📈 Analysis Summary</h3>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    risk_color = "🟢" if mock_results["overall_risk_score"] < 4 else "🟡" if mock_results["overall_risk_score"] < 7 else "🔴"
    metric_card = create_metric_card("Risk Score", f"{mock_results['overall_risk_score']}/10", risk_color)
    st.markdown(metric_card, unsafe_allow_html=True)

with col2:
    compliance_icon = "✅" if "Compliant" in mock_results["compliance_status"] else "⚠️"
    metric_card = create_metric_card("Compliance", mock_results["compliance_status"], compliance_icon)
    st.markdown(metric_card, unsafe_allow_html=True)

with col3:
    metric_card = create_metric_card("Contract Type", mock_results["contract_type"], "📄")
    st.markdown(metric_card, unsafe_allow_html=True)

with col4:
    metric_card = create_metric_card("Parties", str(len(mock_results["parties"])), "👥")
    st.markdown(metric_card, unsafe_allow_html=True)

# Tabbed interface for detailed results
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Summary", "⚖️ Clauses", "🚨 Risks", "📝 Obligations", "✓ Compliance"])

with tab1:
    st.markdown("<h4 style='color: var(--primary);'>Contract Summary</h4>", unsafe_allow_html=True)
    
    summary_content = create_card(f"""
        <div class="animate-fade-in-up">
            <h4 style="color: var(--primary); margin-bottom: 20px;">Key Information</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                <div><strong>Document:</strong> {mock_results['document_name']}</div>
                <div><strong>Type:</strong> {mock_results['contract_type']}</div>
                <div><strong>Analyzed:</strong> {mock_results['analysis_timestamp']}</div>
                <div><strong>Parties:</strong> {', '.join(mock_results['parties'])}</div>
            </div>
            
            <h4 style="color: var(--primary); margin: 30px 0 15px 0;">Key Terms</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                {"".join([f"<div><strong>{k.title()}:</strong> {v}</div>" for k, v in mock_results['key_terms'].items()])}
            </div>
        </div>
    """)
    st.markdown(summary_content, unsafe_allow_html=True)

with tab2:
    st.markdown("<h4 style='color: var(--primary);'>Extracted Clauses</h4>", unsafe_allow_html=True)
    
    clause_cards = []
    for clause in mock_results['clauses_found']:
        risk_color = {"low": "var(--success)", "medium": "var(--warning)", "high": "var(--error)"}.get(clause['risk'], "var(--primary)")
        card = create_card(f"""
            <div class="animate-fade-in-up">
                <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 15px;">
                    <h5 style="margin: 0; color: var(--primary);">{clause['type'].title()} Clause</h5>
                    <span style="background: {risk_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">
                        {clause['risk'].upper()} RISK
                    </span>
                </div>
                <p style="color: var(--text-secondary); line-height: 1.6; margin: 0;">
                    {clause['text'][:150]}...
                </p>
            </div>
        """)
        clause_cards.append(card)
    
    cards_grid = create_responsive_card_grid(clause_cards)
    st.markdown(cards_grid, unsafe_allow_html=True)

with tab3:
    st.markdown("<h4 style='color: var(--primary);'>Risk Assessment</h4>", unsafe_allow_html=True)
    
    risk_cards = []
    for risk in mock_results['risks']:
        severity_color = {"low": "var(--success)", "medium": "var(--warning)", "high": "var(--error)"}.get(risk['severity'], "var(--primary)")
        card = create_card(f"""
            <div class="animate-fade-in-up">
                <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 15px;">
                    <h5 style="margin: 0; color: var(--primary);">{risk['type']}</h5>
                    <span style="background: {severity_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">
                        {risk['severity'].upper()}
                    </span>
                </div>
                <p style="color: var(--text-secondary); line-height: 1.6; margin: 0;">
                    {risk['description']}
                </p>
            </div>
        """)
        risk_cards.append(card)
    
    cards_grid = create_responsive_card_grid(risk_cards)
    st.markdown(cards_grid, unsafe_allow_html=True)

with tab4:
    st.markdown("<h4 style='color: var(--primary);'>Party Obligations</h4>", unsafe_allow_html=True)
    
    obligation_cards = []
    for obligation in mock_results['obligations']:
        card = create_card(f"""
            <div class="animate-fade-in-up">
                <div style="margin-bottom: 15px;">
                    <h5 style="margin: 0; color: var(--primary);">{obligation['party']}</h5>
                    <span style="color: var(--text-secondary); font-size: 0.9rem;">Due: {obligation['due_date']}</span>
                </div>
                <p style="color: var(--text-secondary); line-height: 1.6; margin: 0;">
                    {obligation['description']}
                </p>
            </div>
        """)
        obligation_cards.append(card)
    
    cards_grid = create_responsive_card_grid(obligation_cards)
    st.markdown(cards_grid, unsafe_allow_html=True)

with tab5:
    st.markdown("<h4 style='color: var(--primary);'>Compliance Status</h4>", unsafe_allow_html=True)
    
    compliance_cards = []
    for regulation, status in mock_results['compliance_checks'].items():
        status_color = "var(--success)" if status == "Compliant" else "var(--warning)" if "Review" in status else "var(--error)"
        status_icon = "✅" if status == "Compliant" else "⚠️" if "Review" in status else "❌"
        
        card = create_card(f"""
            <div class="animate-fade-in-up" style="text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 15px;">{status_icon}</div>
                <h5 style="margin: 0 0 10px 0; color: var(--primary);">{regulation}</h5>
                <span style="background: {status_color}; color: white; padding: 6px 16px; border-radius: 20px; font-size: 0.9rem;">
                    {status}
                </span>
            </div>
        """)
        compliance_cards.append(card)
    
    cards_grid = create_responsive_card_grid(compliance_cards)
    st.markdown(cards_grid, unsafe_allow_html=True)

# Action buttons
st.markdown("<h3 style='color: var(--primary); margin: 40px 0 20px 0;'>📥 Export & Actions</h3>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📄 Export PDF Report", type="primary", use_container_width=True):
        st.success("PDF report generation would be implemented here")

with col2:
    if st.button("📊 Export Excel Analysis", type="secondary", use_container_width=True):
        st.success("Excel export would be implemented here")

with col3:
    if st.button("📧 Email Summary", type="secondary", use_container_width=True):
        st.success("Email functionality would be implemented here")

with col4:
    if st.button("🔍 Analyze Another", type="secondary", use_container_width=True):
        st.switch_page("pages/1_📄_Upload_Contract.py")

# Footer with analysis details
footer_content = create_card(f"""
    <div style="text-align: center; color: var(--text-secondary);">
        <p style="margin: 0;">
            <strong>Analysis completed:</strong> {mock_results['analysis_timestamp']} | 
            <strong>Processing time:</strong> 2.3 seconds |
            <strong>Confidence:</strong> 89%
        </p>
        <p style="margin: 10px 0 0 0; font-size: 0.9rem;">
            Powered by DSPy Contract Intelligence Platform with Silicon Valley Design
        </p>
    </div>
""")
st.markdown(footer_content, unsafe_allow_html=True)
