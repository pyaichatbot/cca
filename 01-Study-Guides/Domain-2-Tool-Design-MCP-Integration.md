# Domain 2: Tool Design & MCP Integration
## Claude Certified Architect – Foundations Exam Study Guide

**Exam Weight:** 18% (13 questions)

---

## Table of Contents
1. [Domain Overview](#domain-overview)
2. [Task 2.1: Effective Tool Interface Design](#task-21-effective-tool-interface-design)
3. [Task 2.2: Structured Error Responses](#task-22-structured-error-responses)
4. [Task 2.3: Tool Distribution & Tool Choice](#task-23-tool-distribution--tool-choice)
5. [Task 2.4: MCP Server Integration](#task-24-mcp-server-integration)
6. [Task 2.5: Built-in Tool Selection](#task-25-built-in-tool-selection)
7. [Key Concepts & Memorization](#key-concepts--memorization)
8. [Common Exam Traps](#common-exam-traps)
9. [Quick Reference Cheatsheets](#quick-reference-cheatsheets)

---

## Domain Overview

Domain 2 focuses on **designing robust tool interfaces and integrating tools via MCP (Model Context Protocol) servers**. This domain bridges the gap between tool capability and agent reliability.

### Core Principles
- **Tool descriptions drive selection**: LLMs rely on descriptions, not code implementation
- **Specialization > generalization**: Agents perform better with focused tool sets
- **Error handling matters**: Structured errors guide agent recovery strategies
- **Configuration is infrastructure**: Proper setup (MCP servers, tool_choice) prevents tool misuse

### Why This Matters
Poorly designed tools lead to:
- Tool misrouting (agent calls wrong tool due to ambiguous descriptions)
- Agent confusion (overlapping tool purposes)
- Wasted retries (non-retryable errors treated as transient)
- Security issues (tools given to agents outside their role)

---

## Task 2.1: Effective Tool Interface Design

### Knowledge Deep Dive

#### Tool Descriptions as Primary Selection Mechanism
The LLM **reads tool descriptions first** to decide which tool to call. The implementation is secondary. If descriptions overlap or are vague, selection becomes unreliable.

**Example Problem:**
```json
{
  "tools": [
    {
      "name": "analyze_content",
      "description": "Analyzes content"
    },
    {
      "name": "analyze_document",
      "description": "Analyzes documents"
    }
  ]
}
```

This is **dangerously vague**. The LLM cannot distinguish between them. A web search result vs. a PDF file may be routed to the wrong tool.

**Root Cause:** Both descriptions use "analyze" and both accept generic "content/document" inputs.

#### Minimal Descriptions Cause Misrouting
Generic descriptions like "Analyzes content" lack:
- **Purpose specificity**: What type of content? When should this tool be used?
- **Input format examples**: What does a valid input look like?
- **Output contract**: What will be returned?
- **Boundary cases**: What should NOT be sent to this tool?

#### Impact of System Prompt Wording
The system prompt can **override** well-written tool descriptions:

```python
# BAD: Keyword-sensitive system prompt
system_prompt = """You are a web research agent.
Always use fetch_url when you need information from the internet.
Always use search_index when searching internal docs.
When the user mentions 'web' or 'online', prefer fetch_url."""
```

This creates **unintended associations**. The LLM may call `fetch_url` even when `search_index` would be more appropriate, based solely on user keyword mention.

### Skills: Writing Differentiated Tool Descriptions

#### Principle 1: Include Purpose, Inputs, Outputs, and Boundaries

```python
from anthropic import Anthropic

client = Anthropic()

# POOR tool definition
poor_tools = [
    {
        "name": "extract_data",
        "description": "Extracts data from text",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"}
            }
        }
    }
]

# EXCELLENT tool definition
excellent_tools = [
    {
        "name": "extract_web_results",
        "description": """Extracts structured data from web search results.

PURPOSE: Parses search engine result snippets to extract facts, URLs, and metadata.

INPUTS:
- search_results: List of HTML snippets from Google/Bing results
- extraction_fields: What to extract (e.g., ['url', 'title', 'snippet', 'publication_date'])

OUTPUTS:
- List of dictionaries with extracted fields
- Confidence scores for each extraction
- Raw snippet for verification

WHEN TO USE:
- You have raw search results and need structured extraction
- You need to quickly parse multiple results
- You're building a fact database from search results

WHEN NOT TO USE:
- For internal documentation (use extract_internal_docs instead)
- For database queries (use query_db instead)
- When you need full page content (use fetch_full_page instead)

EXAMPLES:
Input: ["Google result: AI company founded 2018"]
Output: [{"founded": 2018, "type": "company", "confidence": 0.92}]

EDGE CASES:
- Handles missing publication dates (returns null)
- Ignores promotional content automatically
- Returns partial results if some extractions fail""",
        "input_schema": {
            "type": "object",
            "properties": {
                "search_results": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "HTML snippets from search results"
                },
                "extraction_fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Fields to extract: ['url', 'title', 'snippet', 'date', 'source']"
                }
            },
            "required": ["search_results", "extraction_fields"]
        }
    }
]
```

#### Principle 2: Rename Tools to Eliminate Overlap

| Problem | Solution |
|---------|----------|
| `analyze_content` | `extract_web_results` (web-specific) |
| `analyze_document` | `summarize_pdf_content` (PDF-specific) |
| `fetch_data` | `query_database` (DB-specific) |
| `process_file` | `transform_csv_to_json` (CSV-specific) |

Specific names **disambiguate purpose** and guide the LLM toward correct selection.

#### Principle 3: Split Generic Tools Into Purpose-Specific Tools

```python
# BEFORE: One generic tool causes misrouting
generic_tools = [
    {
        "name": "process_data",
        "description": "Processes different types of data",
        "input_schema": {
            "type": "object",
            "properties": {
                "data": {"type": "string"},
                "operation": {"type": "string", "enum": ["convert", "extract", "validate"]}
            }
        }
    }
]

# AFTER: Three specialized tools
specialized_tools = [
    {
        "name": "convert_csv_to_json",
        "description": """Converts CSV data to JSON format.

Input: CSV string (comma-separated values)
Output: JSON array of objects
Handles: Headers, quoted values, escaping""",
        "input_schema": {
            "type": "object",
            "properties": {
                "csv_data": {"type": "string", "description": "CSV content with headers"}
            },
            "required": ["csv_data"]
        }
    },
    {
        "name": "extract_emails_from_text",
        "description": """Extracts email addresses from unstructured text.

Input: Text blob
Output: List of unique email addresses
Validates: RFC 5322 format""",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to search for emails"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "validate_json_schema",
        "description": """Validates JSON data against a schema.

Input: JSON data, JSON schema
Output: Validation result with error details
Supports: JSON Schema Draft 7""",
        "input_schema": {
            "type": "object",
            "properties": {
                "json_data": {"type": "string"},
                "schema": {"type": "string"}
            },
            "required": ["json_data", "schema"]
        }
    }
]
```

#### Principle 4: Review System Prompts for Keyword Sensitivity

```python
# PROBLEM: System prompt overrides tool descriptions
bad_system = """You are a research agent.
When the user asks about 'statistics', always use statistical_analysis_tool first.
If they mention 'web' or 'internet', use web_search_tool.
For 'documents', use document_reader."""

# BETTER: System prompt enables, not overrides
good_system = """You are a research agent specializing in quantitative analysis.
Your tools are:
- statistical_analysis_tool: For statistical computations and trend analysis
- web_search_tool: For current information and real-time data
- document_reader: For reading and summarizing reports

Choose the best tool based on the task requirements. Prioritize accuracy over speed."""

# EXAMPLE SYSTEM PROMPT FOR TOOL DESCRIPTION AUGMENTATION
context_aware_system = """You are an AI research assistant.

Tool Selection Strategy:
1. Read each tool's description carefully
2. Match the tool to the task requirements
3. If tools seem similar, use the descriptions' "WHEN TO USE" sections to disambiguate
4. Ask the user for clarification if tool purpose is unclear

Key distinctions in your toolset:
- extract_web_results: For parsing search snippets → structured data
- fetch_full_page: For downloading complete web pages → raw HTML
- query_internal_db: For structured data queries → database records
"""
```

### Best Practices Summary

| Practice | Why | Example |
|----------|-----|---------|
| **Specific names** | Disambiguate purpose | `extract_web_results` not `parse_data` |
| **Include examples** | Show expected inputs/outputs | `Example: Input: "AI founded 2018" → Output: {founded: 2018}` |
| **List edge cases** | Prepare for unusual inputs | "Returns null for missing dates" |
| **Define boundaries** | Explain what NOT to use for | "For PDF use summarize_pdf, not extract_web_results" |
| **Separate concerns** | One tool = one job | Three tools instead of one `process_data` |
| **System prompt alignment** | Reinforce, don't override | Describe the selection strategy; don't mandate specific tools |

---

## Task 2.2: Structured Error Responses for MCP Tools

### Knowledge Deep Dive

#### The MCP isError Pattern
MCP defines a standard error response structure:

```json
{
  "type": "text",
  "text": "Error message",
  "_mcp_error": true,
  "isError": true
}
```

This flag **signals to the agent** that the tool call failed, enabling appropriate recovery.

#### Four Error Categories

| Category | Definition | Retryable? | Example | Agent Action |
|----------|-----------|-----------|---------|--------------|
| **Transient** | Temporary failures; retry may succeed | YES | Timeout, service unavailable, rate limit | Retry after backoff |
| **Validation** | Invalid input format/semantics | NO | Missing required field, invalid email format | Fix input, retry once |
| **Business Rule** | Policy violation; expected behavior | NO | User lacks permission, quota exceeded | Inform user, stop |
| **Permission** | Authentication/authorization failure | NO | API key invalid, access denied | Request credentials or escalate |

#### Why Uniform Error Responses Fail

```python
# BAD: Generic error prevents recovery decisions
def fetch_data(api_key):
    try:
        response = requests.get(f"https://api.example.com/data",
                              headers={"Authorization": f"Bearer {api_key}"})
        return response.json()
    except Exception as e:
        return {"isError": True, "text": "Operation failed"}
        # ^ Agent doesn't know: Is this retryable? Is it permission? User's fault?
```

An agent receiving "Operation failed" cannot decide:
- Should I retry?
- Should I ask the user for a new API key?
- Should I use an alternative tool?

#### Structured Metadata Prevents Wasted Retries

```python
# GOOD: Structured error with category and metadata
def fetch_data_improved(api_key):
    try:
        response = requests.get(
            f"https://api.example.com/data",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5
        )
        response.raise_for_status()
        return {"data": response.json()}

    except requests.exceptions.Timeout:
        return {
            "isError": True,
            "text": "API request timed out. The service is temporarily slow.",
            "errorCategory": "transient",
            "isRetryable": True,
            "retryAfter": 3,  # seconds
            "context": {
                "endpoint": "/data",
                "timeout_seconds": 5
            }
        }

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return {
                "isError": True,
                "text": "Authentication failed. The API key is invalid or expired.",
                "errorCategory": "permission",
                "isRetryable": False,
                "suggestedAction": "Provide a valid API key",
                "statusCode": 401
            }
        elif e.response.status_code == 429:
            return {
                "isError": True,
                "text": "Rate limit exceeded. Too many requests in a short period.",
                "errorCategory": "transient",
                "isRetryable": True,
                "retryAfter": int(e.response.headers.get("Retry-After", 60)),
                "context": {
                    "remainingRequests": e.response.headers.get("X-RateLimit-Remaining", 0)
                }
            }
        elif e.response.status_code == 403:
            return {
                "isError": True,
                "text": "Access denied. This API key does not have permission for this resource.",
                "errorCategory": "permission",
                "isRetryable": False,
                "suggestedAction": "Request access or use a different API key"
            }

    except Exception as e:
        return {
            "isError": True,
            "text": f"Unexpected error: {str(e)}",
            "errorCategory": "transient",
            "isRetryable": True,
            "context": {
                "errorType": type(e).__name__
            }
        }
```

### Skills: Implementing Structured Error Responses

#### Skill 1: Return Structured Error Metadata

```python
from typing import Union, Dict, Any

def query_database(table: str, filters: Dict[str, Any]) -> Union[Dict, list]:
    """Database query tool with structured error responses."""

    # Validation errors (non-retryable)
    if not table:
        return {
            "isError": True,
            "text": "Table name is required and cannot be empty.",
            "errorCategory": "validation",
            "isRetryable": False,
            "fieldErrors": {
                "table": "Required field missing"
            }
        }

    if not isinstance(filters, dict):
        return {
            "isError": True,
            "text": f"Filters must be a dictionary. Received: {type(filters).__name__}",
            "errorCategory": "validation",
            "isRetryable": False,
            "expectedFormat": {"column_name": "value"}
        }

    try:
        # Attempt query
        conn = get_db_connection()
        results = conn.query(table, filters)
        return results

    except ConnectionError as e:
        # Transient error (retryable)
        return {
            "isError": True,
            "text": "Database connection lost. Please retry.",
            "errorCategory": "transient",
            "isRetryable": True,
            "retryAfter": 2,
            "context": {
                "attemptedTable": table,
                "errorDetails": str(e)
            }
        }

    except PermissionError as e:
        # Permission error (non-retryable)
        return {
            "isError": True,
            "text": f"You do not have permission to query table '{table}'.",
            "errorCategory": "permission",
            "isRetryable": False,
            "suggestedAction": "Contact your database administrator to request access"
        }

    except Exception as e:
        return {
            "isError": True,
            "text": str(e),
            "errorCategory": "transient",
            "isRetryable": True,
            "context": {"errorType": type(e).__name__}
        }
```

#### Skill 2: Business Rule Violations with Human Context

```python
def process_payment(user_id: str, amount: float, currency: str = "USD") -> Dict:
    """Payment processing with business rule error handling."""

    try:
        # Check business rules
        user = get_user(user_id)

        if user.account_status == "suspended":
            return {
                "isError": True,
                "text": f"Account suspended. Cannot process payment.",
                "errorCategory": "business",
                "isRetryable": False,
                "reason": "Account policy violation",
                "suggestedAction": "Contact support to restore account",
                "supportContact": "support@company.com"
            }

        if amount > user.daily_limit:
            return {
                "isError": True,
                "text": f"Transaction exceeds daily limit. Limit: ${user.daily_limit}, Requested: ${amount}",
                "errorCategory": "business",
                "isRetryable": False,
                "reason": "Policy limit exceeded",
                "limit": user.daily_limit,
                "requested": amount,
                "remaining": max(0, user.daily_limit - user.today_spent),
                "suggestedAction": "Request a limit increase or process a smaller transaction"
            }

        # Process payment
        result = charge_payment(user_id, amount, currency)
        return {
            "success": True,
            "transaction_id": result["id"],
            "amount": amount,
            "currency": currency
        }

    except Exception as e:
        return {
            "isError": True,
            "text": str(e),
            "errorCategory": "transient",
            "isRetryable": True
        }
```

#### Skill 3: Local Error Recovery in Subagents

```python
def fetch_with_local_recovery(url: str, max_retries: int = 3) -> Dict:
    """Fetch with local recovery for transient errors."""

    last_error = None
    attempts = []

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return {
                "success": True,
                "content": response.text,
                "status_code": response.status_code,
                "attempts": attempt + 1
            }

        except requests.exceptions.Timeout as e:
            last_error = e
            attempts.append({
                "attempt": attempt + 1,
                "error": "Timeout",
                "action": "Retrying with backoff" if attempt < max_retries - 1 else "Giving up"
            })
            if attempt < max_retries - 1:
                import time
                time.sleep(2 ** attempt)  # Exponential backoff

        except requests.exceptions.ConnectionError as e:
            last_error = e
            attempts.append({
                "attempt": attempt + 1,
                "error": "Connection error",
                "action": "Retrying with backoff" if attempt < max_retries - 1 else "Giving up"
            })
            if attempt < max_retries - 1:
                import time
                time.sleep(2 ** attempt)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code >= 500:
                # Server error: transient, retryable
                last_error = e
                attempts.append({
                    "attempt": attempt + 1,
                    "error": f"Server error ({e.response.status_code})",
                    "action": "Retrying"
                })
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)
            else:
                # Client error: non-retryable, propagate to coordinator
                return {
                    "isError": True,
                    "text": f"HTTP {e.response.status_code}: {e.response.reason}",
                    "errorCategory": "validation" if e.response.status_code == 400 else "permission",
                    "isRetryable": False,
                    "statusCode": e.response.status_code,
                    "url": url
                }

        except Exception as e:
            return {
                "isError": True,
                "text": f"Unexpected error: {str(e)}",
                "errorCategory": "transient",
                "isRetryable": True
            }

    # All retries exhausted: propagate with context
    return {
        "isError": True,
        "text": f"Failed to fetch {url} after {max_retries} attempts.",
        "errorCategory": "transient",
        "isRetryable": False,  # Local recovery exhausted
        "url": url,
        "attempts": attempts,
        "lastError": str(last_error),
        "suggestedAction": "Check if the URL is accessible and try again later"
    }
```

#### Skill 4: Distinguish Empty Results from Errors

```python
def search_database(query: str, table: str) -> Dict:
    """Search that distinguishes 'no results' from 'error'."""

    try:
        conn = get_db_connection()
        results = conn.query(f"SELECT * FROM {table} WHERE content LIKE ?", (query,))

        # SUCCESS: Query executed, returned 0 rows
        if not results:
            return {
                "success": True,
                "results": [],
                "count": 0,
                "message": f"No documents found matching '{query}' in {table}",
                "isError": False  # Important: this is NOT an error
            }

        # SUCCESS: Query executed, returned rows
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "isError": False
        }

    except Exception as e:
        # ACTUAL ERROR
        return {
            "isError": True,
            "text": str(e),
            "errorCategory": "transient",
            "isRetryable": True
        }
```

### Best Practices Summary

| Practice | Why | Example |
|----------|-----|---------|
| **Always include errorCategory** | Guides agent recovery | "transient", "validation", "permission", "business" |
| **Set isRetryable correctly** | Prevents wasted retries | Timeout=True, Invalid format=False |
| **Include retryAfter** | Enables smart backoff | `"retryAfter": 60` (seconds) |
| **Distinguish from success** | Empty results ≠ error | `"isError": False, "results": []` |
| **Provide context** | Helps agent decide next step | Include attempted table, remaining quota, etc. |
| **Suggest actions** | Guide user/agent | "Request access" vs "Provide valid API key" |

---

## Task 2.3: Tool Distribution & Tool Choice

### Knowledge Deep Dive

#### The Principle: Specialization Over Generalization

**Core Insight:** Giving an agent 18 tools degrades decision quality. Agents with 4-5 focused tools make better choices.

**Why?**
1. **Decision complexity grows exponentially**: With 18 tools, LLM must evaluate 18 descriptions to find the right one
2. **Description ambiguity multiplies**: 18 descriptions = more overlap, more confusion
3. **Cross-specialization causes misuse**: An agent trained to do X will misuse tools designed for Y

**Research Insight:** Studies show:
- 4-5 tools: ~95% correct selection
- 8-10 tools: ~85% correct selection
- 15+ tools: ~60% correct selection

#### Specialization Prevents Misuse

```python
# PROBLEM: Synthesis agent with 15 tools
synthesis_agent_with_all_tools = {
    "tools": [
        "web_search",
        "fetch_url",
        "query_db",
        "extract_json",
        "summarize_text",
        "translate_text",
        "calculate_statistics",
        "generate_chart",
        "validate_schema",
        "send_email",
        "create_calendar_event",
        "upload_file",
        "delete_record",
        # ... more tools
    ]
}

# Risk: Synthesis agent might call web_search when it should consult local_search,
# or attempt to delete_record when it lacks authorization for that role.

# SOLUTION: Scoped tools by agent role
synthesis_agent_specialized = {
    "role": "Content synthesis and summarization",
    "tools": [
        "fetch_document",        # Only fetch, no web search
        "summarize_content",     # Specific to synthesis
        "extract_key_facts",     # Specific to synthesis
    ],
    "cross_role_tool": [
        "verify_fact"            # Limited access to specialized tool for fact-checking
    ]
}

research_agent_specialized = {
    "role": "Information gathering",
    "tools": [
        "web_search",
        "fetch_url",
        "extract_web_results"
    ]
}
```

#### Scoped Tool Access: The Pattern

```
Coordinator Agent (orchestrator)
├── knows about all tools
├── delegates to specialized subagents
└── aggregates results

Research Agent
├── web_search
├── fetch_url
├── extract_web_results
├── (CROSS-ROLE) verify_fact  [limited cross-role tool]

Analysis Agent
├── query_database
├── calculate_statistics
├── generate_visualization
├── (CROSS-ROLE) verify_fact

Synthesis Agent
├── summarize_document
├── extract_key_points
├── compose_summary
├── (CROSS-ROLE) verify_fact
```

#### Tool Choice Configuration Options

| Option | Type | Behavior | Use Case |
|--------|------|----------|----------|
| `"auto"` | Default | LLM decides whether to call a tool or respond | Most cases |
| `"any"` | Forcing | LLM **must** call a tool; never return conversational text | Validation step; ensure tool is called |
| `{"type": "tool", "name": "..."}` | Forced | LLM **must** call this specific tool first | Prerequisite (e.g., extract metadata before analysis) |

```python
# Example: tool_choice configurations
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    tools=tools,
    tool_choice="auto",  # LLM decides if tool needed
    messages=[...]
)

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    tools=tools,
    tool_choice="any",  # LLM MUST call a tool
    messages=[...]
)

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    tools=tools,
    tool_choice={"type": "tool", "name": "extract_metadata"},  # MUST call this tool first
    messages=[...]
)
```

### Skills: Implementing Tool Distribution

#### Skill 1: Restrict Tool Sets by Role

```python
from anthropic import Anthropic

client = Anthropic()

# Define tools by specialization
RESEARCH_TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web for current information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "fetch_url",
        "description": "Fetch and parse content from a URL",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "extract_web_results",
        "description": "Extract structured data from search result snippets",
        "input_schema": {
            "type": "object",
            "properties": {
                "snippets": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Search result snippets"
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Fields to extract"
                }
            },
            "required": ["snippets", "fields"]
        }
    },
    {
        "name": "verify_fact",
        "description": "Cross-role: Verify a fact against reliable sources",
        "input_schema": {
            "type": "object",
            "properties": {
                "fact": {"type": "string", "description": "Fact to verify"}
            },
            "required": ["fact"]
        }
    }
]

ANALYSIS_TOOLS = [
    {
        "name": "query_database",
        "description": "Query the database for structured data",
        "input_schema": {
            "type": "object",
            "properties": {
                "table": {"type": "string"},
                "filters": {"type": "object"}
            },
            "required": ["table"]
        }
    },
    {
        "name": "calculate_statistics",
        "description": "Calculate statistical measures (mean, median, std dev)",
        "input_schema": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Numerical data to analyze"
                },
                "metrics": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["mean", "median", "stddev", "min", "max"]}
                }
            },
            "required": ["data", "metrics"]
        }
    },
    {
        "name": "verify_fact",
        "description": "Cross-role: Verify a fact against reliable sources"
        # (same as above)
    }
]

SYNTHESIS_TOOLS = [
    {
        "name": "summarize_document",
        "description": "Summarize a document into key points",
        "input_schema": {
            "type": "object",
            "properties": {
                "document": {"type": "string"},
                "length": {"type": "string", "enum": ["short", "medium", "long"]}
            },
            "required": ["document"]
        }
    },
    {
        "name": "verify_fact",
        "description": "Cross-role: Verify a fact against reliable sources"
        # (same as above)
    }
]

# Agent instances with scoped tools
def research_agent(task: str):
    """Research agent with web-focused tools."""
    return client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        system="You are a research specialist. Use web_search and fetch_url to find information. Call verify_fact to confirm important claims.",
        tools=RESEARCH_TOOLS,
        messages=[{"role": "user", "content": task}]
    )

def analysis_agent(task: str):
    """Analysis agent with data-focused tools."""
    return client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        system="You are a data analyst. Use query_database and calculate_statistics to analyze data. Call verify_fact to ensure conclusions are supported.",
        tools=ANALYSIS_TOOLS,
        messages=[{"role": "user", "content": task}]
    )

def synthesis_agent(task: str):
    """Synthesis agent with summarization tools."""
    return client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        system="You are a synthesis specialist. Summarize documents and extract key insights. Call verify_fact to validate claims.",
        tools=SYNTHESIS_TOOLS,
        messages=[{"role": "user", "content": task}]
    )
```

#### Skill 2: Replace Generic Tools with Constrained Alternatives

```python
# BEFORE: Generic tool with too many uses
generic_fetch = {
    "name": "fetch_url",
    "description": "Fetch content from any URL",
    "input_schema": {
        "type": "object",
        "properties": {
            "url": {"type": "string"}
        },
        "required": ["url"]
    }
}

# AFTER: Constrained alternatives
constrained_tools = [
    {
        "name": "load_document",
        "description": """Load a document from internal storage.

Validates that the URL is in the approved domain.
Prevents external URL access.

APPROVED DOMAINS:
- docs.company.com
- storage.company.com
- archive.company.com

Returns: Document content (text/HTML)""",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Document URL (must be on approved domain)"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "fetch_public_webpage",
        "description": """Fetch content from public web pages.

Can fetch from any public URL.
Returns parsed HTML/text.
Blocks: Internal corporate URLs, local files.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Public URL"}
            },
            "required": ["url"]
        }
    }
]
```

#### Skill 3: Provide Scoped Cross-Role Tools

```python
# Coordinator agent orchestrates specialized subagents
COORDINATOR_TOOLS = [
    {
        "name": "delegate_research",
        "description": "Delegate a research task to the research agent",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Research task"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "delegate_analysis",
        "description": "Delegate an analysis task to the analysis agent",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Analysis task"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "delegate_synthesis",
        "description": "Delegate a synthesis task to the synthesis agent",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Synthesis task"}
            },
            "required": ["task"]
        }
    }
]

def coordinator_agent(user_task: str):
    """Coordinator orchestrates research, analysis, and synthesis agents."""
    messages = [{"role": "user", "content": user_task}]

    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system="""You are a coordinator agent.

Your role: Break down complex tasks into research, analysis, and synthesis phases.
Delegate to specialized agents:
- delegate_research: For information gathering
- delegate_analysis: For data analysis
- delegate_synthesis: For composing final output

Do not attempt these tasks yourself.""",
            tools=COORDINATOR_TOOLS,
            messages=messages
        )

        # Process tool calls
        if response.stop_reason == "tool_use":
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name

                    if tool_name == "delegate_research":
                        result = research_agent(content_block.input["task"])
                    elif tool_name == "delegate_analysis":
                        result = analysis_agent(content_block.input["task"])
                    elif tool_name == "delegate_synthesis":
                        result = synthesis_agent(content_block.input["task"])

                    # Add result and continue
                    messages.append(response)
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content_block.id,
                                "content": str(result)
                            }
                        ]
                    })
        else:
            # No more tool calls, return final response
            return response
```

#### Skill 4: Using tool_choice for Forced Selection

```python
# Pattern 1: Force a prerequisite tool
def process_with_metadata_extraction(document: str):
    """
    Ensure metadata is extracted before processing.
    Step 1: Force extract_metadata
    Step 2: Allow any tool for processing
    """

    # Step 1: Force extract_metadata
    print("Step 1: Extracting metadata...")
    metadata_response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=[
            {
                "name": "extract_metadata",
                "description": "Extract title, author, date from document",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "document": {"type": "string"}
                    },
                    "required": ["document"]
                }
            }
        ],
        tool_choice={"type": "tool", "name": "extract_metadata"},  # FORCE THIS TOOL
        messages=[{"role": "user", "content": document}]
    )

    # Extract metadata result
    metadata = None
    for content_block in metadata_response.content:
        if content_block.type == "tool_use":
            metadata = content_block.input  # Simulated

    # Step 2: Process with metadata context
    print("Step 2: Processing with metadata...")
    processing_tools = [
        {
            "name": "enrich_with_metadata",
            "description": "Add metadata context to analysis",
            "input_schema": {
                "type": "object",
                "properties": {
                    "document": {"type": "string"},
                    "metadata": {"type": "object"}
                },
                "required": ["document", "metadata"]
            }
        },
        {
            "name": "analyze_content",
            "description": "Analyze document content",
            "input_schema": {
                "type": "object",
                "properties": {
                    "document": {"type": "string"}
                },
                "required": ["document"]
            }
        }
    ]

    final_response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        tools=processing_tools,
        tool_choice="auto",  # LLM chooses: enrich or analyze
        messages=[
            {"role": "user", "content": f"Process this document:\n{document}\n\nMetadata: {metadata}"}
        ]
    )

    return final_response

# Pattern 2: Guarantee tool is called
def validate_input_with_guaranteed_tool(data: str):
    """Guarantee a validation tool is called."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=[
            {
                "name": "validate_schema",
                "description": "Validate data against expected schema",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "string"}
                    },
                    "required": ["data"]
                }
            }
        ],
        tool_choice="any",  # LLM MUST call a tool (validate_schema)
        messages=[{"role": "user", "content": f"Validate this data: {data}"}]
    )

    return response
```

### Best Practices Summary

| Practice | Why | Example |
|----------|-----|---------|
| **Specialize by role** | 4-5 focused tools > 15 generic tools | Research agent: web_search, fetch_url, extract_web_results |
| **Limit cross-role tools** | Prevent misuse; reserve for high-frequency needs | verify_fact across agents, not full tool set access |
| **Replace generic with constrained** | Security + specialization | fetch_document (approved URLs) vs fetch_url (any URL) |
| **Use forced tool_choice** | Ensure prerequisites executed | {"type": "tool", "name": "extract_metadata"} |
| **Use "any" for validation** | Guarantee tool is called | When validation is mandatory |
| **Use "auto" as default** | LLM decides when tools needed | Most conversation flows |

---

## Task 2.4: MCP Server Integration

### Knowledge Deep Dive

#### MCP Server Scoping: Project vs. User Level

**Project Level (`.mcp.json` in project root):**
- Shared team tooling
- Committed to version control
- Team members auto-discover servers
- Used for standard integrations (Jira, GitHub, etc.)

**User Level (`~/.claude.json` in home directory):**
- Personal/experimental servers
- Not committed to repo
- Only available to that user
- Used for testing, trial integrations

```
Project Layout:
project-root/
├── .mcp.json           ← Shared team config
├── src/
├── tests/
└── README.md

User Config:
~/.claude.json         ← Personal config (not in repo)
```

#### Environment Variable Expansion for Credentials

Credentials should **never be committed**. Use environment variables:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "jira": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-jira"],
      "env": {
        "JIRA_URL": "${JIRA_URL}",
        "JIRA_USERNAME": "${JIRA_USERNAME}",
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"
      }
    }
  }
}
```

The client expands `${GITHUB_TOKEN}` from environment variables at runtime.

#### Tools from All Configured Servers Are Available Simultaneously

Once configured, all MCP servers connect at startup. Tools from all servers are available in the same agent.

```python
# All tools from all MCP servers are merged and available
# if configured in .mcp.json:
#   - GitHub server tools: create_issue, add_comment, etc.
#   - Jira server tools: create_ticket, transition_issue, etc.

# They're all available to a single agent:
tools_available = [
    "github_create_issue",
    "github_add_comment",
    "jira_create_ticket",
    "jira_transition_issue",
    # ... etc from all configured servers
]
```

#### MCP Resources: Exposing Content Catalogs

MCP supports **resources**: static or dynamic content catalogs that reduce exploratory tool calls.

```json
{
  "mcpServers": {
    "documentation": {
      "command": "node",
      "args": ["./mcp-doc-server.js"],
      "resources": [
        {
          "uri": "docs://api-reference",
          "name": "API Reference",
          "description": "Complete API documentation index"
        },
        {
          "uri": "docs://schema",
          "name": "Database Schema",
          "description": "Database tables and relationships"
        }
      ]
    }
  }
}
```

Instead of agent calling `search_docs` 5 times, it can directly reference the resource:

```python
# Agent sees available resources and can reference directly:
# "Look at docs://schema to understand the tables"
# Without needing exploratory search calls
```

### Skills: Configuring MCP Servers

#### Skill 1: Project-Scoped MCP Server Configuration

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "GITHUB_REPOSITORY": "company/project-repo"
      }
    },
    "jira": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-jira"
      ],
      "env": {
        "JIRA_HOST": "${JIRA_HOST}",
        "JIRA_EMAIL": "${JIRA_EMAIL}",
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"
      }
    },
    "postgres": {
      "command": "node",
      "args": [
        "./servers/postgres-mcp.js"
      ],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

**Setup Instructions:**
1. Create `.mcp.json` in project root
2. Set environment variables (not in `.mcp.json`):
   ```bash
   export GITHUB_TOKEN="ghp_xxxx..."
   export JIRA_HOST="https://company.atlassian.net"
   export JIRA_EMAIL="user@company.com"
   export JIRA_API_TOKEN="atatt_..."
   export DATABASE_URL="postgresql://user:pass@localhost/db"
   ```
3. Claude reads `.mcp.json`, expands env vars, connects to servers

#### Skill 2: User-Scoped MCP Server Configuration

Create `~/.claude.json` (home directory):

```json
{
  "mcpServers": {
    "local-doc-server": {
      "command": "node",
      "args": [
        "/Users/username/projects/personal-mcp/server.js"
      ]
    },
    "experimental-db": {
      "command": "python",
      "args": [
        "/Users/username/mcp-servers/experimental-db.py"
      ],
      "env": {
        "EXP_DB_URL": "${EXP_DB_URL}"
      }
    }
  }
}
```

**Use Case:** Trial integrations, personal tools, experimental servers not yet ready for team sharing.

#### Skill 3: Enhance MCP Tool Descriptions

MCP tool descriptions should be **even more detailed** than built-in tools, because agents may prefer built-in tools (Grep, Read) over MCP tools by default.

```python
# PROBLEM: MCP tool with weak description
weak_mcp_tool = {
    "name": "search_jira",
    "description": "Search Jira",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        }
    }
}

# AGENT BEHAVIOR: Might prefer Grep (built-in) even when Jira search is better

# SOLUTION: Detailed description showing competitive advantage
strong_mcp_tool = {
    "name": "search_jira_issues",
    "description": """Search Jira for issues using JQL (Jira Query Language).

PURPOSE: Find tickets in the team's issue tracking system with advanced filtering.

CAPABILITIES:
- Full-text search across issue titles, descriptions, comments
- Filter by status, assignee, priority, labels, components
- Search across custom fields (e.g., Environment, Root Cause)
- Returns: Issue ID, title, status, assignee, priority, last updated, link

ADVANTAGES OVER GENERIC SEARCH:
- Jira-specific context: understands issue hierarchy and workflow states
- Real-time data: queries live Jira instance, not indexed/cached
- Advanced queries: supports JQL for complex filtering

INPUT:
- jql: Valid JQL query (e.g., "assignee = currentUser() AND status = 'In Progress'")

EXAMPLES:
- Find all open bugs assigned to me: assignee = currentUser() AND type = Bug AND status != Done
- Find issues created this week: created >= -7d
- Find high-priority issues blocking production: priority = Highest AND labels = blocking-prod

RETURNS:
{
  "issues": [
    {
      "id": "PROJ-1234",
      "title": "Feature X implementation",
      "status": "In Progress",
      "assignee": "Alice",
      "priority": "High",
      "updated": "2024-03-20T15:30:00Z"
    }
  ],
  "count": 5
}

WHEN TO USE:
- Searching for tickets assigned to specific people
- Finding issues with specific labels or status
- Looking for bugs, features, or tasks filed in the last N days
- Complex filtering not possible with simple text search

WHEN NOT TO USE:
- For internal documentation (use docs search)
- For code search (use Github code search)
- For finding test files (use Glob)""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "jql": {
                "type": "string",
                "description": "JQL (Jira Query Language) query string"
            }
        },
        "required": ["jql"]
    }
}
```

#### Skill 4: Choosing Community MCP Servers vs. Custom

**Use Community Servers for:**
- Standard integrations (Jira, GitHub, Slack, Notion, etc.)
- Well-documented tools with large user bases
- Reduced maintenance burden

**Use Custom Servers for:**
- Team-specific workflows (custom business logic)
- Internal tools without public MCP servers
- Organizational data models

```python
# Decision matrix
decision = {
    "Integrations": {
        "GitHub": "Community (official server)",
        "Jira": "Community (official server)",
        "Slack": "Community (official server)",
        "Custom Internal CRM": "Custom (build it)",
        "Proprietary Finance Tool": "Custom (build it)",
        "PostgreSQL": "Community or custom (depending on query patterns)"
    }
}

# Example: Using GitHub community server
# Instead of building a custom GitHub integration,
# use the official @modelcontextprotocol/server-github
```

#### Skill 5: Exposing Content Catalogs as Resources

```javascript
// mcp-documentation-server.js
// Exposes documentation catalog to avoid exploratory searches

const { Server, TextContent, ResourceProvider } = require("@modelcontextprotocol/sdk");

const server = new Server({
  name: "documentation-server",
  version: "1.0.0"
});

// Define resource catalog
const documentResources = [
  {
    uri: "docs://architecture/microservices",
    name: "Microservices Architecture",
    description: "Overview of our microservices architecture, deployment patterns, and service dependencies",
    mimeType: "text/markdown"
  },
  {
    uri: "docs://api/rest-endpoints",
    name: "REST API Endpoints",
    description: "Complete REST API reference with all endpoints, parameters, and examples",
    mimeType: "text/markdown"
  },
  {
    uri: "docs://database/schema",
    name: "Database Schema",
    description: "Database tables, columns, relationships, and indexes",
    mimeType: "text/markdown"
  },
  {
    uri: "docs://deployment/kubernetes",
    name: "Kubernetes Deployment",
    description: "How to deploy services to Kubernetes, configuration, secrets management",
    mimeType: "text/markdown"
  }
];

// Implement resource listing
server.setRequestHandler(ResourceProvider.ListResourcesRequestSchema, async () => {
  return {
    resources: documentResources
  };
});

// Implement resource reading
server.setRequestHandler(ResourceProvider.ReadResourceRequestSchema, async (request) => {
  const resourceUri = request.params.uri;

  const resourceContent = {
    "docs://architecture/microservices": "# Microservices Architecture\n...",
    "docs://api/rest-endpoints": "# REST API\n...",
    "docs://database/schema": "# Database Schema\n...",
    "docs://deployment/kubernetes": "# Kubernetes Deployment\n..."
  };

  return {
    contents: [
      {
        uri: resourceUri,
        mimeType: "text/markdown",
        text: resourceContent[resourceUri] || "Resource not found"
      }
    ]
  };
});

module.exports = server;
```

**How Agent Uses Resources:**

```python
# Agent sees available resources in system context:
# Available documentation:
# - docs://architecture/microservices
# - docs://api/rest-endpoints
# - docs://database/schema
# - docs://deployment/kubernetes

# Agent can directly reference without tool calls:
# "Based on docs://database/schema, the User table has..."
# (No exploratory search needed)

# Agent still has search tools for queries not covered by static resources:
# "Search documentation for 'caching strategy'" → calls search_docs tool
```

### Best Practices Summary

| Practice | Why | Example |
|----------|-----|---------|
| **Project-level .mcp.json** | Share team servers; version control | GitHub, Jira integrations committed to repo |
| **User-level ~/.claude.json** | Personal/experimental; not shared | Trial servers, local development tools |
| **Use env vars** | Never commit credentials | `"env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}` |
| **Detailed tool descriptions** | Compete with built-in tools | Show advantages over Grep/Read, not generic descriptions |
| **Community servers first** | Reduce maintenance | Use official GitHub/Jira servers before building custom |
| **Resources for catalogs** | Reduce exploratory calls | Expose docs index, schema index, API reference as resources |

---

## Task 2.5: Built-in Tool Selection

### Knowledge Deep Dive

#### Tool Categories

| Tool | Purpose | Search Target |
|------|---------|---------------|
| **Grep** | Search file **content** | Pattern matching within files (function names, errors, imports) |
| **Glob** | Find **file paths** | Files by name, extension, path pattern |
| **Read** | Load **full file** | Complete file contents; text files, code, config |
| **Write** | Create/overwrite **file** | New files or complete replacements |
| **Edit** | **Targeted modification** | Change specific lines using unique text matching |
| **Bash** | **Execute commands** | Shell commands; file operations, installations, tests |

#### When to Use Each Tool

```
Task: Find all Python files with "import requests"
└─ Strategy: Grep for import pattern
   └─ Command: Grep with pattern "import requests" and glob="**/*.py"

Task: Find all test files modified in the last week
└─ Strategy: Bash for file system queries with timestamps
   └─ Command: bash "find . -name '*.test.py' -mtime -7"

Task: Extract variable definitions in a config file
└─ Strategy: Read full file, then parse
   └─ Command: Read config.json, then identify "name": value pairs

Task: Add one line to a config file
└─ Strategy: Edit with unique anchor text
   └─ Command: Edit with old_string="# Database config\nDB_HOST=localhost"
               and new_string="# Database config\nDB_HOST=prod.example.com"

Task: Find all functions that call "fetch_data"
└─ Strategy: Grep for function name; Read files to understand context
   └─ Commands: (1) Grep "fetch_data" → find files
               (2) Read each file → trace usage
```

#### When Edit Fails: Read + Write Fallback

Edit requires **unique text matching**. If the text appears multiple times, Edit fails:

```python
# PROBLEM: Edit fails because text appears multiple times
old_string = "timeout = 5"  # Appears in 3 places in the file
# → Edit fails: "Text match is not unique"

# SOLUTION: Read entire file, then Write back with changes
file_content = read(path)
new_content = file_content.replace("timeout = 5", "timeout = 10", 1)  # Replace first occurrence
write(path, new_content)
```

### Skills: Effective Built-in Tool Usage

#### Skill 1: Grep for Content Search

```python
# Use Grep to find:
# - Function definitions (grep "def function_name")
# - Import statements (grep "import module_name")
# - Error messages (grep "Error\|Exception")
# - Specific configuration keys (grep "api_key")
# - Function calls (grep "function_name(")

from anthropic import Anthropic

client = Anthropic()

def find_all_api_calls(codebase_path: str) -> dict:
    """Find all calls to fetch_user_data function across codebase."""

    # Step 1: Grep for all calls to the function
    grep_response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        tools=[
            {
                "name": "grep",
                "description": "Search for patterns in file contents",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Regex pattern to search"},
                        "glob": {"type": "string", "description": "File pattern (e.g., **/*.py)"}
                    },
                    "required": ["pattern"]
                }
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Find all calls to 'fetch_user_data' in Python files in {codebase_path}"
            }
        ]
    )

    # Results show files and line numbers where fetch_user_data is called
    # Example output:
    # - api/users.py:42: user = fetch_user_data(user_id)
    # - services/profile.py:105: data = fetch_user_data(id)
    # - etc.

    return grep_response
```

#### Skill 2: Glob for File Path Matching

```python
# Use Glob to find:
# - All test files (glob "**/*.test.py" or "**/*_test.py")
# - Config files (glob "**/*.json", "**/*.yaml")
# - Source files (glob "src/**/*.ts")
# - Specific named files (glob "**/Dockerfile")

def find_config_files(codebase_path: str) -> dict:
    """Find all configuration files in project."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        tools=[
            {
                "name": "glob",
                "description": "Find files matching a pattern",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Glob pattern (e.g., **/*.json, src/**/*.py)"
                        }
                    },
                    "required": ["pattern"]
                }
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Find all config files (.json, .yaml, .toml) in {codebase_path}"
            }
        ]
    )

    # Results show file paths:
    # - config/database.json
    # - config/api.yaml
    # - pyproject.toml
    # - .env (if not ignored)

    return response
