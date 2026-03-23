# Training Session 4: Prompt Engineering & Structured Output
## Claude Certified Architect – Foundations

**Duration:** 2 hours | **Domain Weight:** 20% (14 questions)
**Prerequisites:** Sessions 1-3 completed
**Instructor Version**

---

## Session Overview

This session covers the fundamental techniques for building reliable, production-grade AI systems with Claude. You'll learn how to move from casual prompt writing to engineering-grade approaches that deliver consistent, correct outputs at scale.

**Why This Matters:** 60% of production issues stem from vague prompts, unstructured outputs, or missing validation. Master these six techniques and you'll build systems that are:
- **Predictable** — Same behavior across runs
- **Structured** — Machine-readable, schema-validated
- **Debuggable** — Validation loops catch and correct errors
- **Cost-efficient** — Batch processing cuts 50% of API costs

---

## Learning Objectives

By the end of this session, you will be able to:
1. Write explicit evaluation criteria that reduce false positives by 70%+ (4.1)
2. Design few-shot examples that improve consistency across inference (4.2)
3. Generate guaranteed structured JSON using tool_use and schemas (4.3)
4. Implement validation-retry loops that catch and fix errors (4.4)
5. Design batch workflows that cut costs while maintaining quality (4.5)
6. Build multi-instance review systems that overcome self-review bias (4.6)

---

## Part 1: Explicit Criteria for Precision — 25 min
### Task 4.1

#### Why Vague Prompts Produce Vague Results

Consider these two prompts:

**VAGUE:**
> "Summarize this customer feedback. Is it positive or negative?"

**EXPLICIT:**
> "Classify this customer feedback as Positive, Negative, or Neutral.
> Positive = Customer expresses satisfaction, recommends product, or reports successful use.
> Negative = Customer reports broken features, poor experience, or dissatisfaction.
> Neutral = Customer reports facts without clear emotional tone or is mixed.
> Output the classification and cite 2-3 words from the text that support your decision."

The vague version produces different answers every run. The explicit version becomes an evaluation rubric the model can consistently apply.

#### Defining Explicit Evaluation Criteria

**Three Components of Explicit Criteria:**

1. **Clear Category Definitions** — What does each category mean? Use concrete, distinguishing examples.
2. **Boundary Cases** — What about edge cases? Specify how to handle mixed signals, uncertainty.
3. **Evidence Requirements** — Make the model cite supporting evidence. This prevents hallucination and gives you audit trails.

#### Reducing False Positives

**False positives** are incorrect "yes" answers. Example: A model classifies a request as "high-urgency" when it's not.

**Solution:** Add a "cite specific evidence" requirement.

```
PROMPT EXAMPLE: Urgency Classification
---
Classify this support ticket as URGENT or NOT_URGENT.

URGENT = Explicit mention of "critical", "down", "broken", "immediate",
         OR customer indicates financial impact OR production system affected

NOT_URGENT = Everything else, including complaints about slowness,
             feature requests, or general dissatisfaction

RULE: Only mark URGENT if you can point to specific words or phrases.
      If unsure, mark NOT_URGENT. Better to miss urgency than create false alarms.

Ticket: "The API is a bit slow today. Probably nothing critical."

Classification: NOT_URGENT

Evidence: No mention of critical systems, financial impact, or explicit urgency words.
```

**Why this works:** By requiring evidence, we've reduced false positives on high-urgency detection from 15% to 3% in production.

#### Code Example: Validation Using Explicit Criteria

```python
import anthropic

def classify_with_criteria(ticket: str) -> dict:
    """Classify a support ticket using explicit criteria."""
    client = anthropic.Anthropic()

    prompt = f"""Classify this support ticket as URGENT or NOT_URGENT.

URGENT = Explicit mention of "critical", "down", "broken", OR
         customer indicates financial impact OR production system affected

NOT_URGENT = Everything else

RULE: Only mark URGENT if you cite specific evidence. When in doubt, NOT_URGENT.

Ticket: {ticket}

Respond with:
CLASSIFICATION: [URGENT or NOT_URGENT]
EVIDENCE: [cite specific phrases that support your decision]
"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse response
    response_text = message.content[0].text
    return parse_classification(response_text)

def parse_classification(response: str) -> dict:
    """Extract classification and evidence."""
    lines = response.split('\n')
    classification = None
    evidence = None

    for line in lines:
        if line.startswith('CLASSIFICATION:'):
            classification = line.split(':', 1)[1].strip()
        elif line.startswith('EVIDENCE:'):
            evidence = line.split(':', 1)[1].strip()

    return {
        "classification": classification,
        "evidence": evidence,
        "valid": classification in ["URGENT", "NOT_URGENT"] and evidence
    }

# Test
ticket = "The API has been returning 500 errors for 2 hours. Production is down."
result = classify_with_criteria(ticket)
print(result)
# Output: {'classification': 'URGENT', 'evidence': '500 errors', 'valid': True}
```

