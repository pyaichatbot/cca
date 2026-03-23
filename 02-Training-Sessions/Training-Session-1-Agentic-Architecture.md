# Training Session 1: Agentic Architecture & Orchestration
## Claude Certified Architect – Foundations

**Duration:** 2.5 hours | **Domain Weight:** 27% (highest-weighted domain)
**Prerequisites:** Basic familiarity with Claude API, Python or TypeScript, understanding of API calls and JSON

---

## Session Overview

Domain 1 is the **largest weighted domain** on the CCA Foundations exam (27%, or ~19 questions). This session covers the architecture patterns that make Claude agents autonomous, scalable, and reliable. You'll learn how to design agentic loops, orchestrate multi-agent systems, enforce task completion, and manage complex agent lifecycles.

The key insight: **Agentic systems are not about prompting harder—they're about architectural design**. We use stop_reason to drive control flow, structured patterns to coordinate agents, and programmatic enforcement to guarantee compliance. This is where theoretical prompting knowledge meets production systems design.

---

## Learning Objectives

By the end of this session, you will be able to:

1. **Design and implement agentic loops** using stop_reason-driven control flow, avoiding prompt-parsing anti-patterns
2. **Orchestrate multi-agent systems** with coordinator-subagent patterns, dynamic routing, and context isolation
3. **Configure subagent invocation** with the Task tool, explicit context passing, and appropriate session management
4. **Implement multi-step workflows** with programmatic enforcement, handoff protocols, and prerequisite gates
5. **Apply Agent SDK hooks** (PostToolUse) for deterministic compliance, tool call interception, and data normalization
6. **Design task decomposition strategies** that balance fixed pipelines with adaptive exploration
7. **Manage agent session state** with resumption, forking, and lifecycle awareness

---

## Part 1: Agentic Loops (Task 1.1) — 30 minutes

### Concept: The Agentic Loop Lifecycle

An **agentic loop** is the core pattern that makes an agent autonomous. Instead of a single request-response, the loop iterates:

1. Agent receives a goal and tools
2. Agent responds with `stop_reason: "tool_use"` (wants to call a tool)
3. System appends tool results to conversation
4. Loop continues until `stop_reason: "end_turn"` (agent is done)

This is fundamentally different from chaining sequential API calls. The agent **drives the control flow**, not you.

### Key Mechanism: stop_reason

The `stop_reason` field in the response is your control signal:

- **`tool_use`**: Model wants to call one or more tools. Append the tool results and continue the loop.
- **`end_turn`**: Model has finished. No more tool calls needed. Extract the final message.
- **`max_tokens`** (rare): Model ran out of tokens mid-response. Rare in practice but worth handling.

This is NOT the same as parsing natural language to decide what to do. **Never implement decision logic based on the text of the response**—always use stop_reason.

### Code Walkthrough: Research Agent Loop

```python
import anthropic
import json

def research_agent_loop(query: str) -> str:
    """
    Implements a simple research agent that iteratively calls tools.
    Tools available: web_search, summarize, fact_check.
    """
    client = anthropic.Anthropic()
    model = "claude-opus-4-1-20250805"

    # Define available tools
    tools = [
        {
            "name": "web_search",
            "description": "Search the web for information",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "summarize",
            "description": "Summarize a piece of text",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to summarize"}
                },
                "required": ["text"]
            }
        }
    ]

    # Initialize conversation with the user's query
    messages = [
        {
            "role": "user",
            "content": f"Research and summarize the following: {query}"
        }
    ]

    # Tool simulation function
    def execute_tool(tool_name: str, tool_input: dict) -> str:
        if tool_name == "web_search":
            # Simulated search result
            return json.dumps({
                "results": [
                    {"title": "Example Result", "content": "This is example content from a search."}
                ]
            })
        elif tool_name == "summarize":
            return f"Summary: The text discusses {tool_input['text'][:50]}..."
        return "Tool not found"

    # Agentic loop
    while True:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        print(f"Stop reason: {response.stop_reason}")

        # Critical decision point: based on stop_reason, not text parsing
        if response.stop_reason == "end_turn":
            # Agent is done. Extract final text response.
            final_text = next(
                (block.text for block in response.content if hasattr(block, "text")),
                "No response"
            )
            return final_text

        elif response.stop_reason == "tool_use":
            # Agent wants to call tools. Process all tool uses and append results.
            tool_uses = [block for block in response.content if block.type == "tool_use"]

            if not tool_uses:
                # Safety: stop_reason is tool_use but no tool_use blocks found
                # This should not happen in normal operation
                break

            # Append assistant's response (containing the tool use requests)
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool and collect results
            tool_results = []
            for tool_use in tool_uses:
                result = execute_tool(tool_use.name, tool_use.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result
                })

            # Append all tool results in a single user message
            messages.append({"role": "user", "content": tool_results})

        else:
            # Unexpected stop reason (max_tokens, etc.)
            print(f"Unexpected stop reason: {response.stop_reason}")
            break

    return "Agent failed to complete"
```

