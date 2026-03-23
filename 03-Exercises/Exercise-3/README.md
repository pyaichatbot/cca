# Exercise 3: Structured Data Extraction Pipeline with Validation Loops

## Overview

This exercise demonstrates advanced prompt engineering and context management for a real-world document processing scenario. You'll build an intelligent extraction pipeline that uses Claude's tool-use capabilities to extract, validate, and correct structured data from invoice documents.

This exercise maps to two critical exam domains:
- **Domain 4: Prompt Engineering & Structured Output** - Tool design, schema validation, retry logic
- **Domain 5: Context Management & Reliability** - Context window optimization, confidence calibration, information provenance

**Estimated Time:** 30-40 minutes
**Difficulty Level:** Advanced
**Prerequisites:** Understanding of tool-use, JSON schemas, and Claude's API

---

## Learning Objectives

After completing this exercise, you will be able to:

1. **Design extraction tools with robust JSON schemas**
   - Define required vs optional fields
   - Implement nullable fields for uncertain data
   - Use enum types with "other" + detail pattern
   - Handle "unclear" values explicitly

2. **Implement sophisticated tool-use patterns**
   - Use `tool_choice: "any"` for flexible tool selection
   - Force specific tools with `{"type": "tool", "name": "..."}`
   - Design few-shot examples in system prompts
   - Implement retry-with-error-feedback loops

3. **Validate and self-correct extractions**
   - Compare calculated vs stated totals
   - Detect conflicts and flag them
   - Identify when retries are effective vs ineffective
   - Distinguish between missing information and format errors

4. **Manage context and confidence**
   - Normalize results after tool use
   - Calibrate model confidence for each field
   - Route low-confidence extractions to human review
   - Track information provenance (source sections)

5. **Handle batch-like processing patterns**
   - Simulate batch processing with custom_id correlation
   - Process multiple documents sequentially
   - Aggregate results and metadata

---

## Code Structure Walkthrough

### File Organization

```
Exercise-3/
├── README.md (this file)
└── extraction_pipeline.py (main implementation)
```

### Key Components

#### 1. Tool Definition: `extract_invoice`

```python
{
    "name": "extract_invoice",
    "description": "Extract structured invoice data from document text",
    "input_schema": {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": "Invoice identifier"
            },
            "date": {
                "type": "string",
                "description": "Date in YYYY-MM-DD format"
            },
            "vendor": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["name", "confidence"]
            },
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit_price": {"type": "number"},
                        "total": {"type": "number"}
                    },
                    "required": ["description", "quantity", "unit_price", "total"]
                }
            },
            "totals": {
                "type": "object",
                "properties": {
                    "subtotal": {"type": "number"},
                    "tax": {"type": "number"},
                    "stated_total": {"type": "number"},
                    "calculated_total": {"type": "number"},
                    "conflict_detected": {"type": "boolean"}
                },
                "required": ["subtotal", "tax", "stated_total", "calculated_total", "conflict_detected"]
            },
            "payment_terms": {
                "type": ["string", "null"],
                "enum": ["NET30", "NET60", "DUE_ON_RECEIPT", "other", null],
                "detail": {
                    "type": "string",
                    "description": "Required when payment_terms is 'other'"
                }
            },
            "confidence_summary": {
                "type": "object",
                "properties": {
                    "overall": {"type": "number", "minimum": 0, "maximum": 1},
                    "field_confidences": {"type": "object"}
                }
            }
        },
        "required": [
            "invoice_number",
            "date",
            "vendor",
            "line_items",
            "totals",
            "confidence_summary"
        ]
    }
}
```

#### 2. Retry Logic: Error-Feedback Pattern

When validation fails, the pipeline:
1. Detects validation errors
2. Appends specific error messages to the conversation
3. Requests Claude to retry with error context
4. Distinguishes between:
   - **Format errors** (fixable): Missing required fields, type mismatches
   - **Missing information** (not fixable): Data not in document, marked as "unclear"

#### 3. Validation Functions

```python
def validate_extraction(extraction_data: dict) -> dict:
    """
    Validates extracted data and returns:
    - is_valid: bool
    - errors: list of error messages
    - warnings: list of warnings
    """
```

#### 4. Confidence Routing

Extractions are routed based on confidence thresholds:
- **High confidence (≥0.8)**: Proceed automatically
- **Medium confidence (0.6-0.8)**: Flag for review
- **Low confidence (<0.6)**: Human review required

#### 5. Information Provenance Tracking

Each extraction includes source information:
```python
{
    "field_name": "invoice_number",
    "value": "INV-2024-001",
    "source": "First line of document",
    "confidence": 0.95
}
```

