# Domain 5: Context Management & Reliability
## Claude Certified Architect – Foundations Exam Study Guide

**Domain Weight:** 15% of exam (11 questions)

---

## Table of Contents
1. [Domain Overview](#domain-overview)
2. [Task 5.1: Conversation Context Preservation](#task-51-conversation-context-preservation)
3. [Task 5.2: Escalation and Ambiguity Resolution](#task-52-escalation-and-ambiguity-resolution)
4. [Task 5.3: Error Propagation Across Multi-Agent Systems](#task-53-error-propagation-across-multi-agent-systems)
5. [Task 5.4: Context Management in Large Codebase Exploration](#task-54-context-management-in-large-codebase-exploration)
6. [Task 5.5: Human Review Workflows and Confidence Calibration](#task-55-human-review-workflows-and-confidence-calibration)
7. [Task 5.6: Information Provenance and Uncertainty](#task-56-information-provenance-and-uncertainty)
8. [Quick Reference Cheatsheet](#quick-reference-cheatsheet)
9. [Common Exam Traps](#common-exam-traps)
10. [Code Examples](#code-examples)

---

## Domain Overview

Domain 5 focuses on **managing reliability and context in multi-turn, multi-agent systems**. This is mission-critical for production applications because:

- **Context Accumulation:** Agent conversations grow exponentially; you must design strategies for what to keep vs. discard
- **Error Recovery:** Failures in one agent shouldn't crash the entire system; design graceful degradation
- **Human Trust:** Agents must escalate ambiguous decisions, provide explanations with confidence levels, and track information sources
- **Efficiency:** Context window constraints require strategic information management to keep token usage sustainable

The six tasks build upon each other:
1. **Preserve context** effectively across long conversations
2. **Know when to escalate** instead of continuing automated resolution
3. **Isolate errors** so one failure doesn't cascade
4. **Explore efficiently** in large codebases without exhausting context
5. **Verify work** with independent review, not self-review
6. **Track sources** and express uncertainty explicitly

---

## Task 5.1: Conversation Context Preservation

### Knowledge Breakdown

#### How Conversation History Drives Agentic Behavior

In Claude's architecture, **every tool result becomes a message the agent reads**. The agent always has access to full conversation history when reasoning about the next step. This means:

- Tool outputs are not consumed silently; they become visible context
- The agent can connect results across multiple turns to build complex reasoning
- But accumulated context grows, eventually hitting context window limits

**Example:** In a customer service agent, after calling `get_customer()`, `get_account_history()`, and `analyze_sentiment()`, the agent sees all three results and can synthesize a complete picture before deciding whether to refund, escalate, or explain a policy.

#### PostToolUse Normalization Hooks

**PostToolUse hooks** are critical infrastructure for managing heterogeneous tool outputs. They execute **before the model processes tool results**, allowing you to:

- Normalize timestamps (Unix → ISO 8601)
- Standardize status codes (0/1 → success/failure enums)
- Filter sensitive data before the model sees it
- Restructure nested objects into consistent schemas
- Add metadata (source, confidence, timestamp)

**Why this matters:** If tool A returns `{"timestamp": 1234567890}` and tool B returns `{"date": "2026-03-22"}`, the agent wastes context understanding both formats. Normalize upfront.

#### Strategies for Managing Long Conversations

**1. Summarization at Checkpoints**
- After major decisions (e.g., customer verified, root cause identified), create a structured summary
- Replace verbose earlier exchanges with the summary
- Preserve only the summary and recent context

**2. Context Windowing**
- Keep only the last N turns + the most recent summary
- Discard intermediate steps that led to the summary
- Example: Keep the final decision but discard the 5 back-and-forths that led to it

**3. Selective Retention**
- Identify decision-relevant information: customer ID, error details, constraints
- Discard exploratory reasoning, clarifications that were resolved
- Keep trade-off analysis for future similar decisions

**4. Hierarchical Summaries**
- Level 1: Current conversation (full detail)
- Level 2: Session summary (decisions, escalations, key facts)
- Level 3: Cross-session knowledge (learned patterns, recurring issues)

#### Impact of Context Window Limits on Multi-Step Agent Tasks

With a 200k token context window:
- A 100-turn conversation where each tool result is 500 tokens = 50k tokens consumed
- That leaves 150k for agentic reasoning, tool definitions, system prompts, and plans
- A second complex task in the same session might only have 50k available

**Critical for exam:** Multi-step agent tasks that don't manage context window will:
- Hit token limits mid-task
- Lose earlier context, causing repeated questions
- Force unnecessary escalations or task abandonment

### Skills: Implementation Patterns

#### 1. Implementing PostToolUse Hooks for Data Normalization

```python
import json
from datetime import datetime
from enum import Enum

class StatusCode(Enum):
    SUCCESS = "success"
    TRANSIENT_ERROR = "transient_error"
    PERMANENT_ERROR = "permanent_error"

def posttool_normalize_timestamps(tool_result: dict) -> dict:
    """Convert all timestamp fields to ISO 8601 format."""
    if isinstance(tool_result, dict):
        for key, value in tool_result.items():
            # Unix timestamp (10-digit number)
            if isinstance(value, (int, float)) and 1000000000 < value < 2000000000:
                tool_result[key] = {
                    "unix": value,
                    "iso": datetime.fromtimestamp(value).isoformat()
                }
            # Recursive normalization for nested dicts
            elif isinstance(value, dict):
                posttool_normalize_timestamps(value)
    return tool_result

def posttool_normalize_status(tool_result: dict) -> dict:
    """Standardize status codes to enum format."""
    if "status" in tool_result:
        status = tool_result["status"]
        if status in (0, "0", "success", True):
            tool_result["status"] = StatusCode.SUCCESS.value
        elif status in (1, "1", "error", False):
            # Determine if transient or permanent
            if "retryable" in tool_result and tool_result["retryable"]:
                tool_result["status"] = StatusCode.TRANSIENT_ERROR.value
            else:
                tool_result["status"] = StatusCode.PERMANENT_ERROR.value
    return tool_result

def posttool_filter_pii(tool_result: dict, pii_fields: list) -> dict:
    """Remove PII before model processes result."""
    for field in pii_fields:
        if field in tool_result:
            # Replace with reference rather than deleting
            tool_result[f"{field}_redacted"] = f"[{field} present but redacted]"
            del tool_result[field]
    return tool_result

def posttool_add_metadata(tool_result: dict, tool_name: str, call_timestamp: float) -> dict:
    """Add provenance metadata to all results."""
    return {
        "content": tool_result,
        "metadata": {
            "source_tool": tool_name,
            "retrieved_at": datetime.fromtimestamp(call_timestamp).isoformat(),
            "confidence": tool_result.get("confidence", "unknown")
        }
    }

# Chain multiple hooks
def apply_posttool_hooks(tool_result: dict, tool_name: str, timestamp: float) -> dict:
    """Apply all normalization hooks in sequence."""
    result = tool_result
    result = posttool_normalize_timestamps(result)
    result = posttool_normalize_status(result)
    result = posttool_filter_pii(result, ["ssn", "credit_card", "password"])
    result = posttool_add_metadata(result, tool_name, timestamp)
    return result

# Example usage
if __name__ == "__main__":
    raw_result = {
        "status": 0,
        "timestamp": 1711190400,
        "customer_id": "cust_123",
        "ssn": "123-45-6789",
        "balance": 5000
    }

    normalized = apply_posttool_hooks(raw_result, "get_customer", 1711190400)
    print(json.dumps(normalized, indent=2))
```

**Output:**
```json
{
  "content": {
    "status": "success",
    "timestamp": {
      "unix": 1711190400,
      "iso": "2026-03-23T20:00:00"
    },
    "customer_id": "cust_123",
    "ssn_redacted": "[ssn present but redacted]",
    "balance": 5000
  },
  "metadata": {
    "source_tool": "get_customer",
    "retrieved_at": "2026-03-23T20:00:00",
    "confidence": "unknown"
  }
}
```

#### 2. Designing Context-Aware Agents with Message Pruning

```python
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ConversationSummary:
    """Checkpoint summary to replace verbose history."""
    checkpoint_id: str
    created_at: str
    key_decisions: list[str]
    customer_state: dict
    root_causes_identified: list[str]
    token_saved: int

class ContextManager:
    def __init__(self, max_context_tokens: int = 150000):
        self.max_context_tokens = max_context_tokens
        self.messages = []
        self.summaries = []
        self.current_tokens = 0

    def estimate_tokens(self, text: str) -> int:
        """Rough estimate: ~4 characters per token."""
        return len(text) // 4

    def add_message(self, role: str, content: str) -> None:
        """Add message and track token usage."""
        tokens = self.estimate_tokens(content)
        self.messages.append({"role": role, "content": content})
        self.current_tokens += tokens

    def should_checkpoint(self) -> bool:
        """Trigger checkpoint when context approaches limit."""
        return self.current_tokens > self.max_context_tokens * 0.8

    def create_checkpoint_summary(self,
                                  key_decisions: list[str],
                                  customer_state: dict,
                                  root_causes: list[str]) -> ConversationSummary:
        """Create structured summary of conversation so far."""
        summary = ConversationSummary(
            checkpoint_id=f"checkpoint_{datetime.now().timestamp()}",
            created_at=datetime.now().isoformat(),
            key_decisions=key_decisions,
            customer_state=customer_state,
            root_causes_identified=root_causes,
            token_saved=0
        )

        # Replace old messages with summary
        old_token_count = self.current_tokens
        self.messages = [
            {
                "role": "system",
                "content": f"""CONVERSATION CHECKPOINT:
Key Decisions: {', '.join(key_decisions)}
Customer State: {customer_state}
Root Causes: {', '.join(root_causes)}

Earlier verbose conversation has been summarized above. Continue from this state."""
            }
        ] + self.messages[-5:]  # Keep last 5 messages for immediate context

        summary.token_saved = old_token_count - self.current_tokens
        self.summaries.append(summary)
        return summary

    def get_context_summary(self) -> str:
        """Return current context for logging/debugging."""
        return f"""
Context Status:
- Current tokens: {self.current_tokens}/{self.max_context_tokens}
- Messages: {len(self.messages)}
- Checkpoints created: {len(self.summaries)}
- Tokens saved via summarization: {sum(s.token_saved for s in self.summaries)}
"""

# Example usage
if __name__ == "__main__":
    manager = ContextManager(max_context_tokens=150000)

    # Simulate conversation
    for i in range(10):
        manager.add_message("user", f"Question {i}" * 100)
        manager.add_message("assistant", f"Answer {i}" * 100)

    if manager.should_checkpoint():
        summary = manager.create_checkpoint_summary(
            key_decisions=["Customer verified", "Refund approved"],
            customer_state={"id": "cust_123", "status": "verified"},
            root_causes=["Billing error in April"]
        )
        print(f"Created checkpoint: {summary.checkpoint_id}")

    print(manager.get_context_summary())
```

#### 3. Message History Pruning Strategies

```python
class HistoryPruner:
    """Intelligently prune conversation history while preserving critical context."""

    @staticmethod
    def is_decision_relevant(message: dict) -> bool:
        """Classify if message is decision-relevant."""
        content = message.get("content", "").lower()
        decision_keywords = [
            "customer verified", "refund approved", "escalate",
            "error cause", "root cause", "decision",
            "constraint", "requirement", "confirmed"
        ]
        return any(kw in content for kw in decision_keywords)

    @staticmethod
    def is_exploratory(message: dict) -> bool:
        """Classify if message is exploratory reasoning that can be discarded."""
        content = message.get("content", "").lower()
        exploratory_keywords = [
            "checking", "trying", "let me", "hmm",
            "wondering", "maybe", "possibly", "perhaps"
        ]
        return any(kw in content for kw in exploratory_keywords)

    @staticmethod
    def prune_history(messages: list[dict],
                     keep_recent_n: int = 5,
                     max_tokens: int = 150000) -> tuple[list[dict], int]:
        """
        Prune history: keep recent messages + decision-relevant + first/last important messages.

        Returns: (pruned_messages, tokens_freed)
        """
        if len(messages) <= keep_recent_n:
            return messages, 0

        # Always keep system prompt and last N messages
        keep_indices = set(range(len(messages) - keep_recent_n, len(messages)))

        # Mark decision-relevant messages to keep
        for i, msg in enumerate(messages):
            if HistoryPruner.is_decision_relevant(msg):
                keep_indices.add(i)

        # Discard pure exploratory messages that aren't recent
        for i, msg in enumerate(messages):
            if i not in keep_indices and HistoryPruner.is_exploratory(msg):
                # Can safely discard
                pass

        pruned = [msg for i, msg in enumerate(messages) if i in keep_indices]

        tokens_freed = sum(
            len(msg.get("content", "")) // 4
            for i, msg in enumerate(messages)
            if i not in keep_indices
        )

        return pruned, tokens_freed
```

---

## Task 5.2: Escalation and Ambiguity Resolution

### Knowledge Breakdown

#### When to Escalate vs. Continue Automated Resolution

**Escalate to humans when:**
- Customer request has ambiguity that affects the decision (e.g., "refund my order" without specifying which order)
- Confidence is below threshold (e.g., < 60% sure the diagnosis is correct)
- Action exceeds business rules (e.g., refund > $500 requires manager approval)
- Legal/compliance context requires human review
- Agent has exhausted recovery options for an error

**Continue automated resolution when:**
- Request is clear and unambiguous
- Confidence is above threshold (e.g., > 85%)
- Action is within agent's authorization
- Previous similar cases have predictable outcomes

#### Structured Handoff Protocols

A handoff to human agents must include:
1. **Customer details** - ID, account status, contact info
2. **Root cause analysis** - What was identified, what attempts were made
3. **Current state** - What's been done, what's pending
4. **Recommended actions** - What the agent suggests the human do
5. **Context summary** - Key conversation points human needs to understand

Human agents receiving the handoff **do NOT have access to the conversation transcript**. The handoff summary must be complete and self-contained.

#### Detecting Ambiguity and Asking Clarifying Questions

Before taking action, ask clarifying questions when:
- Multiple interpretations exist: "You mentioned 'the refund' - did you mean order #123 or order #456?"
- Implicit assumptions exist: "By 'immediately,' do you mean today or within 24 hours?"
- Preferences aren't specified: "Would you prefer a refund to original payment method or store credit?"

**Key:** Ask before attempting the action, not after discovering the ambiguity.

#### Confidence Thresholds for Escalation

- **High confidence (>85%):** Proceed with automated action, maybe notify human
- **Medium confidence (60-85%):** Ask clarifying questions, attempt resolution but prepare to escalate
- **Low confidence (<60%):** Escalate immediately or ask detailed clarifying questions

Calibrating these thresholds is domain-dependent:
- Refund decisions: Maybe 85% threshold
- Account deletions: Maybe 95% threshold
- Diagnostic recommendations: Maybe 70% threshold

### Skills: Implementation Patterns

#### 1. Programmatic Prerequisites and Dependency Management

```python
from enum import Enum
from typing import Optional, Callable
from dataclasses import dataclass
from datetime import datetime

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    task_id: str
    name: str
    handler: Callable
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[dict] = None
    error: Optional[str] = None
    prerequisites: list[str] = None

    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []

class TaskOrchestrator:
    """Orchestrate multi-step tasks with prerequisite enforcement."""

    def __init__(self):
        self.tasks = {}
        self.execution_log = []

    def register_task(self, task: Task) -> None:
        """Register a task with its prerequisites."""
        self.tasks[task.task_id] = task

    def can_execute(self, task_id: str) -> tuple[bool, str]:
        """Check if all prerequisites are completed."""
        task = self.tasks.get(task_id)
        if not task:
            return False, f"Task {task_id} not found"

        for prereq_id in task.prerequisites:
            prereq = self.tasks.get(prereq_id)
            if not prereq:
                return False, f"Prerequisite task {prereq_id} not found"
            if prereq.status != TaskStatus.COMPLETED:
                return False, f"Prerequisite {prereq_id} not completed (status: {prereq.status.value})"

        return True, "All prerequisites satisfied"

    def execute_task(self, task_id: str) -> bool:
        """Execute a task only if prerequisites are satisfied."""
        can_run, reason = self.can_execute(task_id)

        if not can_run:
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "task_id": task_id,
                "status": "blocked",
                "reason": reason
            })
            return False

        task = self.tasks[task_id]
        task.status = TaskStatus.IN_PROGRESS

        try:
            result = task.handler()
            task.result = result
            task.status = TaskStatus.COMPLETED
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "task_id": task_id,
                "status": "completed",
                "result": result
            })
            return True
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "task_id": task_id,
                "status": "failed",
                "error": str(e)
            })
            return False

# Example: Customer refund workflow
if __name__ == "__main__":
    orchestrator = TaskOrchestrator()

    # Mock handlers
    def get_customer():
        return {"customer_id": "cust_123", "verified": True}

    def get_customer_account():
        return {"account_id": "acc_456", "balance": 5000, "valid": True}

    def verify_order():
        return {"order_id": "ord_789", "amount": 100, "valid": True}

    def process_refund():
        return {"refund_id": "ref_001", "status": "successful"}

    # Register tasks with prerequisites
    orchestrator.register_task(Task("get_customer", "Get customer", get_customer))
    orchestrator.register_task(Task(
        "get_account",
        "Get account",
        get_customer_account,
        prerequisites=["get_customer"]  # Must get customer first
    ))
    orchestrator.register_task(Task(
        "verify_order",
        "Verify order",
        verify_order,
        prerequisites=["get_customer"]  # Must get customer first
    ))
    orchestrator.register_task(Task(
        "process_refund",
        "Process refund",
        process_refund,
        prerequisites=["get_customer", "get_account", "verify_order"]  # All must complete
    ))

    # Try to execute refund without prerequisites
    success = orchestrator.execute_task("process_refund")
    print(f"Execute refund (no prerequisites met): {success}")
    # Output: False - blocked because prerequisites not completed

    # Execute in proper order
    orchestrator.execute_task("get_customer")
    orchestrator.execute_task("get_account")
    orchestrator.execute_task("verify_order")
    success = orchestrator.execute_task("process_refund")
    print(f"Execute refund (prerequisites satisfied): {success}")
    # Output: True - refund processed successfully
```

#### 2. Multi-Concern Decomposition and Parallel Investigation

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

class MultiConcernResolver:
    """Decompose complex requests into concerns, investigate in parallel, synthesize result."""

    @staticmethod
    def decompose_request(user_request: str) -> list[str]:
        """
        Extract distinct concerns from a multi-concern request.
        Example: "I want a refund and a replacement, plus I can't login"
        Concerns: ["refund", "replacement", "login_issue"]
        """
        # In real implementation, use LLM to extract concerns
        concerns = []

        refund_keywords = ["refund", "money back", "reimburse"]
        replacement_keywords = ["replacement", "replace", "new one"]
        login_keywords = ["login", "access", "password", "account"]

        request_lower = user_request.lower()
        if any(kw in request_lower for kw in refund_keywords):
            concerns.append("refund")
        if any(kw in request_lower for kw in replacement_keywords):
            concerns.append("replacement")
        if any(kw in request_lower for kw in login_keywords):
            concerns.append("login_access")

        return concerns

    @staticmethod
    def investigate_concern(concern: str, shared_context: dict) -> dict:
        """Investigate a single concern using shared context."""
        # Simulate investigation
        results = {
            "refund": {
                "eligible": True,
                "amount": 100,
                "reason": "Product defect",
                "confidence": 0.95
            },
            "replacement": {
                "eligible": True,
                "available": True,
                "reason": "Same issue reported by others",
                "confidence": 0.88
            },
            "login_access": {
                "eligible": True,
                "root_cause": "Password reset token expired",
                "solution": "Send password reset email",
                "confidence": 0.92
            }
        }
        return results.get(concern, {"eligible": False, "confidence": 0})

    @staticmethod
    def synthesize_resolution(investigations: dict) -> dict:
        """Synthesize individual investigations into unified resolution plan."""
        actions = []
        total_confidence = 0
        count = 0

        for concern, investigation in investigations.items():
            total_confidence += investigation.get("confidence", 0)
            count += 1

            if investigation.get("eligible"):
                if concern == "refund":
                    actions.append({
                        "action": "process_refund",
                        "amount": investigation["amount"],
                        "confidence": investigation["confidence"]
                    })
                elif concern == "replacement":
                    actions.append({
                        "action": "send_replacement",
                        "confidence": investigation["confidence"]
                    })
                elif concern == "login_access":
                    actions.append({
                        "action": "send_password_reset",
                        "confidence": investigation["confidence"]
                    })

        avg_confidence = total_confidence / count if count > 0 else 0

        return {
            "actions": actions,
            "average_confidence": avg_confidence,
            "synthesis_note": f"Resolved {len(investigations)} distinct concerns in parallel"
        }

    def resolve_multi_concern_request(self, user_request: str, shared_context: dict) -> dict:
        """End-to-end resolution of multi-concern request."""
        # Step 1: Decompose
        concerns = self.decompose_request(user_request)

        # Step 2: Investigate in parallel
        investigations = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.investigate_concern, concern, shared_context): concern
                for concern in concerns
            }

            for future in as_completed(futures):
                concern = futures[future]
                try:
                    result = future.result()
                    investigations[concern] = result
                except Exception as e:
                    investigations[concern] = {"error": str(e), "confidence": 0}

        # Step 3: Synthesize
        resolution = self.synthesize_resolution(investigations)

        return {
            "user_request": user_request,
            "concerns_identified": concerns,
            "investigations": investigations,
            "resolution": resolution
        }

# Example usage
if __name__ == "__main__":
    resolver = MultiConcernResolver()

    result = resolver.resolve_multi_concern_request(
        "I want a refund for my broken item, and I need a replacement. Also, I can't log in.",
        shared_context={"customer_id": "cust_123"}
    )

    print(f"Concerns identified: {result['concerns_identified']}")
    print(f"Planned actions:")
    for action in result['resolution']['actions']:
        print(f"  - {action['action']} (confidence: {action['confidence']:.0%})")
    print(f"Average confidence: {result['resolution']['average_confidence']:.0%}")
```

#### 3. Structured Handoff Summaries

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class HandoffSummary:
    """Complete, self-contained handoff for human agent."""
    handoff_id: str
    created_at: str
    customer_id: str
    customer_name: str
    customer_contact: str

    # Problem analysis
    issue_description: str
    root_cause: str
    investigation_steps: list[str]

    # What was attempted
    attempts: list[dict]  # [{"action": "...", "result": "...", "timestamp": "..."}]

    # Current state
    current_status: str
    blocker: str  # Why automated resolution failed
    escalation_reason: str

    # Recommendation
    recommended_action: str
    business_impact: str
    suggested_resolution: str

    # Metadata
    agent_name: str
    confidence_level: str  # "high", "medium", "low"
    priority: str  # "critical", "high", "medium", "low"

class HandoffGenerator:
    @staticmethod
    def generate_handoff(
        customer_id: str,
        customer_name: str,
        customer_contact: str,
        issue_description: str,
        root_cause: str,
        investigation_steps: list[str],
        attempts: list[dict],
        current_status: str,
        blocker: str,
        escalation_reason: str,
        recommended_action: str,
        business_impact: str,
        suggested_resolution: str,
        agent_name: str = "AutoAgent_v1",
        confidence_level: str = "medium",
        priority: str = "high"
    ) -> HandoffSummary:
        """Generate a structured handoff summary."""
        return HandoffSummary(
            handoff_id=f"HO_{datetime.now().timestamp()}",
            created_at=datetime.now().isoformat(),
            customer_id=customer_id,
            customer_name=customer_name,
            customer_contact=customer_contact,
            issue_description=issue_description,
            root_cause=root_cause,
            investigation_steps=investigation_steps,
            attempts=attempts,
            current_status=current_status,
            blocker=blocker,
            escalation_reason=escalation_reason,
            recommended_action=recommended_action,
            business_impact=business_impact,
            suggested_resolution=suggested_resolution,
            agent_name=agent_name,
            confidence_level=confidence_level,
            priority=priority
        )

    @staticmethod
    def format_for_human_agent(summary: HandoffSummary) -> str:
        """Format handoff summary as human-readable document."""
        return f"""
HANDOFF SUMMARY (ID: {summary.handoff_id})
Created: {summary.created_at}
Priority: {summary.priority}

CUSTOMER INFORMATION
- Customer ID: {summary.customer_id}
- Name: {summary.customer_name}
- Contact: {summary.customer_contact}

ISSUE SUMMARY
{summary.issue_description}

ROOT CAUSE ANALYSIS
{summary.root_cause}

INVESTIGATION STEPS TAKEN
{chr(10).join(f"- {step}" for step in summary.investigation_steps)}

PREVIOUS ATTEMPTS
{chr(10).join(f"- {a['action']}: {a['result']} ({a.get('timestamp', 'unknown')})" for a in summary.attempts)}

CURRENT STATUS
{summary.current_status}

BLOCKER
{summary.blocker}

ESCALATION REASON
{summary.escalation_reason}

RECOMMENDED ACTION
{summary.recommended_action}

BUSINESS IMPACT
{summary.business_impact}

SUGGESTED RESOLUTION
{summary.suggested_resolution}

AGENT CONFIDENCE
{summary.confidence_level} (Agent: {summary.agent_name})
"""

# Example usage
if __name__ == "__main__":
    handoff = HandoffGenerator.generate_handoff(
        customer_id="cust_123",
        customer_name="John Smith",
        customer_contact="john@example.com",
        issue_description="Customer reports product arrived damaged",
        root_cause="Shipping damage visible on unboxing video",
        investigation_steps=[
            "Reviewed order #ORD-456",
            "Confirmed delivery on 2026-03-20",
            "Examined customer-provided photos",
            "Checked shipping carrier for damage claims"
        ],
        attempts=[
            {"action": "Offered refund", "result": "Customer wants replacement instead", "timestamp": "2026-03-21T10:00Z"},
            {"action": "Checked inventory", "result": "Item in stock but awaiting manager approval for expedited replacement", "timestamp": "2026-03-21T10:05Z"}
        ],
        current_status="Item in stock, refund or replacement eligible",
        blocker="Expedited replacement requires manager approval per policy",
        escalation_reason="Decision requires manager authorization for expedited shipping cost",
        recommended_action="Approve expedited replacement with 2-day shipping",
        business_impact="Retain high-value customer (lifetime value: $2,000+)",
        suggested_resolution="Process replacement immediately, include apology gift ($25 store credit)",
        confidence_level="high",
        priority="high"
    )

    print(HandoffGenerator.format_for_human_agent(handoff))
```

#### 4. Confidence-Calibrated Escalation

```python
from enum import Enum

class ConfidenceLevel(Enum):
    VERY_LOW = (0.0, 0.4)
    LOW = (0.4, 0.6)
    MEDIUM = (0.6, 0.8)
    HIGH = (0.8, 0.95)
    VERY_HIGH = (0.95, 1.0)

    def from_value(self, value: float):
        for level in ConfidenceLevel:
            if level.value[0] <= value < level.value[1]:
                return level
        return ConfidenceLevel.VERY_HIGH

class EscalationRouter:
    """Route issues based on confidence level and business impact."""

    def __init__(self,
                 very_low_threshold: float = 0.4,
                 low_threshold: float = 0.6,
                 medium_threshold: float = 0.8):
        self.very_low_threshold = very_low_threshold
        self.low_threshold = low_threshold
        self.medium_threshold = medium_threshold

    def determine_route(self,
                       confidence: float,
                       business_impact: str,  # "low", "medium", "high"
                       action_reversible: bool) -> str:
        """Determine routing based on confidence, impact, and reversibility."""

        # High-impact + low-confidence = always escalate
        if business_impact == "high" and confidence < self.medium_threshold:
            return "escalate_to_human"

        # Low-impact + high-confidence = proceed automatically
        if business_impact == "low" and confidence > self.low_threshold:
            return "proceed_automated"

        # Medium-impact + medium-confidence with reversible action = proceed but notify
        if business_impact == "medium" and confidence > self.low_threshold and action_reversible:
            return "proceed_with_notification"

        # All other cases: escalate
        return "escalate_to_human"

    def route_decision(self,
                      decision: str,
                      confidence: float,
                      business_impact: str,
                      action_reversible: bool) -> dict:
        """End-to-end routing decision."""
        route = self.determine_route(confidence, business_impact, action_reversible)

        return {
            "decision": decision,
            "confidence": confidence,
            "business_impact": business_impact,
            "action_reversible": action_reversible,
            "route": route,
            "reasoning": self._explain_route(route, confidence, business_impact)
        }

    def _explain_route(self, route: str, confidence: float, impact: str) -> str:
        if route == "escalate_to_human":
            return f"Escalating: {impact} impact with {confidence:.0%} confidence is below threshold"
        elif route == "proceed_automated":
            return f"Proceeding: {impact} impact with {confidence:.0%} confidence is acceptable"
        else:
            return f"Proceeding with notification: {impact} impact with {confidence:.0%} confidence"

# Example usage
if __name__ == "__main__":
    router = EscalationRouter()

    test_cases = [
        ("refund_$50", 0.95, "low", True),  # Low impact, high confidence -> proceed
        ("refund_$500", 0.65, "high", True),  # High impact, medium confidence -> escalate
        ("account_deletion", 0.85, "high", False),  # Irreversible, high impact -> escalate
        ("reset_password", 0.90, "medium", True),  # Reversible, medium impact -> proceed with notification
    ]

    for decision, conf, impact, reversible in test_cases:
        result = router.route_decision(decision, conf, impact, reversible)
        print(f"{decision}: {result['route']}")
        print(f"  Confidence: {conf:.0%}, Impact: {impact}, Reversible: {reversible}")
        print()
```

---

## Task 5.3: Error Propagation Across Multi-Agent Systems

### Knowledge Breakdown

#### Error Handling in Subagents vs. Coordinators

**Local Recovery (in subagent):**
- Transient errors (network timeout, rate limit): retry with exponential backoff
- Temporary service unavailability: fallback to cached data or previous state
- Partial results: continue with what you have, mark what's missing

**Propagation to Coordinator:**
- Unrecoverable errors (permission denied, resource not found, invalid request)
- Repeated transient errors (retry limit exceeded)
- Errors that affect downstream dependencies

**Key principle:** Attempt recovery locally first. Escalate only when recovery is impossible or dangerous.

#### Partial Results and Attribution

When propagating errors, include:
1. **What was attempted** - The goal/action being performed
2. **What succeeded** - Concrete results obtained
3. **What failed** - Specific errors encountered
4. **Whether partial results are usable** - Can the coordinator proceed with incomplete data?

**Example:** "Called get_customer successfully, retrieved order history but rate-limited on payment methods. Partial result sufficient to proceed with refund approval."

#### Error Isolation and Graceful Degradation

**Error isolation:** One subagent's failure should not crash others.
- Each subagent should be independent
- Failures don't block other parallel subagents
- Coordinator can continue with available results

**Graceful degradation:** Deliver partial results clearly marked with what's missing.
- "Account verified but last 30 days of activity not available"
- "Can process refund but shipping address not confirmed"

#### Designing Circuit Breakers and Error Budgets

**Circuit breaker:** After N consecutive failures, stop trying and return error immediately.
- State: CLOSED (normal), OPEN (failing, don't try), HALF_OPEN (test if recovered)
- Prevents cascading failures from consuming resources

**Error budget:** Track cumulative failures to decide if system is healthy.
- Example: "If >20% of calls fail in last 5 minutes, circuit opens"
- Allows some failures while maintaining system stability

### Skills: Implementation Patterns

#### 1. Try-Catch and Local Recovery in Subagents

```python
import time
from enum import Enum
from typing import Optional, Callable, Any

class ErrorType(Enum):
    TRANSIENT = "transient"  # Retry possible
    PERMANENT = "permanent"  # Don't retry
    UNKNOWN = "unknown"

class RetryConfig:
    def __init__(self,
                 max_attempts: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 30.0,
                 backoff_factor: float = 2.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor

class SubagentErrorHandler:
    """Handle errors in subagent with local recovery."""

    @staticmethod
    def classify_error(error: Exception) -> ErrorType:
        """Classify if error is transient or permanent."""
        error_str = str(error).lower()

        transient_keywords = ["timeout", "rate limit", "temporarily unavailable", "connection"]
        permanent_keywords = ["not found", "invalid", "unauthorized", "permission denied"]

        if any(kw in error_str for kw in transient_keywords):
            return ErrorType.TRANSIENT
        elif any(kw in error_str for kw in permanent_keywords):
            return ErrorType.PERMANENT
        else:
            return ErrorType.UNKNOWN

    @staticmethod
    def attempt_with_recovery(handler: Callable,
                             fallback: Optional[Callable] = None,
                             retry_config: Optional[RetryConfig] = None) -> tuple[Any, dict]:
        """
        Attempt operation with local recovery.

        Returns: (result, metadata)
        metadata includes: success, attempts, errors, recovered_from_fallback
        """
        if retry_config is None:
            retry_config = RetryConfig()

        metadata = {
            "success": False,
            "attempts": 0,
            "errors": [],
            "recovered_from_fallback": False
        }

        for attempt in range(retry_config.max_attempts):
            metadata["attempts"] += 1

            try:
                result = handler()
                metadata["success"] = True
                return result, metadata

            except Exception as e:
                error_type = SubagentErrorHandler.classify_error(e)
                metadata["errors"].append({
                    "attempt": attempt + 1,
                    "error": str(e),
                    "type": error_type.value
                })

                # Don't retry permanent errors
                if error_type == ErrorType.PERMANENT:
                    break

                # For transient errors, retry with backoff
                if attempt < retry_config.max_attempts - 1:
                    delay = min(
                        retry_config.base_delay * (retry_config.backoff_factor ** attempt),
                        retry_config.max_delay
                    )
                    time.sleep(delay)

        # All retries exhausted, try fallback
        if fallback:
            try:
                result = fallback()
                metadata["success"] = True
                metadata["recovered_from_fallback"] = True
                return result, metadata
            except Exception as e:
                metadata["errors"].append({
                    "fallback": True,
                    "error": str(e)
                })

        return None, metadata

# Example usage
if __name__ == "__main__":
    call_count = 0

    def unreliable_api():
        global call_count
        call_count += 1
        if call_count < 3:
            raise TimeoutError("Connection timeout (transient)")
        return {"data": "success"}

    def cached_fallback():
        return {"data": "cached"}

    result, metadata = SubagentErrorHandler.attempt_with_recovery(
        unreliable_api,
        fallback=cached_fallback,
        retry_config=RetryConfig(max_attempts=5)
    )

    print(f"Result: {result}")
    print(f"Metadata: {metadata}")
    # Output shows: 2 failed attempts, then successful on attempt 3
```

#### 2. Propagating Errors with Structured Metadata

```python
from dataclasses import dataclass, asdict
from typing import Optional, Any
from datetime import datetime

@dataclass
class PartialResult:
    """Result with partial success and structured error info."""
    success_data: dict
    failed_operations: list[str]
    usable: bool  # Can coordinator proceed?
    errors: list[dict]
    timestamp: str

class SubagentResult:
    """Wrap subagent results with error context."""

    def __init__(self,
                 subagent_id: str,
                 operation: str,
                 success: bool,
                 data: Optional[Any] = None,
                 error: Optional[str] = None,
                 recoverable: bool = False):
        self.subagent_id = subagent_id
        self.operation = operation
        self.success = success
        self.data = data
        self.error = error
        self.recoverable = recoverable
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "subagent_id": self.subagent_id,
            "operation": self.operation,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "recoverable": self.recoverable,
            "timestamp": self.timestamp
        }

def get_customer_with_propagation(customer_id: str) -> SubagentResult:
    """Subagent: get customer with structured error propagation."""
    try:
        # Simulate API call
        if customer_id == "unknown":
            raise ValueError(f"Customer {customer_id} not found")

        customer_data = {
            "id": customer_id,
            "name": "John Doe",
            "verified": True
        }

        return SubagentResult(
            subagent_id="customer_service",
            operation="get_customer",
            success=True,
            data=customer_data
        )

    except Exception as e:
        # Classify if recoverable (transient) or permanent
        error_str = str(e)
        recoverable = "timeout" in error_str or "temporarily" in error_str

        return SubagentResult(
            subagent_id="customer_service",
            operation="get_customer",
            success=False,
            error=error_str,
            recoverable=recoverable
        )

def get_orders_with_partial_result(customer_id: str) -> SubagentResult:
    """Subagent: get orders, may return partial result on rate limit."""
    try:
        orders = [
            {"id": "ORD-001", "amount": 100},
            {"id": "ORD-002", "amount": 250},
            # Simulate: last order fails to fetch due to rate limit
        ]

        # Check if rate limited
        rate_limited = True
        if rate_limited:
            # Return partial result with indication
            return SubagentResult(
                subagent_id="order_service",
                operation="get_orders",
                success=False,  # Operation didn't fully complete
                data={
                    "partial_orders": orders,
                    "failed_to_fetch": ["ORD-003"],  # What we couldn't get
                    "reason": "Rate limited after 2 orders"
                },
                error="Rate limit exceeded on order details",
                recoverable=True
            )

        return SubagentResult(
            subagent_id="order_service",
            operation="get_orders",
            success=True,
            data={"orders": orders}
        )

    except Exception as e:
        return SubagentResult(
            subagent_id="order_service",
            operation="get_orders",
            success=False,
            error=str(e),
            recoverable=False
        )

# Example: Coordinator handling subagent results
def coordinate_customer_refund(customer_id: str) -> dict:
    """Coordinator: use subagent results to make refund decision."""

    # Call subagents
    customer_result = get_customer_with_propagation(customer_id)
    orders_result = get_orders_with_partial_result(customer_id)

    print(f"Customer lookup: {'✓' if customer_result.success else '✗'}")
    print(f"Orders lookup: {'✓ (partial)' if orders_result.data and not orders_result.success else '✓' if orders_result.success else '✗'}")

    # Coordinator logic: what can we do with these results?
    if not customer_result.success:
        if customer_result.recoverable:
            return {
                "status": "retry_later",
                "reason": "Customer service transient error",
                "subagent_results": [customer_result.to_dict()]
            }
        else:
            return {
                "status": "escalate",
                "reason": f"Customer not found: {customer_result.error}",
                "subagent_results": [customer_result.to_dict()]
            }

    # Customer verified, but orders partially retrieved
    if orders_result.data:  # Has partial data
        return {
            "status": "proceed_with_caution",
            "reason": "Refund possible but order history incomplete",
            "customer": customer_result.data,
            "orders": orders_result.data["partial_orders"],
            "missing_orders": orders_result.data.get("failed_to_fetch", []),
            "recommendation": "Can process refund for verified orders; escalate for complete history",
            "subagent_results": [customer_result.to_dict(), orders_result.to_dict()]
        }

    return {
        "status": "proceed",
        "customer": customer_result.data,
        "subagent_results": [customer_result.to_dict(), orders_result.to_dict()]
    }

if __name__ == "__main__":
    result = coordinate_customer_refund("cust_123")
    print(f"\nCoordination result: {result['status']}")
    print(f"Reason: {result.get('reason', 'N/A')}")
```

#### 3. Circuit Breaker Pattern

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, don't try
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Prevent cascading failures from unhealthy services."""

    def __init__(self,
                 name: str,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 success_threshold: int = 2):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout  # seconds
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.open_since = None

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout elapsed
            if datetime.now() - self.open_since > timedelta(seconds=self.recovery_timeout):
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                print(f"[{self.name}] Circuit entering HALF_OPEN state")
            else:
                raise Exception(f"Circuit breaker {self.name} is OPEN")

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result

        except Exception as e:
            self._record_failure()
            raise e

    def _record_success(self):
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                print(f"[{self.name}] Circuit CLOSED - recovered")

    def _record_failure(self):
        self.last_failure_time = datetime.now()
        self.failure_count += 1

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.open_since = datetime.now()
            print(f"[{self.name}] Circuit OPEN - too many failures")

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.open_since = datetime.now()
            print(f"[{self.name}] Circuit OPEN - failed during recovery test")

# Example usage
if __name__ == "__main__":
    breaker = CircuitBreaker("payment_service", failure_threshold=3, recovery_timeout=5)

    fail_count = 0
    def flaky_payment_call():
        global fail_count
        fail_count += 1
        if fail_count <= 3:
            raise Exception("Service unavailable")
        return {"status": "success"}

    # Attempt 1-3: fail and accumulate failures
    for i in range(3):
        try:
            breaker.call(flaky_payment_call)
        except:
            print(f"Attempt {i+1}: Failed")

    # Attempt 4: circuit is open
    try:
        breaker.call(flaky_payment_call)
    except Exception as e:
        print(f"Attempt 4: {e} (circuit open)")

    # Wait for recovery timeout
    print("\nWaiting for recovery timeout...")
    time.sleep(6)

    # Attempt 5: Half-open state, should succeed
    try:
        result = breaker.call(flaky_payment_call)
        print(f"Attempt 5: Success - {result}")
    except Exception as e:
        print(f"Attempt 5: Failed - {e}")
```

---

## Task 5.4: Context Management in Large Codebase Exploration

### Knowledge Breakdown

#### Incremental Codebase Understanding

**Don't:** Read all files upfront (consumes massive context, often irrelevant)

**Do:** Build understanding incrementally:
1. **Grep to find entry points** - Locate main functions, class definitions, imports
2. **Read key files** - Follow imports to understand dependencies
3. **Trace function usage** - Search for where functions are called
4. **Use Explore subagent** - Isolate verbose discovery, get summary back

This keeps context usage manageable while maintaining comprehensive understanding.

#### Starting with Entry Points

Entry points are the gateways into code:
- `main()` function
- `__init__` in package
- API routes
- Exported functions
- Configuration files

Searching for these first gives you the architecture "skeleton" before diving into details.

#### The Explore Subagent Pattern

**Problem:** Multi-file exploration creates verbose output that consumes context.

**Solution:** Use subagent for exploration:
1. Main conversation: "Explore the authentication module and summarize how tokens are validated"
2. Subagent spawned: Does all the grepping, reading, searching
3. Subagent returns: Concise summary with key findings
4. Main conversation: Uses summary without verbose output

This keeps the main conversation focused on high-level reasoning.

### Skills: Implementation Patterns

#### 1. Incremental Codebase Understanding

```python
from typing import Optional
from dataclasses import dataclass

@dataclass
class CodeSearchResult:
    file_path: str
    line_number: int
    context: str

class CodebaseExplorer:
    """Build codebase understanding incrementally."""

    def __init__(self):
        self.explored_files = set()
        self.understood_functions = {}
        self.import_graph = {}

    def find_entry_points(self, codebase_path: str, file_type: str = ".py") -> list[str]:
        """
        Step 1: Find entry points using grep patterns.
        Returns: candidate main functions/classes.
        """
        entry_point_patterns = [
            r"def main\(",
            r"class \w+Application",
            r"class \w+Server",
            r"def start\(",
            r"if __name__ == ['\"]__main__['\"]:"
        ]

        # In real implementation, would grep codebase
        print(f"Searching for entry points in {codebase_path}...")
        print(f"  - Looking for: main(), *Application, *Server classes, start()")

        return [
            "app.py::main",
            "server.py::Server::run",
            "cli.py::CLI::execute"
        ]

    def trace_imports(self, file_path: str) -> dict:
        """
        Step 2: Read file, identify imports, follow dependency chain.
        """
        print(f"Reading {file_path}...")

        # Simulate reading file
        imports = {
            "local": ["auth", "database", "models"],
            "external": ["flask", "sqlalchemy"]
        }

        self.import_graph[file_path] = imports
        return imports

    def find_function_usage(self, function_name: str, codebase_path: str) -> list[CodeSearchResult]:
        """
        Step 3: Search for where function is called (grep for usage).
        """
        print(f"Searching for usage of {function_name}...")

        # Simulate grep results
        return [
            CodeSearchResult("auth/validators.py", 45, f"  result = {function_name}(token)"),
            CodeSearchResult("api/routes.py", 123, f"  verify_{function_name}()"),
        ]

    def understand_function_flow(self, function_name: str, file_path: str) -> dict:
        """
        Step 4: Read function definition, understand logic.
        """
        print(f"Understanding {function_name} in {file_path}...")

        # Simulate reading function
        understanding = {
            "name": function_name,
            "parameters": ["token", "secret"],
            "returns": "bool",
            "logic": "Validates JWT signature",
            "calls": ["jwt.decode()", "crypto.verify()"],
            "key_insight": "Uses HS256 algorithm"
        }

        self.understood_functions[function_name] = understanding
        return understanding

    def explore_incrementally(self, starting_point: str, search_depth: int = 3) -> dict:
        """
        Full incremental exploration workflow.
        """
        findings = {
            "entry_points": [],
            "import_dependencies": {},
            "function_flows": {},
            "key_insights": []
        }

        # Step 1: Find entry points
        entry_points = self.find_entry_points(".")
        findings["entry_points"] = entry_points

        # Step 2: For each entry point, trace imports
        for ep in entry_points[:search_depth]:
            imports = self.trace_imports(f"{ep.split('::')[0]}")
            findings["import_dependencies"][ep] = imports

            # Step 3: Find usage of key functions
            for local_import in imports.get("local", []):
                usage = self.find_function_usage(local_import, ".")

        # Step 4: Understand specific flows
        findings["function_flows"]["validate_token"] = self.understand_function_flow(
            "validate_token",
            "auth/validators.py"
        )

        findings["key_insights"] = [
            "Authentication uses JWT with HS256",
            "Database accessed through ORM (SQLAlchemy)",
            "API routes are Flask-based"
        ]

        return findings

# Example usage
if __name__ == "__main__":
    explorer = CodebaseExplorer()
    findings = explorer.explore_incrementally("app.py")

    print("\n=== EXPLORATION SUMMARY ===")
    print(f"Entry points found: {len(findings['entry_points'])}")
    print(f"Dependencies identified: {len(findings['import_dependencies'])}")
    print(f"Key insights: {findings['key_insights']}")
```

#### 2. Tracing Function Usage Across Modules

```python
from collections import defaultdict

class FunctionTracer:
    """Trace function usage across codebase."""

    def __init__(self):
        self.function_definitions = {}  # {function_name: file_path}
        self.function_calls = defaultdict(list)  # {function_name: [call_sites]}

    def identify_exported_names(self, module_path: str) -> list[str]:
        """
        Step 1: Identify all exported symbols from a module.
        (Would use grep for __all__, public functions, etc.)
        """
        print(f"Identifying exported names from {module_path}...")

        # Simulate grep results
        exports = [
            "validate_token",
            "TokenValidator",
            "InvalidTokenError"
        ]

        for export in exports:
            self.function_definitions[export] = module_path

        return exports

    def find_all_usages(self, function_name: str, codebase_path: str) -> dict:
        """
        Step 2: Search all files for each exported name.
        """
        print(f"Searching for all usages of {function_name}...")

        # Simulate grep across codebase
        usages = {
            "direct_calls": [
                "api/routes.py:45:  token_valid = validate_token(req.headers)",
                "middleware/auth.py:120:  if validate_token(token):"
            ],
            "imports": [
                "api/routes.py:1: from auth import validate_token",
                "cli/commands.py:5: from auth.validators import validate_token"
            ],
            "references": [
                "tests/test_auth.py:30: assert validate_token is not None"
            ]
        }

        self.function_calls[function_name] = usages
        return usages

    def trace_full_usage_graph(self, starting_module: str) -> dict:
        """
        End-to-end: Identify exports, find all usages.
        """
        # Step 1: Identify all exported names
        exports = self.identify_exported_names(starting_module)

        # Step 2: For each exported name, find all usages
        usage_graph = {}
        for export_name in exports:
            usages = self.find_all_usages(export_name, ".")
            usage_graph[export_name] = usages

        return {
            "module": starting_module,
            "exports": exports,
            "usage_graph": usage_graph,
            "summary": f"Found {len(exports)} exports with {sum(len(v['direct_calls']) for v in usage_graph.values())} direct call sites"
        }

# Example usage
if __name__ == "__main__":
    tracer = FunctionTracer()
    graph = tracer.trace_full_usage_graph("auth/validators.py")

    print(f"\n=== USAGE GRAPH ===")
    print(f"Module: {graph['module']}")
    print(f"Exports: {graph['exports']}")
    for func_name, usages in graph['usage_graph'].items():
        print(f"\n{func_name}:")
        print(f"  Direct calls: {len(usages['direct_calls'])}")
        print(f"  Imports: {len(usages['imports'])}")
```

#### 3. Explore Subagent Pattern (Conceptual)

```python
"""
The Explore Subagent pattern isolates verbose discovery work.

Main Conversation:
  "What does the authentication module do?"

Subagent Task Created:
  "Explore auth/ directory: find entry points, identify main components,
   trace usage of validate_token() function, summarize findings."

Subagent Work (verbose, internal):
  - Grep for validate_token definition
  - Read auth/validators.py
  - Grep for validate_token usage across codebase
  - Grep for class definitions in auth/
  - Read auth/exceptions.py
  - Summarize findings

Subagent Returns to Main:
  "Authentication module overview:
   - validate_token() is the main export, called from 12 sites
   - Uses JWT with HS256 algorithm
   - Throws InvalidTokenError on failure
   - Integrated into middleware and API routes
   - Tests in tests/test_auth.py show expected behavior"

Main Conversation Continues:
  "Now I understand auth. Let's look at the database layer."
"""

class ExploreSubagent:
    """
    Conceptual: How to design a subagent for exploration tasks.

    In practice, this would spawn a new Claude session with:
    - Access to grep, read, search tools
    - Instructions to be verbose internally but summarize at the end
    - Task: "Explore [module] and return a concise summary"
    """

    def __init__(self, subagent_task: str):
        self.task = subagent_task
        self.verbose_work = []
        self.summary = None

    def work_step(self, step_description: str, details: str):
        """Record verbose work internally."""
        self.verbose_work.append({
            "step": step_description,
            "details": details
        })

    def generate_summary(self) -> str:
        """Produce concise summary after all work is done."""
        return f"""
EXPLORATION SUMMARY: {self.task}

Key Findings:
- [Finding 1]
- [Finding 2]
- [Finding 3]

Architecture Pattern:
[One-line description]

Integration Points:
[How this module connects to rest of system]

Recommended Next Steps:
[What to explore next]
"""

# Example: How to use Explore pattern in conversation
"""
MAIN AGENT:
"User is asking about authentication flow. This requires understanding auth/,
but reading all files would consume lots of context. I'll spawn an Explore subagent."

>>> Spawn subagent: "Explore auth/ module. Find: (1) main entry points,
    (2) validate_token flow, (3) error handling, (4) integration with middleware.
    Return concise summary of authentication architecture."

SUBAGENT WORK (verbose, not shown to user):
- Grep "def validate" in auth/
- Read auth/validators.py (2000 tokens)
- Grep "validate_token" in api/, middleware/
- Read auth/exceptions.py (500 tokens)
- Read middleware/auth.py (1500 tokens)
- Grep "TokenValidator" class usage
- Internal notes: Very verbose, lots of details

SUBAGENT RETURNS (concise):
"Authentication uses token validation pattern:
1. validate_token(token) checks JWT signature using HS256
2. Called from middleware before route handlers
3. Raises InvalidTokenError if invalid
4. Integration in middleware/auth.py at line 45
Total call sites: 12"

MAIN AGENT (now with context-efficient summary):
"OK, I understand the auth flow now. Let me explore the database layer..."
"""
```

---

## Task 5.5: Human Review Workflows and Confidence Calibration

### Knowledge Breakdown

#### Self-Review Limitations

**Why self-review fails:**
- The model retains its reasoning context from generation
- It's unlikely to question its own reasoning in the same session
- It becomes "locked in" to the original reasoning path

**Example:** If Claude generates "The answer is 42" with specific reasoning, asking it to review that same output in the same session rarely catches errors because the context still contains the original reasoning.

**Solution:** Independent review instances (different Claude instances, no shared context) are far more effective at catching errors.

#### Confidence Calibration and Self-Reporting

Rather than the model simply saying "I think the answer is 42," it should report:
- **Finding:** "The answer is 42"
- **Confidence:** "85% confident"
- **Reasoning:** "Based on X and Y; uncertain about Z"

This allows human reviewers to prioritize:
- High confidence, high impact → might skip review
- Low confidence, low impact → might auto-accept
- Low confidence, high impact → definitely review
- High confidence, high impact → definitely review (rare but critical)

#### Independent Review Instances

**Self-review (same session):**
```
Agent: "The answer is 42"
Agent (reviewing itself): "Yes, looks right" ← Biased by original reasoning
```

**Independent review:**
```
Agent: "The answer is 42" (confidence: 60%)
Separate Claude instance (no context): "I think the answer is 41" (confidence: 70%)
Human: "These disagree; let me investigate"
```

The disagreement signals that independent review caught something.

#### Human Review Queues and Prioritization

Route items to human review based on:
1. **Confidence level** - Low confidence items first
2. **Business impact** - High-impact items first
3. **Reversibility** - Irreversible actions reviewed more carefully
4. **Category** - Different teams review different item types

### Skills: Implementation Patterns

#### 1. Confidence Calibration and Self-Reporting

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ConfidenceLevel(Enum):
    VERY_LOW = (0.0, 0.33)
    LOW = (0.33, 0.66)
    MEDIUM = (0.66, 0.80)
    HIGH = (0.80, 0.95)
    VERY_HIGH = (0.95, 1.0)

@dataclass
class CalibratedFinding:
    """Finding with confidence and reasoning."""
    finding: str
    confidence: float
    confidence_level: str
    reasoning: str
    uncertainties: list[str]
    evidence: list[str]

class ConfidenceCalibrator:
    """Generate findings with calibrated confidence levels."""

    @staticmethod
    def classify_confidence(confidence: float) -> str:
        """Map confidence score to level name."""
        for level in ConfidenceLevel:
            if level.value[0] <= confidence < level.value[1]:
                return level.name.lower()
        return "very_high"

    @staticmethod
    def generate_finding(finding: str,
                        confidence: float,
                        reasoning: str,
                        uncertainties: list[str],
                        evidence: list[str]) -> CalibratedFinding:
        """Create a finding with calibrated confidence."""

        if not (0 <= confidence <= 1):
            raise ValueError("Confidence must be between 0 and 1")

        return CalibratedFinding(
            finding=finding,
            confidence=confidence,
            confidence_level=ConfidenceCalibrator.classify_confidence(confidence),
            reasoning=reasoning,
            uncertainties=uncertainties,
            evidence=evidence
        )

    @staticmethod
    def format_for_review(finding: CalibratedFinding) -> str:
        """Format finding for human review."""
        return f"""
FINDING: {finding.finding}

CONFIDENCE: {finding.confidence:.0%} ({finding.confidence_level})

REASONING:
{finding.reasoning}

EVIDENCE:
{chr(10).join(f"- {e}" for e in finding.evidence)}

UNCERTAINTIES:
{chr(10).join(f"- {u}" for u in finding.uncertainties)}
"""

# Example usage
if __name__ == "__main__":
    finding = ConfidenceCalibrator.generate_finding(
        finding="Customer is eligible for refund",
        confidence=0.82,
        reasoning="Order is within 30-day window, item has defect, customer has verified account history",
        uncertainties=[
            "Unclear if defect is manufacturing vs. shipping damage",
            "Customer damaged protective packaging before reporting"
        ],
        evidence=[
            "Order placed 2026-03-10 (12 days ago)",
            "Customer submitted damage photos on 2026-03-20",
            "Account created 2025-06-01 (9 months old)",
            "No previous refunds in account history"
        ]
    )

    print(ConfidenceCalibrator.format_for_review(finding))
```

#### 2. Human Review Queue with Routing

```python
from datetime import datetime
from typing import Optional
from enum import Enum

class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class ReviewItem:
    def __init__(self,
                 item_id: str,
                 finding: str,
                 confidence: float,
                 business_impact: str,  # "low", "medium", "high"
                 reversible: bool,
                 category: str,  # "refund", "account", "diagnostic", etc.
                 created_at: Optional[str] = None):
        self.item_id = item_id
        self.finding = finding
        self.confidence = confidence
        self.business_impact = business_impact
        self.reversible = reversible
        self.category = category
        self.created_at = created_at or datetime.now().isoformat()
        self.priority = self._calculate_priority()

    def _calculate_priority(self) -> Priority:
        """Calculate priority based on confidence and impact."""

        # Low confidence always high priority
        if self.confidence < 0.66:
            return Priority.CRITICAL if self.business_impact == "high" else Priority.HIGH

        # High impact always priority
        if self.business_impact == "high":
            return Priority.HIGH if self.confidence < 0.85 else Priority.MEDIUM

        # Irreversible actions higher priority
        if not self.reversible:
            return Priority.MEDIUM if self.confidence < 0.9 else Priority.LOW

        # Default: low priority for reversible, high-confidence, low-impact
        return Priority.LOW

class ReviewQueue:
    """Human review queue with intelligent routing."""

    def __init__(self):
        self.queue = []
        self.completed = []

    def add_item(self, item: ReviewItem) -> None:
        """Add item to review queue."""
        self.queue.append(item)
        self._sort_queue()

    def _sort_queue(self) -> None:
        """Sort by priority, then by creation time."""
        self.queue.sort(
            key=lambda x: (x.priority.value, x.created_at)
        )

    def get_next_item(self, reviewer_role: str) -> Optional[ReviewItem]:
        """Get next item for specific reviewer role."""
        # Filter by role
        role_categories = {
            "refund_specialist": ["refund", "return"],
            "account_manager": ["account", "identity"],
            "quality_assurance": ["diagnostic", "analysis"]
        }

        allowed_categories = role_categories.get(reviewer_role, [])

        for item in self.queue:
            if item.category in allowed_categories:
                return item

        return None

    def mark_reviewed(self, item_id: str, approved: bool, notes: str) -> None:
        """Mark item as reviewed."""
        item = next((i for i in self.queue if i.item_id == item_id), None)
        if item:
            self.queue.remove(item)
            self.completed.append({
                "item_id": item_id,
                "approved": approved,
                "notes": notes,
                "reviewed_at": datetime.now().isoformat()
            })

    def get_queue_summary(self) -> dict:
        """Summary of queue status."""
        return {
            "total_items": len(self.queue),
            "critical": sum(1 for i in self.queue if i.priority == Priority.CRITICAL),
            "high": sum(1 for i in self.queue if i.priority == Priority.HIGH),
            "medium": sum(1 for i in self.queue if i.priority == Priority.MEDIUM),
            "low": sum(1 for i in self.queue if i.priority == Priority.LOW),
            "by_category": self._group_by_category()
        }

    def _group_by_category(self) -> dict:
        """Group items by category."""
        groups = {}
        for item in self.queue:
            groups.setdefault(item.category, []).append(item.item_id)
        return groups

# Example usage
if __name__ == "__main__":
    queue = ReviewQueue()

    # Add various items
    queue.add_item(ReviewItem(
        "item_1",
        "Approve $500 refund",
        confidence=0.95,
        business_impact="high",
        reversible=True,
        category="refund"
    ))

    queue.add_item(ReviewItem(
        "item_2",
        "Delete customer account",
        confidence=0.60,
        business_impact="high",
        reversible=False,
        category="account"
    ))

    queue.add_item(ReviewItem(
        "item_3",
        "Diagnostic: likely billing error",
        confidence=0.72,
        business_impact="medium",
        reversible=True,
        category="diagnostic"
    ))

    # Show queue status
    print("=== REVIEW QUEUE ===")
    summary = queue.get_queue_summary()
    print(f"Total items: {summary['total_items']}")
    print(f"Critical: {summary['critical']}, High: {summary['high']}, Medium: {summary['medium']}")

    # Get next item for refund specialist
    next_item = queue.get_next_item("refund_specialist")
    if next_item:
        print(f"\nNext for refund specialist: {next_item.finding} (Priority: {next_item.priority.name})")
```

#### 3. Independent Review Instance Pattern

```python
"""
INDEPENDENT REVIEW PATTERN

Original Agent (Session A):
- Analyzes customer request
- Generates finding with reasoning
- Reports confidence

Independent Reviewer (Session B):
- Receives ONLY: Finding, customer data (no original reasoning)
- Analyzes independently
- Reports own confidence and any disagreements

If confident findings disagree -> requires human arbitration
If reviewer is more confident -> suggests correction
If reviewer agrees and confident -> approves action

This prevents "confirmation bias" from same-session self-review.
"""

@dataclass
class FindingWithContext:
    """Finding + minimal context for independent review."""
    finding_id: str
    finding_text: str
    original_confidence: float
    customer_data: dict  # Minimal: ID, account status, order info
    action_requested: str

class IndependentReviewProcess:
    """
    Simulate independent review by separate Claude instance.
    In practice, this spawns a new session.
    """

    def __init__(self, finding: FindingWithContext):
        self.finding = finding
        self.review_confidence = None
        self.review_conclusion = None
        self.agreements = []
        self.disagreements = []

    def review_independently(self) -> dict:
        """
        Simulate independent Claude reviewing the finding.

        Note: Real implementation would spawn separate Claude session
        with instructions: "Review this finding independently. What is
        your confidence? Do you agree?"
        """

        # Simulate independent analysis
        # (In real world, this would be actual Claude API call)

        self.review_confidence = 0.88  # Different from original
        self.review_conclusion = f"Agree: {self.finding.finding_text}"

        # Compare with original
        confidence_diff = abs(self.review_confidence - self.finding.original_confidence)

        if confidence_diff > 0.15:
            self.disagreements.append(
                f"Confidence difference: Original {self.finding.original_confidence:.0%}, "
                f"Review {self.review_confidence:.0%}"
            )
        else:
            self.agreements.append("Confidence levels align")

        return {
            "finding_id": self.finding.finding_id,
            "original_confidence": self.finding.original_confidence,
            "review_confidence": self.review_confidence,
            "review_conclusion": self.review_conclusion,
            "high_confidence_agreement": self.review_confidence > 0.85 and self.finding.original_confidence > 0.85,
            "potential_disagreement": len(self.disagreements) > 0,
            "requires_human_review": len(self.disagreements) > 0 or self.review_confidence < 0.7,
            "differences": self.disagreements
        }

# Example: Two-stage review process
if __name__ == "__main__":
    # Stage 1: Original agent finds something
    original_finding = FindingWithContext(
        finding_id="finding_001",
        finding_text="Customer eligible for $500 refund",
        original_confidence=0.92,
        customer_data={
            "customer_id": "cust_123",
            "account_age_days": 120,
            "account_status": "verified"
        },
        action_requested="process_refund"
    )

    print(f"Original finding: {original_finding.finding_text}")
    print(f"Original confidence: {original_finding.original_confidence:.0%}")

    # Stage 2: Independent review
    reviewer = IndependentReviewProcess(original_finding)
    review_result = reviewer.review_independently()

    print(f"\nIndependent review confidence: {review_result['review_confidence']:.0%}")
    print(f"High-confidence agreement: {review_result['high_confidence_agreement']}")
    print(f"Requires human review: {review_result['requires_human_review']}")

    if review_result['differences']:
        print("Differences found:")
        for diff in review_result['differences']:
            print(f"  - {diff}")
```

---

## Task 5.6: Information Provenance and Uncertainty

### Knowledge Breakdown

#### Importance of Tracking Sources in Multi-Agent Systems

In a multi-agent system, information passes through multiple hands:
- Agent A reads a document and extracts customer info
- Agent B receives that info and makes a decision
- Agent C implements the decision

If there's ambiguity later ("Did the document really say that?"), you need to trace back. Provenance (source tracking) enables this.

**Without provenance:** "The system decided X" - unclear why or based on what
**With provenance:** "Agent A extracted X from document Y (line Z), then Agent B used it to decide..."

#### Information Sources and Attribution

Always separate:
- **Content:** "Customer verified"
- **Source metadata:** {url: "...", page: 3, timestamp: 2026-03-20}

This allows downstream agents to:
- Verify claims against originals
- Assess source reliability
- Trace incorrect decisions back to bad source data

#### Expressing Uncertainty vs. Fabrication

**Don't:** Generate plausible-sounding but unverified information
**Do:** Explicitly state what's unknown

```python
# Bad: Agent asserts without evidence
"Customer has not contacted support in 6 months"  # Made up?

# Good: Explicit uncertainty
"Customer support history: Last contact was 2026-01-15 (66 days ago)
 Note: Support history may be incomplete if customer contacted other channels"
```

#### Provenance Tracking Across Handoffs

When Agent A hands off to Agent B:
- Include source URLs, document names, page numbers
- Timestamp when information was retrieved
- Indicate confidence level and any caveats
- Flag if information is inferred vs. directly stated

### Skills: Implementation Patterns

#### 1. Structured Data with Separated Content and Metadata

```python
from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime

@dataclass
class SourceMetadata:
    """Metadata about information source."""
    source_type: str  # "document", "api", "database", "video", etc.
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    page_number: Optional[int] = None
    line_number: Optional[int] = None
    retrieved_at: str = None
    retrieved_by: Optional[str] = None
    confidence: float = 1.0  # How confident we are in this source

    def __post_init__(self):
        if self.retrieved_at is None:
            self.retrieved_at = datetime.now().isoformat()

@dataclass
class ProvenanceRecord:
    """Information with provenance."""
    content: Any  # The actual data/finding
    metadata: SourceMetadata
    caveats: list[str] = None  # Limitations or uncertainties
    derived_from: Optional[list['ProvenanceRecord']] = None

    def __post_init__(self):
        if self.caveats is None:
            self.caveats = []

class ProvenanceTracker:
    """Track and format information with provenance."""

    @staticmethod
    def create_record(content: Any,
                     source_type: str,
                     source_url: Optional[str] = None,
                     source_name: Optional[str] = None,
                     page_number: Optional[int] = None,
                     confidence: float = 1.0,
                     caveats: Optional[list[str]] = None) -> ProvenanceRecord:
        """Create a provenance record."""
        metadata = SourceMetadata(
            source_type=source_type,
            source_url=source_url,
            source_name=source_name,
            page_number=page_number,
            confidence=confidence
        )

        return ProvenanceRecord(
            content=content,
            metadata=metadata,
            caveats=caveats or []
        )

    @staticmethod
    def format_for_human_review(record: ProvenanceRecord) -> str:
        """Format record with full provenance."""
        output = f"INFORMATION: {record.content}\n\n"

        output += "SOURCE METADATA:\n"
        output += f"  Type: {record.metadata.source_type}\n"
        if record.metadata.source_url:
            output += f"  URL: {record.metadata.source_url}\n"
        if record.metadata.source_name:
            output += f"  Name: {record.metadata.source_name}\n"
        if record.metadata.page_number:
            output += f"  Page: {record.metadata.page_number}\n"
        output += f"  Retrieved: {record.metadata.retrieved_at}\n"
        output += f"  Confidence: {record.metadata.confidence:.0%}\n"

        if record.caveats:
            output += "\nCAVEATS:\n"
            for caveat in record.caveats:
                output += f"  - {caveat}\n"

        if record.derived_from:
            output += "\nDERIVED FROM:\n"
            for source in record.derived_from:
                output += f"  - {source.metadata.source_name} ({source.metadata.source_type})\n"

        return output

# Example usage
if __name__ == "__main__":
    # Direct extraction from document
    customer_verified = ProvenanceTracker.create_record(
        content={"customer_id": "cust_123", "verified": True, "verified_at": "2026-03-20T10:00:00"},
        source_type="document",
        source_url="https://company.internal/customers/cust_123",
        source_name="Customer Verification Document",
        confidence=0.99
    )

    # Derived record: synthesized from multiple sources
    refund_eligible = ProvenanceTracker.create_record(
        content={"eligible": True, "reason": "Within 30-day refund window"},
        source_type="derived",
        confidence=0.95,
        caveats=[
            "Assumes current date is 2026-03-20",
            "Refund window may be different for this product category"
        ],
        derived_from=[customer_verified]
    )

    print(ProvenanceTracker.format_for_human_review(refund_eligible))
```

#### 2. Prompts That Instruct Explicit Uncertainty

```python
class UncertaintyExplicitPrompt:
    """Prompts that instruct models to express uncertainty."""

    @staticmethod
    def system_prompt() -> str:
        return """You are a careful analyst. When you don't have information or are uncertain:

DO NOT make up plausible-sounding details.
DO explicitly state what you don't know or are uncertain about.

Format your analysis as:

VERIFIED FACTS:
- [Things confirmed by sources]

REASONABLE INFERENCES:
- [Things inferred but not directly stated, with confidence level]

UNKNOWN/UNCERTAIN:
- [Things you don't have data for, with explanation of why they matter]

Always separate what you know from what you're guessing.
Never present uncertain information as fact.
"""

    @staticmethod
    def extraction_task() -> str:
        return """Extract customer information from the document.

For each piece of information, indicate:
1. Is it explicitly stated? (yes/no)
2. If inferred, explain the inference
3. If unknown, explain what would be needed to determine it

Example:
- Last purchase date: 2026-03-15 (explicitly stated in order history)
- Satisfaction level: Likely high (inferred from 4.8/5 review, but not directly measured)
- Account lifetime value: Unknown (not shown in this document)
"""

    @staticmethod
    def verification_task() -> str:
        return """You are reviewing an extracted fact for accuracy.

Fact: {fact}
Source: {source}

Provide:
1. Confidence in the fact (0-100%)
2. What assumption s might be wrong
3. What additional verification would be valuable

Don't just agree or disagree. Explain your reasoning.
"""

# Example usage with explicit uncertainty
if __name__ == "__main__":
    analysis = """
VERIFIED FACTS:
- Customer account created: 2025-06-01 (directly from account table)
- Last payment processed: 2026-03-15 (confirmed in payment ledger)
- Current balance: $0 (shown in account dashboard)

REASONABLE INFERENCES (confidence noted):
- Customer likely satisfied with service (~75% confident):
  Reasoning: No support tickets in last 90 days, active usage patterns

- Customer will continue to be active (~60% confident):
  Reasoning: Consistent monthly usage, but no explicit retention commitment

UNKNOWN/UNCERTAIN:
- Exact reasons for account creation:
  Why it matters: Might indicate product fit
  How to find out: Survey customer or analyze usage patterns

- Customer's future willingness to upgrade to premium:
  Why it matters: Affects upsell strategy
  How to find out: Direct question to customer, A/B test offer
"""

    print(analysis)
```

#### 3. Verification Against Original Documents

```python
@dataclass
class VerificationResult:
    claim: str
    claimed_source: str
    verification_status: str  # "verified", "contradicted", "not_found", "uncertain"
    evidence: str
    confidence: float

class DocumentVerifier:
    """Verify extracted claims against original documents."""

    def __init__(self, documents: dict):
        """documents: {source_name: document_content}"""
        self.documents = documents

    def verify_claim(self, claim: str, claimed_source: str) -> VerificationResult:
        """
        Check if claim appears in the claimed source document.
        """
        if claimed_source not in self.documents:
            return VerificationResult(
                claim=claim,
                claimed_source=claimed_source,
                verification_status="not_found",
                evidence=f"Source document '{claimed_source}' not available",
                confidence=0.0
            )

        document = self.documents[claimed_source]

        # Simulate searching document
        if claim.lower() in document.lower():
            return VerificationResult(
                claim=claim,
                claimed_source=claimed_source,
                verification_status="verified",
                evidence=f"Claim found in {claimed_source}",
                confidence=0.95
            )
        elif any(word in document.lower() for word in claim.lower().split()):
            return VerificationResult(
                claim=claim,
                claimed_source=claimed_source,
                verification_status="uncertain",
                evidence=f"Partial match in {claimed_source}; full claim not found",
                confidence=0.50
            )
        else:
            return VerificationResult(
                claim=claim,
                claimed_source=claimed_source,
                verification_status="not_found",
                evidence=f"Claim not found in {claimed_source}",
                confidence=0.0
            )

    def cross_reference_claims(self, claims: list[tuple[str, str]]) -> list[VerificationResult]:
        """Verify multiple claims."""
        return [self.verify_claim(claim, source) for claim, source in claims]

# Example usage
if __name__ == "__main__":
    documents = {
        "order_confirmation.pdf": "Order #123 placed on March 15, 2026. Customer name: John Smith. Total: $100.",
        "shipping_label.txt": "Tracking: ABC123. Shipped March 16, 2026. Destination: 123 Main St."
    }

    verifier = DocumentVerifier(documents)

    claims_to_verify = [
        ("Order placed on March 15, 2026", "order_confirmation.pdf"),
        ("Total order value was $100", "order_confirmation.pdf"),
        ("Shipped via FedEx", "shipping_label.txt"),
        ("Order was expedited", "order_confirmation.pdf")
    ]

    results = verifier.cross_reference_claims(claims_to_verify)

    for result in results:
        print(f"{result.claim}")
        print(f"  Status: {result.verification_status} (confidence: {result.confidence:.0%})")
        print(f"  Evidence: {result.evidence}\n")
```

---

## Quick Reference Cheatsheet

### Context Management
| Concept | Key Points |
|---------|-----------|
| **PostToolUse Hooks** | Normalize timestamps, filter PII, add metadata BEFORE model sees tool output |
| **Context Checkpointing** | Create summaries at decision points to replace verbose history |
| **Message Pruning** | Keep recent messages + decision-relevant ones; discard exploratory reasoning |
| **Windowing** | Maintain last N turns + summary, discard intermediate steps |

### Escalation
| Trigger | Action |
|---------|--------|
| **Ambiguous request** | Ask clarifying questions BEFORE attempting action |
| **Low confidence** | Escalate or ask clarifying questions; don't guess |
| **High-impact action** | Require manager/human approval |
| **Exceeded authorization** | Always escalate (e.g., refund > $500) |
| **Error recovery impossible** | Propagate to coordinator with structured metadata |

### Error Handling
| Pattern | Use When |
|---------|----------|
| **Try-catch with retry** | Transient errors (timeouts, rate limits) |
| **Fallback to cached data** | Service temporarily unavailable |
| **Graceful degradation** | Continue with partial results |
| **Circuit breaker** | Service repeatedly failing; prevent cascading |

### Code Exploration
| Step | Tools/Approach |
|------|----------------|
| 1. Find entry points | Grep for `main()`, `__init__`, API routes |
| 2. Trace imports | Read key files, follow dependency chain |
| 3. Find usage | Grep for function names across codebase |
| 4. Understand flows | Read specific function definitions |
| 5. Use Explore subagent | For verbose discovery work |

### Human Review
| Strategy | When to Use |
|----------|------------|
| **Confidence reporting** | Every finding; enables prioritization |
| **Independent review** | High-impact or low-confidence decisions |
| **Review queues** | Route to right person by role and priority |
| **Approval gates** | Irreversible actions (deletions, refunds > $X) |

### Provenance & Uncertainty
| Concept | Implementation |
|---------|-----------------|
| **Source metadata** | Separate content from URL, page#, timestamp |
| **Explicit uncertainty** | State what's verified vs. inferred vs. unknown |
| **Verification** | Cross-reference claims against original documents |
| **Derived records** | Track which sources contributed to derived facts |

---

## Common Exam Traps

### Trap 1: "I'll Just Read All the Files Upfront"
**Wrong:** Reading a 500-file codebase exhausts context window
**Right:** Grep for entry points → Read key files → Trace imports incrementally

**Exam question:** "You need to understand a large codebase's authentication flow. What's the most context-efficient approach?"
**Answer:** Start with grep for `validate_token()`, read that file, grep for its callers, then read those files.

### Trap 2: "Self-Review Will Catch the Errors"
**Wrong:** Model reviewing its own reasoning in same session won't catch errors
**Right:** Use independent Claude instance (different session, no context) for review

**Exam question:** "Your agent made a decision. How do you verify it?"
**Answer:** Spin up independent review session with findings but not original reasoning.

### Trap 3: "High Confidence Means No Escalation"
**Wrong:** Even high-confidence decisions might need escalation if impact is high and action is irreversible
**Right:** Consider both confidence AND impact AND reversibility

**Exam question:** "Your agent is 90% confident the account should be deleted. Should it proceed?"
**Answer:** No—account deletion is irreversible. Even 90% confidence requires human approval.

### Trap 4: "Normalize After the Model Processes Tool Results"
**Wrong:** PostToolUse hooks run AFTER the model sees the output; doesn't help context
**Right:** PostToolUse hooks normalize BEFORE the model processes results

**Exam question:** "Where should you normalize timestamps from different tools?"
**Answer:** PostToolUse hooks, before the model's reasoning sees them.

### Trap 5: "Escalate Without Handoff Context"
**Wrong:** Handing off to human without customer ID, root cause, previous attempts
**Right:** Structured handoff includes complete summary; human doesn't have transcript

**Exam question:** "You're escalating a refund request to a human agent. What must be included?"
**Answer:** Customer ID, issue description, root cause, attempted solutions, confidence level, recommended action.

### Trap 6: "One Subagent Failure = System Failure"
**Wrong:** If a subagent fails, the entire multi-agent system crashes
**Right:** Design error isolation; continue with partial results

**Exam question:** "Subagent A fails to get customer orders. Should the coordinator abort?"
**Answer:** No—if Subagent B (customer verification) succeeded, continue with partial results.

### Trap 7: "Just Tell Them the Answer"
**Wrong:** "The answer is 42" (no indication of uncertainty)
**Right:** "The answer is 42 (85% confident) based on X; uncertain about Y"

**Exam question:** "Your agent extracted a customer's VIP status from a document. How should it report this?"
**Answer:** Include confidence level, source document, and any caveats about data completeness.

---

## Code Examples

See the detailed code examples integrated throughout the six task sections above. Key patterns include:

1. **PostToolUse Hooks** (Task 5.1): Normalize timestamps, filter PII, add metadata
2. **Context Management** (Task 5.1): Message pruning, checkpointing, history management
3. **Escalation Logic** (Task 5.2): Prerequisites enforcement, multi-concern decomposition, handoff generation
4. **Error Handling** (Task 5.3): Retry logic with classification, structured error propagation, circuit breakers
5. **Code Exploration** (Task 5.4): Incremental understanding, entry point discovery, function tracing
6. **Confidence Calibration** (Task 5.5): Self-reporting, review queues, independent review
7. **Provenance Tracking** (Task 5.6): Source metadata, explicit uncertainty, document verification

All examples are in Python and demonstrate exam-relevant patterns.

---

## Exam Strategy

### Time Management
- Domain 5 is **15% of exam** (11 questions)
- Allocate roughly 18-20 minutes (assuming 2-2.5 min/question)
- Context management questions will likely be scenario-based

### Question Types to Expect
1. **Scenario:** "Agent encounters ambiguous request - what should it do?" → Escalation decision
2. **Best practice:** "How to manage long conversations?" → Checkpointing, pruning
3. **Error handling:** "Subagent fails - coordinator action?" → Graceful degradation
4. **Multi-agent:** "How to track information across agents?" → Provenance
5. **Review process:** "Verify agent decision - approach?" → Independent review, confidence

### Study Tips
- Practice writing escalation logic and error handling code
- Memorize the 6 task statements; questions will map to them
- Understand the difference between local recovery and escalation
- Know when to use independent review vs. self-review
- Remember: Context window is always a constraint

---

**Last Updated:** March 2026
**For Exam:** Claude Certified Architect – Foundations
