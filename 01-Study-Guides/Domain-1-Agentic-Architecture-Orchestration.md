# Domain 1: Agentic Architecture & Orchestration
## Claude Certified Architect – Foundations Study Guide

**Exam Weight:** 27% (19 questions)
**Questions:** Q1, Q7-Q9, Q13-Q29
**Last Updated:** March 2026

---

## Table of Contents
1. [Task 1.1: Agentic Loops for Autonomous Task Execution](#task-11-agentic-loops)
2. [Task 1.2: Multi-Agent Coordination](#task-12-multi-agent-coordination)
3. [Task 1.3: Subagent Invocation & Context Passing](#task-13-subagent-invocation)
4. [Task 1.4: Multi-Step Workflows with Enforcement](#task-14-multi-step-workflows)
5. [Task 1.5: Agent SDK Hooks for Tool Interception](#task-15-sdk-hooks)
6. [Task 1.6: Task Decomposition Strategies](#task-16-task-decomposition)
7. [Task 1.7: Session State Management](#task-17-session-management)
8. [Quick Reference Cheatsheet](#quick-reference-cheatsheet)
9. [Exam Traps & Distractors](#exam-traps-and-distractors)

---

## Task 1.1: Agentic Loops for Autonomous Task Execution

### Conceptual Overview

An **agentic loop** is the fundamental execution pattern that powers autonomous agents. Claude evaluates a prompt, determines if it needs external tools, executes those tools, incorporates results back into the conversation, and repeats until the task is complete.

The loop terminates based on the model's **`stop_reason`** field:
- **`"end_turn"`** (PRIMARY): Model has completed the task and deliberately stopped
- **`"tool_use"`**: Model generated a tool call requiring execution
- **`"max_tokens"`**: Hit output token limit (usually indicates incomplete work)
- **`"refusal"`**: Model declined the request on safety grounds
- **`null`**: Unspecified termination

**Key Principle:** `stop_reason == "end_turn"` is the PRIMARY termination condition. Iteration caps are SAFETY GUARDRAILS, not the primary mechanism.

### Deep Conceptual Explanation

#### The Execution Flow

```
Initialize conversation history
Set iteration counter = 0
Set max_iterations = 10 (safety guardrail)

WHILE True:
    1. Call Claude API with messages
    2. Receive response with stop_reason

    IF stop_reason == "end_turn":
        → Agent completed task: BREAK LOOP

    ELIF stop_reason == "tool_use":
        → Extract tool calls from response
        → Execute tools and collect results
        → Append assistant response to history
        → Append tool results as user message
        → Continue loop

    ELIF stop_reason == "max_tokens":
        → Task incomplete: Handle gracefully
        → Return partial results or error
        → BREAK LOOP

    ELIF stop_reason == "refusal":
        → Task declined on safety grounds
        → Return refusal explanation
        → BREAK LOOP

    Increment iteration counter
    IF iteration counter >= max_iterations:
        → Force termination (safety guardrail)
        → Log warning
        → Return partial results
        → BREAK LOOP
```

#### Why stop_reason Matters

The model uses `stop_reason` to communicate its intent:
- When it sets `stop_reason` to `"end_turn"`, it's explicitly saying "I'm done"
- When it sets `stop_reason` to `"tool_use"`, it's requesting execution before continuing
- When it sets `stop_reason` to `"max_tokens"`, it's warning "I ran out of space"

**Exam Critical:** Never rely on iteration count as primary termination. The model knows when it's done; iteration caps prevent infinite loops on broken code.

#### Conversation History Accumulation

Each iteration must properly maintain conversation history:

```
Turn 1:
  messages = [
    {role: "user", content: "Original prompt"}
  ]
  response = Claude's first response (may contain tool_use)

Turn 2 (if tool_use):
  messages = [
    {role: "user", content: "Original prompt"},
    {role: "assistant", content: response},
    {role: "user", content: "Tool results"}  ← CRITICAL: Tool results are user messages
  ]
  response = Claude's second response
```

This is crucial because Claude needs to see its own tool calls and their results to reason about the next steps.

### Python Code Examples

#### Basic Agentic Loop Pattern

```python
import anthropic
import json

def run_agent_loop(initial_prompt: str, tools: list) -> dict:
    """
    Basic agentic loop with proper stop_reason handling.

    References: Exercise-1/agent.py pattern
    """
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": initial_prompt}]

    iteration = 0
    max_iterations = 10  # Safety guardrail

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")

        # Call Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        print(f"Stop reason: {response.stop_reason}")

        # PRIMARY TERMINATION: end_turn
        if response.stop_reason == "end_turn":
            print("Agent completed task.")
            return {
                "status": "completed",
                "iterations": iteration,
                "final_response": response.content,
                "stop_reason": response.stop_reason
            }

        # TOOL EXECUTION: tool_use
        elif response.stop_reason == "tool_use":
            # Append assistant response to history
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            # Process tool calls
            tool_results = []
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    tool_use_id = content_block.id

                    print(f"Executing tool: {tool_name}")

                    # Execute tool (simplified)
                    result = execute_tool(tool_name, tool_input)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json.dumps(result) if isinstance(result, dict) else result
                    })

            # Append tool results as user message
            messages.append({
                "role": "user",
                "content": tool_results
            })

        # ERROR CASES
        elif response.stop_reason == "max_tokens":
            print("Hit max tokens - task incomplete")
            return {
                "status": "incomplete",
                "reason": "max_tokens",
                "iterations": iteration,
                "partial_response": response.content
            }

        elif response.stop_reason == "refusal":
            print("Agent refused task")
            return {
                "status": "refused",
                "iterations": iteration,
                "reason": response.content
            }

    # SAFETY GUARDRAIL: Exceeded max iterations
    print(f"Exceeded max iterations ({max_iterations})")
    return {
        "status": "timeout",
        "iterations": iteration,
        "reason": "Max iteration safety guardrail triggered"
    }


def execute_tool(tool_name: str, tool_input: dict) -> any:
    """
    Executes a tool and returns results.

    This is where you integrate with your actual tools:
    - File operations
    - API calls
    - Database queries
    - External services
    """
    if tool_name == "read_file":
        # Actual file reading logic
        return {"content": "file contents"}
    elif tool_name == "search":
        # Actual search logic
        return {"results": ["result1", "result2"]}
    else:
        return {"error": f"Unknown tool: {tool_name}"}
```

#### Agentic Loop with Structured Tools

```python
def create_tools_definition() -> list:
    """
    Define tools with proper schemas for Claude to understand.
    """
    return [
        {
            "name": "search_documentation",
            "description": "Search Claude documentation for information",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "filters": {
                        "type": "object",
                        "properties": {
                            "domain": {"type": "string"},
                            "version": {"type": "string"}
                        }
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "analyze_code",
            "description": "Analyze code samples for patterns",
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to analyze"
                    },
                    "aspect": {
                        "type": "string",
                        "enum": ["performance", "security", "architecture"]
                    }
                },
                "required": ["code", "aspect"]
            }
        }
    ]


def run_agent_with_iteration_tracking(
    initial_prompt: str,
    tools: list,
    on_iteration: callable = None
) -> dict:
    """
    Agent loop with iteration callback for monitoring.

    Args:
        on_iteration: Callback(iteration, stop_reason, tool_calls_count)
    """
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": initial_prompt}]

    iteration = 0
    tool_call_history = []

    while iteration < 10:
        iteration += 1

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        tool_calls_count = sum(
            1 for block in response.content
            if hasattr(block, 'type') and block.type == "tool_use"
        )

        if on_iteration:
            on_iteration(iteration, response.stop_reason, tool_calls_count)

        # Track tool usage
        if response.stop_reason == "tool_use":
            tool_call_history.append({
                "iteration": iteration,
                "tool_count": tool_calls_count
            })

        if response.stop_reason == "end_turn":
            return {
                "status": "completed",
                "iterations": iteration,
                "tool_call_history": tool_call_history,
                "final_response": response.content
            }

        elif response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            # Process tools
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })

            messages.append({"role": "user", "content": tool_results})

        else:
            break

    return {
        "status": "timeout",
        "iterations": iteration,
        "tool_call_history": tool_call_history
    }
```

#### Safety Guardrail Pattern

```python
def run_agent_with_safety_guardrails(
    initial_prompt: str,
    tools: list,
    max_iterations: int = 10,
    max_tool_calls: int = 50,
    timeout_seconds: float = 300.0
) -> dict:
    """
    Agentic loop with comprehensive safety guardrails.

    Guardrails are supplementary - stop_reason="end_turn" is primary termination.
    """
    import time

    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": initial_prompt}]

    iteration = 0
    total_tool_calls = 0
    start_time = time.time()

    while True:
        # Check safety guardrails BEFORE calling API
        if iteration >= max_iterations:
            return {
                "status": "error",
                "reason": "max_iterations_exceeded",
                "iterations": iteration
            }

        if total_tool_calls >= max_tool_calls:
            return {
                "status": "error",
                "reason": "max_tool_calls_exceeded",
                "total_calls": total_tool_calls
            }

        if time.time() - start_time > timeout_seconds:
            return {
                "status": "error",
                "reason": "timeout_exceeded",
                "elapsed_seconds": time.time() - start_time
            }

        iteration += 1

        # Main API call
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        # PRIMARY CHECK: stop_reason
        if response.stop_reason == "end_turn":
            return {
                "status": "success",
                "iterations": iteration,
                "total_tool_calls": total_tool_calls,
                "result": response.content
            }

        if response.stop_reason != "tool_use":
            return {
                "status": "error",
                "reason": response.stop_reason,
                "iterations": iteration
            }

        # Process tool calls
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                total_tool_calls += 1

                try:
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })
                except Exception as e:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Tool error: {str(e)}",
                        "is_error": True
                    })

        messages.append({"role": "user", "content": tool_results})
```

### Common Exam Traps

**TRAP 1: "Iteration caps are the primary termination mechanism"**
- **Reality:** `stop_reason == "end_turn"` is PRIMARY. Iteration caps are safety guardrails.
- **Exam Answer:** When asked what terminates an agent loop normally, answer: "When `stop_reason` equals `'end_turn'`"

**TRAP 2: "Tool results should be appended as assistant messages"**
- **Reality:** Tool results are USER messages in the conversation history.
- **Exam Answer:** After receiving tool results, append them with `role: "user"`

**TRAP 3: "You should terminate when max_tokens is reached"**
- **Reality:** When `stop_reason == "max_tokens"`, you CAN continue if you want (it's not a hard stop like `end_turn`). This indicates incomplete work - decide whether to retry.
- **Exam Answer:** Recognize this as a signal of incomplete work, but it's not an error - handle gracefully.

**TRAP 4: "ignore stop_reason and just check for tool_use blocks"**
- **Reality:** Must check `stop_reason` to understand intent. A response might have no content blocks even if `tool_use` is the stop reason (edge case).
- **Exam Answer:** Always check `stop_reason` as the primary control flow mechanism.

### Quick Reference

| Concept | Key Points |
|---------|-----------|
| **Primary Termination** | `stop_reason == "end_turn"` |
| **Tool Processing** | Extract from `response.content` where `.type == "tool_use"` |
| **Tool Results in History** | Append as `role: "user"` with array of `tool_result` blocks |
| **Safety Guardrails** | Iteration caps, tool call limits, timeouts - supplementary only |
| **Error Handling** | Check `stop_reason` for "max_tokens", "refusal" - not loop-breaking |
| **Conversation Continuity** | Maintain full message history; append each turn |

---

## Task 1.2: Multi-Agent Coordination

### Conceptual Overview

**Multi-agent coordination** uses a hub-and-spoke model where:
- **Coordinator (Hub):** Routes tasks to subagents, evaluates output quality, decides on re-delegation
- **Subagents (Spokes):** Specialized agents handling delegated tasks in parallel
- **Dynamic Routing:** Decisions based on query complexity, not static keyword tables
- **Output Evaluation:** Coordinator checks if subagent results are complete and covers necessary aspects
- **Re-delegation:** Coordinator invokes subagents with targeted prompts for missing work

This differs from basic sequential tool use - subagents are SPECIALIZED (different system prompts, tools, knowledge), not just function calls.

### Deep Conceptual Explanation

#### Hub-and-Spoke Architecture

```
User Query
    ↓
[Coordinator Agent]
    ├─→ Analyze complexity
    ├─→ Decompose into tasks
    ├─→ Route to subagents (parallel)
    │   ├─→ [SubAgent-A] (specialized domain)
    │   ├─→ [SubAgent-B] (specialized domain)
    │   └─→ [SubAgent-C] (specialized domain)
    ├─→ Collect outputs
    ├─→ Evaluate for coverage gaps
    └─→ Re-delegate if needed
         ├─→ [SubAgent-A] (targeted refinement)
         └─→ [SubAgent-B] (targeted refinement)
    ↓
Integrated Final Response
```

#### Dynamic Routing (NOT Static Keyword Tables)

**WRONG:** Static routing
```python
if "technical" in query.lower():
    route_to_subagent_A()
elif "business" in query.lower():
    route_to_subagent_B()
```

**CORRECT:** Dynamic routing based on evaluation
```python
# Coordinator evaluates the query
analysis = coordinator.evaluate_query_complexity(query)
# analysis.required_expertise = ["database_design", "optimization"]
# analysis.complexity_score = 0.85
# analysis.estimated_effort = "moderate"

# Route based on actual needs
for expertise in analysis.required_expertise:
    subagent = select_subagent_for_expertise(expertise)
    invoke_subagent(subagent, query)
```

#### Output Evaluation and Re-delegation

```python
def coordinate_multi_agent_task(query: str) -> str:
    """
    Coordinator pattern: route → evaluate → re-delegate if needed
    """
    # Initial routing
    subagent_outputs = {}

    # Route based on dynamic analysis
    route_plan = coordinator_analyze_query(query)

    for subagent_id, task_spec in route_plan.items():
        output = invoke_subagent(
            subagent_id=subagent_id,
            task_description=task_spec["description"],
            context=query
        )
        subagent_outputs[subagent_id] = output

    # Evaluate coverage
    coverage_analysis = evaluate_output_coverage(
        query=query,
        outputs=subagent_outputs
    )

    # Check for gaps
    if coverage_analysis.has_gaps:
        for gap in coverage_analysis.gaps:
            # Targeted re-delegation
            refinement = invoke_subagent(
                subagent_id=gap["responsible_subagent"],
                task_description=gap["gap_description"],
                previous_output=subagent_outputs[gap["responsible_subagent"]],
                focus_areas=gap["specific_areas"]
            )
            subagent_outputs[gap["responsible_subagent"]] = refinement

    # Integrate results
    return integrate_outputs(subagent_outputs)
```

#### Quality Evaluation Pattern

The coordinator must evaluate:
1. **Completeness:** Does the output address all aspects?
2. **Accuracy:** Is the information correct (sanity checks)?
3. **Relevance:** Does it answer the actual question?
4. **Consistency:** Do outputs from multiple subagents align?

### Python Code Examples

#### Basic Coordinator Pattern

```python
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class SubagentOutput:
    subagent_id: str
    content: str
    confidence: float
    areas_covered: List[str]
    potential_gaps: List[str]


def create_coordinator_agent(subagent_specs: Dict[str, dict]):
    """
    Create a coordinator agent that manages subagents.

    Args:
        subagent_specs: Dict mapping subagent_id to {
            "role": str,
            "specialization": str,
            "tools": List[str]
        }
    """

    coordinator_prompt = f"""You are a coordinator agent managing a team of specialists.

Your subagents:
{format_subagent_specs(subagent_specs)}

When given a task:
1. Analyze what expertise is needed
2. Decompose into focused subtasks for each relevant specialist
3. Provide each specialist with clear context and goals
4. After receiving results, evaluate for completeness
5. If gaps exist, re-delegate with targeted guidance

Respond with clear routing decisions in JSON format."""

    return coordinator_prompt


def dynamic_route_query(
    query: str,
    subagent_specs: Dict[str, dict],
    coordinator_client
) -> Dict[str, str]:
    """
    Dynamically analyze query and create routing plan.

    Returns: Dict mapping subagent_id → task_description
    """

    analysis_prompt = f"""Analyze this query and determine which specialists should handle it:

Query: {query}

For each relevant specialist, explain:
- Why they're needed
- What specific subtask to delegate
- Key constraints for their work

Be precise - don't route to specialists unnecessarily."""

    response = coordinator_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{"role": "user", "content": analysis_prompt}]
    )

    # Parse response to extract routing decisions
    routing_plan = parse_routing_decisions(response.content[0].text)
    return routing_plan


def evaluate_subagent_outputs(
    query: str,
    outputs: Dict[str, SubagentOutput],
    coordinator_client
) -> dict:
    """
    Coordinator evaluates if subagent outputs adequately address the query.

    Returns: {
        "is_complete": bool,
        "gaps": [{"area": str, "responsible_subagent": str, "guidance": str}],
        "quality_score": float
    }
    """

    evaluation_prompt = f"""Evaluate if these specialist outputs adequately address the query.

ORIGINAL QUERY:
{query}

SPECIALIST OUTPUTS:
{format_outputs(outputs)}

Assess:
1. Does it answer the original question completely?
2. Are there important aspects left uncovered?
3. Are there contradictions between outputs?
4. What additional work is needed, if any?

Be critical and specific about gaps."""

    response = coordinator_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{"role": "user", "content": evaluation_prompt}]
    )

    evaluation = parse_evaluation(response.content[0].text)
    return evaluation


def handle_redelegation(
    gap_info: dict,
    previous_output: SubagentOutput,
    query: str,
    subagent_client
) -> SubagentOutput:
    """
    Re-invoke a subagent with targeted guidance about gaps.

    Key: Be specific about WHAT was missing, not just "provide more detail"
    """

    refinement_prompt = f"""Review your previous work on this task:

ORIGINAL TASK: {query}

YOUR PREVIOUS OUTPUT:
{previous_output.content}

FEEDBACK - GAPS IDENTIFIED:
{gap_info['gap_description']}

Specific areas to address:
{format_list(gap_info['specific_areas'])}

Provide an enhanced response that specifically addresses these gaps.
Integrate with your previous findings, don't just repeat."""

    response = subagent_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{"role": "user", "content": refinement_prompt}]
    )

    return SubagentOutput(
        subagent_id=previous_output.subagent_id,
        content=response.content[0].text,
        confidence=0.85,  # Re-delegated work is usually higher confidence
        areas_covered=gap_info['specific_areas'],
        potential_gaps=[]
    )


def integrate_multi_agent_outputs(
    outputs: Dict[str, SubagentOutput],
    original_query: str,
    coordinator_client
) -> str:
    """
    Synthesize outputs from multiple subagents into coherent response.
    """

    integration_prompt = f"""Synthesize these specialist outputs into a unified response.

ORIGINAL QUERY:
{original_query}

SPECIALIST OUTPUTS:
{format_outputs(outputs)}

Create a cohesive response that:
1. Flows naturally without abrupt transitions
2. Attributes credit where appropriate ("Specialist A identified...", etc.)
3. Resolves any contradictions with explanation
4. Provides clear conclusions
5. Suggests next steps if relevant

Do NOT just concatenate the outputs."""

    response = coordinator_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{"role": "user", "content": integration_prompt}]
    )

    return response.content[0].text


def full_multi_agent_coordination(
    query: str,
    subagent_specs: Dict[str, dict],
    coordinator_client,
    subagent_clients: Dict[str, any]
) -> str:
    """
    Complete multi-agent coordination workflow.

    References: Exercise-1/agent.py - extend with subagent spawning
    """

    # Step 1: Route query to appropriate subagents
    routing_plan = dynamic_route_query(
        query=query,
        subagent_specs=subagent_specs,
        coordinator_client=coordinator_client
    )

    # Step 2: Invoke subagents (can be parallel)
    outputs = {}
    for subagent_id, task_description in routing_plan.items():
        if subagent_id in subagent_clients:
            output = invoke_subagent_with_loop(
                subagent_client=subagent_clients[subagent_id],
                task=task_description,
                context=query
            )
            outputs[subagent_id] = output

    # Step 3: Evaluate coverage
    max_refinement_iterations = 2
    for iteration in range(max_refinement_iterations):
        evaluation = evaluate_subagent_outputs(
            query=query,
            outputs=outputs,
            coordinator_client=coordinator_client
        )

        if not evaluation["gaps"]:
            print(f"Outputs complete after {iteration} iterations")
            break

        # Step 4: Re-delegate for gaps
        for gap in evaluation["gaps"]:
            refined_output = handle_redelegation(
                gap_info=gap,
                previous_output=outputs[gap["responsible_subagent"]],
                query=query,
                subagent_client=subagent_clients[gap["responsible_subagent"]]
            )
            outputs[gap["responsible_subagent"]] = refined_output

    # Step 5: Integrate outputs
    final_response = integrate_multi_agent_outputs(
        outputs=outputs,
        original_query=query,
        coordinator_client=coordinator_client
    )

    return final_response
```

### Common Exam Traps

**TRAP 1: "Use keyword matching to route tasks"**
- **Reality:** Dynamic routing analyzes complexity and expertise needs.
- **Exam Answer:** Coordinator evaluates the query to determine required expertise, not keyword-based rules.

**TRAP 2: "Subagents work sequentially, not in parallel"**
- **Reality:** In hub-and-spoke, subagents can work in parallel (coordinated next task).
- **Exam Answer:** Subagents can be invoked in parallel; coordinator waits for all, then evaluates.

**TRAP 3: "Coordinator accepts first subagent output without evaluation"**
- **Reality:** Coordinator evaluates for completeness, accuracy, consistency.
- **Exam Answer:** Coordinator must assess coverage gaps before integrating results.

**TRAP 4: "Re-delegation means starting fresh"**
- **Reality:** Re-delegation includes previous output and specific gap guidance.
- **Exam Answer:** When re-delegating, reference previous work and highlight specific missing areas.

### Quick Reference

| Concept | Key Points |
|---------|-----------|
| **Hub-and-Spoke** | One coordinator, multiple specialized subagents |
| **Dynamic Routing** | Analyze query to determine routing, not static keywords |
| **Parallel Execution** | Subagents work simultaneously on their tasks |
| **Output Evaluation** | Check completeness, accuracy, consistency, coverage |
| **Targeted Re-delegation** | Include previous output + specific gap guidance |
| **Integration** | Synthesize outputs into coherent response |

---

## Task 1.3: Subagent Invocation, Context Passing, and Spawning

### Conceptual Overview

Subagent spawning is the mechanism for creating autonomous specialized agents. Key elements:

1. **Task Tool:** The primary mechanism for spawning subagents (must be in `allowedTools`)
2. **Context Passing:** Structured data formats for sharing information between agents
3. **Parallel Execution:** Multiple Task calls in a single response = parallel execution
4. **Metadata Preservation:** Structured output formats maintain traceability

### Deep Conceptual Explanation

#### The Task Tool

The **Task tool** is Claude's mechanism for an agent to spawn subagents:

```python
{
    "type": "tool_use",
    "id": "task_xyz",
    "name": "Task",
    "input": {
        "title": "Analyze Security Report",
        "description": "Review security audit findings and identify critical issues",
        "context": {
            "audit_data": audit_json,
            "compliance_framework": "SOC2",
            "priority_focus": ["authentication", "data_protection"]
        }
    }
}
```

**CRITICAL EXAM POINT:** For a coordinator agent to use the Task tool, `"Task"` MUST be in its `allowedTools` list.

#### allowedTools Requirement

```python
# WRONG - subagent can't spawn other subagents
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=messages,
    tools=available_tools,
    # allowedTools=[...] doesn't include Task
)

# RIGHT - coordinator can spawn subagents
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=messages,
    tools=available_tools,
    allowedTools=["Task", "Read", "Glob", "Grep"]  # Task must be included
)
```

#### Context Passing with Structured Formats

Context must be passed as structured data, not free-form text:

```python
# Good: Structured claim-source mapping
context = {
    "claims": [
        {
            "id": "claim_001",
            "text": "Claude processes 10B tokens daily",
            "source": "anthropic_blog_2024",
            "claim_type": "capability"
        },
        {
            "id": "claim_002",
            "text": "Token limit is 200k",
            "source": "api_docs_section_3.2",
            "claim_type": "technical_spec"
        }
    ],
    "verification_criteria": {
        "required_fields": ["id", "text", "source"],
        "allowed_types": ["capability", "technical_spec", "performance"]
    }
}

# Poor: Unstructured text
context = {
    "data": "Claude processes 10B tokens daily according to the blog. Token limit is 200k from API docs."
}
```

#### Parallel Execution Pattern

When a coordinator emits MULTIPLE Task calls in a SINGLE response, they execute in parallel:

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[...],
    tools=[task_tool],
    allowedTools=["Task"]
)

# If response.content contains 3 Task tool_use blocks:
# - All 3 tasks are spawned simultaneously
# - Coordinator waits for all 3 to complete
# - Results come back in a single batch

# Tool use blocks in a single response:
task1 = {
    "type": "tool_use",
    "id": "task_1",
    "name": "Task",
    "input": {
        "title": "Security Analysis",
        ...
    }
}

task2 = {
    "type": "tool_use",
    "id": "task_2",
    "name": "Task",
    "input": {
        "title": "Performance Analysis",
        ...
    }
}

task3 = {
    "type": "tool_use",
    "id": "task_3",
    "name": "Task",
    "input": {
        "title": "Cost Analysis",
        ...
    }
}

# All three execute in parallel
```

#### Metadata Preservation in Subagent Output

Subagent responses should preserve metadata for traceability:

```python
# Subagent output with metadata
subagent_output = {
    "task_id": "task_001",
    "subagent_id": "security_specialist",
    "execution_status": "completed",
    "findings": [
        {
            "category": "critical",
            "issue": "SQL injection vulnerability in auth module",
            "location": "auth.py:line 145",
            "severity_score": 9.8,
            "recommendation": "Implement parameterized queries"
        }
    ],
    "metadata": {
        "execution_time_ms": 2340,
        "tools_used": ["codebase_search", "vulnerability_database"],
        "confidence": 0.95
    }
}
```

### Python Code Examples

#### Spawning Subagents with Task Tool

```python
def create_coordinator_with_subagent_spawning():
    """
    Coordinator that spawns subagents using Task tool.

    Key: allowedTools must include "Task"
    """

    task_tool_definition = {
        "name": "Task",
        "description": "Spawn a subagent to handle a specialized task",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Clear, concise task title"
                },
                "description": {
                    "type": "string",
                    "description": "Detailed task description and requirements"
                },
                "context": {
                    "type": "object",
                    "description": "Structured context data for subagent",
                    "properties": {
                        "input_data": {"type": "object"},
                        "constraints": {"type": "array"},
                        "required_output_format": {"type": "object"}
                    }
                }
            },
            "required": ["title", "description"]
        }
    }

    return task_tool_definition


def run_coordinator_with_allowed_tools(
    initial_prompt: str,
    subagent_specs: list
):
    """
    Coordinator agent that can spawn subagents.

    CRITICAL: allowedTools includes "Task" for subagent spawning
    """
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": initial_prompt}]

    # Define available tools
    tools = [
        {
            "name": "Task",
            "description": "Spawn a subagent for specialized work"
            # ... full definition
        },
        {
            "name": "SearchKnowledge",
            "description": "Search coordinator's knowledge base"
        }
    ]

    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=tools,
            allowedTools=["Task", "SearchKnowledge"],  # MUST include Task
            messages=messages
        )

        if response.stop_reason == "end_turn":
            return response.content

        if response.stop_reason != "tool_use":
            break

        # Append response
        messages.append({
            "role": "assistant",
            "content": response.content
        })

        # Process tool calls (Task calls will be subagent spawns)
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                if block.name == "Task":
                    # Spawn subagent
                    result = spawn_subagent(
                        title=block.input["title"],
                        description=block.input["description"],
                        context=block.input.get("context", {})
                    )
                else:
                    # Other tool execution
                    result = execute_coordinator_tool(block.name, block.input)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result)
                })

        messages.append({
            "role": "user",
            "content": tool_results
        })


def spawn_subagent(
    title: str,
    description: str,
    context: dict
) -> dict:
    """
    Spawn a subagent and run it to completion.

    This simulates what the Agent SDK does when Task tool is invoked.
    """

    subagent_prompt = f"""You are a specialized subagent.

TASK: {title}

DESCRIPTION:
{description}

CONTEXT:
{json.dumps(context, indent=2)}

Complete this task thoroughly. Provide structured output."""

    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": subagent_prompt}]

    # Run subagent's agentic loop
    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            return {
                "task_id": title,
                "status": "completed",
                "result": response.content[0].text if response.content else ""
            }

        # Handle any tools the subagent might use
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    # Execute subagent tools
                    result = execute_subagent_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return {"task_id": title, "status": "error"}


def parallel_subagent_spawning_example():
    """
    Example of spawning multiple subagents in parallel.

    When coordinator emits multiple Task calls in single response,
    all execute in parallel.
    """

    coordinator_prompt = """You are coordinating an analysis.

Spawn 3 specialized subagents to analyze this report:
1. Security Specialist - analyze security aspects
2. Performance Specialist - analyze performance aspects
3. Cost Specialist - analyze cost optimization

Use the Task tool to spawn each one in parallel."""

    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": coordinator_prompt}]

    tools = [{
        "name": "Task",
        "description": "Spawn subagent",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "context": {"type": "object"}
            },
            "required": ["title", "description"]
        }
    }]

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        tools=tools,
        allowedTools=["Task"],
        messages=messages
    )

    # Count Task calls - should be 3
    task_count = sum(
        1 for block in response.content
        if hasattr(block, 'type') and block.type == "tool_use" and block.name == "Task"
    )

    print(f"Spawned {task_count} subagents (should be 3)")
    print("All 3 execute in parallel")

    # Process all Task calls
    subagent_results = []
    for block in response.content:
        if block.type == "tool_use" and block.name == "Task":
            result = spawn_subagent(
                title=block.input["title"],
                description=block.input["description"],
                context=block.input.get("context", {})
            )
            subagent_results.append(result)

    return subagent_results
