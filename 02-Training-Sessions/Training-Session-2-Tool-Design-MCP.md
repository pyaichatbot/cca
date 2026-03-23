# Training Session 2: Tool Design & MCP Integration
## Claude Certified Architect – Foundations

**Duration:** 2 hours | **Domain Weight:** 18% (13 questions)
**Prerequisites:** Session 1 completed, basic API familiarity
**Delivery Format:** Instructor-led with live coding examples

---

## Session Overview

Tool design and MCP (Model Context Protocol) integration are foundational to building reliable Claude applications. In this session, we move beyond basic tool calling to understand how Claude actually **selects** which tool to use, how to **communicate failures**, how to **distribute tools** across agents, and how to **configure MCP servers** for production use.

This domain accounts for 18% of the CCA Foundations exam—a significant portion. The exam tests not just knowledge of features, but **judgment**: knowing when a tool is badly designed, recognizing error patterns, and making architectural decisions about tool distribution.

---

## Learning Objectives

By the end of this session, you will be able to:

1. **Design tool descriptions** that prevent misrouting and provide clear input/output contracts
2. **Implement structured error responses** that enable clients to recover intelligently
3. **Distribute tools** across agents to maximize reliability and minimize hallucination
4. **Configure MCP servers** at project and user scopes
5. **Select the right built-in tool** for common tasks (read, write, edit, bash, grep, glob)
6. **Recognize and avoid** 5 common tool design anti-patterns

---

## Part 1: Tool Interface Design (Task 2.1) — 30 minutes

### Why Tool Descriptions Are Everything

When you add a tool to Claude, the **description is the primary selection mechanism**. Claude doesn't see the code—it sees only:
- Tool name
- Description
- Parameter schema (types, required fields)
- Examples (if provided)

If your description is unclear, ambiguous, or overlaps with other tools, Claude will guess—and it will guess wrong.

**Real exam scenario:** You have two tools:
- `fetch_user_data` — "Retrieves user information"
- `get_customer_profile` — "Gets customer profile data"

Claude treats these as nearly identical. It will use them interchangeably, sometimes calling both when one would suffice. **Result: wasted API calls, latency, cost.**

### Writing Effective Descriptions

A good tool description answers these questions:

1. **What does it do?** (specific, not generic)
2. **When should I use it?** (vs other tools)
3. **What are inputs/outputs?** (format, constraints, edge cases)
4. **What can go wrong?** (errors, edge cases, limits)

**GOOD example:**

```python
{
  "name": "search_product_catalog",
  "description": """Search for products by keyword, category, or price range.

  Use this to find products a customer is looking for. DO NOT use for inventory
  checks or supplier lookups.

  Inputs:
  - query: free-text search (e.g., "blue running shoes")
  - category: optional, e.g. "footwear", "apparel"
  - max_price: optional, in USD

  Outputs: list of products with id, name, price, stock_status

  Edge cases:
  - Returns empty list if no matches (not an error)
  - Maximum 50 results returned; use pagination for more
  - Does NOT check real-time inventory; use check_inventory for that
  """,
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {"type": "string"},
      "category": {"type": "string", "enum": ["footwear", "apparel", "accessories"]},
      "max_price": {"type": "number", "minimum": 0}
    },
    "required": ["query"]
  }
}
```

**BAD example:**

```python
{
  "name": "search",
  "description": "Search for things",
  "inputSchema": {
    "type": "object",
    "properties": {
      "q": {"type": "string"}
    }
  }
}
```

Why is this bad?
- "Search for things"—*what things?*
- No mention of what gets returned
- No mention of limits, edge cases, or when NOT to use it
- Parameter named `q` (cryptic)

### Avoiding Overlapping Tools

When descriptions overlap, Claude plays roulette. Use a **differentiation matrix**:

| Tool | Primary Use | Secondary Use | When NOT to Use |
|------|-------------|---------------|-----------------|
| `search_products` | Find by keyword/category | Price discovery | Inventory checks |
| `get_product_details` | Fetch full specs by ID | Reviews, images | Searching across catalogs |
| `check_inventory` | Real-time stock levels | — | Searching, price comparisons |