```

#### Skill 3: Read for Full File Operations

```python
def understand_function_signature(file_path: str, function_name: str) -> str:
    """Read file to understand function signature and usage."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        tools=[
            {
                "name": "read",
                "description": "Read file contents",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"}
                    },
                    "required": ["file_path"]
                }
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Read {file_path} and explain the signature and purpose of {function_name}"
            }
        ]
    )

    # Read returns full file content
    # Agent can then analyze function definition, parameters, return type, docstring

    return response
```

#### Skill 4: Edit for Targeted Modifications

```python
def update_config_setting(file_path: str, old_value: str, new_value: str) -> dict:
    """Edit a specific config value using unique text matching."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        tools=[
            {
                "name": "edit",
                "description": "Modify specific lines in a file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"},
                        "old_string": {"type": "string", "description": "Unique text to find"},
                        "new_string": {"type": "string", "description": "Replacement text"}
                    },
                    "required": ["file_path", "old_string", "new_string"]
                }
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"""Update {file_path}:
Change: {old_value}
To: {new_value}

Use surrounding context to make the old_string unique."""
            }
        ]
    )

    return response

# Example: Edit config file
# old_string: "database:\n  host: localhost"  ← Includes context for uniqueness
# new_string: "database:\n  host: prod.example.com"
```

#### Skill 5: Write for File Creation/Complete Replacement

```python
def create_new_config_file(file_path: str, config_content: str) -> dict:
    """Create a new file or completely replace an existing file."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        tools=[
            {
                "name": "write",
                "description": "Create or overwrite a file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["file_path", "content"]
                }
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Create {file_path} with the following content:\n{config_content}"
            }
        ]
    )

    return response
```

#### Skill 6: Bash for System Operations

```python
def run_tests_and_check_results(project_path: str) -> dict:
    """Use Bash to run tests and capture output."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        tools=[
            {
                "name": "bash",
                "description": "Execute shell commands",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell command to execute"}
                    },
                    "required": ["command"]
                }
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Run tests in {project_path} and report the results"
            }
        ]
    )

    return response
