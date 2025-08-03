from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .tools import search_books, handoff
import os
from dotenv import load_dotenv

load_dotenv()

model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
model = ChatOpenAI(model=model_name)

PUBLISHING_PROMPT = """
You are the Publishing agent. Use search_books for book queries.
If the user asks for TV, films, or documentaries -> hand off to 'broadcasting'.
If the user asks for news or journalism -> hand off to 'news'.
Always explain why you handed off in one short sentence.
"""

publishing_agent = create_react_agent(
    model,
    tools=[search_books, handoff],
    prompt=PUBLISHING_PROMPT,
)
