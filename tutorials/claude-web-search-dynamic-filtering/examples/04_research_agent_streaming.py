"""
Example 4: Multi-Turn Research Agent with Streaming
=====================================================

This example builds a conversational research agent that:
1. Streams results in real-time so users see progress
2. Handles multi-turn conversations with context
3. Gracefully handles pause_turn for long research tasks
4. Uses prompt caching to reduce costs across turns
5. Extracts and displays citations properly

This is the pattern you'd use for a production research assistant.
"""

import os
import sys
import anthropic
from dotenv import load_dotenv

load_dotenv()

# Configuration
MODEL = "claude-opus-4-6"
MAX_TOKENS = 16384
BETA_HEADERS = ["code-execution-web-tools-2026-02-09"]

TOOLS = [
    {
        "type": "web_search_20260209",
        "name": "web_search",
        "max_uses": 8,
    },
    {
        "type": "web_fetch_20260209",
        "name": "web_fetch",
        "max_uses": 5,
        "max_content_tokens": 50000,
        "citations": {"enabled": True},
    },
]

SYSTEM_PROMPT = (
    "You are an expert research assistant. When asked to research a topic:\n"
    "1. Search for the most authoritative and recent sources\n"
    "2. Fetch and analyze key documents when needed\n"
    "3. Cross-reference information across multiple sources\n"
    "4. Provide a well-structured response with proper citations\n"
    "5. Note any uncertainties or conflicting information\n"
    "Be thorough but concise. Prioritize quality of sources over quantity."
)


