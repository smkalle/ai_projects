from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .tools import search_tv, handoff
import os

model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
model = ChatOpenAI(model=model_name)

BROADCASTING_PROMPT = """
You are the Broadcasting agent. Use search_tv for TV/films/docs.
If it's books -> hand off to 'publishing'. If it's news -> 'news'.
"""

broadcasting_agent = create_react_agent(
    model,
    tools=[search_tv, handoff],
    prompt=BROADCASTING_PROMPT,
)
