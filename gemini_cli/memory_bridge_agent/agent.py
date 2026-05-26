"""ADK agent entry point for Memory Bridge."""

from google.adk.agents.llm_agent import Agent

from .tools import create_memory_bridge_kit


root_agent = Agent(
    model="gemini-3-flash-preview",
    name="memory_bridge_agent",
    description="Creates caregiver-reviewed memory and orientation support kits.",
    instruction="""You create non-clinical Memory Bridge kits for caregivers.
When the user provides a local profile path, validate the profile first.
Never provide diagnosis, prognosis, medication advice, emergency guidance,
or claims about improving cognition. Always call create_memory_bridge_kit for
a profile path and report the output directory, evaluation status, and caregiver
review requirement.""",
    tools=[create_memory_bridge_kit],
)

memory_bridge_agent = root_agent
