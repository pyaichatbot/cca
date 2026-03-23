# Exercise 1: Multi-Tool Customer Support Agent with Escalation Logic
## CCA Exam Study Companion

This exercise implements a production-grade **customer support agent** that demonstrates core patterns from **Domain 1 (Agentic Architecture)**, **Domain 2 (Tool Design & MCP Integration)**, and **Domain 5 (Context Management & Reliability)**.

---

## PART 1: EXAM DOMAIN MAPPING

### Table 1: Code Section → Exam Domain/Task Mapping

| **Code Lines** | **Component** | **Domain** | **Exam Tasks** | **Relevant Q#s** | **Key Concept** |
|---|---|---|---|---|---|
| 23-101 | `TOOLS` list + definitions | Domain 2 | 2.1, 2.2 | Q2, Q30-Q31 | Tool schema design, required parameters |
| 23-37 | `get_customer` tool definition | Domain 2 | 2.1 | Q30 | Prerequisite validation, tool entry point |
| 39-55 | `lookup_order` tool definition | Domain 2 | 2.1, 2.5 | Q30, Q40 | Tool dependencies, input validation |
| 57-77 | `process_refund` tool definition | Domain 2 | 2.1, 2.2 | Q30-Q31 | Multi-parameter tool, complex schema |
| 79-101 | `escalate_to_human` tool definition | Domain 2 | 2.1 | Q30 | Enum-based parameters, tool metadata |
| 107-139 | `get_customer()` implementation | Domain 2, 5 | 2.3, 5.2 | Q32-Q33, Q70 | Error response format, mock implementation |
| 140-182 | `lookup_order()` implementation | Domain 2, 5 | 2.3, 5.2 | Q32-Q33, Q70 | Structured error responses, NOT_FOUND |
| 183-207 | `process_refund()` implementation | Domain 2, 5 | 2.3, 5.2 | Q32-Q33, Q70 | Business logic, prerequisite checks |
| 208-222 | `escalate_to_human()` implementation | Domain 2 | 2.3 | Q32 | Side effects, human handoff logic |
| 227-256 | ToolExecutor.__init__ & execute() prerequisites | Domain 1, 2 | 1.1, 2.2, 2.4 | Q1, Q31, Q37 | **Prerequisite gating** - CORE PATTERN |
| 240-255 | Prerequisite validation logic | Domain 1, 2 | 1.1, 2.4 | Q1, Q37 | Error routing, PREREQUISITE_NOT_MET |
| 257-286 | Tool execution + tracking | Domain 1, 2 | 1.2, 2.3 | Q7, Q32 | Tool invocation, state tracking |
| 287-304 | PostToolUse normalization | Domain 5, 2 | 5.3, 2.5 | Q69-Q70, Q40 | **Response normalization** - CORE PATTERN |
| 309-360 | `run_agent()` - Main agentic loop | Domain 1 | 1.1-1.7 | Q1, Q7-Q9, Q13-Q29 | **THE AGENTIC LOOP** - FOUNDATIONAL |
| 345-360 | While loop + iteration control | Domain 1 | 1.1, 1.3 | Q1, Q13-Q15 | Loop termination, max_iterations safety |
| 353-360 | client.messages.create() call | Domain 1 | 1.2 | Q7 | API interaction, tool parameter |
| 361-368 | Stop reason checking | Domain 1 | 1.1, 1.4 | Q1, Q16-Q18 | **stop_reason == "tool_use"** decision point |
| 371-393 | Tool use block processing | Domain 1 | 1.5 | Q19-Q21 | Tool extraction, result wrapping |
| 383-393 | Tool result message assembly | Domain 1 | 1.6 | Q22-Q24 | Message format, role="user" for results |
| 395-410 | end_user_message handling | Domain 1 | 1.7 | Q25-Q29 | Final response extraction, loop termination |
| 421-447 | Test scenarios - multi-concern | Domain 1 | 1.6, 1.7 | Q25-Q29 | Real-world complexity, edge cases |

---

## PART 2: 10 PRACTICE EXAM QUESTIONS (WITH ANSWERS)

### **QUESTION 1: Agentic Loop Termination**
**Difficulty:** Medium | **Domain:** 1.4 | **Related Code:** Lines 395-410

In the `run_agent()` function, what indicates that the agent has completed its task and should return a final response to the user?

A) When `response.stop_reason == "tool_use"` and the agent has called at least one tool
B) When `response.stop_reason == "end_user_message"` and the agent has finished reasoning
C) When `iteration >= max_iterations` regardless of stop_reason
D) When all tools in the `TOOLS` list have been executed

**Correct Answer:** B

**Detailed Explanation:**
The agentic loop operates as follows:
- When `stop_reason == "tool_use"`: The agent wants to call tools. Extract tool calls from `response.content`, execute them, add results to `messages`, and continue the loop.
- When `stop_reason == "end_user_message"`: The agent has completed reasoning and generated a natural language response. Extract the final text from the response blocks and return it.
- The code (lines 395-410) explicitly checks: `elif response.stop_reason == "end_user_message": ... return final_response`
- The `max_iterations` limit (line 346) is a **safety mechanism** to prevent infinite loops, not a normal termination condition.

**Why this matters (Exam relevance):** Understanding `stop_reason` is fundamental to Domain 1. The exam will test your ability to distinguish between different stop reasons and handle them appropriately. This pattern appears in Q7-Q9, Q16-Q18.

---

### **QUESTION 2: Prerequisite Gating Error Handling**
**Difficulty:** Hard | **Domain:** 2.4 | **Related Code:** Lines 240-255

A user requests a refund for order ORD-101, but in the same conversation, the agent has not yet called `get_customer`. What will happen when the agent attempts to call `process_refund`?

A) The `process_refund()` function will execute successfully because the mock implementation doesn't validate prerequisites
B) The ToolExecutor will return a PREREQUISITE_NOT_MET error and the agent will receive guidance to call `get_customer` first
C) The request will be silently dropped and the agent will move to the next tool
D) The agent will retry the same tool up to 3 times before giving up