```

#### Skill 7: Building Codebase Understanding Incrementally

```python
def trace_function_usage_comprehensive(codebase_path: str, function_name: str):
    """
    Trace function usage across codebase:
    1. Grep for all calls
    2. Read files to understand context
    3. Trace through wrapper modules
    """

    messages = []

    # Step 1: Find all files that call the function
    messages.append({
        "role": "user",
        "content": f"Search for all calls to '{function_name}' in {codebase_path}"
    })

    response1 = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        tools=[
            {
                "name": "grep",
                "description": "Search file contents",
                "input_schema": {
                    "type": "object",
                    "properties": {"pattern": {"type": "string"}},
                    "required": ["pattern"]
                }
            }
        ],
        messages=messages
    )

    # Extract files from grep results
    # Example: api.py:42, services.py:105, utils.py:8

    messages.append(response1)

    # Step 2: Read each file to understand context
    # For each file found:
    for file_in_results in ["api.py", "services.py", "utils.py"]:
        messages.append({
            "role": "user",
            "content": f"Read {file_in_results} and explain how {function_name} is used in context"
        })

        response2 = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=[
                {
                    "name": "read",
                    "description": "Read file contents",
                    "input_schema": {
                        "type": "object",
                        "properties": {"file_path": {"type": "string"}},
                        "required": ["file_path"]
                    }
                }
            ],
            messages=messages
        )

        messages.append(response2)

    # Step 3: Check for wrapper modules and exports
    messages.append({
        "role": "user",
        "content": "Look at the export statements and module dependencies. Are there wrapper modules that re-export this function?"
    })

    response3 = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        tools=[
            {
                "name": "grep",
                "description": "Search for exports",
                "input_schema": {
                    "type": "object",
                    "properties": {"pattern": {"type": "string"}},
                    "required": ["pattern"]
                }
            }
        ],
        messages=messages
    )

    # Now we have complete understanding:
    # - All files that call the function
    # - Context of each call
    # - Any wrapper modules that re-export it

    return response3