### Key Insights

1. **The loop drives everything.** The agent decides whether to call tools or finish—you just respond to stop_reason.
2. **Tool results are always appended as user messages.** This is how the agent sees the outcome of its actions.
3. **No iteration caps as a primary mechanism.** Some agents might need 3 tool calls, others need 15. The agent knows when it's done; trust stop_reason.
4. **Batch tool calls.** If the agent returns multiple tool_use blocks, execute them all before the next loop iteration.

### Common Exam Traps

**TRAP 1: Parsing natural language to detect completion**
- ❌ WRONG: `if "complete" in response.text or "finished" in response.text`
- ✅ RIGHT: `if response.stop_reason == "end_turn"`

**TRAP 2: Stopping the loop early based on a heuristic iteration count**
- ❌ WRONG: `for i in range(5): ...` (arbitrary cap prevents agent from solving harder problems)
- ✅ RIGHT: Let the loop continue until `stop_reason == "end_turn"`

**TRAP 3: Not appending tool results correctly**
- ❌ WRONG: Appending only the tool names or a summary of results
- ✅ RIGHT: Appending the complete tool result objects with the tool_use_id linking

**TRAP 4: Forgetting to check if tool_use blocks exist when stop_reason is tool_use**
- Edge case, but stop_reason can be tool_use with no actual tool_use blocks in rare cases. Always validate.

### Practice Question

**Q1.1:** You're implementing an agentic loop. The response has `stop_reason: "tool_use"` but your code finds zero tool_use blocks in response.content. What should you do?

A) Continue the loop and append an empty user message
B) Treat this as end_turn and return the final response
C) Throw an error immediately
D) Log a warning and break the loop

**Answer: D.** This is an edge case that shouldn't happen, but it's safer to log and break rather than create an infinite loop or crash. In production, you'd also want to alert monitoring.

---

## Part 2: Multi-Agent Coordination (Tasks 1.2, 1.3) — 40 minutes

### Concept: Coordinator-Subagent Architecture

When a single agent isn't enough, we use a **hub-and-spoke** (coordinator-subagent) pattern:

- **Coordinator**: Understands the high-level goal, decides which subagents to invoke, aggregates results
- **Subagents**: Specialized agents with narrower scope (e.g., "code reviewer", "security analyst", "performance tester")
- **Isolation**: Each subagent has its own context and tool set; no automatic inheritance

This pattern scales to hundreds of agents and enables parallel execution.

### The Task Tool and AgentDefinition

The **Task tool** is how coordinators invoke subagents in the Agent SDK:

```python
{
    "name": "Task",
    "description": "Invoke a subagent to complete a subtask",
    "input_schema": {
        "type": "object",
        "properties": {
            "subagent_id": {
                "type": "string",
                "description": "ID of the subagent to invoke"
            },
            "task": {
                "type": "string",
                "description": "The task prompt for the subagent"
            }
        },
        "required": ["subagent_id", "task"]
    }
}
```

Requirements:
- The **coordinator** must have "Task" in its `allowedTools` configuration
- **Subagents are defined in AgentDefinition**, not dynamically created
- The coordinator explicitly **includes findings in the task prompt** (no auto-inheritance)

### Context Passing Between Agents

**Critical point:** Subagents don't automatically see what the coordinator sees. You must explicitly pass context:

```python
# DON'T assume the subagent knows about findings
task = "Review the code"

# DO include the findings explicitly
task = f"""Review the following code and identify security issues:

```python
{code_snippet}
```

Context from previous analysis:
- Performance bottleneck identified in the parsing step
- Currently handles 1000 requests/sec
- Team wants to improve to 5000 requests/sec
"""
```

### Code Walkthrough: Multi-Agent Code Review System

