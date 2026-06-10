import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    trace,
)


load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

deepseek_client = AsyncOpenAI(base_url=DEEPSEEK_BASE_URL, api_key=deepseek_api_key)
groq_client = AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=groq_api_key)
open_ai_client = AsyncOpenAI(api_key=openai_api_key)

deepseek_model = OpenAIChatCompletionsModel(
    model="deepseek-chat", openai_client=deepseek_client
)
gpt4o_mini_model = OpenAIChatCompletionsModel(
    model="gpt-4o-mini", openai_client=open_ai_client
)
llama3_3_model = OpenAIChatCompletionsModel(
    model="llama-3.3-70b-versatile", openai_client=groq_client
)
gpt4o_model = OpenAIChatCompletionsModel(
    model="gpt-4o", openai_client=open_ai_client
)


@function_tool
def visualize_architectures(output: str) -> dict[str, str]:
    """Display a given string as Markdown.

    Args:
        output: The markdown content to display.

    Returns:
        A status dict.
    """
    print(f"\n{'=' * 60}\n{output}\n{'=' * 60}\n")
    return {"status": "success"}


async def main() -> None:
    """Run the supervisor pattern: 3 architects + visualizer, coordinated by orchestrator."""
    architect_one_prompt = (
        "You are a software architect that loves builder patterns and clean domain design. "
        "Design software architectures that are scalable, maintainable, and easy to "
        "understand. Use best practices and design patterns. Consider end-user needs "
        "and business requirements."
    )
    architect_two_prompt = (
        "You are a software architect that loves domain separation and clearly layered "
        "software. Validation should only be done once. Items should be immutable when possible."
    )
    architect_three_prompt = (
        "You are a young developer and love new patterns and new approaches."
    )

    architect_one = Agent(
        "Deep Seek Architect",
        instructions=architect_one_prompt,
        model=deepseek_model,
    )
    architect_two = Agent(
        "Gemini Architect",
        instructions=architect_two_prompt,
        model=gpt4o_mini_model,
    )
    architect_three = Agent(
        "Groq Architect",
        instructions=architect_three_prompt,
        model=llama3_3_model,
    )

    task = (
        "Design a clean architectural solution to store requests in a database "
        "so they can be retried later (in case things fail)"
    )

    architect_one_tool = architect_one.as_tool(
        tool_name="architect_one", tool_description=task
    )
    architect_two_tool = architect_two.as_tool(
        tool_name="architect_two", tool_description=task
    )
    architect_three_tool = architect_three.as_tool(
        tool_name="architect_three", tool_description=task
    )

    visualizer = Agent(
        name="Visualizer",
        instructions=(
            "You are a software architecture visualizer. Display ideas in a well "
            "structured output in markdown format. Your diagrams are in mermaid format."
        ),
        model=gpt4o_mini_model,
        tools=[visualize_architectures],
        handoff_description="Convert a given document to markdown and display it",
    )

    orchestrator = Agent(
        name="Orchestrator",
        model=gpt4o_model,
        instructions=(
            "You are a supervisor that loves to delegate tasks to others. "
            "You have three software architects that should discuss issues regarding "
            "software architectures. They should find a good solution by interacting "
            "with each other. Although architect_one is the most senior, you also want "
            "to give the youngest architect (architect_three) a chance to have a say. "
            "Once the architects have provided their designs, you MUST hand off the "
            "final consolidated design to the visualizer to display it. "
            "DO NOT display it yourself."
        ),
        tools=[architect_one_tool, architect_two_tool, architect_three_tool],
        handoffs=[visualizer],
    )

    message = (
        "Create clean architectural designs for a request storage. This storage is "
        "intended to store requests for another execution in case they failed."
    )

    with trace("architecture standoff"):
        result = await Runner.run(orchestrator, message)
        print(f"Final: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