```

### Best Practices Summary

| Scenario | Tools | Strategy |
|----------|-------|----------|
| Find function implementations | Grep + Read | Grep for "def name", then Read files to understand signatures |
| Find all test files | Glob | Glob for `**/*.test.ts` or `**/*_test.py` |
| Understand a module's exports | Read | Read file to see module.exports or export statements |
| Add a line to config | Edit (or Read+Write) | Use unique context to find the right place |
| Complete file replacement | Write | When file should be entirely rewritten |
| Run tests/builds | Bash | Execute commands; capture output for analysis |
| Trace function usage | Grep → Read → Grep | Find callers, read context, check for re-exports |

---

## Key Concepts & Memorization

### Core Principles (Exam-Tested)

1. **Tool descriptions drive selection** - LLM reads descriptions first, implementation is secondary
2. **Minimal descriptions cause misrouting** - Vague descriptions lead to wrong tool calls
3. **Specialization > generalization** - 4-5 focused tools beat 18 generic tools
4. **Structured errors guide recovery** - errorCategory + isRetryable tell agent what to do
5. **Scoped access prevents misuse** - Agent with 100 tools will misuse them; 5 focused tools prevent mistakes

### Error Categories (Must Know)

| Category | Retryable | Example | Agent Should |
|----------|-----------|---------|--------------|
| Transient | YES | Timeout, unavailable service | Retry after backoff |
| Validation | NO | Invalid input format | Fix input, retry once |
| Business | NO | Policy violation, quota exceeded | Inform user, stop |
| Permission | NO | 401/403 errors, invalid key | Request credentials |

### Tool Choice Options (Must Know)

| Option | Effect | When to Use |
|--------|--------|------------|
| `"auto"` | LLM decides if tool needed | Most cases (default) |
| `"any"` | LLM must call a tool | Mandatory validation steps |
| `{"type": "tool", "name": "..."}` | Force specific tool first | Prerequisites (extract before analyze) |

### MCP Configuration (Must Know)

| Scope | Location | Use Case | Versioned |
|-------|----------|----------|-----------|
| Project | `.mcp.json` | Team tooling, standard integrations | YES (in git) |
| User | `~/.claude.json` | Personal, experimental servers | NO (local only) |

### Built-in Tool Specialties (Must Know)

| Tool | Specializes In | Use Case |
|------|---|---|
| Grep | Pattern matching in file **content** | Find imports, function calls, error messages |
| Glob | File **path** pattern matching | Find files by extension or name pattern |
| Read | Complete file **content** | Load full file to understand context |
| Write | Create/completely replace files | New files, full overwrites |
| Edit | **Targeted modifications** | Change one section using unique text anchor |
| Bash | System **command execution** | Tests, builds, file operations |

### Keywords for Exam Identification

- **"Tool selection is unreliable"** → Problem: ambiguous descriptions; Solution: specific names, examples, boundaries
- **"Agent misusing tool"** → Problem: too many tools or overlapping purposes; Solution: scope by role
- **"Wasted retries"** → Problem: non-retryable error returned as retryable; Solution: structured error with errorCategory
- **"MCP server not appearing"** → Problem: not configured in .mcp.json or ~/.claude.json
- **"Generic tool being called when specific tool is better"** → Problem: weak MCP tool description; Solution: enhance description to show advantages
- **"Edit command failed"** → Problem: non-unique text; Solution: Read + Write fallback
- **"Can't distinguish between error and empty result"** → Problem: both return isError flag; Solution: return isError=False for empty results

---

## Common Exam Traps

### Trap 1: Confusing Tool Selection with Tool Implementation

**False Assumption:** "If my tool code is correct, the LLM will use it correctly."

**Reality:** LLM selects tools based on **descriptions**, not implementation. Correct code + bad description = tool misuse.

**Exam Scenario:**
```
Q: Your tool analyze_content is being called instead of analyze_document.
   Both do slightly different things. The implementations are correct.
   What's the problem?