If you find tools that overlap in >2 columns, merge or rename them.

### System Prompt Interactions

The system prompt can **enhance or sabotage** tool descriptions.

**System prompt that helps:**
```
You are a sales agent. Use search_products to find items,
then get_product_details for specs. Never use get_product_details
as a search tool—always search first.
```

**System prompt that hurts:**
```
You have access to search, get_details, and lookup tools.
Use search for everything.
```

The second one directly contradicts a good tool design—now Claude thinks search is universal.

### Code Walkthrough: Good vs Bad Tool Definition

**BAD (overlapping, vague):**

```python
tools = [
    {
        "name": "get_data",
        "description": "Gets data from the system",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "filter": {"type": "string"}
            }
        }
    }
]
```

**GOOD (clear, non-overlapping, bounded):**

```python
tools = [
    {
        "name": "get_user_by_id",
        "description": """Fetch a single user record by ID.

        Returns: name, email, created_at, last_login

        Returns null if user not found (not an error).
        Do NOT use for searching or listing users—use search_users instead.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "Unique user ID (UUID format)"
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "search_users",
        "description": """Search users by name, email, or status.

        Returns: list of users with id, name, email, status

        Use this to find users when you don't have their ID.
        Maximum 100 results per request.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "status": {"type": "string", "enum": ["active", "inactive", "pending"]}
            },
            "required": ["query"]
        }
    }
]
```

### Practice Question

**Q: You're defining tools for an HR system. You have:**
- `get_employee` — fetches by ID
- `list_employees` — returns all employees in a department
- `search_employees` — keyword search across name/email/department

An engineer says you have "too many overlapping tools." What's your response?

**A:** These tools are differentiated and serve different use cases:
- `get_employee` is for direct lookups (fast, specific)
- `list_employees` is for roster operations (manager viewing their team)
- `search_employees` is for discovery (HR admin finding employees by partial info)

However, if Claude frequently confuses them, the descriptions need clarification. Add language like: "Use only when you have an exact employee ID. For finding employees, use search_employees."

---

## Part 2: Structured Error Responses (Task 2.2) — 30 minutes

### The isError Flag Pattern

When a tool fails, Claude needs to know: **Can I retry, or is this permanent?**

The standard pattern is an `isError` field + `errorCategory`:

```typescript
interface ToolResponse {
  isError: boolean;
  errorCategory?: "transient" | "validation" | "business" | "permission";
  isRetryable?: boolean;
  message: string;
  data?: any;
}
```

Without this, Claude treats all responses the same. It might retry a permanent business error or give up on a transient network blip.

### Error Categories: Transient, Validation, Business, Permission

**Transient (isRetryable: true):**
- Network timeout
- Service temporarily down
- Rate limit (with backoff)
- Database connection timeout

Example response:
```json
{
  "isError": true,
  "errorCategory": "transient",
  "isRetryable": true,
  "message": "Database connection timeout. Please retry in 5 seconds."
}
```

**Validation (isRetryable: false):**
- Missing required field
- Invalid format (email, phone number)
- Parameter out of range
- Type mismatch

Example response:
```json
{
  "isError": true,
  "errorCategory": "validation",
  "isRetryable": false,
  "message": "Invalid email format. Expected 'user@example.com', got 'jdoe@invalid'"
}
```

**Business (isRetryable: false):**
- Insufficient funds
- Item out of stock
- Business rule violation
- Quota exceeded

Example response:
```json
{
  "isError": true,
  "errorCategory": "business",
  "isRetryable": false,
  "message": "Cannot refund order #12345: refund window (30 days) has expired. Contact support."
}
```

**Permission (isRetryable: false):**
- User lacks permissions
- API key invalid
- Resource access denied
- Authentication failed

Example response:
```json
{
  "isError": true,
  "errorCategory": "permission",
  "isRetryable": false,
  "message": "User ID 5001 does not have permission to delete department 7. Contact your administrator."
}
```

### Structured Error Metadata

