# Critical Exam Gaps - Quick Reference Guide

**Purpose:** This document addresses the 7 most critical gaps in the study materials that will appear on the CCA exam. Use this as a supplement to the main study guides.

---

## Gap 1: Tool Choice Mechanics (Domain 2)

### What's Missing
The study materials mention `tool_choice` in exercises but don't systematically compare the three settings in Domain 2.

### Exam Question Likely Format
> "Which `tool_choice` setting guarantees that the model will call a tool, and what's the risk?"

### Complete Answer

```python
# The Three Tool Choice Settings

# 1. tool_choice="auto" (DEFAULT)
#    - Model may return text OR call tool
#    - GUARANTEE: NONE
#    - Use: Optional extraction where text response is acceptable
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    tools=tools,
    tool_choice="auto",  # ❌ TRAP: Might get text instead of structured output
    messages=[...]
)

# 2. tool_choice="any"
#    - Model MUST call a tool (any tool, if multiple available)
#    - GUARANTEE: ✅ Tool WILL be called
#    - Use: When mandatory extraction is required
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    tools=tools,
    tool_choice="any",  # ✅ CORRECT for mandatory extraction
    messages=[...]
)

# 3. tool_choice with forced selection
#    - Model MUST call specific tool
#    - GUARANTEE: ✅ Specific tool AND schema will be enforced
#    - Use: Single extraction format, two-stage pipelines
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    tools=extraction_tools,
    tool_choice={"type": "tool", "name": "extract_invoice"},  # ✅ Forced
    messages=[...]
)
```

### Comparison Table for Exam

| Setting | Guarantee | When to Use | When NOT to Use |
|---------|-----------|-------------|-----------------|
| `"auto"` | NONE - may skip | Optional extraction (user might want text) | Mandatory extraction where structure is required |
| `"any"` | Must call some tool | Unknown document type, multiple extraction tools | When specific tool output format required |
| `{"type": "tool", "name": "X"}` | Specific tool forced | Single extraction format, two-stage pipeline | When document type varies (inflexible) |

### Common Trap
Students often think `tool_choice="auto"` guarantees tool use. **IT DOES NOT.**
- `tool_choice="auto"` = Model might respond with text instead of calling the tool
- `tool_choice="any"` = Tool WILL be called (your guarantee)

---

## Gap 2: Lost in the Middle Effect (Domain 5)

### What's Missing
This critical concept is completely absent from Domain 5. It's fundamental to long-conversation agent behavior.

### Exam Question Likely Format
> "In a 40-turn conversation, you notice the agent keeps asking about information provided in turn 15 (the middle of the conversation). Why? How would you fix it?"

### What is "Lost in the Middle"?

In long contexts:
- **Beginning of context:** Well-retained (initial system prompt, first query)
- **Middle of context:** Often missed/under-weighted by the model
- **End of context:** Well-retained (recent messages)

This is an empirical finding in transformer attention patterns.

### Practical Impact Example

```
Turns 1-5 (Beginning):
- System prompt: "You are a customer service agent"
- User: "I want to return a order"
✅ Model remembers these well

Turns 6-35 (Middle - LOST):
- Order details retrieved
- Return policy discussed
- Cost analysis for refund
❌ Model has weaker memory of these

Turns 36-40 (End - Recent):
- "Process the refund"
- "Confirm amount: $250"
✅ Model remembers these well
```

### Solution: Prevent Lost in the Middle

**Strategy 1: Summarization at Checkpoints**
```python
# After turn 20, create structured summary
checkpoint_summary = """
KEY DECISIONS TO REMEMBER:
- Customer wants refund for order #12345
- Order cost: $250
- Return policy: 30 days (within window)
- Condition: Unopened
- Decision: APPROVE refund

Previous conversation replaced above summary.
Continue with next customer issue.
"""

# Replace turns 6-20 with the summary
messages = [
    {"role": "system", "content": checkpoint_summary},
    # ... keep turns 21-40 in full detail
]
```

