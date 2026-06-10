import argparse
import asyncio
import os

from dotenv import load_dotenv
from agents import Agent, ModelSettings, Runner, function_tool, trace


load_dotenv(override=True)
SHELL_AUTO_APPROVE = os.environ.get("SHELL_AUTO_APPROVE") == "1"


async def prompt_shell_approval(command: str) -> bool:
    """Prompt the user to approve a shell command.

    Args:
        command: The shell command pending approval.

    Returns:
        True if the user approved, False otherwise.
    """
    if SHELL_AUTO_APPROVE:
        return True
    print(f"Shell command approval required:\n  {command}")
    response = input("Proceed? [y/N] ").strip().lower()
    return response in {"y", "yes"}


@function_tool
async def run_shell_command(command: str) -> str:
    """Execute a shell command and return its output. User must approve each command before it runs.

    Args:
        command: The shell command to execute.

    Returns:
        The command's stdout output, stderr if present, or an error message.
    """
    approved = await prompt_shell_approval(command)
    if not approved:
        return "Command rejected by user."

    timeout = 30
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=os.environ.copy(),
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            stdout_bytes, stderr_bytes = await proc.communicate()
            stdout = stdout_bytes.decode("utf-8", errors="ignore")
            stderr = stderr_bytes.decode("utf-8", errors="ignore")
            return (
                f"Command timed out after {timeout}s.\n"
                f"Stdout:\n{stdout}\n"
                f"Stderr:\n{stderr}"
            )

        stdout = stdout_bytes.decode("utf-8", errors="ignore")
        stderr = stderr_bytes.decode("utf-8", errors="ignore")

        if stderr:
            return f"Stdout:\n{stdout}\nStderr:\n{stderr}"
        return stdout if stdout else "(no output)"
    except Exception as exc:
        return f"Error executing command: {exc}"


async def main(prompt: str, model: str) -> None:
    """Run the shell assistant agent with the given prompt.

    Args:
        prompt: The user's instruction for the agent.
        model: The model name to use.
    """
    with trace("shell_example"):
        print(f"[info] Using model: {model}")

        agent = Agent(
            name="Shell Assistant",
            model=model,
            instructions=(
                "You can run shell commands using the run_shell_command tool. "
                "Execute one command at a time. "
                "Keep responses concise and include command output when helpful."
            ),
            tools=[run_shell_command],
            model_settings=ModelSettings(tool_choice="required"),
        )

        result = await Runner.run(agent, prompt)
        print(f"\nFinal response:\n{result.final_output}")


def ask_user_for_shell_prompt() -> str:
    """Prompt the user for an agent instruction.

    Returns:
        The user's input string.
    """
    print("Enter a prompt for the agent (or 'exit' to quit):")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() == "exit":
            print("Exiting.")
            exit(0)
        if user_input:
            return user_input
        print("Please enter a non-empty prompt (or 'exit' to quit).")


if __name__ == "__main__":
    while True:
        user_task = ask_user_for_shell_prompt()
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--prompt",
            default=user_task,
            help="Instruction to send to the agent.",
        )
        parser.add_argument(
            "--model",
            default="gpt-4o-mini",
        )
        args = parser.parse_args()
        asyncio.run(main(args.prompt, args.model))