```

#### Structured Context Passing

```python
def pass_structured_context_to_subagent():
    """
    Example of structured context passing.

    Context should preserve metadata and structure.
    """

    # Structured claim-source mapping
    context = {
        "verification_task": {
            "type": "fact_verification",
            "claims_to_verify": [
                {
                    "id": "claim_001",
                    "statement": "Claude can process up to 200k tokens",
                    "sources": ["api_documentation", "blog_2024"],
                    "priority": "high"
                },
                {
                    "id": "claim_002",
                    "statement": "Vision capability requires claude-3-5-sonnet",
                    "sources": ["technical_docs"],
                    "priority": "medium"
                }
            ],
            "verification_criteria": {
                "required_accuracy": 0.95,
                "sources_to_check": ["official_docs", "api_spec"],
                "disallowed_sources": ["blog_speculation", "user_rumors"]
            },
            "expected_output_format": {
                "verified_claims": [
                    {"claim_id": str, "verified": bool, "evidence": str}
                ]
            }
        },
        "metadata": {
            "request_timestamp": "2026-03-22T10:00:00Z",
            "requester_id": "coordinator_main",
            "priority_level": "standard"
        }
    }

    task_invocation = {
        "title": "Verify Claude Capability Claims",
        "description": "Systematically verify the provided claims against authoritative sources",
        "context": context
    }

    return task_invocation