**Correct Answer:** B

**Detailed Explanation:**
The ToolExecutor class maintains an `executed_tools` dictionary (line 231) to track which tools have been successfully called. Before executing any tool, the `execute()` method checks its prerequisites:

```python
prerequisites = {
    "lookup_order": ["get_customer"],
    "process_refund": ["get_customer", "lookup_order"],  # Requires BOTH!
}

required_tools = prerequisites.get(tool_name, [])
for required_tool in required_tools:
    if required_tool not in self.executed_tools:
        return json.dumps({
            "success": False,
            "errorCategory": "PREREQUISITE_NOT_MET",
            "isRetryable": True,  # Important: isRetryable=True
            "message": f"Tool '{tool_name}' requires '{required_tool}' to be called first",
            "suggestedNextStep": f"Call {required_tool} first with customer_id"
        })
```

Notice the `isRetryable: True` flag. This tells Claude that it can retry after calling the missing prerequisite. The `suggestedNextStep` provides explicit guidance, enabling the agent to self-correct.

**Why this matters (Exam relevance):** Domain 2.4 and 2.5 test error handling and tool sequencing. The exam will ask how to enforce data dependencies and what error information should be returned. The combination of `errorCategory + isRetryable + suggestedNextStep` is the CCA's recommended error pattern.

---

### **QUESTION 3: PostToolUse Normalization and Response Schema**
**Difficulty:** Medium | **Domain:** 5.3 | **Related Code:** Lines 287-304

Why does the code normalize tool responses using the `_normalize_response()` method before adding them to the messages?

A) To reduce the token count of the message history
B) To ensure all tool responses have a consistent schema that the agent can reliably interpret
C) To encrypt sensitive customer data
D) To improve the performance of subsequent API calls

**Correct Answer:** B

**Detailed Explanation:**
The `_normalize_response()` method (lines 287-304) transforms raw tool outputs into a standard format:

**Input (raw success):**
```python
{
    "success": True,
    "data": {...}
}
```

**Output (normalized):**
```python
{
    "status": "success",
    "data": {...},
    "timestamp": "2024-03-22T11:30:00Z"
}
```

**Input (raw error):**
```python
{
    "success": False,
    "errorCategory": "NOT_FOUND",
    "isRetryable": False,
    "message": "..."
}
```

**Output (normalized):**
```python
{
    "status": "error",
    "errorCategory": "NOT_FOUND",
    "isRetryable": False,
    "message": "...",
    "suggestedNextStep": None,
    "timestamp": "..."
}
```

This is critical because real-world tools return wildly different schemas (database APIs, REST endpoints, legacy systems). By normalizing, the agent always sees the same structure and can reason more reliably. Without this, the agent would hallucinate or misinterpret responses.

**Why this matters (Exam relevance):** Domain 5 (Context Management, 15% of exam) explicitly covers "PostToolUse hooks" and response normalization. This is a production pattern that prevents hallucinations and improves agentic reasoning. Questions Q69-Q70 test this directly.

---

### **QUESTION 4: Tool Definition and Input Schema**
**Difficulty:** Medium | **Domain:** 2.1 | **Related Code:** Lines 39-55

Looking at the `lookup_order` tool definition, what is the purpose of the "required" field in the input_schema?

A) It restricts who can call the tool (requires authentication)
B) It specifies which input parameters must be provided by the caller
C) It marks the tool as required for all customer requests
D) It indicates the tool is dependent on another tool being called first

**Correct Answer:** B

**Detailed Explanation:**
In the tool schema (lines 39-55):
```python
{
    "name": "lookup_order",
    "description": "...",
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_id": {...},
            "order_id": {...}
        },
        "required": ["customer_id", "order_id"]  # BOTH must be provided
    }
}
```

The `required` array tells Claude which parameters are mandatory. If the agent tries to call `lookup_order` without providing `order_id`, the API will reject the call. This is schema-level validation.

Importantly: **Tool definition specifies what inputs Claude MUST provide. Prerequisite gating in ToolExecutor specifies what tools Claude must call in sequence.** These are complementary but different concepts:
- **Schema validation** (input_schema): "Does the function call have all required parameters?"
- **Prerequisite gating** (executed_tools check): "Has the agent already called prerequisite tools?"

**Why this matters (Exam relevance):** Domain 2.1-2.2 test tool design. Questions Q30-Q31 will ask how to define tools properly and what should be in the schema.

---

### **QUESTION 5: Multi-Concern Request Handling**
**Difficulty:** Hard | **Domain:** 1.6 | **Related Code:** Lines 435-438

In Scenario 2, the user says: "I have two issues: (1) I haven't received my order ORD-102 yet, and (2) I want to return ORD-101 because it's defective."

How does the agent handle both concerns in a single request without needing to be prompted separately?

A) The agent calls all four tools in sequence, then provides a combined response
B) The agent's system prompt instructs it to address multiple concerns, and the agentic loop continues for multiple iterations with each tool call adding context
C) The system force-calls all tools and combines results
D) The agent can only handle one concern per request and would need a second user message

**Correct Answer:** B

**Detailed Explanation:**
The multi-concern handling works through the **agentic loop's message accumulation** (Domain 1):

1. **Iteration 1:** Agent receives: `"[Customer ID: CUST-001]\n\nI have two issues: (1) I haven't received my order ORD-102 yet, and (2) I want to return ORD-101 because it's defective."`
   - Agent decides: "I need customer info first"
   - Calls: `get_customer(CUST-001)`
   - Stop reason: `tool_use`

2. **Iteration 2:** Messages now include:
   - User's original message
   - Assistant's tool call to get_customer
   - Tool result (customer data)
   - Agent reads full context and reasons: "Now check order ORD-102"
   - Calls: `lookup_order(CUST-001, ORD-102)`

3. **Iteration 3:** Agent sees ORD-102 is in_transit, then decides to check ORD-101
   - Calls: `lookup_order(CUST-001, ORD-101)`

