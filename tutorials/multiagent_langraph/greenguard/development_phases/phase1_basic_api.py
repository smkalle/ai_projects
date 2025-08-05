from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="GreenGuard Phase 1 - Basic API")

class LocationRequest(BaseModel):
    location: str

class HealthCheckResponse(BaseModel):
    status: str
    message: str
    api_keys_configured: dict

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GreenGuard - Phase 1 Testing</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2e7d32;
                text-align: center;
            }
            .test-section {
                margin: 20px 0;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #45a049;
            }
            .result {
                margin-top: 20px;
                padding: 15px;
                background-color: #f0f0f0;
                border-radius: 5px;
                white-space: pre-wrap;
                font-family: monospace;
            }
            .error {
                background-color: #ffebee;
                color: #c62828;
            }
            .success {
                background-color: #e8f5e9;
                color: #2e7d32;
            }
            input[type="text"] {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                box-sizing: border-box;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌿 GreenGuard Environmental Health System</h1>
            <h2>Phase 1: Basic API Testing</h2>
            
            <div class="test-section">
                <h3>1. Health Check</h3>
                <p>Test basic API connectivity and configuration</p>
                <button onclick="testHealthCheck()">Test Health Check</button>
                <div id="health-result" class="result" style="display:none;"></div>
            </div>
            
            <div class="test-section">
                <h3>2. Location Input Test</h3>
                <p>Test basic location input handling</p>
                <input type="text" id="location-input" placeholder="Enter location (e.g., San Francisco, CA)" value="San Francisco, CA">
                <button onclick="testLocationInput()">Test Location Input</button>
                <div id="location-result" class="result" style="display:none;"></div>
            </div>
        </div>
        
        <script>
            async function testHealthCheck() {
                const resultDiv = document.getElementById('health-result');
                resultDiv.style.display = 'block';
                resultDiv.className = 'result';
                resultDiv.textContent = 'Testing...';
                
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    resultDiv.className = 'result success';
                    resultDiv.textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.textContent = 'Error: ' + error.message;
                }
            }
            
            async function testLocationInput() {
                const resultDiv = document.getElementById('location-result');
                const location = document.getElementById('location-input').value;
                
                resultDiv.style.display = 'block';
                resultDiv.className = 'result';
                resultDiv.textContent = 'Processing...';
                
                try {
                    const response = await fetch('/test-location', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ location: location })
                    });
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.className = 'result success';
                    } else {
                        resultDiv.className = 'result error';
                    }
                    resultDiv.textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.textContent = 'Error: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    tavily_configured = bool(os.getenv("TAVILY_API_KEY"))
    
    return HealthCheckResponse(
        status="healthy",
        message="API is running - Phase 1",
        api_keys_configured={
            "openai": openai_configured,
            "tavily": tavily_configured
        }
    )

@app.post("/test-location")
async def test_location(request: LocationRequest):
    if not request.location:
        raise HTTPException(status_code=400, detail="Location is required")
    
    return {
        "status": "success",
        "location_received": request.location,
        "message": f"Successfully received location: {request.location}",
        "next_phase": "DataScout agent will search for environmental data here"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)