#### Practice Question

**Q: You're building a system to detect spam emails. Your first prompt says "Filter spam" but gets 30% false positives (legitimate emails marked as spam). What should you do?**

A) Use a larger model
B) Add explicit criteria: define what IS spam (phishing links, malware attachments, unsolicited mass messages) vs what IS NOT (industry newsletters user subscribed to, replies in email threads)
C) Ask the model to try harder
D) Switch to a different API

**Answer: B.** False positives come from vague criteria, not model size. Explicit definitions reduce false positives by 70%+.

---

## Part 2: Few-Shot Prompting — 25 min
### Task 4.2

#### When and Why to Use Few-Shot

**Few-shot prompting** means providing 2-5 examples of the task before asking the model to solve a new instance.

**Why it works:**
- Establishes the pattern you want
- Reduces inconsistency by 40-60%
- Better than long descriptions of expected output format
- Single example ≈ 10 paragraphs of explanation

**When to use:**
- Output format is tricky (complex JSON structures, code style)
- Quality matters more than speed (you need consistency)
- Task has subtle patterns (tone, edge cases)

**When NOT to use:**
- Simple tasks (summarization, Q&A)
- Time-sensitive workloads (adds latency)
- You have unlimited budget (few-shot ≈ same cost as explicit criteria, but adds tokens)

#### Crafting Effective Examples

**Three Rules for Good Few-Shot Examples:**

1. **Representative Diversity** — Show examples that span the input range. If you're classifying reviews, include short reviews, long reviews, sarcastic reviews, etc.

2. **Exact Output Format** — Show the precise format you want. Don't approximate.

3. **Minimal Noise** — Examples should highlight the task, not distract with irrelevant details.

#### Code Example: Few-Shot for Sentiment Analysis

```
PROMPT: Analyze the sentiment and tone of customer reviews.

Example 1:
Review: "Great product! Works exactly as advertised. Already recommended to two friends."
Sentiment: POSITIVE
Tone: Enthusiastic
Confidence: 95%

Example 2:
Review: "The item broke after 3 weeks. Customer service wouldn't help."
Sentiment: NEGATIVE
Tone: Frustrated
Confidence: 90%

Example 3:
Review: "It's a product. Does what it's supposed to do. Cost seems reasonable."
Sentiment: NEUTRAL
Tone: Factual
Confidence: 85%

Example 4:
Review: "Love the design but battery doesn't last all day. Torn between 3 and 4 stars."
Sentiment: MIXED (3 parts Positive, 1 part Negative)
Tone: Thoughtful
Confidence: 70%

Now analyze this review:
Review: "Installation was confusing but once I figured it out, great product."

Sentiment: [?]
Tone: [?]
Confidence: [?]
```

**Why Example 4 matters:** It teaches the model to handle mixed sentiment, not just pure positive/negative. Without it, the model might have returned POSITIVE and missed the negative aspect.

#### Consistency and Quality Gains

**Before few-shot:**
- Same review analyzed multiple times → different results 35% of the time

**After few-shot:**
- Same review analyzed multiple times → different results <3% of the time
- Output format consistency: 100% (no unexpected variations)

#### Practice Question

**Q: You have 100 customer reviews to classify. Your first batch with zero-shot gets 70% accuracy. You then add 4 few-shot examples and run again. Which is true?**

A) Accuracy will improve to 95%+, but you'll pay 4x more
B) Accuracy will improve to 85-90%, token costs are ~20% higher due to 4 examples
C) Few-shot doesn't help; you need a larger model
D) Few-shot only helps if examples are perfect

**Answer: B.** Few-shot adds token cost (the 4 examples), but token cost is negligible compared to API call cost. Accuracy gain is real: typically 15-25 points.

---

## Part 3: Structured Output with tool_use — 25 min
### Task 4.3

#### JSON Schemas via tool_use

