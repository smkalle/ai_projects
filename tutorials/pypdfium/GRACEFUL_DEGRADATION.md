# 🛡️ Graceful Degradation

Energy Document AI is designed to handle missing components gracefully, ensuring the system remains functional even when some services are unavailable.

## 🔄 System Behavior Without Components

### Without Qdrant Vector Database

**Status**: ⚠️ Limited Functionality  
**What Works**:
- ✅ UI loads and displays properly
- ✅ API endpoints respond (with appropriate error codes)
- ✅ Document upload interface remains accessible
- ✅ System status monitoring
- ✅ Configuration management

**What's Limited**:
- ❌ Document storage (processed but not saved)
- ❌ Vector similarity search
- ❌ Document retrieval for queries
- ❌ Chat history search

**User Experience**:
- Clear warning banners in UI
- Disabled query functionality with explanatory messages
- System status shows "Vector database unavailable"
- API returns 503 errors for search/query endpoints

### Without OpenAI API Key

**Status**: ⚠️ Limited Functionality  
**What Works**:
- ✅ UI and API remain functional
- ✅ Document upload interface
- ✅ System monitoring

**What's Limited**:
- ❌ Text embeddings generation
- ❌ Document semantic search
- ❌ AI-powered query processing

**User Experience**:
- Warning about missing embeddings
- Instructions to configure API key
- System status shows "OpenAI embeddings unavailable"

### Without Both Components

**Status**: 📱 Demo Mode  
**What Works**:
- ✅ UI displays properly with modern design
- ✅ API endpoints for health checks and status
- ✅ Configuration and help documentation
- ✅ File validation utilities

**User Experience**:
- Clear instructions on what needs to be configured
- Links to setup documentation
- Professional error messages with solutions

## 🎛️ Status Indicators

### UI Status Indicators

The sidebar shows real-time status:
```
📊 Document Stats
⚠️ Vector database unavailable
ℹ️ Documents can be processed but not stored or searched

🔧 System Info
Database: ❌ Disconnected
Embeddings: ❌ Not configured
```

### API Status Codes

| Endpoint | No Qdrant | No API Key | Response |
|----------|-----------|------------|----------|
| `/health` | 200 | 200 | Always healthy |
| `/health/detailed` | 200 | 200 | Shows degraded status |
| `/status` | 200 | 200 | Returns limited status |
| `/query` | 503 | 503 | Service unavailable |
| `/documents/search` | 503 | 503 | Service unavailable |
| `/documents/upload` | 200* | 503 | *Processes but doesn't store |

## 🔧 Recovery Process

### Starting from Minimal Setup

1. **Clone and Basic Setup**
   ```bash
   git clone <repo> && cd pypdfium
   ./start.sh  # Choose option 1 (UI only)
   ```
   Result: UI accessible, shows what's needed

2. **Add Qdrant Database**
   ```bash
   ./start.sh  # Choose option 5 (Start Qdrant)
   ```
   Result: Vector storage available, embeddings still needed

3. **Add OpenAI API Key**
   ```bash
   nano .env  # Add OPENAI_API_KEY=your-key
   ./start.sh  # Restart application
   ```
   Result: Full functionality restored

### Troubleshooting Components

#### Check Qdrant Status
```bash
curl http://localhost:6333/health
# or
docker ps | grep qdrant
```

#### Check API Configuration
```bash
# Via API
curl http://localhost:8000/health/detailed

# Via UI
# Check sidebar "System Info" section
```

#### Restart Individual Components
```bash
# Restart Qdrant only
./start_qdrant.sh  # or ./start_qdrant_termux.sh

# Restart application
./start.sh  # Choose option 7 (Restart), then option 1
```

## 🎯 Design Principles

### 1. **Fail Gracefully**
- No crashes when components are missing
- Clear error messages with solutions
- UI remains usable for configuration

### 2. **Progressive Enhancement**
- Basic functionality always available
- Features unlock as components come online
- Real-time status updates

### 3. **Clear Communication**
- Status indicators in both UI and API
- Specific error messages
- Actionable instructions

### 4. **Easy Recovery**
- Single commands to start missing components
- Automatic detection when services come online
- No manual configuration needed for most setups

## 📊 Monitoring and Alerts

### Health Check Endpoints

- **Basic**: `GET /health` - Always returns 200
- **Detailed**: `GET /health/detailed` - Component status
- **System**: `GET /status` - Statistics and operational status

### UI Monitoring

- Real-time status in sidebar
- Warning banners when functionality is limited
- Progress indicators during component startup

This design ensures Energy Document AI provides value at every stage of setup, from initial installation to full deployment! 🚀