def preserve_metadata_in_subagent_output():
    """
    Subagents should preserve metadata in their output.

    This ensures coordinator can trace decisions and re-delegate if needed.
    """

    # Poor: Unstructured output
    poor_output = "Claims verified. Everything looks good."

    # Good: Structured output with metadata
    good_output = {
        "task_id": "verify_claims_001",
        "subagent_id": "verification_specialist_A",
        "status": "completed",
        "timestamp": "2026-03-22T10:15:30Z",
        "findings": [
            {
                "claim_id": "claim_001",
                "statement": "Claude can process up to 200k tokens",
                "verified": True,
                "confidence": 0.99,
                "evidence": [
                    {
                        "source": "https://platform.claude.com/docs",
                        "quote": "Maximum context window is 200k tokens",
                        "retrieved_date": "2026-03-22"
                    }
                ],
                "notes": "Verified against official API documentation"
            },
            {
                "claim_id": "claim_002",
                "statement": "Vision capability requires claude-3-5-sonnet",
                "verified": False,
                "confidence": 0.85,
                "evidence": [
                    {
                        "source": "model_documentation",
                        "finding": "Vision available in claude-3-5-sonnet AND other recent models",
                        "retrieved_date": "2026-03-22"
                    }
                ],
                "correction": "Vision is available in multiple models, not just claude-3-5-sonnet"
            }
        ],
        "execution_metadata": {
            "tools_used": ["search_documentation", "api_reference_lookup"],
            "execution_time_ms": 4250,
            "sources_checked": 12,
            "confidence_average": 0.92
        },
        "gaps": None
    }

    return good_output