4. **Iteration 4:** Agent sees ORD-101 is delivered but defective, initiates refund
   - Calls: `process_refund(CUST-001, ORD-101, "defective")`

5. **Iteration 5:** Agent reads all context and decides ORD-102 needs human support
   - Calls: `escalate_to_human(CUST-001, "Order ORD-102 not received", "high")`

6. **Iteration 6:** Agent has resolved both concerns and responds
   - Stop reason: `end_user_message`
   - Returns final response summarizing both resolutions

The key insight: **Each tool result adds context to the messages. The agent reads the full message history to decide which tool to call next.** This is why the system prompt (lines 332-343) is crucial: it guides the agent's reasoning across multiple iterations.

**Why this matters (Exam relevance):** Domain 1 (27% of exam) emphasizes that agents think sequentially but handle complex problems. Q7-Q9, Q25-Q29 test your understanding of multi-turn, multi-concern scenarios.

---

### **QUESTION 6: Error Categories and Retry Logic**
**Difficulty:** Medium | **Domain:** 2.2, 2.5 | **Related Code:** Lines 249-255, 287-304

When a tool execution fails, why is the distinction between `"isRetryable": True` and `"isRetryable": False` important?

A) It affects how quickly the API responds to the next request
B) It tells the agent whether it should retry the same tool or pivot to a different strategy
C) It determines whether an error is logged to the system
D) It is only relevant for tools that modify data (refunds)

**Correct Answer:** B

**Detailed Explanation:**
The `isRetryable` flag guides the agent's decision-making:

**Retryable errors (isRetryable: True):**
```python
# PREREQUISITE_NOT_MET
{
    "errorCategory": "PREREQUISITE_NOT_MET",
    "isRetryable": True,  # Agent should call the missing prerequisite!
    "suggestedNextStep": "Call get_customer first with customer_id"
}
```
When the agent sees `isRetryable: True`, it knows the problem is fixable by taking a suggested action.

**Non-retryable errors (isRetryable: False):**
```python
# NOT_FOUND
{
    "errorCategory": "NOT_FOUND",
    "isRetryable": False,  # Calling again won't help; customer doesn't exist
    "message": "Customer CUST-999 not found"
}
```
When the agent sees `isRetryable: False`, it knows calling the same tool again is futile and must pivot to a different strategy (e.g., inform the user to verify their ID).

**Example from the code (lines 249-255):**
```python
if required_tool not in self.executed_tools:
    return json.dumps({
        "errorCategory": "PREREQUISITE_NOT_MET",
        "isRetryable": True,  # ← Agent will call prerequisite
        "suggestedNextStep": f"Call {required_tool} first"
    })
```

vs. **Example from get_customer (lines 133-138):**
```python
return {
    "success": False,
    "errorCategory": "NOT_FOUND",
    "isRetryable": False,  # ← Agent will NOT retry; will ask user to verify ID
    "message": f"Customer {customer_id} not found"
}
```

**Why this matters (Exam relevance):** Domain 2 and 5 test error design. The exam will ask how to structure error responses so the agent can make intelligent recovery decisions. This pattern prevents infinite retry loops and enables graceful degradation.

---

### **QUESTION 7: The Role of Tool Tracking (executed_tools)**
**Difficulty:** Medium | **Domain:** 1.2 | **Related Code:** Lines 231, 278

What is the purpose of the `self.executed_tools` dictionary in the ToolExecutor class?

A) To prevent the same tool from being called twice in succession
B) To enable prerequisite validation by tracking which tools have been successfully called
C) To log all tool execution for audit purposes
D) To cache tool results so repeated calls are faster

**Correct Answer:** B

**Detailed Explanation:**
The `executed_tools` dictionary is initialized (line 231):
```python
def __init__(self):
    self.executed_tools = {}  # Track which tools have been executed
```

And updated after each successful execution (line 278):
```python
# Track executed tool
self.executed_tools[tool_name] = tool_input
```

This tracking enables the prerequisite check (lines 246-255):
```python
required_tools = prerequisites.get(tool_name, [])
for required_tool in required_tools:
    if required_tool not in self.executed_tools:  # ← Check against history
        return PREREQUISITE_NOT_MET_ERROR
```

**Example flow:**
1. Agent calls `process_refund(CUST-001, ORD-101, "defective")`
2. ToolExecutor checks: Is "get_customer" in executed_tools? No.
3. ToolExecutor checks: Is "lookup_order" in executed_tools? No.
4. Returns PREREQUISITE_NOT_MET error
5. Agent calls `get_customer(CUST-001)` first
6. Now "get_customer" is added to executed_tools
7. Agent calls `lookup_order(CUST-001, ORD-101)`
8. Now both "get_customer" and "lookup_order" are in executed_tools
9. Agent calls `process_refund` again → prerequisite check passes!

**Why this matters (Exam relevance):** Domain 1 (Agentic Architecture) requires understanding state management. The exam will ask how to enforce data dependencies and track agent progress. This pattern is foundational to multi-step agents.

---

### **QUESTION 8: Message Format for Tool Results**
**Difficulty:** Medium | **Domain:** 1.5 | **Related Code:** Lines 383-393

In the agentic loop, after executing a tool, how are the results added back to the messages?

A) They are added as `{"role": "assistant", "content": tool_result_json}`
B) They are added as `{"role": "user", "content": [{"type": "tool_result", "tool_use_id": "...", "content": "..."}]}`
C) They are prepended to the system prompt
D) They replace the previous assistant message

**Correct Answer:** B

**Detailed Explanation:**
The code (lines 383-393) shows:
```python
tool_results = []
for block in response.content:
    if block.type == "tool_use":
        tool_name = block.name
        tool_input = block.input
        tool_use_id = block.id  # ← Critical: matches the tool call

        result = tool_executor.execute(tool_name, tool_input)

        tool_results.append({
            "type": "tool_result",
            "tool_use_id": tool_use_id,  # ← Links result to tool call
            "content": result
        })

# Add tool results to messages
messages.append({
    "role": "user",  # ← IMPORTANT: role is "user", not "assistant"
    "content": tool_results
})
```

