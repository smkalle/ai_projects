"""Professional Contract Intelligence Platform - Production Quality UI."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page configuration with professional branding
st.set_page_config(
    page_title="Contract Intelligence Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Contract Intelligence Platform - AI-Powered Legal Document Analysis"
    }
)

# Professional CSS styling
st.markdown("""
<style>
/* Hide Streamlit branding and menu */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Professional color scheme */
:root {
    --primary-blue: #1e40af;
    --primary-light: #3b82f6;
    --accent-gold: #f59e0b;
    --success-green: #059669;
    --warning-orange: #ea580c;
    --error-red: #dc2626;
    --neutral-100: #f3f4f6;
    --neutral-200: #e5e7eb;
    --neutral-800: #1f2937;
    --neutral-900: #111827;
}

/* Main container styling */
.main > div {
    padding-top: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

/* Professional header */
.professional-header {
    background: linear-gradient(135deg, var(--primary-blue), var(--primary-light));
    color: white;
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.professional-header h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 700;
}

.professional-header p {
    margin: 0.5rem 0 0 0;
    font-size: 1.1rem;
    opacity: 0.9;
}

/* Metric cards */
.metric-card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid var(--neutral-200);
    text-align: center;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.2s ease;
}

.metric-card:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--primary-blue);
    margin: 0.5rem 0;
}

.metric-label {
    font-size: 0.875rem;
    color: var(--neutral-800);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Content sections */
.content-section {
    background: white;
    border-radius: 8px;
    border: 1px solid var(--neutral-200);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.section-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--neutral-900);
    margin-bottom: 1rem;
    border-bottom: 2px solid var(--primary-blue);
    padding-bottom: 0.5rem;
}

/* Status badges */
.status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.status-success {
    background-color: #d1fae5;
    color: var(--success-green);
}

.status-warning {
    background-color: #fef3c7;
    color: var(--warning-orange);
}

.status-error {
    background-color: #fee2e2;
    color: var(--error-red);
}

/* Professional buttons */
.stButton > button {
    background: var(--primary-blue);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-weight: 500;
    transition: background-color 0.2s ease;
}

.stButton > button:hover {
    background: var(--primary-light);
}

/* File uploader styling */
.stFileUploader > div > div {
    border: 2px dashed var(--primary-blue);
    border-radius: 8px;
    padding: 2rem;
    background: var(--neutral-100);
}

/* Sidebar styling */
.css-1d391kg {
    background: var(--neutral-100);
}

/* Remove default Streamlit padding */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'
if 'contracts_processed' not in st.session_state:
    st.session_state.contracts_processed = 156
if 'compliance_rate' not in st.session_state:
    st.session_state.compliance_rate = 94.2

# Professional sidebar navigation
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: var(--primary-blue); color: white; border-radius: 8px; margin-bottom: 1.5rem;">
        <h3 style="margin: 0; font-weight: 600;">⚖️ Contract Intelligence</h3>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.875rem; opacity: 0.9;">Professional Legal Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation menu
    page = st.selectbox(
        "Navigate to:",
        ["📊 Executive Dashboard", "📄 Upload & Analyze", "📈 Analytics", "⚖️ Compliance", "📋 Reports"],
        key="navigation"
    )
    
    st.markdown("---")
    
    # Quick stats in sidebar
    st.markdown("**📊 Quick Stats**")
    st.metric("Contracts This Month", "23", "↑ 12%")
    st.metric("Avg Risk Score", "3.2/10", "↓ 0.8")
    st.metric("Processing Time", "< 30s", "↓ 15s")