```

### Common Exam Traps

**TRAP 1: "Task tool doesn't need to be in allowedTools"**
- **Reality:** If Task is not in `allowedTools`, coordinator can't spawn subagents.
- **Exam Answer:** Coordinator's `allowedTools` MUST include "Task" for subagent spawning.

**TRAP 2: "Multiple Task calls in one response run sequentially"**
- **Reality:** Multiple Task calls in a single response execute in parallel.
- **Exam Answer:** If coordinator emits 3 Task calls at once, all 3 run simultaneously.

**TRAP 3: "Pass context as plain text strings"**
- **Reality:** Context must be structured data (JSON objects with metadata).
- **Exam Answer:** Use structured formats like claim-source mappings with metadata preservation.

**TRAP 4: "Subagent output loses metadata"**
- **Reality:** Well-designed subagent output preserves task ID, status, metadata for re-delegation.
- **Exam Answer:** Subagent output should include task_id, status, timestamp, and execution metadata.

### Quick Reference

| Concept | Key Points |
|---------|-----------|
| **Task Tool** | Mechanism for spawning subagents |
| **allowedTools** | MUST include "Task" for coordinator to spawn |
| **Parallel Execution** | Multiple Task calls in single response = parallel |
| **Context Structure** | Use claim-source mappings, not free text |
| **Metadata Preservation** | Include task_id, status, timestamp in output |
| **Structured Output** | Maintain traceability for re-delegation |

---

## Task 1.4: Multi-Step Workflows with Enforcement and Handoff Patterns

### Conceptual Overview

Complex workflows often require:
- **Programmatic Prerequisites:** Tools can only execute if conditions are met (not optional prompting)
- **Tool Ordering:** Enforced sequences (e.g., must validate data before processing)
- **Handoff Patterns:** Passing context between workflow stages
- **Multi-Concern Decomposition:** Handling independent customer concerns in parallel with shared context

The KEY DISTINCTION: Programmatic enforcement > prompt-based guidance for critical logic.

### Deep Conceptual Explanation

#### Programmatic vs Prompt-Based Enforcement

**WRONG: Prompt-Based (unreliable for critical logic)**
```python
prompt = """Please validate the customer data before updating the database.
Try to follow this order:
1. Check email format
2. Verify phone number
3. Validate address

Then update the customer record."""

# Problem: Claude might skip validation if it deems unnecessary
# Problem: No guarantee of tool execution order
# Problem: Can't enforce prerequisites programmatically
```

**RIGHT: Programmatic (reliable for critical logic)**
```python
def execute_workflow(customer_data):
    # Step 1: ENFORCE validation before anything else
    validation_result = validate_email_format(customer_data.email)
    if not validation_result.passed:
        return {"error": "Email validation failed", "reason": validation_result.reason}

    validation_result = validate_phone_number(customer_data.phone)
    if not validation_result.passed:
        return {"error": "Phone validation failed", "reason": validation_result.reason}

    validation_result = validate_address(customer_data.address)
    if not validation_result.passed:
        return {"error": "Address validation failed", "reason": validation_result.reason}

    # Step 2: Only after ALL validations pass, execute update
    update_result = update_customer_record(customer_data)
    return update_result

# Guarantee: Validations always run in order, all must pass
# Guarantee: Update never happens without successful validations
# Guarantee: No exceptions or edge cases bypass enforcement
```

#### Tool Availability Control

Control which tools are available at each workflow stage:

```python
# Stage 1: Gathering and Validation
stage1_tools = [
    "retrieve_customer_info",
    "validate_email",
    "validate_phone",
    "validate_address"
]
# Stage 1 does NOT have: update_customer, delete_customer

# Stage 2: Processing (only after successful validation)
stage2_tools = [
    "update_customer",
    "send_confirmation_email",
    "log_transaction"
]
# Stage 2 does NOT have validation tools (already done)

# This prevents accidentally skipping validation
```

#### Multi-Concern Parallel Processing with Shared Context

```
Customer Request: "Update my address AND change my billing method AND verify my phone"

[Coordinator]
├─ Concern 1: Address Update
│  ├─ Validate new address
│  └─ Update address (prerequisites met)
│
├─ Concern 2: Billing Change  (parallel to Concern 1)
│  ├─ Validate payment method
│  ├─ Check fraud flags
│  └─ Update billing (prerequisites met)
│
└─ Concern 3: Phone Verification  (parallel to Concerns 1 & 2)
   ├─ Validate phone format
   ├─ Send OTP
   └─ Wait for verification

Shared Context: customer_id, session_token, transaction_log
```

### Python Code Examples

#### ToolExecutor with Prerequisites

```python
from typing import Callable, Any, Dict, List
from dataclasses import dataclass
from enum import Enum

class ExecutionStatus(Enum):
    BLOCKED = "blocked"
    READY = "ready"
    EXECUTED = "executed"
    FAILED = "failed"


@dataclass
class ToolDefinition:
    name: str
    description: str
    schema: Dict[str, Any]
    prerequisites: List[str]  # Names of tools that must execute first
    executor: Callable  # Actual function to run


class ToolExecutor:
    """
    Enforces tool execution order based on prerequisites.

    References: Exercise-1/agent.py - extend with prerequisite checking
    """

    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.execution_log: Dict[str, bool] = {}  # tool_name -> success

    def register_tool(self, definition: ToolDefinition):
        """Register a tool with its prerequisites."""
        self.tools[definition.name] = definition

    def can_execute_tool(self, tool_name: str) -> tuple[bool, List[str]]:
        """
        Check if tool can execute (all prerequisites met).

        Returns: (can_execute: bool, blocking_prerequisites: List[str])
        """
        if tool_name not in self.tools:
            return False, [f"Unknown tool: {tool_name}"]

        definition = self.tools[tool_name]

        blocking = []
        for prerequisite in definition.prerequisites:
            if prerequisite not in self.execution_log:
                blocking.append(prerequisite)
            elif not self.execution_log[prerequisite]:
                blocking.append(prerequisite)

        return len(blocking) == 0, blocking

    def execute_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute tool, enforcing prerequisites.
        """
        can_execute, blocking = self.can_execute_tool(tool_name)

        if not can_execute:
            return {
                "status": "blocked",
                "tool": tool_name,
                "reason": f"Blocked by prerequisites: {blocking}",
                "blocking_prerequisites": blocking
            }

        try:
            definition = self.tools[tool_name]
            result = definition.executor(**tool_input)

            success = result.get("success", True)
            self.execution_log[tool_name] = success

            return {
                "status": "executed",
                "tool": tool_name,
                "success": success,
                "result": result
            }

        except Exception as e:
            self.execution_log[tool_name] = False
            return {
                "status": "error",
                "tool": tool_name,
                "error": str(e)
            }

    def get_available_tools(self) -> List[str]:
        """Get list of tools that can execute right now."""
        available = []
        for tool_name in self.tools.keys():
            can_execute, _ = self.can_execute_tool(tool_name)
            if can_execute:
                available.append(tool_name)
        return available

    def reset(self):
        """Reset execution state."""
        self.execution_log.clear()


# Example usage
def create_customer_update_workflow() -> ToolExecutor:
    """
    Create workflow: Validate email → Validate phone → Update customer
    """
    executor = ToolExecutor()

    # Tool 1: Validate email (no prerequisites)
    executor.register_tool(ToolDefinition(
        name="validate_email",
        description="Validate email format and uniqueness",
        schema={"email": "string"},
        prerequisites=[],  # No prerequisites
        executor=lambda email: {
            "success": "@" in email,
            "valid": "@" in email
        }
    ))

    # Tool 2: Validate phone (no prerequisites)
    executor.register_tool(ToolDefinition(
        name="validate_phone",
        description="Validate phone number format",
        schema={"phone": "string"},
        prerequisites=[],  # Can run in parallel with validate_email
        executor=lambda phone: {
            "success": len(phone) >= 10,
            "valid": len(phone) >= 10
        }
    ))

    # Tool 3: Update customer (REQUIRES both validations first)
    def update_customer(customer_id: str, new_email: str, new_phone: str):
        return {
            "success": True,
            "customer_id": customer_id,
            "message": "Customer updated"
        }

    executor.register_tool(ToolDefinition(
        name="update_customer",
        description="Update customer record",
        schema={"customer_id": "string", "new_email": "string", "new_phone": "string"},
        prerequisites=["validate_email", "validate_phone"],  # MUST run first
        executor=update_customer
    ))

    return executor


def workflow_with_enforcement():
    """
    Demonstrate programmatic enforcement vs prompt-based.
    """
    executor = create_customer_update_workflow()

    # Initially, only validation tools are available
    print(f"Available tools: {executor.get_available_tools()}")
    # Output: ['validate_email', 'validate_phone']

    # Execute validations in any order (prerequisites allow both)
    result1 = executor.execute_tool("validate_email", {"email": "user@example.com"})
    print(f"Validate email: {result1['status']}")  # executed

    result2 = executor.execute_tool("validate_phone", {"phone": "1234567890"})
    print(f"Validate phone: {result2['status']}")  # executed

    # Now update is available
    print(f"Available tools after validation: {executor.get_available_tools()}")
    # Output: ['update_customer']

    # This will succeed (prerequisites met)
    result3 = executor.execute_tool("update_customer", {
        "customer_id": "cust_123",
        "new_email": "user@example.com",
        "new_phone": "1234567890"
    })
    print(f"Update customer: {result3['status']}")  # executed

    # Try to execute update without validation (if executor resets)
    executor.reset()
    result4 = executor.execute_tool("update_customer", {
        "customer_id": "cust_123",
        "new_email": "invalid",
        "new_phone": "123"
    })
    print(f"Update without validation: {result4['status']}")  # blocked
    print(f"Blocked by: {result4['blocking_prerequisites']}")
    # Output: Blocked by: ['validate_email', 'validate_phone']
```

#### Multi-Concern Parallel Processing with Shared Context

```python
@dataclass
class WorkflowContext:
    """Shared context across all concerns."""
    customer_id: str
    session_token: str
    request_timestamp: str
    shared_data: Dict[str, Any]  # Shared state between concerns

    def update_shared_data(self, key: str, value: Any):
        """Update shared context."""
        self.shared_data[key] = value

    def get_shared_data(self, key: str, default=None):
        """Read shared context."""
        return self.shared_data.get(key, default)


@dataclass
class ConcernResult:
    """Result from processing a single concern."""
    concern_id: str
    status: str  # "success", "failed", "blocked"
    result: Dict[str, Any]
    shared_context_updates: Dict[str, Any]


def process_multi_concern_request(
    customer_id: str,
    concerns: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Process multiple independent concerns in parallel with shared context.

    Example concerns:
    [
        {"type": "address_update", "new_address": "..."},
        {"type": "billing_change", "new_method": "..."},
        {"type": "phone_verify", "new_phone": "..."}
    ]
    """
    # Create shared context
    context = WorkflowContext(
        customer_id=customer_id,
        session_token=generate_session_token(),
        request_timestamp=get_timestamp(),
        shared_data={}
    )

    results = {}

    # Process each concern
    for concern in concerns:
        concern_type = concern["type"]

        if concern_type == "address_update":
            result = process_address_concern(concern, context)
        elif concern_type == "billing_change":
            result = process_billing_concern(concern, context)
        elif concern_type == "phone_verify":
            result = process_phone_concern(concern, context)
        else:
            result = ConcernResult(
                concern_id=concern_type,
                status="failed",
                result={"error": f"Unknown concern type: {concern_type}"},
                shared_context_updates={}
            )

        results[concern_type] = result

        # Update shared context with results from this concern
        for key, value in result.shared_context_updates.items():
            context.update_shared_data(key, value)

    # Check for conflicts in shared context
    conflict_check = check_shared_context_conflicts(context)

    if conflict_check["has_conflicts"]:
        return {
            "status": "conflict",
            "conflicts": conflict_check["conflicts"],
            "partial_results": results
        }

    return {
        "status": "completed",
        "results": results,
        "final_context": context.shared_data
    }


