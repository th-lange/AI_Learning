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


def create_experts() -> tuple[Agent, Agent, Agent, Agent]:
    """Create three security expert agents and a picker agent.

    Returns:
        A tuple of (pedantic_agent, sarcastic_agent, helpful_agent, picker_agent).
    """
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
        name="Pedantic Security Agent",
        instructions=instructions1,
        model="gpt-4o-mini",
    )

    sarcastic = Agent(
        name="Sarcastic Security Agent",
        instructions=instructions2,
        model="gpt-4o-mini",
    )

    helpful = Agent(
        name="Helpful Security Agent",
        instructions=instructions3,
        model="gpt-4o-mini",
    )

    picker = Agent(
        name="security_picker",
        instructions=(
            "You pick the best security expert to answer the question. "
            "Choose between Pedantic Security Agent, Sarcastic Security Agent, "
            "and Helpful Security Agent. Do not give an explanation; reply with "
            "the selected output only and use display_info to send the output."
        ),
        model="gpt-4o-mini",
        tools=[display_info],
    )

    return pedantic, sarcastic, helpful, picker


async def main() -> None:
    """Run the fan-out + picker pattern: 3 experts in parallel, picker selects best."""
    pedantic, sarcastic, helpful, picker = create_experts()

    message = (
        "Write a short security summary for a python project that uses the following "
        "packages: flask, requests, numpy, pandas, scikit-learn. The summary should be "
        "in markdown format and should be less than 200 words."
    )

    with trace("Selection from security experts"):
        results = await asyncio.gather(
            Runner.run(pedantic, message),
            Runner.run(sarcastic, message),
            Runner.run(helpful, message),
        )

        outputs = [result.final_output for result in results]
        best = await Runner.run(picker, "".join(outputs))
        print(f"Picker selected: {best.final_output[:200]}...")


if __name__ == "__main__":
    asyncio.run(main())