```python
import anthropic
import json
from typing import Optional

def multi_agent_code_review(code_snippet: str) -> dict:
    """
    Coordinator agent that invokes specialized subagents to review code.
    Subagents: security_reviewer, performance_reviewer, style_reviewer
    """
    client = anthropic.Anthropic()
    model = "claude-opus-4-1-20250805"

    # Coordinator tools include the Task tool
    tools = [
        {
            "name": "Task",
            "description": "Invoke a specialized subagent to review code",
            "input_schema": {
                "type": "object",
                "properties": {
                    "subagent_id": {
                        "type": "string",
                        "enum": ["security_reviewer", "performance_reviewer", "style_reviewer"],
                        "description": "Which subagent to invoke"
                    },
                    "task": {
                        "type": "string",
                        "description": "The review task (include code and context)"
                    }
                },
                "required": ["subagent_id", "task"]
            }
        }
    ]

    # Coordinator's initial prompt
    initial_prompt = f"""You are a code review coordinator. Your job is to orchestrate specialized reviewers.

For the code below, determine which reviewers should be involved. You might need security, performance, and style reviews.
Invoke the appropriate subagents, then aggregate their findings into a comprehensive review.

Code to review:
```python
{code_snippet}
```

Invoke subagents using the Task tool. Include the code and all relevant context in each task prompt."""

    messages = [
        {"role": "user", "content": initial_prompt}
    ]

    results = {
        "coordinator_findings": [],
        "subagent_reports": {},
        "final_review": None
    }

    iteration = 0
    max_iterations = 10  # Safety limit for loop

    while iteration < max_iterations:
        iteration += 1

        response = client.messages.create(
            model=model,
            max_tokens=2048,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            # Coordinator has aggregated all findings
            final_text = next(
                (block.text for block in response.content if hasattr(block, "text")),
                None
            )
            results["final_review"] = final_text
            break

        elif response.stop_reason == "tool_use":
            # Coordinator is invoking subagents
            tool_uses = [block for block in response.content if block.type == "tool_use"]

            # Append coordinator's request
            messages.append({"role": "assistant", "content": response.content})

            # Simulate subagent responses (in production, these would be real agent calls)
            tool_results = []
            for tool_use in tool_uses:
                if tool_use.name == "Task":
                    subagent_id = tool_use.input.get("subagent_id")
                    task = tool_use.input.get("task")

                    # Simulate subagent response
                    if subagent_id == "security_reviewer":
                        subagent_response = "Security Review: No SQL injection vulnerabilities detected. Input validation is present. Recommend adding rate limiting."
                    elif subagent_id == "performance_reviewer":
                        subagent_response = "Performance Review: O(n^2) algorithm detected in loop. Recommend using a hash set for lookups to achieve O(n)."
                    else:
                        subagent_response = "Style Review: Code follows PEP 8. Variable names are clear. Consider adding docstrings to public functions."

                    results["subagent_reports"][subagent_id] = subagent_response

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": subagent_response
                    })

            # Append results
            messages.append({"role": "user", "content": tool_results})

    return results
```

### Dynamic Subagent Selection

The coordinator doesn't need to invoke all subagents. It decides based on context:

```python
task_prompt = """Review this code for issues:

```python
{code}
```

Based on what you see:
- If there are security concerns, invoke the security_reviewer subagent
- If there are performance issues, invoke the performance_reviewer subagent
- If there are style issues, invoke the style_reviewer subagent

You may invoke multiple subagents if needed. Aggregate all findings and provide a consolidated review."""
```

### Common Exam Traps

**TRAP 1: Assuming subagents inherit coordinator context**
- ❌ WRONG: Coordinator sees code, so subagent automatically knows about it
- ✅ RIGHT: Explicitly include code and context in the task prompt passed to the subagent

**TRAP 2: Overcomplicating subagent scope**
- ❌ WRONG: Creating subagents that are too specialized ("function_name_validator", "function_docstring_validator")
- ✅ RIGHT: Balanced scope ("security_reviewer", "performance_reviewer")

**TRAP 3: Not using the Task tool**
- ❌ WRONG: Trying to invoke subagents via prompting ("Please contact the security team...")
- ✅ RIGHT: Using the Task tool to formally invoke registered subagents

**TRAP 4: Forgetting to include findings in subsequent tasks**
- ❌ WRONG: Coordinator finds issue A, invokes subagent without mentioning issue A, subagent misses the connection
- ✅ RIGHT: Include all relevant findings from prior analysis in each subagent task

### Practice Questions

**Q2.1:** A coordinator agent is reviewing a request that could have security, performance, and style issues. It invokes the security_reviewer subagent. In the task prompt, should the coordinator include the entire code snippet?

A) No, the subagent should fetch it from the coordinator's context
B) Yes, always include the code snippet explicitly in the task prompt
C) Only if the code is less than 500 lines
D) No, just describe the security concern in natural language

**Answer: B.** Subagents don't have automatic context inheritance. Explicit is better than implicit.

**Q2.2:** You have three subagents: code_reviewer, security_reviewer, and performance_reviewer. Your code review coordinator needs to get feedback on all three dimensions. What's the best approach?

A) Invoke code_reviewer with all three tasks, then let it delegate
B) Invoke all three subagents in parallel using the Task tool
C) Invoke them sequentially, passing results from one to the next
D) Invoke just security_reviewer and let it handle everything

**Answer: B.** The Task tool supports parallel invocation. The coordinator can invoke multiple subagents in a single turn, then aggregate results.

---

## Part 3: Multi-Step Workflows & Enforcement (Task 1.4) — 25 minutes

### Programmatic vs Prompt-Based Enforcement

There are two ways to ensure workflows follow required steps:

1. **Prompt-based**: "Please verify the security review before approving" (probabilistic, not guaranteed)
2. **Programmatic**: Block downstream tools until prerequisites are met (deterministic, guaranteed)

