#!/usr/bin/env python3
"""
Exercise 3: Structured Data Extraction Pipeline with Validation Loops

This exercise demonstrates advanced prompt engineering and context management:
- Domain 4: Tool design with JSON schemas, retry-with-error-feedback, few-shot examples
- Domain 5: Context management, confidence calibration, information provenance

Key patterns:
1. Tool-use with forced selection and flexible selection
2. Few-shot examples in system prompt for consistency
3. Validation-driven retry loops (error feedback)
4. Self-correction through conflict detection
5. Confidence calibration and routing
6. Information provenance tracking
7. Simulated batch processing with custom_id
"""

import json
import os
from typing import Optional
from dataclasses import dataclass, asdict
from anthropic import Anthropic

# Initialize Anthropic client
client = Anthropic()
MODEL = "claude-3-5-sonnet-20241022"

# ==============================================================================
# DATA STRUCTURES
# ==============================================================================


@dataclass
class ConfidenceInfo:
    """Tracks confidence for a field"""
    overall: float
    field_confidences: dict


@dataclass
class ExtractionResult:
    """Final extraction result with metadata"""
    invoice_number: Optional[str]
    date: Optional[str]
    vendor_name: Optional[str]
    vendor_confidence: float
    line_items: list
    subtotal: float
    tax: float
    stated_total: float
    calculated_total: float
    conflict_detected: bool
    payment_terms: Optional[str]
    overall_confidence: float
    extraction_attempt: int
    validation_passed: bool
    validation_errors: list
    routing_decision: str
    source_info: dict


# ==============================================================================
# TOOL DEFINITION
# ==============================================================================

EXTRACTION_TOOL = {
    "name": "extract_invoice",
    "description": "Extract structured invoice data from document text. Extracts all financial information, vendor details, and payment terms.",
    "input_schema": {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": "Invoice identifier (e.g., INV-2024-001). Mark as 'unclear' if ambiguous.",
            },
            "date": {
                "type": "string",
                "description": "Invoice date in YYYY-MM-DD format. Mark as 'unclear' if date is ambiguous or not present.",
            },
            "vendor": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Vendor/supplier name",
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "Your confidence in the vendor name (0.0-1.0)",
                    },
                },
                "required": ["name", "confidence"],
            },
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Item description",
                        },
                        "quantity": {
                            "type": "number",
                            "description": "Quantity ordered",
                        },
                        "unit_price": {
                            "type": "number",
                            "description": "Price per unit",
                        },
                        "total": {
                            "type": "number",
                            "description": "Line item total (quantity * unit_price)",
                        },
                    },
                    "required": ["description", "quantity", "unit_price", "total"],
                },
                "description": "List of items on invoice",
            },
            "totals": {
                "type": "object",
                "properties": {
                    "subtotal": {
                        "type": "number",
                        "description": "Sum of all line items before tax",
                    },
                    "tax": {
                        "type": "number",
                        "description": "Tax amount",
                    },
                    "stated_total": {
                        "type": "number",
                        "description": "Total stated on invoice",
                    },
                    "calculated_total": {
                        "type": "number",
                        "description": "Your calculated total (subtotal + tax)",
                    },
                    "conflict_detected": {
                        "type": "boolean",
                        "description": "True if stated_total != calculated_total",
                    },
                },
                "required": ["subtotal", "tax", "stated_total", "calculated_total", "conflict_detected"],
            },
            "payment_terms": {
                "type": ["string", "null"],
                "enum": ["NET30", "NET60", "DUE_ON_RECEIPT", "other", None],
                "description": "Payment terms if specified",
            },
            "payment_terms_detail": {
                "type": ["string", "null"],
                "description": "Details for non-standard payment terms (required if payment_terms='other')",
            },
            "confidence_summary": {
                "type": "object",
                "properties": {
                    "overall": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "Overall confidence in extraction (0.0-1.0)",
                    },
                    "field_confidences": {
                        "type": "object",
                        "description": "Confidence for each major field",
                    },
                },
                "required": ["overall", "field_confidences"],
            },
        },
        "required": [
            "invoice_number",
            "date",
            "vendor",
            "line_items",
            "totals",
            "confidence_summary",
        ],
    },
}

# ==============================================================================
# SYSTEM PROMPT WITH FEW-SHOT EXAMPLES
# ==============================================================================