---

## Key Patterns Explained

### Pattern 1: Tool Choice Control

**Domain 4 Relevance:** Demonstrates mastery of tool-use mechanics

```python
# Flexible tool selection - model chooses when/if to use
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    tools=[extraction_tool],
    tool_choice="any"  # Allows model to decide
)

# Forced tool selection - always use this tool
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    tools=[extraction_tool],
    tool_choice={"type": "tool", "name": "extract_invoice"}  # Forces usage
)
```

**When to use:**
- `"any"`: Initial exploration, optional extraction tasks
- Force tool: Ensuring structured output, when extraction is mandatory

### Pattern 2: Few-Shot Examples in System Prompt

**Domain 4 Relevance:** Ensuring consistent extraction behavior

The system prompt includes examples of:
- Correct extraction structure
- How to handle uncertain fields
- How to calculate and detect total conflicts
- When to mark fields as "unclear"

```python
system_prompt = """
You are an expert invoice extraction system.

EXAMPLES OF CORRECT EXTRACTION:

Example 1: Standard Invoice
Input: "INV-2024-001 dated 2024-03-15..."
Output:
{
    "invoice_number": "INV-2024-001",
    "date": "2024-03-15",
    "conflict_detected": false
}

Example 2: Total Mismatch
Input: "Line items total $100, but invoice says $105"
Output:
{
    "stated_total": 105,
    "calculated_total": 100,
    "conflict_detected": true
}

Example 3: Unclear Information
Input: "The date is somewhere in March... vendor is Smith or Schmidt?"
Output:
{
    "date": "unclear",
    "vendor": {
        "name": "Smith or Schmidt",
        "confidence": 0.4
    }
}
"""
```

### Pattern 3: Retry-with-Error-Feedback

**Domain 4 & 5 Relevance:** Implementing reliable extraction through validation loops

```python
attempt = 0
max_retries = 2

while attempt < max_retries:
    # Make extraction attempt
    response = client.messages.create(...)
    extraction = parse_tool_response(response)
    validation = validate_extraction(extraction)

    if validation["is_valid"]:
        break

    # Effective retry: append error feedback
    if is_fixable_error(validation["errors"]):
        conversation_history.append({
            "role": "user",
            "content": f"Validation failed. Please fix: {validation['errors']}"
        })
        attempt += 1
    else:
        # Ineffective: missing data in document
        break
```

**Key Distinction:**
- **Fixable errors**: Field type mismatch, missing optional field → retry works
- **Unfixable errors**: Data genuinely not in document → mark as "unclear", don't retry

### Pattern 4: Self-Correction Validation

**Domain 4 Relevance:** Using tool output to self-correct

```python
# Model reports both values
extraction = {
    "line_items": [
        {"description": "Service", "quantity": 2, "unit_price": 50, "total": 100}
    ],
    "totals": {
        "stated_total": 110,      # What invoice says
        "calculated_total": 100,   # What we computed
        "conflict_detected": true   # Model detects discrepancy
    }
}

# Pipeline can:
# 1. Flag for human review if conflict_detected=true
# 2. Request clarification from model
# 3. Look for typos/corrections in document
```

### Pattern 5: Confidence Calibration

**Domain 5 Relevance:** Context management through confidence-based routing

```python
def route_for_review(extraction: dict) -> str:
    """Route based on confidence thresholds"""
    overall_confidence = extraction["confidence_summary"]["overall"]

    if overall_confidence >= 0.8:
        return "APPROVED"
    elif overall_confidence >= 0.6:
        return "REVIEW_QUEUE"
    else:
        return "HUMAN_REVIEW"
```

### Pattern 6: Information Provenance

**Domain 5 Relevance:** Tracking information sources for reliability

```python
# Each extraction tracks its source:
{
    "invoice_number": "INV-2024-001",
    "confidence": 0.95,
    "source": "Document header, line 1",
    "source_context": "Invoice number clearly stated as INV-2024-001"
}

# Allows:
# - Verification by going back to source
# - Understanding confidence basis
# - Debugging extraction issues
```

### Pattern 7: Simulated Batch Processing

**Domain 5 Relevance:** Processing multiple documents efficiently

```python
batch_records = [
    {
        "custom_id": "doc_001",
        "document_content": invoice_1,
        "retry_count": 0,
        "confidence": None,
        "status": "pending"
    },
    # ... more records
]

# Process with tracking
for record in batch_records:
    extraction = extract_invoice(record["document_content"])
    record["status"] = "completed"
    record["confidence"] = extraction["confidence_summary"]["overall"]
```