For production systems with compliance requirements, **always use programmatic enforcement**.

### Structured Handoff Protocols

When one agent hands off work to the next, use a structured format:

```python
handoff_summary = {
    "agent": "security_reviewer",
    "findings": [
        {
            "category": "SQL_INJECTION",
            "severity": "HIGH",
            "location": "line 45",
            "description": "User input not sanitized in database query"
        }
    ],
    "recommendation": "BLOCK_DEPLOYMENT",
    "timestamp": "2025-03-22T14:30:00Z",
    "requires_review_by": ["lead_architect", "security_lead"]
}
```

The next agent (approval_agent) receives this structure, not a text summary. This enables deterministic routing.

### Programmatic Prerequisites with PostToolUse Hooks

Using Agent SDK hooks to enforce prerequisites:

```python
def post_tool_use_hook(tool_use: ToolUse, tool_result: str) -> Optional[str]:
    """
    Hook that runs after a tool is used. Can transform results or block tools.
    Returns the modified result, or raises an exception to block.
    """

    # Example: Block deployment approval if security review hasn't completed
    if tool_use.name == "approve_deployment":
        # Check if security_review_completed flag is set
        if not workflow_state.get("security_review_completed"):
            raise PermissionError(
                "Cannot approve deployment until security review is complete. "
                "Invoke the security_review tool first."
            )

    return tool_result
```

### Code Walkthrough: Deployment Approval Workflow

```python
import anthropic
from enum import Enum

class WorkflowState(Enum):
    INITIAL = "initial"
    SECURITY_REVIEW_PENDING = "security_review_pending"
    SECURITY_REVIEW_COMPLETE = "security_review_complete"
    APPROVAL_PENDING = "approval_pending"
    APPROVED = "approved"
    DEPLOYMENT_COMPLETE = "deployment_complete"

def deployment_workflow(code_changes: str) -> dict:
    """
    Multi-step workflow:
    1. Security review (required before approval)
    2. Approval (requires security review)
    3. Deployment (requires approval)
    """
    client = anthropic.Anthropic()
    model = "claude-opus-4-1-20250805"

    workflow_state = {
        "status": WorkflowState.INITIAL.value,
        "security_findings": None,
        "approval_status": None,
        "deployment_status": None
    }

    tools = [
        {
            "name": "security_review",
            "description": "Run security analysis on code changes",
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"}
                },
                "required": ["code"]
            }
        },
        {
            "name": "approve_deployment",
            "description": "Approve the deployment for production",
            "input_schema": {
                "type": "object",
                "properties": {
                    "justification": {"type": "string"}
                },
                "required": ["justification"]
            }
        },
        {
            "name": "deploy_to_production",
            "description": "Deploy code to production",
            "input_schema": {
                "type": "object",
                "properties": {
                    "version": {"type": "string"}
                },
                "required": ["version"]
            }
        }
    ]

    prompt = f"""You are a deployment orchestrator. Follow these steps in order:

1. Review the code for security issues
2. If security review passes, approve the deployment
3. If approved, deploy to production

Code to review:
```
{code_changes}
```

Use the tools in order. You cannot skip steps."""

    messages = [{"role": "user", "content": prompt}]

    while True:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            final_text = next(
                (block.text for block in response.content if hasattr(block, "text")),
                None
            )
            workflow_state["final_message"] = final_text
            return workflow_state

        elif response.stop_reason == "tool_use":
            tool_uses = [block for block in response.content if block.type == "tool_use"]
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for tool_use in tool_uses:

                # PROGRAMMATIC ENFORCEMENT: Check prerequisites
                if tool_use.name == "approve_deployment":
                    if workflow_state["security_findings"] is None:
                        error_msg = "BLOCKED: Security review must complete before approval. Run security_review first."
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": error_msg,
                            "is_error": True
                        })
                        continue

                if tool_use.name == "deploy_to_production":
                    if workflow_state["approval_status"] != "approved":
                        error_msg = "BLOCKED: Deployment must be approved before production deployment."
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": error_msg,
                            "is_error": True
                        })
                        continue

                # Execute tool and update state
                if tool_use.name == "security_review":
                    result = "Security review complete. No critical vulnerabilities found."
                    workflow_state["security_findings"] = result
                    workflow_state["status"] = WorkflowState.SECURITY_REVIEW_COMPLETE.value

                elif tool_use.name == "approve_deployment":
                    result = "Deployment approved for production."
                    workflow_state["approval_status"] = "approved"
                    workflow_state["status"] = WorkflowState.APPROVAL_PENDING.value

                elif tool_use.name == "deploy_to_production":
                    result = "Deployment to production successful. Version v1.2.3 is now live."
                    workflow_state["deployment_status"] = "complete"
                    workflow_state["status"] = WorkflowState.DEPLOYMENT_COMPLETE.value

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result
                })

            messages.append({"role": "user", "content": tool_results})

```

