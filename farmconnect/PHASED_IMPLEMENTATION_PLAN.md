# FarmConnect - Phased Implementation Plan
## Fully Functional UI & Testing Strategy for Each Phase

---

## 📋 Implementation Overview

### Timeline: 12 Months
### Budget: ₹2.5 Cr total investment
### Team: 8-12 developers (scaling by phase)
### Deployment: Kubernetes + Docker on AWS/GCP

---

## 🚀 Phase 1: Foundation & Core Marketplace (Weeks 1-8) ✅

### **Objectives:**
- Launch functional marketplace with basic features
- Implement core user flows (farmer onboarding, product listing, consumer purchase)
- Deploy to production with 100 farmers, 1000 consumers
- Achieve ₹10L GMV in first 2 months

### **Success Metrics:**
- ✅ **100 farmers** onboarded with verified profiles
- ✅ **1000 consumers** registered and active
- ✅ **₹10L GMV** in first 2 months
- ✅ **95% uptime** with proper monitoring
- ✅ **<2s page load** times
- ✅ **90% test coverage** (unit + integration)

---

## 🤖 Phase 2: AI Agent Integration (Weeks 9-16)

### **Objectives:**
- Integrate LangGraph-based multi-agent system
- Implement automated price monitoring across 5 platforms
- Deploy AI quality inspection with computer vision
- Launch intelligent farmer assistance with voice interface
- Scale to ₹50L GMV monthly

---

### **Week 9-10: Agent Infrastructure & Backend**

#### **LangGraph Agent System Setup:**

1. **Agent Dependencies Installation**
```python
# requirements-phase2.txt
langchain==0.1.0
langgraph==0.0.26
langchain-openai==0.0.5
langchain-community==0.0.10
playwright==1.40.0
beautifulsoup4==4.12.2
opencv-python==4.8.1
pillow==10.1.0
celery==5.3.4
redis==5.0.1
prophet==1.1.5
scikit-learn==1.3.2
```

2. **Agent Service Architecture**
```python
# agents/agent_manager.py
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
from agents.supervisor_agent import SupervisorAgent
from agents.price_monitor import PriceMonitorAgent
from agents.quality_inspector import QualityInspectorAgent
from agents.farmer_assistant import FarmerAssistantAgent

class AgentManager:
    """Central manager for all AI agents"""
    
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.active_tasks: Dict[str, Dict] = {}
        
    async def execute_task(self, task_type: str, data: Dict[str, Any]) -> Dict:
        """Execute agent task and return results"""
        
        task_id = f"{task_type}_{datetime.now().timestamp()}"
        
        # Track active task
        self.active_tasks[task_id] = {
            "status": "running",
            "started_at": datetime.now(),
            "task_type": task_type,
            "data": data
        }
        
        try:
            # Execute through supervisor
            result = await self.supervisor.execute(task_type, data)
            
            # Update status
            self.active_tasks[task_id].update({
                "status": "completed",
                "completed_at": datetime.now(),
                "result": result
            })
            
            return {
                "task_id": task_id,
                "success": True,
                "result": result
            }
            
        except Exception as e:
            self.active_tasks[task_id].update({
                "status": "failed",
                "completed_at": datetime.now(),
                "error": str(e)
            })
            
            return {
                "task_id": task_id,
                "success": False,
                "error": str(e)
            }
    
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a running task"""
        return self.active_tasks.get(task_id)

# Initialize global agent manager
agent_manager = AgentManager()
```

3. **Enhanced API Endpoints**
```python
# app/routers/agents.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.agents.agent_manager import agent_manager
from app.models.agent_models import TaskRequest, TaskResponse

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.post("/price-check", response_model=TaskResponse)
async def price_check(
    request: TaskRequest,
    background_tasks: BackgroundTasks
):
    """Trigger automated price checking across platforms"""
    
    task_data = {
        "products": request.products,
        "platforms": request.platforms or ["bigbasket", "zepto", "swiggy", "blinkit", "jiomart"],
        "location": request.location
    }
    
    # Execute in background
    result = await agent_manager.execute_task("price_check", task_data)
    
    return TaskResponse(
        task_id=result["task_id"],
        success=result["success"],
        message="Price checking initiated",
        data=result.get("result")
    )

@router.post("/quality-inspect", response_model=TaskResponse)
async def quality_inspect(
    product_id: str,
    image_urls: List[str]
):
    """AI-powered quality inspection"""
    
    task_data = {
        "product_id": product_id,
        "images": image_urls
    }
    
    result = await agent_manager.execute_task("quality_assess", task_data)
    
    return TaskResponse(
        task_id=result["task_id"],
        success=result["success"],
        message="Quality inspection completed",
        data=result.get("result")
    )

@router.post("/farmer-assist")
async def farmer_assist(
    farmer_id: str,
    query: str,
    voice_input: Optional[str] = None
):
    """AI farming assistant with voice support"""
    
    task_data = {
        "farmer_id": farmer_id,
        "query": query,
        "voice_input": voice_input
    }
    
    result = await agent_manager.execute_task("farmer_assist", task_data)
    
    return result

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of running task"""
    
    status = await agent_manager.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return status
```

4. **Database Schema Updates**
```sql
-- Agent execution tracking
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(255) UNIQUE NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    status ENUM('running', 'completed', 'failed') NOT NULL,
    input_data JSONB,
    result_data JSONB,
    error_message TEXT,
    execution_time_ms INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Price monitoring results
CREATE TABLE price_monitoring (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    platform VARCHAR(50) NOT NULL,
    price DECIMAL(10,2),
    availability BOOLEAN,
    discount_percentage DECIMAL(5,2),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent_confidence DECIMAL(3,2)
);

-- Quality inspection results
CREATE TABLE quality_inspections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    inspection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    grade ENUM('A', 'B', 'C', 'Rejected') NOT NULL,
    confidence_score DECIMAL(3,2),
    defects_detected TEXT[],
    ai_recommendation TEXT,
    inspector_notes TEXT,
    images_analyzed TEXT[]
);

-- Farmer assistance interactions
CREATE TABLE farmer_assistance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farmer_id UUID REFERENCES farmers(id),
    query_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    query_type VARCHAR(100),
    voice_input_url TEXT,
    voice_response_url TEXT,
    satisfaction_rating INTEGER CHECK (satisfaction_rating BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### **Week 11-12: Frontend Agent Integration**

#### **AI-Powered Price Monitoring Dashboard**

1. **Real-time Price Comparison Component**
```tsx
// components/PriceMonitoring/PriceComparison.tsx
interface PriceData {
  platform: string;
  price: number;
  availability: boolean;
  lastUpdated: string;
  trend: 'up' | 'down' | 'stable';
}