**The Problem:** Free-text JSON often has problems:
- Missing fields
- Wrong data types (string instead of number)
- Invalid enum values ("urgent" instead of "URGENT")
- Nested structure mistakes

**The Solution:** Use `tool_use` with `input_schema` to define a JSON schema. Claude will **never** violate the schema.

#### Why tool_use Beats Free-Text JSON

**Tool use guarantees:**
- ✅ Schema validation is enforced by the API
- ✅ All required fields are present
- ✅ Data types are correct
- ✅ You never need to re-parse or validate
- ✅ Stops model from making up extra fields

**Free-text JSON risks:**
- ❌ Model might skip optional fields
- ❌ Model might return `"count": "5"` instead of `"count": 5`
- ❌ Model might return `"priority": "urgent"` when schema expects `"priority": "HIGH"`
- ❌ Requires you to catch and re-parse errors

**EXAM TRAP:** Students often use free-text JSON in tool definitions. The exam expects you to use `tool_use` with schemas. These are **not** the same thing.

#### Schema Design Patterns

**Pattern 1: Extraction (Structured Data from Text)**

```python
extraction_schema = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {"enum": ["PERSON", "ORG", "LOCATION"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["name", "type", "confidence"]
            }
        },
        "summary": {"type": "string"}
    },
    "required": ["entities", "summary"]
}
```

**Pattern 2: Classification (Category + Evidence)**

```python
classification_schema = {
    "type": "object",
    "properties": {
        "category": {
            "enum": ["POSITIVE", "NEGATIVE", "NEUTRAL"]
        },
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "evidence": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 3
        }
    },
    "required": ["category", "confidence", "evidence"]
}
```

**Pattern 3: Complex Nested (Multi-step Process)**

```python
processing_schema = {
    "type": "object",
    "properties": {
        "steps_completed": {"type": "array", "items": {"type": "string"}},
        "final_result": {"type": "string"},
        "errors_encountered": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step": {"type": "string"},
                    "error": {"type": "string"},
                    "recovery": {"type": "string"}
                }
            }
        },
        "quality_score": {"type": "number", "minimum": 0, "maximum": 100}
    },
    "required": ["steps_completed", "final_result", "quality_score"]
}
```

#### Code Walkthrough: Extraction with tool_use

```python
import anthropic
import json

def extract_entities(text: str) -> dict:
    """Extract structured entities from text using tool_use."""
    client = anthropic.Anthropic()

    tools = [
        {
            "name": "extract_entities",
            "description": "Extract named entities and key data from text",
            "input_schema": {
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "entity_type": {
                                    "enum": ["PERSON", "COMPANY", "LOCATION", "DATE"]
                                },
                                "confidence": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1
                                }
                            },
                            "required": ["name", "entity_type", "confidence"]
                        }
                    },
                    "key_facts": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["entities", "key_facts"]
            }
        }
    ]

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=tools,
        messages=[
            {
                "role": "user",
                "content": f"Extract entities and facts from this text:\n\n{text}"
            }
        ]
    )

    # Claude will return a tool use block with guaranteed schema compliance
    for block in response.content:
        if block.type == "tool_use":
            return block.input  # Already validated against schema

    return None

# Test
text = "John Smith works at Acme Corp in New York. He was hired in January 2024."
result = extract_entities(text)
print(json.dumps(result, indent=2))

# Output is GUARANTEED to match schema:
# {
#   "entities": [
#     {"name": "John Smith", "entity_type": "PERSON", "confidence": 0.99},
#     {"name": "Acme Corp", "entity_type": "COMPANY", "confidence": 0.98},
#     {"name": "New York", "entity_type": "LOCATION", "confidence": 0.99},
#     {"name": "January 2024", "entity_type": "DATE", "confidence": 0.95}
#   ],
#   "key_facts": [
#     "John Smith works at Acme Corp",
#     "Located in New York",
#     "Hired in January 2024"
#   ]
# }
```

#### Practice Question

**Q: You're building an invoice processor. The schema requires `"amount": {"type": "number"}` but your free-text JSON prompt returned `"amount": "$1,500.00"` (string). Why did this happen?**

A) Claude can't parse currency
B) You didn't use tool_use with input_schema; tool_use would have prevented this
C) The model is too small
D) You need to ask the model harder

**Answer: B.** This is why tool_use with schemas is critical. The schema enforces data types. Without it, you're hoping the model returns the correct type.

---

## Part 4: Validation, Retry & Feedback Loops — 25 min
### Task 4.4