### Common Exam Traps

**TRAP 1: Relying on prompt-based enforcement**
- ❌ WRONG: Assuming the prompt "You must review security before approving" prevents unauthorized deployments
- ✅ RIGHT: Using tool availability checks or hooks to block the approve tool until security review is complete

**TRAP 2: Allowing tool execution despite prerequisites not being met**
- ❌ WRONG: Executing "approve_deployment" without verifying "security_review" has been called
- ✅ RIGHT: Checking workflow state before allowing tool execution

**TRAP 3: Using string-based handoff data**
- ❌ WRONG: "Security review says everything is fine" (unstructured)
- ✅ RIGHT: Structured data with categories, severity, findings (enables deterministic routing)

### Practice Question

**Q3.1:** Your deployment workflow requires security review before approval. You use prompt-based guidance: "You must complete security review before approving deployment." However, the agent calls approve_deployment without calling security_review first. Why did this happen?

A) The model didn't read the prompt carefully enough
B) Prompt-based enforcement is probabilistic, not deterministic
C) You need to add a safety check in your code
D) B and C

**Answer: D.** Prompts are guidance, not guarantees. You must use programmatic enforcement (hooks, tool availability checks) for deterministic compliance.

---

## Part 4: Agent SDK Hooks (Task 1.5) — 25 minutes

### PostToolUse Hooks for Tool Call Interception

The Agent SDK provides hooks that intercept tool calls. **PostToolUse** runs after a tool result is received:

```python
def post_tool_use_hook(
    tool_name: str,
    tool_input: dict,
    tool_result: str,
    stop_reason: str
) -> Optional[str]:
    """
    Called after a tool is used. Can:
    - Transform the result
    - Block the tool (raise exception)
    - Log or monitor
    """
    pass
```

### Use Cases for PostToolUse Hooks

1. **Data normalization**: Standardize tool outputs (different sources, different formats)
2. **Policy enforcement**: Block tools that violate policy
3. **Audit logging**: Track who called what and when
4. **Result transformation**: Convert raw results to agent-friendly format

### Deterministic vs Probabilistic Compliance

- **Probabilistic compliance** (prompt-based): "Please only call tools that are safe" (doesn't guarantee compliance)
- **Deterministic compliance** (hook-based): Hook checks every tool call and blocks if it violates policy (guarantees compliance)

For regulated systems (healthcare, finance, legal), always use deterministic enforcement.

### Code Walkthrough: Data Privacy Hook

```python
import anthropic
from datetime import datetime

class DataPrivacyEnforcer:
    """
    Enforces data privacy policies using PostToolUse hook.
    Prevents agents from logging, exporting, or sharing sensitive data.
    """

    SENSITIVE_PATTERNS = [
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"\b\d{16}\b",              # Credit card
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"  # Email
    ]

    def __init__(self):
        self.blocked_calls = []
        self.allowed_calls = []

    def check_for_sensitive_data(self, text: str) -> bool:
        """Returns True if sensitive data is found."""
        import re
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def post_tool_use_hook(
        self,
        tool_name: str,
        tool_input: dict,
        tool_result: str
    ) -> Optional[str]:
        """
        Intercept tool results. Block if sensitive data would be exposed.
        """

        # Tools that should never expose sensitive data
        restricted_tools = ["log_to_external", "export_to_csv", "email_results"]

        if tool_name in restricted_tools:
            # Check input for sensitive data
            input_str = str(tool_input)
            if self.check_for_sensitive_data(input_str):
                error_msg = (
                    f"BLOCKED: {tool_name} cannot be used with sensitive data. "
                    "This tool may expose PII. Use a secure alternative."
                )
                self.blocked_calls.append({
                    "tool": tool_name,
                    "reason": "sensitive_data_detected",
                    "timestamp": datetime.now().isoformat()
                })
                raise PermissionError(error_msg)

            # Check result for sensitive data
            if self.check_for_sensitive_data(tool_result):
                error_msg = (
                    f"BLOCKED: {tool_name} returned sensitive data. "
                    "Cannot proceed with restricted tool."
                )
                self.blocked_calls.append({
                    "tool": tool_name,
                    "reason": "result_contains_sensitive_data",
                    "timestamp": datetime.now().isoformat()
                })
                raise PermissionError(error_msg)

        # Normalize results from different sources
        if tool_name == "fetch_user_data":
            # Different APIs return data in different formats
            # Normalize to standard schema
            try:
                import json
                data = json.loads(tool_result)
                normalized = {
                    "user_id": data.get("id") or data.get("user_id"),
                    "email": data.get("email") or data.get("contact"),
                    "created_at": data.get("created") or data.get("date_created")
                }
                self.allowed_calls.append({
                    "tool": tool_name,
                    "timestamp": datetime.now().isoformat()
                })
                return json.dumps(normalized)
            except:
                pass

        self.allowed_calls.append({
            "tool": tool_name,
            "timestamp": datetime.now().isoformat()
        })
        return tool_result


def privacy_aware_agent(user_query: str) -> dict:
    """
    Agent that processes user requests while enforcing data privacy.
    """
    client = anthropic.Anthropic()
    enforcer = DataPrivacyEnforcer()

    tools = [
        {
            "name": "fetch_user_data",
            "description": "Fetch user data from database",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"]
            }
        },
        {
            "name": "log_to_external",
            "description": "Log information to external service",
            "input_schema": {
                "type": "object",
                "properties": {
                    "data": {"type": "string"}
                },
                "required": ["data"]
            }
        }
    ]

    messages = [{"role": "user", "content": user_query}]

    while True:
        response = client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            break

        elif response.stop_reason == "tool_use":
            tool_uses = [block for block in response.content if block.type == "tool_use"]
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for tool_use in tool_uses:
                try:
                    # Simulate tool execution
                    if tool_use.name == "fetch_user_data":
                        tool_result = '{"id": "u123", "email": "user@example.com", "ssn": "123-45-6789"}'
                    else:
                        tool_result = "Logged successfully"

                    # Apply hook: enforce privacy
                    normalized_result = enforcer.post_tool_use_hook(
                        tool_use.name,
                        tool_use.input,
                        tool_result
                    )

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": normalized_result
                    })

                except PermissionError as e:
                    # Hook blocked the tool
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": str(e),
                        "is_error": True
                    })

            messages.append({"role": "user", "content": tool_results})

    return {
        "blocked_calls": enforcer.blocked_calls,
        "allowed_calls": enforcer.allowed_calls
    }
```

### Common Exam Traps

**TRAP 1: Using hooks when prompt guidance would work**
- ❌ WRONG: "Use this hook to gently suggest the agent not call dangerous tools"
- ✅ RIGHT: Use hooks for hard requirements; use prompting for suggestions

**TRAP 2: Treating hooks as a substitute for tool design**
- ❌ WRONG: Giving agents access to all tools, then blocking bad ones in hooks
- ✅ RIGHT: Design the tool set so agents only have access to tools appropriate for their role

**TRAP 3: Hooks that don't raise exceptions**
- ❌ WRONG: Hook that logs a warning but returns the result anyway
- ✅ RIGHT: Hook raises PermissionError to actually block execution

### Practice Question

**Q4.1:** You want to ensure agents never call a dangerous_operation tool. Which approach is most deterministic?

A) Add a prompt saying "Do not call dangerous_operation"
B) Include dangerous_operation in the tool list with a scary description
C) Remove dangerous_operation from the tool list entirely
D) Use a PostToolUse hook to block it

