import asyncio
import os

from dotenv import load_dotenv
from agents import (
    Agent,
    GuardrailFunctionOutput,
    Runner,
    output_guardrail,
)
from pydantic import BaseModel


load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")


class CallbackRequested(BaseModel):
    """Structured output for the callback guardrail agent."""

    callback_requested: bool
    callback_time: str


@output_guardrail()
async def no_callback_guardrail(
    ctx: object, agent: Agent, output_data: CallbackRequested
) -> GuardrailFunctionOutput:
    """Guardrail that trips when the user does NOT want a callback.

    Args:
        ctx: The run context.
        agent: The agent that produced the output.
        output_data: The structured output from the agent.

    Returns:
        GuardrailFunctionOutput with tripwire triggered if no callback was requested.
    """
    print(f"callback_requested={output_data.callback_requested} "
          f"callback_time='{output_data.callback_time}'")

    no_callback = not output_data.callback_requested

    return GuardrailFunctionOutput(
        output_info={"no_callback_requested": output_data.callback_time},
        tripwire_triggered=no_callback,
    )


async def main() -> None:
    """Run the guardrail agent and demonstrate tripwire behavior."""
    message = (
        "Hey guys - please leave me alone for now - I don't want to be contacted"
    )

    guardrail_agent = Agent(
        name="Callback Agent",
        instructions="Check if the user wants to be called back and at what time.",
        output_type=CallbackRequested,
        model="gpt-4o-mini",
        output_guardrails=[no_callback_guardrail],
    )

    try:
        result = await Runner.run(guardrail_agent, message)
        print(f"Result: {result.final_output}")
    except Exception as e:
        print(f"Guardrail tripped: {e}")


if __name__ == "__main__":
    asyncio.run(main())