A: The descriptions are ambiguous. Rename to extract_web_results and
   summarize_pdf_content. Add "WHEN TO USE" sections to disambiguate.
```

### Trap 2: Mistaking Business Errors for Transient Errors

**False Assumption:** "isRetryable: true when the agent retries, it might succeed."

**Reality:** Business errors (quota exceeded, policy violation) will **never** succeed on retry. Return `isRetryable: false`.

**Exam Scenario:**
```
Q: User exceeds daily transaction limit. Error response has isRetryable: true.
   What's the problem?

A: This is a business rule violation, non-retryable. Retrying won't help.
   Return isRetryable: false and suggest increasing limit or waiting until tomorrow.
```

### Trap 3: Overlooking Permission Errors as Validation Errors

**False Assumption:** "Invalid input (401/403) is just a validation error."

**Reality:** 401/403 are **permission errors**, not validation errors. Agent should ask for credentials, not fix input.

**Exam Scenario:**
```
Q: API call returns 403 Forbidden. Should isRetryable be true?

A: No. errorCategory should be "permission", not "validation".
   Suggest: "Request access or use different API key".
```

### Trap 4: Giving Agents Too Many Cross-Role Tools

**False Assumption:** "Extra cross-role tools help agents be more flexible."

**Reality:** Extra tools increase decision complexity. Agents misuse tools outside their specialization.

**Exam Scenario:**
```
Q: Why is the synthesis agent calling web_search?