**Answer: C.** If you don't want the agent to call a tool, don't include it. Hooks are for enforcing constraints on the tools that ARE included. The most deterministic approach is to not expose the tool at all.

---

## Part 5: Task Decomposition & Session Management (Tasks 1.6, 1.7) — 20 minutes

### Fixed Pipelines vs Dynamic Decomposition

**Fixed pipeline**: "Always do steps A, B, C in order"
**Dynamic decomposition**: "Investigate what's needed, then decide on steps"

Dynamic is more powerful but harder to control. Choose based on your problem:

- **Fixed**: Data processing, defined workflow steps, regulated processes
- **Dynamic**: Research, debugging, exploratory tasks

### Session Resumption and Forking

The Agent SDK supports **named sessions**:

```bash
# Run agent in a named session
agent --session-name "code-review-123"

# Resume session later
agent --session-name "code-review-123" --resume

# Fork to parallel exploration
agent --session-name "code-review-123" --fork "alternative-approach"
```

**Resume**: Continue where you left off (same context, same conversation history)
**Fork**: Create a parallel branch (useful for exploring multiple solutions)

### Code Walkthrough: Adaptive Debugging Workflow

```python
import anthropic
import json

def adaptive_debugging_agent(error_message: str, system_context: dict) -> dict:
    """
    Dynamically decomposes debugging task based on error analysis.
    Rather than following a fixed "check logs, check config, check code" pipeline,
    the agent analyzes the error and decides which investigations are most relevant.
    """
    client = anthropic.Anthropic()
    model = "claude-opus-4-1-20250805"

    tools = [
        {
            "name": "analyze_error",
            "description": "Analyze error message to understand root cause",
            "input_schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },
                "required": ["error"]
            }
        },
        {
            "name": "fetch_logs",
            "description": "Fetch application logs around the error time",
            "input_schema": {
                "type": "object",
                "properties": {
                    "service": {"type": "string"},
                    "time_range": {"type": "string"}
                },
                "required": ["service", "time_range"]
            }
        },
        {
            "name": "check_config",
            "description": "Check system configuration for mismatches",
            "input_schema": {
                "type": "object",
                "properties": {
                    "service": {"type": "string"}
                },
                "required": ["service"]
            }
        },
        {
            "name": "check_dependencies",
            "description": "Check if external service dependencies are available",
            "input_schema": {
                "type": "object",
                "properties": {
                    "services": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["services"]
            }
        }
    ]

    prompt = f"""You are a debugging agent. Diagnose the following error and determine the root cause.

Error: {error_message}

System context:
{json.dumps(system_context, indent=2)}

Your task:
1. Analyze the error to form hypotheses
2. Based on your analysis, use tools to investigate the most likely causes
3. Do NOT follow a fixed pipeline. Investigate what you think matters.
4. Once you've identified the root cause, provide a clear explanation and recommendation.

For example:
- If the error looks like a dependency issue, check dependencies and logs
- If it looks like a config issue, check config and logs for that service
- If it looks like a timeout, check logs and service health

Be selective in your investigations."""

    messages = [{"role": "user", "content": prompt}]

    results = {
        "root_cause": None,
        "recommendation": None,
        "investigation_steps": []
    }

    iteration = 0
    while iteration < 10:
        iteration += 1

        response = client.messages.create(
            model=model,
            max_tokens=2048,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            final_text = next(
                (block.text for block in response.content if hasattr(block, "text")),
                None
            )
            results["final_analysis"] = final_text
            break

        elif response.stop_reason == "tool_use":
            tool_uses = [block for block in response.content if block.type == "tool_use"]
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for tool_use in tool_uses:
                results["investigation_steps"].append(tool_use.name)

                # Simulate tool results
                if tool_use.name == "analyze_error":
                    result = json.dumps({
                        "error_type": "TimeoutError",
                        "likely_causes": [
                            "Database connection timeout",
                            "Slow external API",
                            "High system load"
                        ],
                        "severity": "HIGH"
                    })

                elif tool_use.name == "fetch_logs":
                    result = json.dumps({
                        "logs": [
                            "2025-03-22 14:30:00 - Connection timeout to database",
                            "2025-03-22 14:30:01 - Retry attempt 1",
                            "2025-03-22 14:30:05 - Max retries exceeded"
                        ]
                    })

                elif tool_use.name == "check_config":
                    result = json.dumps({
                        "db_timeout": "5s",
                        "connection_pool": "10",
                        "recommended_timeout": "30s"
                    })

                else:
                    result = json.dumps({"status": "all_dependencies_healthy"})

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result
                })

            messages.append({"role": "user", "content": tool_results})

    return results
```

