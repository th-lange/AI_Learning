from agents import Agent, WebSearchTool, trace, Runner, gen_trace_id, function_tool
from agents.model_settings import ModelSettings
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import asyncio
import sendgrid
import os
from pathlib import Path
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Dict

load_dotenv(override=True)

async def main():
    INSTRUCTIONS = "You are a research assistant. Given a search term, you search the web for that term and \
    produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 \
    words. Capture the main points. Write succintly, no need to have complete sentences or good \
    grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the \
    essence and ignore any fluff. Do not include any additional commentary other than the summary itself."

    search_agent = Agent(
        name="Search agent",
        instructions=INSTRUCTIONS,
        tools=[WebSearchTool(search_context_size="low")],
        model="gpt-4o-mini",
        model_settings=ModelSettings(tool_choice="required")
    )

    message = "Latest technologies and trends to save token when using agentic AI - reply in markdown format with a concise summary of the search results. Focus on the main points."

    with trace("Search"):
        result = await Runner.run(search_agent, message)


    output_path = Path(__file__).resolve().parent / "EXAMPLE_OUTPUT.md"
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(result.final_output)

if __name__ == "__main__":
   asyncio.run(main()) 