**Strategy 2: Information Placement**
```python
# For critical information in long context:
# Place at BEGINNING (with system prompt) AND END (recent messages)

system_prompt = """You are a customer service agent.
CUSTOMER: John Smith, Order #12345, Status: Return Pending, Amount: $250
Your task: Resolve the return issue."""

# Then in conversation, repeat critical facts near the end
messages = [
    ... [middle conversation, turns 1-35] ...
    {
        "role": "user",
        "content": "Before final decision: Confirm - we're refunding John Smith $250 for order #12345. Correct?"
    }
]
```

**Strategy 3: Token Budget Management**
```python
# For N-turn conversation with token limit:
# Allocate token budget:
# - 15% for initial context (system + first few turns)
# - 20% for checkpoint summaries
# - 35% for recent 5-10 turns
# - 30% for tool descriptions and new reasoning

def manage_lost_in_middle(messages: list, max_tokens: int = 150000) -> list:
    """
    Manage context to prevent lost-in-the-middle effect.
    """
    if len(messages) < 10:
        return messages  # Too short, keep all

    # Strategy: Keep first 3 turns, last 5 turns, summarize middle
    initial = messages[:3]
    recent = messages[-5:]
    middle = messages[3:-5]

    # Create summary of middle turns
    middle_summary = create_summary(middle)

    return initial + [middle_summary] + recent
```

### Exam Key Points
- Lost in the middle is real, not a misconception
- Affects long conversation agents (>20 turns)
- Fixed by strategic information placement (beginning/end) or summarization
- Critical for production reliability

---

## Gap 3: Silent Error Suppression Anti-Pattern (Domain 5)

### What's Missing
The study materials don't explicitly discuss the anti-pattern of masking failures with generic success responses.

### Exam Question Likely Format
> "A tool returns `{"status": "success", "result": null}` when it actually fails. What problem does this cause in multi-agent systems? How should it be fixed?"

### The Anti-Pattern

```python
# ❌ BAD: Silent error suppression
def fetch_customer_data(customer_id: str) -> dict:
    try:
        result = database.query(customer_id)
        return {"status": "success", "data": result}
    except DatabaseError:
        # ERROR IS MASKED HERE!
        return {"status": "success", "data": None}  # ❌ Lying to agent
```

**Why this is dangerous:**
1. Agent thinks operation succeeded
2. Agent might use `None` data anyway
3. Agent repeats the operation (cascading failures)
4. Human observers see only "success", missing real failures
5. Reliability metrics hide actual problems

### The Fix: Structured Error Propagation

```python
# ✅ GOOD: Explicit error response
def fetch_customer_data(customer_id: str) -> dict:
    try:
        result = database.query(customer_id)
        return {
            "status": "success",
            "data": result,
            "confidence": 0.95
        }
    except DatabaseError as e:
        # ERROR IS EXPLICIT
        return {
            "status": "error",
            "error": {
                "category": "transient",  # Transient = retry might work
                "message": f"Database connection failed: {str(e)}",
                "isRetryable": True,
                "suggestedNextStep": "Retry with exponential backoff"
            },
            "confidence": 0.0
        }
```

### Multi-Agent Cascade Example

**Scenario:** Search → Analysis → Synthesis pipeline

```
Turn 1: Search agent finds 3 results ✅
Turn 2: Analysis agent tries to analyze results
  - Analysis tool fails silently: {"status": "success", "insights": []}
  - ❌ Agent thinks analysis succeeded but got empty results

Turn 3: Synthesis agent tries to compile report
  - No insights to compile
  - Produces bad report
  - ❌ User sees bad report, doesn't know analysis failed

WITH STRUCTURED ERRORS:
Turn 2: Analysis tool explicitly fails: {"status": "error", "category": "api_limit", ...}
  - Coordinator sees failure
  - ✅ Re-delegates analysis or routes to human review
  - ✅ Bad report prevented
```

### Error Response Template