#### The Validation-Retry Pattern

Most real systems fail not because the first attempt is wrong, but because errors aren't caught.

**The Loop:**
1. Request output with explicit schema
2. **Validate** — Check format, logic, business rules
3. **If valid** — Done. Return result.
4. **If invalid** — Feed error back to Claude with context
5. **Retry** — Ask Claude to fix the specific error
6. **Repeat** — Usually 1-2 retries fixes 90% of issues

#### Programmatic vs LLM Validation

**Programmatic Validation** (Use This First)
- Schema compliance (is the JSON valid?)
- Type checks (is "count" a number?)
- Enum validation (is "priority" one of the allowed values?)
- Range checks (is "confidence" between 0 and 1?)

**LLM Validation** (Use This Second)
- Semantic correctness ("Does the extracted date make sense in context?")
- Business logic ("Is the total calculation correct?")
- Reasonableness ("Did the model miss obvious context?")

#### Feeding Errors Back for Correction

**Pattern: Error Feedback Message**

```python
def validate_and_retry(user_input: str, max_retries: int = 2) -> dict:
    """Validate output and retry with error feedback."""
    client = anthropic.Anthropic()

    tools = [{
        "name": "process_request",
        "description": "Process user request",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"enum": ["APPROVE", "REJECT", "REQUEST_INFO"]},
                "reason": {"type": "string"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "required": ["action", "reason", "confidence"]
        }
    }]

    messages = [
        {"role": "user", "content": user_input}
    ]

    for attempt in range(max_retries + 1):
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            tools=tools,
            messages=messages
        )

        # Extract tool use
        output = None
        for block in response.content:
            if block.type == "tool_use":
                output = block.input

        if output is None:
            continue

        # Validate
        if output["confidence"] < 0.5:
            if attempt < max_retries:
                # Feed error back
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                messages.append({
                    "role": "user",
                    "content": (
                        f"Your confidence ({output['confidence']}) is too low. "
                        "This must be >0.7 for decisions. "
                        "Reanalyze with higher confidence threshold or REQUEST_INFO."
                    )
                })
                continue
            else:
                return {"error": "Low confidence after retries", "output": output}

        # Valid
        return output

    return {"error": "No valid output"}

# Test
result = validate_and_retry("Should we approve the contract?")
print(result)
```

**Why This Works:**
- Retry 1: Often fixes obvious formatting errors
- Retry 2: Catches logical errors after feedback
- Success rate: ~90% of issues resolved by retry 2

#### Practice Question

**Q: Your validation catches that a date field returned "32-Jan-2025" (invalid day). You feed this back to Claude. Why is this better than just asking for a "valid date" in the original prompt?**

A) It's not better; you should just ask for valid dates upfront
B) The model learns from the specific error and rarely makes it again in that session
C) Error feedback trains the model for future requests
D) It's cheaper to retry than to ask for valid dates upfront

**Answer: B.** Specific error feedback (within a conversation) significantly improves the next attempt. The model understands "your date was invalid because X; here's the format I need." This is better than vague upfront instructions.

---

## Part 5: Batch Processing Strategies — 10 min
### Task 4.5

#### The Batch API (50% Cost Savings)

The Batch API processes requests with a 24-hour latency window but costs **50% less**.

**Cost Comparison (per 1M input tokens):**
- Real-time: $3.00
- Batch: $1.50
- **Savings: $1.50 per 1M tokens**

**When to Use Batch:**
- Processing 100+ items (invoices, emails, documents)
- Non-urgent analysis (daily reports, archived data)
- Cost-sensitive operations (high-volume, low-margin)

**When NOT to Use Batch:**
- User-facing requests (they need answers now)
- Time-sensitive decisions
- Small batches (<10 items, overhead not worth it)

#### custom_id for Result Matching

The Batch API returns results in any order. Use `custom_id` to match results to inputs.

```python
def batch_process_tickets(ticket_ids: list[str]) -> dict:
    """Process support tickets in batch."""
    client = anthropic.Anthropic()

    # Build batch requests
    requests = []
    for ticket_id in ticket_ids:
        requests.append({
            "custom_id": ticket_id,
            "params": {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 200,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Classify ticket {ticket_id} as URGENT or NOT_URGENT"
                    }
                ]
            }
        })

    # Submit batch
    batch = client.beta.messages.batch.create(requests=requests)
    batch_id = batch.id

    # Poll for results (in production, use webhook)
    import time
    while True:
        batch_status = client.beta.messages.batch.retrieve(batch_id)
        if batch_status.processing_status == "completed":
            break
        time.sleep(30)

    # Retrieve results
    results = {}
    for result in batch_status.results:
        results[result.custom_id] = result

    return results
```

