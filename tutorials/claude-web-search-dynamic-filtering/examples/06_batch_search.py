"""
Example 6: Batch Processing with Web Search
=============================================

This example demonstrates using the Messages Batches API with web search
for non-real-time workloads. Batch processing is ideal for:
- Research pipelines that process many queries
- Content indexing and enrichment
- Periodic monitoring and alerting
- Bulk fact-checking and verification

Batch requests have the same pricing as regular requests but offer
better throughput for large-scale operations.
"""

import os
import json
import time
import anthropic
from dotenv import load_dotenv

load_dotenv()


def create_research_batch(queries: list, model: str = "claude-sonnet-4-6"):
    """
    Submit a batch of research queries using the Messages Batches API.

    Each query gets its own independent web search with dynamic filtering.
    Results are processed asynchronously.
    """
    client = anthropic.Anthropic()

    print("=" * 70)
    print(f"BATCH RESEARCH: {len(queries)} queries")
    print("=" * 70)

    # Build batch requests
    requests = []
    for i, query in enumerate(queries):
        request = {
            "custom_id": f"research-{i:04d}",
            "params": {
                "model": model,
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Research the following topic and provide a concise, "
                            f"well-cited summary:\n\n{query}"
                        ),
                    }
                ],
                "tools": [
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "max_uses": 3,
                    }
                ],
            },
        }
        requests.append(request)
        print(f"  [{i}] {query[:60]}...")

    # Submit the batch
    print(f"\nSubmitting batch of {len(requests)} requests...")
    batch = client.batches.create(requests=requests)

    print(f"  Batch ID: {batch.id}")
    print(f"  Status: {batch.processing_status}")

    return batch.id


def poll_batch_status(batch_id: str, poll_interval: int = 30):
    """Poll for batch completion and return results."""
    client = anthropic.Anthropic()

    print(f"\nPolling batch {batch_id}...")

    while True:
        batch = client.batches.retrieve(batch_id)
        status = batch.processing_status

        completed = getattr(batch.request_counts, "succeeded", 0)
        failed = getattr(batch.request_counts, "errored", 0)
        total = getattr(batch.request_counts, "processing", 0) + completed + failed

        print(
            f"  Status: {status} | "
            f"Completed: {completed}/{total} | "
            f"Failed: {failed}"
        )

        if status == "ended":
            break

        time.sleep(poll_interval)

    return batch


def process_batch_results(batch_id: str):
    """Retrieve and process batch results."""
    client = anthropic.Anthropic()

    print(f"\n{'=' * 70}")
    print("BATCH RESULTS")
    print("=" * 70)

    results = []
    total_searches = 0
    total_input_tokens = 0
    total_output_tokens = 0

    # Stream results from the batch
    for result in client.batches.results(batch_id):
        custom_id = result.custom_id

        if result.result.type == "succeeded":
            message = result.result.message

            # Extract text
            text_parts = []
            citations = []
            for block in message.content:
                if block.type == "text":
                    text_parts.append(block.text)
                    if hasattr(block, "citations") and block.citations:
                        for c in block.citations:
                            if hasattr(c, "url"):
                                citations.append({
                                    "url": c.url,
                                    "title": getattr(c, "title", ""),
                                })

            # Track usage
            usage = message.usage
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
            searches = 0
            if hasattr(usage, "server_tool_use") and usage.server_tool_use:
                stu = usage.server_tool_use
                if isinstance(stu, dict):
                    searches = stu.get("web_search_requests", 0)
                else:
                    searches = getattr(stu, "web_search_requests", 0)

            total_searches += searches
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens

            result_data = {
                "custom_id": custom_id,
                "status": "succeeded",
                "text": "".join(text_parts),
                "citations": citations,
                "searches": searches,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            }
            results.append(result_data)

            print(f"\n--- {custom_id} (SUCCESS) ---")
            print(f"  Text: {result_data['text'][:200]}...")
            print(f"  Citations: {len(citations)}")
            print(f"  Searches: {searches} | Tokens: {input_tokens:,} in / {output_tokens:,} out")

        elif result.result.type == "errored":
            error = result.result.error
            print(f"\n--- {custom_id} (ERROR) ---")
            print(f"  Error: {error}")
            results.append({
                "custom_id": custom_id,
                "status": "errored",
                "error": str(error),
            })

    # Summary
    succeeded = sum(1 for r in results if r["status"] == "succeeded")
    failed = sum(1 for r in results if r["status"] == "errored")

    print(f"\n{'=' * 70}")
    print("BATCH SUMMARY")
    print("=" * 70)
    print(f"  Total requests:  {len(results)}")
    print(f"  Succeeded:       {succeeded}")
    print(f"  Failed:          {failed}")
    print(f"  Total searches:  {total_searches}")
    print(f"  Total input:     {total_input_tokens:,} tokens")
    print(f"  Total output:    {total_output_tokens:,} tokens")

    search_cost = (total_searches / 1000) * 10.00
    print(f"  Search cost:     ${search_cost:.4f}")
    print("=" * 70)

    return results