```python
ERROR_RESPONSE_TEMPLATE = {
    "status": "error",
    "error": {
        "category": "transient" or "permanent" or "permission" or "not_found",
        "message": "Human-readable error description",
        "isRetryable": True or False,  # Can retry fix this?
        "suggestedNextStep": "Retry", "Escalate", "Skip", etc.
    },
    "data": {...}  # Partial data if available (graceful degradation)
}
```

### Exam Key Points
- Silent errors are anti-pattern
- Always propagate structured error information
- Multi-agent systems require explicit error handling
- Graceful degradation > silent failure
- "Success" with no data = actual failure

---

## Gap 4: Scratchpad Persistence for Multi-Phase Tasks (Domain 5)

### What's Missing
No mention of scratchpad files for persisting findings across multiple agent phases.

### Exam Question Likely Format
> "A research coordinator delegates to three subagents sequentially: search, analysis, synthesis. How can the synthesis subagent access findings from the search phase without exceeding context limits?"

### Scratchpad Pattern

```python
# Phase 1: Search Subagent
# ===========================
search_findings = """
# Search Findings (Updated 2026-03-22 10:00)

## Sources Found
- URL: https://example.com/safety, Confidence: 0.95
- URL: https://example.com/alignment, Confidence: 0.88
- ...

## Key Quotes
- "Interpretability is..." (Source: safety URL)
- ...

## Meta
- Search completed: 10:05 UTC
- Sources found: 5 total
"""

# Write to scratchpad (file, database, or shared memory)
scratchpad.write("research_findings", search_findings)

# Phase 2: Analysis Subagent
# ==========================
search_context = scratchpad.read("research_findings")  # ✅ Access previous phase

analysis_findings = f"""
{search_context}

# Analysis Results (Updated 2026-03-22 10:30)

## Themes Identified
- Theme A: Interpretability (3 sources)
- Theme B: Governance (2 sources)
- ...

## Key Insights
- Insight 1: ...
"""

scratchpad.write("research_findings", analysis_findings)  # Append/update

# Phase 3: Synthesis Subagent
# ============================
accumulated_findings = scratchpad.read("research_findings")

# Can now compile full report from accumulated findings
report = synthesize_report(accumulated_findings)
```

### Token Efficiency Comparison

**WITHOUT Scratchpad (All in Context):**
```
Phase 1 (Search):    5k tokens output → 5k tokens in context
Phase 2 (Analysis):  10k tokens output → 15k total in context
Phase 3 (Synthesis): 20k tokens output → 35k total in context

Total context burden: 35k tokens for synthesis
```

**WITH Scratchpad (Persistence):**
```
Phase 1 (Search):    5k tokens → written to scratchpad
Phase 2 (Analysis):  10k tokens → read scratchpad (1k), write updated (8k)
Phase 3 (Synthesis): 20k tokens → read scratchpad (8k), generate report

Total context burden: Each phase only ~10-15k tokens
Context saved: ~50%
```

### Implementation Approaches

**Option 1: File-Based**
```python
import json
import os

class FileBasedScratchpad:
    def __init__(self, base_path: str = "/tmp/scratchpad"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def write(self, key: str, content: str):
        with open(f"{self.base_path}/{key}.txt", "w") as f:
            f.write(content)

    def read(self, key: str) -> str:
        with open(f"{self.base_path}/{key}.txt", "r") as f:
            return f.read()

scratchpad = FileBasedScratchpad()
scratchpad.write("phase1_findings", findings_text)
phase1_context = scratchpad.read("phase1_findings")
```

**Option 2: Shared Memory (In-Process)**
```python
class MemoryScratchpad:
    def __init__(self):
        self.data = {}

    def write(self, key: str, content: str):
        self.data[key] = {
            "content": content,
            "timestamp": time.time()
        }

    def read(self, key: str) -> str:
        return self.data.get(key, {}).get("content", "")

# Passed between phases
scratchpad = MemoryScratchpad()
```

