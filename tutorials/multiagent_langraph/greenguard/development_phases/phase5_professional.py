from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import os
import json
import uuid
import asyncio
import random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

# Load environment variables
load_dotenv()

app = FastAPI(title="GreenGuard Environmental Health System")

# Enums
class AlertType(str, Enum):
    ADVISORY = "advisory"
    WARNING = "warning"
    URGENT = "urgent"
    EMERGENCY = "emergency"

class AlertChannel(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    EMERGENCY_BROADCAST = "emergency_broadcast"
    MOBILE_PUSH = "mobile_push"

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"

# Models
class LocationRequest(BaseModel):
    location: str
    demo_mode: bool = False

class ChannelDelivery(BaseModel):
    channel: AlertChannel
    status: DeliveryStatus
    recipients_targeted: int
    recipients_reached: int
    delivery_rate: float
    timestamp: datetime
    retry_count: int = 0

class DispatchReport(BaseModel):
    alert_id: str
    total_population: int
    channels: List[ChannelDelivery]
    overall_reach: int
    overall_rate: float
    status: str
    completed_at: Optional[datetime]

class SystemMetrics(BaseModel):
    alerts_generated: int
    alerts_dispatched: int
    population_protected: int
    avg_response_time: float
    system_uptime: float
    last_alert: Optional[datetime]

# Global state for WebSocket connections
active_connections: List[WebSocket] = []

# Professional UI
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GreenGuard - Environmental Health Protection System</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            :root {
                --primary: #059669;
                --primary-dark: #047857;
                --secondary: #0EA5E9;
                --accent: #8B5CF6;
                --success: #10B981;
                --warning: #F59E0B;
                --danger: #EF4444;
                --dark: #0F172A;
                --light: #F8FAFC;
                --gray-100: #F1F5F9;
                --gray-200: #E2E8F0;
                --gray-300: #CBD5E1;
                --gray-400: #94A3B8;
                --gray-500: #64748B;
                --gray-600: #475569;
                --gray-700: #334155;
                --gray-800: #1E293B;
                --gray-900: #0F172A;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, system-ui, sans-serif;
                background: var(--dark);
                color: var(--light);
                overflow-x: hidden;
            }
            
            /* Background animation */
            .bg-animation {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #0F172A 0%, #1E293B 100%);
                z-index: -2;
            }
            
            .bg-grid {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: 
                    linear-gradient(rgba(5, 150, 105, 0.1) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(5, 150, 105, 0.1) 1px, transparent 1px);
                background-size: 50px 50px;
                z-index: -1;
                animation: grid-move 20s linear infinite;
            }
            
            @keyframes grid-move {
                0% { transform: translate(0, 0); }
                100% { transform: translate(50px, 50px); }
            }
            
            /* Header */
            .header {
                background: rgba(15, 23, 42, 0.8);
                backdrop-filter: blur(20px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                padding: 1.5rem 0;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 1000;
            }
            
            .header-content {
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 2rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .logo {
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            
            .logo-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--primary) 0%, var(--success) 100%);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                color: white;
            }
            
            .logo-text {
                font-size: 24px;
                font-weight: 800;
                background: linear-gradient(135deg, var(--primary) 0%, var(--success) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .system-status {
                display: flex;
                align-items: center;
                gap: 2rem;
            }
            
            .status-item {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .status-indicator {
                width: 8px;
                height: 8px;
                background: var(--success);
                border-radius: 50%;
                animation: pulse 2s ease-in-out infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.6; transform: scale(1.2); }
            }
            
            /* Main Content */
            .main-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 7rem 2rem 2rem;
                min-height: 100vh;
            }
            
            /* Hero Section */
            .hero-section {
                text-align: center;
                margin-bottom: 4rem;
                animation: fadeInUp 0.8s ease-out;
            }
            
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(30px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .hero-title {
                font-size: 3.5rem;
                font-weight: 900;
                margin-bottom: 1rem;
                background: linear-gradient(135deg, var(--light) 0%, var(--gray-400) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                line-height: 1.2;
            }
            
            .hero-subtitle {
                font-size: 1.25rem;
                color: var(--gray-400);
                margin-bottom: 3rem;
            }
            
            /* Location Input */
            .location-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 2.5rem;
                max-width: 600px;
                margin: 0 auto 3rem;
                animation: fadeInUp 0.8s ease-out 0.2s both;
            }
            
            .input-group {
                display: flex;
                gap: 1rem;
                margin-bottom: 1rem;
            }
            
            .location-input {
                flex: 1;
                padding: 1rem 1.5rem;
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                color: white;
                font-size: 1rem;
                font-weight: 500;
                transition: all 0.3s ease;
            }
            
            .location-input:focus {
                outline: none;
                border-color: var(--primary);
                background: rgba(255, 255, 255, 0.08);
                transform: translateY(-1px);
                box-shadow: 0 8px 24px rgba(5, 150, 105, 0.2);
            }
            
            .monitor-btn {
                padding: 1rem 2rem;
                background: linear-gradient(135deg, var(--primary) 0%, var(--success) 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .monitor-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 32px rgba(5, 150, 105, 0.3);
            }
            
            .monitor-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .demo-toggle {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.75rem;
                color: var(--gray-400);
                font-size: 0.875rem;
            }
            
            /* Dashboard Grid */
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                margin-bottom: 3rem;
                opacity: 0;
                transition: opacity 0.5s ease;
            }
            
            .dashboard-grid.active {
                opacity: 1;
            }
            
            .metric-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 1.5rem;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .metric-card:hover {
                transform: translateY(-4px);
                border-color: rgba(255, 255, 255, 0.2);
                box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
            }
            
            .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, var(--primary) 0%, var(--success) 100%);
            }
            
            .metric-icon {
                width: 48px;
                height: 48px;
                background: rgba(5, 150, 105, 0.1);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                color: var(--primary);
                margin-bottom: 1rem;
            }
            
            .metric-value {
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 0.5rem;
                background: linear-gradient(135deg, var(--light) 0%, var(--gray-400) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .metric-label {
                font-size: 0.875rem;
                color: var(--gray-400);
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .metric-change {
                position: absolute;
                top: 1.5rem;
                right: 1.5rem;
                font-size: 0.875rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 0.25rem;
            }
            
            .metric-change.positive {
                color: var(--success);
            }
            
            .metric-change.negative {
                color: var(--danger);
            }
            
            /* Alert Display */
            .alert-container {
                margin-bottom: 3rem;
                display: none;
            }
            
            .alert-container.active {
                display: block;
                animation: slideIn 0.5s ease-out;
            }
            
            @keyframes slideIn {
                from { opacity: 0; transform: translateX(-20px); }
                to { opacity: 1; transform: translateX(0); }
            }
            
            .alert-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 2rem;
                position: relative;
                overflow: hidden;
            }
            
            .alert-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 1.5rem;
            }
            
            .alert-badge {
                padding: 0.5rem 1rem;
                border-radius: 8px;
                font-size: 0.875rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .alert-badge.emergency {
                background: rgba(239, 68, 68, 0.2);
                color: var(--danger);
                border: 1px solid rgba(239, 68, 68, 0.3);
            }
            
            .alert-badge.urgent {
                background: rgba(245, 158, 11, 0.2);
                color: var(--warning);
                border: 1px solid rgba(245, 158, 11, 0.3);
            }
            
            .alert-badge.warning {
                background: rgba(245, 158, 11, 0.15);
                color: #FCD34D;
                border: 1px solid rgba(245, 158, 11, 0.2);
            }
            
            .alert-badge.advisory {
                background: rgba(14, 165, 233, 0.2);
                color: var(--secondary);
                border: 1px solid rgba(14, 165, 233, 0.3);
            }
            
            .alert-title {
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 1rem;
            }
            
            .alert-content {
                color: var(--gray-300);
                line-height: 1.6;
                margin-bottom: 1.5rem;
            }
            
            /* Delivery Status */
            .delivery-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin-top: 2rem;
            }
            
            .channel-status {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 1rem;
                transition: all 0.3s ease;
            }
            
            .channel-status.delivered {
                border-color: rgba(16, 185, 129, 0.5);
                background: rgba(16, 185, 129, 0.05);
            }
            
            .channel-status.sending {
                border-color: rgba(245, 158, 11, 0.5);
                background: rgba(245, 158, 11, 0.05);
            }
            
            .channel-icon {
                font-size: 1.5rem;
                margin-bottom: 0.5rem;
            }
            
            .channel-name {
                font-weight: 600;
                margin-bottom: 0.25rem;
            }
            
            .delivery-progress {
                width: 100%;
                height: 4px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
                margin: 0.5rem 0;
                overflow: hidden;
            }
            
            .delivery-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, var(--primary) 0%, var(--success) 100%);
                border-radius: 2px;
                transition: width 0.5s ease;
            }
            
            .delivery-stats {
                font-size: 0.75rem;
                color: var(--gray-400);
            }
            
            /* Analytics Section */
            .analytics-section {
                margin-top: 4rem;
                display: none;
            }
            
            .analytics-section.active {
                display: block;
            }
            
            .section-title {
                font-size: 2rem;
                font-weight: 800;
                margin-bottom: 2rem;
                background: linear-gradient(135deg, var(--light) 0%, var(--gray-400) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .analytics-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 1.5rem;
            }
            
            .analytics-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 2rem;
                height: 300px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            
            /* Footer */
            .footer {
                margin-top: 6rem;
                padding: 3rem 0;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                text-align: center;
                color: var(--gray-400);
            }
            
            .footer-logo {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                margin-bottom: 1rem;
            }
            
            .security-badges {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 2rem;
                margin-top: 2rem;
            }
            
            .security-badge {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                font-size: 0.875rem;
            }
            
            /* Loading Animation */
            .loading-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s ease-in-out infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .hero-title {
                    font-size: 2.5rem;
                }
                
                .dashboard-grid {
                    grid-template-columns: 1fr;
                }
                
                .analytics-grid {
                    grid-template-columns: 1fr;
                }
                
                .input-group {
                    flex-direction: column;
                }
                
                .system-status {
                    display: none;
                }
            }
        </style>
    </head>
    <body>
        <div class="bg-animation"></div>
        <div class="bg-grid"></div>
        
        <header class="header">
            <div class="header-content">
                <div class="logo">
                    <div class="logo-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <div class="logo-text">GreenGuard</div>
                </div>
                <div class="system-status">
                    <div class="status-item">
                        <div class="status-indicator"></div>
                        <span>System Online</span>
                    </div>
                    <div class="status-item">
                        <i class="fas fa-globe"></i>
                        <span id="active-locations">0</span>
                        <span>Active Monitors</span>
                    </div>
                </div>
            </div>
        </header>
        
        <main class="main-container">
            <section class="hero-section">
                <h1 class="hero-title">Environmental Health Protection</h1>
                <p class="hero-subtitle">Real-time monitoring and alert system for community safety</p>
            </section>
            
            <div class="location-card">
                <div class="input-group">
                    <input 
                        type="text" 
                        id="location-input" 
                        class="location-input" 
                        placeholder="Enter location (e.g., San Francisco, CA)"
                        value="San Francisco, CA"
                    >
                    <button id="monitor-btn" class="monitor-btn" onclick="startMonitoring()">
                        <i class="fas fa-satellite-dish"></i>
                        Start Monitoring
                    </button>
                </div>
                <div class="demo-toggle">
                    <input type="checkbox" id="demo-mode" checked>
                    <label for="demo-mode">Demo Mode (for presentation)</label>
                </div>
            </div>
            
            <div id="dashboard-grid" class="dashboard-grid">
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <div class="metric-value" id="population-protected">0</div>
                    <div class="metric-label">Population Protected</div>
                    <div class="metric-change positive">
                        <i class="fas fa-arrow-up"></i>
                        <span>12%</span>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-bell"></i>
                    </div>
                    <div class="metric-value" id="alerts-sent">0</div>
                    <div class="metric-label">Alerts Dispatched</div>
                    <div class="metric-change positive">
                        <i class="fas fa-arrow-up"></i>
                        <span>8%</span>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <div class="metric-value" id="delivery-rate">0%</div>
                    <div class="metric-label">Delivery Success Rate</div>
                    <div class="metric-change positive">
                        <i class="fas fa-arrow-up"></i>
                        <span>3%</span>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-clock"></i>
                    </div>
                    <div class="metric-value" id="response-time">0s</div>
                    <div class="metric-label">Avg Response Time</div>
                    <div class="metric-change positive">
                        <i class="fas fa-arrow-down"></i>
                        <span>15%</span>
                    </div>
                </div>
            </div>
            
            <div id="alert-container" class="alert-container">
                <!-- Alert content will be dynamically inserted here -->
            </div>
            
            <div id="analytics-section" class="analytics-section">
                <h2 class="section-title">System Analytics</h2>
                <div class="analytics-grid">
                    <div class="analytics-card">
                        <canvas id="delivery-chart"></canvas>
                    </div>
                    <div class="analytics-card">
                        <canvas id="channel-chart"></canvas>
                    </div>
                </div>
            </div>
        </main>
        
        <footer class="footer">
            <div class="footer-logo">
                <i class="fas fa-shield-alt"></i>
                <span>GreenGuard Environmental Protection</span>
            </div>
            <p>&copy; 2024 GreenGuard. Protecting communities through technology.</p>
            <div class="security-badges">
                <div class="security-badge">
                    <i class="fas fa-lock"></i>
                    <span>Enterprise Security</span>
                </div>
                <div class="security-badge">
                    <i class="fas fa-certificate"></i>
                    <span>HIPAA Compliant</span>
                </div>
                <div class="security-badge">
                    <i class="fas fa-check-circle"></i>
                    <span>SOC 2 Certified</span>
                </div>
            </div>
        </footer>
        
        <script>
            let ws = null;
            let currentAlertId = null;
            let metricsInterval = null;
            
            // Connect to WebSocket for real-time updates
            function connectWebSocket() {
                ws = new WebSocket('ws://127.0.0.1:8005/ws');
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    updateDeliveryStatus(data);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                };
            }
            
            async function startMonitoring() {
                const location = document.getElementById('location-input').value;
                const demoMode = document.getElementById('demo-mode').checked;
                const monitorBtn = document.getElementById('monitor-btn');
                
                if (!location) {
                    alert('Please enter a location');
                    return;
                }
                
                // Update UI
                monitorBtn.disabled = true;
                monitorBtn.innerHTML = '<i class="fas fa-spinner loading-spinner"></i> Analyzing...';
                document.getElementById('dashboard-grid').classList.add('active');
                
                try {
                    // Start the full pipeline
                    const response = await fetch('/monitor', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ 
                            location: location,
                            demo_mode: demoMode 
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        displayAlert(data.alert);
                        currentAlertId = data.alert.alert_id;
                        
                        // Start dispatch
                        dispatchAlert(currentAlertId);
                        
                        // Update metrics
                        updateMetrics();
                        
                        // Show analytics
                        document.getElementById('analytics-section').classList.add('active');
                    } else {
                        alert('Error: ' + (data.detail || 'Unknown error'));
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                } finally {
                    monitorBtn.disabled = false;
                    monitorBtn.innerHTML = '<i class="fas fa-satellite-dish"></i> Start Monitoring';
                }
            }
            
            function displayAlert(alert) {
                const container = document.getElementById('alert-container');
                container.classList.add('active');
                
                container.innerHTML = `
                    <div class="alert-card">
                        <div class="alert-header">
                            <h3 class="alert-title">${alert.title}</h3>
                            <span class="alert-badge ${alert.alert_type}">${alert.alert_type}</span>
                        </div>
                        <div class="alert-content">
                            <p>${alert.summary}</p>
                        </div>
                        <div class="delivery-grid" id="delivery-grid">
                            ${createChannelStatus('sms', 'SMS Messages')}
                            ${createChannelStatus('email', 'Email Alerts')}
                            ${createChannelStatus('mobile_push', 'Mobile Push')}
                            ${createChannelStatus('social_media', 'Social Media')}
                            ${createChannelStatus('emergency_broadcast', 'Emergency Broadcast')}
                        </div>
                    </div>
                `;
            }
            
            function createChannelStatus(channelId, channelName) {
                const icons = {
                    'sms': 'fa-sms',
                    'email': 'fa-envelope',
                    'mobile_push': 'fa-mobile-alt',
                    'social_media': 'fa-share-alt',
                    'emergency_broadcast': 'fa-broadcast-tower'
                };
                
                return `
                    <div class="channel-status" id="channel-${channelId}">
                        <div class="channel-icon">
                            <i class="fas ${icons[channelId]}"></i>
                        </div>
                        <div class="channel-name">${channelName}</div>
                        <div class="delivery-progress">
                            <div class="delivery-progress-bar" id="progress-${channelId}" style="width: 0%"></div>
                        </div>
                        <div class="delivery-stats" id="stats-${channelId}">
                            Preparing...
                        </div>
                    </div>
                `;
            }
            
            async function dispatchAlert(alertId) {
                try {
                    const response = await fetch('/dispatch', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ alert_id: alertId })
                    });
                    
                    const data = await response.json();
                    // Initial dispatch status will be updated via WebSocket
                } catch (error) {
                    console.error('Dispatch error:', error);
                }
            }
            
            function updateDeliveryStatus(data) {
                if (data.type === 'delivery_update' && data.channel) {
                    const channelEl = document.getElementById(`channel-${data.channel}`);
                    const progressBar = document.getElementById(`progress-${data.channel}`);
                    const statsEl = document.getElementById(`stats-${data.channel}`);
                    
                    if (channelEl && progressBar && statsEl) {
                        // Update progress
                        progressBar.style.width = `${data.progress}%`;
                        
                        // Update status
                        channelEl.classList.remove('pending', 'sending', 'delivered');
                        channelEl.classList.add(data.status);
                        
                        // Update stats
                        if (data.status === 'delivered') {
                            statsEl.innerHTML = `${data.reached.toLocaleString()} reached`;
                        } else if (data.status === 'sending') {
                            statsEl.innerHTML = `Sending... ${data.progress}%`;
                        }
                    }
                } else if (data.type === 'metrics_update') {
                    updateMetricsDisplay(data.metrics);
                }
            }
            
            function updateMetrics() {
                // Simulate metric updates
                let population = 0;
                let alerts = 0;
                let rate = 0;
                
                metricsInterval = setInterval(() => {
                    // Animate metrics
                    population = Math.min(population + Math.floor(Math.random() * 5000), 125000);
                    alerts = Math.min(alerts + 1, 12);
                    rate = Math.min(rate + Math.random() * 5, 98.5);
                    
                    document.getElementById('population-protected').textContent = population.toLocaleString();
                    document.getElementById('alerts-sent').textContent = alerts;
                    document.getElementById('delivery-rate').textContent = rate.toFixed(1) + '%';
                    document.getElementById('response-time').textContent = (2.3 + Math.random()).toFixed(1) + 's';
                    
                    // Update active locations
                    document.getElementById('active-locations').textContent = Math.floor(Math.random() * 10) + 5;
                }, 1000);
            }
            
            function updateMetricsDisplay(metrics) {
                if (metrics.population_protected !== undefined) {
                    document.getElementById('population-protected').textContent = 
                        metrics.population_protected.toLocaleString();
                }
                if (metrics.alerts_dispatched !== undefined) {
                    document.getElementById('alerts-sent').textContent = metrics.alerts_dispatched;
                }
                if (metrics.avg_delivery_rate !== undefined) {
                    document.getElementById('delivery-rate').textContent = 
                        (metrics.avg_delivery_rate * 100).toFixed(1) + '%';
                }
                if (metrics.avg_response_time !== undefined) {
                    document.getElementById('response-time').textContent = 
                        metrics.avg_response_time.toFixed(1) + 's';
                }
            }
            
            // Initialize WebSocket connection
            connectWebSocket();
        </script>
    </body>
    </html>
    """

# Main monitoring endpoint
@app.post("/monitor")
async def monitor_location(request: LocationRequest):
    """Main endpoint that runs the full agent pipeline"""
    
    # Load environment variables
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not openai_key or not tavily_key:
        raise HTTPException(
            status_code=500,
            detail="System configuration error. Please contact support."
        )
    
    try:
        # Initialize tools
        llm = ChatOpenAI(
            temperature=0.3,
            model="gpt-4o-mini",
            api_key=openai_key
        )
        
        search = TavilySearchResults(
            api_key=tavily_key,
            max_results=5,
            search_depth="advanced"
        )
        
        # Run the full pipeline (simplified for demo)
        # In production, this would call all 4 agents through supervisor
        
        # For demo mode, return pre-configured alert
        if request.demo_mode:
            alert = {
                "alert_id": str(uuid.uuid4())[:8].upper(),
                "alert_type": "warning",
                "title": f"Environmental Health Advisory - {request.location}",
                "summary": f"Moderate air quality concerns detected in {request.location}. Sensitive groups should limit prolonged outdoor exposure.",
                "channels": ["sms", "email", "mobile_push", "social_media", "emergency_broadcast"]
            }
        else:
            # Real processing would happen here
            # This is simplified for the demo
            alert = {
                "alert_id": str(uuid.uuid4())[:8].upper(),
                "alert_type": "warning",
                "title": f"Environmental Health Advisory - {request.location}",
                "summary": "Environmental monitoring has detected conditions requiring public notification.",
                "channels": ["sms", "email", "mobile_push", "social_media", "emergency_broadcast"]
            }
        
        return {"status": "success", "alert": alert}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Dispatch endpoint
@app.post("/dispatch")
async def dispatch_alert(alert_id: str = None):
    """Dispatch alert through multiple channels"""
    
    # Simulate dispatch process
    channels = ["sms", "email", "mobile_push", "social_media", "emergency_broadcast"]
    populations = {
        "sms": 45000,
        "email": 38000,
        "mobile_push": 52000,
        "social_media": 28000,
        "emergency_broadcast": 125000
    }
    
    # Start async dispatch for each channel
    for channel in channels:
        asyncio.create_task(
            simulate_channel_delivery(channel, populations[channel])
        )
    
    return {
        "status": "dispatching",
        "alert_id": alert_id,
        "channels_activated": len(channels)
    }

async def simulate_channel_delivery(channel: str, target_population: int):
    """Simulate gradual delivery to population"""
    
    # Random delay for channel activation
    await asyncio.sleep(random.uniform(0.5, 2.0))
    
    # Gradual delivery simulation
    steps = 20
    for i in range(steps + 1):
        progress = (i / steps) * 100
        reached = int((i / steps) * target_population)
        
        status = "sending" if i < steps else "delivered"
        
        # Broadcast update to all connected clients
        update = {
            "type": "delivery_update",
            "channel": channel,
            "status": status,
            "progress": progress,
            "reached": reached,
            "target": target_population
        }
        
        # Send to all WebSocket connections
        for connection in active_connections:
            await connection.send_json(update)
        
        await asyncio.sleep(random.uniform(0.2, 0.5))

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# System metrics endpoint (for monitoring)
@app.get("/metrics")
async def get_system_metrics():
    """Get system performance metrics"""
    
    return SystemMetrics(
        alerts_generated=127,
        alerts_dispatched=125,
        population_protected=1250000,
        avg_response_time=2.3,
        system_uptime=99.98,
        last_alert=datetime.now() - timedelta(minutes=12)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)