SYSTEM_PROMPT = """You are an expert invoice extraction system. Your role is to extract structured data from invoice documents with high accuracy.

EXTRACTION RULES:

1. CONFIDENCE REPORTING:
   - Report realistic confidence (0.0-1.0) for each field
   - Lower confidence if data is unclear, ambiguous, or missing
   - Mark ambiguous values as "unclear" and report low confidence

2. HANDLING UNCLEAR DATA:
   - If a field is present but ambiguous (e.g., "possibly INV-2024 or INV-024"), report the ambiguity and low confidence
   - If a field is completely missing, mark as "unclear"
   - DO NOT invent data you cannot see

3. TOTAL CONFLICT DETECTION:
   - Always calculate the total from line items (subtotal + tax)
   - Compare with the stated total on the invoice
   - If they differ, set conflict_detected=true and report both values
   - This helps identify OCR errors, discounts, or missing line items

4. LINE ITEMS:
   - Extract all line items with description, quantity, unit_price
   - Calculate total for each line item (qty * unit_price)
   - If line item information is incomplete, still extract what you can

5. PAYMENT TERMS:
   - Use standard values: NET30, NET60, DUE_ON_RECEIPT when applicable
   - If custom terms are shown, use "other" and provide detail
   - If not specified, use null

EXAMPLES OF CORRECT EXTRACTION:

Example 1: Clear Invoice
Input: "Invoice INV-2024-001, Date: 2024-03-15, Vendor: Acme Corp, Service $100, Tax $10, Total $110"
Output:
{
    "invoice_number": "INV-2024-001",
    "date": "2024-03-15",
    "vendor": {"name": "Acme Corp", "confidence": 0.95},
    "line_items": [{"description": "Service", "quantity": 1, "unit_price": 100, "total": 100}],
    "totals": {
        "subtotal": 100,
        "tax": 10,
        "stated_total": 110,
        "calculated_total": 110,
        "conflict_detected": false
    },
    "confidence_summary": {"overall": 0.94, "field_confidences": {"invoice_number": 0.95, "date": 0.95, "vendor": 0.95}}
}

Example 2: Conflict Detection
Input: "Invoice INV-2024, Date: Mar 15, Vendor: Smith Inc, Item $50 x2 = $100, Tax $10, Total $115"
Output:
{
    "invoice_number": "INV-2024",
    "date": "2024-03-15",
    "vendor": {"name": "Smith Inc", "confidence": 0.90},
    "line_items": [{"description": "Item", "quantity": 2, "unit_price": 50, "total": 100}],
    "totals": {
        "subtotal": 100,
        "tax": 10,
        "stated_total": 115,
        "calculated_total": 110,
        "conflict_detected": true
    },
    "confidence_summary": {"overall": 0.80, "field_confidences": {"totals": 0.70}}
}
Note: Conflict detected! Stated $115 but calculated $110 (possible $5 discount or error)

Example 3: Unclear Data
Input: "Invoice ?, Date: [unclear], Vendor: could be ABC or XYZ Corp, No clear line items visible"
Output:
{
    "invoice_number": "unclear",
    "date": "unclear",
    "vendor": {"name": "ABC or XYZ Corp", "confidence": 0.35},
    "line_items": [],
    "totals": {
        "subtotal": 0,
        "tax": 0,
        "stated_total": 0,
        "calculated_total": 0,
        "conflict_detected": false
    },
    "confidence_summary": {"overall": 0.25, "field_confidences": {"invoice_number": 0.1, "date": 0.1, "vendor": 0.35}}
}

CRITICAL:
- Always report confidence honestly
- Always calculate totals and flag conflicts
- Always provide line items even if incomplete
- Mark unclear data as "unclear" - do not guess
- Use the extract_invoice tool for every document"""

# ==============================================================================
# VALIDATION FUNCTIONS
# ==============================================================================


def validate_extraction(data: dict) -> dict:
    """
    Validate extracted data.
    Returns: {is_valid, errors, warnings}
    """
    errors = []
    warnings = []

    # Check required fields
    if not data.get("invoice_number") or data.get("invoice_number") == "unclear":
        errors.append("invoice_number is missing or unclear")

    if not data.get("date") or data.get("date") == "unclear":
        errors.append("date is missing or unclear")

    if not data.get("vendor", {}).get("name"):
        errors.append("vendor name is missing")

    # Check totals structure
    totals = data.get("totals", {})
    if "stated_total" not in totals or "calculated_total" not in totals:
        errors.append("totals are incomplete")

    # Check for total conflicts
    if totals.get("conflict_detected"):
        warnings.append(
            f"Total conflict: stated ${totals.get('stated_total')}, "
            f"calculated ${totals.get('calculated_total')}"
        )

    # Check confidence
    confidence = data.get("confidence_summary", {}).get("overall", 0)
    if confidence < 0.5:
        warnings.append(f"Low overall confidence: {confidence:.2f}")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "confidence": confidence,
    }