**Option 3: Database-Backed**
```python
class DatabaseScratchpad:
    def __init__(self, db_url: str):
        self.db = setup_connection(db_url)

    def write(self, key: str, content: str):
        self.db.execute(
            "INSERT INTO scratchpad (key, content) VALUES (?, ?)",
            (key, content)
        )

    def read(self, key: str) -> str:
        result = self.db.execute(
            "SELECT content FROM scratchpad WHERE key = ? ORDER BY timestamp DESC LIMIT 1",
            (key,)
        ).fetchone()
        return result[0] if result else ""
```

### Exam Key Points
- Scratchpad prevents context explosion in multi-phase tasks
- Enables cross-phase knowledge transfer
- Can be file, memory, or database backed
- Critical for complex agent workflows
- Reduces overall token consumption

---

## Gap 5: Batch API Economics (Domain 4)

### What's Missing
Batch API mentioned 122 times but lacks specific cost/timing analysis and when NOT to use.

### Exam Question Likely Format
> "You need to extract data from 500 documents. Batch API saves 50%, but processing takes up to 24 hours. Should you use it? What are the tradeoffs?"

### Cost & Timing Analysis

```python
# REGULAR API CALLS
# =================
100 requests × 1000 tokens = $0.30 per request
100 × $0.30 = $30.00
Time: Immediate (seconds)
Cost: $30.00

# BATCH API
# ==========
100 requests × 1000 tokens = $0.15 per request (50% discount)
100 × $0.15 = $15.00
Time: Up to 24 hours (usually 5-30 minutes)
Cost: $15.00

SAVINGS: $15.00 per 100 requests = 50%
```

### When to Use Batch API ✅

```python
# 1. Non-blocking background tasks
if not user_waiting:  # ✅ User doesn't need immediate response
    use_batch_api()

# 2. Bulk processing (100+ items)
if num_documents > 100:  # ✅ Cost savings significant
    use_batch_api()

# 3. Deadline > 1 hour
if deadline_minutes > 60:  # ✅ 24-hour window acceptable
    use_batch_api()

# 4. Cost-sensitive operations
if budget_constrained:  # ✅ 50% savings critical
    use_batch_api()

# Example: Nightly data processing
batch_requests = [
    {"custom_id": "doc_001", "params": {...}},
    {"custom_id": "doc_002", "params": {...}},
    # ... 500 more
]
client.beta.messages.batches.create(requests=batch_requests)
# Process nightly, results available in morning
```

### When NOT to Use Batch API ❌

```python
# 1. User blocking (needs immediate response)
if user_is_waiting:  # ❌ User cannot wait 24 hours
    use_regular_api()

# 2. Interactive agent workflows
if requires_immediate_feedback:  # ❌ Agent needs next step now
    use_regular_api()

# 3. Sub-minute SLA
if sla_milliseconds < 60000:  # ❌ Batch too slow
    use_regular_api()

# 4. Latency-sensitive operations
if latency_critical:  # ❌ 24-hour window unacceptable
    use_regular_api()

# Example: Real-time customer service
user_message = "Help me with my account"
# ❌ DON'T use batch (customer waiting)
response = client.messages.create(...)  # ✅ Regular API
```

### Batch Request Structure

```python
# Each batch request needs custom_id for result correlation
batch_requests = [
    {
        "custom_id": "extraction_001",
        "params": {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": "Extract data from document 1..."}]
        }
    },
    {
        "custom_id": "extraction_002",
        "params": {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": "Extract data from document 2..."}]
        }
    }
]

# Submit batch
batch = client.beta.messages.batches.create(requests=batch_requests)
batch_id = batch.id

# Later: retrieve results
results = client.beta.messages.batches.results(batch_id)
for result in results:
    custom_id = result.custom_id  # ✅ Correlate back to original doc
    extracted_data = result.result  # Process results
```

### Anti-Pattern: Blocking Workflow with Batch

```python
# ❌ BAD: Using batch for blocking user workflow
@app.post("/extract")
def extract_documents(docs: list):
    batch_id = submit_batch(docs)
    # User waiting...
    # Process takes up to 24 hours...
    # ❌ User abandons page, timeout, etc.

# ✅ GOOD: Queue for background processing
@app.post("/extract")
def extract_documents(docs: list):
    job_id = str(uuid.uuid4())
    enqueue_batch_job(job_id, docs)  # Queue for later
    return {"job_id": job_id, "status": "queued"}

@app.get("/extract/{job_id}")
def check_extraction_status(job_id: str):
    results = get_batch_results(job_id)
    if results:
        return {"status": "complete", "data": results}
    else:
        return {"status": "processing"}
```