def run_batch_pipeline(queries: list):
    """
    End-to-end batch research pipeline.

    1. Submit queries as a batch
    2. Poll for completion
    3. Process and display results
    """
    # Step 1: Submit
    batch_id = create_research_batch(queries)

    # Step 2: Poll
    poll_batch_status(batch_id)

    # Step 3: Process
    results = process_batch_results(batch_id)

    return results


def create_monitoring_batch(topics: dict):
    """
    Create a monitoring batch that checks multiple topics.

    Useful for:
    - Competitive intelligence monitoring
    - News monitoring for specific topics
    - Regulatory change tracking
    - Technology trend monitoring

    Args:
        topics: dict mapping topic_id to search query
    """
    client = anthropic.Anthropic()

    print("=" * 70)
    print(f"MONITORING BATCH: {len(topics)} topics")
    print("=" * 70)

    requests = []
    for topic_id, query in topics.items():
        request = {
            "custom_id": f"monitor-{topic_id}",
            "params": {
                "model": "claude-sonnet-4-6",
                "max_tokens": 2048,
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Search for the latest news and updates on: {query}\n\n"
                            "Provide:\n"
                            "1. A brief summary of the most significant recent development\n"
                            "2. Whether this represents a major change from the status quo\n"
                            "3. Key sources\n\n"
                            "Keep your response under 300 words."
                        ),
                    }
                ],
                "tools": [
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "max_uses": 2,  # Keep costs low for monitoring
                    }
                ],
            },
        }
        requests.append(request)
        print(f"  [{topic_id}] {query[:60]}...")

    batch = client.batches.create(requests=requests)
    print(f"\n  Batch ID: {batch.id}")
    return batch.id


if __name__ == "__main__":
    # Example 1: Research batch
    research_queries = [
        "Latest developments in large language model efficiency and distillation",
        "Current state of autonomous vehicle regulations in the US and EU",
        "Recent breakthroughs in solid-state battery technology for EVs",
        "Progress on room-temperature superconductor research since 2024",
        "New approaches to AI alignment and safety published in 2025-2026",
    ]

    print("This example demonstrates batch processing with web search.")
    print("It will submit queries to the Batches API and poll for results.")
    print()

    # Uncomment to actually run (will use API credits):
    # results = run_batch_pipeline(research_queries)

    # Example 2: Monitoring batch
    monitoring_topics = {
        "ai-regulation": "AI regulation and governance policy changes",
        "llm-benchmarks": "New LLM benchmark results and model comparisons",
        "ai-infrastructure": "AI infrastructure and GPU availability updates",
        "open-source-ai": "Open source AI model releases and licensing changes",
    }

    # Uncomment to run:
    # batch_id = create_monitoring_batch(monitoring_topics)
    # poll_batch_status(batch_id)
    # results = process_batch_results(batch_id)

    print("Examples are commented out to avoid API charges.")
    print("Uncomment the desired example in __main__ to run it.")
