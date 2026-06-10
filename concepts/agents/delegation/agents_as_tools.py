import asyncio
import os

from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool


load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")


@function_tool
def display_info(body: str) -> dict[str, str]:
    """Display the security analysis in markdown format.

    Args:
        body: The markdown content to display.

    Returns:
        A status dict.
    """
    print(f"\n{'=' * 60}\n{body}\n{'=' * 60}\n")
    return {"status": "success"}


async def main() -> None:
    """Run the agents-as-tools pattern: orchestrator calls subagents as function tools."""
    instructions1 = (
        "You are a pedantic security expert. You provide detailed information about "
        "the python environment and focus on security implications of the packages used. "
        "You write detailed and technical cold summaries."
    )

    instructions2 = (
        "You are a sarcastic security expert. You provide cursory information about "
        "the python environment and make sarcastic comments about the security "
        "implications of the packages used. You write sarcastic and witty cold summaries."
    )

    instructions3 = (
        "You are a helpful security expert. You provide detailed information about the "
        "python environment and focus on security implications of the packages used. "
        "You write short funny summaries that are easy to understand for non technical people."
    )

    pedantic = Agent(
        name="transfer_to_pedantic_security_agent",
        instructions=instructions1,
        model="gpt-4o-mini",
        handoff_description="Pedantic Security Agent that generates pedantic security summaries",
    )

    sarcastic = Agent(
        name="transfer_to_sarcastic_security_agent",
        instructions=instructions2,
        model="gpt-4o-mini",
        handoff_description="Sarcastic Security Agent that generates sarcastic security summaries",
    )

    helpful = Agent(
        name="transfer_to_helpful_security_agent",
        instructions=instructions3,
        model="gpt-4o-mini",
        handoff_description="Helpful Security Agent that generates helpful security summaries",
    )

    pedantic_tool = pedantic.as_tool(
        tool_name="pedantic_expert",
        tool_description="Generates a pedantic, technical security summary",
    )
    sarcastic_tool = sarcastic.as_tool(
        tool_name="sarcastic_expert",
        tool_description="Generates a sarcastic, witty security summary",
    )
    helpful_tool = helpful.as_tool(
        tool_name="helpful_expert",
        tool_description="Generates a short, funny security summary for non-technical people",
    )

    orchestrator = Agent(
        name="orchestrator",
        instructions=(
            "You are an orchestrator. Call all three security experts and then use "
            "display_info to show the one you find most useful."
        ),
        model="gpt-4o-mini",
        tools=[pedantic_tool, sarcastic_tool, helpful_tool, display_info],
    )

    message = (
        "Write a short sarcastic security summary for a python project that uses the "
        "following packages: flask, requests, numpy, pandas, scikit-learn. The summary "
        "should be in markdown format and should be less than 200 words."
    )

    with trace("Agents as Tools"):
        result = await Runner.run(orchestrator, message)
        print(f"Final: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