### Exam Key Points
- 50% cost savings from Batch API
- Up to 24-hour processing window
- Use `custom_id` for result correlation
- NEVER use batch for blocking user workflows
- Perfect for nightly processing, bulk extractions
- Not suitable for real-time agents

---

## Gap 6: Multi-Pass Review Architecture (Domain 4)

### What's Missing
Multi-pass review patterns not systematically covered. Students don't know about avoiding "attention dilution."

### Exam Question Likely Format
> "You're reviewing code for security issues AND performance issues. Should you do this in one pass or multiple passes? Why?"

### The Problem: Single-Pass Review

```
Single pass review of:
- Security? Check
- Performance? Check
- Logic? Check
- Style? Check

Problem: Context switching causes attention dilution
- Brain can't simultaneously hold 4 concerns
- Miss issues in lower-priority concerns
- 30-50% lower detection rate for non-primary concerns
```

### The Solution: Multi-Pass Architecture

```python
def multi_pass_code_review(code: str) -> dict:
    """Review code in separate passes per concern."""

    # PASS 1: Security Review Only
    security_pass = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{
            "role": "user",
            "content": f"""Review ONLY for security issues:
- SQL injection vulnerabilities
- XSS vulnerabilities
- Authentication bypass
- Permission escalation
- Hardcoded credentials

IGNORE: Performance, style, logic

Code:
{code}"""
        }]
    )
    security_findings = parse_findings(security_pass)

    # PASS 2: Performance Review Only
    perf_pass = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{
            "role": "user",
            "content": f"""Review ONLY for performance issues:
- Algorithm complexity (O(n²) where O(n) possible)
- N+1 database queries
- Missing caches
- Resource leaks
- Inefficient string operations

IGNORE: Security, style, logic

Code:
{code}"""
        }]
    )
    perf_findings = parse_findings(perf_pass)

    # PASS 3: Logic & Style Review Only
    logic_pass = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{
            "role": "user",
            "content": f"""Review ONLY for logic and style:
- Correctness of algorithm
- Edge case handling
- Code style conventions
- Variable naming
- Function organization

IGNORE: Security, performance

Code:
{code}"""
        }]
    )
    logic_findings = parse_findings(logic_pass)

    # Combine all findings
    return {
        "security": security_findings,
        "performance": perf_findings,
        "logic": logic_findings,
        "total_issues": len(security_findings) + len(perf_findings) + len(logic_findings)
    }
```

### Comparative Analysis: Single vs Multi-Pass

```
Single Pass (1 API call):
- Cost: $0.30
- Time: 30 seconds
- Security issues found: 2/5 (40%)
- Performance issues found: 1/4 (25%)
- Logic issues found: 3/5 (60%)
- Quality: 40%

Multi-Pass (3 API calls):
- Cost: $0.90 (3x cost, but still cheap)
- Time: 90 seconds
- Security issues found: 5/5 (100%)
- Performance issues found: 4/4 (100%)
- Logic issues found: 5/5 (100%)
- Quality: 100%

Cost/benefit: 3x cost for 2.5x better quality = worthwhile
```

### When to Use Multi-Pass

```python
# ✅ Use multi-pass when:
multi_pass_if = [
    "Review is for production code",
    "High quality requirement (security-critical)",
    "Multiple concerns are important",
    "Cost is secondary to quality",
]

# ❌ Single-pass acceptable when:
single_pass_if = [
    "Quick feedback on draft code",
    "Cost is critical constraint",
    "Single concern (only style check)",
    "Limited context/token budget",
]
```

### Implementation Pattern

