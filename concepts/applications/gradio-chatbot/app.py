import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
import requests

load_dotenv(override=True)

openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")


def push(text: str) -> None:
    """Send a notification via Pushover.

    Args:
        text: The message to push.
    """
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        },
    )


def record_user_details(
    email: str, name: str = "Name not provided", notes: str = "not provided"
) -> dict[str, str]:
    """Record a user's contact details and push a notification.

    Args:
        email: The user's email address.
        name: The user's name if provided.
        notes: Additional context about the conversation.

    Returns:
        A confirmation dict.
    """
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}


def record_unknown_question(question: str) -> dict[str, str]:
    """Record a question the assistant couldn't answer and push a notification.

    Args:
        question: The unanswered question.

    Returns:
        A confirmation dict.
    """
    push(f"Recording {question}")
    return {"recorded": "ok"}


record_user_details_json = {
    "name": "record_user_details",
    "description": (
        "Use this tool to record that a user is interested in being in touch "
        "and provided an email address"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user",
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it",
            },
            "notes": {
                "type": "string",
                "description": (
                    "Any additional information about the conversation "
                    "that's worth recording to give context"
                ),
            },
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": (
        "Always use this tool to record any question that couldn't be answered "
        "as you didn't know the answer"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered",
            },
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]


class TechnicalSupport:
    """A Gradio technical support chatbot powered by GPT-4o-mini.

    Loads documents from the `documents/` subfolder as its knowledge base.
    Supports two function-calling tools: record_user_details and record_unknown_question.
    """

    def __init__(self) -> None:
        self.openai = OpenAI()
        self.name = "Technical Support Assistant"
        self.knowledge_base = self.load_documents()

    def load_documents(self) -> str:
        """Load all documents from the documents subfolder.

        Supports PDF, TXT, MD, RST, JSON, YAML, XML, and CSV files.

        Returns:
            Concatenated document content as a single string.
        """
        documents_content: list[str] = []
        documents_dir = os.path.dirname(os.path.abspath(__file__))
        documents_path = os.path.join(documents_dir, "documents")

        if not os.path.exists(documents_path):
            os.makedirs(documents_path)
            print(
                f"Created {documents_path} folder. "
                "Please add your technical documentation files there."
            )
            return ""

        for filename in os.listdir(documents_path):
            filepath = os.path.join(documents_path, filename)

            if not os.path.isfile(filepath):
                continue

            try:
                if filename.endswith(".pdf"):
                    reader = PdfReader(filepath)
                    pdf_text = ""
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            pdf_text += text
                    documents_content.append(
                        f"## Document: {filename}\n{pdf_text}\n"
                    )

                elif filename.endswith((".txt", ".md", ".rst")):
                    with open(filepath, "r", encoding="utf-8") as f:
                        documents_content.append(
                            f"## Document: {filename}\n{f.read()}\n"
                        )

                elif filename.endswith((".json", ".yaml", ".yml", ".xml", ".csv")):
                    with open(filepath, "r", encoding="utf-8") as f:
                        documents_content.append(
                            f"## Document: {filename}\n{f.read()}\n"
                        )

            except Exception as e:
                print(f"Error reading {filename}: {e}")

        return (
            "\n\n".join(documents_content)
            if documents_content
            else "No documents loaded yet."
        )

    def handle_tool_call(
        self, tool_calls: list
    ) -> list[dict[str, str]]:
        """Execute function tool calls requested by the LLM.

        Args:
            tool_calls: A list of tool call objects from the OpenAI response.

        Returns:
            A list of tool response message dicts.
        """
        results: list[dict[str, str]] = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append(
                {
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id,
                }
            )
        return results

    def system_prompt(self) -> str:
        """Build the system prompt including the loaded knowledge base.

        Returns:
            The full system prompt string.
        """
        system_prompt = (
            f"You are acting as {self.name}, helping users with technical issues. "
            "Provide accurate, helpful technical support based on the documentation "
            "and knowledge base available to you. Be professional, clear, and helpful. "
            "If you don't know the answer, use record_unknown_question to record it. "
            "If the user wants to follow up, encourage them to provide their email "
            "address; record it using record_user_details. "
        )

        system_prompt += f"\n\n## Technical Documentation:\n{self.knowledge_base}\n\n"
        system_prompt += "With this context, please help the user with their questions."
        return system_prompt

    def chat(self, message: str, history: list) -> str:
        """Handle a single chat turn.

        Args:
            message: The user's latest message.
            history: The conversation history as list of (user, assistant) tuples.

        Returns:
            The assistant's response string.
        """
        messages = [
            {"role": "system", "content": self.system_prompt()}
        ] + history + [{"role": "user", "content": message}]

        done = False
        while not done:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini", messages=messages, tools=tools
            )
            if response.choices[0].finish_reason == "tool_calls":
                msg = response.choices[0].message
                tool_calls = msg.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(msg)
                messages.extend(results)
            else:
                done = True

        return response.choices[0].message.content


if __name__ == "__main__":
    support = TechnicalSupport()
    gr.ChatInterface(support.chat).launch()
