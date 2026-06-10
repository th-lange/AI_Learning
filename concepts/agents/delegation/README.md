# Agent Delegation Patterns

## Overview

Compares three ways to coordinate multiple specialist agents in the OpenAI Agents SDK, using security expert personas analyzing Python packages. Each pattern trades off cost, control, and decision quality differently.

## Key Concepts

- **Fan-out + Picker** — Parallel execution of all experts, picker judges outputs
- **Handoffs** — Router delegates to one specialist and hands off control
- **Agents as Tools** — Subagents wrapped as callable tools; orchestrator stays in control
- Trade-offs between LLM call count, output visibility, and control granularity

## How It Works

### Flow — All Three Patterns

```mermaid
flowchart TD
    classDef user fill:#B4F9F8,stroke:#333,color:#333
    classDef agent fill:#BB9AF7,stroke:#333,color:#333
    classDef success fill:#9ECE6A,stroke:#333,color:#333

    subgraph P1 [Pattern 1: Fan-Out + Picker]
        U1([User]) -->|message| A1[Pedantic]
        U1 -->|message| A2[Sarcastic]
        U1 -->|message| A3[Helpful]
        A1 -->|output| PK[Picker]
        A2 -->|output| PK
        A3 -->|output| PK
        PK --> D1[display_info]
    end

    subgraph P2 [Pattern 2: Handoffs]
        U2([User]) --> PK2[Picker]
        PK2 -->|handoff| CH[chosen Agent]
        CH --> D2[display_info]
    end

    subgraph P3 [Pattern 3: Agents as Tools]
        U3([User]) --> OR[Orchestrator]
        OR -->|tool call| AT1[Pedantic]
        OR -->|tool call| AT2[Sarcastic]
        OR -->|tool call| AT3[Helpful]
        AT1 -->|output| OR
        AT2 -->|output| OR
        AT3 -->|output| OR
        OR --> D3[display_info]
    end

    class U1,U2,U3 user
    class A1,A2,A3,PK,PK2,CH,OR,AT1,AT2,AT3 agent
    class D1,D2,D3 success
```

### Execution — Pattern 1: Fan-Out + Picker

```mermaid
sequenceDiagram
    participant U as User
    participant A1 as Pedantic
    participant A2 as Sarcastic
    participant A3 as Helpful
    participant P as Picker

    par
        U->>A1: message
        U->>A2: message
        U->>A3: message
    end
    A1-->>P: output1
    A2-->>P: output2
    A3-->>P: output3
    P->>U: display_info(best output)
```

> **Always 4 LLM calls.** Picker sees all outputs. Most expensive, most informed.

### Execution — Pattern 2: Handoffs

```mermaid
sequenceDiagram
    participant U as User
    participant P as Picker
    participant A as chosen Agent

    U->>P: message
    P->>A: handoff
    A->>U: display_info(output)
```

> **2 LLM calls.** Cheapest. Picker decides without seeing any output. Each subagent needs `display_info` in its own `tools=[]`.

### Execution — Pattern 3: Agents as Tools

```mermaid
sequenceDiagram
    participant U as User
    participant O as Orchestrator
    participant A1 as Pedantic
    participant A2 as Sarcastic
    participant A3 as Helpful
    participant D as display_info

    U->>O: message
    O->>A1: tool call
    A1-->>O: pedantic output
    O->>A2: tool call
    A2-->>O: sarcastic output
    O->>A3: tool call
    A3-->>O: helpful output
    O->>D: tool call (best output)
    D-->>U: rendered Markdown
```

> **1–4 LLM calls, dynamic.** Orchestrator stays in control. Subagents only receive the input string, not full history.

## Code Walkthrough

### `fan_out_picker.py`

1. `create_experts()` — Creates 3 expert agents (pedantic, sarcastic, helpful) and a picker agent.
2. `main()` — Runs all 3 experts simultaneously via `asyncio.gather`, collects outputs, feeds them to the picker.

### `handoffs.py`

1. Each expert is registered as a `handoffs=[...]` target on the picker with a `handoff_description`.
2. Each expert has `display_info` in its `tools` list so it can output directly after taking control.
3. The picker routes to one expert and hands off full control.

### `agents_as_tools.py`

1. Each expert is wrapped with `.as_tool(tool_name=..., tool_description=...)`.
2. All tool-wrapped agents and `display_info` go into the orchestrator's `tools=[...]`.
3. The orchestrator stays in control and can call any subset of experts dynamically.

## Comparison

| Pattern | LLM Calls | Picker Sees Output? | Control Model |
|---|---|---|---|
| Fan-out + Picker | 4 (always) | Yes, all outputs | Picker judges after |
| Handoffs | 2 (always) | No, none | Subagent takes over |
| Agents as Tools | 1–4 (dynamic) | Yes, each result | Orchestrator throughout |

## Takeaways

- **Fan-out + Picker** is best when you need to compare multiple expert opinions and cost is not a concern.
- **Handoffs** are ideal for efficient routing when you trust the picker's intent-based decision.
- **Agents as Tools** gives maximum control and flexibility at the cost of more LLM calls if all experts are invoked.