---

## Expected Output Examples

### Successful Extraction (High Confidence)

```
========== EXTRACTION RESULT ==========
Document ID: doc_001
Status: APPROVED (confidence: 0.92)

Extracted Data:
- Invoice Number: INV-2024-001
- Date: 2024-03-15
- Vendor: Acme Corp (confidence: 0.95)
- Line Items: 3 items totaling $250.00
- Subtotal: $250.00
- Tax: $25.00
- Total: $275.00
- Payment Terms: NET30

Validation: PASSED
No conflicts detected.
```

### Partial Extraction (Medium Confidence, Flagged for Review)

```
========== EXTRACTION RESULT ==========
Document ID: doc_002
Status: REVIEW_QUEUE (confidence: 0.68)

Extracted Data:
- Invoice Number: unclear (could be "INV-024" or "INV-2024")
- Date: 2024-03-20 (confidence: 0.85)
- Vendor: Smith & Co (confidence: 0.72)
- Total Conflict: stated $500, calculated $485
  → Possible OCR error or discount not captured

Validation: WARNINGS
- Field 'invoice_number' has low confidence (0.45)
- Total mismatch detected

Recommended Action: Human review for clarification
```

### Failed Extraction (Low Confidence, Requires Human Review)

```
========== EXTRACTION RESULT ==========
Document ID: doc_003
Status: HUMAN_REVIEW (confidence: 0.52)

Extracted Data:
- Invoice Number: unclear
- Date: unclear
- Vendor: unclear
- Line Items: Unable to extract structure

Validation: FAILED
- Critical fields missing or unclear
- Document may be malformed or in unexpected format
- Total: Cannot compute (no valid line items)

Recommended Action: Manual data entry required
```

---

## Exam Questions This Prepares You For

### Question 1: Tool Design & Schemas

**Question:** "You need to extract invoice data where the payment terms might be one of several standard values or something custom. How would you design the schema for the payment_terms field?"

**Answer:**
```json
{
    "payment_terms": {
        "type": ["string", "null"],
        "enum": ["NET30", "NET60", "DUE_ON_RECEIPT", "other"],
        "description": "Payment terms, or 'other' if non-standard",
        "detail": {
            "type": "string",
            "description": "Details for non-standard payment terms (required when 'other' is selected)"
        }
    }
}
```

**Key Principle:** Use enum for known values, "other" + detail pattern for extensibility. Mark as nullable to handle cases where the field isn't present.

---

### Question 2: Tool Choice vs Forced Tools

**Question:** "In what scenarios would you use `tool_choice: "any"` vs forcing a specific tool with `{"type": "tool", "name": "extract_invoice"}`?"

**Answer:**

| Scenario | Tool Choice | Rationale |
|----------|-------------|-----------|
| Initial triage (is this extractable?) | `"any"` | Model decides if extraction is possible |
| Mandatory extraction (must structure data) | Forced | Ensures tool is always used |
| Complex multi-step extraction | `"any"` | Model can call other tools if needed |
| Simple extraction (one tool does it all) | Forced | Efficiency and consistency |

**Key Principle:** Use flexible choice when you want the model's judgment. Force tools when output structure is non-negotiable.

---

### Question 3: Retry Strategy

**Question:** "You extract an invoice total of $100, but line items calculate to $95. The model reports low confidence in the total. Should you retry the extraction?"

**Answer:**

**Yes, if:** The error is likely fixable (typo, OCR error, format issue)
- Retry with error feedback: "Calculated total from line items is $95, but stated total is $100. Please verify."

**No, if:** The document genuinely has conflicting information
- Mark as `conflict_detected: true`
- Route for human review instead of retrying
- Include both values (stated_total, calculated_total) in output

**Key Principle:** Distinguish between format errors (retry) and missing/conflicting data (escalate).

---

### Question 4: Confidence Calibration

**Question:** "How should you design a confidence calibration system to route extractions appropriately?"

**Answer:**

```python
# Per-field confidence
{
    "invoice_number": {"value": "INV-001", "confidence": 0.95},
    "vendor": {"value": "Unknown", "confidence": 0.30}
}

# Overall confidence (weighted or average)
overall = (0.95 + 0.30) / 2 = 0.625

# Routing logic
if overall >= 0.8:      # High confidence
    route = "AUTO_APPROVE"
elif overall >= 0.6:    # Medium confidence
    route = "REVIEW_QUEUE"
else:                   # Low confidence
    route = "HUMAN_REVIEW"
```

**Key Principle:** Use per-field confidence, compute overall metric, route based on thresholds.