Always include:
- **Human-readable message** (what to show the user)
- **Category** (so the system knows how to respond)
- **Retryable** flag (is this worth retrying?)
- **Actionable guidance** (what should happen next?)

```python
def refund_order(order_id: str, user_id: str) -> dict:
    # Check permission
    if not user_has_permission(user_id, "refunds"):
        return {
            "isError": True,
            "errorCategory": "permission",
            "isRetryable": False,
            "message": f"User {user_id} lacks 'refunds' permission. Contact admin.",
            "required_role": "manager_or_above"
        }

    order = get_order(order_id)

    # Check business rule
    if is_refund_window_expired(order):
        return {
            "isError": True,
            "errorCategory": "business",
            "isRetryable": False,
            "message": f"Order {order_id} refund window (30 days) expired.",
            "days_since_order": (today - order.created_at).days,
            "next_step": "Contact support for exception handling"
        }

    # Attempt refund (transient possible)
    try:
        result = payment_processor.refund(order.payment_id, order.amount)
        return {
            "isError": False,
            "message": f"Refund processed: {result.transaction_id}",
            "refund_amount": order.amount
        }
    except PaymentGatewayTimeout:
        return {
            "isError": True,
            "errorCategory": "transient",
            "isRetryable": True,
            "message": "Payment gateway timeout. Retry in 10 seconds.",
            "retry_after_seconds": 10
        }
```

### Retryable vs Non-Retryable

**EXAM TRAP:** Many developers return `isRetryable: true` for business errors.

```python
# WRONG
if account.balance < withdrawal_amount:
    return {
        "isError": True,
        "isRetryable": True,  # ❌ WRONG!
        "message": "Insufficient funds"
    }
```

Retrying this 100 times won't change the account balance. Mark it `isRetryable: false`.

**Correct:**
```python
if account.balance < withdrawal_amount:
    return {
        "isError": True,
        "errorCategory": "business",
        "isRetryable": False,
        "message": f"Insufficient funds. Account balance: ${account.balance}, requested: ${withdrawal_amount}"
    }
```

### Code Walkthrough: Error Response Library

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any

class ErrorCategory(Enum):
    TRANSIENT = "transient"
    VALIDATION = "validation"
    BUSINESS = "business"
    PERMISSION = "permission"

@dataclass
class ToolError:
    message: str
    category: ErrorCategory
    is_retryable: bool
    details: Optional[dict] = None

    def to_response(self) -> dict:
        return {
            "isError": True,
            "errorCategory": self.category.value,
            "isRetryable": self.is_retryable,
            "message": self.message,
            **(self.details or {})
        }

# Usage:
if not user.has_permission("delete_user"):
    error = ToolError(
        message="Permission denied: only admins can delete users",
        category=ErrorCategory.PERMISSION,
        is_retryable=False,
        details={"user_role": user.role, "required_role": "admin"}
    )
    return error.to_response()
```

### Practice Questions

**Q1: A tool calls an external API. The API returns a 503 error (service unavailable). Should isRetryable be true or false?**

A: **True.** 503 is transient; the service may recover. Return:
```json
{"isError": true, "errorCategory": "transient", "isRetryable": true, "message": "External service temporarily unavailable"}
```

**Q2: Your tool tries to assign a user to a role they're already assigned to. What error category?**

A: **Business.** Assigning to an existing role is a business rule (idempotency), not a transient failure. Return `isRetryable: false`.

---

## Part 3: Tool Distribution & tool_choice (Task 2.3) — 25 minutes

### The Too-Many-Tools Problem

Claude's tool selection reliability degrades with tool count.

- **4–5 tools:** >95% accuracy
- **10–15 tools:** ~85% accuracy
- **20+ tools:** ~70% accuracy

More tools = more hallucination, wrong tool selection, longer latency.

**EXAM SCENARIO:** A company adds 25 tools to Claude for a customer service agent. They expect "Claude will just pick the right one." Reality: Claude calls the wrong tool 30% of the time, leading to cascading errors.

### Scoped Tool Access: The Solution

Instead of giving one agent all 25 tools, **distribute tools across specialized sub-agents**:

```
Main Agent (5 tools)
├─ search_orders
├─ search_customers
├─ contact_support
├─ escalate_issue
└─ route_to_specialist