def process_address_concern(
    concern: Dict[str, Any],
    context: WorkflowContext
) -> ConcernResult:
    """Process address update concern."""

    # Validate new address
    validation = validate_address(concern["new_address"])
    if not validation["valid"]:
        return ConcernResult(
            concern_id="address_update",
            status="failed",
            result={"error": validation["error"]},
            shared_context_updates={}
        )

    # Update address
    update_result = update_customer_address(
        customer_id=context.customer_id,
        new_address=concern["new_address"],
        session_token=context.session_token
    )

    return ConcernResult(
        concern_id="address_update",
        status="success" if update_result["success"] else "failed",
        result=update_result,
        shared_context_updates={
            "address_updated": True,
            "new_address": concern["new_address"],
            "address_update_timestamp": get_timestamp()
        }
    )


def process_billing_concern(
    concern: Dict[str, Any],
    context: WorkflowContext
) -> ConcernResult:
    """Process billing method change concern."""

    # Validate payment method
    validation = validate_payment_method(concern["new_method"])
    if not validation["valid"]:
        return ConcernResult(
            concern_id="billing_change",
            status="failed",
            result={"error": validation["error"]},
            shared_context_updates={}
        )

    # Check fraud flags
    fraud_check = check_fraud_flags(
        customer_id=context.customer_id,
        new_method=concern["new_method"]
    )

    if fraud_check["flagged"]:
        return ConcernResult(
            concern_id="billing_change",
            status="blocked",
            result={"error": "Fraud check failed", "details": fraud_check},
            shared_context_updates={}
        )

    # Update billing
    update_result = update_billing_method(
        customer_id=context.customer_id,
        new_method=concern["new_method"],
        session_token=context.session_token
    )

    return ConcernResult(
        concern_id="billing_change",
        status="success" if update_result["success"] else "failed",
        result=update_result,
        shared_context_updates={
            "billing_updated": True,
            "new_billing_method": concern["new_method"],
            "billing_update_timestamp": get_timestamp()
        }
    )


def check_shared_context_conflicts(context: WorkflowContext) -> dict:
    """Check for conflicts in shared context state."""

    conflicts = []

    # Example conflict: Address update failed but billing succeeded
    # (might want to warn user about partial success)

    return {
        "has_conflicts": len(conflicts) > 0,
        "conflicts": conflicts
    }
```

### Common Exam Traps

**TRAP 1: "Use prompting to enforce prerequisites"**
- **Reality:** Prompts are suggestions. Prerequisites must be programmatic.
- **Exam Answer:** Prerequisites are enforced through code, not instructions in prompts.

**TRAP 2: "Tool availability is static throughout workflow"**
- **Reality:** Available tools change based on workflow state.
- **Exam Answer:** Different stages unlock different tools (validation stage ≠ execution stage).

**TRAP 3: "Multi-concern updates should always be sequential"**
- **Reality:** Independent concerns can run in parallel with shared context coordination.
- **Exam Answer:** Parallel processing of independent concerns, with shared context for coordination.

**TRAP 4: "Ignore failed prerequisites and proceed anyway"**
- **Reality:** Blocked tools should never execute, even if model requests them.
- **Exam Answer:** Return "blocked" status with list of blocking prerequisites.

### Quick Reference

| Concept | Key Points |
|---------|-----------|
| **Programmatic Enforcement** | Code-level prerequisites, not prompts |
| **Tool Availability Control** | Different tools for different workflow stages |
| **ToolExecutor Pattern** | Check prerequisites before execution |
| **Shared Context** | Coordinate state across parallel concerns |
| **Conflict Detection** | Check for conflicts in shared state after parallel execution |

---

## Task 1.5: Agent SDK Hooks for Tool Call Interception and Data Normalization

### Conceptual Overview

**Hooks** are callbacks that fire at specific points in the agent loop:
- **PreToolUse:** Before tool execution (can block)
- **PostToolUse:** After tool execution (can't block, but can transform)
- **OnAgentStart:** When agent starts
- **OnAgentEnd:** When agent completes

The most important for domain 1: **PostToolUse hooks for normalization and rule enforcement**.

**Key Principle:** PostToolUse hooks normalize BEFORE the model processes results (not after).

### Deep Conceptual Explanation

#### Hook Execution Points

```
Agent Loop:
    ├─ OnAgentStart hook
    │
    └─ Iteration 1:
        ├─ API call → get response
        │
        ├─ PreToolUse hook (if tool_use)
        │   └─ Can block tool execution
        │
        ├─ Execute tool
        │
        ├─ PostToolUse hook ← TRANSFORMATION POINT
        │   └─ Normalize results before model sees them
        │   └─ Can't block (tool already ran)
        │   └─ Can add context, transform output, trim data
        │
        └─ Model sees normalized tool result
           └─ Continues agentic loop

    ├─ Iteration 2...
    │
    └─ OnAgentEnd hook
```

#### PostToolUse vs PreToolUse

```python
# PreToolUse: Before execution (can block)
def pre_tool_use_hook(tool_name: str, tool_input: dict) -> dict:
    """
    Called BEFORE tool executes.
    Can prevent execution by raising exception or returning error.
    """
    if tool_name == "delete_customer" and tool_input.get("force_delete"):
        # Block dangerous operations
        raise Exception("Force delete not allowed")

    return {}  # Return empty dict to allow execution


# PostToolUse: After execution (can't block, but can transform)
def post_tool_use_hook(
    tool_name: str,
    tool_input: dict,
    tool_response: dict  # Actual result from tool
) -> dict:
    """
    Called AFTER tool executes successfully.
    Can transform the result before model processes it.
    """

    if tool_name == "search_database":
        # Normalize search results (different APIs return different formats)
        normalized = {
            "count": len(tool_response.get("items", [])),
            "items": [
                {
                    "id": item.get("id") or item.get("_id"),
                    "name": item.get("name") or item.get("title"),
                    "relevance": item.get("score") or 1.0
                }
                for item in tool_response.get("items", [])
            ]
        }
        return {
            "additionalContext": f"Normalized {len(normalized['items'])} results"
        }

    return {}  # Return empty dict for no changes
```

#### Normalization Use Cases

```python
# Use Case 1: Timestamp normalization
# API A returns: "2026-03-22T10:00:00Z"
# API B returns: "2026-03-22 10:00:00"
# API C returns: 1711099200 (Unix timestamp)

def normalize_timestamps(tool_response: dict) -> dict:
    """Normalize timestamps from different sources."""
    if "timestamp" in tool_response:
        # Parse whatever format it is
        ts = parse_timestamp(tool_response["timestamp"])
        # Return ISO 8601 standard
        normalized_ts = ts.isoformat() + "Z"
        return {
            "additionalContext": f"Timestamp normalized: {normalized_ts}"
        }
    return {}


# Use Case 2: Status code normalization
# API A returns: {"status": "success", "code": 0}
# API B returns: {"status": 200}
# API C returns: {"ok": true}

def normalize_status_codes(tool_response: dict) -> dict:
    """Normalize status indicators."""
    success = (
        tool_response.get("status") == "success" or
        tool_response.get("status") == 200 or
        tool_response.get("ok") is True or
        tool_response.get("error") is None
    )

    return {
        "additionalContext": f"Execution status: {'SUCCESS' if success else 'FAILED'}"
    }


# Use Case 3: Context trimming for verbose outputs
def trim_verbose_output(tool_response: dict) -> dict:
    """Reduce token consumption from verbose tool outputs."""

    if tool_name == "retrieve_full_audit_log":
        # Tool returns 50KB of log entries
        # Trim to most relevant
        entries = tool_response.get("entries", [])

        # Keep only recent errors or warnings
        trimmed = [
            e for e in entries[-100:]
            if e.get("level") in ["ERROR", "WARNING"]
        ]

        summary = f"Trimmed {len(entries)} entries to {len(trimmed)} relevant ones"
        return {
            "additionalContext": summary
        }

    return {}
```

#### Business Rule Enforcement via Hooks

```python
def enforce_business_rules_with_hooks():
    """
    Use PostToolUse hooks to enforce deterministic business rules.

    Example: Refund thresholds - no refund above threshold without approval
    """

    def refund_business_rule_hook(
        tool_name: str,
        tool_input: dict,
        tool_response: dict
    ) -> dict:
        """Enforce refund policy."""

        if tool_name != "process_refund":
            return {}

        refund_amount = tool_response.get("refund_amount", 0)
        requires_approval_threshold = 5000  # $5000

        # Business rule: Refunds above threshold require manager approval
        if refund_amount > requires_approval_threshold:
            # Check if approval was obtained
            approval_status = tool_response.get("manager_approval")

            if not approval_status:
                # Reject the refund and provide feedback
                return {
                    "additionalContext": (
                        f"REFUND REJECTED: Amount ${refund_amount} exceeds "
                        f"threshold ${requires_approval_threshold} and lacks "
                        f"manager approval. Obtain approval first."
                    )
                }

        return {}
