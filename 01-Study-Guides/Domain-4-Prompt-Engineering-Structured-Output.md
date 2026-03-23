# Domain 4: Prompt Engineering & Structured Output
## Claude Certified Architect – Foundations Exam Study Guide

**Domain Weight:** 20% of exam (14 questions)
**Format:** Mix of scenario-based, code-based, and knowledge questions
**Key Focus:** Practical implementation of prompt engineering patterns and structured output techniques

---

## Table of Contents

1. [Domain Overview](#domain-overview)
2. [Task 4.1: Design Prompts with Explicit Criteria](#task-41-design-prompts-with-explicit-criteria)
3. [Task 4.2: Apply Few-Shot Prompting](#task-42-apply-few-shot-prompting)
4. [Task 4.3: Enforce Structured Output](#task-43-enforce-structured-output)
5. [Task 4.4: Implement Validation & Feedback Loops](#task-44-implement-validation--feedback-loops)
6. [Task 4.5: Design Efficient Batch Processing](#task-45-design-efficient-batch-processing)
7. [Task 4.6: Design Multi-Instance & Multi-Pass Review](#task-46-design-multi-instance--multi-pass-review)
8. [Key Concepts & Memory Items](#key-concepts--memory-items)
9. [Exam Traps & Misconceptions](#exam-traps--misconceptions)
10. [Quick Reference Cheatsheet](#quick-reference-cheatsheet)
11. [Complete Code Examples](#complete-code-examples)

---

## Domain Overview

Domain 4 focuses on moving beyond basic prompting to production-grade prompt engineering techniques. The core principle is that **precision, consistency, and scalability** require structured approaches:

- **Explicit criteria** eliminate ambiguity that vague instructions create
- **Few-shot examples** demonstrate expected behavior better than prose descriptions
- **Tool use + JSON schemas** guarantee syntactically correct structured output
- **Validation loops** catch semantic errors that schemas miss
- **Batch API** enables cost-effective large-scale processing
- **Multi-instance architectures** overcome self-review limitations

This domain heavily emphasizes the difference between **what should work** (confidence-based filtering, self-review, detailed instructions) and **what actually works** (explicit criteria, few-shot examples, tool-use, independent review).

---

## Task 4.1: Design Prompts with Explicit Criteria

### Core Concept: Explicit Criteria > Vague Guidance

The fundamental principle: **specific categorical criteria outperform general instructions for improving precision.**

#### The Problem with Vague Instructions

```python
# ❌ INEFFECTIVE - Relies on model's interpretation of "be conservative"
prompt = """
Review this code for issues. Be conservative - only report high-confidence bugs.
Don't report style issues or minor improvements.
"""

# ✅ EFFECTIVE - Explicit categorical criteria
prompt = """
Report ONLY these issue types:
1. LOGIC_BUG: Code behavior contradicts its comments or requirements
2. SECURITY: Unvalidated user input, SQL injection, auth bypass
3. MEMORY_LEAK: Resources not released (handles, database connections)

DO NOT report:
- Code style or formatting
- Variable naming conventions
- Local library usage patterns known to work
- TODO comments

For each issue, specify: [TYPE] Location: Detail with concrete contradiction.
"""
```

#### Why This Works

**False positive impact:** When a category has high false positive rate (e.g., 40% of style issues flagged are actually acceptable), developers dismiss findings in that entire category, including legitimate ones.

**Explicit criteria solution:**
- Categories are defined by what to report vs. skip
- No "confidence" judgment—criteria are deterministic
- Developers know exactly why something was flagged

#### Key Implementation Pattern

```python
def design_review_criteria():
    """
    Best practice template for review prompts.
    """
    criteria = {
        "report": {
            "logic_bugs": "Actual behavior contradicts stated behavior (comments, requirements)",
            "security_issues": "Unvalidated input, auth bypass, data exposure",
            "critical_performance": "O(n²) in tight loop, unbounded memory growth"
        },
        "skip": {
            "style": "Spacing, naming, import order",
            "local_patterns": "Framework-specific idioms we use throughout",
            "minor_improvements": "Suggests that would require refactor"
        },
        "severity_criteria": {
            "critical": "Security bypass, data loss, production outage",
            "high": "Logic error affecting core functionality",
            "medium": "Edge case handling, incomplete validation",
            "low": "Documentation, debug code left in"
        }
    }
    return criteria

# Concrete examples make criteria unambiguous
severity_examples = {
    "critical": {
        "example": "SELECT * FROM users WHERE id = ' + user_id",
        "why": "SQL injection—unvalidated user input in query"
    },
    "high": {
        "example": "if (count > 0) return results[count];  # array bounds error",
        "why": "Off-by-one accesses beyond array length"
    },
    "medium": {
        "example": "Parse JSON without handling malformed input",
        "why": "Exception not caught; API could crash"
    }
}
```

#### Improving Existing High False-Positive Categories

```python
def improve_false_positive_category():
    """
    When a category has high dismissal rate:
    1. Temporarily disable it
    2. Refine the criteria with concrete examples
    3. Re-enable with improved definition
    """

    # Step 1: Recognize high false positive pattern
    # (Developers dismiss 60% of "memory_leak" findings)

    # Step 2: Replace vague category with specific subcategories
    improved_criteria = {
        "skip_these": [
            "Static variables with program lifetime",
            "Memory freed by OS at process exit",
            "Connection pooling where pool manager handles cleanup"
        ],
        "report_these": [
            "Loop: new Connection() without close() in finally block",
            "Callback: registered listener never unregistered",
            "Stream: open file handle without explicit close"
        ]
    }

    # Step 3: Add detection logic examples
    detection_examples = [
        {
            "code": "for item in items: conn = db.connect(); conn.query()",
            "category": "REPORT - connection opened in loop, never closed",
            "fix": "Use context manager: with db.connect() as conn:"
        },
        {
            "code": "static Logger logger = Logger.getLogger();",
            "category": "SKIP - static variable with program lifetime",
            "reason": "Logger remains valid entire program execution"
        }
    ]

    return improved_criteria, detection_examples
```

#### Exam Focus Points

**Remember these distinctions:**
1. **Explicit criteria** = what to report vs. skip (categorical)
2. **Confidence-based filtering** = doesn't improve precision (TRAP)
3. **"Be conservative"** = vague, ineffective (TRAP)
4. **False positive cascades** = dismissal in one category reduces trust in others
5. **Concrete examples** = make criteria testable and unambiguous

---

## Task 4.2: Apply Few-Shot Prompting

### Core Concept: Few-Shot Examples as Gold Standard

Few-shot prompting is the **most reliable technique** for achieving consistent, formatted, actionable output when detailed instructions alone fail.

#### Why Few-Shot Works

```python
# ❌ Instruction alone - produces inconsistent results
instruction_only = """
Extract security issues and format as [SEVERITY] Location: Description.
For SQL injection, explain the vulnerability.
"""
# Results: Sometimes "WARNING sql_injection in line 42: ...", sometimes "CRITICAL, line 42, SQL injection because..."

# ✅ Few-shot example + instruction - consistent, actionable output
few_shot_pattern = """
Extract security issues. Format examples:

EXAMPLE 1 (SQL Injection - Critical):
Query: "SELECT * FROM users WHERE id = " + request.user_id
Finding: [CRITICAL] line 42: SQL Injection - unvalidated user_id directly concatenated
Explanation: Attacker can inject SQL: id=1' OR '1'='1
Suggested fix: Use parameterized query: execute("SELECT * FROM users WHERE id = ?", [user_id])

EXAMPLE 2 (Missing CSRF token - High):
<form action="/delete_account">
Finding: [HIGH] line 156: Missing CSRF token in form
Explanation: POST request accepts user action without verification
Suggested fix: Add <input type="hidden" name="csrf_token" value="{token}">

EXAMPLE 3 (Hardcoded API key - Critical):
api_key = "sk_live_abcd1234efgh5678"
Finding: [CRITICAL] line 23: Hardcoded API key exposed in source
Explanation: Key visible in repo; attackers can impersonate service
Suggested fix: Use environment variable: api_key = os.environ["API_KEY"]

Now extract findings from the provided code:
"""
```

#### Few-Shot for Ambiguous Cases

Few-shot examples are most powerful when they demonstrate judgment calls:

```python
def ambiguous_case_examples():
    """
    Few-shot examples showing how to handle edge cases.
    These generalize to novel patterns.
    """

    examples = [
        {
            "input": "Tool: write_file, Tool: append_file, Tool: create_directory, Tool: read_file. User asks: 'Make a backup of my config'",
            "reasoning": "Create backup = read existing file, then write with .bak extension. Write_file is correct, not append_file.",
            "output": "Tool: read_file(config.json) → write_file(config.json.bak, contents)"
        },
        {
            "input": "Tool: write_file, Tool: append_file. User asks: 'Add a debug log line to my startup script'",
            "reasoning": "Adding to existing file = append_file, not write_file (which would overwrite).",
            "output": "Tool: append_file(startup.sh, '\\necho DEBUG: Starting...')"
        },
        {
            "input": "Tool: summarize, Tool: rewrite, Tool: extract_bullets. User asks: 'What are the main points of this article?'",
            "reasoning": "Main points could be summary or bullets. For lists of distinct points, extract_bullets better than prose. Summarize = narrative form.",
            "output": "Tool: extract_bullets (preserves distinct points)"
        }
    ]

    return examples
```

#### Few-Shot for Format Consistency

```python
def format_consistency_examples():
    """
    Few-shot examples demonstrating exact output format.
    """

    prompt = """
Extract findings from code review. Each finding must follow this exact format:

Finding 1:
Location: path/file.py, lines 45-48
Issue: Logic error - loop condition wrong
Severity: HIGH
Code: for i in range(len(items)-1):  # off-by-one error
Explanation: Should be range(len(items)) to include last element
Suggested fix: Remove the "-1"
Confidence: HIGH

Finding 2:
Location: path/utils.py, line 12
Issue: Security - unvalidated input
Severity: CRITICAL
Code: user_id = request.args.get('id')
       query = f"SELECT * FROM users WHERE id = {user_id}"
Explanation: User input directly in SQL; allows injection
Suggested fix: Use parameterized query with placeholders
Confidence: CRITICAL

---
Now review this code and extract findings in the same format:
[CODE HERE]
"""
    return prompt
```

#### Few-Shot for Reducing False Positives

```python
def reduce_false_positives_pattern():
    """
    Few-shot examples showing acceptable patterns vs. genuine issues.
    Reduces false positives while enabling generalization.
    """

    prompt = """
Review for security issues. Skip acceptable patterns; report only genuine risks.

ACCEPTABLE PATTERN (skip):
Pattern: result = users[user_id]
Context: user_id is validated by database query; integer only, range 0-1000
Decision: SKIP - validation ensures safe access

GENUINE ISSUE (report):
Pattern: result = users[request.args.get('id')]
Context: request.args is unvalidated user input, string
Decision: REPORT - no validation; could contain non-integer, negative, or index-out-of-bounds values

ACCEPTABLE PATTERN (skip):
Pattern: HTML: <script src="jquery-3.6.0.min.js"></script>
Context: Well-known library from CDN; has integrity hash verification
Decision: SKIP - integrity hash prevents tampering

GENUINE ISSUE (report):
Pattern: HTML: <script src="http://cdn.example.com/utils.js"></script>
Context: Unclear origin; loaded over HTTP not HTTPS
Decision: REPORT - no integrity check; http allows MITM injection

---
Apply this reasoning to review the code below:
"""
    return prompt
```

#### Few-Shot for Document Format Variation

```python
def varied_document_format_examples():
    """
    Few-shot handling of varied document structures.
    Addresses inconsistent citation formats, methodology placement, etc.
    """

    prompt = """
Extract citations from research papers. Format varies by paper.

DOCUMENT TYPE 1 (Inline citations):
Text: "Studies show benefits [42]. The meta-analysis concluded X [42] [15]."
Extraction:
  - Citation ID 42: "benefits", "meta-analysis concluded X"
  - Citation ID 15: "meta-analysis concluded X"

DOCUMENT TYPE 2 (Footnotes):
Text: "The experiment was conducted[1] with controls[2]."
Footnote 1: "Smith et al., 2020"
Footnote 2: "Randomized, n=500"
Extraction:
  - "Smith et al., 2020": "experiment was conducted"
  - "Randomized, n=500": "with controls"

DOCUMENT TYPE 3 (Bibliography references):
Text: "As per the literature review section."
[Later] Bibliography: "1. Jones (2021) - Analysis methodology"
Extraction: Link section reference to bibliography entry

---
Extract citations from this document, handling varied formats:
"""
    return prompt
```

#### Exam Focus Points

**Critical few-shot concepts:**
1. **2-4 targeted examples** is optimal (diminishing returns beyond 4)
2. **Few-shot > detailed instructions** when dealing with edge cases
3. **Generalization** - examples should cover ambiguous patterns the model will encounter
4. **Format examples** must show exact output structure
5. **Reasoning** - include "why this action" not just the action
6. **Distinguishing** acceptable from unacceptable patterns is key
7. **Varied formats** require examples showing different structures

---

## Task 4.3: Enforce Structured Output

### Core Concept: Tool Use + JSON Schemas = Guaranteed Compliance

Tool use with JSON schemas is the **only reliable way** to guarantee schema-compliant structured output, eliminating JSON syntax errors.

#### Tool Use Fundamentals

```python
import anthropic
import json

def tool_use_structured_output():
    """
    Using tool_use to enforce structured output.
    """
    client = anthropic.Anthropic()

    # Define the extraction tool with schema
    tools = [
        {
            "name": "extract_security_findings",
            "description": "Extract security findings from code",
            "input_schema": {
                "type": "object",
                "properties": {
                    "findings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "File path and line number"
                                },
                                "issue_type": {
                                    "type": "string",
                                    "enum": ["SQL_INJECTION", "XSS", "AUTH_BYPASS", "OTHER"],
                                    "description": "Category of security issue"
                                },
                                "severity": {
                                    "type": "string",
                                    "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                                    "description": "Issue severity"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Detailed explanation of vulnerability"
                                },
                                "suggested_fix": {
                                    "type": "string",
                                    "description": "How to remediate"
                                }
                            },
                            "required": ["location", "issue_type", "severity", "description"]
                        },
                        "description": "List of security findings"
                    }
                },
                "required": ["findings"]
            }
        }
    ]

    # Make request with tool_choice: "any"
    # (guarantees tool is called, model chooses which tool)
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        tools=tools,
        tool_choice="any",  # ✅ GUARANTEES a tool will be called
        messages=[
            {
                "role": "user",
                "content": "Review this code for security issues:\n" + code_sample
            }
        ]
    )

    # Extract tool use block
    for block in response.content:
        if block.type == "tool_use":
            findings = block.input  # Already validated against schema
            return findings

    return None
```

#### Tool Choice Options

```python
def tool_choice_patterns():
    """
    Three tool_choice settings with different guarantees.
    """

    patterns = {
        "auto": {
            "meaning": "Model may return text or call tool",
            "use_case": "Optional extraction (user might ask for text description)",
            "guarantee": "NONE - might get text instead of structured output",
            "example": 'tool_choice="auto"'
        },
        "any": {
            "meaning": "Model MUST call a tool, can choose which one",
            "use_case": "Unknown document type, multiple extraction tools",
            "guarantee": "✅ STRUCTURED OUTPUT - but might pick wrong tool",
            "example": 'tool_choice="any"'
        },
        "forced": {
            "meaning": "Model MUST call this specific tool",
            "use_case": "Single extraction format, two-stage pipeline",
            "guarantee": "✅ STRUCTURED OUTPUT - enforces specific schema",
            "example": 'tool_choice={"type": "tool", "name": "extract_invoice"}'
        }
    }

    return patterns

# ✅ CORRECT: Guarantees extraction with specific format
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    tools=extraction_tools,
    tool_choice={"type": "tool", "name": "extract_invoice"},  # Force this tool
    messages=[...]
)

# ❌ WRONG: Might return text, not structured output
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    tools=extraction_tools,
    tool_choice="auto",  # Model might skip tool entirely
    messages=[...]
)
```

#### Schema Design: Required vs. Optional Fields

```python
def schema_design_patterns():
    """
    When to use required vs. optional fields.
    Key principle: Only mark as required if all documents will have it.
    """

    # ✅ CORRECT: Optional for fields that may not exist in source
    invoice_schema = {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": ["string", "null"],
                "description": "Invoice ID if present in document"
            },
            "vendor_name": {
                "type": ["string", "null"],
                "description": "Vendor/seller name if present"
            },
            "total_amount": {
                "type": ["number", "null"],
                "description": "Total cost if explicitly stated"
            },
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit_price": {"type": "number"},
                        "notes": {"type": ["string", "null"]}  # Optional
                    },
                    "required": ["description", "quantity", "unit_price"]
                }
            }
        },
        "required": ["line_items"]  # Only require items that will always exist
    }

    # ❌ WRONG: Marking everything required causes fabrication
    # When "invoice_number" is required but missing, model makes up values

    return invoice_schema
```

#### Extensible Categories with "Other"

```python
def extensible_category_pattern():
    """
    Enum fields with "other" + detail string for flexibility.
    """

    schema = {
        "type": "object",
        "properties": {
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "issue_type": {
                            "type": "string",
                            "enum": [
                                "SQL_INJECTION",
                                "XSS",
                                "CSRF",
                                "AUTH_BYPASS",
                                "OTHER"  # ✅ Extensible category
                            ]
                        },
                        "issue_detail": {
                            "type": ["string", "null"],
                            "description": "If issue_type is OTHER, provide specific issue type here"
                        },
                        "severity": {
                            "type": "string",
                            "enum": [
                                "CRITICAL",
                                "HIGH",
                                "MEDIUM",
                                "LOW",
                                "UNCLEAR"  # ✅ For ambiguous cases
                            ]
                        },
                        "severity_reasoning": {
                            "type": ["string", "null"],
                            "description": "If severity is UNCLEAR, explain why"
                        }
                    },
                    "required": ["issue_type", "severity"]
                }
            }
        }
    }

    return schema
```

#### Format Normalization Rules

```python
def format_normalization_in_prompt():
    """
    Include format normalization rules alongside schemas
    to handle inconsistent source formatting.
    """

    prompt = """
Extract structured data from receipt.

SCHEMA REQUIREMENTS:
- All amounts must be numbers (no $ or commas)
- Dates must be YYYY-MM-DD format
- Quantities must be integers

FORMAT NORMALIZATION RULES:
- If amount is "$1,234.50", extract as 1234.50
- If date is "Jan 15, 2024", convert to "2024-01-15"
- If quantity is "Qty: 5 units", extract 5 as integer

Example:
Source: "Total: $1,234.50"
Normalized: {"amount": 1234.50}

Source: "Purchase Date: March 22, 2026"
Normalized: {"date": "2026-03-22"}

Now extract from this receipt:
[RECEIPT TEXT]
"""
    return prompt
```

#### Exam Focus Points

**Tool use + schema essentials:**
1. **Tool use = syntactically guaranteed** structured output
2. **tool_choice="auto"** doesn't guarantee tool use (TRAP)
3. **tool_choice="any"** guarantees tool, model chooses which
4. **Forced tool** guarantees specific tool and schema
5. **Optional fields** = use null types, not required array
6. **"Other" + detail** pattern handles extensions
7. **Schemas don't prevent semantic errors** (numbers don't sum, wrong field values)
8. **Normalization rules in prompt** handle format variations

---

## Task 4.4: Implement Validation, Retry, and Feedback Loops

### Core Concept: Validation Errors Guide Retry, But Missing Data Won't

Validation loops catch **semantic errors** (structure, consistency) that schemas don't. However, retries are ineffective when required information is absent from the source document.

#### Retry-with-Error-Feedback Pattern

```python
def retry_with_error_feedback():
    """
    Core pattern: validate extraction, provide specific errors on retry.
    """
    client = anthropic.Anthropic()

    def extract_with_retry(document: str, max_retries: int = 2) -> dict:
        """
        Extract data with automatic retry on validation failures.
        """

        extraction_tool = {
            "name": "extract_invoice",
            "description": "Extract invoice data",
            "input_schema": {
                "type": "object",
                "properties": {
                    "invoice_number": {"type": ["string", "null"]},
                    "date": {"type": ["string", "null"]},
                    "line_items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "quantity": {"type": "number"},
                                "unit_price": {"type": "number"},
                                "line_total": {"type": "number"}
                            },
                            "required": ["description", "quantity", "unit_price"]
                        }
                    },
                    "total": {"type": ["number", "null"]}
                }
            }
        }

        messages = [
            {
                "role": "user",
                "content": f"Extract invoice data from this document:\n{document}"
            }
        ]

        for attempt in range(max_retries + 1):
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                tools=[extraction_tool],
                tool_choice={"type": "tool", "name": "extract_invoice"},
                messages=messages
            )

            # Extract the tool use block
            extraction = None
            for block in response.content:
                if block.type == "tool_use":
                    extraction = block.input
                    break

            if not extraction:
                continue

            # Validate semantic correctness
            validation_errors = validate_extraction(extraction)

            if not validation_errors:
                return extraction  # ✅ Valid, return

            if attempt < max_retries:
                # Append validation error to messages for retry
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                messages.append({
                    "role": "user",
                    "content": f"""The extraction has validation errors. Please correct them:

{format_validation_errors(validation_errors)}

Original document:
{document}

Retry the extraction, fixing these specific errors."""
                })
            else:
                # Final attempt, return with errors
                return {"extraction": extraction, "validation_errors": validation_errors}

        return None

    return extract_with_retry
```

#### Validation Error Types

```python
def validate_extraction(extraction: dict) -> list:
    """
    Identify semantic validation errors.
    """
    errors = []

    # Structural validation
    if extraction.get("line_items") is None:
        errors.append("STRUCTURE: line_items array is missing")

    # Consistency validation
    if extraction.get("line_items"):
        calculated_total = sum(
            item.get("quantity", 0) * item.get("unit_price", 0)
            for item in extraction["line_items"]
        )
        stated_total = extraction.get("total")

        if stated_total is not None and abs(calculated_total - stated_total) > 0.01:
            errors.append(
                f"CONSISTENCY: Line items sum to {calculated_total:.2f} "
                f"but stated total is {stated_total:.2f}"
            )

    # Field value validation
    if extraction.get("date"):
        if not is_valid_date(extraction["date"]):
            errors.append(f"FORMAT: Date '{extraction['date']}' is not valid ISO format")

    # Range validation
    if extraction.get("quantity") and extraction["quantity"] < 0:
        errors.append("RANGE: Quantity cannot be negative")

    return errors

def format_validation_errors(errors: list) -> str:
    """
    Format errors for clear presentation in retry prompt.
    """
    return "\n".join(f"- {error}" for error in errors)
```

#### When Retries Work vs. Don't Work

```python
def retry_effectiveness_analysis():
    """
    Understanding when retries succeed or fail.
    """

    scenarios = {
        "RETRY WILL SUCCEED": [
            {
                "case": "Line items sum incorrect",
                "reason": "Information exists in document; model just formatted wrong",
                "example": "Items: $10 + $20 = $30, but model extracted total as $50",
                "retry": "Provide extracted data + error 'total should be 30' → model recalculates"
            },
            {
                "case": "Date format inconsistent",
                "reason": "Date exists in document; just needs reformatting",
                "example": "Source: 'March 22, 2026', extracted: '22/03/2026', needed: '2026-03-22'",
                "retry": "Provide format rule + extracted date → model converts"
            },
            {
                "case": "Enum value wrong category",
                "reason": "Item exists; model just chose wrong category",
                "example": "Severity: source clearly says CRITICAL, model extracted HIGH",
                "retry": "Point out: 'This is clearly critical, not high. Reason: [quote source]'"
            }
        ],
        "RETRY WILL FAIL": [
            {
                "case": "Information missing from source",
                "reason": "Can't extract what doesn't exist",
                "example": "Trying to extract 'invoice_date' from document with no date",
                "retry": "Retrying won't help; information simply not in document"
            },
            {
                "case": "Document is outside context",
                "reason": "Retry can't access external references",
                "example": "Source says 'see appendix B', appendix B not provided",
                "retry": "Would need to provide appendix B to extract data"
            },
            {
                "case": "Conflicting source information",
                "reason": "Retry can't resolve conflicts model didn't create",
                "example": "Document says invoice_date='March 22' in header, 'April 15' in footer",
                "retry": "Model can report conflict but can't resolve without guidance"
            }
        ]
    }

    return scenarios
```

#### Multi-Pass Validation with Confidence

```python
def validation_with_confidence_calibration():
    """
    Extract with confidence scores to enable calibrated review routing.
    """

    schema = {
        "type": "object",
        "properties": {
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "issue": {"type": "string"},
                        "severity": {
                            "type": "string",
                            "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
                        },
                        "confidence": {
                            "type": "string",
                            "enum": ["HIGH", "MEDIUM", "LOW"],
                            "description": "How confident is the model in this finding"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Why this confidence level"
                        }
                    },
                    "required": ["location", "issue", "severity", "confidence"]
                }
            }
        }
    }

    # Use confidence for routing:
    # - HIGH confidence → auto-approve
    # - MEDIUM confidence → human review
    # - LOW confidence → require evidence or skip

    return schema
```

#### Tracking Detected Patterns for Analysis

```python
def pattern_tracking_for_analysis():
    """
    Add detected_pattern field to enable systematic analysis
    of false positive patterns when developers dismiss findings.
    """

    extraction_with_patterns = {
        "findings": [
            {
                "location": "auth.py:45",
                "issue": "Unvalidated input in SQL query",
                "severity": "CRITICAL",
                "detected_pattern": "f-string concatenation in query",
                "code_sample": "query = f'SELECT * FROM users WHERE id = {user_id}'",
                "confidence": "HIGH"
            },
            {
                "location": "utils.py:12",
                "issue": "Unused variable assignment",
                "severity": "LOW",
                "detected_pattern": "variable assigned but never read",
                "code_sample": "x = some_function()",
                "confidence": "MEDIUM"
            }
        ]
    }

    # Analysis: Track which patterns developers dismiss
    # If they dismiss 60% of "unused_variable" findings, pattern is unreliable
    # If they dismiss 10% of "SQL_concat" findings, pattern is reliable

    return extraction_with_patterns
```

#### Exam Focus Points

**Validation loop essentials:**
1. **Retry-with-error-feedback** = append specific errors to prompt
2. **Semantic validation** = catches errors schemas miss (sums, consistency)
3. **Schema validation** = syntax only (caught by tool use)
4. **Retries work when** = information exists but formatting/categorization wrong
5. **Retries fail when** = information doesn't exist in source
6. **Confidence fields** enable routing (high=auto, medium=review, low=skip)
7. **detected_pattern** field enables dismissal analysis
8. **conflict_detected** boolean for inconsistent source data

---

## Task 4.5: Design Efficient Batch Processing Strategies

### Core Concept: Right Tool for Right Workflow

Batch API is for cost-effective, latency-tolerant workflows. Synchronous API for latency-critical operations.

#### Message Batches API Fundamentals

```python
import anthropic
import json
from datetime import datetime

def batch_processing_guide():
    """
    Complete guide to Message Batches API.
    """

    api_details = {
        "cost_savings": "50% reduction",
        "processing_window": "Up to 24 hours",
        "latency_sla": "No guaranteed SLA (can take full 24 hours)",
        "multi_turn_limitation": "No multi-turn tool calling within single request",
        "use_case": "Latency-tolerant batch work (overnight reports, weekly audits)",
        "anti_use_case": "Blocking workflows (pre-merge checks, user-facing APIs)"
    }

    return api_details

def batch_api_workflow():
    """
    Complete batch API workflow example.
    """
    client = anthropic.Anthropic()

    # Step 1: Create batch requests
    batch_requests = [
        {
            "custom_id": "doc_001",
            "params": {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": "Review this code for security issues:\n[CODE1]"
                    }
                ]
            }
        },
        {
            "custom_id": "doc_002",
            "params": {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": "Review this code for security issues:\n[CODE2]"
                    }
                ]
            }
        }
    ]

    # Step 2: Submit batch
    batch = client.beta.messages.batches.create(
        requests=batch_requests,
        betas=["batch-2024-07-15"]
    )

    batch_id = batch.id
    print(f"Submitted batch: {batch_id}")

    # Step 3: Poll for completion (in practice, check periodically)
    import time
    while True:
        batch_status = client.beta.messages.batches.retrieve(
            batch_id,
            betas=["batch-2024-07-15"]
        )

        if batch_status.processing_status == "ended":
            break

        print(f"Status: {batch_status.processing_status}")
        time.sleep(30)

    # Step 4: Process results
    results = {}
    for result in batch_status.request_results:
        custom_id = result.custom_id
        message = result.result.message
        results[custom_id] = message.content[0].text

    return results

def batch_vs_synchronous_choice():
    """
    Decision matrix: when to use batch API vs. synchronous API.
    """

    decision_matrix = {
        "Use SYNCHRONOUS API when": [
            "User is waiting (pre-merge check, IDE suggestion)",
            "SLA < 10 minutes required",
            "Workflow is interactive",
            "Multi-turn tool calling needed (tool calls with results)",
            "Cost is less important than latency"
        ],
        "Use BATCH API when": [
            "No immediate user wait (overnight report, scheduled scan)",
            "SLA measured in hours or next business day",
            "Processing 100+ documents",
            "Cost savings (50% reduction) matters",
            "Can delay results up to 24 hours"
        ]
    }

    return decision_matrix
```

#### Handling Batch Failures

```python
def batch_failure_handling():
    """
    Strategy for resubmitting failed documents.
    """

    def process_batch_results(batch_status, original_requests):
        """
        Identify failures and prepare resubmission.
        """
        failed_requests = []
        successful_results = {}

        # Map custom_id to original request for retries
        request_map = {req["custom_id"]: req for req in original_requests}

        for result in batch_status.request_results:
            custom_id = result.custom_id

            if result.result.type == "succeeded":
                successful_results[custom_id] = result.result.message
            elif result.result.type == "expired":
                # Retry with original request
                failed_requests.append(request_map[custom_id])
            elif result.result.type == "errored":
                error = result.result.error

                # Strategy: identify error type and adjust request
                if "context_length_exceeded" in str(error):
                    # Document too long: chunk it
                    chunked_requests = chunk_request(request_map[custom_id])
                    failed_requests.extend(chunked_requests)
                elif "overloaded" in str(error):
                    # Retry unmodified (temporary issue)
                    failed_requests.append(request_map[custom_id])
                else:
                    # Log for manual review
                    print(f"Unrecoverable error for {custom_id}: {error}")

        return successful_results, failed_requests

    def chunk_request(request: dict) -> list:
        """
        Split large document into chunks if it exceeds context limit.
        """
        # Extract content from request
        messages = request["params"]["messages"]
        content = messages[0]["content"]

        # Split by newlines or sentences
        chunks = split_document(content)

        # Create separate request for each chunk
        chunked_requests = []
        for i, chunk in enumerate(chunks):
            chunked_requests.append({
                "custom_id": f"{request['custom_id']}_chunk_{i}",
                "params": {
                    "model": request["params"]["model"],
                    "max_tokens": request["params"]["max_tokens"],
                    "messages": [
                        {
                            "role": "user",
                            "content": chunk
                        }
                    ]
                }
            })

        return chunked_requests

    return process_batch_results, chunk_request
```

#### Batch Submission Frequency Strategy

```python
def batch_submission_frequency():
    """
    Calculate submission frequency based on SLA requirements.
    """

    scenario = {
        "requirement": "Guarantee 30-hour SLA with 24-hour batch processing",
        "calculation": "4-hour submission windows",
        "reasoning": """
        - Batch takes up to 24 hours
        - Need 30-hour SLA maximum
        - Maximum wait time = 30 hours - 24 hours = 6 hours
        - To guarantee worst-case (just missed window), submit every 4 hours
        - With 4-hour windows: submit at 00:00, 04:00, 08:00, 12:00, 16:00, 20:00
        - Latest document enters system within 4 hours
        - Worst case: 4 hours wait + 24 hours processing = 28 hours (meets SLA)
        """
    }

    # More granular frequency for tighter SLA
    sla_calculations = {
        "SLA 6 hours": {
            "batch_processing": "24 hours",
            "note": "Not achievable with batch API (incompatible)"
        },
        "SLA 30 hours": {
            "batch_processing": "24 hours",
            "submission_window": "4 hours",
            "reasoning": "4 hour delay + 24 hour processing = 28 hours max"
        },
        "SLA 48 hours": {
            "batch_processing": "24 hours",
            "submission_window": "12 hours",
            "reasoning": "12 hour delay + 24 hour processing = 36 hours max"
        }
    }

    return sla_calculations
```

#### Prompt Refinement Before Batch Processing

```python
def batch_refinement_strategy():
    """
    Refine prompts on sample set before batch-processing volumes.
    Maximizes first-pass success and reduces resubmission costs.
    """

    workflow = """
    PHASE 1: Sample Refinement (synchronous API)
    - Select 5-10 representative documents from batch
    - Test with initial prompt
    - Analyze failures and iterate prompt
    - Track: success rate, error types, output quality

    Metrics to track:
    - Schema compliance: 95%+ (target)
    - Semantic validation: 95%+ (target)
    - Format consistency: 100% (required)

    When to iterate:
    - < 90% success: Major prompt issues
    - 90-95% success: Minor refinements needed
    - > 95% success: Ready for batch

    PHASE 2: Batch Submission
    - Submit full batch with refined prompt
    - Monitor processing
    - Plan for resubmission of failures

    PHASE 3: Resubmission Strategy
    - Failures due to document issues: modify request (chunk, etc)
    - Failures due to prompt issues: apply learned refinements
    - Estimate cost: 50% savings even with resubmissions
    """

    return workflow
```

#### Exam Focus Points

**Batch processing essentials:**
1. **50% cost savings** - major advantage
2. **24-hour window** - not guaranteed SLA
3. **Inappropriate for blocking workflows** (pre-merge checks, APIs)
4. **No multi-turn tool calling** within single request
5. **custom_id fields** correlate requests/responses
6. **Failure handling** - resubmit with modifications
7. **Submission frequency** = based on SLA requirements
8. **Sample refinement first** = maximize batch success rate

---

## Task 4.6: Design Multi-Instance & Multi-Pass Review Architectures

### Core Concept: Independent Review Catches What Self-Review Misses

Self-review is limited because the model retains reasoning context from generation. Independent instances provide fresh perspective and catch subtle issues.

#### Self-Review Limitations

```python
def self_review_limitations():
    """
    Why self-review is less effective than independent review.
    """

    limitations = {
        "reasoning_context_retention": {
            "problem": "Model retains generation reasoning when reviewing same output",
            "example": """
            Generation: Model writes code with subtle off-by-one error
            Reasoning: "Loop from 0 to len(array)-1 is correct"
            Self-review: Sees same code, remembers reasoning, doesn't question it

            Independent review: No prior reasoning; spots: "Why -1? That's off-by-one"
            """,
            "solution": "Use second independent instance"
        },
        "confirmation_bias": {
            "problem": "Model less likely to find fault in its own decisions",
            "example": "Model generated: 'This API pattern is correct' → reviews own code → 'I was right'",
            "solution": "Independent reviewer without generation context"
        },
        "decision_reinforcement": {
            "problem": "Having committed to decision makes model reluctant to contradict itself",
            "example": "Model: 'I chose Algorithm A for reason X' → later 'Algorithm A still seems right'",
            "solution": "Fresh instance sees Algorithm B might be better"
        }
    }

    return limitations
```

#### Multi-Instance Architecture Pattern

```python
import anthropic
import json

def multi_instance_independent_review():
    """
    Two-instance architecture: generator + independent reviewer.
    """

    # INSTANCE 1: Code Generator
    generator = anthropic.Anthropic()

    # INSTANCE 2: Independent Reviewer (separate conversation)
    reviewer = anthropic.Anthropic()

    def generate_and_review(requirements: str):
        """
        Generate code with one instance, review with independent instance.
        """

        # ✅ PHASE 1: Code Generation
        generation_response = generator.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"Write Python code for: {requirements}"
                }
            ]
        )

        generated_code = generation_response.content[0].text

        # ❌ DON'T do this: Same instance reviewing own work
        # generation_response = generator.messages.create(
        #     model="claude-3-5-sonnet-20241022",
        #     messages=[..., {"role": "assistant", "content": generated_code}]
        # )

        # ✅ DO this: Independent instance, no generation context
        review_response = reviewer.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"""Review this code for issues WITHOUT considering any generation decisions.
Look for:
- Logic errors
- Edge cases
- Performance problems
- Security issues

Code to review:
{generated_code}"""
                }
            ]
        )

        review_feedback = review_response.content[0].text

        return {
            "code": generated_code,
            "review": review_feedback
        }

    return generate_and_review
```

#### Multi-Pass Review Architecture

```python
def multi_pass_review_architecture():
    """
    Split large multi-file reviews into focused passes.
    Prevents attention dilution and contradictory findings.
    """

    review_strategy = {
        "problem": """
        Reviewing 10 files simultaneously:
        - Model attention dilutes across all files
        - Cross-file context is large, reduces depth of local analysis
        - Might find issue in file A, miss same pattern in file B
        - Contradictory findings across files
        """,

        "solution": "Multi-pass architecture with specialized focus"
    }

    # PASS 1: Per-file local analysis (independent of other files)
    pass_1_config = {
        "name": "Local Security Review",
        "focus": "Security issues within single file",
        "prompt": """Review ONLY this file for security issues.
        Ignore cross-file data flow.
        Check: input validation, auth, SQL injection, XSS.

        File: {file}""",
        "output": "File-local security findings"
    }

    # PASS 2: Cross-file integration analysis (focused on interactions)
    pass_2_config = {
        "name": "Cross-File Data Flow Review",
        "focus": "Data flow and interactions between files",
        "prompt": """Given the security findings from local review,
        analyze cross-file data flow:
        - Does untrusted data flow from input handlers to DB?
        - Are validation boundaries crossed?
        - Do findings in file A affect assumptions in file B?

        Files: [list provided]
        Local findings from Pass 1: [structured findings]""",
        "input": "All files + local findings from Pass 1",
        "output": "Integration issues, contradictions, data flow violations"
    }

    # PASS 3: Verification (optional)
    pass_3_config = {
        "name": "Verification & Confidence Assessment",
        "focus": "Double-check findings, assess confidence",
        "prompt": """Review findings from Passes 1-2.
        For each finding:
        - Verify it's a genuine issue (not false positive)
        - Assess confidence: HIGH/MEDIUM/LOW
        - Provide reasoning

        Findings to verify: [structured list from Pass 2]""",
        "output": "Verified findings with confidence scores"
    }

    passes = [pass_1_config, pass_2_config, pass_3_config]

    return review_strategy, passes
```

#### Multi-Pass Implementation

```python
def implement_multi_pass_review():
    """
    Concrete implementation of multi-pass architecture.
    """
    client = anthropic.Anthropic()

    def multi_pass_code_review(files_dict: dict) -> dict:
        """
        Review multiple files with multi-pass architecture.
        files_dict = {"file1.py": code1, "file2.py": code2, ...}
        """

        # PASS 1: Per-file local analysis
        local_findings = {}
        for filename, code in files_dict.items():
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Review this file for security issues, logic bugs, and performance problems.
Focus on issues WITHIN this file only. Don't consider cross-file interactions.

File: {filename}

{code}

Provide findings in JSON format:
{{
    "findings": [
        {{
            "location": "line number",
            "issue": "description",
            "severity": "CRITICAL|HIGH|MEDIUM|LOW",
            "category": "SECURITY|LOGIC|PERFORMANCE|OTHER"
        }}
    ]
}}"""
                    }
                ]
            )

            # Parse findings
            findings_text = response.content[0].text
            local_findings[filename] = findings_text

        # PASS 2: Cross-file integration analysis
        integration_response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze cross-file data flow and interactions.

Files and their local findings:
{json.dumps(local_findings, indent=2)}

Files:
{json.dumps(files_dict, indent=2)}

Look for:
- Data flow from untrusted input (in one file) to security boundary (in another)
- Validation bypasses across file boundaries
- Contradictory findings or assumptions

Provide integration findings in JSON format:
{{
    "integration_findings": [
        {{
            "files_involved": ["file1", "file2"],
            "issue": "Cross-file issue description",
            "severity": "CRITICAL|HIGH|MEDIUM"
        }}
    ]
}}"""
                }
            ]
        )

        integration_findings = integration_response.content[0].text

        # PASS 3: Verification with confidence
        verification_response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""Verify and assess confidence in these findings:

Local findings:
{local_findings}

Integration findings:
{integration_findings}

For each finding, provide:
- Is this a genuine issue? (YES/NO)
- Confidence: HIGH/MEDIUM/LOW
- Reasoning

Respond in JSON format:
{{
    "verified_findings": [
        {{
            "original_finding": "...",
            "is_genuine": true,
            "confidence": "HIGH|MEDIUM|LOW",
            "reasoning": "..."
        }}
    ]
}}"""
                }
            ]
        )

        verified_findings = verification_response.content[0].text

        return {
            "pass_1_local": local_findings,
            "pass_2_integration": integration_findings,
            "pass_3_verification": verified_findings
        }

    return multi_pass_code_review
```

#### Confidence-Calibrated Review Routing

```python
def confidence_calibrated_routing():
    """
    Use self-reported confidence to route findings appropriately.
    """

    routing_logic = {
        "HIGH_confidence": {
            "action": "Auto-approve / Auto-commit",
            "reasoning": "Model has high confidence and explicit evidence",
            "developer_review": "Not required"
        },
        "MEDIUM_confidence": {
            "action": "Human review queue",
            "reasoning": "Needs judgment call; human can verify",
            "developer_review": "Required"
        },
        "LOW_confidence": {
            "action": "Skip or require evidence",
            "reasoning": "Model uncertain; requires explicit evidence",
            "developer_review": "Required; ask for clarification"
        }
    }

    # Implementation
    def route_finding(finding: dict) -> str:
        """
        Route finding based on confidence level.
        """
        confidence = finding.get("confidence", "MEDIUM")

        if confidence == "HIGH":
            return "auto_approve"
        elif confidence == "MEDIUM":
            return "human_review"
        else:
            return "skip_unless_justified"

    return routing_logic, route_finding
```

#### Exam Focus Points

**Multi-instance & multi-pass essentials:**
1. **Self-review limitation** = model retains generation reasoning
2. **Independent review** = fresh instance, no prior context
3. **Multi-pass** = splits large reviews into focused passes
4. **Pass 1** = per-file local analysis (local scope)
5. **Pass 2** = cross-file integration (interactions)
6. **Pass 3** = verification with confidence (optional)
7. **Confidence calibration** = route HIGH auto, MEDIUM human, LOW skip
8. **Attention dilution** = multi-pass prevents with focused scope

---

## Key Concepts & Memory Items

### Critical Distinctions (Exam Trap Topics)

| Concept | What Works | What Doesn't Work | Exam Implication |
|---------|-----------|-------------------|------------------|
| **Precision** | Explicit categorical criteria | "Be conservative" instructions | Specific categories beat confidence-based filtering |
| **Consistency** | Few-shot examples (2-4) | Detailed prose instructions | Examples > descriptions |
| **Structured output** | tool_choice="any" or forced tool | tool_choice="auto" | Auto doesn't guarantee tool use |
| **Retry effectiveness** | Format/structural errors | Information missing from source | Retries don't create new data |
| **Batch API** | Latency-tolerant overnight work | Pre-merge checks, user-facing APIs | Wrong tool for wrong job |
| **Review quality** | Independent instances | Self-review on same session | Reasoning context bias |

### Memory Anchors

**4.1 - Explicit Criteria**
- False positives cascade: High FP in category A reduces trust in finding from category A and B
- Solution: Replace vague ("be conservative") with categorical ("report only: logic, security, memory")
- Test: Can you determine if something should be reported WITHOUT model judgment?

**4.2 - Few-Shot Prompting**
- Sweet spot: 2-4 examples (diminishing returns after 4)
- Power: Demonstrates reasoning ("why this tool"), not just action
- Key: Include ambiguous edge cases that generalize

**4.3 - Tool Use + Schemas**
- Schemas guarantee syntax, not semantics (numbers might not sum)
- tool_choice options: "auto" (no guarantee), "any" (some tool), forced (specific tool)
- Optional fields use `null` types, not required arrays

**4.4 - Validation & Retry**
- Validate: semantic errors (sums, consistency) not caught by schemas
- Retry works: Format/categorization errors
- Retry fails: Missing information
- Track: detected_pattern field for dismissal analysis

**4.5 - Batch Processing**
- Use: 50% cost savings, 24-hour window, non-blocking work
- Don't use: Blocking workflows, no multi-turn tool calling
- Frequency: Based on SLA (e.g., 4-hour windows for 30-hour SLA)
- Strategy: Sample refinement before batch submission

**4.6 - Multi-Instance & Multi-Pass**
- Problem: Self-review retains reasoning context
- Solution: Independent instance fresh perspective
- Multi-pass: PASS 1 (local per-file) → PASS 2 (cross-file) → PASS 3 (verify + confidence)

### Exam Question Types

1. **Scenario-based**: "You're building X system. Which approach best..."
   - Answer relies on understanding tradeoffs (explicit criteria vs. confidence, batch vs. sync, independent vs. self-review)

2. **Code-based**: "What's wrong with this prompt/schema/tool_choice?"
   - Look for: vague instructions, missing schemas, wrong tool_choice, missing examples

3. **Architecture-based**: "Design a review system for [description]"
   - Plan: multi-pass, multi-instance, confidence routing, batch if applicable

---

## Exam Traps & Misconceptions

### Trap 1: Confidence-Based Filtering Improves Precision
**False Claim:** "Add instruction: 'only report high-confidence findings' will reduce false positives"

**Reality:** Confidence filtering doesn't change precision because the model doesn't have better information. The issue is ambiguous criteria.

**Solution:** Use explicit categorical criteria instead. "Only report logic bugs where code contradicts comments" works; "only report high-confidence issues" doesn't.

### Trap 2: tool_choice="auto" Guarantees Structured Output
**False Claim:** "Setting tool_choice to 'auto' means I'll get structured output"

**Reality:** "auto" means the model *may* return text instead of calling the tool.

**Correct:** Use tool_choice="any" (guarantees some tool) or forced tool selection.

### Trap 3: Retries Always Fix Extraction Issues
**False Claim:** "If extraction fails, just retry with validation feedback"

**Reality:** Retries only work if the information exists in the source. They can't create data that's not there.

**Solution:** Before retrying, verify information exists in original document. If missing, adjust scope or provide additional documents.

### Trap 4: Batch API Suitable for Pre-Merge Checks
**False Claim:** "Batch API is perfect for pre-merge code review - saves 50% cost!"

**Reality:** Batch has no latency SLA (can take 24 hours). Developers can't wait 24 hours for pre-merge check.

**Correct:** Use synchronous API for blocking workflows, batch for asynchronous (overnight reports, weekly audits).

### Trap 5: Self-Review Instruction Improves Review Quality
**False Claim:** "Adding 'review your own work for mistakes' instruction improves review"

**Reality:** Model retains reasoning from generation. Same reasoning context prevents catching subtle issues.

**Solution:** Use independent instance without prior context for better detection.

### Trap 6: JSON Schemas Prevent All Output Errors
**False Claim:** "Strict JSON schema via tool use guarantees correct output"

**Reality:** Schemas guarantee syntactic correctness but not semantic correctness. Numbers might not sum, values might be in wrong fields.

**Solution:** Add validation logic to check semantic correctness (sums match, required fields populated consistently).

### Trap 7: Vague "Conservative" Instructions Work
**False Claim:** "Instruction 'be conservative and only report high-confidence findings' works as well as explicit criteria"

**Reality:** "Conservative" is subjective. Different reviewers (and different model runs) interpret it differently.

**Solution:** Use explicit criteria like "report only if: actual behavior contradicts stated behavior in comments."

### Trap 8: More Few-Shot Examples Always Better
**False Claim:** "10 few-shot examples better than 2"

**Reality:** Diminishing returns after 4 examples. Too many examples dilute the pattern and waste tokens.

**Solution:** 2-4 targeted examples covering edge cases (ambiguous tool choice, format variations, etc).

---

## Quick Reference Cheatsheet

### Task 4.1 Checklist: Explicit Criteria
- [ ] Criteria are categorical (what to report vs. skip), not confidence-based
- [ ] Each category has concrete code examples
- [ ] False positive categories have high-confidence detection rules
- [ ] Severity has explicit examples (CRITICAL = actual harm, not potential)
- [ ] Instructions are testable (can verify adherence to criteria)

### Task 4.2 Checklist: Few-Shot Prompting
- [ ] 2-4 examples (not 1, not 10)
- [ ] Examples cover edge cases (ambiguous tool choice, varied formats)
- [ ] Each example includes "why" reasoning, not just the action
- [ ] Examples show exact output format
- [ ] Examples distinguish acceptable from unacceptable patterns
- [ ] Different document structures represented

### Task 4.3 Checklist: Structured Output
- [ ] Tool use with JSON schema defined
- [ ] tool_choice is "any" or forced, NOT "auto"
- [ ] Optional fields use `null` type, not required
- [ ] Enums include "other" + detail field
- [ ] Format normalization rules in prompt
- [ ] Schema focuses on required information (doesn't force fabrication)

### Task 4.4 Checklist: Validation & Retry
- [ ] Validation errors are semantic (sums, consistency), not syntactic
- [ ] Retry prompt includes specific validation errors
- [ ] detected_pattern field tracks issue patterns
- [ ] Before retry, verify information exists in source document
- [ ] Confidence fields enable routing (HIGH=auto, MEDIUM=review, LOW=skip)
- [ ] conflict_detected for inconsistent source data

### Task 4.5 Checklist: Batch Processing
- [ ] Batch API used for non-blocking work (overnight, weekly)
- [ ] Synchronous API used for blocking work (pre-merge checks)
- [ ] custom_id fields correlate requests/responses
- [ ] Batch submission frequency calculated for SLA (e.g., 4-hour windows)
- [ ] Sample refinement on small set before batch submission
- [ ] Failure handling plan (chunk oversized documents, retry errors)

### Task 4.6 Checklist: Multi-Instance & Multi-Pass
- [ ] Review uses independent instance (not same session as generation)
- [ ] Multi-pass for files > 5: PASS 1 (local), PASS 2 (cross-file), PASS 3 (verify)
- [ ] Confidence field in verification for routing
- [ ] Each pass has focused prompt (don't dilute attention)
- [ ] Independent instances used for finding subtle issues

---

## Complete Code Examples

### Example 1: Complete Security Review with Explicit Criteria & Few-Shot

```python
"""
Complete example: Security code review with explicit criteria and few-shot examples.
"""

import anthropic
import json

def security_review_with_criteria_and_examples(code_to_review: str) -> dict:
    """
    Comprehensive security review combining:
    - Explicit categorical criteria (Task 4.1)
    - Few-shot examples (Task 4.2)
    - Tool use with schema (Task 4.3)
    """

    client = anthropic.Anthropic()

    # Define extraction tool with schema
    security_tool = {
        "name": "extract_security_findings",
        "description": "Extract security findings from code review",
        "input_schema": {
            "type": "object",
            "properties": {
                "findings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "File and line number"
                            },
                            "issue_type": {
                                "type": "string",
                                "enum": ["SQL_INJECTION", "XSS", "AUTH_BYPASS", "HARDCODED_SECRET",
                                        "CSRF", "DESERIALIZATION", "PATH_TRAVERSAL", "OTHER"]
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
                            },
                            "description": {
                                "type": "string",
                                "description": "What is the vulnerability"
                            },
                            "code_evidence": {
                                "type": "string",
                                "description": "Exact code snippet showing the issue"
                            },
                            "suggested_fix": {
                                "type": "string",
                                "description": "How to remediate"
                            },
                            "confidence": {
                                "type": "string",
                                "enum": ["HIGH", "MEDIUM", "LOW"]
                            },
                            "detected_pattern": {
                                "type": "string",
                                "description": "Pattern that triggered this finding (for analysis)"
                            }
                        },
                        "required": ["location", "issue_type", "severity", "description", "confidence"]
                    }
                }
            },
            "required": ["findings"]
        }
    }

    # Comprehensive prompt with explicit criteria and few-shot
    review_prompt = """Review this code for SECURITY ISSUES ONLY.

EXPLICIT CRITERIA - Report ONLY these categories:

CATEGORY 1: SQL_INJECTION
- REPORT: User input directly concatenated in SQL query (string concat or f-string)
- SKIP: Parameterized queries, prepared statements
- Example severity:
  CRITICAL: "SELECT * FROM users WHERE id = " + request.id
  HIGH: SQL concatenation in less critical query (not auth)

CATEGORY 2: XSS (Cross-Site Scripting)
- REPORT: User input rendered in HTML without escaping
- SKIP: Properly escaped output, HTML entities, framework auto-escape
- Example severity:
  CRITICAL: response.write("<div>" + user_input + "</div>")
  HIGH: form fields with unescaped user data

CATEGORY 3: AUTH_BYPASS
- REPORT: Authentication check can be skipped or forged
- SKIP: Proper JWT validation, session verification
- Example severity:
  CRITICAL: if request.args.get('admin'): grant_access()
  HIGH: Weak token validation (ignoring expiration)

CATEGORY 4: HARDCODED_SECRET
- REPORT: API keys, passwords, tokens hardcoded in source
- SKIP: Environment variables, config files outside repo
- Example severity:
  CRITICAL: api_key = "sk_live_abcd1234efgh5678"
  HIGH: Database password in code

DO NOT REPORT:
- Style issues, naming conventions
- Performance improvements
- Minor refactorings
- Comments that are unclear
- TODOs without security impact

---
FEW-SHOT EXAMPLES (showing exact judgment):

EXAMPLE 1 - Report as CRITICAL SQL_INJECTION:
Code: query = f"SELECT * FROM accounts WHERE user_id = {request.args['id']}"
Reasoning: Direct f-string concatenation of user input (request.args) into SQL. Attacker can inject: id=1' OR '1'='1
Fix: Use parameterized: execute("SELECT * FROM accounts WHERE user_id = ?", [request.args['id']])
Confidence: HIGH (obvious vulnerability)

EXAMPLE 2 - Skip (acceptable pattern):
Code: connection.execute("SELECT * FROM users WHERE id = ?", [user_id])
Reasoning: Using placeholders (?) with parameterized query. User input is safely bound.
Skip reason: This is correct SQL parameterization.

EXAMPLE 3 - Report as HIGH XSS:
Code: <form> {user_comment} </form>
Reasoning: User-controlled comment rendered directly in HTML without escaping. Attacker can inject: <img src=x onerror="alert('xss')">
Fix: Use escape function: {escape(user_comment)} or framework auto-escape
Confidence: HIGH

EXAMPLE 4 - Skip (acceptable pattern):
Code: <form> {escape(user_comment)} </form> (using proper HTML escape function)
Reasoning: User input is escaped before rendering. HTML entities prevent tag injection.
Skip reason: Properly escaped.

EXAMPLE 5 - Report as CRITICAL AUTH_BYPASS:
Code: if request.args.get('is_admin') == 'true': grant_admin_access()
Reasoning: User can set their own admin flag. No actual authentication/authorization check.
Fix: Check session token or database role: if current_user.is_admin: grant_admin_access()
Confidence: CRITICAL

EXAMPLE 6 - Report as CRITICAL HARDCODED_SECRET:
Code: stripe_api_key = "sk_live_abcd1234efgh5678"
Reasoning: Production API key visible in source code. Exposed in repo; attacker can use key directly.
Fix: stripe_api_key = os.environ["STRIPE_API_KEY"]
Confidence: HIGH

---
Now review this code. For each finding, use the exact format shown above.
Provide findings in structured format.

CODE TO REVIEW:
{code}
"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        tools=[security_tool],
        tool_choice={"type": "tool", "name": "extract_security_findings"},
        messages=[
            {
                "role": "user",
                "content": review_prompt.format(code=code_to_review)
            }
        ]
    )

    # Extract findings from tool use
    findings = None
    for block in response.content:
        if block.type == "tool_use":
            findings = block.input
            break

    return findings or {"findings": []}

# Test code with vulnerability
test_code = """
from flask import Flask, request
app = Flask(__name__)

@app.route('/user/<user_id>')
def get_user(user_id):
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)
    return result

@app.route('/search')
def search():
    # XSS vulnerability
    term = request.args.get('q')
    return f"<div>You searched for: {term}</div>"

@app.route('/admin')
def admin():
    # Auth bypass
    if request.args.get('admin') == 'true':
        return "Admin panel"
    return "Access denied"
"""

# Run review
findings = security_review_with_criteria_and_examples(test_code)
print(json.dumps(findings, indent=2))
```

### Example 2: Validation & Retry Loop

```python
"""
Complete example: Extraction with validation and retry-with-error-feedback.
"""

import anthropic
import json
from typing import Optional

def extraction_with_retry_validation():
    """
    Extraction with semantic validation and error-guided retry.
    Combines Tool Use (4.3), Validation (4.4).
    """

    client = anthropic.Anthropic()

    extraction_tool = {
        "name": "extract_invoice",
        "description": "Extract invoice data from document",
        "input_schema": {
            "type": "object",
            "properties": {
                "invoice_number": {"type": ["string", "null"]},
                "invoice_date": {"type": ["string", "null"], "description": "YYYY-MM-DD format"},
                "vendor_name": {"type": ["string", "null"]},
                "line_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "quantity": {"type": "number"},
                            "unit_price": {"type": "number"},
                            "line_total": {"type": "number"}
                        },
                        "required": ["description", "quantity", "unit_price"]
                    }
                },
                "subtotal": {"type": ["number", "null"]},
                "tax": {"type": ["number", "null"]},
                "total": {"type": ["number", "null"]}
            },
            "required": ["line_items"]
        }
    }

    def validate_extraction(data: dict) -> list:
        """
        Validate semantic correctness of extraction.
        """
        errors = []

        # Validation 1: Line items must exist
        if not data.get("line_items"):
            errors.append("No line items extracted; document must contain itemized list")
            return errors

        # Validation 2: Line item totals (if present) should match calculation
        for i, item in enumerate(data["line_items"]):
            calc_total = item.get("quantity", 0) * item.get("unit_price", 0)
            stated_total = item.get("line_total")

            if stated_total is not None and abs(calc_total - stated_total) > 0.01:
                errors.append(
                    f"Line item {i+1}: quantity ({item['quantity']}) × "
                    f"unit_price ({item['unit_price']}) = {calc_total:.2f}, "
                    f"but line_total is {stated_total}. These must match."
                )

        # Validation 3: Invoice total should match sum of items + tax
        if data.get("line_items") and data.get("total"):
            calculated_subtotal = sum(
                item.get("quantity", 0) * item.get("unit_price", 0)
                for item in data["line_items"]
            )

            stated_total = data["total"]
            stated_tax = data.get("tax", 0) or 0

            expected_total = calculated_subtotal + stated_tax

            if abs(expected_total - stated_total) > 0.01:
                errors.append(
                    f"Total mismatch: Line items sum to {calculated_subtotal:.2f} + "
                    f"tax {stated_tax:.2f} = {expected_total:.2f}, "
                    f"but stated total is {stated_total}. These must match exactly."
                )

        # Validation 4: Date format
        if data.get("invoice_date"):
            import re
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', data["invoice_date"]):
                errors.append(
                    f"Date format error: '{data['invoice_date']}' is not YYYY-MM-DD. "
                    f"Must be formatted as YYYY-MM-DD (e.g., 2026-03-22)"
                )

        return errors

    def extract_with_retry(
        document_text: str,
        max_retries: int = 2,
        retry_history: Optional[list] = None
    ) -> dict:
        """
        Extract invoice data with automatic retry on validation failures.
        """

        if retry_history is None:
            retry_history = []

        messages = [
            {
                "role": "user",
                "content": f"""Extract invoice data from this document.
Format dates as YYYY-MM-DD.
For line totals, calculate: quantity × unit_price.
For invoice total, sum all line totals and add tax.

Document:
{document_text}"""
            }
        ]

        for attempt in range(max_retries + 1):
            print(f"\n[Attempt {attempt + 1}] Extracting...")

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                tools=[extraction_tool],
                tool_choice={"type": "tool", "name": "extract_invoice"},
                messages=messages
            )

            # Extract tool use
            extraction = None
            for block in response.content:
                if block.type == "tool_use":
                    extraction = block.input
                    break

            if not extraction:
                print("❌ No extraction returned")
                continue

            print(f"✓ Extraction received. Validating...")

            # Validate
            errors = validate_extraction(extraction)

            if not errors:
                print("✅ Validation passed!")
                return {
                    "success": True,
                    "data": extraction,
                    "attempts": attempt + 1
                }

            print(f"❌ Validation failed with {len(errors)} error(s)")
            for error in errors:
                print(f"  - {error}")

            if attempt < max_retries:
                # Retry with error feedback
                print(f"📝 Retrying with error feedback...")

                error_feedback = "\n".join(f"- {e}" for e in errors)

                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user",
                    "content": f"""Validation errors found. Please correct them and re-extract:

VALIDATION ERRORS:
{error_feedback}

ORIGINAL DOCUMENT:
{document_text}

Re-extract the invoice data, fixing each validation error above."""
                })

                retry_history.append({
                    "attempt": attempt + 1,
                    "errors": errors
                })

        # Final attempt failed
        return {
            "success": False,
            "data": extraction,
            "validation_errors": errors,
            "retry_history": retry_history,
            "attempts": max_retries + 1
        }

    return extract_with_retry

# Example usage
extract_func = extraction_with_retry_validation()

sample_invoice = """
INVOICE

Invoice #: INV-2026-0512
Date: March 22, 2026

From: Tech Supplies Inc
To: Acme Corporation

Line Items:
1. Software Licenses (5 users)      Qty: 5    Price: $50.00 each    Total: $250.00
2. Implementation Services (2 days) Qty: 2    Price: $800.00 each   Total: $1600.00
3. Support Package (annual)         Qty: 1    Price: $500.00 each   Total: $500.00

Subtotal: $2,350.00
Tax (10%): $235.00
TOTAL: $2,585.00
"""

result = extract_func(sample_invoice)
print("\n" + "="*60)
print(json.dumps(result, indent=2, default=str))
```

### Example 3: Multi-Instance Independent Review

```python
"""
Complete example: Multi-instance architecture for independent review.
Combines Task 4.6 with few-shot confidence calibration.
"""

import anthropic
import json

def multi_instance_code_review():
    """
    Generator creates code, independent reviewer assesses quality.
    Independent review catches issues self-review would miss.
    """

    # Instance 1: Code generation
    generator = anthropic.Anthropic()

    # Instance 2: Independent review (separate conversation)
    reviewer = anthropic.Anthropic()

    def generate_and_review(requirements: str) -> dict:
        """
        Generate code with generator instance.
        Review with independent reviewer instance (no generation context).
        """

        # ✅ PHASE 1: Generation
        print("[PHASE 1] Generating code...")

        generation_response = generator.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""Write Python code to: {requirements}

Requirements:
- Include error handling
- Add docstrings
- Make it production-ready"""
                }
            ]
        )

        generated_code = generation_response.content[0].text
        print("✓ Code generated")

        # ❌ DON'T do self-review
        # (generator still has reasoning context)

        # ✅ DO: Independent review with fresh instance
        print("\n[PHASE 2] Independent Review...")

        review_tool = {
            "name": "review_code",
            "description": "Review code for bugs, security, and quality issues",
            "input_schema": {
                "type": "object",
                "properties": {
                    "findings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "issue_type": {
                                    "type": "string",
                                    "enum": ["BUG", "SECURITY", "PERFORMANCE", "MAINTAINABILITY", "ERROR_HANDLING"]
                                },
                                "location": {"type": "string"},
                                "severity": {
                                    "type": "string",
                                    "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
                                },
                                "description": {"type": "string"},
                                "code_evidence": {"type": "string"},
                                "suggested_fix": {"type": "string"},
                                "confidence": {
                                    "type": "string",
                                    "enum": ["HIGH", "MEDIUM", "LOW"]
                                }
                            },
                            "required": ["issue_type", "location", "severity", "confidence", "description"]
                        }
                    }
                },
                "required": ["findings"]
            }
        }

        review_prompt = """Review this code WITHOUT considering any generation reasoning.
Look for issues with fresh perspective:

LOOK FOR:
1. Logic bugs - does code do what it claims?
2. Security - unvalidated input, secrets, auth issues
3. Performance - O(n²) loops, unbounded memory
4. Error handling - what if input is invalid/missing?
5. Edge cases - off-by-one, empty input, negative values

FEW-SHOT EXAMPLES (showing judgment):

EXAMPLE 1 - Report BUG:
Code:
  for i in range(len(items)-1):
    print(items[i+1])
Issue: Off-by-one error - accesses items[len(items)] (out of bounds)
Fix: Should be range(len(items)-1) or access items[i]
Confidence: HIGH (clear bug)

EXAMPLE 2 - Skip (acceptable):
Code:
  for i in range(len(items)-1):
    process(items[i], items[i+1])  # Adjacent pairs
Issue would be: "Loop range too small"
Skip reason: Intentional - deliberately processing adjacent pairs

EXAMPLE 3 - Report SECURITY:
Code:
  data = eval(json_string)
Issue: eval() allows code injection
Fix: Use json.loads() instead
Confidence: CRITICAL

EXAMPLE 4 - Report ERROR_HANDLING:
Code:
  def get_value():
    return data[key]
Issue: KeyError if key missing, not caught
Fix: Use .get(key, default) or explicit try/except
Confidence: HIGH

---
Review this code carefully:

{code}"""

        review_response = reviewer.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=[review_tool],
            tool_choice={"type": "tool", "name": "review_code"},
            messages=[
                {
                    "role": "user",
                    "content": review_prompt.format(code=generated_code)
                }
            ]
        )

        # Extract review findings
        review_findings = None
        for block in review_response.content:
            if block.type == "tool_use":
                review_findings = block.input
                break

        print("✓ Independent review complete")

        # ✅ PHASE 3: Calibrated routing
        print("\n[PHASE 3] Routing findings by confidence...")

        high_confidence = [f for f in review_findings.get("findings", [])
                          if f.get("confidence") == "HIGH"]
        medium_confidence = [f for f in review_findings.get("findings", [])
                            if f.get("confidence") == "MEDIUM"]
        low_confidence = [f for f in review_findings.get("findings", [])
                         if f.get("confidence") == "LOW"]

        return {
            "generated_code": generated_code,
            "review_findings": review_findings,
            "routing": {
                "auto_approve": len(high_confidence),
                "human_review": len(medium_confidence),
                "skip_or_justify": len(low_confidence)
            },
            "findings_by_confidence": {
                "HIGH": high_confidence,
                "MEDIUM": medium_confidence,
                "LOW": low_confidence
            }
        }

    return generate_and_review

# Example usage
review_func = multi_instance_code_review()

requirements = "Function that finds the longest substring without repeating characters"

result = review_func(requirements)
print("\n" + "="*60)
print("GENERATED CODE:")
print(result["generated_code"])
print("\n" + "="*60)
print("REVIEW FINDINGS:")
print(json.dumps(result["findings_by_confidence"], indent=2, default=str))
print("\n" + "="*60)
print(f"Routing: {result['routing']}")
print(f"- {result['routing']['auto_approve']} HIGH confidence → auto-approve")
print(f"- {result['routing']['human_review']} MEDIUM confidence → human review")
print(f"- {result['routing']['skip_or_justify']} LOW confidence → skip/justify")
```

### Example 4: Batch API for Large-Scale Processing

```python
"""
Complete example: Batch API workflow for efficient large-scale processing.
Demonstrates Task 4.5 concepts.
"""

import anthropic
import json
import time
from typing import Optional

def batch_processing_workflow():
    """
    Complete workflow: sample refinement → batch submission → result processing.
    """

    client = anthropic.Anthropic()

    def refine_on_sample(documents: list, sample_size: int = 3) -> dict:
        """
        PHASE 1: Refine prompt on sample before batch processing.
        """

        print(f"[PHASE 1] Refining on {sample_size} sample documents...")

        sample = documents[:sample_size]
        refinement_results = []

        for i, doc in enumerate(sample):
            print(f"  Testing on sample {i+1}/{sample_size}...", end="", flush=True)

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Extract key metrics from this report:
- Project name
- Quarter (Q1-Q4)
- Revenue
- Customer count
- Success rate (%)

Report: {doc}

Format as JSON."""
                    }
                ]
            )

            try:
                extracted = json.loads(response.content[0].text)
                success = True
                error = None
            except json.JSONDecodeError:
                success = False
                error = "Invalid JSON output"

            refinement_results.append({
                "sample_index": i,
                "success": success,
                "error": error,
                "output": response.content[0].text
            })

            print(" ✓" if success else " ✗")

        success_rate = sum(1 for r in refinement_results if r["success"]) / len(refinement_results)
        print(f"\nSample success rate: {success_rate*100:.0f}%")

        if success_rate < 0.9:
            print("⚠️  Success rate < 90%. Would refine prompt and retry sample.")
        else:
            print("✅ Success rate adequate for batch processing")

        return refinement_results

    def submit_batch(documents: list) -> str:
        """
        PHASE 2: Submit full batch with refined prompt.
        """

        print(f"\n[PHASE 2] Submitting batch with {len(documents)} documents...")

        batch_requests = []
        for i, doc in enumerate(documents):
            batch_requests.append({
                "custom_id": f"report_{i:03d}",
                "params": {
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 512,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"""Extract key metrics from this report:
- Project name
- Quarter (Q1-Q4)
- Revenue
- Customer count
- Success rate (%)

Report: {doc}

Format as JSON."""
                        }
                    ]
                }
            })

        batch = client.beta.messages.batches.create(
            requests=batch_requests,
            betas=["batch-2024-07-15"]
        )

        batch_id = batch.id
        print(f"✓ Batch submitted: {batch_id}")
        print(f"  Processing up to 24 hours...")

        return batch_id

    def check_batch_status(batch_id: str) -> dict:
        """
        PHASE 3: Check batch status and process results.
        """

        print(f"\n[PHASE 3] Checking batch status...")

        batch = client.beta.messages.batches.retrieve(
            batch_id,
            betas=["batch-2024-07-15"]
        )

        status = {
            "batch_id": batch_id,
            "status": batch.processing_status,
            "created_at": batch.created_at,
            "expires_at": batch.expires_at,
            "request_counts": {
                "succeeded": batch.request_counts.succeeded,
                "errored": batch.request_counts.errored,
                "processing": batch.request_counts.processing,
                "total": sum([
                    batch.request_counts.succeeded,
                    batch.request_counts.errored,
                    batch.request_counts.processing
                ])
            }
        }

        return status

    def process_batch_results(batch_id: str) -> dict:
        """
        PHASE 4: Process successful results and handle failures.
        """

        print(f"\n[PHASE 4] Processing results...")

        batch = client.beta.messages.batches.retrieve(
            batch_id,
            betas=["batch-2024-07-15"]
        )

        if batch.processing_status != "ended":
            return {"error": "Batch not yet complete"}

        successful = {}
        failed_custom_ids = []

        for result in batch.request_results:
            custom_id = result.custom_id

            if result.result.type == "succeeded":
                message = result.result.message
                successful[custom_id] = message.content[0].text
            elif result.result.type == "errored":
                failed_custom_ids.append(custom_id)
                print(f"⚠️  {custom_id} failed: {result.result.error}")
            elif result.result.type == "expired":
                failed_custom_ids.append(custom_id)
                print(f"⚠️  {custom_id} expired (will resubmit)")

        print(f"\n✓ Processed {len(successful)} successful results")
        print(f"⚠️  {len(failed_custom_ids)} failures to retry")

        return {
            "successful_count": len(successful),
            "failed_count": len(failed_custom_ids),
            "failed_custom_ids": failed_custom_ids,
            "results": successful
        }

    return {
        "refine_on_sample": refine_on_sample,
        "submit_batch": submit_batch,
        "check_batch_status": check_batch_status,
        "process_batch_results": process_batch_results
    }

# Example usage (showing the workflow, not actual execution)
workflow = batch_processing_workflow()

sample_documents = [
    "Q1 2026: Project Alpha Revenue $100k Customers 50 Success 95%",
    "Q2 2026: Project Beta Revenue $250k Customers 120 Success 98%",
    "Q3 2026: Project Gamma Revenue $500k Customers 300 Success 92%",
    # ... more documents ...
]

print("BATCH PROCESSING WORKFLOW")
print("=" * 60)

# Phase 1: Refine on sample
refinement = workflow["refine_on_sample"](sample_documents)

# Phase 2: Submit batch (commented out for example)
# batch_id = workflow["submit_batch"](sample_documents)

# Phase 3: Check status
# status = workflow["check_batch_status"](batch_id)
# print(json.dumps(status, indent=2, default=str))

# Phase 4: Process results
# results = workflow["process_batch_results"](batch_id)
```

---

## Final Exam Preparation Tips

1. **Understand the principles**, not just the code
   - Why explicit criteria work (not just "use them")
   - Why few-shot works (not just "add examples")
   - Why independent review works (not just "use second instance")

2. **Know the traps**
   - Confidence filtering (doesn't work)
   - tool_choice="auto" (no guarantee)
   - Retries without information (won't help)
   - Self-review instruction (retains context bias)

3. **Read scenario questions carefully**
   - Identify constraints (latency, cost, quality, time)
   - Match approach to constraints
   - Spot when wrong tool is suggested

4. **Practice choosing between options**
   - Explicit criteria vs. general instructions
   - Few-shot vs. detailed prose
   - Tool use vs. text output
   - Batch API vs. synchronous API
   - Independent vs. self-review

5. **Code examples should emphasize**
   - Exact tool_choice syntax
   - Schema structure (required, optional, enums)
   - Prompt structure (criteria, examples, instructions)
   - Validation logic
   - Error handling

Good luck on the exam!