Refund Specialist Sub-Agent (4 tools)
├─ get_order_details
├─ check_refund_policy
├─ process_refund
└─ send_confirmation_email

Technical Support Sub-Agent (6 tools)
├─ get_system_status
├─ list_common_errors
├─ view_logs
├─ run_diagnostics
├─ create_ticket
└─ request_logs_from_user
```

Each agent has a **focused toolset**, improving accuracy from 70% to 95%.

### tool_choice Modes: auto, any, forced tool

```python
# mode: "auto" (default)
# Claude chooses whether to use tools or return text
response = client.messages.create(
    model="claude-opus-4-1-20250805",
    max_tokens=1024,
    tools=tools,
    tool_choice={"type": "auto"},
    messages=[{"role": "user", "content": "What's 2+2?"}]
)
# Claude can say "4" without using a tool

# mode: "any"
# Claude must use a tool if available
response = client.messages.create(
    model="claude-opus-4-1-20250805",
    max_tokens=1024,
    tools=tools,
    tool_choice={"type": "any"},
    messages=[{"role": "user", "content": "Get customer 123"}]
)
# Claude must pick a tool; it won't say "I could use the get_customer tool"

# mode: "forced" (restricted)
# Claude must use a specific tool
response = client.messages.create(
    model="claude-opus-4-1-20250805",
    max_tokens=1024,
    tools=tools,
    tool_choice={"type": "tool", "name": "get_customer"},
    messages=[{"role": "user", "content": "Get customer 123"}]
)
# Claude must call get_customer; no other option
```

**Use cases:**
- `auto`: General-purpose agents (max flexibility)
- `any`: Specialized intake workflows (force tool use for data collection)
- `forced`: Strict linear workflows (e.g., "always refund first, then email")

### Code Walkthrough: Multi-Agent Architecture

```python
class OrderAgent:
    """Primary agent: search and triage orders"""
    tools = [
        get_order_tool,
        search_orders_tool,
        check_status_tool
    ]
    tool_choice = "auto"

class RefundAgent:
    """Specialized: refund operations only"""
    tools = [
        get_refund_policy_tool,
        process_refund_tool,
        send_refund_email_tool
    ]
    tool_choice = "any"  # Force refund specialist to use tools

class IntakeAgent:
    """Data collection: must gather required fields"""
    tools = [
        get_customer_details_tool,
        get_account_status_tool
    ]
    tool_choice = "any"  # Force data collection before escalation

# Workflow:
# 1. OrderAgent triages customer request (auto tool choice)
# 2. If refund needed, delegate to RefundAgent (any tool choice)
# 3. If dispute, delegate to IntakeAgent first (any tool choice)
```

### Practice Question

**Q: Your e-commerce system has 22 tools. A single agent using all 22 has 70% tool selection accuracy. How do you improve to 95%?**

A:
1. Identify primary use cases (search, checkout, support, admin)
2. Create sub-agents: SearchAgent (4 tools), CheckoutAgent (5 tools), SupportAgent (6 tools), AdminAgent (7 tools)
3. Route customer requests to the appropriate agent
4. Use `tool_choice: "any"` for critical workflows (checkout) to force tool use
5. Result: each agent now has 4–7 tools, accuracy improves to 95%+

---

## Part 4: MCP Server Integration (Task 2.4) — 20 minutes

### Project vs User MCP Config

MCP servers can be configured at two scopes:

**Project-level (.mcp.json):**
- Specific to one project
- Checked into version control (if not sensitive)
- Used by developers on that project
- Example: a project needs a custom database connector

**User-level (~/.claude.json):**
- Available to all Claude Code projects
- User's personal setup
- Secrets, personal integrations
- Example: user's GitHub token, personal API keys

### .mcp.json vs ~/.claude.json

**Project-level (.mcp.json):**

```json
{
  "mcpServers": {
    "project-db": {
      "command": "python",
      "args": ["./mcp_servers/postgres_server.py"],
      "env": {
        "DB_HOST": "${DB_HOST}",
        "DB_PORT": "5432"
      }
    }
  }
}
```

**User-level (~/.claude.json):**

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}"
      }
    }
  }
}
```

