# 🚀 Building Your AI-Powered Student Research Tool with Gemini & LangGraph

This tutorial guides you through setting up and understanding a "deep research" tool. This tool leverages the power of the **Gemini API** and **LangGraph** to create AI agents capable of performing comprehensive web research, complete with citations. It features a **React frontend** for user interaction and a **LangGraph-powered Python backend** for the heavy lifting.

You'll be working with an open-source quickstart project that demonstrates dynamic search query generation, iterative refinement of results through reflection, and the identification of knowledge gaps to provide thorough answers.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed and configured:

* **Node.js and npm** (or yarn/pnpm): For frontend development (Node.js v18 or higher recommended).
* **Python**: Version 3.8 or higher for backend development.
* **Git**: For cloning the project repository.
* **GEMINI_API_KEY**: You'll need an API key for the Gemini API. You can obtain one from [Google AI Studio](https://aistudio.google.com/getting-started).
* **(Optional) Search API Keys**: The project may use Tavily or Google Search.
    * **Tavily API Key**: Get from the [Tavily website](https://tavily.com/).
    * **Google Search API Key & Custom Search Engine ID**: Set up via the [Google Cloud Console](https://console.cloud.google.com/).

---

## 📝 Step 1: Project Setup

Let's get the project code and configure your environment.

1.  **Clone the Repository**
    Open your terminal and clone the quickstart repository:
    ```bash
    git clone [https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart.git](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart.git)
    cd gemini-fullstack-langgraph-quickstart
    ```

2.  **Configure Backend Environment**
    Navigate to the backend directory:
    ```bash
    cd backend
    ```
    Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
    Now, open the `.env` file with a text editor and add your `GEMINI_API_KEY` and any other required keys:
    ```plaintext
    GEMINI_API_KEY="YOUR_ACTUAL_API_KEY"
    
    # If using Tavily for search
    TAVILY_API_KEY="YOUR_TAVILY_API_KEY"

    # If you're using LangSmith for monitoring (optional but recommended)
    LANGCHAIN_TRACING_V2="true"
    LANGCHAIN_ENDPOINT="[https://api.smith.langchain.com](https://api.smith.langchain.com)"
    LANGCHAIN_API_KEY="YOUR_LANGSMITH_API_KEY"
    LANGCHAIN_PROJECT="gemini-fullstack-langgraph-quickstart"
    ```
    > **Note**: Check the backend code (e.g., in `backend/app/agent.py`) to confirm which search API is being used and what environment variables are expected.

3.  **Install Backend Dependencies**
    While still in the `backend` directory, install the required Python packages:
    ```bash
    pip install .
    ```

4.  **Install Frontend Dependencies**
    Navigate to the frontend directory:
    ```bash
    cd ../frontend
    ```
    Install the Node.js dependencies:
    ```bash
    npm install
    ```

---

## 🏃‍♂️ Step 2: Running the Development Environment

With the setup complete, you can run the frontend and backend servers. The project includes a `Makefile` for convenience.

To start both backend and frontend development servers concurrently, run this command from the project's root directory:
```bash
make dev