This might seem counterintuitive: **why is the role "user" for tool results?** Because in Claude's message protocol, tool results are always sent from the "user" role. The flow is:
1. **Assistant** calls tools (says "I want to use X tool with inputs Y")
2. **User** provides tool results (says "Here's what the tool returned")
3. **Assistant** reads results and decides next step

**Why this matters (Exam relevance):** Domain 1 (Message protocol and agentic loops) requires precise understanding of message formatting. The exam will include questions about message roles and content structure. Getting this wrong breaks the entire agent.

---

### **QUESTION 9: System Prompt Role in Multi-Concern Handling**
**Difficulty:** Hard | **Domain:** 1.2 | **Related Code:** Lines 332-343

The system prompt includes the guideline: "Handle multiple concerns in a single request (e.g., 'I have two issues')". How does this guideline enable the agent to resolve multiple concerns without explicit user intervention?

A) It hard-codes the agent to always call all four tools in order
B) It instructs Claude to sequence tool calls intelligently based on dependencies and concerns in the user's message
C) It prevents the agent from responding until all possible tools are called
D) It is ignored by Claude; the agentic loop naturally handles multiple concerns

**Correct Answer:** B

**Detailed Explanation:**
The system prompt (lines 332-343) serves as the agent's reasoning guide:
```python
system_prompt = """You are a customer support agent. Your goal is to resolve customer issues...

Guidelines:
1. Always start by calling get_customer to verify and load the customer profile
2. For order-related issues, call lookup_order to understand the situation
3. For refund requests, call process_refund with appropriate reasons
4. If an issue is complex or beyond your authority, escalate_to_human
5. If a tool call fails due to PREREQUISITE_NOT_MET, acknowledge and call the prerequisite tool
6. Provide clear, customer-friendly responses
7. Handle multiple concerns in a single request (e.g., "I have two issues")
```

When the user says "I have two issues: (1) order not arrived, (2) defective item", Claude reads this input and the system prompt together. It reasons:
- "The user has two concerns"
- "I need to check the status of issue 1 (order status)"
- "I need to process a refund for issue 2"
- "Both require starting with get_customer"
- "Then I'll call lookup_order for each order"
- "Then I'll process_refund for the defective item"
- "For the missing order, I should escalate since I can't control shipping"

The system prompt gives Claude the **strategy**, and the agentic loop provides the **mechanism** (multiple iterations, tool accumulation, full message history context).

**Why this matters (Exam relevance):** Domain 1 emphasizes that agent behavior is driven by system prompts + API interactions. The exam will test your understanding of how to craft prompts that guide multi-step reasoning. Q7-Q9 cover this.

---

### **QUESTION 10: Error Recovery and Suggested Next Steps**
**Difficulty:** Hard | **Domain:** 2.4 | **Related Code:** Lines 249-255

A developer creates a tool error response with `"errorCategory": "PREREQUISITE_NOT_MET"`, `"isRetryable": True`, but forgets to include `"suggestedNextStep"`. What happens?

A) Claude will deterministically fail and refuse to continue
B) Claude may struggle to figure out which prerequisite to call next, reducing agent effectiveness
C) The error will be silently ignored
D) The system will automatically call the prerequisite tool

**Correct Answer:** B

**Detailed Explanation:**
The normalized error response (lines 249-255) includes:
```python
return json.dumps({
    "success": False,
    "errorCategory": "PREREQUISITE_NOT_MET",
    "isRetryable": True,
    "message": f"Tool '{tool_name}' requires '{required_tool}' to be called first",
    "suggestedNextStep": f"Call {required_tool} first with customer_id"  # ← Guidance
})
```

The `suggestedNextStep` field is **not technically required** by the API, but it's critical for agent effectiveness:

**With `suggestedNextStep`:**
- Claude reads: "Call get_customer first with customer_id"
- Claude knows exactly what to do
- Next iteration: agent calls `get_customer` → continues smoothly

**Without `suggestedNextStep`:**
- Claude reads: "Tool 'process_refund' requires 'get_customer' to be called first"
- Claude must infer which parameter to use
- Claude might guess correctly or might hallucinate
- Agent effectiveness decreases
- In some cases, agent might get stuck in confusion loop

This is why Domain 2 (Tool Design) and Domain 5 (Context Management) emphasize that **errors are opportunities to guide the agent**. A well-designed error response includes:
1. `errorCategory` (what went wrong?)
2. `isRetryable` (should I try again?)
3. `message` (why did it fail?)
4. `suggestedNextStep` (what should I do next?)

**Why this matters (Exam relevance):** Domain 2 and 5 (combined 33% of exam) test error design patterns. The certification emphasizes that **every error should either guide the agent to resolution or inform the user clearly**. Omitting guidance information is a common mistake that reduces agent reliability.

---

## PART 3: CODE WALKTHROUGH - THE AGENTIC LOOP STEP-BY-STEP

### **The Agentic Loop Visualization**