### Session Resumption Example

```python
def resume_debugging_session(session_name: str, additional_context: str):
    """
    Resume a previous debugging session and add new findings.
    """
    client = anthropic.Anthropic()

    # Resume uses the same context as before
    # If the user says "But have you checked X?", we can ask the agent to investigate X

    new_message = f"""New information has come to light:
{additional_context}

Given this new information, do you still believe your previous diagnosis was correct?
If not, what changes to your recommendation?"""

    # In a real session, we'd fetch the session's message history and append
    # For this example, we show the concept
    return new_message
```

### Common Exam Traps

**TRAP 1: Using fixed decomposition for exploratory tasks**
- ❌ WRONG: "Always check A, then B, then C" for debugging (ignores evidence)
- ✅ RIGHT: "Analyze the error, then investigate likely causes" (adaptive)

**TRAP 2: Not informing agents about changes when resuming**
- ❌ WRONG: Resume session without telling agent "Files X, Y, Z have changed"
- ✅ RIGHT: Include context about what changed since the last session

**TRAP 3: Confusing fork and resume**
- ❌ WRONG: Fork when you mean resume (creates parallel timeline instead of continuing)
- ✅ RIGHT: Resume to continue; fork only when exploring alternatives

### Practice Questions

**Q5.1:** You're debugging an application. The error could be caused by (1) database timeout, (2) bad config, or (3) dependency failure. Should you check all three in a fixed order, or adapt based on error analysis?

A) Always check all three in order
B) Analyze the error first, then investigate likely causes
C) Randomly pick one
D) Ask the user which one to check first

**Answer: B.** Dynamic decomposition is more efficient. Analyze first, then focus investigations.

**Q5.2:** You're resuming a debugging session from yesterday. Files have changed since then. What should you do?

A) Just resume without mentioning file changes
B) Include a message about which files changed and ask the agent to reconsider
C) Start fresh instead of resuming
D) Fork the session to explore both old and new scenarios

**Answer: B.** Inform the agent of changes so it can adapt its analysis.

---

## Session Summary & Key Takeaways

| Concept | Key Mechanism | Common Mistake |
|---------|--------------|-----------------|
| **Agentic loops** | stop_reason-driven control flow | Parsing NL instead of using stop_reason |
| **Multi-agent coordination** | Task tool + explicit context passing | Assuming subagents inherit context |
| **Workflow enforcement** | Programmatic prerequisites | Relying on prompts for compliance |
| **SDK hooks** | PostToolUse for deterministic control | Using hooks when tool design would suffice |
| **Decomposition** | Adaptive vs fixed strategies | Fixed decomposition for exploratory tasks |
| **Session management** | Resume vs fork | Not informing agent about context changes |