A: Synthesis agent has access to web_search (cross-role tool).
   Solution: Remove access. For web info, delegate to research agent via coordinator.
```

### Trap 5: Confusing Edit Failure with Implementation Bug

**False Assumption:** "Edit failed means my file path is wrong or file doesn't exist."

**Reality:** Edit fails when `old_string` is not unique (appears multiple times). Solution: use Read + Write.

**Exam Scenario:**
```
Q: Edit tool keeps failing on config.json. File exists and path is correct.

A: old_string probably appears multiple times.
   Solution: Read config.json, then Write with changes.
```

### Trap 6: Treating All MCP Servers the Same

**False Assumption:** "All MCP servers go in .mcp.json"

**Reality:** `.mcp.json` = team-shared; `~/.claude.json` = personal. Put experimental servers in user config.

**Exam Scenario:**
```
Q: You're testing a new experimental Slack MCP server.
   Where should you configure it?

A: ~/.claude.json (user config), not .mcp.json (team config).
   Only move to .mcp.json after testing is complete and team approves.
```

### Trap 7: Weak MCP Tool Descriptions Leading to Preference for Built-ins

**False Assumption:** "MCP tools are always preferred over built-in tools."

**Reality:** If MCP tool description is weak, agent will prefer built-in tools like Grep.

**Exam Scenario:**
```
Q: Agent using Grep to search Jira instead of search_jira_issues tool.
   Both are available. Why?