```
┌─────────────────────────────────────────────────────────────────┐
│ START: run_agent(user_request, customer_id)                    │
├─────────────────────────────────────────────────────────────────┤
│ 1. Initialize:                                                  │
│    - Create ToolExecutor (empty executed_tools dict)           │
│    - Create messages list with user's initial request          │
│    - iteration = 0                                              │
└────────────────┬────────────────────────────────────────────────┘
                 │
    ┌────────────▼────────────────────────────────────┐
    │ LOOP: while iteration < max_iterations (10)    │
    │ iteration += 1                                 │
    └────────────┬─────────────────────────────────┬─┘
                 │                                 │
       ┌─────────▼─────────┐         ┌─────────────▼──────────┐
       │ 2. Call API:      │         │ 6. Check iteration:    │
       │ messages.create() │         │ if iteration >= 10 → BREAK
       │ with tools=TOOLS  │         │                        │
       │                   │         │ (safety limit)         │
       └────────┬──────────┘         └────────────────────────┘
                │
       ┌────────▼──────────────────────────┐
       │ 3. Append assistant message:      │
       │    {"role": "assistant",          │
       │     "content": response.content}  │
       └────────┬───────────────────────┬──┘
                │                       │
    ┌───────────▼──────────┐  ┌────────▼──────────────┐
    │ 4a. TOOL_USE:        │  │ 4b. END_USER_MESSAGE:│
    │                      │  │                      │
    │ Extract tool_use     │  │ Extract text from    │
    │ blocks from response │  │ response.content     │
    │ .content             │  │                      │
    │                      │  │ Final response found!│
    └────────┬─────────────┘  └────────┬─────────────┘
             │                         │
       ┌─────▼──────────────┐   ┌──────▼─────────────┐
       │ For each tool_use: │   │ 5b. RETURN:        │
       │ - Get tool_name    │   │ print final_text   │
       │ - Get tool_input   │   │ return             │
       │ - Get tool_use_id  │   │ (exit loop)        │
       │                    │   │                    │
       │ Execute via        │   └────────────────────┘
       │ ToolExecutor:      │
       │ - Check prereqs    │
       │ - Run mock tool    │
       │ - Normalize result │
       │                    │
       │ Wrap in tool_result│
       │ with tool_use_id   │
       │                    │
       │ Append as {"role": │
       │  "user", "content":│
       │  [tool_results]}   │
       │                    │
       │ Loop continues ↑   │
       └────────────────────┘
```

### **Detailed Step-by-Step Example**

**Scenario:** User requests refund for order ORD-101 (customer CUST-001)

**ITERATION 1:**
```
Input messages:
[
  {"role": "user", "content": "[Customer ID: CUST-001]\n\nI want to return order ORD-101 because the stand doesn't fit my desk."}
]

API Call:
client.messages.create(
  model="claude-3-5-sonnet-20241022",
  max_tokens=1024,
  system="You are a customer support agent...",
  tools=TOOLS,  # 4 tools available
  messages=messages
)

Claude's Internal Reasoning:
- Sees: Customer wants to return an order
- Sees: Customer ID is CUST-001
- Sees: Order ID is ORD-101
- Thinks: "I need to check if this customer exists before I can process a refund"
- Decides: "I'll call get_customer first"
- Generates: tool_use block for get_customer

API Response:
{
  "stop_reason": "tool_use",
  "content": [
    {
      "type": "tool_use",
      "id": "tool_use_abc123",
      "name": "get_customer",
      "input": {"customer_id": "CUST-001"}
    }
  ]
}

Agentic Loop Processing:
- Check: response.stop_reason == "tool_use"? YES
- Extract tool block: name="get_customer", input={"customer_id": "CUST-001"}, id="tool_use_abc123"
- Call: ToolExecutor.execute("get_customer", {"customer_id": "CUST-001"})
  * Prerequisite check: get_customer has no prerequisites ✓
  * Call mock: get_customer("CUST-001")
  * Return: {"success": True, "data": {"id": "CUST-001", "name": "Alice Johnson", ...}}
  * Normalize: {"status": "success", "data": {...}, "timestamp": "..."}
  * Track: executed_tools["get_customer"] = {"customer_id": "CUST-001"}
  * Result: JSON string
- Wrap in tool_result: {"type": "tool_result", "tool_use_id": "tool_use_abc123", "content": "..."}
- Append to messages:
  {
    "role": "user",
    "content": [
      {"type": "tool_result", "tool_use_id": "tool_use_abc123", "content": "{\"status\": \"success\", \"data\": {...}}"}
    ]
  }

Updated messages:
[
  {"role": "user", "content": "[Customer ID: CUST-001]\n\nI want to return order ORD-101..."},
  {"role": "assistant", "content": [{"type": "tool_use", ...}]},
  {"role": "user", "content": [{"type": "tool_result", ...}]}
]

Continue to ITERATION 2
```

**ITERATION 2:**
```
Input messages:
[messages from iteration 1 + new tool_result]

API Call (Claude now reads full context):
Claude reads:
- "Customer wants to return order ORD-101"
- "Customer is CUST-001 (Alice Johnson)"
- "I successfully retrieved customer data"
- Thinks: "Now I need to check if the order exists and what its status is"
- Decides: "I'll call lookup_order for ORD-101"

API Response:
{
  "stop_reason": "tool_use",
  "content": [
    {
      "type": "tool_use",
      "id": "tool_use_xyz789",
      "name": "lookup_order",
      "input": {"customer_id": "CUST-001", "order_id": "ORD-101"}
    }
  ]
}

Agentic Loop Processing:
- Check: response.stop_reason == "tool_use"? YES
- Extract tool block: name="lookup_order", input={...}, id="tool_use_xyz789"
- Call: ToolExecutor.execute("lookup_order", {...})
  * Prerequisite check: lookup_order requires ["get_customer"]
  * Is "get_customer" in executed_tools? YES ✓
  * Call mock: lookup_order("CUST-001", "ORD-101")
  * Return: {"success": True, "data": {"id": "ORD-101", "status": "delivered", "total": 150.00, ...}}
  * Normalize + track
- Wrap and append to messages

Updated messages: [iteration 1 messages + new tool_result]

Continue to ITERATION 3
```