### Environment Variable Expansion

Both configs support env var expansion via `${VAR_NAME}`.

**How it works:**
1. Claude Code reads `.mcp.json` or `~/.claude.json`
2. Sees `${DB_PASSWORD}`
3. Substitutes the actual value from the environment
4. Launches the MCP server

**EXAM TRAP:** Storing secrets in .mcp.json directly.

```json
{
  "mcpServers": {
    "mydb": {
      "env": {
        "DB_PASSWORD": "super-secret-password"  // ❌ WRONG
      }
    }
  }
}
```

**Correct:**

```json
{
  "mcpServers": {
    "mydb": {
      "env": {
        "DB_PASSWORD": "${DB_PASSWORD}"  // ✓ Read from env at runtime
      }
    }
  }
}
```

Then set in shell:
```bash
export DB_PASSWORD="super-secret-password"
claude code ./my-project
```

### Practice Question

**Q: You're setting up GitHub and Slack MCP servers. Should they go in .mcp.json or ~/.claude.json?**

A: **~/.claude.json** (user-level). These are personal integrations. GitHub and Slack tokens are user-specific secrets that shouldn't be in project version control. Project-specific servers (like a custom database connector) go in .mcp.json.

---

## Part 5: Built-in Tools (Task 2.5) — 15 minutes

Claude provides five core file and system tools. Knowing when to use each is critical.

### When to Use Which

| Tool | Purpose | Example |
|------|---------|---------|
| `read` | Read file contents | Analyze code, read configuration |
| `write` | Create or overwrite files | Generate new file from scratch |
| `edit` | Modify specific sections | Fix a bug in one function |
| `bash` | Execute shell commands | Run tests, git operations, package installs |
| `grep` | Search file contents | Find all references to a function |
| `glob` | Find files by pattern | Find all `.ts` files in src/ |

**read vs grep:**
- Use `read` if you know the file path and want full content
- Use `grep` if you're searching across many files

**write vs edit:**
- Use `write` for new files or complete rewrites
- Use `edit` for targeted changes (preserves context)

**bash vs built-in tools:**
- Use `bash` for complex shell operations, pipelines
- Use `glob` or `grep` for file operations (faster, safer)

### Code Walkthrough: Built-in Tool Selection

**Task: Find all references to `getUserById` and fix them**

Bad approach (bash only):
```bash
grep -r "getUserById" src/
# Output shows 12 matches across 4 files
```

Good approach (grep + read + edit):
```python
# Step 1: Find files
grep_result = tool_grep(pattern="getUserById", path="src/")
# Returns: ["src/api.ts:34", "src/utils.ts:12", ...]

# Step 2: Read each file
for file in grep_result.files:
    content = tool_read(file)
    # Analyze context

# Step 3: Edit each file
tool_edit(file="src/api.ts",
          old_string="const user = getUserById(123);",
          new_string="const user = await getUser(123);")
```

### Practice Question

**Q: You need to find and count how many times the word "TODO" appears across 500 JavaScript files. What's the best approach?**

A: **Use grep with count mode:**
```bash
grep --count "TODO" src/**/*.js
# Or via tool:
grep_result = tool_grep(pattern="TODO", path="src/", glob="**/*.js", output_mode="count")
```

This is faster and more resource-efficient than reading all 500 files.

---

## Session Summary & Key Takeaways

1. **Tool descriptions are the selection mechanism.** Write them as contracts: what it does, when to use it, what can go wrong.

2. **Error responses must distinguish transient from permanent.** Use `isRetryable` and `errorCategory` consistently.

3. **Distribute tools to agents by specialization.** Fewer tools per agent = higher accuracy. 4–5 tools optimal.

4. **Use tool_choice strategically.** `auto` for flexibility, `any` for mandatory flows, `forced` for strict workflows.

5. **MCP config scopes matter.** Secrets go in `~/.claude.json` with env var expansion; project tools go in `.mcp.json`.