```

### Python Code Examples

#### PostToolUse Hook for Normalization

```python
import anthropic
from typing import Any

def run_agent_with_posttooluse_normalization():
    """
    Agent loop with PostToolUse hooks for normalization.

    References: Exercise-1/agent.py - extend with hook registration
    """

    client = anthropic.Anthropic()

    # Define PostToolUse hook
    def normalize_tool_output(
        tool_name: str,
        tool_input: dict,
        tool_response: Any
    ) -> dict:
        """
        Normalize heterogeneous tool outputs.

        Runs BEFORE model processes the tool result.
        """

        # Normalize search results from different APIs
        if tool_name == "search_articles":
            if isinstance(tool_response, dict):
                articles = tool_response.get("results", [])
            else:
                articles = tool_response  # Might be list directly

            # Standard format
            normalized = {
                "additionalContext": f"Found {len(articles)} articles"
                # additionalContext is appended to tool result
            }
            return normalized

        # Normalize API error responses
        elif tool_name == "fetch_user_data":
            if isinstance(tool_response, dict) and "error" in tool_response:
                return {
                    "additionalContext": f"API error: {tool_response['error']}"
                }

        # Default: no transformation
        return {}

    # Tool definitions
    tools = [
        {
            "name": "search_articles",
            "description": "Search for articles",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    ]

    messages = [
        {"role": "user", "content": "Search for articles about Claude AI"}
    ]

    # Agent loop with hook
    iteration = 0
    while iteration < 10:
        iteration += 1

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            return response.content

        if response.stop_reason != "tool_use":
            break

        messages.append({"role": "assistant", "content": response.content})

        # Process tool calls with PostToolUse hook
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                # Execute tool
                tool_response = execute_tool_stub(block.name, block.input)

                # PostToolUse hook runs here
                hook_result = normalize_tool_output(
                    tool_name=block.name,
                    tool_input=block.input,
                    tool_response=tool_response
                )

                # Combine tool response with hook additions
                tool_result_content = str(tool_response)
                if hook_result.get("additionalContext"):
                    tool_result_content += f"\n[NORMALIZED] {hook_result['additionalContext']}"

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": tool_result_content
                })

        messages.append({"role": "user", "content": tool_results})


def comprehensive_posttooleuse_hook():
    """
    Comprehensive example with multiple hook patterns.
    """

    class ToolHooks:
        """Container for all hooks."""

        @staticmethod
        def normalize_timestamps(tool_name: str, tool_response: dict) -> dict:
            """Normalize timestamp formats."""
            if "timestamp" in tool_response and tool_name in ["get_events", "fetch_logs"]:
                ts = tool_response["timestamp"]
                if isinstance(ts, int):  # Unix timestamp
                    from datetime import datetime
                    iso_ts = datetime.fromtimestamp(ts).isoformat()
                else:
                    iso_ts = ts

                return {
                    "additionalContext": f"Timestamp: {iso_ts}"
                }
            return {}

        @staticmethod
        def trim_large_outputs(
            tool_name: str,
            tool_response: dict
        ) -> dict:
            """Reduce context consumption from verbose outputs."""

            if tool_name == "fetch_audit_log":
                entries = tool_response.get("entries", [])
                if len(entries) > 100:
                    # Keep recent entries
                    trimmed = entries[-50:]
                    return {
                        "additionalContext": (
                            f"Output trimmed: {len(entries)} entries → {len(trimmed)} recent"
                        )
                    }

            return {}

        @staticmethod
        def enforce_refund_rules(
            tool_name: str,
            tool_response: dict
        ) -> dict:
            """Enforce business rule: refund threshold."""

            if tool_name == "process_refund":
                amount = tool_response.get("amount", 0)

                # Business rule: >$5000 needs approval
                if amount > 5000 and not tool_response.get("approved_by_manager"):
                    return {
                        "additionalContext": (
                            f"REJECTED: Refund ${amount} requires manager approval. "
                            f"Resubmit with approval."
                        )
                    }

            return {}

        @staticmethod
        def apply_all_hooks(
            tool_name: str,
            tool_input: dict,
            tool_response: dict
        ) -> dict:
            """Apply all hooks in sequence."""

            results = []

            # Apply each hook
            hook_results = [
                ToolHooks.normalize_timestamps(tool_name, tool_response),
                ToolHooks.trim_large_outputs(tool_name, tool_response),
                ToolHooks.enforce_refund_rules(tool_name, tool_response)
            ]

            # Combine all results
            additional_context_parts = [
                h.get("additionalContext")
                for h in hook_results
                if h.get("additionalContext")
            ]

            if additional_context_parts:
                return {
                    "additionalContext": "\n".join(additional_context_parts)
                }

            return {}

    return ToolHooks


def execute_tool_stub(tool_name: str, tool_input: dict):
    """Stub tool executor for examples."""
    return {
        "status": "success",
        "tool": tool_name,
        "input": tool_input
    }
```

### Common Exam Traps

**TRAP 1: "PostToolUse hooks run after the model processes results"**
- **Reality:** PostToolUse hooks run immediately after tool execution, BEFORE model processes.
- **Exam Answer:** PostToolUse hooks normalize BEFORE model sees the result.

**TRAP 2: "PreToolUse hooks can transform output after execution"**
- **Reality:** PreToolUse runs before execution. PostToolUse runs after.
- **Exam Answer:** Use PreToolUse to block, PostToolUse to transform.

**TRAP 3: "Hook context trimming happens at response time"**
- **Reality:** Hooks trim during tool result processing, reducing tokens for model input.
- **Exam Answer:** Hooks normalize and trim early to reduce context consumption.

**TRAP 4: "Business rules enforcement must happen in prompts"**
- **Reality:** Hooks enforce rules deterministically, prompts are suggestions.
- **Exam Answer:** Use hooks for mandatory business rules (refund thresholds, etc).

### Quick Reference

| Concept | Key Points |
|---------|-----------|
| **PostToolUse Timing** | Runs BEFORE model processes result |
| **Normalization** | Convert heterogeneous outputs to standard format |
| **Context Trimming** | Reduce verbose output tokens early |
| **Business Rules** | Use hooks for deterministic enforcement |
| **additionalContext** | Appended to tool result for model to see |

---

## Task 1.6: Task Decomposition Strategies for Complex Workflows

### Conceptual Overview

Two primary decomposition strategies:

1. **Prompt Chaining:** Sequential focused passes on known-structure problems
   - Use when workflow structure is KNOWN and PREDICTABLE
   - Each pass has focused, well-defined goal
   - Good for: step-by-step analysis, structured transformations

2. **Dynamic Adaptive Decomposition:** Iterative investigation when scope is UNKNOWN
   - Use when problem scope cannot be determined in advance
   - Agent explores iteratively, decides on next steps
   - Good for: open-ended investigations, research, discovery

**Key Exam Point:** Choose the right strategy based on whether workflow structure is known.

### Deep Conceptual Explanation

#### Prompt Chaining (Known Structure)

```
Input: Customer complaint

Step 1: Categorization
  Input: Raw complaint text
  Prompt: "Categorize this complaint into one of: billing, technical, service quality"
  Output: {category, confidence}

Step 2: Root Cause Analysis
  Input: Complaint + category
  Prompt: "Analyze the root cause of this {category} complaint"
  Output: {root_cause, supporting_evidence}

Step 3: Resolution Recommendation
  Input: Complaint + category + root_cause
  Prompt: "Recommend resolution based on this {root_cause}"
  Output: {recommendation, estimated_cost, timeline}

Step 4: Policy Check
  Input: Complaint + recommendation
  Prompt: "Verify if this resolution complies with our policies"
  Output: {compliant, policy_references, modifications_needed}

Step 5: Final Response
  Input: All previous outputs
  Prompt: "Draft response to customer incorporating all analysis"
  Output: {response_text}

Each step feeds into the next with focused, specific goal.
```

**When to use:** Known workflow structure, predictable steps, well-defined stages.

#### Dynamic Adaptive Decomposition (Unknown Scope)

```
Input: Research task "Find all security vulnerabilities in codebase"

Agent Loop:
  Iteration 1:
    Agent: "I should scan for common vulnerability patterns"
    → Searches for: SQL injection, XSS, auth bypass
    → Finds: 3 SQL injection risks

  Iteration 2:
    Agent: "I need to check for more subtle issues"
    → Searches for: timing attacks, side channels, crypto issues
    → Finds: 2 timing vulnerability candidates

  Iteration 3:
    Agent: "Should verify these findings and check for logic errors"
    → Investigates: business logic flaws, state management
    → Finds: 1 critical race condition

  Iteration 4:
    Agent: "I think I've covered the major categories. Let me summarize."
    → Compilation of findings
    → Total vulnerabilities found: 6
    → Confidence: "Likely complete for known vulnerability classes"

Agent itself decides when additional investigation is needed.
```

**When to use:** Unknown problem scope, discovery needed, exploratory research.

### Python Code Examples

#### Prompt Chaining Implementation

```python
def prompt_chaining_workflow(complaint: str) -> dict:
    """
    Prompt chaining for known-structure complaint resolution.

    Structure: Categorize → Root cause → Recommendation → Verify → Response
    """
    client = anthropic.Anthropic()

    # Step 1: Categorization
    print("Step 1: Categorizing complaint...")
    categorization_prompt = f"""Categorize this customer complaint into exactly one category:

Complaint: {complaint}

Categories: billing, technical, service_quality, product_defect, other

Respond with JSON: {{"category": "...", "confidence": 0.0}}"""

    response1 = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=256,
        messages=[{"role": "user", "content": categorization_prompt}]
    )

    category_result = parse_json(response1.content[0].text)
    category = category_result["category"]

    # Step 2: Root Cause Analysis
    print(f"Step 2: Analyzing root cause for {category}...")
    root_cause_prompt = f"""Analyze the root cause of this {category} complaint:

Complaint: {complaint}

Provide JSON: {{"root_cause": "...", "evidence": [...], "severity": 1-10}}"""

    response2 = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,
        messages=[{"role": "user", "content": root_cause_prompt}]
    )

    root_cause_result = parse_json(response2.content[0].text)

    # Step 3: Recommendation
    print("Step 3: Generating recommendation...")
    recommendation_prompt = f"""Based on this {category} complaint with root cause:

{root_cause_result['root_cause']}

Recommend a resolution. Provide JSON:
{{"recommendation": "...", "cost": 0.0, "timeline_hours": 0}}"""

    response3 = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,
        messages=[{"role": "user", "content": recommendation_prompt}]
    )

    recommendation = parse_json(response3.content[0].text)

    # Step 4: Policy Verification
    print("Step 4: Verifying against policies...")
    policy_check_prompt = f"""Check if this recommendation complies with our policies:

Recommendation: {recommendation['recommendation']}

Policies:
- No refunds over $500 without manager approval
- No service improvements promised without feasibility check
- All resolutions must have documented timeline

Provide JSON: {{"compliant": true/false, "issues": [], "required_approvals": []}}"""

    response4 = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,
        messages=[{"role": "user", "content": policy_check_prompt}]
    )

    policy_check = parse_json(response4.content[0].text)

    # Step 5: Final Response
    print("Step 5: Drafting customer response...")
    final_response_prompt = f"""Draft a customer-facing response incorporating:

Complaint: {complaint}
Category: {category}
Root Cause: {root_cause_result['root_cause']}
Recommendation: {recommendation['recommendation']}
Policy Check: {'PASSED' if policy_check['compliant'] else 'FAILED - ' + str(policy_check['issues'])}

Write professional response addressing the complaint."""

    response5 = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": final_response_prompt}]
    )

    return {
        "step1_categorization": category_result,
        "step2_root_cause": root_cause_result,
        "step3_recommendation": recommendation,
        "step4_policy_check": policy_check,
        "step5_response": response5.content[0].text
    }


