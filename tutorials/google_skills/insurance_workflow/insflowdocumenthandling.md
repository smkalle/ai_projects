**🚀 Multimodal Agentic RAG Tutorial: Built with Gemini Embedding 2 + Google ADK**  
*Hands-on guide for AI engineers by a Google L6 AI Technical Product Manager*

Hey folks — I’m a Google L6 AI Technical Product Manager (working on Vertex AI, Agent Development Kit, and multimodal tooling). Shubham Saboo just open-sourced this **Multimodal Agentic RAG** demo in the #1 AI repo on GitHub (`awesome-llm-apps`, 109k+ stars). It’s 100% production-ready starter code that handles **any input** (text, URLs, PDFs, images, audio, video) and delivers **cited, grounded answers** while projecting everything into a **live interactive 3D embedding space** for full transparency.

This is the perfect playground to learn:
- True multimodal embeddings (Gemini Embedding 2)
- Agentic RAG orchestration with **Google ADK**
- Interpretable retrieval via PCA-projected 3D visualization
- Clean separation of retrieval + answer synthesis (same evidence packet used for both)

I’ve turned the fresh README + code into a **complete, zero-to-running, step-by-step tutorial** you can finish in <15 minutes.

### What You’ll Build & See
- Upload **multimodal sources** → they get embedded with Gemini Embedding 2.
- Ask any question → ADK agent retrieves, reasons, and synthesizes a cited answer.
- Watch sources + query projected into a **live 3D PCA embedding space** (cited sources light up).
- Full agent trace (SOURCE_INGESTOR → RETRIEVAL_TOOL → ANSWER_SYNTHESIZER).

(Shubham’s demo video shows exactly this in action — PDFs, URLs, even images like `gemini_agent_skills.png` all work seamlessly.)

### Prerequisites
- Python 3.10+
- Node.js 18+ + npm
- Git
- Google API key (free from [Google AI Studio](https://aistudio.google.com/app/apikey))
- (Optional but recommended) Google Cloud project with Vertex AI API enabled for production use later

### Step 1: Clone the Repository
```bash
git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
cd awesome-llm-apps/rag_tutorials/multimodal_agentic_rag
```

### Step 2: Backend Setup (FastAPI + Gemini + ADK)
```bash
cd backend

# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# 2. Install dependencies (exact from requirements.txt)
pip install -r requirements.txt

# 3. Set your Google API key (Gemini Embedding 2 + ADK)
export GOOGLE_API_KEY="your-google-ai-studio-key-here"

# Optional: Allow private/localhost URLs for testing
# export ALLOW_PRIVATE_URLS=true
```

**Dependencies you’ll get** (FastAPI, Uvicorn, google-genai, google-adk, beautifulsoup4, httpx, python-multipart).

### Step 3: Run the Backend
```bash
python server.py
```
→ Backend starts at **http://localhost:8897**  
You’ll see health check output confirming Gemini Embedding 2 + ADK are ready.

### Step 4: Frontend Setup (React + Vite + 3D viz)
Open a **new terminal** and run:
```bash
cd ../frontend

npm install
npm run dev -- --port 5177
```

(If backend is on a different port/machine, add: `VITE_API_URL=http://localhost:8897 npm run dev -- --port 5177`)

→ Frontend starts at **http://localhost:5177**

### Step 5: Open the App & Start Experimenting
1. Go to **http://localhost:5177** in your browser.
2. **Indexed Sources** panel (left) — shows everything in the in-memory vector store.
3. **Embedding Space** (center) — live 3D PCA plot (7,680+ dimensions → 3D). Each source = one interactive point.
4. **Q&A + Agent Trace + Citations** (right) — where the magic happens.

### Step 6: Hands-On Demo Walkthrough
1. **Add sources** (use the “Add source” panel):
   - **Text**: Paste anything.
   - **URL**: Paste a public article (e.g. `https://theunwindai.com/...`).
   - **File**: Upload PDF, image, audio, or video. (Gemini File API handles multimodal natively — temporary files auto-cleaned.)

2. **Ask a question** in the Q&A panel (example: “What is the new agent governance stack?”).

3. Watch the magic:
   - Retrieval happens (nearest-neighbor in embedding space).
   - ADK agent trace updates in real time.
   - Answer appears **with separate Citations** panel (no ugly [1][2] clutter).
   - In the **3D Embedding Space**: query point appears (often red/orange), cited sources highlight and connect.

4. Click and drag the 3D view — fully interactive. Hover points to see source metadata.

**Pro tip**: Try uploading a mix of PDFs + images + URLs about the same topic. The 3D space makes clustering obvious.

### Architecture Deep Dive (for AI Engineers)
| Layer                  | Component                          | What it does |
|------------------------|------------------------------------|--------------|
| **Frontend**           | React + Vite + Three.js (implied) | Source manager, Q&A, live 3D PCA viz |
| **Backend**            | FastAPI                            | All APIs (/sources, /ask, /space) |
| **Store**              | MultimodalRagStore (in-memory)     | Chunks, embeddings, cosine search, PCA projection |
| **Embeddings**         | Gemini Embedding 2                 | Handles text, image, audio, video, PDF natively |
| **Agent**              | Google ADK agent                   | Coordinates answer synthesis from the **exact same** retrieval packet shown in UI |

Key insight: `/ask` does **one retrieval pass** and passes that exact packet to the ADK agent → perfect grounding + citations.

### Step 7: Explore & Customize the Code
Key files to study:
- `backend/rag_store.py` → embedding logic + PCA projection
- `backend/agentic_rag_agent/agent.py` → ADK agent definition
- `backend/server.py` → FastAPI endpoints
- `frontend/src/App.tsx` → UI + 3D rendering

**Quick customizations you can ship today**:
- Swap in-memory store for a real vector DB (pgvector, Pinecone, etc.)
- Add auth + persistent storage
- Deploy backend on Cloud Run / Vertex AI
- Extend ADK agent with more tools

### Troubleshooting
- No embeddings? Double-check `GOOGLE_API_KEY` is exported **before** starting `server.py`.
- Frontend can’t reach backend? Use `VITE_API_URL=...`
- Private URLs blocked? `export ALLOW_PRIVATE_URLS=true`
- Restart backend → index clears (by design for demo).
- Still stuck? The repo issues + Shubham’s replies on X are very responsive.

### Production-Ready Next Steps (L6 PM Advice)
1. Replace in-memory store with durable vector DB + background jobs.
2. Add eval harness (RAGAS-style) for citation accuracy.
3. Add observability (LangSmith / Vertex AI Agent Engine tracing).
4. Scale embeddings with Vertex AI batch prediction.
5. Turn the ADK agent into a reusable skill for larger agent teams.

You now have a fully working **multimodal agentic RAG** with beautiful 3D interpretability — all in <15 minutes.

**Repo**: https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/rag_tutorials/multimodal_agentic_rag  
**Star it** — it’s the fastest way to level up your RAG game with Google’s latest multimodal stack.

Go build something amazing. Drop your screenshots or custom extensions in the repo — I’ll be watching!  

— Your Google L6 AI TPM (and huge fan of open-source agentic tooling)