def is_retry_effective(validation: dict, previous_validation: Optional[dict] = None) -> bool:
    """
    Determine if retrying makes sense.
    - True: Format/structure issues that might be fixed with feedback
    - False: Missing data in document (can't be fixed by retry)
    """
    errors = validation.get("errors", [])

    # Don't retry if core data is genuinely missing
    has_missing_data = any("unclear" in str(e).lower() for e in errors)
    if has_missing_data:
        return False

    # Retry if it's format/structure issues
    has_structure_issues = any(
        "incomplete" in str(e).lower() or "missing" in str(e).lower()
        for e in errors
    )

    return has_structure_issues


def calculate_routing_decision(validation: dict) -> str:
    """Route extraction based on confidence and validation"""
    confidence = validation.get("confidence", 0)
    is_valid = validation.get("is_valid", False)

    if not is_valid:
        return "HUMAN_REVIEW"
    elif confidence >= 0.8:
        return "APPROVED"
    elif confidence >= 0.6:
        return "REVIEW_QUEUE"
    else:
        return "HUMAN_REVIEW"


# ==============================================================================
# EXTRACTION FUNCTIONS
# ==============================================================================


def extract_invoice(document_content: str, attempt: int = 1) -> dict:
    """
    Extract invoice data from document using Claude.
    Uses forced tool selection to ensure structured output.
    """
    conversation_history = [
        {
            "role": "user",
            "content": f"Extract invoice data from this document:\n\n{document_content}",
        }
    ]

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "extract_invoice"},  # Force tool use
        messages=conversation_history,
    )

    # Extract tool use response
    tool_use = None
    for block in response.content:
        if block.type == "tool_use":
            tool_use = block
            break

    if not tool_use:
        return {
            "extraction_attempt": attempt,
            "error": "No tool use in response",
            "raw_response": str(response.content),
        }

    # Parse tool input
    try:
        extraction = tool_use.input
        extraction["extraction_attempt"] = attempt
        return extraction
    except Exception as e:
        return {
            "extraction_attempt": attempt,
            "error": f"Failed to parse extraction: {str(e)}",
            "raw_input": tool_use.input,
        }


def extract_with_validation(document_content: str, custom_id: str) -> tuple:
    """
    Extract invoice with validation and retry logic.
    Returns: (final_extraction, validation_result, attempt_count)
    """
    max_retries = 2
    attempt = 1
    previous_validation = None

    print(f"\n  Attempt {attempt}: Extracting...")
    extraction = extract_invoice(document_content, attempt)

    if "error" in extraction:
        print(f"    Error: {extraction.get('error')}")
        return extraction, {"is_valid": False, "errors": [extraction.get("error")]}, attempt

    validation = validate_extraction(extraction)
    print(f"    Validation: {'PASSED' if validation['is_valid'] else 'FAILED'}")

    if not validation["is_valid"]:
        print(f"    Errors: {validation['errors']}")

    # Retry loop
    while not validation["is_valid"] and attempt < max_retries + 1:
        # Check if retry is worthwhile
        if not is_retry_effective(validation, previous_validation):
            print(f"    Retry ineffective (missing data in document) - escalating")
            break

        attempt += 1
        previous_validation = validation

        print(f"  Attempt {attempt}: Retrying with error feedback...")
        print(f"    Feedback: {validation['errors']}")

        # Retry with error feedback
        extraction = extract_invoice(document_content, attempt)

        if "error" in extraction:
            print(f"    Error: {extraction.get('error')}")
            break

        validation = validate_extraction(extraction)
        print(f"    Validation: {'PASSED' if validation['is_valid'] else 'FAILED'}")

        if not validation["is_valid"]:
            print(f"    Errors: {validation['errors']}")

    return extraction, validation, attempt


# ==============================================================================
# RESULT NORMALIZATION & ROUTING
# ==============================================================================