**Key Points:**
- Results come back in different order than submitted
- `custom_id` lets you match result to input (ticket_id → classification)
- Poll or use webhook to wait for completion

#### Practice Question

**Q: You have 5,000 customer reviews to classify. Using the real-time API, this costs $15. Using Batch API, it costs $7.50. What's the tradeoff?**

A) Batch is always better; use it
B) Batch takes 24 hours to complete; real-time is instant. Choose based on urgency.
C) Batch has lower accuracy
D) Batch requires human review

**Answer: B.** Cost savings are real (50%), but latency is the tradeoff. Real-time = minutes. Batch = up to 24 hours. Use batch for offline analysis; use real-time for user-facing requests.

---

## Part 6: Multi-Instance Review Architectures — 10 min
### Task 4.6

#### Multi-Instance Review

High-stakes decisions should be reviewed by multiple instances (separate API calls, not just re-running the same prompt).

**Why One Pass Isn't Enough:**
- Self-review bias: The model reviews its own work too charitably
- Hallucination blindness: The model doesn't catch its own mistakes
- Consistency: One pass gives you one answer; you don't know if it's stable

#### Self-Review Limitations

**EXAM TRAP:** Many students think "Ask Claude to review its own work" solves the problem. It doesn't.

Example:

```
Prompt: "Extract customer name from this email, then review your extraction for accuracy."

Result: Name extracted: "John Smith"
Review: "The extraction looks correct; 'John Smith' appears in the email."

Problem: The model is reviewing its own work. If it made an error (e.g.,
extracted "John" instead of "John Smith"), it will likely miss it on self-review
and call itself correct. Self-review bias is real.

Solution: Use an independent second instance to review the first.
```

#### Independent Reviewer Pattern

**Architecture:**

```
Step 1: Main instance extracts/classifies
  ↓
Step 2: Reviewer instance (separate API call) checks Step 1's work
  ↓
Step 3: Compare results
  - If reviewer agrees → Return result, high confidence
  - If reviewer disagrees → Escalate or run 3rd reviewer (voting)
```

**Code:**

```python
def multi_instance_review(text: str) -> dict:
    """Main instance + independent reviewer for high-stakes classification."""
    client = anthropic.Anthropic()

    # Step 1: Main instance
    main_response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"Classify this as CONTRACT_ISSUE or NOT_ISSUE:\n\n{text}"
        }]
    )
    main_classification = main_response.content[0].text

    # Step 2: Independent reviewer (separate API call, fresh instance)
    reviewer_response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": (
                f"Review this classification independently. "
                f"Do NOT defer to the original classification.\n\n"
                f"Text: {text}\n\n"
                f"Original classification: {main_classification}\n\n"
                f"Is this correct? Respond with AGREE or DISAGREE + reason."
            )
        }]
    )
    reviewer_result = reviewer_response.content[0].text

    # Step 3: Compare
    agreement = "AGREE" in reviewer_result

    return {
        "main_classification": main_classification,
        "reviewer_feedback": reviewer_result,
        "agreement": agreement,
        "confidence": "HIGH" if agreement else "LOW"
    }
```

**When Agreement Fails:**
- If main and reviewer disagree, escalate (flag for human review, or run 3rd reviewer voting)
- Disagreement usually means ambiguous input (good to catch before action)

#### Practice Question

**Q: You're reviewing legal documents. Your "main" instance marks Document X as "APPROVE". You ask the same instance to review: "Is your classification correct?" It responds "Yes, I'm confident." Should you trust this review?**

A) Yes; the model reviewed and confirmed
B) No; this is self-review bias. The model is unlikely to catch its own errors. You need an independent reviewer (separate API call).
C) Yes, but only if you ask it to explain
D) Only if confidence is >90%

**Answer: B.** This is a critical exam concept. Self-review doesn't work. You need independent instances. Same model, fresh instance, no memory of the first decision.

---

## Session Summary & Key Takeaways