```python
class CodeReviewer:
    def __init__(self, client):
        self.client = client
        self.passes = {
            "security": "Check for security vulnerabilities...",
            "performance": "Check for performance issues...",
            "logic": "Check for logic and correctness...",
        }

    def review(self, code: str, passes: list = None) -> dict:
        """
        Review code with specified passes.

        Args:
            code: Code to review
            passes: List of passes to run (default: all)

        Returns:
            Dict with findings per pass
        """
        passes = passes or list(self.passes.keys())
        results = {}

        for pass_name in passes:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                messages=[{
                    "role": "user",
                    "content": f"{self.passes[pass_name]}\n\nCode:\n{code}"
                }]
            )
            results[pass_name] = response.content[0].text

        return results
```

### Exam Key Points
- Single pass causes attention dilution
- Multi-pass separates concerns, improves quality
- Cost 3x but quality often 2.5x better
- Worthwhile for production/security-critical code
- Each pass ignores other concerns

---

## Gap 7: Confidence Calibration with Labeled Validation Sets (Domain 5)

### What's Missing
Confidence calibration mentioned but no discussion of measuring against labeled validation sets.

### Exam Question Likely Format
> "Your extraction model returns 95% confidence on all fields. In reality, 70% are correct. What's wrong? How would you fix it?"

### The Problem: Miscalibrated Confidence

```python
# Model returns:
extraction = {
    "invoice_number": {"value": "INV-001", "confidence": 0.95},
    "vendor": {"value": "Unknown Corp", "confidence": 0.95},
    "total": {"value": 1500.00, "confidence": 0.95}
}

# But actual accuracy per field:
actual_accuracy = {
    "invoice_number": 0.98,  # Actually very accurate
    "vendor": 0.65,          # Much lower than reported!
    "total": 0.72            # Much lower than reported!
}

# Problem: Model is OVERCONFIDENT
# - Confidence doesn't match actual correctness
# - Routes all to "auto-approve" based on false confidence
# - Bad extractions slip through
```

### The Solution: Calibration Against Labeled Data

```python
class ConfidenceCalibrator:
    def __init__(self):
        self.validation_set = []  # Labeled gold-standard data

    def add_labeled_example(self, extraction: dict, ground_truth: dict, confidence: dict):
        """
        Add labeled example for calibration.

        Args:
            extraction: Model's extracted values
            ground_truth: Correct values (human-labeled)
            confidence: Model's confidence scores
        """
        self.validation_set.append({
            "extraction": extraction,
            "ground_truth": ground_truth,
            "confidence": confidence
        })

    def calibrate(self) -> dict:
        """
        Compute actual accuracy per confidence bucket.
        """
        # Group by confidence bins
        bins = {
            "0.0-0.2": [],
            "0.2-0.4": [],
            "0.4-0.6": [],
            "0.6-0.8": [],
            "0.8-1.0": [],
        }

        for item in self.validation_set:
            confidence = item["confidence"]
            is_correct = item["extraction"] == item["ground_truth"]

            # Find appropriate bin
            if confidence < 0.2:
                bins["0.0-0.2"].append(is_correct)
            elif confidence < 0.4:
                bins["0.2-0.4"].append(is_correct)
            elif confidence < 0.6:
                bins["0.4-0.6"].append(is_correct)
            elif confidence < 0.8:
                bins["0.6-0.8"].append(is_correct)
            else:
                bins["0.8-1.0"].append(is_correct)

        # Compute accuracy per bin
        calibration_curve = {}
        for bin_name, results in bins.items():
            if results:
                accuracy = sum(results) / len(results)
                calibration_curve[bin_name] = accuracy

        return calibration_curve

# Usage
calibrator = ConfidenceCalibrator()

# Add 100 labeled examples
for i in range(100):
    extraction = model.extract(documents[i])
    ground_truth = human_labels[i]
    confidence = extraction["confidence"]

    calibrator.add_labeled_example(extraction, ground_truth, confidence)

# Compute calibration curve
calibration = calibrator.calibrate()

# Results might show:
# 0.0-0.2 confidence: 45% actual accuracy (model underconfident)
# 0.2-0.4 confidence: 55% actual accuracy
# 0.4-0.6 confidence: 65% actual accuracy
# 0.6-0.8 confidence: 80% actual accuracy (starting to match)
# 0.8-1.0 confidence: 92% actual accuracy (well-calibrated)
```

