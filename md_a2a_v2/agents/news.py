from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .tools import search_news, handoff
import os
from dotenv import load_dotenv

load_dotenv()

model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
model = ChatOpenAI(model=model_name)

NEWS_PROMPT = """
You are the News agent. Use search_news for journalism.
If it's books -> 'publishing'. If it's TV -> 'broadcasting'.
"""

news_agent = create_react_agent(
    model,
    tools=[search_news, handoff],
    prompt=NEWS_PROMPT,
)