6. **Choose the right built-in tool.** `grep` for search, `read` for content, `edit` for changes, `bash` for complex operations.

---

## Hands-On Lab Exercise

**Scenario:** You're building a support ticket system. You have these tools:

1. `get_ticket` — fetch ticket by ID
2. `list_tickets` — list all tickets for a user
3. `update_ticket_status` — update status (open, in_progress, closed)
4. `add_ticket_comment` — add a comment
5. `escalate_ticket` — move to specialist queue
6. `get_user_account` — fetch user account
7. `list_user_invoices` — list invoices
8. `check_refund_eligibility` — check if eligible for refund
9. `process_refund` — process a refund
10. `send_email_template` — send email to user

**Tasks:**

1. **Identify overlaps:** Which tools are redundant or conflicting?
2. **Design sub-agents:** Split into a Support Agent and a Refund Agent. What tools does each have?
3. **Write tool descriptions:** Write clear descriptions for `get_ticket` and `check_refund_eligibility` that prevent misrouting.
4. **Design error responses:** The refund processor encounters an API timeout. Write the response object.
5. **Configure tool_choice:** For the Support Agent, should tool_choice be "auto" or "any"? Why?

---

## Self-Assessment Quiz

**Q1: Your tool description says "Get user data." A colleague says this is bad. Why?**
- A) It's too short
- B) It doesn't differentiate from other get_* tools
- C) It doesn't explain edge cases or constraints
- D) All of the above

**Answer: D.** Good descriptions explain what, when, and what can go wrong.

---

**Q2: A tool fails because the external API is temporarily down (503 error). How should isRetryable be set?**
- A) true (transient failure)
- B) false (permanent failure)
- C) It depends on the specific API
- D) Don't use isRetryable; use only errorCategory

**Answer: A.** 503 errors are transient and often resolve with retry.

---

**Q3: You're building an agent with 18 tools. Tool selection accuracy is 72%. What's the most effective fix?**
- A) Improve tool descriptions
- B) Reorder tools in the list
- C) Create sub-agents and distribute tools
- D) Use tool_choice="forced" for all tools

**Answer: C.** Sub-agents with 4–5 tools each improve accuracy to 95%+.

---

**Q4: Your project needs a custom MCP server for database access. Should you:**
- A) Add it to ~/.claude.json
- B) Add it to .mcp.json
- C) Run it as a separate service
- D) Hardcode it in the application

**Answer: B.** Project-specific integrations go in .mcp.json. User integrations go in ~/.claude.json.

---

**Q5: When should you use the grep tool instead of the bash command?**
- A) For simple pattern matching across multiple files
- B) For complex regex with piping
- C) For counting matches
- D) Both A and C

**Answer: D.** `grep` is more efficient for search operations; `bash` is for complex pipelines.

---

**Q6: What error category should be returned if a user tries to refund an order outside the 30-day window?**
- A) transient
- B) validation
- C) business
- D) permission

**Answer: C.** It's a business rule violation, not a transient failure or permission issue.

---

**Q7: You have a critical workflow that must collect customer ID, order ID, and reason before proceeding. What tool_choice should you use?**
- A) auto
- B) any
- C) forced
- D) undefined (disable tool choice)

**Answer: B.** `any` forces the agent to use tools, ensuring data collection happens.

---

## Recommended Study Resources

1. **Official MCP Documentation:** https://modelcontextprotocol.io
2. **Claude API Documentation:** https://docs.anthropic.com
3. **Tool Design Best Practices:** Review the exam study guide's tool description examples
4. **Error Handling Patterns:** Study the isError/errorCategory spec in detail
5. **Sub-Agent Architectures:** Practice breaking down multi-tool problems into focused agents

---

**End of Session 2**

**Checkpoint:** Before moving to Session 3, ensure you can:
- ✓ Write non-overlapping tool descriptions
- ✓ Structure error responses with proper categories
- ✓ Design a multi-agent system to improve tool accuracy
- ✓ Configure MCP servers at project and user scopes
- ✓ Select the appropriate built-in tool for a task