def normalize_extraction_result(
    extraction: dict, validation: dict, attempt: int, custom_id: str
) -> ExtractionResult:
    """
    Normalize extraction into a structured result.
    Domain 5: PostToolUse normalization pattern
    """
    routing = calculate_routing_decision(validation)

    # Extract fields with defaults
    invoice_number = extraction.get("invoice_number", "")
    if invoice_number == "unclear":
        invoice_number = None

    date = extraction.get("date", "")
    if date == "unclear":
        date = None

    vendor = extraction.get("vendor", {})
    vendor_name = vendor.get("name") if isinstance(vendor, dict) else None
    vendor_confidence = vendor.get("confidence", 0.0) if isinstance(vendor, dict) else 0.0

    if vendor_name == "unclear":
        vendor_name = None

    line_items = extraction.get("line_items", [])
    totals = extraction.get("totals", {})

    subtotal = totals.get("subtotal", 0)
    tax = totals.get("tax", 0)
    stated_total = totals.get("stated_total", 0)
    calculated_total = totals.get("calculated_total", 0)
    conflict_detected = totals.get("conflict_detected", False)

    payment_terms = extraction.get("payment_terms")
    if payment_terms == "other":
        payment_terms = extraction.get("payment_terms_detail", "Custom")

    confidence_info = extraction.get("confidence_summary", {})
    overall_confidence = confidence_info.get("overall", 0.0)

    source_info = {
        "vendor_section": "Document header or from:line",
        "line_items_section": "Table or itemized list",
        "total_section": "Bottom of document",
    }

    return ExtractionResult(
        invoice_number=invoice_number,
        date=date,
        vendor_name=vendor_name,
        vendor_confidence=vendor_confidence,
        line_items=line_items,
        subtotal=subtotal,
        tax=tax,
        stated_total=stated_total,
        calculated_total=calculated_total,
        conflict_detected=conflict_detected,
        payment_terms=payment_terms,
        overall_confidence=overall_confidence,
        extraction_attempt=attempt,
        validation_passed=validation.get("is_valid", False),
        validation_errors=validation.get("errors", []),
        routing_decision=routing,
        source_info=source_info,
    )


# ==============================================================================
# SAMPLE INVOICES
# ==============================================================================

SAMPLE_INVOICES = [
    (
        "doc_001",
        """
INVOICE
Invoice Number: INV-2024-001
Date: 2024-03-15
From: Acme Corporation
        123 Business Street
        Springfield, IL 62701

Bill To: Your Company
        456 Main Avenue
        Capital City, ST 12345

Description                              Qty    Unit Price    Total
-------------------------------------------------------------------
Professional Consulting Services          10      $150.00    $1,500.00
Software License (Annual)                  2      $500.00    $1,000.00
Technical Support Package                  1      $300.00      $300.00

Subtotal:                                                    $2,800.00
Tax (7%):                                                      $196.00
-------------------------------------------------------------------
TOTAL DUE:                                                  $2,996.00

Payment Terms: NET30
Due Date: 2024-04-14
""",
    ),
    (
        "doc_002",
        """
INVOICE #INV-2024-0045
Date: March 20, 2024
Vendor: Smith & Associates LLC

Items Provided:
- Graphic Design Work: 15 hours @ $75/hour = $1,125
- Website Updates: 8 hours @ $85/hour = $680
- Project Management: 4 hours @ $100/hour = $400

Subtotal: $2,205
Tax: $176.40
Invoice Total: $2,380

Payment: Due on receipt preferred, but NET60 acceptable.
Note: There's a $15 discount for early payment.
        """,
    ),
    (
        "doc_003",
        """
INV 2024 - 789

Date: March 25 (approximately)
Vendor: Could be "XYZ Industries" or "XYZ Inc" - unclear from document

Items:
[DOCUMENT QUALITY POOR - OCR ERRORS PRESENT]

Item 1: Damaged line items - quantity unclear, price appears to be $500?
Item 2: Text cut off - price unknown
Item 3: ???

Subtotal: Approx $1,000 (rough estimate)
Tax: Unknown
Total Shown: $1,250

Payment Terms: Not clearly specified
        """,
    ),
]

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================


