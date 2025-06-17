# 🚀 Building Your AI‑Powered Student Research Tool with Gemini & LangGraph

This tutorial guides you through setting up and understanding a **deep‑research** tool that leverages the **Gemini API** and **LangGraph** to create AI agents capable of performing comprehensive web research—complete with citations.  
A **React** frontend handles user interaction, while a **LangGraph‑powered Python** backend does the heavy lifting.

You’ll be working with an **open‑source quick‑start project** that demonstrates:

* Dynamic search‑query generation  
* Iterative refinement of results through reflection  
* Automatic identification of knowledge gaps to provide thorough answers  

---

## 🛠️ Prerequisites

| Requirement | Purpose |
|-------------|---------|
| **Node.js (≥ v18)** & **npm/yarn/pnpm** | Front‑end development |
| **Python (≥ 3.8)** | Back‑end development |
| **Git** | Clone the repository |
| **`GEMINI_API_KEY`** | Access the Gemini API (get one from **[Google AI Studio](https://aistudio.google.com/getting-started)**) |
| **(Optional) Search API keys** | Tavily or Google Search support |
| &nbsp;&nbsp;• `TAVILY_API_KEY` | **[Tavily](https://tavily.com/)** search |
| &nbsp;&nbsp;• `GOOGLE_SEARCH_API_KEY` + `GOOGLE_CSE_ID` | Google Programmable Search |

---

## 📝 Step 1 – Project Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart.git
   cd gemini-fullstack-langgraph-quickstart
   ```

2. **Configure the backend environment**

   ```bash
   cd backend
   cp .env.example .env
   ```

   Edit **`.env`** and add your keys:

   ```dotenv
   GEMINI_API_KEY="YOUR_ACTUAL_API_KEY"

   # Tavily (optional)
   TAVILY_API_KEY="YOUR_TAVILY_API_KEY"

   # LangSmith (optional but recommended)
   LANGCHAIN_TRACING_V2="true"
   LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
   LANGCHAIN_API_KEY="YOUR_LANGSMITH_API_KEY"
   LANGCHAIN_PROJECT="gemini-fullstack-langgraph-quickstart"
   ```

   > **Tip:** Confirm which search API is used in `backend/app/agent.py` and set only the variables you need.

3. **Install backend dependencies**

   ```bash
   pip install .
   ```

4. **Install frontend dependencies**

   ```bash
   cd ../frontend
   npm install
   ```

---

## 🏃‍♂️ Step 2 – Running the Development Environment

From the project root you can launch both services at once:

```bash
make dev
```

**Or run them in separate terminals:**

* **Backend (LangGraph)**  
  ```bash
  cd backend
  langgraph dev        # default → http://localhost:8000
  ```

* **Frontend (React + Vite)**  
  ```bash
  cd frontend
  npm run dev          # default → http://localhost:5173
  ```

---

## 🏛️ Step 3 – Understanding the Architecture

### Frontend (React)

* Presents a form for research queries  
* Shows the AI‑generated answer **with citations**

### Backend (Python + LangGraph)

* Uses **Gemini** models for language reasoning  
* Builds a **stateful, multi‑agent graph** with **LangGraph**

### How the Agents Collaborate

1. **Query Generation Agent** → crafts search queries  
2. **Web Searching Agent** → calls Tavily/Google Search  
3. **Result Analysis Agent** → extracts facts & detects gaps  
4. **Query Refinement Agent** → improves queries when needed  
5. **Answer Compilation Agent** → synthesises a cited answer  
6. **Supervisor Agent** → routes control between the above agents

---

## ⚙️ Step 4 – Deep Dive into the Backend (Conceptual)

```python
# backend/app/workflow.py  (illustrative)
from langgraph.graph import StateGraph, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List

class ResearchState(TypedDict):
    user_query: str
    search_queries: List[str]
    # … other fields

workflow = StateGraph(ResearchState)

# — Nodes -----------------------------------------------------------
workflow.add_node("query_generator", generate_queries_node)
workflow.add_node("web_searcher", search_web_node)
workflow.add_node("query_refiner", refine_queries_node)
workflow.add_node("answer_compiler", compile_answer_node)

# — Edges -----------------------------------------------------------
workflow.set_entry_point("query_generator")

workflow.add_edge("query_generator", "web_searcher")

# Decide dynamically whether to refine or compile
workflow.add_conditional_edges(
    "web_searcher",
    should_refine_or_compile,   # returns "refine" / "compile" / "__end__"
    {
        "refine": "query_refiner",
        "compile": "answer_compiler",
        "__end__": "__end__"
    }
)

app = workflow.compile()
```

### Gemini Integration

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")

prompt = ChatPromptTemplate.from_template(
    "Generate three diverse search queries for the topic: '{topic}'"
)

query_generation_chain = prompt | llm
response = query_generation_chain.invoke({"topic": user_query})
```

---

## 🔗 Step 5 – Frontend Integration (Conceptual)

The backend is served with **LangServe**, exposing `/research_agent/invoke`.

```tsx
// frontend/src/ResearchComponent.tsx (excerpt)
const apiUrl = "http://localhost:8000/research_agent/invoke";

const response = await fetch(apiUrl, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ input: { user_query: query } })
});
const data = await response.json();
setResult(data.output);
```

---

## 🧪 Step 6 – Using & Testing the Tool

1. Ensure both servers are running (`make dev`).  
2. Open **http://localhost:5173** in your browser.  
3. Enter a query like **“latest advancements in quantum computing”**.  
4. Wait for processing and review the answer & citations.

---

## 📦 Step 7 – Deployment (Optional via Docker)

```bash
# Build the image
docker build -t gemini-fullstack-langgraph -f Dockerfile .

# Launch with Docker Compose (requires populated backend/.env)
docker-compose up --build
```

The app will be available on the port specified in **docker-compose.yml** (e.g., `http://localhost:8080`).

---

## 🔧 Step 8 – Customization Ideas

* **Modify agents** – fine‑tune prompts or logic  
* **Add tools** – PDF readers, ArXiv API, database connectors  
* **Bring your data** – academic DBs, internal knowledge bases  
* **Polish the UI** – richer result views, feedback widgets  

---

## ⚠️ Important Considerations

* **Gemini API quotas** – monitor limits in Google Cloud Console.  
* **Search API costs** – Tavily / Google Programmable Search have their own pricing.  
* **Monitoring** – enable **LangSmith** via environment variables for tracing.

---

## 🎉 Conclusion

You now have a working scaffold for an AI‑powered deep‑research assistant.  
Build on it—add new agents, integrate fresh data sources, and craft specialised tools for students and researchers.

---

## 📚 Key Resources

* **GitHub repo** – `gemini-fullstack-langgraph-quickstart`  
* **LangGraph docs** – https://python.langgraph.org  
* **Google AI Studio** – https://aistudio.google.com  
* **LangSmith** – https://smith.langchain.com  
* **Google Cloud Console – Quotas** – https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