### Calibration vs Accuracy

```python
# ACCURACY: "How many predictions are correct?"
accuracy = correct_predictions / total_predictions

# CALIBRATION: "When model says 80% confidence, is it right 80% of the time?"
# Example:
# - Model says 80% confidence on 100 predictions
# - 82 of them are actually correct
# - Model is well-calibrated (80% ≈ 82%)

# Example of poor calibration:
# - Model says 95% confidence on 100 predictions
# - Only 70 are actually correct
# - Model is OVERCONFIDENT (95% reported vs 70% actual)
```

### Using Calibration for Routing

```python
def route_extraction(extraction: dict, calibration_curve: dict) -> str:
    """
    Route based on calibrated confidence, not raw confidence.
    """
    raw_confidence = extraction["confidence"]

    # Use calibration curve to get actual expected accuracy
    if raw_confidence < 0.2:
        actual_confidence = calibration_curve.get("0.0-0.2", 0.5)
    elif raw_confidence < 0.4:
        actual_confidence = calibration_curve.get("0.2-0.4", 0.5)
    elif raw_confidence < 0.6:
        actual_confidence = calibration_curve.get("0.4-0.6", 0.5)
    elif raw_confidence < 0.8:
        actual_confidence = calibration_curve.get("0.6-0.8", 0.5)
    else:
        actual_confidence = calibration_curve.get("0.8-1.0", 0.9)

    # Route based on actual (calibrated) confidence
    if actual_confidence >= 0.85:
        return "AUTO_APPROVE"
    elif actual_confidence >= 0.70:
        return "REVIEW_QUEUE"
    else:
        return "HUMAN_REVIEW"
```

### Exam Key Points
- Confidence calibration ≠ accuracy
- Measure against labeled validation sets (100+ examples)
- Group by confidence bins and compute actual accuracy
- Use calibration curve for routing decisions
- Overconfidence causes false auto-approvals
- Underconfidence causes unnecessary escalations

---

## Quick Reference: When to Use What

### Tool Choice Settings
- **"auto"**: Optional extraction, text response OK
- **"any"**: Mandatory extraction, any tool
- **Forced**: Single specific extraction tool required

### Context Management
- **Scratchpad**: Multi-phase agent tasks
- **Checkpoint summaries**: Long conversations (>20 turns)
- **Lost-in-the-middle prevention**: Keep info at beginning & end

### Error Handling
- **Always propagate errors**: Never mask with generic success
- **Structured errors**: Include category, retryable, suggested next step
- **Graceful degradation**: Return partial results when possible

### Review Quality
- **Multi-pass**: Code review for multiple concerns
- **Separate passes**: One concern per pass
- **Cost-benefit**: 3x cost for 2.5x quality often worth it

### Batch Processing
- **Use batch**: Nightly jobs, bulk extractions, >100 items
- **Use regular API**: User blocking, <1 hour deadline, interactive agents
- **Remember**: custom_id for result correlation

---

## Practice Questions

1. What does `tool_choice="auto"` guarantee? (Answer: Nothing - might skip tool)
2. In a 50-turn conversation, where should critical info be placed? (Answer: Beginning and end)
3. What's silent error suppression? (Answer: Returning success when tool fails)
4. Why use scratchpad in multi-phase tasks? (Answer: Reduce context burden, enable cross-phase knowledge)
5. When should you use Batch API? (Answer: Non-blocking, >100 items, deadline >1 hour)
6. Why multi-pass review over single-pass? (Answer: Prevent attention dilution, improve quality)
7. What's the difference between accuracy and calibration? (Answer: Accuracy=correct%, Calibration=reported confidence matches actual%)

---

**Print this document or keep it handy while studying - these are the concepts most likely to appear on the exam but are underrepresented in the main study guides.**
