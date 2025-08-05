from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
import json

load_dotenv()

app = FastAPI(title="GreenGuard Phase 2 - DataScout Agent")

class LocationRequest(BaseModel):
    location: str

class DataScoutResponse(BaseModel):
    status: str
    location: str
    search_results: List[Dict[str, Any]]
    agent_analysis: str
    raw_search_data: List[Dict[str, Any]]

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GreenGuard - Phase 2: DataScout Agent</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
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
            button:disabled {
                background-color: #cccccc;
                cursor: not-allowed;
            }
            .result {
                margin-top: 20px;
                padding: 15px;
                background-color: #f0f0f0;
                border-radius: 5px;
                font-family: monospace;
                max-height: 600px;
                overflow-y: auto;
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
            .search-result {
                background-color: #f9f9f9;
                padding: 10px;
                margin: 10px 0;
                border-left: 3px solid #4CAF50;
                border-radius: 3px;
            }
            .agent-analysis {
                background-color: #e3f2fd;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
            }
            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #4CAF50;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-left: 10px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌿 GreenGuard Environmental Health System</h1>
            <h2>Phase 2: DataScout Agent Testing</h2>
            
            <div class="test-section">
                <h3>1. API Keys Test</h3>
                <p>Test if OpenAI and Tavily APIs are working</p>
                <button onclick="testAPIs()">Test API Keys</button>
                <div id="api-result" class="result" style="display:none;"></div>
            </div>
            
            <div class="test-section">
                <h3>2. DataScout Agent Test</h3>
                <p>Search for environmental hazard data using DataScout</p>
                <input type="text" id="location-input" placeholder="Enter location (e.g., San Francisco, CA)" value="San Francisco, CA">
                <button id="search-btn" onclick="searchEnvironmentalData()">Search Environmental Data</button>
                <div id="search-result" class="result" style="display:none;"></div>
            </div>
        </div>
        
        <script>
            async function testAPIs() {
                const resultDiv = document.getElementById('api-result');
                resultDiv.style.display = 'block';
                resultDiv.className = 'result';
                resultDiv.innerHTML = 'Testing API keys...<div class="loading"></div>';
                
                try {
                    const response = await fetch('/test-apis');
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <h4>✅ API Keys Test Results:</h4>
                            <pre>${JSON.stringify(data, null, 2)}</pre>
                        `;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `<h4>❌ Error:</h4><pre>${JSON.stringify(data, null, 2)}</pre>`;
                    }
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = '❌ Error: ' + error.message;
                }
            }
            
            async function searchEnvironmentalData() {
                const resultDiv = document.getElementById('search-result');
                const location = document.getElementById('location-input').value;
                const searchBtn = document.getElementById('search-btn');
                
                if (!location) {
                    alert('Please enter a location');
                    return;
                }
                
                resultDiv.style.display = 'block';
                resultDiv.className = 'result';
                resultDiv.innerHTML = 'DataScout is searching for environmental hazard data...<div class="loading"></div>';
                searchBtn.disabled = true;
                
                try {
                    const response = await fetch('/datascout-search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ location: location })
                    });
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.className = 'result success';
                        let html = `<h4>✅ DataScout Results for ${data.location}:</h4>`;
                        
                        // Show agent analysis
                        html += '<div class="agent-analysis">';
                        html += '<h5>🤖 Agent Analysis:</h5>';
                        html += '<p>' + data.agent_analysis.replace(/\\n/g, '<br>') + '</p>';
                        html += '</div>';
                        
                        // Show search results
                        html += '<h5>📊 Search Results:</h5>';
                        data.search_results.forEach((result, index) => {
                            html += `<div class="search-result">
                                <strong>${index + 1}. ${result.title}</strong><br>
                                <small>Source: ${result.url}</small><br>
                                <p>${result.content}</p>
                            </div>`;
                        });
                        
                        // Show raw data in collapsible
                        html += '<details><summary>View Raw Search Data</summary>';
                        html += '<pre>' + JSON.stringify(data.raw_search_data, null, 2) + '</pre>';
                        html += '</details>';
                        
                        resultDiv.innerHTML = html;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `<h4>❌ Error:</h4><pre>${JSON.stringify(data, null, 2)}</pre>`;
                    }
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = '❌ Error: ' + error.message;
                } finally {
                    searchBtn.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/test-apis")
async def test_apis():
    results = {
        "openai": {"configured": False, "working": False, "error": None},
        "tavily": {"configured": False, "working": False, "error": None}
    }
    
    # Test OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    results["openai"]["configured"] = bool(openai_key)
    
    if openai_key:
        try:
            llm = ChatOpenAI(
                temperature=0,
                model="gpt-4o-mini",
                api_key=openai_key
            )
            response = llm.invoke("Say 'API working' in 3 words")
            results["openai"]["working"] = True
            results["openai"]["response"] = response.content
        except Exception as e:
            results["openai"]["error"] = str(e)
    
    # Test Tavily
    tavily_key = os.getenv("TAVILY_API_KEY")
    results["tavily"]["configured"] = bool(tavily_key)
    
    if tavily_key:
        try:
            search = TavilySearchResults(api_key=tavily_key, max_results=1)
            search_results = search.invoke("test query environmental health")
            results["tavily"]["working"] = True
            results["tavily"]["sample_result"] = "Search successful - found results"
        except Exception as e:
            results["tavily"]["error"] = str(e)
    
    return results

@app.post("/datascout-search")
async def datascout_search(request: LocationRequest):
    # Validate API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not openai_key or not tavily_key:
        raise HTTPException(
            status_code=500,
            detail="Missing API keys. Please configure OPENAI_API_KEY and TAVILY_API_KEY"
        )
    
    try:
        # Initialize tools
        llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini",
            api_key=openai_key
        )
        
        search = TavilySearchResults(
            api_key=tavily_key,
            max_results=5,
            search_depth="advanced"
        )
        
        # DataScout agent prompt
        agent_prompt = f"""You are DataScout, an environmental hazard detection specialist.
        
        Your task: Search for environmental health hazards in {request.location}.
        Focus on:
        - Air quality issues
        - Water contamination
        - Industrial pollution
        - Chemical hazards
        - Recent environmental incidents
        
        Based on the search results, provide a concise summary of environmental hazards found."""
        
        # Perform search
        search_query = f"environmental hazards pollution air quality water contamination {request.location}"
        raw_results = search.invoke(search_query)
        
        # Process results with LLM
        search_context = json.dumps(raw_results, indent=2)
        analysis_prompt = f"{agent_prompt}\n\nSearch Results:\n{search_context}\n\nProvide your analysis:"
        
        response = llm.invoke(analysis_prompt)
        
        # Format results
        formatted_results = []
        for result in raw_results:
            formatted_results.append({
                "title": result.get("title", "No title"),
                "url": result.get("url", ""),
                "content": result.get("content", "")[:500] + "..."  # Truncate long content
            })
        
        return DataScoutResponse(
            status="success",
            location=request.location,
            search_results=formatted_results,
            agent_analysis=response.content,
            raw_search_data=raw_results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DataScout error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)