# Main content area
if "Executive Dashboard" in page:
    # Professional header
    st.markdown("""
    <div class="professional-header">
        <h1>Contract Intelligence Platform</h1>
        <p>AI-powered legal document analysis and risk assessment</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Total Contracts</div>
            <div class="metric-value">1,247</div>
            <div style="color: var(--success-green); font-size: 0.875rem;">↑ 8.2% this month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Risk Score Avg</div>
            <div class="metric-value">2.8</div>
            <div style="color: var(--success-green); font-size: 0.875rem;">↓ 0.4 improvement</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Compliance Rate</div>
            <div class="metric-value">96.8%</div>
            <div style="color: var(--success-green); font-size: 0.875rem;">↑ 2.1% this quarter</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Processing Time</div>
            <div class="metric-value">18s</div>
            <div style="color: var(--success-green); font-size: 0.875rem;">↓ 42% faster</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Content sections
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="content-section">
            <div class="section-title">📈 Risk Analysis Trends</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate sample data for chart
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='ME')
        risk_data = pd.DataFrame({
            'Month': dates,
            'Average Risk Score': [4.2, 3.8, 3.9, 3.6, 3.4, 3.1, 2.9, 2.8, 2.7, 2.9, 2.8, 2.6],
            'Contracts Processed': [89, 92, 106, 118, 124, 132, 145, 156, 162, 168, 174, 180]
        })
        
        fig = px.line(risk_data, x='Month', y='Average Risk Score', 
                     title="Risk Score Trends Over Time",
                     color_discrete_sequence=['#1e40af'])
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_color='#1f2937',
            title_font_size=16,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="content-section">
            <div class="section-title">🎯 Recent Activity</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Recent contracts list
        recent_contracts = [
            {"name": "Service Agreement - TechCorp", "risk": "Low", "status": "Approved"},
            {"name": "NDA - StartupXYZ", "risk": "Low", "status": "Approved"},
            {"name": "Employment Contract", "risk": "Medium", "status": "Review"},
            {"name": "Vendor Agreement", "risk": "Low", "status": "Approved"},
            {"name": "Lease Agreement", "risk": "Medium", "status": "Pending"}
        ]
        
        for contract in recent_contracts:
            risk_class = "status-success" if contract["risk"] == "Low" else "status-warning"
            status_class = "status-success" if contract["status"] == "Approved" else "status-warning"
            
            st.markdown(f"""
            <div style="padding: 0.75rem; border-bottom: 1px solid var(--neutral-200);">
                <div style="font-weight: 500; margin-bottom: 0.25rem;">{contract["name"]}</div>
                <div>
                    <span class="status-badge {risk_class}">{contract["risk"]} Risk</span>
                    <span class="status-badge {status_class}" style="margin-left: 0.5rem;">{contract["status"]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif "Upload & Analyze" in page:
    st.markdown("""
    <div class="professional-header">
        <h1>📄 Contract Upload & Analysis</h1>
        <p>Upload contracts for AI-powered legal analysis and risk assessment</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="content-section">
        <div class="section-title">📁 Upload Documents</div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose contract files (PDF, DOCX, TXT)",
        type=['pdf', 'docx', 'doc', 'txt'],
        accept_multiple_files=True,
        help="Upload one or more contract documents for analysis"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
                # Simulate processing
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(100):
                    progress_bar.progress(i + 1)
                    if i < 30:
                        status_text.text("📄 Parsing documents...")
                    elif i < 60:
                        status_text.text("🤖 AI analysis in progress...")
                    elif i < 90:
                        status_text.text("⚖️ Compliance checking...")
                    else:
                        status_text.text("✅ Analysis complete!")
                    
                    if i % 10 == 0:  # Update every 10%
                        import time
                        time.sleep(0.1)
                
                st.balloons()
                st.success("🎉 Analysis completed successfully!")
                
                # Show mock results
                st.markdown("""
                <div class="content-section">
                    <div class="section-title">📊 Analysis Results</div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Overall Risk Score", "2.8/10", "Low Risk")
                with col2:
                    st.metric("Compliance Status", "96%", "Compliant")
                with col3:
                    st.metric("Processing Time", "12.3s", "Fast")

elif "Analytics" in page:
    st.markdown("""
    <div class="professional-header">
        <h1>📈 Contract Analytics</h1>
        <p>Comprehensive insights and trends from your contract portfolio</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Analytics dashboard with charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="content-section">
            <div class="section-title">📊 Risk Distribution</div>
        </div>
        """, unsafe_allow_html=True)
        
        risk_data = pd.DataFrame({
            'Risk Level': ['Low', 'Medium', 'High'],
            'Count': [789, 324, 134]
        })
        
        fig = px.pie(risk_data, values='Count', names='Risk Level',
                    color_discrete_sequence=['#059669', '#f59e0b', '#dc2626'])
        fig.update_layout(showlegend=True, font_color='#1f2937')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="content-section">
            <div class="section-title">📋 Contract Types</div>
        </div>
        """, unsafe_allow_html=True)
        
        contract_types = pd.DataFrame({
            'Type': ['Service Agreements', 'NDAs', 'Employment', 'Vendor Contracts', 'Leases'],
            'Count': [345, 298, 189, 156, 89]
        })
        
        fig = px.bar(contract_types, x='Type', y='Count',
                    color_discrete_sequence=['#1e40af'])
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_color='#1f2937',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

elif "Compliance" in page:
    st.markdown("""
    <div class="professional-header">
        <h1>⚖️ Compliance Dashboard</h1>
        <p>Monitor regulatory compliance across your contract portfolio</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Compliance overview
    col1, col2, col3, col4 = st.columns(4)
    
    compliance_data = [
        ("GDPR", 98.5, "success"),
        ("SOX", 96.2, "success"), 
        ("HIPAA", 89.7, "warning"),
        ("PCI DSS", 94.1, "success")
    ]
    
    for i, (regulation, score, status) in enumerate(compliance_data):
        with [col1, col2, col3, col4][i]:
            status_color = "var(--success-green)" if status == "success" else "var(--warning-orange)"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{regulation}</div>
                <div class="metric-value" style="color: {status_color};">{score}%</div>
                <div style="color: {status_color}; font-size: 0.875rem;">{"✅ Compliant" if status == "success" else "⚠️ Needs Attention"}</div>
            </div>
            """, unsafe_allow_html=True)

elif "Reports" in page:
    st.markdown("""
    <div class="professional-header">
        <h1>📋 Reports & Export</h1>
        <p>Generate comprehensive reports and export contract analysis data</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="content-section">
        <div class="section-title">📄 Available Reports</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Executive Summary Report", use_container_width=True):
            st.success("Executive summary report generated and ready for download")
        
        if st.button("⚖️ Compliance Audit Report", use_container_width=True):
            st.success("Compliance audit report generated and ready for download")
    
    with col2:
        if st.button("🚨 Risk Assessment Report", use_container_width=True):
            st.success("Risk assessment report generated and ready for download")
        
        if st.button("📈 Analytics Dashboard Export", use_container_width=True):
            st.success("Analytics data exported to Excel format")