A: search_jira_issues has weak description.
   Solution: Add detailed description with advantages, examples,
   showing why it's better than Grep for Jira data.
```

### Trap 8: Misunderstanding Tool Choice Options

**False Assumption:** "`tool_choice: 'any'` means the agent can use any tool (with freedom)."

**Reality:** `tool_choice: 'any'` means the agent **must call a tool** (no freedom to skip).

**Exam Scenario:**
```
Q: What does tool_choice: 'any' do?

A: Forces the model to call a tool rather than returning text.
   Useful when tool execution is mandatory (e.g., validation step).
```

### Trap 9: Returning Error When Empty Result is Expected

**False Assumption:** "No results found" should return isError: true.

**Reality:** "No results found" is a successful query (zero matches). Return isError: false.

**Exam Scenario:**
```
Q: Database query for users matching a filter returns 0 rows.
   What should you return?

A: {
     "isError": false,
     "results": [],
     "message": "No users matched the filter",
     "count": 0
   }

   NOT: {"isError": true, "text": "No results found"}
```

### Trap 10: Forgetting Environment Variable Expansion in .mcp.json

**False Assumption:** "I can commit the API key directly in .mcp.json."

**Reality:** Never commit secrets. Use `${ENV_VAR}` syntax and set env vars at runtime.

**Exam Scenario:**
```
Q: Your .mcp.json has "GITHUB_TOKEN": "ghp_xxxx...". What's wrong?