def main():
    """Main execution: process sample invoices through the extraction pipeline"""

    print("=" * 80)
    print("EXERCISE 3: STRUCTURED DATA EXTRACTION PIPELINE WITH VALIDATION LOOPS")
    print("=" * 80)
    print("\nDomain 4 (Prompt Engineering & Structured Output)")
    print("Domain 5 (Context Management & Reliability)")
    print("\nProcessing 3 sample invoice documents...\n")

    # Batch processing results
    batch_results = []
    routing_summary = {"APPROVED": 0, "REVIEW_QUEUE": 0, "HUMAN_REVIEW": 0}

    for custom_id, document_content in SAMPLE_INVOICES:
        print(f"\n{'=' * 80}")
        print(f"Processing Document: {custom_id}")
        print("=" * 80)
        print(f"Document preview: {document_content[:100]}...\n")

        # Extract with validation and retries
        extraction, validation, attempt = extract_with_validation(document_content, custom_id)

        # Normalize result
        result = normalize_extraction_result(extraction, validation, attempt, custom_id)

        # Print detailed result
        print(f"\n{'=' * 80}")
        print(f"EXTRACTION RESULT: {custom_id}")
        print("=" * 80)
        print(f"Status: {result.routing_decision} (Confidence: {result.overall_confidence:.2%})")
        print(f"Extraction Attempts: {result.extraction_attempt}")
        print(f"Validation: {'PASSED' if result.validation_passed else 'FAILED'}")

        if result.validation_errors:
            print(f"Validation Errors: {', '.join(result.validation_errors)}")

        print(f"\nExtracted Data:")
        print(f"  Invoice Number: {result.invoice_number or 'N/A'}")
        print(f"  Date: {result.date or 'N/A'}")
        print(f"  Vendor: {result.vendor_name} (confidence: {result.vendor_confidence:.2%})")

        if result.line_items:
            print(f"  Line Items: {len(result.line_items)} items")
            for item in result.line_items:
                print(
                    f"    - {item.get('description', 'N/A')}: {item.get('quantity', 0)} "
                    f"@ ${item.get('unit_price', 0):.2f} = ${item.get('total', 0):.2f}"
                )
        else:
            print(f"  Line Items: None extracted")

        print(f"\n  Financial Summary:")
        print(f"    Subtotal: ${result.subtotal:.2f}")
        print(f"    Tax: ${result.tax:.2f}")
        print(f"    Stated Total: ${result.stated_total:.2f}")
        print(f"    Calculated Total: ${result.calculated_total:.2f}")

        if result.conflict_detected:
            print(f"    ⚠️  CONFLICT DETECTED: ${result.stated_total:.2f} vs ${result.calculated_total:.2f}")

        if result.payment_terms:
            print(f"  Payment Terms: {result.payment_terms}")

        print(f"\n  Routing Decision: {result.routing_decision}")
        if result.routing_decision == "APPROVED":
            print("    → Approved for auto-processing")
        elif result.routing_decision == "REVIEW_QUEUE":
            print("    → Flagged for manual review")
        else:
            print("    → Requires human review (low confidence or missing data)")

        # Update routing summary
        routing_summary[result.routing_decision] += 1
        batch_results.append(result)

    # Print batch summary
    print(f"\n\n{'=' * 80}")
    print("BATCH PROCESSING SUMMARY")
    print("=" * 80)
    print(f"Total Documents Processed: {len(batch_results)}")
    print(f"Approved (High Confidence): {routing_summary['APPROVED']}")
    print(f"Review Queue (Medium Confidence): {routing_summary['REVIEW_QUEUE']}")
    print(f"Human Review (Low Confidence/Errors): {routing_summary['HUMAN_REVIEW']}")

    # Calculate averages
    avg_confidence = (
        sum(r.overall_confidence for r in batch_results) / len(batch_results)
        if batch_results
        else 0
    )
    avg_attempts = (
        sum(r.extraction_attempt for r in batch_results) / len(batch_results)
        if batch_results
        else 0
    )

    print(f"\nAverage Confidence: {avg_confidence:.2%}")
    print(f"Average Extraction Attempts: {avg_attempts:.1f}")

    print(f"\n{'=' * 80}")
    print("EXERCISE COMPLETE")
    print("=" * 80)
    print("\nKey Concepts Demonstrated:")
    print("  ✓ Tool-use with forced selection (tool_choice)")
    print("  ✓ Few-shot examples in system prompt")
    print("  ✓ Validation-driven retry loops")
    print("  ✓ Self-correction (conflict detection)")
    print("  ✓ Confidence calibration")
    print("  ✓ Routing based on confidence")
    print("  ✓ Information provenance tracking")
    print("  ✓ Batch-like processing with custom_id")


if __name__ == "__main__":
    main()