export const PriceComparison: React.FC<{ productId: string }> = ({ productId }) => {
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    const fetchPrices = async () => {
      setLoading(true);
      try {
        const response = await api.post('/api/agents/price-check', {
          products: [{ id: productId }],
          platforms: ['bigbasket', 'zepto', 'swiggy', 'blinkit', 'jiomart']
        });
        
        // Poll for results
        const taskId = response.data.task_id;
        pollTaskStatus(taskId);
        
      } catch (error) {
        console.error('Price check failed:', error);
        setLoading(false);
      }
    };

    const pollTaskStatus = async (taskId: string) => {
      const pollInterval = setInterval(async () => {
        try {
          const status = await api.get(`/api/agents/tasks/${taskId}`);
          
          if (status.data.status === 'completed') {
            setPriceData(status.data.result.prices);
            setLoading(false);
            clearInterval(pollInterval);
          } else if (status.data.status === 'failed') {
            setLoading(false);
            clearInterval(pollInterval);
          }
        } catch (error) {
          clearInterval(pollInterval);
          setLoading(false);
        }
      }, 2000);
    };

    fetchPrices();
    
    // Auto-refresh every 5 minutes if enabled
    let refreshInterval: NodeJS.Timeout;
    if (autoRefresh) {
      refreshInterval = setInterval(fetchPrices, 5 * 60 * 1000);
    }

    return () => {
      if (refreshInterval) clearInterval(refreshInterval);
    };
  }, [productId, autoRefresh]);

  const calculateSavings = (farmerPrice: number, retailPrices: PriceData[]) => {
    const avgRetailPrice = retailPrices
      .filter(p => p.availability)
      .reduce((sum, p) => sum + p.price, 0) / retailPrices.length;
    
    return ((avgRetailPrice - farmerPrice) / avgRetailPrice * 100).toFixed(1);
  };

  if (loading) {
    return <PriceComparisonSkeleton />;
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-2xl font-bold text-gray-900">
          Live Price Comparison
        </h3>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-3 py-2 rounded-lg text-sm font-medium ${
              autoRefresh 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            {autoRefresh ? '🟢 Auto-refresh ON' : '⚪ Auto-refresh OFF'}
          </button>
          <span className="text-sm text-gray-500">
            Last updated: {priceData[0]?.lastUpdated}
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-gray-200">
              <th className="text-left py-4 px-4 font-semibold">Platform</th>
              <th className="text-center py-4 px-4 font-semibold">Price (₹/kg)</th>
              <th className="text-center py-4 px-4 font-semibold">Status</th>
              <th className="text-center py-4 px-4 font-semibold">Trend</th>
              <th className="text-center py-4 px-4 font-semibold">Your Advantage</th>
            </tr>
          </thead>
          <tbody>
            {/* FarmConnect row */}
            <tr className="bg-green-50 border-b">
              <td className="py-4 px-4 font-bold text-green-800 flex items-center">
                <span className="material-icons mr-2">agriculture</span>
                FarmConnect (Direct)
              </td>
              <td className="text-center py-4 px-4 font-bold text-green-600 text-lg">
                ₹35.00
              </td>
              <td className="text-center py-4 px-4">
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm">
                  ✓ Available
                </span>
              </td>
              <td className="text-center py-4 px-4">
                <span className="text-green-600">📈 Best Price</span>
              </td>
              <td className="text-center py-4 px-4 bg-green-100">
                <span className="bg-green-600 text-white px-3 py-1 rounded-full font-bold">
                  {calculateSavings(35, priceData)}% SAVINGS
                </span>
              </td>
            </tr>
            
            {/* Retail platforms */}
            {priceData.map((platform, index) => (
              <tr key={platform.platform} className="border-b hover:bg-gray-50">
                <td className="py-4 px-4 flex items-center">
                  <img 
                    src={`/logos/${platform.platform}.png`} 
                    alt={platform.platform}
                    className="w-6 h-6 mr-2"
                  />
                  {platform.platform.charAt(0).toUpperCase() + platform.platform.slice(1)}
                </td>
                <td className="text-center py-4 px-4 text-gray-500">
                  {platform.availability ? (
                    <span className="line-through">₹{platform.price.toFixed(2)}</span>
                  ) : (
                    <span className="text-red-500">Out of Stock</span>
                  )}
                </td>
                <td className="text-center py-4 px-4">
                  <span className={`px-2 py-1 rounded-full text-sm ${
                    platform.availability 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {platform.availability ? '✓ Available' : '✗ Out of Stock'}
                  </span>
                </td>
                <td className="text-center py-4 px-4">
                  {platform.trend === 'up' && <span className="text-red-500">📈 ↑</span>}
                  {platform.trend === 'down' && <span className="text-green-500">📉 ↓</span>}
                  {platform.trend === 'stable' && <span className="text-gray-500">→</span>}
                </td>
                <td className="text-center py-4 px-4">
                  {platform.availability ? (
                    <span className="text-red-600 font-medium">
                      +₹{(platform.price - 35).toFixed(2)} more
                    </span>
                  ) : (
                    <span className="text-gray-400">N/A</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Market Insights */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-semibold text-blue-900 mb-2">💡 AI Market Insights</h4>
        <p className="text-blue-800 text-sm">
          Current demand is HIGH for this product. Retail prices have increased 8% this week. 
          Your direct pricing offers customers significant savings while maintaining quality.
        </p>
      </div>
    </div>
  );
};
```

2. **AI Quality Inspector Interface**
```tsx
// components/QualityInspection/QualityInspector.tsx
export const QualityInspector: React.FC<{ productId: string }> = ({ productId }) => {
  const [images, setImages] = useState<File[]>([]);
  const [inspectionResult, setInspectionResult] = useState<QualityReport | null>(null);
  const [loading, setLoading] = useState(false);

  const handleImageUpload = (files: FileList) => {
    const newImages = Array.from(files);
    setImages(prev => [...prev, ...newImages]);
  };

  const runQualityInspection = async () => {
    if (images.length === 0) return;

    setLoading(true);
    
    try {
      // Upload images
      const imageUrls = await uploadImages(images);
      
      // Trigger AI inspection
      const response = await api.post('/api/agents/quality-inspect', {
        product_id: productId,
        image_urls: imageUrls
      });
      
      // Poll for results
      const taskId = response.data.task_id;
      const pollInterval = setInterval(async () => {
        const status = await api.get(`/api/agents/tasks/${taskId}`);
        
        if (status.data.status === 'completed') {
          setInspectionResult(status.data.result);
          setLoading(false);
          clearInterval(pollInterval);
        }
      }, 1000);
      
    } catch (error) {
      console.error('Quality inspection failed:', error);
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-2xl font-bold text-gray-900 mb-6">
        🔍 AI Quality Inspector
      </h3>

      {/* Image Upload Area */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload Product Images (Max 5)
        </label>
        
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
          <input
            type="file"
            multiple
            accept="image/*"
            onChange={(e) => handleImageUpload(e.target.files!)}
            className="hidden"
            id="image-upload"
            disabled={images.length >= 5}
          />
          <label
            htmlFor="image-upload"
            className="cursor-pointer inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <span className="material-icons mr-2">cloud_upload</span>
            Choose Images
          </label>
          <p className="mt-2 text-sm text-gray-500">
            PNG, JPG up to 10MB each ({images.length}/5)
          </p>
        </div>

        {/* Image Preview */}
        {images.length > 0 && (
          <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-4">
            {images.map((image, index) => (
              <div key={index} className="relative">
                <img
                  src={URL.createObjectURL(image)}
                  alt={`Preview ${index + 1}`}
                  className="w-full h-32 object-cover rounded-lg"
                />
                <button
                  onClick={() => setImages(prev => prev.filter((_, i) => i !== index))}
                  className="absolute -top-2 -right-2 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Inspect Button */}
      <Button
        onClick={runQualityInspection}
        disabled={images.length === 0 || loading}
        loading={loading}
        className="w-full mb-6"
      >
        {loading ? 'AI Analyzing Images...' : 'Run Quality Inspection'}
      </Button>

      {/* Inspection Results */}
      {inspectionResult && (
        <div className="space-y-6">
          {/* Overall Grade */}
          <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-xl font-bold text-gray-900">Quality Assessment</h4>
              <div className={`px-4 py-2 rounded-full font-bold text-lg ${
                inspectionResult.grade === 'A' ? 'bg-green-600 text-white' :
                inspectionResult.grade === 'B' ? 'bg-yellow-500 text-white' :
                inspectionResult.grade === 'C' ? 'bg-orange-500 text-white' :
                'bg-red-600 text-white'
              }`}>
                Grade {inspectionResult.grade}
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {inspectionResult.freshness_score}/10
                </div>
                <div className="text-sm text-gray-600">Freshness</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {inspectionResult.confidence}%
                </div>
                <div className="text-sm text-gray-600">AI Confidence</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {inspectionResult.shelf_life}
                </div>
                <div className="text-sm text-gray-600">Shelf Life</div>
              </div>
              <div className="text-center">
                <div className={`text-2xl font-bold ${
                  inspectionResult.defects.length === 0 ? 'text-green-600' : 'text-orange-600'
                }`}>
                  {inspectionResult.defects.length}
                </div>
                <div className="text-sm text-gray-600">Issues Found</div>
              </div>
            </div>
          </div>

          {/* Detailed Analysis */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Defects */}
            <div className="bg-white border rounded-lg p-4">
              <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                <span className="material-icons mr-2 text-orange-500">warning</span>
                Issues Detected
              </h5>
              {inspectionResult.defects.length > 0 ? (
                <ul className="space-y-2">
                  {inspectionResult.defects.map((defect, index) => (
                    <li key={index} className="flex items-center text-sm text-gray-700">
                      <span className="w-2 h-2 bg-orange-400 rounded-full mr-2"></span>
                      {defect}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-green-600 text-sm">✓ No issues detected</p>
              )}
            </div>

            {/* Recommendations */}
            <div className="bg-white border rounded-lg p-4">
              <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                <span className="material-icons mr-2 text-blue-500">lightbulb</span>
                AI Recommendations
              </h5>
              <p className="text-sm text-gray-700">
                {inspectionResult.recommendation}
              </p>
            </div>
          </div>

          {/* Pricing Suggestions */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h5 className="font-semibold text-blue-900 mb-2">💰 Pricing Suggestions</h5>
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="font-medium text-blue-800">Premium Market:</span>
                <span className="text-blue-700 ml-1">₹45-50/kg</span>
              </div>
              <div>
                <span className="font-medium text-blue-800">Regular Market:</span>
                <span className="text-blue-700 ml-1">₹35-40/kg</span>
              </div>
              <div>
                <span className="font-medium text-blue-800">Quick Sale:</span>
                <span className="text-blue-700 ml-1">₹25-30/kg</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
```

3. **Voice-Enabled Farmer Assistant**
```tsx
// components/FarmerAssistant/VoiceAssistant.tsx
export const VoiceAssistant: React.FC<{ farmerId: string }> = ({ farmerId }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState<string>('hi-IN'); // Hindi default

  // Voice recognition setup
  const recognition = useSpeechRecognition({
    onResult: (text: string) => {
      setTranscript(text);
      if (!isListening) {
        handleVoiceQuery(text);
      }
    },
    language: language
  });

  const toggleListening = () => {
    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      recognition.start();
      setIsListening(true);
    }
  };

  const handleVoiceQuery = async (query: string) => {
    setLoading(true);
    
    try {
      const response = await api.post('/api/agents/farmer-assist', {
        farmer_id: farmerId,
        query: query,
        voice_input: query,
        language: language
      });
      
      setResponse(response.data.result.response);
      
      // Text-to-speech for response
      if (response.data.result.voice_response_url) {
        const audio = new Audio(response.data.result.voice_response_url);
        audio.play();
      } else {
        // Fallback to browser TTS
        const utterance = new SpeechSynthesisUtterance(response.data.result.response);
        utterance.lang = language;
        speechSynthesis.speak(utterance);
      }
      
    } catch (error) {
      console.error('Farmer assistance failed:', error);
      setResponse('Sorry, I could not process your request. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTextQuery = async () => {
    if (!transcript.trim()) return;
    await handleVoiceQuery(transcript);
  };

  return (
    <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-bold text-gray-900">
          🤖 AI Farming Assistant
        </h3>
        
        {/* Language Selection */}
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        >
          <option value="hi-IN">हिंदी (Hindi)</option>
          <option value="en-IN">English</option>
          <option value="mr-IN">मराठी (Marathi)</option>
          <option value="te-IN">తెలుగు (Telugu)</option>
          <option value="ta-IN">தமிழ் (Tamil)</option>
          <option value="kn-IN">ಕನ್ನಡ (Kannada)</option>
          <option value="gu-IN">ગુજરાતી (Gujarati)</option>
          <option value="pa-IN">ਪੰਜਾਬੀ (Punjabi)</option>
        </select>
      </div>

      {/* Voice Input Section */}
      <div className="bg-white rounded-lg p-6 mb-6">
        <div className="text-center">
          {/* Voice Button */}
          <button
            onClick={toggleListening}
            className={`w-20 h-20 rounded-full flex items-center justify-center text-2xl transition-all duration-300 ${
              isListening
                ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                : 'bg-green-500 hover:bg-green-600 text-white'
            }`}
            disabled={loading}
          >
            {loading ? (
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
            ) : (
              <span className="material-icons">
                {isListening ? 'mic' : 'mic_none'}
              </span>
            )}
          </button>
          
          <p className="mt-4 text-sm text-gray-600">
            {isListening
              ? 'Listening... Speak now'
              : loading
              ? 'Processing your query...'
              : 'Click to start voice input'
            }
          </p>
        </div>

        {/* Text Input */}
        <div className="mt-6">
          <div className="flex space-x-2">
            <input
              type="text"
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Or type your farming question here..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && handleTextQuery()}
            />
            <button
              onClick={handleTextQuery}
              disabled={!transcript.trim() || loading}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Ask
            </button>
          </div>
        </div>
      </div>

      {/* Response Section */}
      {response && (
        <div className="bg-white rounded-lg p-6">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <span className="material-icons text-green-600">agriculture</span>
              </div>
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-gray-900 mb-2">AI Assistant Response:</h4>
              <div className="prose prose-sm text-gray-700">
                <ReactMarkdown>{response}</ReactMarkdown>
              </div>
              
              {/* Action Buttons */}
              <div className="mt-4 flex space-x-2">
                <button
                  onClick={() => {
                    const utterance = new SpeechSynthesisUtterance(response);
                    utterance.lang = language;
                    speechSynthesis.speak(utterance);
                  }}
                  className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm hover:bg-blue-200"
                >
                  🔊 Read Aloud
                </button>
                <button
                  onClick={() => navigator.clipboard.writeText(response)}
                  className="px-3 py-1 bg-gray-100 text-gray-800 rounded text-sm hover:bg-gray-200"
                >
                  📋 Copy
                </button>
                <button
                  onClick={() => {/* Share functionality */}}
                  className="px-3 py-1 bg-green-100 text-green-800 rounded text-sm hover:bg-green-200"
                >
                  📤 Share
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Suggestions */}
      <div className="mt-6">
        <h4 className="font-semibold text-gray-900 mb-3">💡 Quick Questions:</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            "आज मौसम कैसा है? (How's the weather today?)",
            "टमाटर की फसल कब तैयार होगी? (When will tomato crop be ready?)",
            "बाजार में प्याज का भाव क्या है? (What's the onion price in market?)",
            "कीटनाशक कब छिड़कना चाहिए? (When to spray pesticide?)"
          ].map((question, index) => (
            <button
              key={index}
              onClick={() => {
                setTranscript(question);
                handleVoiceQuery(question);
              }}
              className="text-left px-4 py-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-sm transition-colors"
            >
              {question}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
```

---

### **Week 13-14: Advanced Agent Features**

1. **Market Intelligence Dashboard**
```tsx
// components/MarketIntelligence/MarketDashboard.tsx
export const MarketDashboard: React.FC = () => {
  const [marketData, setMarketData] = useState<MarketInsights>();
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [selectedCrops, setSelectedCrops] = useState<string[]>(['tomato', 'onion', 'potato']);

  const fetchMarketInsights = async () => {
    const response = await api.post('/api/agents/market-analysis', {
      crops: selectedCrops,
      timeRange: selectedTimeRange,
      includeWeatherData: true,
      includePriceForecasts: true
    });
    
    setMarketData(response.data.result);
  };

  return (
    <div className="space-y-6">
      {/* Market Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard
          title="Market Sentiment"
          value={marketData?.sentiment || 'Bullish'}
          change="+5% vs last week"
          icon="trending_up"
          color="green"
        />
        <MetricCard
          title="Avg Price Increase"
          value={`${marketData?.avgPriceChange || 8}%`}
          change="Across all crops"
          icon="attach_money"
          color="blue"
        />
        <MetricCard
          title="Supply Status"
          value={marketData?.supplyStatus || 'Normal'}
          change="Adequate for demand"
          icon="inventory"
          color="yellow"
        />
        <MetricCard
          title="Weather Impact"
          value={marketData?.weatherImpact || 'Low'}
          change="Next 15 days"
          icon="cloud"
          color="purple"
        />
      </div>

      {/* Price Trend Charts */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold text-gray-900">Price Trends & Forecasts</h3>
          <div className="flex space-x-2">
            {['7d', '30d', '90d'].map((range) => (
              <button
                key={range}
                onClick={() => setSelectedTimeRange(range)}
                className={`px-3 py-2 rounded-lg text-sm font-medium ${
                  selectedTimeRange === range
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {range.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Interactive Chart Component */}
        <PriceChart data={marketData?.priceHistory} forecasts={marketData?.forecasts} />
      </div>

      {/* AI Insights & Recommendations */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <span className="material-icons mr-2 text-blue-500">psychology</span>
            AI Market Insights
          </h4>
          <div className="space-y-3">
            {marketData?.insights?.map((insight, index) => (
              <div key={index} className="p-3 bg-blue-50 rounded-lg">
                <div className="flex justify-between items-start mb-2">
                  <span className="font-medium text-blue-900">{insight.title}</span>
                  <span className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded">
                    {Math.round(insight.confidence * 100)}% confident
                  </span>
                </div>
                <p className="text-blue-800 text-sm">{insight.description}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <span className="material-icons mr-2 text-green-500">recommend</span>
            Recommended Actions
          </h4>
          <div className="space-y-3">
            {marketData?.recommendations?.map((rec, index) => (
              <div key={index} className="p-3 bg-green-50 rounded-lg">
                <div className="flex items-start space-x-3">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    rec.priority === 'high' ? 'bg-red-500' :
                    rec.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                  }`}></div>
                  <div className="flex-1">
                    <p className="font-medium text-green-900">{rec.action}</p>
                    <p className="text-green-700 text-sm mt-1">{rec.reason}</p>
                    <p className="text-green-600 text-xs mt-1">
                      Expected impact: {rec.expectedImpact}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
```

2. **Automated Logistics Optimization**
```tsx
// components/Logistics/LogisticsOptimizer.tsx
export const LogisticsOptimizer: React.FC = () => {
  const [pendingOrders, setPendingOrders] = useState<Order[]>([]);
  const [optimizationResult, setOptimizationResult] = useState<LogisticsPlan>();
  const [optimizing, setOptimizing] = useState(false);

  const optimizeRoutes = async () => {
    setOptimizing(true);
    
    try {
      const response = await api.post('/api/agents/optimize-logistics', {
        orders: pendingOrders.map(order => ({
          id: order.id,
          delivery_location: order.delivery_address,
          items: order.items,
          priority: order.priority,
          time_window: order.preferred_delivery_time
        })),
        constraints: {
          max_vehicle_capacity: 500, // kg
          max_delivery_time: 8, // hours
          driver_count: 3
        }
      });
      
      setOptimizationResult(response.data.result);
      
    } catch (error) {
      console.error('Logistics optimization failed:', error);
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Optimization Controls */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-xl font-bold text-gray-900">Logistics Optimization</h3>
            <p className="text-gray-600">AI-powered route planning and delivery optimization</p>
          </div>
          
          <button
            onClick={optimizeRoutes}
            disabled={pendingOrders.length === 0 || optimizing}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {optimizing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Optimizing...</span>
              </>
            ) : (
              <>
                <span className="material-icons">route</span>
                <span>Optimize Routes</span>
              </>
            )}
          </button>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{pendingOrders.length}</div>
            <div className="text-sm text-gray-600">Pending Orders</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {pendingOrders.reduce((sum, o) => sum + o.total_weight, 0)}kg
            </div>
            <div className="text-sm text-gray-600">Total Weight</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">
              {optimizationResult?.routes?.length || 0}
            </div>
            <div className="text-sm text-gray-600">Optimized Routes</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-orange-600">
              ₹{optimizationResult?.total_cost || 0}
            </div>
            <div className="text-sm text-gray-600">Estimated Cost</div>
          </div>
        </div>
      </div>

      {/* Route Visualization */}
      {optimizationResult && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h4 className="text-lg font-bold text-gray-900 mb-4">Optimized Routes</h4>
          
          {/* Map Component */}
          <div className="h-96 bg-gray-100 rounded-lg mb-6 relative">
            <InteractiveMap
              routes={optimizationResult.routes}
              orderLocations={pendingOrders.map(o => o.delivery_address)}
            />
          </div>

          {/* Route Details */}
          <div className="space-y-4">
            {optimizationResult.routes.map((route, index) => (
              <div key={route.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-center mb-3">
                  <h5 className="font-semibold text-gray-900">
                    Route {index + 1} - Vehicle {route.vehicle_id}
                  </h5>
                  <div className="flex space-x-4 text-sm text-gray-600">
                    <span>{route.distance}km</span>
                    <span>{route.duration}hrs</span>
                    <span>₹{route.cost}</span>
                  </div>
                </div>
                
                <div className="grid md:grid-cols-2 gap-4">
                  {/* Delivery Stops */}
                  <div>
                    <h6 className="font-medium text-gray-800 mb-2">Delivery Stops</h6>
                    <div className="space-y-2">
                      {route.stops.map((stop, stopIndex) => (
                        <div key={stopIndex} className="flex items-center space-x-3 text-sm">
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-xs ${
                            stopIndex === 0 ? 'bg-green-500' : 
                            stopIndex === route.stops.length - 1 ? 'bg-red-500' : 'bg-blue-500'
                          }`}>
                            {stopIndex + 1}
                          </div>
                          <div className="flex-1">
                            <div className="font-medium">{stop.customer_name}</div>
                            <div className="text-gray-600">{stop.address}</div>
                          </div>
                          <div className="text-gray-500">
                            {stop.estimated_time}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Route Statistics */}
                  <div>
                    <h6 className="font-medium text-gray-800 mb-2">Route Statistics</h6>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Load Utilization:</span>
                        <span className="font-medium">{route.load_utilization}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Fuel Efficiency:</span>
                        <span className="font-medium">{route.fuel_efficiency} km/l</span>
                      </div>
                      <div className="flex justify-between">
                        <span>CO2 Emissions:</span>
                        <span className="font-medium">{route.co2_emissions} kg</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Delivery Time Window:</span>
                        <span className="font-medium">{route.time_window}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="mt-4 flex space-x-2">
                  <button className="px-3 py-2 bg-green-100 text-green-800 rounded text-sm hover:bg-green-200">
                    Assign Driver
                  </button>
                  <button className="px-3 py-2 bg-blue-100 text-blue-800 rounded text-sm hover:bg-blue-200">
                    Track Route
                  </button>
                  <button className="px-3 py-2 bg-gray-100 text-gray-800 rounded text-sm hover:bg-gray-200">
                    Send Notifications
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

---

### **Week 15-16: Testing & Integration**

#### **Phase 2 Testing Strategy:**

1. **Agent Unit Tests**
```python
# tests/test_agents/test_supervisor.py
import pytest
import asyncio
from agents.supervisor_agent import SupervisorAgent, AgentState

@pytest.mark.asyncio
async def test_supervisor_price_monitoring():
    """Test supervisor orchestrating price monitoring"""
    
    supervisor = SupervisorAgent()
    
    initial_data = {
        "products": [
            {"id": "1", "name": "Tomatoes", "unit": "kg"}
        ],
        "max_iterations": 5
    }
    
    result = await supervisor.execute("price_check", initial_data)
    
    assert result["success"] == True
    assert "prices" in result
    assert result["iterations"] <= 5
    assert len(result["prices"]) > 0

@pytest.mark.asyncio 
async def test_supervisor_quality_inspection():
    """Test supervisor orchestrating quality inspection"""
    
    supervisor = SupervisorAgent()
    
    initial_data = {
        "product_images": ["/path/to/tomato.jpg"],
        "max_iterations": 3
    }
    
    result = await supervisor.execute("quality_assess", initial_data)
    
    assert result["success"] == True
    assert "quality_reports" in result
    assert result["quality_reports"][0]["grade"] in ["A", "B", "C", "Rejected"]

# Agent Integration Tests
@pytest.mark.integration
async def test_full_agent_workflow():
    """Test complete agent workflow from price check to quality assessment"""
    
    supervisor = SupervisorAgent()
    
    # Multi-step task
    initial_data = {
        "task_description": "Check prices and assess quality for tomato batch",
        "products": [{"id": "1", "name": "Tomatoes"}],
        "product_images": ["/path/to/tomato.jpg"]
    }
    
    result = await supervisor.execute("market_analysis", initial_data)
    
    assert result["success"] == True
    assert result["prices"] is not None
    assert result["quality_reports"] is not None
    assert result["market_insights"] is not None
```

2. **Frontend Integration Tests**
```typescript
// cypress/integration/phase2-agents.spec.ts
describe('Phase 2: AI Agent Integration', () => {
  beforeEach(() => {
    // Setup authenticated farmer
    cy.login('farmer', '9876543210');
    cy.visit('/farmer/dashboard');
  });

  it('should trigger and display price monitoring results', () => {
    // Navigate to price monitoring
    cy.get('[data-testid=price-monitoring]').click();
    
    // Select product
    cy.get('[data-testid=product-selector]').select('Tomatoes');
    
    // Start price check
    cy.get('[data-testid=start-price-check]').click();
    
    // Wait for results (with timeout)
    cy.get('[data-testid=price-results]', { timeout: 30000 }).should('be.visible');
    
    // Verify platform prices displayed
    cy.get('[data-testid=platform-price]').should('have.length.at.least', 3);
    
    // Verify savings calculation
    cy.get('[data-testid=savings-percentage]').should('contain', '%');
  });

  it('should complete quality inspection workflow', () => {
    cy.get('[data-testid=quality-inspector]').click();
    
    // Upload images
    const fileName = 'tomato-sample.jpg';
    cy.fixture(fileName).then(fileContent => {
      cy.get('[data-testid=image-upload]').attachFile(fileName);
    });
    
    // Start inspection
    cy.get('[data-testid=run-inspection]').click();
    
    // Wait for AI analysis
    cy.get('[data-testid=inspection-results]', { timeout: 45000 }).should('be.visible');
    
    // Verify grade assigned
    cy.get('[data-testid=quality-grade]').should('contain.oneOf', ['A', 'B', 'C', 'Rejected']);
    
    // Verify confidence score
    cy.get('[data-testid=confidence-score]').should('contain', '%');
  });

  it('should handle voice assistant interaction', () => {
    cy.get('[data-testid=voice-assistant]').click();
    
    // Mock voice input (since we can't test actual speech)
    cy.get('[data-testid=transcript-input]').type('What is the weather today?');
    
    // Submit query
    cy.get('[data-testid=ask-assistant]').click();
    
    // Wait for response
    cy.get('[data-testid=assistant-response]', { timeout: 20000 }).should('be.visible');
    
    // Verify response content
    cy.get('[data-testid=assistant-response]').should('not.be.empty');
    
    // Test language switching
    cy.get('[data-testid=language-selector]').select('Hindi');
    cy.get('[data-testid=transcript-input]').clear().type('आज मौसम कैसा है?');
    cy.get('[data-testid=ask-assistant]').click();
    
    cy.get('[data-testid=assistant-response]').should('be.visible');
  });

  it('should display market intelligence dashboard', () => {
    cy.get('[data-testid=market-intelligence]').click();
    
    // Verify market sentiment
    cy.get('[data-testid=market-sentiment]').should('be.visible');
    
    // Verify price charts
    cy.get('[data-testid=price-chart]').should('be.visible');
    
    // Test time range selection
    cy.get('[data-testid=time-range-30d]').click();
    cy.get('[data-testid=price-chart]').should('be.visible');
    
    // Verify AI insights
    cy.get('[data-testid=ai-insights]').should('have.length.at.least', 1);
    
    // Verify recommendations
    cy.get('[data-testid=recommendations]').should('have.length.at.least', 1);
  });
});
```

3. **Load Testing for Agent System**
```python
# load_tests/test_agent_performance.py
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

async def test_agent_concurrency():
    """Test agent system under concurrent load"""
    
    async def make_request(session, endpoint, data):
        async with session.post(f"http://localhost:8000/api/agents/{endpoint}", json=data) as response:
            return await response.json()
    
    # Test data
    test_data = {
        "products": [{"id": str(i), "name": f"Product {i}"} for i in range(10)],
        "platforms": ["bigbasket", "zepto", "swiggy"]
    }
    
    async with aiohttp.ClientSession() as session:
        # Concurrent price checks
        tasks = []
        for i in range(50):  # 50 concurrent requests
            task = make_request(session, "price-check", test_data)
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyze results
        successful_requests = [r for r in results if not isinstance(r, Exception)]
        failed_requests = [r for r in results if isinstance(r, Exception)]
        
        print(f"Concurrent Agent Load Test Results:")
        print(f"Total requests: 50")
        print(f"Successful: {len(successful_requests)}")
        print(f"Failed: {len(failed_requests)}")
        print(f"Total time: {end_time - start_time:.2f} seconds")
        print(f"Avg response time: {(end_time - start_time) / 50:.2f} seconds")
        
        assert len(successful_requests) >= 45  # 90% success rate
        assert (end_time - start_time) < 60  # Complete within 1 minute

if __name__ == "__main__":
    asyncio.run(test_agent_concurrency())
```

#### **Phase 2 Success Metrics:**
- ✅ **95% accuracy** in price scraping across 5 platforms
- ✅ **90% accuracy** in AI quality grading
- ✅ **<30 seconds** average agent response time
- ✅ **Voice support** in 8 Indian languages
- ✅ **₹50L GMV** monthly (5x growth from Phase 1)
- ✅ **500 farmers** actively using AI tools
- ✅ **85% farmer satisfaction** with AI assistance
- ✅ **50% reduction** in manual quality disputes

**Phase 2 Deployment Checklist:**
```markdown
## Phase 2 Production Deployment

### Infrastructure
- [ ] Agent services deployed on Kubernetes
- [ ] Redis cluster for agent state management
- [ ] OpenAI API keys configured
- [ ] Webhook endpoints for real-time updates
- [ ] LangSmith monitoring enabled

### Agent Systems
- [ ] All 6 agents responding correctly
- [ ] Supervisor orchestration working
- [ ] Error handling and retries implemented
- [ ] Rate limiting configured for external APIs

### Frontend Integration
- [ ] Price monitoring dashboard functional
- [ ] Quality inspection UI working with image upload
- [ ] Voice assistant with multi-language support
- [ ] Market intelligence dashboard displaying data
- [ ] Real-time updates via WebSocket

### Testing
- [ ] All agent unit tests passing
- [ ] Integration tests covering workflows
- [ ] Load testing completed (50 concurrent users)
- [ ] End-to-end user journeys validated

### Monitoring
- [ ] Agent execution metrics tracked
- [ ] API response times monitored
- [ ] Error rates below 1%
- [ ] LangSmith traces available for debugging
```

---

## 🚀 Phase 3: Advanced Features & Financial Services (Weeks 17-24)

### **Objectives:**
- Implement IoT sensor integration for smart farming
- Launch FarmCredit micro-lending platform
- Deploy blockchain traceability system
- Scale to ₹2Cr GMV monthly
- Expand to 5 cities with 2000 farmers

---

### **Week 17-18: IoT & Smart Farming**

#### **IoT Sensor Integration Dashboard**

1. **Real-time Farm Monitoring**
```tsx
// components/IoT/FarmMonitoring.tsx
export const FarmMonitoringDashboard: React.FC<{ farmerId: string }> = ({ farmerId }) => {
  const [sensorData, setSensorData] = useState<SensorData[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedField, setSelectedField] = useState<string>('all');

  useEffect(() => {
    // WebSocket connection for real-time data
    const ws = new WebSocket(`ws://localhost:8000/ws/iot/${farmerId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setSensorData(prev => [...prev.slice(-99), data]); // Keep last 100 readings
    };

    return () => ws.close();
  }, [farmerId]);

  return (
    <div className="space-y-6">
      {/* Sensor Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SensorCard
          title="Soil Moisture"
          value={`${sensorData[0]?.soil_moisture || 0}%`}
          status={getSensorStatus(sensorData[0]?.soil_moisture, 'moisture')}
          icon="water_drop"
          trend={calculateTrend(sensorData, 'soil_moisture')}
        />
        <SensorCard
          title="pH Level"
          value={sensorData[0]?.ph_level || 'N/A'}
          status={getSensorStatus(sensorData[0]?.ph_level, 'ph')}
          icon="science"
          trend={calculateTrend(sensorData, 'ph_level')}
        />
        <SensorCard
          title="Temperature"
          value={`${sensorData[0]?.temperature || 0}°C`}
          status={getSensorStatus(sensorData[0]?.temperature, 'temperature')}
          icon="thermostat"
          trend={calculateTrend(sensorData, 'temperature')}
        />
        <SensorCard
          title="Humidity"
          value={`${sensorData[0]?.humidity || 0}%`}
          status={getSensorStatus(sensorData[0]?.humidity, 'humidity')}
          icon="humidity_percentage"
          trend={calculateTrend(sensorData, 'humidity')}
        />
      </div>

      {/* Real-time Charts */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold mb-4">Soil Moisture Trend</h3>
          <LineChart
            data={sensorData.map(d => ({
              time: d.timestamp,
              value: d.soil_moisture
            }))}
            color="#10B981"
          />
          <div className="mt-4 p-3 bg-green-50 rounded-lg">
            <p className="text-green-800 text-sm">
              💡 AI Recommendation: Soil moisture is optimal. Next irrigation suggested in 2 days.
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold mb-4">pH Level Monitoring</h3>
          <LineChart
            data={sensorData.map(d => ({
              time: d.timestamp,
              value: d.ph_level
            }))}
            color="#3B82F6"
          />
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-blue-800 text-sm">
              ⚠️ pH slightly acidic (6.2). Consider lime application next week.
            </p>
          </div>
        </div>
      </div>

      {/* Automated Actions */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold mb-4">🤖 Automated Actions</h3>
        <div className="space-y-4">
          {[
            {
              trigger: 'Soil moisture < 30%',
              action: 'Auto-irrigation triggered',
              status: 'active',
              lastExecuted: '2 hours ago'
            },
            {
              trigger: 'Temperature > 35°C',
              action: 'Shade net deployment alert',
              status: 'pending',
              lastExecuted: 'Never'
            },
            {
              trigger: 'pH < 6.0',
              action: 'Lime application reminder',
              status: 'scheduled',
              lastExecuted: '1 week ago'
            }
          ].map((automation, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <div className="font-medium text-gray-900">{automation.trigger}</div>
                <div className="text-sm text-gray-600">{automation.action}</div>
              </div>
              <div className="text-right">
                <div className={`px-2 py-1 rounded text-xs font-medium ${
                  automation.status === 'active' ? 'bg-green-100 text-green-800' :
                  automation.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {automation.status.toUpperCase()}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Last: {automation.lastExecuted}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
```

2. **Smart Irrigation Control**
```tsx
// components/IoT/IrrigationControl.tsx
export const IrrigationControl: React.FC = () => {
  const [irrigationSchedule, setIrrigationSchedule] = useState<IrrigationPlan[]>([]);
  const [manualMode, setManualMode] = useState(false);
  const [zones, setZones] = useState<IrrigationZone[]>([]);

  const triggerIrrigation = async (zoneId: string, duration: number) => {
    try {
      await api.post('/api/iot/irrigation/trigger', {
        zone_id: zoneId,
        duration_minutes: duration,
        triggered_by: 'manual'
      });
      
      toast.success(`Irrigation started for Zone ${zoneId}`);
    } catch (error) {
      toast.error('Failed to start irrigation');
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold">💧 Smart Irrigation Control</h3>
        <div className="flex items-center space-x-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={manualMode}
              onChange={(e) => setManualMode(e.target.checked)}
              className="mr-2"
            />
            Manual Mode
          </label>
        </div>
      </div>

      {/* Irrigation Zones */}
      <div className="grid md:grid-cols-2 gap-6">
        {zones.map((zone) => (
          <div key={zone.id} className="border rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h4 className="font-semibold">{zone.name}</h4>
              <div className={`px-2 py-1 rounded text-xs ${
                zone.status === 'active' ? 'bg-blue-100 text-blue-800' :
                zone.status === 'scheduled' ? 'bg-green-100 text-green-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {zone.status.toUpperCase()}
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Soil Moisture:</span>
                <span className={`font-medium ${
                  zone.current_moisture < 30 ? 'text-red-600' :
                  zone.current_moisture < 60 ? 'text-yellow-600' : 'text-green-600'
                }`}>
                  {zone.current_moisture}%
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Last Watered:</span>
                <span>{zone.last_irrigation}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Next Scheduled:</span>
                <span>{zone.next_irrigation}</span>
              </div>
            </div>

            {manualMode && (
              <div className="mt-4 flex space-x-2">
                <select className="flex-1 px-3 py-2 border rounded">
                  <option value="15">15 minutes</option>
                  <option value="30">30 minutes</option>
                  <option value="60">1 hour</option>
                </select>
                <button
                  onClick={() => triggerIrrigation(zone.id, 30)}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Start
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
```

### **Week 19-20: FarmCredit Micro-lending Platform**

1. **Credit Assessment Dashboard**
```tsx
// components/Credit/CreditAssessment.tsx
export const CreditAssessment: React.FC<{ farmerId: string }> = ({ farmerId }) => {
  const [creditScore, setCreditScore] = useState<CreditScore | null>(null);
  const [loanApplications, setLoanApplications] = useState<LoanApplication[]>([]);
  const [availableLoans, setAvailableLoans] = useState<LoanProduct[]>([]);

  useEffect(() => {
    fetchCreditData();
  }, [farmerId]);

  const applyForLoan = async (loanProductId: string, amount: number) => {
    try {
      const response = await api.post('/api/credit/apply', {
        farmer_id: farmerId,
        loan_product_id: loanProductId,
        requested_amount: amount,
        purpose: 'crop_financing'
      });
      
      toast.success('Loan application submitted successfully');
      fetchCreditData();
    } catch (error) {
      toast.error('Failed to submit loan application');
    }
  };

  return (
    <div className="space-y-6">
      {/* Credit Score Card */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl text-white p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold mb-2">FarmCredit Score</h3>
            <div className="text-5xl font-bold">
              {creditScore?.score || 'N/A'}
            </div>
            <div className="text-blue-100 mt-2">
              {creditScore?.grade || 'Not Assessed'}
            </div>
          </div>
          <div className="text-right">
            <div className="text-blue-100 text-sm">Credit Limit</div>
            <div className="text-2xl font-bold">
              ₹{creditScore?.credit_limit?.toLocaleString() || '0'}
            </div>
            <div className="text-blue-100 text-sm mt-2">
              Interest Rate: {creditScore?.interest_rate || 'N/A'}% p.a.
            </div>
          </div>
        </div>

        {/* Credit Factors */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          {creditScore?.factors.map((factor, index) => (
            <div key={index} className="text-center">
              <div className="text-2xl font-bold">{factor.score}</div>
              <div className="text-blue-100 text-sm">{factor.name}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Available Loans */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold mb-6">💰 Available Loan Products</h3>
        
        <div className="grid md:grid-cols-2 gap-6">
          {availableLoans.map((loan) => (
            <div key={loan.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h4 className="font-semibold text-lg">{loan.name}</h4>
                  <p className="text-gray-600 text-sm">{loan.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500">Interest Rate</div>
                  <div className="text-lg font-bold text-green-600">{loan.interest_rate}%</div>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Loan Amount:</span>
                  <span>₹{loan.min_amount?.toLocaleString()} - ₹{loan.max_amount?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Tenure:</span>
                  <span>{loan.min_tenure} - {loan.max_tenure} months</span>
                </div>
                <div className="flex justify-between">
                  <span>Processing Fee:</span>
                  <span>{loan.processing_fee}%</span>
                </div>
              </div>

              <div className="mt-4 flex space-x-2">
                <button
                  onClick={() => applyForLoan(loan.id, loan.max_amount)}
                  className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
                >
                  Apply Now
                </button>
                <button className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50">
                  Details
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Loan Applications */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold mb-6">📋 Your Loan Applications</h3>
        
        {loanApplications.length > 0 ? (
          <div className="space-y-4">
            {loanApplications.map((application) => (
              <div key={application.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <div className="font-semibold">{application.loan_product_name}</div>
                    <div className="text-sm text-gray-600">
                      Applied on {new Date(application.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                    application.status === 'approved' ? 'bg-green-100 text-green-800' :
                    application.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    application.status === 'rejected' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {application.status.toUpperCase()}
                  </div>
                </div>
                
                <div className="grid md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Amount:</span>
                    <span className="ml-2 font-medium">₹{application.amount?.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Tenure:</span>
                    <span className="ml-2 font-medium">{application.tenure} months</span>
                  </div>
                  <div>
                    <span className="text-gray-600">EMI:</span>
                    <span className="ml-2 font-medium">₹{application.emi?.toLocaleString()}</span>
                  </div>
                </div>

                {application.status === 'approved' && (
                  <div className="mt-4 p-3 bg-green-50 rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="text-green-800 font-medium">Loan Approved!</span>
                      <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                        Accept & Disburse
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No loan applications found. Apply for a loan to get started.
          </div>
        )}
      </div>
    </div>
  );
};
```

### **Week 21-22: Blockchain Traceability**

1. **Farm-to-Fork Traceability**
```tsx
// components/Blockchain/TraceabilityTracker.tsx
export const TraceabilityTracker: React.FC<{ productId: string }> = ({ productId }) => {
  const [traceabilityData, setTraceabilityData] = useState<TraceabilityRecord[]>([]);
  const [qrCode, setQrCode] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTraceabilityData();
  }, [productId]);

  const generateQRCode = async () => {
    try {
      const response = await api.post('/api/blockchain/generate-qr', {
        product_id: productId
      });
      
      setQrCode(response.data.qr_code_url);
      toast.success('QR Code generated successfully');
    } catch (error) {
      toast.error('Failed to generate QR code');
    }
  };

  return (
    <div className="space-y-6">
      {/* Product Journey Map */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold">🔗 Farm-to-Fork Journey</h3>
          <button
            onClick={generateQRCode}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Generate QR Code
          </button>
        </div>

        {/* Timeline */}
        <div className="relative">
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
          
          {traceabilityData.map((record, index) => (
            <div key={record.id} className="relative flex items-start mb-6">
              <div className={`relative z-10 w-8 h-8 rounded-full flex items-center justify-center text-white text-sm ${
                record.verified ? 'bg-green-500' : 'bg-gray-400'
              }`}>
                {record.verified ? '✓' : index + 1}
              </div>
              
              <div className="ml-6 flex-1">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold">{record.stage}</h4>
                      <p className="text-sm text-gray-600">{record.location}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">
                        {new Date(record.timestamp).toLocaleDateString()}
                      </div>
                      <div className="text-xs text-gray-400">
                        {new Date(record.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-700 mb-3">{record.description}</p>
                  
                  {/* Record Details */}
                  <div className="grid md:grid-cols-2 gap-4 text-xs">
                    {record.details.map((detail, idx) => (
                      <div key={idx} className="flex justify-between">
                        <span className="text-gray-600">{detail.key}:</span>
                        <span className="font-medium">{detail.value}</span>
                      </div>
                    ))}
                  </div>

                  {/* Blockchain Hash */}
                  <div className="mt-3 p-2 bg-blue-50 rounded">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-blue-600">Blockchain Hash:</span>
                      <button
                        onClick={() => navigator.clipboard.writeText(record.blockchain_hash)}
                        className="text-xs text-blue-600 hover:text-blue-800"
                      >
                        📋 Copy
                      </button>
                    </div>
                    <div className="text-xs font-mono text-blue-800 break-all">
                      {record.blockchain_hash}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* QR Code Display */}
      {qrCode && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold mb-4">📱 Consumer QR Code</h3>
          <div className="flex items-center space-x-6">
            <div className="flex-shrink-0">
              <img src={qrCode} alt="Traceability QR Code" className="w-48 h-48" />
            </div>
            <div className="flex-1">
              <h4 className="font-semibold mb-2">How it works:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Consumers scan this QR code on the product package</li>
                <li>• They can view the complete farm-to-fork journey</li>
                <li>• All data is verified on the blockchain</li>
                <li>• Builds trust and transparency with customers</li>
                <li>• Enables premium pricing for traceable products</li>
              </ul>
              
              <div className="mt-4 flex space-x-2">
                <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                  Download QR Code
                </button>
                <button className="bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300">
                  Print Labels
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Carbon Footprint Tracker */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold mb-4">🌱 Carbon Footprint Analysis</h3>
        
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">2.4 kg</div>
            <div className="text-sm text-gray-600">CO₂ per kg product</div>
            <div className="text-xs text-green-600 mt-1">30% below average</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">45 km</div>
            <div className="text-sm text-gray-600">Total transport distance</div>
            <div className="text-xs text-blue-600 mt-1">Local sourcing</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">₹2.50</div>
            <div className="text-sm text-gray-600">Carbon credit earned</div>
            <div className="text-xs text-purple-600 mt-1">Per kg sold</div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-green-50 rounded-lg">
          <h4 className="font-semibold text-green-900 mb-2">🏆 Sustainability Achievements</h4>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div className="flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              Zero pesticide residue detected
            </div>
            <div className="flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              Water usage 20% below benchmark
            </div>
            <div className="flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              Solar-powered farm operations
            </div>
            <div className="flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              Biodegradable packaging used
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
```

### **Week 23-24: Testing & Scaling**

#### **Phase 3 Success Metrics:**
- ✅ **2000 farmers** across 5 cities
- ✅ **₹2Cr GMV** monthly (4x growth from Phase 2)
- ✅ **1000 IoT sensors** deployed
- ✅ **₹10Cr loans** disbursed with <2% NPL
- ✅ **100% traceability** for premium products
- ✅ **50,000 consumers** actively using platform
- ✅ **95% uptime** with auto-scaling

---

## 🌟 Phase 4: Community & Expansion (Months 10-12)

### **Objectives:**
- Launch FarmConnect Community platform
- Implement carbon credits marketplace
- Deploy satellite-based crop monitoring
- Scale to 10 cities, 5000 farmers
- Achieve ₹5Cr GMV monthly
- Prepare for Series A funding

---

## 📈 Success Metrics & KPIs by Phase

| Metric | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|--------|---------|---------|---------|---------|
| **Monthly GMV** | ₹10L | ₹50L | ₹2Cr | ₹5Cr |
| **Active Farmers** | 100 | 500 | 2,000 | 5,000 |
| **Active Consumers** | 1,000 | 5,000 | 25,000 | 75,000 |
| **Cities Covered** | 1 | 2 | 5 | 10 |
| **Order Success Rate** | 95% | 97% | 98% | 99% |
| **Customer NPS** | 60 | 70 | 80 | 85 |
| **Agent Response Time** | N/A | <30s | <20s | <15s |
| **AI Accuracy** | N/A | 90% | 95% | 97% |
| **Loans Disbursed** | N/A | N/A | ₹10Cr | ₹50Cr |

---

## 💰 Investment & Revenue Breakdown

### **Phase-wise Investment:**
- **Phase 1:** ₹50L (Team: 6 developers, Infrastructure: Basic)
- **Phase 2:** ₹80L (Team: 8 developers, AI/ML infrastructure)
- **Phase 3:** ₹1Cr (Team: 12 developers, IoT devices, Credit platform)
- **Phase 4:** ₹70L (Team: 15 developers, Marketing, Expansion)
- **Total:** ₹3Cr over 12 months

### **Revenue Projections:**
```
Month 1-2:   ₹10L
Month 3-6:   ₹50L/month
Month 7-9:   ₹2Cr/month
Month 10-12: ₹5Cr/month

Annual Run Rate by Month 12: ₹60Cr
```

### **Unit Economics:**
- **Take Rate:** 8-10% commission
- **Customer Acquisition Cost:** ₹500 (farmer), ₹200 (consumer)
- **Lifetime Value:** ₹25,000 (farmer), ₹8,000 (consumer)
- **Gross Margin:** 65%
- **Break-even:** Month 8

---

## 🚀 Deployment Strategy

### **Infrastructure Evolution:**

#### **Phase 1: Basic Setup**
```yaml
Infrastructure:
  - 2x Application servers (4 vCPU, 16GB RAM)
  - 1x Database server (8 vCPU, 32GB RAM)
  - 1x Redis server (2 vCPU, 8GB RAM)
  - CDN for static assets
  - Basic monitoring (Prometheus + Grafana)

Cost: ~₹50,000/month
```

#### **Phase 2: AI-Enhanced**
```yaml
Infrastructure:
  - 5x Application servers (autoscaling)
  - 1x Database cluster (Primary + Replica)
  - 3x Redis cluster
  - GPU instances for AI processing
  - LangSmith for agent monitoring
  - Advanced monitoring + Alerting

Cost: ~₹2,00,000/month
```

#### **Phase 3: Enterprise Scale**
```yaml
Infrastructure:
  - Kubernetes cluster (10+ nodes)
  - Multi-region deployment
  - Database sharding
  - Message queues (Kafka)
  - ML model serving platform
  - Blockchain nodes
  - IoT data processing pipeline

Cost: ~₹5,00,000/month
```

### **Testing Strategy by Phase:**

#### **Phase 1 Testing:**
- ✅ Unit tests: 90% coverage
- ✅ Integration tests: API endpoints
- ✅ E2E tests: Core user journeys
- ✅ Load testing: 100 concurrent users
- ✅ Manual UAT: 20 test cases

#### **Phase 2 Testing:**
- ✅ Agent unit tests: All agents
- ✅ LangGraph workflow tests
- ✅ Performance tests: <30s response time
- ✅ Load testing: 500 concurrent users
- ✅ Security testing: OWASP compliance
- ✅ Mobile testing: iOS + Android

#### **Phase 3 Testing:**
- ✅ IoT integration tests
- ✅ Blockchain transaction tests  
- ✅ Credit scoring model validation
- ✅ Load testing: 2000 concurrent users
- ✅ Disaster recovery testing
- ✅ Compliance testing: RBI guidelines

---

## 📱 UI/UX Testing Checklist

### **Phase 1 UI Testing:**
```markdown
## Core Marketplace Testing

### Authentication & Onboarding
- [ ] Phone OTP verification works across carriers
- [ ] User type selection (farmer/consumer) persists
- [ ] Profile completion wizard guides users
- [ ] Error states are user-friendly

### Farmer Experience
- [ ] Product listing form validates correctly
- [ ] Image upload works (multiple formats)
- [ ] Inventory management updates real-time
- [ ] Order notifications display properly
- [ ] Dashboard analytics load correctly

### Consumer Experience  
- [ ] Product search returns relevant results
- [ ] Filters work (category, location, organic)
- [ ] Cart management (add/remove/update)
- [ ] Checkout flow completes successfully
- [ ] Order tracking updates in real-time

### Mobile Responsiveness
- [ ] All pages responsive on mobile (320px-1920px)
- [ ] Touch gestures work (swipe, pinch, tap)
- [ ] Forms are mobile-optimized
- [ ] Loading states don't block interaction
```

### **Phase 2 UI Testing:**
```markdown
## AI Agent Integration Testing

### Price Monitoring Dashboard
- [ ] Real-time price updates via WebSocket
- [ ] Price comparison table loads correctly
- [ ] Auto-refresh toggle works
- [ ] Savings calculation accurate
- [ ] Platform logos display correctly

### Quality Inspector
- [ ] Image upload supports drag & drop
- [ ] Multiple image selection works
- [ ] AI analysis progress indicator
- [ ] Quality grades display correctly
- [ ] Recommendations are actionable

### Voice Assistant
- [ ] Microphone access permissions
- [ ] Voice recognition in multiple languages
- [ ] Text-to-speech playback works
- [ ] Transcript editing functionality
- [ ] Response history accessible

### Market Intelligence
- [ ] Charts render correctly (responsive)
- [ ] Time range selection updates data
- [ ] AI insights load dynamically
- [ ] Recommendations actionable
```

### **Phase 3 UI Testing:**
```markdown
## Advanced Features Testing

### IoT Dashboard
- [ ] Real-time sensor data updates
- [ ] Charts responsive to data changes
- [ ] Automation rules configurable
- [ ] Alerts display prominently
- [ ] Historical data accessible

### Credit Platform
- [ ] Credit score displays correctly
- [ ] Loan products comparison table
- [ ] Application form validation
- [ ] Document upload progress
- [ ] Approval status updates

### Blockchain Traceability
- [ ] QR code generation works
- [ ] Journey timeline interactive
- [ ] Blockchain hash verification
- [ ] Carbon footprint calculation
```

---

## 🎯 Go-Live Checklist

### **Pre-Launch (Each Phase):**
```markdown
## Technical Readiness
- [ ] All tests passing (unit, integration, E2E)
- [ ] Performance benchmarks met
- [ ] Security audit completed
- [ ] Database migrations tested
- [ ] Backup & recovery procedures tested
- [ ] Monitoring alerts configured
- [ ] Error tracking setup (Sentry)
- [ ] API rate limiting configured

## Business Readiness  
- [ ] User acceptance testing completed
- [ ] Support documentation created
- [ ] Customer service team trained
- [ ] Legal compliance verified
- [ ] Pricing strategy finalized
- [ ] Marketing materials ready
- [ ] PR strategy planned

## Operational Readiness
- [ ] 24/7 support coverage planned
- [ ] Incident response procedures
- [ ] Scaling procedures documented
- [ ] User onboarding materials
- [ ] Training videos created
- [ ] FAQ sections updated
```

---

## 🏆 Final Success Metrics

By Month 12, FarmConnect will achieve:

### **Scale Metrics:**
- ✅ **5,000 verified farmers** across 10 cities
- ✅ **75,000 active consumers** monthly
- ✅ **₹5Cr GMV** per month
- ✅ **₹60Cr annual run rate**
- ✅ **99% platform uptime**

### **AI Performance:**
- ✅ **97% accuracy** in price monitoring
- ✅ **95% accuracy** in quality grading
- ✅ **<15 seconds** agent response time
- ✅ **85% farmer satisfaction** with AI tools

### **Financial Services:**
- ✅ **₹50Cr total loans** disbursed
- ✅ **<2% NPL ratio** maintained
- ✅ **15% interest rate** average

### **Innovation Metrics:**
- ✅ **1000+ IoT sensors** deployed
- ✅ **100% blockchain traceability** for premium products
- ✅ **50,000 carbon credits** traded

### **Business Impact:**
- ✅ **40% farmer income increase** on average
- ✅ **35% consumer savings** vs retail
- ✅ **Series A ready** (₹50Cr valuation target)

This comprehensive phased implementation plan ensures FarmConnect evolves from a basic marketplace to India's most advanced agricultural technology platform, ready for scale and investment.