class ResearchAgent:
    """A multi-turn research agent with streaming and citation tracking."""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.messages = []
        self.all_citations = []
        self.turn_count = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_searches = 0
        self.total_fetches = 0

    def research(self, query: str) -> str:
        """
        Execute a research query with streaming output.
        Returns the full text response.
        """
        self.turn_count += 1
        print(f"\n{'=' * 70}")
        print(f"TURN {self.turn_count}: {query}")
        print("=" * 70)

        # Add user message
        user_message = {"role": "user", "content": query}

        # Add cache_control on follow-up turns to cache previous search results
        if self.turn_count > 1:
            user_message["cache_control"] = {"type": "ephemeral"}

        self.messages.append(user_message)

        # Run the query (may loop for pause_turn)
        full_response_text = self._execute_with_streaming()
        return full_response_text

    def _execute_with_streaming(self) -> str:
        """Execute the query with streaming, handling pause_turn."""
        full_text = []

        while True:
            response_text, stop_reason = self._stream_single_turn()
            full_text.append(response_text)

            if stop_reason == "end_turn":
                break
            elif stop_reason == "pause_turn":
                print("\n[Research continuing...]")
                # The assistant content was already added in _stream_single_turn
                self.messages.append({
                    "role": "user",
                    "content": "Continue your research.",
                })
            else:
                print(f"\n[Unexpected stop: {stop_reason}]")
                break

        return "".join(full_text)

    def _stream_single_turn(self) -> tuple:
        """
        Stream a single turn, collecting text and handling events.
        Returns (text, stop_reason).
        """
        collected_text = []
        collected_content = []
        stop_reason = "end_turn"

        try:
            with self.client.beta.messages.stream(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                betas=BETA_HEADERS,
                system=SYSTEM_PROMPT,
                messages=self.messages,
                tools=TOOLS,
            ) as stream:
                current_block_type = None

                for event in stream:
                    if event.type == "content_block_start":
                        block = event.content_block
                        current_block_type = block.type

                        if block.type == "text":
                            pass  # Text will come via deltas
                        elif block.type == "server_tool_use":
                            name = getattr(block, "name", "unknown")
                            sys.stdout.write(f"\n  [{name}] ")
                            sys.stdout.flush()

                    elif event.type == "content_block_delta":
                        delta = event.delta
                        if hasattr(delta, "type"):
                            if delta.type == "text_delta":
                                sys.stdout.write(delta.text)
                                sys.stdout.flush()
                                collected_text.append(delta.text)
                            elif delta.type == "input_json_delta":
                                # Tool input being streamed (e.g., search query)
                                sys.stdout.write(".")
                                sys.stdout.flush()

                    elif event.type == "content_block_stop":
                        current_block_type = None

                    elif event.type == "message_stop":
                        pass

                # Get the final message for context and metadata
                final_message = stream.get_final_message()
                stop_reason = final_message.stop_reason

                # Extract citations from the final message
                for block in final_message.content:
                    if block.type == "text" and hasattr(block, "citations") and block.citations:
                        for c in block.citations:
                            citation_info = {}
                            if hasattr(c, "url"):
                                citation_info = {
                                    "url": c.url,
                                    "title": getattr(c, "title", ""),
                                    "cited_text": getattr(c, "cited_text", ""),
                                }
                            elif hasattr(c, "document_title"):
                                citation_info = {
                                    "title": c.document_title,
                                    "cited_text": getattr(c, "cited_text", ""),
                                }
                            if citation_info:
                                self.all_citations.append(citation_info)

                # Track usage
                usage = final_message.usage
                self.total_input_tokens += usage.input_tokens
                self.total_output_tokens += usage.output_tokens

                if hasattr(usage, "server_tool_use") and usage.server_tool_use:
                    stu = usage.server_tool_use
                    if isinstance(stu, dict):
                        self.total_searches += stu.get("web_search_requests", 0)
                        self.total_fetches += stu.get("web_fetch_requests", 0)
                    else:
                        self.total_searches += getattr(stu, "web_search_requests", 0)
                        self.total_fetches += getattr(stu, "web_fetch_requests", 0)

                cache_read = getattr(usage, "cache_read_input_tokens", 0)
                if cache_read:
                    print(f"\n  [Cache hit: {cache_read:,} tokens]")

                # Add assistant response to conversation history
                self.messages.append({
                    "role": "assistant",
                    "content": final_message.content,
                })

        except anthropic.APIError as e:
            print(f"\n[API Error: {e}]")
            collected_text.append(f"\n[Error: {e}]")

        return "".join(collected_text), stop_reason

    def print_session_summary(self):
        """Print a summary of the entire research session."""
        print(f"\n{'=' * 70}")
        print("SESSION SUMMARY")
        print("=" * 70)
        print(f"  Turns:         {self.turn_count}")
        print(f"  Input tokens:  {self.total_input_tokens:,}")
        print(f"  Output tokens: {self.total_output_tokens:,}")
        print(f"  Web searches:  {self.total_searches}")
        print(f"  Web fetches:   {self.total_fetches}")

        if self.all_citations:
            # Deduplicate by URL
            seen_urls = set()
            unique_citations = []
            for c in self.all_citations:
                url = c.get("url", c.get("title", ""))
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_citations.append(c)

            print(f"\n  Unique sources cited: {len(unique_citations)}")
            for i, c in enumerate(unique_citations, 1):
                title = c.get("title", "Untitled")
                url = c.get("url", "")
                print(f"    [{i}] {title}")
                if url:
                    print(f"        {url}")
        print("=" * 70)


def run_interactive_session():
    """Run an interactive research session."""
    agent = ResearchAgent()

    print("=" * 70)
    print("INTERACTIVE RESEARCH AGENT")
    print("Type your research questions. Type 'quit' to exit.")
    print("Type 'summary' to see session statistics.")
    print("=" * 70)

    while True:
        try:
            query = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not query:
            continue
        if query.lower() == "quit":
            break
        if query.lower() == "summary":
            agent.print_session_summary()
            continue

        agent.research(query)

    agent.print_session_summary()


def run_scripted_research():
    """Run a scripted multi-turn research session for demonstration."""
    agent = ResearchAgent()

    # Turn 1: Initial research
    agent.research(
        "What are the most promising approaches to achieving AGI, "
        "according to leading AI researchers? Focus on recent papers "
        "and statements from 2025-2026."
    )

    # Turn 2: Follow-up (benefits from prompt caching)
    agent.research(
        "Based on what you found, which approach has the strongest "
        "empirical evidence? Are there any benchmarks or metrics "
        "that show clear progress?"
    )

    # Turn 3: Specific deep dive
    agent.research(
        "Tell me more about the scaling laws research. What are the "
        "latest findings on whether scaling alone is sufficient?"
    )

    agent.print_session_summary()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive_session()
    else:
        run_scripted_research()