**The Golden Rule:** Agentic systems are about **architectural design**, not prompt magic. Use:
- **stop_reason** for control flow (not NL parsing)
- **Task tool** for agent coordination (not prompting agents to contact each other)
- **Programmatic enforcement** for compliance (not prompts)
- **Hooks** for deterministic behavior (not hoping the agent does what you want)

---

## Hands-On Lab Exercise

### Scenario: Multi-Agent Code Analysis System

Build a system with three agents:
1. **Coordinator**: Takes a code repository, decides what analysis is needed, delegates to specialists
2. **Security Analyzer**: Finds security vulnerabilities
3. **Performance Analyzer**: Identifies performance bottlenecks

**Requirements:**
- Use the Task tool to invoke specialists
- Include code context explicitly in each subagent task
- Aggregate findings with structured format
- Programmatically enforce that coordinator must invoke both specialists before generating final report

**Success Criteria:**
- Coordinator invokes both specialists
- Each specialist receives the complete code context
- Both reports are aggregated into final summary
- Reports are in structured format (JSON, not free-form text)

**Estimated Time:** 45 minutes

---

## Self-Assessment Quiz

**Question 1:** What does `stop_reason: "tool_use"` indicate?
A) The tool call was successful
B) The agent wants to call one or more tools
C) The agent is finished
D) An error occurred

**Answer: B**

**Question 2:** In a coordinator-subagent pattern, does the subagent automatically see everything the coordinator sees?
A) Yes, context is automatically inherited
B) No, context must be explicitly passed in the task prompt
C) Yes, but only the most recent findings
D) No, subagents have completely isolated tools

**Answer: B**

**Question 3:** You want to ensure a tool is never called before its prerequisites are met. Which is most reliable?
A) Include guidance in the prompt
B) Use a PostToolUse hook to block it
C) Don't include the tool in the tool list at all until prerequisites are met
D) Both B and C are equally reliable

**Answer: C**

**Question 4:** When resuming an agent session, should you tell the agent about files that have changed?
A) No, it should remember from last time
B) Yes, explicitly include information about what changed
C) Only if files were deleted
D) Only if it asks

**Answer: B**

**Question 5:** In the agentic loop, when should you stop iterating?
A) After 5 iterations (arbitrary limit)
B) After 10 tool calls
C) When `stop_reason == "end_turn"`
D) When the agent mentions it's done in the text response

**Answer: C**

**Question 6:** Which pattern is best for a fixed, compliance-heavy workflow (e.g., loan approval)?
A) Dynamic decomposition with adaptive routing
B) Fixed pipeline with programmatic enforcement of prerequisites
C) Prompt-based guidance only
D) A single agent handling everything

**Answer: B**

**Question 7:** The Task tool requires what to be in the coordinator agent's allowedTools?
A) The names of all subagents
B) The string "Task"
C) A list of available tasks
D) Nothing—Task is always available

**Answer: B**

**Question 8:** What is the primary benefit of using PostToolUse hooks over prompt-based guidance?
A) Hooks are easier to write
B) Hooks provide deterministic enforcement, not probabilistic guidance
C) Hooks work for all types of agents
D) Hooks are cheaper than prompting

**Answer: B**

---

## Recommended Study Resources

### Official Documentation
- Claude API documentation: Agent loops and tool use
- Agent SDK documentation: Multi-agent systems, hooks, session management
- CCA Exam Guide: Domain 1 task statements and knowledge areas

### Key Concepts to Deep-Dive
1. **stop_reason mechanism**: Understand how it drives the loop
2. **Task tool configuration**: Practice setting up coordinator-subagent patterns
3. **Structured data in handoffs**: Design your handoff protocols before coding
4. **Hook patterns**: Study deterministic vs probabilistic enforcement
5. **Session lifecycle**: Understand when to resume vs fork vs start fresh

### Practice Problems
- Implement a 3-agent system with coordinator and two specialists
- Build a workflow that blocks downstream tools until prerequisites are met
- Design a decomposition strategy for an open-ended research task
- Implement a PostToolUse hook for data transformation

### Common Gotchas to Memorize
1. Subagents don't inherit coordinator context
2. Prompts are guidance; hooks are enforcement
3. stop_reason drives control flow; text parsing is wrong
4. Fixed pipelines for known workflows; dynamic for exploratory
5. Always inform agents about context changes when resuming

---

**End of Training Session 1**

This document covers approximately 70% of the knowledge needed for Domain 1 questions. The remaining 30% comes from hands-on practice with the Agent SDK and exposure to real-world system designs. Study the code examples, practice the lab exercise, and take the self-assessment quiz multiple times until you score 8/8 consistently.