---

### Question 5: Information Provenance

**Question:** "Why should extractions include source/provenance information, and how would you use it?"

**Answer:**

**Benefits:**
1. **Verification:** Go back to source document to confirm extraction
2. **Debugging:** Understand why confidence is low ("extracted from blurry section")
3. **Audit trail:** Track decision-making and extraction basis
4. **Quality improvement:** Identify patterns in errors (e.g., "OCR fails on handwriting")

**Implementation:**
```python
{
    "field": "invoice_number",
    "value": "INV-2024-001",
    "confidence": 0.95,
    "source": "Document header, first line",
    "source_context": "Text clearly shows 'Invoice: INV-2024-001'"
}
```

**Key Principle:** Always track where data came from, not just what the data is.

---

### Question 6: Batch-like Processing

**Question:** "How would you handle extracting invoices from 100 documents while tracking retry counts and confidence?"

**Answer:**

```python
# Simulate batch with custom_id tracking
batch_requests = [
    {"custom_id": "doc_001", "document": content_1},
    {"custom_id": "doc_002", "document": content_2},
    # ...
]

# Process with metadata
results = {
    "doc_001": {
        "extraction": {...},
        "confidence": 0.92,
        "retry_count": 0,
        "status": "approved"
    },
    # ...
}

# Aggregate metrics
approved = sum(1 for r in results.values() if r["status"] == "approved")
review_needed = sum(1 for r in results.values() if r["status"] == "review")
human_review = sum(1 for r in results.values() if r["status"] == "human_review")
```

**Key Principle:** Assign stable identifiers, track per-document state, aggregate results.

---

## How to Run the Exercise

### Prerequisites

1. **Python 3.8+** installed
2. **Anthropic SDK:** `pip install anthropic`
3. **API Key:** Set `ANTHROPIC_API_KEY` environment variable

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Running the Script

```bash
cd /sessions/quirky-blissful-archimedes/mnt/CCA/Exercise-3/
python extraction_pipeline.py
```

### Expected Runtime

- **Total time:** 30-60 seconds (depends on API latency)
- **Number of API calls:** 6-15 (3 documents × up to 2 retries each)
- **Output:** Detailed extraction results with validation and confidence scores

### Understanding the Output

The script prints:

1. **Document Processing:** Shows each document being processed
2. **Extraction Attempts:** Displays extraction attempts and retries
3. **Validation Results:** Shows what passed/failed validation
4. **Final Results:** Structured data, confidence, routing decision
5. **Summary:** Overall statistics (approved, review, human_review counts)

### Customizing the Exercise

**To add more documents:**
Edit the `sample_invoices` list in `extraction_pipeline.py`:

```python
sample_invoices = [
    ("doc_001", "INVOICE INV-2024-001..."),
    ("doc_002", "INVOICE INV-2024-002..."),
    ("doc_003", "INVOICE INV-2024-003..."),
    ("doc_004", "YOUR NEW INVOICE HERE..."),  # Add more
]
```

**To change confidence thresholds:**
Edit the routing logic:

```python
def route_extraction(extraction: dict) -> str:
    confidence = extraction["confidence_summary"]["overall"]
    if confidence >= 0.85:  # Raised from 0.8
        return "APPROVED"
    # ...
```

**To disable retries:**
In `extract_with_validation()`, set `max_retries = 0`

---

## Learning Path

This exercise builds on earlier exercises:
- **Exercise 1:** Basic tool-use patterns
- **Exercise 2:** Multi-turn conversations with tool use
- **Exercise 3:** (This) Validation loops, confidence, batch-like processing

Next exercises (if available) will cover:
- **Exercise 4:** Advanced context management and token optimization
- **Exercise 5:** Production reliability patterns and error handling

---

## Additional Resources

- Anthropic API Documentation: https://docs.anthropic.com
- Tool Use Guide: https://docs.anthropic.com/en/docs/build-a-system/tool-use
- JSON Schema Reference: https://json-schema.org/
- Claude Certified Architect Exam Guide: [Provided separately]

---

## Summary Checklist

Before moving on, verify you understand:

- [ ] How to design JSON schemas with required/optional/enum/nullable fields
- [ ] When to use `tool_choice: "any"` vs forced tool selection
- [ ] How to implement retry logic with error feedback
- [ ] The difference between fixable and unfixable errors
- [ ] How to calibrate and route based on confidence
- [ ] Why information provenance matters
- [ ] How to process multiple documents with tracking
- [ ] The relationship between validation and retries

If you can explain all these concepts, you're ready for the exam questions related to Domains 4 and 5.