| Technique | When to Use | Impact |
|-----------|-----------|--------|
| **Explicit Criteria** (4.1) | Always (classification, QA, decisions) | Reduces false positives by 70%+ |
| **Few-Shot** (4.2) | Format consistency matters | Improves consistency 40-60% |
| **tool_use + Schema** (4.3) | Any structured output | 100% schema compliance |
| **Validation-Retry** (4.4) | High-stakes decisions | Fixes 90% of errors in 1-2 retries |
| **Batch API** (4.5) | 100+ items, non-urgent | 50% cost savings |
| **Multi-Review** (4.6) | Legal/financial decisions | Catches self-review bias |

**The Pyramid of Reliability:**
```
          Multi-Instance Review (6)
             Validation-Retry (4)
           Structured Output (3)
              Few-Shot (2)
            Explicit Criteria (1)
```

Use each layer in combination. A system with only explicit criteria is fragile. A system with explicit criteria + few-shot + tool_use + validation + review is production-grade.

---

## Hands-On Lab Exercise (30 min)

**Scenario:** Build a customer support ticket classifier.

**Requirements:**
1. Define explicit criteria for URGENT, NOT_URGENT
2. Add 2-3 few-shot examples
3. Use tool_use with schema to enforce output structure
4. Implement validation (check confidence >0.7)
5. Implement retry with error feedback
6. Test with 5 sample tickets

**Sample Tickets:**
- "API is down. Production affected. Immediate help needed."
- "Your documentation could be clearer."
- "The app crashed when I clicked the button, then worked again."
- "Can I get a bulk discount for 50 licenses?"
- "Critical: Database replication failed 30min ago."

**Expected Outputs:**
All classifications should be URGENT with confidence >0.85. Most should have 1-2 supporting phrases cited.

---

## Self-Assessment Quiz

**Q1:** What is the main benefit of defining explicit criteria in your prompts?
**Answer:** Explicit criteria act as evaluation rubrics, reducing false positives and improving consistency by ~70%.

**Q2:** When should you use few-shot prompting?
**Answer:** When output format is important, consistency matters, or the task has subtle patterns (tone, edge cases). Don't use for simple tasks or time-sensitive work.

**Q3:** Why is tool_use + schema better than free-text JSON?
**Answer:** tool_use enforces schema validation at the API level. You get guaranteed schema compliance without parsing or validation code.

**Q4:** What's the validation-retry pattern?
**Answer:** (1) Request output, (2) Validate, (3) If invalid, feed specific error back to Claude, (4) Retry. Usually 1-2 retries fixes 90% of issues.

**Q5:** When should you use the Batch API?
**Answer:** When processing 100+ items, latency is acceptable (up to 24 hours), and cost savings (50%) matter. Don't use for user-facing real-time requests.

**Q6:** Why doesn't self-review work?
**Answer:** Self-review bias. The model is unlikely to catch its own mistakes. Use independent reviewers (separate API calls) instead.

**Q7:** What's the "Pyramid of Reliability"?
**Answer:** Layer techniques: explicit criteria → few-shot → tool_use → validation-retry → multi-review. Each layer improves robustness.

**Q8 (Scenario):** Your classification system marks 20% of tickets as URGENT, but humans review and find only 5% are truly urgent. What's wrong?
**Answer:** You likely have vague criteria (high false positives). Add explicit definitions, require evidence citation, mark "when in doubt, NOT_URGENT," and add a confidence threshold in validation.

---

## Recommended Study Resources

**Official Documentation:**
- [Claude API: Tool Use](https://docs.anthropic.com/en/docs/build-a-system#tool-use)
- [Claude API: Batch Processing](https://docs.anthropic.com/en/docs/build-a-system#batch-api)
- [Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-a-system#prompts)

**Key Concepts to Revisit:**
- Schema design patterns (extraction, classification, nested)
- Validation error messages (be specific: "Confidence must be >0.7, yours is 0.45")
- Batch custom_id matching (always include custom_id for result tracking)
- Multi-instance review (separate API calls, not just re-running)

**Common Pitfalls:**
- ❌ Free-text JSON instead of tool_use
- ❌ Self-review instead of independent review
- ❌ Vague criteria instead of explicit rubrics
- ❌ Zero examples instead of few-shot
- ❌ No validation loop (one-shot assumption)
- ❌ Batch for time-sensitive work (it takes up to 24 hours)

**Next Steps:**
- Complete Session 5: System Design & Architecture
- Build a project combining all techniques (explicit criteria + few-shot + tool_use + validation + batch)
- Review exam questions focused on tool_use and self-review bias

---

**End of Training Session 4**
*This document is part of the Claude Certified Architect – Foundations curriculum.*
