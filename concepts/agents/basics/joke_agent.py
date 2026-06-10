import asyncio
import os

from dotenv import load_dotenv
from agents import Agent, Runner, trace


load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")


async def main() -> None:
    """Create and run a basic joke-telling agent."""
    agent = Agent(
        name="Jokester",
        instructions="You are a joke teller. Tell a short, funny joke.",
        model="gpt-4o-mini",
    )

    with trace("Telling a joke"):
        result = await Runner.run(agent, "Tell a joke about Autonomous AI Agents")
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