**ITERATION 3:**
```
Claude now knows:
- Customer: Alice Johnson (CUST-001)
- Order: ORD-101 delivered, $150, Laptop Stand
- User wants: Refund

Thinks: "I have all information needed. I can process the refund."
Decides: "I'll call process_refund with reason='defective'"

API Response:
{
  "stop_reason": "tool_use",
  "content": [
    {
      "type": "tool_use",
      "id": "tool_use_def456",
      "name": "process_refund",
      "input": {
        "customer_id": "CUST-001",
        "order_id": "ORD-101",
        "reason": "doesn't fit / customer_request"
      }
    }
  ]
}

Agentic Loop Processing:
- Check: response.stop_reason == "tool_use"? YES
- Extract and execute process_refund
  * Prerequisite check: requires ["get_customer", "lookup_order"]
  * Are both in executed_tools? YES ✓
  * Call mock: process_refund(...)
  * Return: {"success": True, "data": {"refund_id": "REF-ORD-101", "status": "processed", "amount": 150.00, "estimated_arrival": "3-5 business days"}}
- Normalize + track

Updated messages: [all previous + new tool_result]

Continue to ITERATION 4
```

**ITERATION 4:**
```
Claude reads full context:
- Retrieved customer ✓
- Looked up order ✓
- Processed refund ✓
- All user concerns addressed

Thinks: "I have completed the refund. I should now summarize the resolution for the customer."
Decides: "I'll generate a helpful final response"

API Response:
{
  "stop_reason": "end_user_message",
  "content": [
    {
      "type": "text",
      "text": "Thank you for contacting us, Alice. I've successfully processed your refund for order ORD-101...\n\nRefund Details:\n- Refund ID: REF-ORD-101\n- Amount: $150.00\n- Status: Processed\n- Estimated Arrival: 3-5 business days\n\nThe refund will be credited back to your original payment method. Please allow 3-5 business days for the funds to appear. Thank you for your patience, and we apologize that the stand didn't meet your needs."
    }
  ]
}

Agentic Loop Processing:
- Check: response.stop_reason == "tool_use"? NO
- Check: response.stop_reason == "end_user_message"? YES
- Extract final response text
- Print: "AGENT RESPONSE: [extracted text]"
- Return final_response
- EXIT LOOP

Agent completes successfully.
```

---

## PART 4: KEY PATTERNS TO MEMORIZE FOR THE EXAM

### **Pattern 1: The Agentic Loop Structure**
**What:** The core pattern that makes all agents work
**Where it appears:** Domain 1.1, Questions Q1, Q7-Q9, Q13-Q29
**The pattern:**
```python
iteration = 0
while iteration < max_iterations:
    iteration += 1
    response = client.messages.create(tools=TOOLS, messages=messages)

    if response.stop_reason == "tool_use":
        # Process tool calls, add results to messages
    elif response.stop_reason == "end_user_message":
        # Extract final response and return
        return final_response
```

**Memorize:**
- `stop_reason` is the decision point: should agent use tools or respond?
- Messages accumulate across iterations (not reset)
- Tool results are added as `{"role": "user", "content": [tool_result]}`
- Always use `max_iterations` safety limit

---

### **Pattern 2: Prerequisite Gating**
**What:** Enforcing tool call sequencing
**Where it appears:** Domain 1.1, Domain 2.4, Questions Q1, Q31, Q37
**The pattern:**
```python
prerequisites = {
    "lookup_order": ["get_customer"],
    "process_refund": ["get_customer", "lookup_order"],
}

required_tools = prerequisites.get(tool_name, [])
for required_tool in required_tools:
    if required_tool not in self.executed_tools:
        return PREREQUISITE_NOT_MET_ERROR
```

**Memorize:**
- Track executed tools in a dictionary
- Prevent illogical tool sequences
- Return retryable error with `suggestedNextStep`
- Agent learns from error and self-corrects

---

### **Pattern 3: Structured Error Responses**
**What:** Consistent error format that guides agent behavior
**Where it appears:** Domain 2.2, Domain 2.5, Questions Q31, Q40
**The pattern:**
```python
{
    "status": "error",
    "errorCategory": "PREREQUISITE_NOT_MET|NOT_FOUND|INVALID_REQUEST",
    "isRetryable": True|False,  # Key decision point
    "message": "Human-readable error",
    "suggestedNextStep": "What agent should do next"
}
```

**Memorize:**
- `errorCategory` tells agent type of error
- `isRetryable: True` → agent will retry after fixing something
- `isRetryable: False` → agent will pivot strategy
- Always include `suggestedNextStep` for better agent behavior

---

### **Pattern 4: PostToolUse Normalization**
**What:** Standardizing tool responses for agent reasoning
**Where it appears:** Domain 5.3, Questions Q69-Q70
**The pattern:**
```python
def _normalize_response(self, result: dict) -> dict:
    if result.get("success"):
        return {
            "status": "success",
            "data": result.get("data"),
            "timestamp": "..."
        }
    else:
        return {
            "status": "error",
            "errorCategory": result.get("errorCategory"),
            "isRetryable": result.get("isRetryable"),
            "message": result.get("message")
        }
```

**Memorize:**
- Raw tools return inconsistent schemas
- Normalization ensures consistency
- Agent reasoning improves with consistent data structure
- Apply after every tool execution, before adding to messages

---

### **Pattern 5: Tool Result Wrapping**
**What:** Packaging tool results for the API
**Where it appears:** Domain 1.5, Questions Q19-Q21, Q22-Q24
**The pattern:**
```python
tool_results = []
for block in response.content:
    if block.type == "tool_use":
        result = tool_executor.execute(block.name, block.input)
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": block.id,  # Link to tool call
            "content": result  # JSON string
        })

messages.append({
    "role": "user",  # Important: "user", not "assistant"
    "content": tool_results
})
```

**Memorize:**
- `tool_use_id` links result back to specific tool call
- Role is "user", not "assistant"
- Content is list of tool_result objects
- tool_use_id MUST match the id from tool_use block

---

### **Pattern 6: Multi-Concern Handling**
**What:** Using agentic loop to resolve multiple issues in one request
**Where it appears:** Domain 1.6, Domain 1.7, Questions Q25-Q29
**The pattern:**
- System prompt instructs agent to handle multiple concerns
- Each tool call adds context to messages
- Agent reads full message history to decide next step
- Iteration continues until all concerns resolved
- Final response summarizes all actions taken