def compare_prompt_chaining():
    """
    Show why prompt chaining is better for known structure.
    """

    # WRONG: Try to do everything in one call (less focused)
    wrong_prompt = """Process this complaint comprehensively:

Complaint: [...]

Categorize it, analyze root cause, provide recommendation,
check policies, draft response."""

    # RIGHT: Sequential focused prompts
    # Each prompt focuses on ONE specific task
    # Each can optimize for its specific goal
    # Results flow naturally from one to next

    return {
        "wrong": "Single large prompt - less focused, harder to verify each step",
        "right": "Chain of focused prompts - verifiable, correctable, optimizable"
    }
```

#### Dynamic Adaptive Decomposition

```python
def dynamic_adaptive_decomposition(research_query: str) -> dict:
    """
    Dynamic decomposition for open-ended investigation.

    Agent itself decides on next investigation steps.
    """
    client = anthropic.Anthropic()

    investigation_state = {
        "query": research_query,
        "findings": [],
        "areas_investigated": [],
        "areas_to_investigate": [],
        "iteration": 0
    }

    max_iterations = 10

    while investigation_state["iteration"] < max_iterations:
        investigation_state["iteration"] += 1

        # Create prompt for current iteration
        iteration_prompt = create_adaptive_iteration_prompt(
            query=research_query,
            findings=investigation_state["findings"],
            areas_investigated=investigation_state["areas_investigated"],
            iteration=investigation_state["iteration"]
        )

        # Get agent's decision on what to investigate next
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{"role": "user", "content": iteration_prompt}]
        )

        # Parse agent's decision
        decision = parse_investigation_decision(response.content[0].text)

        print(f"\nIteration {investigation_state['iteration']}:")
        print(f"  Investigation area: {decision['next_area']}")
        print(f"  Findings: {len(decision['findings'])} new items")

        # Update state
        investigation_state["findings"].extend(decision["findings"])
        investigation_state["areas_investigated"].append(decision["next_area"])

        # Check if agent decides investigation is complete
        if decision["investigation_complete"]:
            print(f"Investigation complete after {investigation_state['iteration']} iterations")
            break

        # Check if new areas to investigate
        if decision.get("next_areas"):
            investigation_state["areas_to_investigate"] = decision["next_areas"]

    return {
        "query": research_query,
        "total_iterations": investigation_state["iteration"],
        "areas_investigated": investigation_state["areas_investigated"],
        "findings": investigation_state["findings"]
    }


def create_adaptive_iteration_prompt(
    query: str,
    findings: list,
    areas_investigated: list,
    iteration: int
) -> str:
    """Create prompt for current iteration of investigation."""

    current_findings_str = "\n".join(
        f"  - {f}" for f in findings
    ) if findings else "  (none yet)"

    prompt = f"""You are investigating: {query}

PREVIOUS FINDINGS (Iteration {iteration}):
{current_findings_str}

AREAS ALREADY INVESTIGATED:
{format_areas(areas_investigated) if areas_investigated else "  (none yet)"}

Now decide your next step:
1. What NEW area should you investigate?
2. What did you find in that area?
3. Are there more areas to investigate? Or are you done?

Think carefully - you're trying to ensure complete coverage.

Respond with JSON:
{{
  "next_area": "specific area to investigate",
  "findings": ["finding1", "finding2"],
  "next_areas": ["area1", "area2"],
  "investigation_complete": true/false,
  "reasoning": "why this is complete or what's next"
}}"""

    return prompt


def parse_investigation_decision(response_text: str) -> dict:
    """Parse agent's investigation decision."""
    # Extract JSON from response
    import json
    import re

    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())

    return {}


def choose_decomposition_strategy(problem_description: str) -> str:
    """
    Help choose between prompt chaining and dynamic decomposition.
    """

    # Indicators for Prompt Chaining (known structure)
    known_structure_indicators = [
        "step-by-step",
        "process",
        "workflow",
        "pipeline",
        "stages",
        "phases",
        "sequential",
        "stages are"
    ]

    # Indicators for Dynamic Decomposition (unknown scope)
    unknown_scope_indicators = [
        "find all",
        "discover",
        "explore",
        "investigate",
        "research",
        "unknown",
        "scope",
        "comprehensive search"
    ]

    problem_lower = problem_description.lower()

    known_count = sum(
        1 for indicator in known_structure_indicators
        if indicator in problem_lower
    )

    unknown_count = sum(
        1 for indicator in unknown_scope_indicators
        if indicator in problem_lower
    )

    if known_count > unknown_count:
        return "prompt_chaining"
    elif unknown_count > known_count:
        return "dynamic_decomposition"
    else:
        return "hybrid"  # Use both as appropriate
```

### Common Exam Traps

**TRAP 1: "Always use dynamic decomposition for flexibility"**
- **Reality:** Prompt chaining is more efficient when structure is known.
- **Exam Answer:** Use prompt chaining for known structure, dynamic for unknown scope.

**TRAP 2: "Prompt chaining requires more API calls"**
- **Reality:** Yes, but each call is more focused and cheaper overall.
- **Exam Answer:** More calls but smaller, focused - better for accuracy.

**TRAP 3: "Dynamic decomposition continues until token limit"**
- **Reality:** Agent decides when investigation is complete based on findings.
- **Exam Answer:** Agent evaluates completeness, not just resource limits.

**TRAP 4: "Can't use both strategies in same workflow"**
- **Reality:** Hybrid approach possible - chaining for known parts, dynamic for unknown.
- **Exam Answer:** Choose strategy per subworkflow based on whether structure is known.

### Quick Reference

| Concept | Use When | Characteristics |
|---------|----------|-----------------|
| **Prompt Chaining** | Structure known | Sequential, focused, predictable |
| **Dynamic Decomposition** | Scope unknown | Iterative, exploratory, adaptive |
| **Hybrid** | Mixed problems | Chaining for known parts, dynamic for discovery |

---

## Task 1.7: Session State, Resumption, and Forking

### Conceptual Overview

Claude Code (and Agent SDK) provide session management capabilities:

- **`--resume SESSION_NAME`:** Continue a previous session, get notified of file changes
- **`fork_session`:** Create divergent exploration from shared baseline
- **`/compact`:** Trim context history to reduce token usage

These enable building sophisticated workflows with long-running agents.

### Deep Conceptual Explanation

#### Session Resumption

```
Day 1:
  user> Start analysis of codebase
  claude> [analyzes, creates plans, findings]
  user> /stop

  → Session saved as "codebase-analysis-001"

Day 2:
  user> claude-code --resume codebase-analysis-001
  claude> "Session resumed. Detected file changes:
           - modified: src/app.py
           - deleted: config/old.json

           What would you like to continue with?"

  → Full conversation history available
  → Agent aware of what changed since last session
  → Can pick up where it left off
```

**Key Value:** Long-running analysis, multi-session projects, persistent investigations.

#### Session Forking

```
Main Session - Testing Architecture:
  [Shared baseline investigation of 3 architectures]

  → Agent decides to explore two architectures in parallel:

  Fork-A: Deep dive on Microservices
    [Specialized investigation]
    [Parallel to Fork-B]

  Fork-B: Deep dive on Monolithic
    [Specialized investigation]
    [Parallel to Fork-A]

  Main session can:
  - Review both fork results
  - Re-synthesize comparison
  - Choose best direction
```

**Key Value:** Parallel exploration, alternative analysis paths, divergent investigation.

### Python Code Examples

#### Session Management Pattern

```python
import subprocess
import json
from datetime import datetime

class SessionManager:
    """Manage Claude Code sessions for long-running workflows."""

    @staticmethod
    def create_session(name: str, initial_prompt: str) -> str:
        """Create new named session."""
        cmd = ["claude-code", "--session", name]
        # Initial prompt provided to session
        return name

    @staticmethod
    def resume_session(session_name: str) -> dict:
        """
        Resume session and get context about changes.

        Returns notification of:
        - Modified files
        - Deleted files
        - Session history available
        """
        cmd = ["claude-code", "--resume", session_name]
        # Claude Code returns session context and change notifications
        return {
            "session_name": session_name,
            "resumed": True,
            "file_changes": {
                "modified": [],
                "deleted": [],
                "created": []
            }
        }

    @staticmethod
    def fork_session(parent_session: str, fork_name: str) -> str:
        """
        Fork session for divergent exploration.

        Child inherits parent's full conversation and state.
        Changes in child don't affect parent.
        """
        # Creates new session as copy of parent
        return fork_name

    @staticmethod
    def list_sessions() -> list:
        """List all available sessions."""
        return [
            {"name": "session-1", "created": "2026-03-20", "type": "main"},
            {"name": "session-1-fork-a", "created": "2026-03-21", "type": "fork"}
        ]


def long_running_analysis_with_resumption():
    """
    Example: Multi-day code analysis with session resumption.
    """

    # Day 1: Initial analysis
    session = SessionManager.create_session(
        name="architecture-analysis",
        initial_prompt="""Analyze the codebase architecture:
        1. Identify core modules
        2. Map dependencies
        3. Identify issues

        Focus on structure first."""
    )

    # ... Agent does analysis, creates findings
    # User pauses: /stop

    # Day 2: Resume and continue
    context = SessionManager.resume_session("architecture-analysis")
    # Context includes:
    # - Modified files since last session
    # - Full conversation history
    # - Current findings

    if context["file_changes"]["modified"]:
        # Agent can re-analyze modified components
        print(f"Files changed: {context['file_changes']['modified']}")
        print("Re-analyzing changed components...")


