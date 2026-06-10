# Agent Basics

## Overview

Introduces the simplest building block of the OpenAI Agents SDK: creating an `Agent` with a name, instructions, and model, then running it with `Runner.run()`.

## Key Concepts

- Agent instantiation with `Agent(name, instructions, model)`
- Running an agent via `Runner.run(agent, prompt)`
- Tracing execution with `trace()`
- Loading API keys from environment variables

## How It Works

### Flow

```mermaid
flowchart TD
    classDef user fill:#B4F9F8,stroke:#333,color:#333
    classDef agent fill:#BB9AF7,stroke:#333,color:#333
    classDef success fill:#9ECE6A,stroke:#333,color:#333

    U[User prompt] --> A[Jokester Agent]
    A --> R[Runner.run]
    R --> O[final_output]
    O --> P[Print to console]
    class U user
    class A agent
    class O,P success
```

### Execution

```mermaid
sequenceDiagram
    participant U as User
    participant M as main()
    participant A as Jokester Agent
    participant T as trace

    U->>M: run
    M->>T: start trace
    M->>A: Runner.run(prompt)
    A-->>M: result.final_output
    M->>U: print(output)
```

## Code Walkthrough

`joke_agent.py` is a minimal agent script:

1. **`load_dotenv(override=True)`** — Loads `.env` file for API keys.
2. **`api_key` check** — Raises `ValueError` if `OPENAI_API_KEY` is missing.
3. **`Agent(name="Jokester", ...)`** — Creates an agent with a simple instruction.
4. **`trace("Telling a joke")`** — Wraps execution in a named trace for observability.
5. **`Runner.run(agent, prompt)`** — Sends the prompt to the agent and waits for the response.
6. **`print(result.final_output)`** — Outputs the agent's response.

## Expected Output

```
Why did the autonomous AI agent break up with its partner?

It needed more space... to compute!
```

*(Actual joke varies per run.)*

## Takeaways

- An `Agent` is the atomic unit — name, instructions, model.
- `Runner.run()` is the standard way to execute an agent.
- `trace()` provides execution observability.
- Always validate API keys at startup with a clear error message.