**Memorize:**
- Multiple concerns = multiple tool calls across multiple iterations
- NOT multiple tools in single iteration (usually)
- System prompt guides sequencing strategy
- Message accumulation enables context awareness

---

### **Pattern 7: Tool Definition Best Practices**
**What:** Designing tools that agents can use effectively
**Where it appears:** Domain 2.1, Domain 2.2, Questions Q30-Q31
**The pattern:**
```python
{
    "name": "lookup_order",
    "description": "Look up order details. Prerequisite: get_customer must be called first.",
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The customer ID"
            },
            "order_id": {
                "type": "string",
                "description": "The order ID"
            }
        },
        "required": ["customer_id", "order_id"]
    }
}
```

**Memorize:**
- Description should be clear and action-oriented
- List prerequisites in description (agent reads this)
- Input schema must specify required parameters
- Properties should have types and descriptions

---

## PART 5: COMMON EXAM TRAPS & HOW TO AVOID THEM

### **Trap 1: Confusing `stop_reason` Values**
**The trap:**
Thinking `stop_reason == "tool_use"` means "agent is done using tools" (wrong)

**The reality:**
- `stop_reason == "tool_use"` means "agent **wants to use** tools now"
- Agent has generated tool call blocks
- Your code must execute them and loop back
- `stop_reason == "end_user_message"` means agent is done and ready to respond

**How to avoid:**
- Remember: `tool_use` = keep looping, `end_user_message` = exit loop
- Test your logic: What happens if stop_reason is `tool_use`? (should execute tools)
- What if stop_reason is `end_user_message`? (should return final response)

---

### **Trap 2: Forgetting to Update `executed_tools` Dictionary**
**The trap:**
Checking prerequisites but never tracking successful executions:
```python
# WRONG
if tool_name == "process_refund":
    result = process_refund(...)
    # Forgot to add: self.executed_tools[tool_name] = tool_input
```

**The reality:**
Without tracking, prerequisite checks always fail. Agent gets stuck in loop.

**How to avoid:**
- Always update `self.executed_tools[tool_name] = tool_input` after successful execution
- Test scenario: Can you process a refund after calling get_customer + lookup_order? If not, prerequisite tracking is broken.

---

### **Trap 3: Incorrect Message Role for Tool Results**
**The trap:**
Adding tool results with wrong role:
```python
# WRONG
messages.append({
    "role": "assistant",  # ← Should be "user"
    "content": tool_results
})
```

**The reality:**
Claude expects tool results from the "user" role. Using "assistant" breaks the protocol.

**How to avoid:**
- Remember: Messages are always a conversation between "user" and "assistant"
- User sends: requests and tool results
- Assistant sends: responses and tool calls
- Tool results = user role

---

### **Trap 4: Mixing Success and Error Handling**
**The trap:**
Returning inconsistent error formats:
```python
# WRONG: Inconsistent
if error1:
    return {"error": "...", "code": 404}  # Different schema
elif error2:
    return {"status": "error", "errorCategory": "NOT_FOUND"}  # Different schema
```

**The reality:**
Agent expects consistent structure. Inconsistency causes hallucinations.

**How to avoid:**
- All errors should use same schema: `{status, errorCategory, isRetryable, message, suggestedNextStep}`
- Use normalization function `_normalize_response()` to ensure consistency
- Test: Print both success and error responses. Do they have same top-level keys?

---

### **Trap 5: Forgetting `isRetryable` Flag**
**The trap:**
Returning errors without `isRetryable`:
```python
# INCOMPLETE
return {
    "status": "error",
    "errorCategory": "PREREQUISITE_NOT_MET",
    "message": "..."
    # Forgot: "isRetryable": True
}
```

**The reality:**
Agent doesn't know whether to retry. Behavior becomes unpredictable.

