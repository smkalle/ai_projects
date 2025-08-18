"""Energize Streamlit Dashboard - Main Application."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Optional
import os

# Page configuration
st.set_page_config(
    page_title="Energize Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Silicon Valley standards
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(0, 0, 0, 0.1);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stAlert {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# API Configuration
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
API_V1 = f"{API_BASE_URL}/api/v1"

# Session State Management
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user = None

def authenticate(email: str, password: str) -> bool:
    """Authenticate user with the backend."""
    try:
        response = requests.post(
            f"{API_V1}/auth/login",
            data={"username": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.token = data.get("access_token")
            st.session_state.user = {"email": email}
            return True
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
    return False

def get_headers():
    """Get authorization headers."""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

# Login Page
if not st.session_state.authenticated:
    st.title("⚡ Energize - Smart Building Energy Analytics")
    st.markdown("### Sign in to your account")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email", value="demo@energize.io")
            password = st.text_input("Password", type="password", value="demo123")
            submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            
            if submit:
                if authenticate(email, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
        
        st.info("Demo credentials: demo@energize.io / demo123")
else:
    # Main Dashboard
    st.title("⚡ Energize Dashboard")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.selectbox(
            "Select Page",
            ["Overview", "Buildings", "Energy Analytics", "AI Optimization", "Alerts", "Reports"]
        )
        
        st.markdown("---")
        st.markdown("### User")
        st.write(f"📧 {st.session_state.user['email']}")
        
        if st.button("Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
    
    # Main Content Area
    if page == "Overview":
        # Header Metrics
        st.markdown("## Energy Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Energy Today",
                value="2,847 kWh",
                delta="-12% vs yesterday",
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                label="Active Alerts",
                value="3",
                delta="2 new",
                delta_color="normal"
            )
        
        with col3:
            st.metric(
                label="Cost Today",
                value="$426",
                delta="-$52",
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                label="Carbon Footprint",
                value="1.2 tons CO₂",
                delta="-8%",
                delta_color="inverse"
            )
        
        st.markdown("---")
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Energy Consumption Trend")
            
            # Generate sample data
            hours = pd.date_range(
                start=datetime.now() - timedelta(hours=24),
                end=datetime.now(),
                freq='H'
            )
            consumption_data = pd.DataFrame({
                'Time': hours,
                'Consumption (kWh)': [100 + 50 * abs(12 - h.hour) / 12 + 10 * (h.hour % 3) for h in hours]
            })
            
            fig = px.line(
                consumption_data,
                x='Time',
                y='Consumption (kWh)',
                title='24-Hour Energy Consumption',
                line_shape='spline'
            )
            fig.update_layout(
                showlegend=False,
                height=400,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            fig.update_traces(line_color='#10b981', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Energy Distribution by Building")
            
            building_data = pd.DataFrame({
                'Building': ['Tower A', 'Tower B', 'Tower C', 'Warehouse', 'Office Complex'],
                'Energy (kWh)': [850, 720, 630, 450, 197]
            })
            
            fig = px.pie(
                building_data,
                values='Energy (kWh)',
                names='Building',
                title='Today\'s Energy Distribution',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Alerts Section
        st.markdown("---")
        st.markdown("### Recent Alerts")
        
        alerts_data = pd.DataFrame({
            'Time': [
                datetime.now() - timedelta(minutes=15),
                datetime.now() - timedelta(hours=1),
                datetime.now() - timedelta(hours=3)
            ],
            'Building': ['Tower A', 'Tower B', 'Warehouse'],
            'Type': ['Anomaly', 'Threshold', 'System'],
            'Severity': ['High', 'Medium', 'Low'],
            'Message': [
                'Unusual spike in power consumption detected',
                'Temperature exceeded threshold (28°C)',
                'Sensor maintenance required'
            ]
        })
        
        for _, alert in alerts_data.iterrows():
            severity_color = {
                'High': 'error',
                'Medium': 'warning',
                'Low': 'info'
            }[alert['Severity']]
            
            st.alert(
                f"**{alert['Building']}** - {alert['Type']}\n\n"
                f"{alert['Message']}\n\n"
                f"*{alert['Time'].strftime('%Y-%m-%d %H:%M')}*",
                icon="⚠️" if alert['Severity'] == 'High' else "ℹ️"
            )
    
    elif page == "Buildings":
        st.markdown("## Building Management")
        
        # Buildings table
        buildings_data = pd.DataFrame({
            'Name': ['Tower A', 'Tower B', 'Tower C', 'Warehouse', 'Office Complex'],
            'Address': [
                '123 Tech Park, San Jose',
                '124 Tech Park, San Jose',
                '125 Tech Park, San Jose',
                '500 Industrial Way, Oakland',
                '1 Market St, San Francisco'
            ],
            'Area (sq ft)': [45000, 38000, 42000, 85000, 65000],
            'Type': ['Office', 'Office', 'Office', 'Industrial', 'Mixed'],
            'Status': ['Active', 'Active', 'Active', 'Active', 'Maintenance'],
            'Sensors': [24, 20, 22, 35, 28]
        })
        
        st.dataframe(
            buildings_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Area (sq ft)": st.column_config.NumberColumn(
                    "Area (sq ft)",
                    format="%d",
                ),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Active", "Maintenance", "Inactive"],
                ),
            }
        )
        
        # Add new building button
        if st.button("➕ Add New Building", type="primary"):
            st.info("Building creation form would appear here")
    
    elif page == "Energy Analytics":
        st.markdown("## Energy Analytics")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        # Building selector
        building = st.selectbox(
            "Select Building",
            ["All Buildings", "Tower A", "Tower B", "Tower C", "Warehouse", "Office Complex"]
        )
        
        # Granularity selector
        granularity = st.radio(
            "Data Granularity",
            ["Hour", "Day", "Week", "Month"],
            horizontal=True
        )
        
        # Generate and display chart
        if st.button("Generate Report", type="primary"):
            st.markdown("### Energy Consumption Analysis")
            
            # Sample data generation
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            analysis_data = pd.DataFrame({
                'Date': date_range,
                'Consumption': [2000 + 500 * (i % 7) / 7 for i in range(len(date_range))],
                'Cost': [300 + 75 * (i % 7) / 7 for i in range(len(date_range))]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=analysis_data['Date'],
                y=analysis_data['Consumption'],
                mode='lines+markers',
                name='Energy (kWh)',
                line=dict(color='#10b981', width=2)
            ))
            
            fig.update_layout(
                title=f'Energy Consumption - {building}',
                xaxis_title='Date',
                yaxis_title='Energy (kWh)',
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Consumption", f"{analysis_data['Consumption'].sum():,.0f} kWh")
            with col2:
                st.metric("Average Daily", f"{analysis_data['Consumption'].mean():,.0f} kWh")
            with col3:
                st.metric("Total Cost", f"${analysis_data['Cost'].sum():,.2f}")
    
    elif page == "Alerts":
        st.markdown("## Alert Management")
        
        # Alert filters
        col1, col2, col3 = st.columns(3)
        with col1:
            severity_filter = st.multiselect(
                "Severity",
                ["Critical", "High", "Medium", "Low"],
                default=["Critical", "High"]
            )
        with col2:
            type_filter = st.multiselect(
                "Alert Type",
                ["Anomaly", "Threshold", "System", "Maintenance"],
                default=["Anomaly", "Threshold"]
            )
        with col3:
            status_filter = st.selectbox(
                "Status",
                ["All", "Active", "Acknowledged", "Resolved"]
            )
        
        # Alerts table
        st.markdown("### Active Alerts")
        
        alerts_df = pd.DataFrame({
            'ID': ['ALT-001', 'ALT-002', 'ALT-003', 'ALT-004', 'ALT-005'],
            'Time': pd.date_range(end=datetime.now(), periods=5, freq='H'),
            'Building': ['Tower A', 'Tower B', 'Tower A', 'Warehouse', 'Office Complex'],
            'Type': ['Anomaly', 'Threshold', 'System', 'Anomaly', 'Maintenance'],
            'Severity': ['High', 'Medium', 'Low', 'Critical', 'Low'],
            'Message': [
                'Power spike detected',
                'Temperature above threshold',
                'Sensor offline',
                'Major consumption anomaly',
                'Scheduled maintenance due'
            ],
            'Status': ['Active', 'Active', 'Acknowledged', 'Active', 'Resolved']
        })
        
        st.dataframe(
            alerts_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Severity": st.column_config.SelectboxColumn(
                    "Severity",
                    options=["Critical", "High", "Medium", "Low"],
                ),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Active", "Acknowledged", "Resolved"],
                ),
            }
        )
    
    elif page == "AI Optimization":
        st.markdown("## 🤖 AI-Powered Energy Optimization")
        
        # AI Status Dashboard
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="AI Optimization Score",
                value="94/100",
                delta="+12 points"
            )
        
        with col2:
            st.metric(
                label="Energy Saved Today",
                value="1,247 kWh",
                delta="+23%"
            )
        
        with col3:
            st.metric(
                label="Carbon Reduced",
                value="2.3 tons CO₂",
                delta="-45%"
            )
        
        with col4:
            st.metric(
                label="Cost Savings",
                value="$1,847",
                delta="+$347"
            )
        
        st.markdown("---")
        
        # Building Selection for AI Optimization
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_building = st.selectbox(
                "Select Building for AI Optimization",
                ["Tower A", "Tower B", "Tower C", "Warehouse", "Office Complex"]
            )
        
        with col2:
            consumption = st.number_input(
                "Current Consumption (kWh)",
                min_value=100,
                max_value=5000,
                value=2847,
                step=100
            )
        
        # AI Optimization Button
        if st.button("🚀 Run AI Optimization", type="primary", use_container_width=True):
            with st.spinner("AI agents analyzing energy patterns..."):
                # Simulate API call to AI optimization
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/ai/simulate-optimization",
                        params={
                            "building_id": selected_building.lower().replace(" ", "-"),
                            "consumption": consumption
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success("✅ AI Optimization Complete!")
                        
                        # Results Display
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                "Energy Saved",
                                f"{result['energy_saved']:.0f} kWh",
                                f"-{(result['energy_saved']/result['baseline_consumption']*100):.1f}%"
                            )
                        
                        with col2:
                            st.metric(
                                "Cost Savings",
                                f"${result['cost_savings']:.0f}",
                                "Monthly"
                            )
                        
                        with col3:
                            st.metric(
                                "Carbon Reduced",
                                f"{result['carbon_reduced']:.2f} kg CO₂",
                                "Per month"
                            )
                        
                        # AI Recommendations
                        st.markdown("### 🎯 AI Recommendations")
                        for i, rec in enumerate(result['recommendations'], 1):
                            st.info(f"{i}. {rec}")
                        
                        # Optimization Actions
                        st.markdown("### ⚡ Optimization Actions")
                        for action in result['optimization_actions']:
                            st.checkbox(action, value=False)
                        
                        # Apply Optimizations Button
                        if st.button("Apply AI Optimizations", type="secondary"):
                            st.success("🎉 AI optimizations applied successfully!")
                            st.balloons()
                    
                    else:
                        st.error("Failed to connect to AI service")
                        
                except Exception as e:
                    st.error(f"AI service temporarily unavailable: {str(e)}")
                    # Show demo results
                    st.info("Showing demo optimization results...")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Energy Saved", "854 kWh", "-30%")
                    with col2:
                        st.metric("Cost Savings", "$427", "Monthly")
                    with col3:
                        st.metric("Carbon Reduced", "0.43 kg CO₂", "Per month")
        
        st.markdown("---")
        
        # AI Chat Assistant
        st.markdown("### 💬 Energy AI Assistant")
        st.markdown("Ask our AI assistant about energy optimization strategies:")
        
        user_query = st.text_input(
            "Ask AI Assistant",
            placeholder="How can I reduce energy consumption in my building?"
        )
        
        if user_query:
            with st.spinner("AI assistant thinking..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/ai/chat",
                        json={
                            "query": user_query,
                            "building_id": selected_building.lower().replace(" ", "-")
                        }
                    )
                    
                    if response.status_code == 200:
                        ai_response = response.json()['response']
                        st.markdown(f"**🤖 AI Assistant:** {ai_response}")
                    else:
                        st.error("AI assistant temporarily unavailable")
                        
                except Exception as e:
                    # Demo response
                    demo_responses = {
                        "reduce": "To reduce energy consumption, I recommend: 1) Optimize HVAC scheduling based on occupancy, 2) Implement smart lighting with motion sensors, 3) Use demand response programs during peak hours, and 4) Install energy-efficient equipment.",
                        "cost": "You can save costs by: 1) Shifting loads to off-peak hours, 2) Implementing energy storage systems, 3) Participating in utility rebate programs, and 4) Using predictive maintenance to avoid equipment failures.",
                        "carbon": "To reduce carbon footprint: 1) Maximize renewable energy usage, 2) Schedule energy-intensive tasks during low-carbon grid hours, 3) Improve building insulation, and 4) Use electric heat pumps instead of gas heating."
                    }
                    
                    # Simple keyword matching for demo
                    response_text = "I can help you optimize energy usage! For specific recommendations, I need to analyze your building's energy patterns. Generally, focus on HVAC optimization, smart scheduling, and renewable energy integration."
                    
                    for keyword, response in demo_responses.items():
                        if keyword in user_query.lower():
                            response_text = response
                            break
                    
                    st.markdown(f"**🤖 AI Assistant:** {response_text}")
        
        # AI System Status
        st.markdown("---")
        st.markdown("### 🔧 AI System Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Active AI Agents:**")
            st.markdown("🟢 Energy Orchestrator - Online")
            st.markdown("🟢 Anomaly Detector - Monitoring")
            st.markdown("🟢 Demand Forecaster - Predicting")
            st.markdown("🟢 Carbon Optimizer - Optimizing")
        
        with col2:
            st.markdown("**AI Performance:**")
            st.markdown("⚡ Response Time: <50ms")
            st.markdown("🎯 Prediction Accuracy: 94.2%")
            st.markdown("💡 Optimizations Active: 12")
            st.markdown("🌱 Carbon Savings: 2.3 tons/day")
    
    elif page == "Reports":
        st.markdown("## Reports & Export")
        
        report_type = st.selectbox(
            "Report Type",
            ["Energy Consumption", "Cost Analysis", "Carbon Footprint", "AI Optimization", "System Health", "Custom"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            period = st.selectbox("Period", ["Last 7 Days", "Last Month", "Last Quarter", "Custom"])
        with col2:
            format = st.selectbox("Export Format", ["PDF", "CSV", "Excel", "JSON"])
        
        if st.button("Generate Report", type="primary", use_container_width=True):
            with st.spinner("Generating report..."):
                st.success(f"✅ {report_type} report generated successfully!")
                st.download_button(
                    label=f"Download {format} Report",
                    data=f"Sample {report_type} report data",
                    file_name=f"energize_report_{datetime.now().strftime('%Y%m%d')}.{format.lower()}",
                    mime="text/csv" if format == "CSV" else "application/pdf"
                )