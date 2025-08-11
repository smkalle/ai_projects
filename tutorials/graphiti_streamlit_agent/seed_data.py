import os
import asyncio
from datetime import datetime, timezone

from dotenv import load_dotenv
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType


async def seed(graph):
    await graph.add_episode(
        name="User_Feedback_1",
        episode_body=(
            "Alice bought Allbirds Wool Runners. She loves the comfort but "
            "complains about durability after 3 months."
        ),
        source=EpisodeType.text,
        source_description="User review from forum",
        reference_time=datetime(2025, 1, 15, 10, 0, tzinfo=timezone.utc),
    )

    await graph.add_episode(
        name="Support_Chat_1",
        episode_body=(
            "Alice: My Allbirds shoes are falling apart.\n"
            "Support: Sorry, Alice. We'll send a replacement."
        ),
        source=EpisodeType.message,
        source_description="Customer support transcript",
        reference_time=datetime(2025, 2, 20, 14, 30, tzinfo=timezone.utc),
    )

    await graph.add_episode(
        name="Product_Update_1",
        episode_body={
            "id": "PROD001",
            "name": "Allbirds Wool Runners",
            "material": "Merino Wool",
            "price": 120.00,
            "in_stock": True,
            "last_updated": "2025-03-01T12:00:00Z",
        },
        source=EpisodeType.json,
        source_description="Product catalog update",
        reference_time=datetime.now(tz=timezone.utc),
    )


async def main():
    load_dotenv()
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    graph = await Graphiti.build(uri, user, password)
    await seed(graph)


if __name__ == "__main__":
    asyncio.run(main())