**How to avoid:**
- Always include `isRetryable`
- `PREREQUISITE_NOT_MET` → `isRetryable: True` (agent can fix by calling prerequisite)
- `NOT_FOUND` → `isRetryable: False` (retrying won't help)
- `INVALID_REQUEST` → `isRetryable: False` (bad input won't improve)

---

### **Trap 6: Accessing `response.stop_reason` Without Checking First**
**The trap:**
Assuming `stop_reason` is always one of two values:
```python
# WRONG
if response.stop_reason == "tool_use":
    # handle
else:
    # assume "end_user_message", but could be something else
```

**The reality:**
Claude can return other stop reasons: `"max_tokens"`, `"stop_sequence"`, etc.

**How to avoid:**
```python
# CORRECT
if response.stop_reason == "tool_use":
    # handle tools
elif response.stop_reason == "end_user_message":
    # return final response
else:
    print(f"Unexpected stop_reason: {response.stop_reason}")
    break  # Exit loop safely
```

---

### **Trap 7: Assuming Tools Work Without Validation**
**The trap:**
Not checking if tool execution was successful:
```python
# WRONG
result = tool_executor.execute(tool_name, tool_input)
# Assume success and continue
# But result might be error!
```

**The reality:**
Tools return normalized responses with `status: "success"` or `status: "error"`. Must check.

**How to avoid:**
- Tool executor always returns JSON with structure: `{status: "success|error", ...}`
- Agent reads the JSON and can decide: Should I retry? Pivot? Escalate?
- You don't need to validate in the loop; agent reads the normalized response

---

### **Trap 8: Tool Prerequisites in Description But Not in Gating**
**The trap:**
Documenting prerequisites but not enforcing them:
```python
{
    "name": "process_refund",
    "description": "... Prerequisite: get_customer must be called first."  # Says it
    # But no code enforces it!
}
```

**The reality:**
Agents read the description but prioritize results. If not enforced, agent might skip prerequisite if it feels confident.

**How to avoid:**
- Always enforce prerequisites in `ToolExecutor.execute()`
- Don't rely on description alone
- Test: Can agent bypass prerequisites? If yes, gating is broken.

---

### **Trap 9: Infinite Loops Due to Poor Error Messages**
**The trap:**
Error doesn't guide agent to recovery:
```python
# POOR ERROR
{
    "status": "error",
    "errorCategory": "PREREQUISITE_NOT_MET",
    "message": "Prerequisite failed"
    # No suggestedNextStep = agent might get confused
}
```

**The reality:**
Agent might retry same tool, creating infinite loop.

**How to avoid:**
```python
# GOOD ERROR
{
    "status": "error",
    "errorCategory": "PREREQUISITE_NOT_MET",
    "isRetryable": True,
    "message": "Tool 'process_refund' requires 'get_customer' to be called first",
    "suggestedNextStep": "Call get_customer with the customer_id"
}
```

---

### **Trap 10: Normalizing Only Successful Responses**
**The trap:**
Only normalizing success, forgetting errors:
```python
# WRONG
if result["success"]:
    return normalize_success(result)
else:
    return result  # Forgot to normalize error!
```

**The reality:**
Errors need normalization too. Inconsistent error structure breaks agent reasoning.

**How to avoid:**
```python
# CORRECT
def _normalize_response(self, result: dict) -> dict:
    if result.get("success"):
        return {
            "status": "success",
            "data": ...,
            "timestamp": "..."
        }
    else:
        return {
            "status": "error",
            "errorCategory": ...,
            "isRetryable": ...,
            ...
        }
```

---

## PART 6: QUICK REFERENCE - EXAM QUESTION TYPES & THIS CODE

| **Domain** | **Topic** | **Exam Q Range** | **This Code Section** | **Key Concept** |
|---|---|---|---|---|
| **1.1** | Agentic architecture fundamentals | Q1, Q7 | Lines 345-415 | Stop reason, loop structure |
| **1.2** | Tool integration | Q7, Q19 | Lines 361-393 | Tool extraction, execution |
| **1.3** | Loop control & termination | Q13-Q15 | Lines 346, 395-410 | max_iterations, stop_reason |
| **1.4** | Stop reason handling | Q16-Q18 | Lines 361, 371, 395 | tool_use vs end_user_message |
| **1.5** | Tool use block processing | Q19-Q21 | Lines 374-387 | Extracting tool info, wrapping |
| **1.6** | Tool result messaging | Q22-Q24 | Lines 383-393 | tool_use_id, role="user" |
| **1.7** | Final response extraction | Q25-Q29 | Lines 395-410 | Getting text from blocks |
| **2.1** | Tool definition | Q30 | Lines 23-101 | Schema, properties, required |
| **2.2** | Error categories | Q31 | Lines 135-138, 249-255 | errorCategory values |
| **2.3** | Tool implementation | Q32-Q33 | Lines 107-222 | Mock implementations |
| **2.4** | Prerequisite gating | Q37 | Lines 240-255 | Checking executed_tools |
| **2.5** | Response normalization | Q40 | Lines 287-304 | Consistent schema |
| **5.2** | Error handling | Q70 | Lines 135-138, 249-255 | isRetryable, suggestedNextStep |
| **5.3** | PostToolUse hooks | Q69-Q70 | Lines 280-304 | _normalize_response() |

---

## PART 7: FINAL STUDY CHECKLIST

### **Before the Exam, Verify You Can Explain:**

- [ ] The agentic loop iteration pattern (why iterate, what's checked each time)
- [ ] The difference between `stop_reason == "tool_use"` and `stop_reason == "end_user_message"`
- [ ] How tool results are added back to messages (role, content structure, tool_use_id)
- [ ] How prerequisite gating prevents invalid tool sequences
- [ ] Why `executed_tools` dictionary is necessary
- [ ] The purpose of each field in a normalized error response
- [ ] Why normalization is applied PostToolUse
- [ ] How system prompt guides multi-concern handling
- [ ] The relationship between tool definition (schema) and tool execution (gating)
- [ ] Real-world scenarios where each pattern prevents bugs

### **Code Patterns You Should Be Able to Write from Memory:**

- [ ] Basic agentic loop: check stop_reason → process tools → check again
- [ ] Prerequisite checking: access executed_tools dict → validate
- [ ] Error response: {status, errorCategory, isRetryable, message, suggestedNextStep}
- [ ] Tool result wrapping: {type: "tool_result", tool_use_id, content}
- [ ] Message appending: {role: "user", content: [tool_results]}

### **Exam Scenarios You Might See (Based on This Code):**

**Scenario A:** "Design a system where users can request refunds. What checks must pass before calling process_refund?"
- Answer: get_customer AND lookup_order must be called first

**Scenario B:** "An agent gets PREREQUISITE_NOT_MET error. What should happen next?"
- Answer: Agent should call the missing prerequisite first, then retry

**Scenario C:** "Why normalize tool responses?"
- Answer: Different tools return different schemas. Normalization ensures agent sees consistent structure, improving reasoning reliability

**Scenario D:** "How does the agent handle 'I have 3 problems'?"
- Answer: Single agentic loop with multiple iterations. Each tool call adds context. Agent reads full history and sequences calls intelligently.

---

## Summary Table: Domain Concepts & This Exercise

| **Domain** | **Concept** | **Appears in Code** | **Exam Weight** |
|---|---|---|---|
| **1: Agentic Architecture** | Iteration pattern | run_agent() loop (lines 345-415) | 27% |
| | Stop reason handling | Lines 361, 371, 395 | |
| | Tool orchestration | Lines 371-393 | |
| | Multi-turn context | Message accumulation | |
| **2: Tool Design** | Tool definitions | Lines 23-101 | 18% |
| | Prerequisite gating | Lines 240-255 | |
| | Error categories | Lines 135-138, 249-255 | |
| | Response schema | Lines 107-222 | |
| **5: Context Management** | Message accumulation | Lines 325-393 | 15% |
| | PostToolUse normalization | Lines 287-304 | |
| | State tracking | Lines 231, 278 | |

---

**This Exercise Is Your Reference Implementation.** Return to it whenever you need to clarify domain concepts during exam prep. The code shows best practices for all three domains tested in the certification.

**Good luck on your exam!**
