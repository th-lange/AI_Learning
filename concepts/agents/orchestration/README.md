# Supervisor / Orchestrator Pattern

## Overview

Implements a **Supervisor multi-agent architecture** where a central orchestrator coordinates three architect agents (each using a different LLM model) to produce architectural designs, then hands off to a visualizer agent for final presentation. Demonstrates mixing **agents-as-tools** and **handoffs** in a single workflow.

## Key Concepts

- Multi-model agents: DeepSeek, GPT-4o-mini, and Llama 3.3 via Groq
- `OpenAIChatCompletionsModel` — wrapping any OpenAI-compatible API as an agent model
- Mixing `tools` (architects as callable tools) and `handoffs` (visualizer)
- Supervisor delegates to architects, collects results, hands off to visualizer

## How It Works

### Flow

```mermaid
flowchart TD
    classDef user fill:#B4F9F8,stroke:#333,color:#333
    classDef agent fill:#BB9AF7,stroke:#333,color:#333
    classDef success fill:#9ECE6A,stroke:#333,color:#333

    User([User Task]) --> Orchestrator

    subgraph OrchestratorBox [Orchestrator gpt-4o]
        O[Orchestrator]
    end

    subgraph Architects [Architect Team]
        A1[Architect 1<br/>DeepSeek<br/>Senior Builder]
        A2[Architect 2<br/>GPT-4o-mini<br/>Domain Separation]
        A3[Architect 3<br/>Llama 3.3<br/>Young Innovator]
    end

    subgraph Presentation [Presentation]
        V[Visualizer Agent<br/>GPT-4o-mini]
        D[Markdown + Mermaid Output]
    end

    Orchestrator -->|tool: architect_one| A1
    Orchestrator -->|tool: architect_two| A2
    Orchestrator -->|tool: architect_three| A3
    A1 -->|design proposals| Orchestrator
    A2 -->|design proposals| Orchestrator
    A3 -->|design proposals| Orchestrator
    Orchestrator -->|handoff| V
    V -->|visualize_architectures| D

    class User user
    class Orchestrator,O,A1,A2,A3,V agent
    class D success
```

### Execution

```mermaid
sequenceDiagram
    participant U as User
    participant O as Orchestrator
    participant A1 as DeepSeek Arch.
    participant A2 as GPT-4o-mini Arch.
    participant A3 as Llama 3.3 Arch.
    participant V as Visualizer

    U->>O: design task
    O->>A1: tool call
    A1-->>O: SQL-based design
    O->>A2: tool call
    A2-->>O: NoSQL-based design
    O->>A3: tool call
    A3-->>O: hybrid design
    O->>V: handoff with consolidated designs
    V->>U: visualize_architectures(markdown + mermaid)
```

## Code Walkthrough

`supervisor.py` builds a multi-agent system across three layers:

1. **Model Setup** — Three `AsyncOpenAI` clients configured for DeepSeek, Groq, and OpenAI APIs. Each wrapped in `OpenAIChatCompletionsModel` to be used as an agent model.
2. **Architect Agents** — Three agents with distinct personas:
   - *Deep Seek Architect*: Senior builder, loves patterns and clean domain design
   - *Gemini Architect*: Domain separation advocate, immutability and layered architecture
   - *Groq Architect*: Young developer, embraces new patterns
   - All three wrapped as tools via `.as_tool()`
3. **Visualizer Agent** — Converts raw designs into formatted Markdown with Mermaid diagrams. Registered as a `handoff` target.
4. **Orchestrator** — The supervisor (gpt-4o). Calls each architect as a tool, consolidates results, then hands off to the visualizer.

## Agents Overview

| Agent | Model | Personality |
|---|---|---|
| Orchestrator | `gpt-4o` | Delegates, coordinates, hands off |
| Architect 1 | `deepseek-chat` | Senior builder, patterns, scalability |
| Architect 2 | `gpt-4o-mini` | Domain separation, immutability |
| Architect 3 | `llama-3.3-70b` | Young innovator, new approaches |
| Visualizer | `gpt-4o-mini` | Converts designs to markdown + mermaid |

## Expected Output

The visualizer produces architectural designs with mermaid diagrams. Example designs generated:

- **SQL-Based Recoverable Request Storage** — Idempotency via payload hashing, priority queuing, circuit breaker, `SKIP LOCKED` for concurrent processing
- **NoSQL-Based Request Storage** — Flexible schemas, async event-driven decoupling, lower transactional guarantees
- **Hybrid Architecture** — NoSQL for request metadata, SQL for processing outcomes, best of both worlds

## Takeaways

- `.as_tool()` gives the orchestrator fine-grained control over when sub-agents are called.
- Handoffs transfer full control — use them for the final presentation layer.
- `OpenAIChatCompletionsModel` lets you use any OpenAI-compatible API as an agent model.
- The supervisor pattern cleanly separates coordination (orchestrator), execution (architects), and presentation (visualizer).