def parallel_exploration_with_forking():
    """
    Example: Parallel exploration of alternatives using fork_session.
    """

    # Main session: Establish baseline understanding
    main_session = SessionManager.create_session(
        name="design-comparison",
        initial_prompt="""Compare 3 system design options:
        1. Microservices
        2. Monolithic
        3. Serverless

        Document trade-offs for each."""
    )

    # ... Agent analyzes all three options at high level

    # Create forks for deep dives
    fork_microservices = SessionManager.fork_session(
        parent_session="design-comparison",
        fork_name="design-comparison-fork-microservices"
    )

    fork_monolithic = SessionManager.fork_session(
        parent_session="design-comparison",
        fork_name="design-comparison-fork-monolithic"
    )

    # Forks run in parallel (different processes/sessions)
    # Fork-A: Deep dive into Microservices
    #   - Detailed architecture
    #   - Implementation patterns
    #   - Operational complexity

    # Fork-B: Deep dive into Monolithic
    #   - Deployment strategy
    #   - Scaling challenges
    #   - Team coordination

    # Later, main session can:
    # - Review results from both forks
    # - Synthesize comparison
    # - Make recommendation


def context_optimization_with_compact():
    """
    Example: Optimize context with /compact command.
    """

    # After many iterations, conversation history grows
    # (many tool calls, results, analysis)

    # User invokes: /compact

    # Claude Code returns:
    # "Summarizing conversation history for efficiency...
    #  Trimmed from 50KB to 15KB
    #  Preserved: Key findings, active context
    #  Removed: Repetitive exploration, completed tasks"

    # Continued analysis benefits from:
    # - Reduced token consumption
    # - Faster API responses
    # - Same context preservation
```

### Common Exam Traps

**TRAP 1: "Forking creates independent copies that can't be reconciled"**
- **Reality:** Forks are independent but can be manually reviewed and synthesized.
- **Exam Answer:** Forking enables parallel exploration; results must be manually integrated.

**TRAP 2: "--resume loses file context"**
- **Reality:** Resumption includes notification of what changed since last session.
- **Exam Answer:** Resume provides agent with change notifications for re-analysis.

**TRAP 3: "/compact deletes conversation history"**
- **Reality:** Compact summarizes and preserves key context while reducing tokens.
- **Exam Answer:** Compact maintains context while reducing history size.

**TRAP 4: "Sessions are only for interactive use"**
- **Reality:** Sessions can be used in workflows for persistence and state management.
- **Exam Answer:** Sessions enable multi-step, long-running agent workflows.

### Quick Reference

| Concept | Purpose |
|---------|---------|
| **--resume** | Continue previous session, get change notifications |
| **fork_session** | Parallel exploration from shared baseline |
| **Merged results** | Manual synthesis of fork findings |
| **/compact** | Reduce context size while preserving key state |

---

## Quick Reference Cheatsheet

### Agentic Loop Termination (Task 1.1)
```python
# PRIMARY termination condition
if response.stop_reason == "end_turn":
    return result  # Agent completed

# Tool processing
elif response.stop_reason == "tool_use":
    execute_tools()
    continue_loop()

# Safety guardrails (secondary)
if iteration >= max_iterations:
    force_terminate()  # Prevents infinite loops
```

### Multi-Agent Coordination (Task 1.2)
```python
# Dynamic routing (not keyword-based)
route_plan = coordinator.analyze_query(query)

# Invoke subagents
for subagent_id, task in route_plan.items():
    spawn_subagent(subagent_id, task)

# Evaluate and re-delegate
evaluation = evaluate_outputs(outputs)
if evaluation.gaps:
    for gap in evaluation.gaps:
        refined_output = invoke_subagent(gap)
```

### Subagent Spawning (Task 1.3)
```python
# CRITICAL: Task must be in allowedTools
allowedTools=["Task", "Read", "Glob"]

# Structured context passing
context = {
    "claims": [{"id": "...", "text": "..."}],
    "verification_criteria": {...}
}

# Parallel execution (multiple Task calls in one response)
# All execute simultaneously if emitted together
```

### Workflow Enforcement (Task 1.4)
```python
# Programmatic prerequisites (not prompt-based)
class ToolExecutor:
    def can_execute(tool):
        if tool.prerequisites not satisfied:
            return False, blocking_list
        return True, []

# Multi-concern parallel processing with shared context
for concern in concerns:
    result = process_concern(concern, shared_context)
    shared_context.update(result)
```

### SDK Hooks (Task 1.5)
```python
# PostToolUse: normalize BEFORE model processes
def post_tool_use(tool_name, tool_input, tool_response):
    normalized = normalize(tool_response)
    return {"additionalContext": normalized}

# Business rule enforcement
if tool_name == "refund" and amount > threshold:
    return {"additionalContext": "REJECTED: requires approval"}
```

### Task Decomposition (Task 1.6)
```python
# Known structure → Prompt Chaining
step1_result = run_focused_prompt(prompt1)
step2_result = run_focused_prompt(prompt2, step1_result)
step3_result = run_focused_prompt(prompt3, step2_result)

# Unknown scope → Dynamic Decomposition
while not investigation_complete:
    decision = agent.decide_next_steps()
    findings.extend(decision.findings)
```

### Session Management (Task 1.7)
```python
# Resumption preserves context and change notifications
claude-code --resume session-name

# Forking enables parallel exploration
fork_session(parent="main", child="fork-a")

# Context optimization
/compact  # Reduces history while preserving state
```

---

## Exam Traps and Distractors

### Critical Trap Patterns

1. **Iteration Caps as Primary Termination**
   - WRONG: Treat iteration count as primary termination
   - RIGHT: `stop_reason == "end_turn"` is primary; iteration caps are safety
   - Questions disguise this with phrasing like "when does the loop finally exit?"

2. **Static vs Dynamic Routing**
   - WRONG: Use keyword matching for multi-agent routing
   - RIGHT: Dynamically evaluate query complexity to determine routing
   - Questions ask "how should coordinator decide which subagent to use?"

3. **Tool Availability and allowedTools**
   - WRONG: Assume Task tool is available by default
   - RIGHT: Task MUST be explicitly in allowedTools for subagent spawning
   - Questions present scenarios where Task isn't invoked when it should be

4. **Tool Results as Assistant vs User Messages**
   - WRONG: Append tool results as assistant message
   - RIGHT: Tool results are user messages in conversation history
   - Questions about conversation history structure

5. **Sequential vs Parallel Tool Calls**
   - WRONG: Assume multiple Task calls execute sequentially
   - RIGHT: Multiple Task calls in single response execute in parallel
   - Questions about agent team parallelism

6. **Prompt-Based vs Programmatic Enforcement**
   - WRONG: Use prompts to enforce critical prerequisites
   - RIGHT: Use code-level enforcement, prompts are suggestions
   - Questions about business rule reliability

7. **Hook Timing (PostToolUse Before vs After)**
   - WRONG: PostToolUse runs after model processes result
   - RIGHT: PostToolUse runs immediately after execution, before model
   - Questions about when normalization happens

8. **Prompt Chaining vs Dynamic Decomposition**
   - WRONG: Always use dynamic decomposition for flexibility
   - RIGHT: Chaining for known structure, dynamic for unknown scope
   - Questions present problems asking which strategy fits

9. **Session Forking Independence**
   - WRONG: Forks automatically merge back to main session
   - RIGHT: Forks are independent; results must be manually synthesized
   - Questions about fork results consolidation

10. **Context Trimming Timing**
    - WRONG: Trim context at response time (too late)
    - RIGHT: Trim in PostToolUse hook early to reduce model input
    - Questions about context optimization strategy

### Question Type Patterns

**Pattern A: "How does agent know when to stop?"**
- Correct answer involves `stop_reason == "end_turn"`
- Incorrect options mention iteration counts or max_tokens as primary

**Pattern B: "How should coordinator decide routing?"**
- Correct answer: dynamic analysis of requirements
- Incorrect: static keyword matching

**Pattern C: "How do multiple subagents execute?"**
- Correct answer: parallel if multiple Task calls in same response
- Incorrect: sequential execution

**Pattern D: "What prevents critical business logic errors?"**
- Correct answer: programmatic enforcement with hooks or ToolExecutor
- Incorrect: prompt-based guidance

**Pattern E: "When does tool result normalization occur?"**
- Correct answer: PostToolUse hook, before model processes
- Incorrect: after model response

---

## References and Further Reading

### Official Documentation
- [Claude Agent SDK Overview](https://platform.claude.com/docs/en/agent-sdk/overview)
- [How the Agent Loop Works](https://platform.claude.com/docs/en/agent-sdk/agent-loop)
- [Handling Stop Reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons)
- [Agent SDK Hooks Reference](https://platform.claude.com/docs/en/agent-sdk/hooks)
- [Claude Code Documentation](https://code.claude.com/docs)
- [Claude Code Agent Teams](https://code.claude.com/docs/en/agent-teams)

### Key Concepts by Task
- **Task 1.1:** [Agent Loop Documentation](https://platform.claude.com/docs/en/agent-sdk/agent-loop)
- **Task 1.2:** [Claude Code Agent Teams](https://code.claude.com/docs/en/agent-teams)
- **Task 1.3:** [Agent SDK Quickstart](https://platform.claude.com/docs/en/agent-sdk/quickstart)
- **Task 1.4:** [Intercept and Control with Hooks](https://platform.claude.com/docs/en/agent-sdk/hooks)
- **Task 1.5:** [Hooks Reference](https://code.claude.com/docs/en/hooks)
- **Task 1.6:** Task decomposition principles from Agent SDK docs
- **Task 1.7:** Claude Code session management

### Recommended Practice
- Review Exercise-1/agent.py for base agentic loop pattern
- Implement variations of ToolExecutor for prerequisite enforcement
- Practice creating coordinator + subagent patterns
- Experiment with prompt chaining vs dynamic decomposition

---

## Summary by Task

| Task | Core Concept | Key Principle | Exam Focus |
|------|--------------|---------------|-----------|
| 1.1 | Agentic Loops | `stop_reason == "end_turn"` is primary | Loop termination, tool processing |
| 1.2 | Multi-Agent | Dynamic routing, output evaluation | Coordinator pattern, re-delegation |
| 1.3 | Subagent Spawning | Task in allowedTools, parallel execution | Context passing, metadata preservation |
| 1.4 | Workflow Enforcement | Programmatic > prompt-based | Prerequisites, tool ordering |
| 1.5 | SDK Hooks | PostToolUse before model processes | Normalization, business rules |
| 1.6 | Decomposition | Known structure → chaining; unknown → dynamic | Strategy selection |
| 1.7 | Sessions | Resumption = continuity; forking = parallel | State management, exploration patterns |

---

**Document Version:** 1.0
**Domain:** 1 - Agentic Architecture & Orchestration
**Exam Coverage:** 27% (19 questions: Q1, Q7-Q9, Q13-Q29)
**Last Updated:** March 2026