A: Credentials committed to repo.
   Fix: "GITHUB_TOKEN": "${GITHUB_TOKEN}", then export GITHUB_TOKEN=ghp_xxxx at runtime.
```

---

## Quick Reference Cheatsheets

### Cheatsheet 1: Tool Description Template

```markdown
# Tool Name: [Specific Purpose]

## PURPOSE
[What this tool does, not "analyzes data"]

## INPUT SCHEMA
- field1 (required): Description, expected format
- field2 (optional): Description, default value

## OUTPUT
- Returns: Data structure/format
- Example: {field: value}

## WHEN TO USE
- Condition 1
- Condition 2

## WHEN NOT TO USE
- Condition 1 (use this_tool instead)
- Condition 2 (use that_tool instead)

## EXAMPLES
Input: ...
Output: ...

## EDGE CASES
- Handles null values: ...
- Handles empty input: ...
- Handles malformed data: ...
```

### Cheatsheet 2: Error Response Template

```python
error_response = {
    "isError": True,
    "text": "Human-readable error message",
    "errorCategory": "transient|validation|permission|business",
    "isRetryable": True|False,
    "retryAfter": 60,  # (optional, for transient)
    "suggestedAction": "What to do next",
    "context": {
        # (optional) Additional debug info
    }
}
```

### Cheatsheet 3: MCP Configuration Template

```json
{
  "mcpServers": {
    "server_name": {
      "command": "npx|node|python",
      "args": ["package_or_script"],
      "env": {
        "TOKEN": "${ENVIRONMENT_VAR_NAME}",
        "URL": "${ANOTHER_VAR}"
      }
    }
  }
}
```

### Cheatsheet 4: Tool Selection Decision Tree

```
Question: "What tool should I use?"

1. Looking for FILE PATHS?
   → Glob (*.json, **/*.ts, src/**/test_*)

2. Searching FILE CONTENT for PATTERN?
   → Grep (function names, imports, errors)

3. Need FULL FILE CONTENT to understand context?
   → Read (complete file, then analyze)

4. Modifying ONE SECTION of a file?
   → Edit (if old_string is unique)
   → Read + Write (if old_string not unique)

5. Creating NEW FILE or REPLACING ENTIRE FILE?
   → Write

6. Need to RUN COMMANDS or check system state?
   → Bash (tests, builds, file metadata)

7. Need to access JIRA/GitHub/Database/etc?
   → MCP tool (search_jira, create_github_issue, query_db)
```

### Cheatsheet 5: Exam Question Keywords

| Keyword | What's Being Tested |
|---------|-------------------|
| "tool selection is unreliable" | Tool description quality |
| "agent misusing tool" | Tool scoping / specialization |
| "wasted retries" | Error categorization |
| "environment variable" | MCP configuration security |
| "Edit failed" | Read + Write fallback strategy |
| "empty results vs error" | isError flag distinction |
| "cross-role tool" | Scoped access pattern |
| "tool_choice" | Forcing tool execution |
| ".mcp.json vs ~/.claude.json" | Configuration scope |
| "MCP tool ignored in favor of Grep" | Tool description quality |

### Cheatsheet 6: Common Tool Combinations

| Goal | Tools | Sequence |
|------|-------|----------|
| Understand function behavior | Grep → Read → Grep (for callers) | 1. Find definition 2. Read context 3. Find all calls |
| Update a setting | Read → Edit (or Read+Write) | 1. Read file 2. Make targeted change |
| Audit code for pattern | Grep → Read (files with matches) | 1. Find pattern 2. Examine context |
| Test code | Bash (pytest/npm test) → Bash (view output) | 1. Run tests 2. Analyze failures |
| Set up new MCP server | .mcp.json (config) + env vars (secrets) | 1. Configure server 2. Set env vars 3. Restart |

---

## Exercise 1 Code Reference

The Exercise 1 codebase (`Exercise-1/agent.py`) demonstrates several Domain 2 concepts:

### Example: Tool Definition in agent.py

```python
# Tool with clear purpose and boundaries
tools = [
    {
        "name": "fetch_document",
        "description": """Fetch a document by URL.

ACCEPTS: URLs from approved document storage (docs.company.com, storage.company.com)
RETURNS: Document content as text
ERRORS: Non-retryable for invalid URLs (validation error)
         Retryable for timeouts (transient error)""",
        "input_schema": {...}
    }
]
```

### Example: Structured Error Response in agent.py

```python
def tool_response(success, data=None, error=None):
    if error:
        return {
            "isError": True,
            "text": error.get("message"),
            "errorCategory": error.get("category"),  # transient/validation/permission/business
            "isRetryable": error.get("retryable", False)
        }
    return {"success": True, "data": data}
```

### Example: PostToolUse Normalization in agent.py

Tools may return various formats. PostToolUse normalizes responses before returning to the coordinator:

```python
def normalize_tool_response(raw_response):
    """
    Normalize tool response to standard format.
    Handles: plain text, JSON, errors, empty results
    """
    if isinstance(raw_response, str):
        return {"content": raw_response}
    if isinstance(raw_response, dict) and "isError" in raw_response:
        return raw_response  # Already structured
    return {"content": str(raw_response)}
```

---

## Summary: What to Focus On for the Exam

1. **Tool Descriptions**: Practice writing specific, disambiguated descriptions with WHEN TO USE sections
2. **Error Categories**: Know the four categories and when each applies
3. **Tool Scoping**: Understand how to restrict agents' tool access by role
4. **MCP Configuration**: Know `.mcp.json` vs `~/.claude.json` and env var expansion
5. **Built-in Tools**: Know when to use Grep, Glob, Read, Edit, Write, Bash
6. **Tool Choice**: Know "auto", "any", and forced selection use cases
7. **Common Traps**: Be ready to identify and fix tool misrouting, error categorization, and over-scoping

---

## Final Checklist Before Exam

- [ ] Can I write a tool description that prevents misrouting?
- [ ] Do I understand the four error categories and when each applies?
- [ ] Can I explain why giving an agent 15 tools degrades performance?
- [ ] Do I know the difference between `.mcp.json` and `~/.claude.json`?
- [ ] Can I explain why environment variables should never be committed?
- [ ] Do I know when Edit fails and when to use Read + Write instead?
- [ ] Can I explain the tool_choice options and when each is appropriate?
- [ ] Do I know the difference between isError=false (empty results) vs isError=true (actual error)?
- [ ] Can I trace function usage using Grep → Read → Grep?
- [ ] Do I understand MCP resources and when to expose content catalogs?
