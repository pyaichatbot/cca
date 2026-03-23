# Training Session 5: Context Management & Reliability
## Claude Certified Architect – Foundations

**Duration:** 1.5 hours | **Domain Weight:** 15% (11 questions)
**Prerequisites:** Sessions 1-4 completed
**Last Updated:** March 2026

---

## Session Overview

In Sessions 1-4, you learned how to design robust prompts, implement tool use patterns, and architect multi-agent systems. Domain 5 focuses on the critical operational aspects that keep these systems reliable in production: managing conversation context over long interactions, gracefully handling errors and ambiguities, and maintaining accountability through uncertainty communication and human oversight.

This is where architectural maturity meets operational reality. A perfectly designed system fails in production if it can't:
- Maintain clarity across long conversations
- Recover from errors without losing state
- Admit what it doesn't know
- Hand off to humans at the right moment

By the end of this session, you'll understand how to build systems that remain reliable, transparent, and maintainable at scale.

---

## Learning Objectives

After completing this session, you will be able to:

1. **Preserve context** through long conversations using strategies tailored to each interaction pattern
2. **Design escalation workflows** that distinguish between solvable ambiguities and genuine handoff scenarios
3. **Propagate errors gracefully** in multi-agent systems, preserving partial results and diagnostic information
4. **Explore large codebases** without losing focus or exceeding context limits
5. **Implement confidence-based routing** to the human loop at the right decision points
6. **Communicate uncertainty** transparently, including source attribution and reasoning provenance

---

## Part 1: Conversation Context Preservation (Task 5.1) — 20 min

### Context Window Mechanics: The Reality

Your conversation context is finite. Claude operates with a context window (currently 200K tokens for Claude 3.5 Sonnet), but **production reality is often tighter**:
- User instructions: 500 tokens
- System prompt: 2K tokens
- Available for conversation: 197.5K tokens
- Each user message: 100-500 tokens
- Each assistant response: 500-2K tokens

**In practice, you typically have 10-50 high-quality exchanges before quality degrades.**

### Strategies for Long Conversations

#### Strategy 1: Scratchpad Summaries (Most Common)
Maintain a persistent summary at the conversation start that gets updated periodically:

```
## Conversation Scratchpad
- **User Goal:** Refactor authentication system in 3 microservices
- **Completed:** ✓ Service A auth redesign
- **In Progress:** Service B token validation (currently reviewing error logs)
- **Pending:** Service C migration, integration testing
- **Key Decisions:** Using JWT with 1-hour rotation, stored in httpOnly cookies
- **Open Questions:** Cache invalidation strategy for token revocation
- **Context Saved:** 3 token exchange rounds (~8K tokens)
```

**When to use:** Multi-turn problem solving, design sessions, code reviews lasting 20+ exchanges.

#### Strategy 2: Structured Handoff Documents
When moving between sessions or agents, create a JSON state object:

```json
{
  "session_id": "auth-refactor-2026-03",
  "user_goal": "Refactor microservice authentication",
  "completed_tasks": ["Service A auth redesign"],
  "current_context": {
    "focus": "Service B token validation",
    "recent_findings": "Cache hit rate at 94%, but 6% miss on revoked tokens",
    "blocker": "Need clarity on TTL for revocation cache"
  },
  "decisions_made": {
    "token_type": "JWT",
    "storage": "httpOnly cookies",
    "rotation": "1 hour"
  },
  "next_steps": ["Resolve cache TTL", "Service C migration"]
}
```

**When to use:** Handing off to different AI systems, storing state in a database, multi-day projects.

#### Strategy 3: Per-File Context Isolation
When working with large codebases, isolate analysis by file or module:

```
## Analysis Context - Authentication Module
**Current File:** src/auth/token-validator.ts (320 lines)

### Dependencies Mapped
- ✓ src/auth/types.ts (JWT types, cache interface)
- ✓ src/cache/redis-client.ts (token revocation cache)
- → src/audit/logger.ts (not yet reviewed)

### Context Preserved
- Token validation flow: input → cache check → signature verify → TTL check → return
- Cache hit/miss patterns documented
- Error cases: expired, revoked, malformed, signature mismatch

### Attention Budget: 7/10 tokens reserved
**Next focus:** src/cache/redis-client.ts
```

**When to use:** Codebase analysis, architectural documentation, exploring unfamiliar code.

### Exam Trap #1: "Context Never Runs Out"
**Wrong:** Assuming context is infinite or that quality never degrades.
**Right:** Plan for context limits explicitly; implement rollover strategies at 60% window usage.

### Practice Question 5.1
*A user is working with you on a 50-turn conversation designing a real-time notification system. You're on turn 38. What should you do?*

A) Continue normally; context management isn't needed yet
B) Summarize the scratchpad, add it to the next message, and offer to continue fresh if needed
C) Stop immediately and require a new session
D) Ask the user to compress their messages

**Answer: B** — At turn 38, you're approaching the practical limit for high-quality interaction. Proactively offering a summary-and-restart pattern preserves context while giving the user control over whether to continue.

---

## Part 2: Escalation & Ambiguity Resolution (Task 5.2) — 20 min

### The Decision Tree: Resolve vs. Escalate

```
┌─ Ambiguous user request?
│  ├─ Can I detect intent with 95%+ confidence?
│  │  ├─ YES → Resolve (ask clarifying question, make justified assumption)
│  │  └─ NO → Escalate (structured handoff to human)
│  └─ Would wrong assumption cause >$100 impact or legal risk?
│     ├─ YES → Escalate (always)
│     └─ NO → Resolve with confidence flag
```

### Structured Escalation Format (Required Knowledge)

When escalating, always provide:

```
## ESCALATION REQUIRED

**Issue Type:** Ambiguity / Missing Information / Out of Scope

**Ambiguity Details:**
- User requested: "Update the system to improve performance"
- Possible interpretations: (a) Reduce latency, (b) increase throughput, (c) reduce cost
- Impact: Architectural decisions differ by interpretation
- Confidence in auto-resolution: 30%

**What I Can Do:**
- Provide latency optimization strategies
- Provide throughput optimization strategies
- Provide cost optimization strategies

**What Needs Human Decision:**
- User must clarify primary optimization goal
- Trade-offs between latency/throughput/cost must be weighted by product

**Recommended Human Task:**
- [ ] Ask user: "Which metric should we optimize for: response time, requests/sec, or monthly infrastructure cost?"
- [ ] Once clarified, resubmit with decision and I'll proceed

**Hand-off Summary:** User goal ambiguous around system performance metric.
```

### Ambiguity Detection Patterns

**High-Confidence Signals for Escalation:**
- "What does X mean?" + multiple interpretations exist
- "Should I do A or B?" + significant trade-offs
- "Is this right?" + domain-specific judgment needed
- Budget/timeline/scope conflicts mentioned

**When You CAN Resolve:**
- Missing detail but multiple approaches are equivalent (try all)
- User says "either way is fine" (choose reasonable default)
- Ambiguity about implementation details, not goals (choose best practice)

### Exam Trap #2: Over-Escalating
**Wrong:** Escalating every unclear request; leaving humans to make obvious decisions.
**Right:** Escalate high-impact ambiguities; resolve low-impact ones with confidence flags and clear assumptions stated.

### Practice Question 5.2
*A user asks: "Can you review my code for quality?" You have no context about what "quality" means to them: Could be performance, security, readability, or test coverage. The code is internal tooling with no security-critical components. What's your response?*

A) Escalate to human immediately
B) Review for all four dimensions and let user pick what matters
C) Ask: "When you say quality, do you mean performance, security, readability, or test coverage?" and wait for clarification
D) Review for readability (most common interpretation) and proceed

**Answer: C** — This is solvable ambiguity that benefits from 15 seconds of clarification. No escalation needed, but you must ask rather than assume. (B is wasteful; D assumes wrong metric.)

---

## Part 3: Error Propagation in Multi-Agent Systems (Task 5.3) — 20 min

### The Anti-Pattern: Silent Failure

**What NOT to do:**
```python
def coordinator_execute(tasks):
    results = []
    for task in tasks:
        try:
            result = agent.execute(task)
            results.append(result)
        except Exception:
            pass  # Silent failure — WRONG
    return results
```

This loses critical diagnostic information. In production, silence is death.

### The Pattern: Graceful Degradation with Context

```python
class TaskResult:
    def __init__(self, task_id, success, output=None, error=None, attempts=None):
        self.task_id = task_id
        self.success = success
        self.output = output
        self.error = error  # Full error context
        self.attempts = attempts  # How many tries?
        self.partial_output = None  # What DID we get?

def coordinator_execute(tasks, max_retries=2):
    results = []

    for task in tasks:
        result = TaskResult(task.id, success=False)
        attempts = 0

        for attempt in range(max_retries):
            attempts += 1
            try:
                output = agent.execute(task)
                result.success = True
                result.output = output
                result.attempts = attempts
                break
            except Exception as e:
                result.error = str(e)
                result.attempts = attempts

                # Capture partial output if available
                if hasattr(e, 'partial_output'):
                    result.partial_output = e.partial_output

                # Log for debugging
                logger.warning(f"Task {task.id} failed on attempt {attempts}: {e}")

        results.append(result)

    return results

# Consumer code:
results = coordinator_execute(tasks)

# Summary for user:
successful = [r for r in results if r.success]
failed = [r for r in results if not r.success]

print(f"✓ {len(successful)}/{len(results)} tasks succeeded")

if failed:
    print("\n⚠ Failed tasks (with diagnostic context):")
    for result in failed:
        print(f"  - {result.task_id}: {result.error}")
        if result.partial_output:
            print(f"    Partial result: {result.partial_output[:100]}...")
        print(f"    Attempts: {result.attempts}")
```

**Why this works:**
- ✓ Partial results are preserved (e.g., "got 7 of 10 items")
- ✓ Error context is available ("timeout vs. validation error")
- ✓ Retry telemetry is captured (was it a transient blip?)
- ✓ User gets realistic summary ("5 succeeded, 2 failed")

### Coordinator Error Handling Pattern

```python
def coordinator_decide_next_steps(results):
    """Intelligent routing based on failure patterns."""

    all_successful = all(r.success for r in results)
    if all_successful:
        return "PROCEED_WITH_FULL_RESULTS"

    # Check for systematic failures (same error across many tasks)
    error_counts = {}
    for r in results:
        if not r.success:
            error_counts[r.error] = error_counts.get(r.error, 0) + 1

    systematic_failure = max(error_counts.values()) > len(results) / 2

    if systematic_failure:
        return "ESCALATE_SYSTEMATIC_ERROR"

    # Partial success — proceed but flag uncertainties
    partial_success_rate = sum(1 for r in results if r.success) / len(results)

    if partial_success_rate > 0.7:
        return "PROCEED_WITH_CONFIDENCE_FLAG"
    else:
        return "ESCALATE_HIGH_FAILURE_RATE"
```

### Exam Trap #3: "All-or-Nothing" Thinking
**Wrong:** "If any task fails, fail the whole workflow."
**Right:** Capture partial results, aggregate errors intelligently, route based on failure patterns (systematic vs. transient).

### Practice Question 5.3
*You're coordinating 10 code review subtasks. 8 succeed with results. 2 fail with "timeout" errors. What should you do?*

A) Return only the 8 successful reviews; ignore the 2 timeouts
B) Retry the 2 timeouts once; if they succeed, return all 10; if they fail, escalate
C) Return all 8 successful reviews + a flag noting "2 of 10 reviews incomplete due to timeout"
D) Fail the entire review process

**Answer: B or C** — Both are reasonable. B is better if timeouts are transient. C is better if you want to move fast and accept partial results. The key: Don't silently drop the 2 reviews (A), and don't fail the entire process (D). Capture what you learned and either retry or flag appropriately.

---

## Part 4: Context in Large Codebase Exploration (Task 5.4) — 15 min

### The Problem: Attention Dilution

When exploring a large codebase (100K+ lines), you face a dilemma:
- **Explore broadly:** Risk missing critical dependencies and architectural patterns
- **Explore deeply:** Risk losing the "big picture" and exceeding context limits

**Solution:** Progressive exploration with explicit scoping

### The Pattern: Per-File Analysis + Integration Pass

**Phase 1: Scoping (2-3 exchanges, ~4K tokens)**
```
Goal: Understand Authentication System (2000 lines across 8 files)

Files to analyze:
1. auth/types.ts (80 lines) — Data structures
2. auth/jwt-handler.ts (250 lines) — Token generation/validation
3. auth/middleware.ts (180 lines) — Express middleware
4. auth/session-store.ts (320 lines) — Session persistence
5. cache/redis-client.ts (150 lines) — Token revocation cache
6. audit/logger.ts (120 lines) — Audit logging
7. tests/auth.test.ts (400 lines) — Test coverage insights
8. docs/AUTH.md (100 lines) — Architecture documentation

Analysis strategy:
- Phase 1 (files 1-2): Type system and core logic
- Phase 2 (files 3-4): Integration points
- Phase 3 (files 5-7): Dependencies and testing
- Phase 4: Cross-file architecture synthesis
```

**Phase 2: Per-File Analysis (3-4 exchanges, ~6K tokens)**
```
## File: auth/jwt-handler.ts (250 lines)

Key findings:
- generateToken(): Creates JWT with 1-hour TTL, HS256 signature
- validateToken(): Checks signature, TTL, revocation list (via Redis)
- Error cases: ExpiredTokenError, InvalidSignatureError, RevokedTokenError

Dependencies:
- ✓ auth/types.ts (imports TokenPayload, TokenConfig)
- → cache/redis-client.ts (revocation check, not yet analyzed)
- ✓ Built-in: crypto, jsonwebtoken

Critical detail: validateToken has 3 async calls (potential performance bottleneck)
```

**Phase 3: Cross-File Integration (2 exchanges, ~3K tokens)**
```
## Architecture Map: Authentication System

Data Flow:
User Login → middleware.ts → jwt-handler.ts (generateToken)
  → session-store.ts (save) → Redis (cache layer)

User Request → middleware.ts (extractToken)
  → jwt-handler.ts (validateToken)
  → Redis (revocation check) → logger.ts (audit)

Critical Path: generateToken + Redis write (async, potential bottleneck)
Revocation check: 3-step process, could be optimized with caching

Risks identified:
- Redis dependency for revocation (single point of failure)
- No timeout on revocation check (could block request)
```

### Avoiding Attention Dilution

**Rule 1: One file at a time**
Read a single file completely before asking about another.

**Rule 2: Save scoping decisions**
Document which files you'll analyze and in what order; stick to it.

**Rule 3: Synthesize explicitly**
After individual file analysis, do a dedicated "integration pass" to connect findings.

**Rule 4: Time-box analysis**
5 files max per session; plan continuation for larger codebases.

### Exam Trap #4: "Analyze Everything at Once"
**Wrong:** Asking about all 8 files in the initial request; risk hitting context limits before finishing.
**Right:** Scope 3-5 files explicitly, analyze per-file, then synthesize cross-file dependencies in a final pass.

### Practice Question 5.4
*You're exploring a codebase with 12 files. You've analyzed 4 files and used 20K of your 50K available tokens. What should you do?*

A) Continue analyzing all remaining 8 files; plenty of tokens left
B) Analyze 2-3 more files, then do an integration pass summarizing the architecture
C) Pause, generate a summary of the 4 files, save it, and start fresh with remaining files in the next session
D) Ask the user which 2 files are most critical and focus only on those

**Answer: B or C** — B is good if you're at 40% context usage and can fit 2-3 more files + synthesis. C is better if you want to continue with new context-preservation state. Both are better than A (finish without understanding architecture) or D (shifting responsibility to user when you should be strategic).

---

## Part 5: Human Review & Confidence Calibration (Task 5.5) — 10 min

### Confidence Scoring: The Framework

Not all outputs are equally reliable. Implement explicit confidence scoring:

```python
class AnalysisResult:
    def __init__(self, conclusion, confidence_score, reasoning):
        self.conclusion = conclusion
        self.confidence_score = confidence_score  # 0.0 to 1.0
        self.reasoning = reasoning
        self.recommended_action = self.route()

    def route(self):
        """Route based on confidence."""
        if self.confidence_score >= 0.95:
            return "AUTONOMOUS_PROCEED"
        elif self.confidence_score >= 0.75:
            return "AUTONOMOUS_PROCEED_WITH_FLAG"
        elif self.confidence_score >= 0.50:
            return "HUMAN_REVIEW_RECOMMENDED"
        else:
            return "ESCALATE_IMMEDIATELY"

# Example: Code security analysis
result = AnalysisResult(
    conclusion="No SQL injection vulnerabilities detected",
    confidence_score=0.92,
    reasoning="Analyzed 5 database query patterns; all use parameterized queries. Automated tool + manual review of edge cases. Small risk: dynamic table names in 1 legacy function (low-risk path)."
)
# → AUTONOMOUS_PROCEED_WITH_FLAG

# Example: Architecture recommendation
result = AnalysisResult(
    conclusion="Recommend switching from REST to gRPC for internal APIs",
    confidence_score=0.65,
    reasoning="Clear performance benefits (30-40% latency reduction based on literature). Tradeoff: operational complexity. Organization preference + team experience unknown. Missing: load test data from current architecture."
)
# → HUMAN_REVIEW_RECOMMENDED
```

### When Automated Review Suffices

**High-confidence buckets (no human review needed):**
- Syntax validation (100% machine decision)
- Format conversions (100% deterministic)
- Code style enforcement (99%+ automated)
- Dependency scanning (95%+; known database)

**Medium-confidence buckets (flag but proceed):**
- Performance recommendations (80-90%; missing deploy context)
- Security suggestions (85-95%; may not know organization's risk appetite)
- Naming/readability feedback (70-85%; subjective)

### When Human Review is Required

**Lower-confidence buckets (must escalate):**
- Architecture decisions (50-75%; too many org factors)
- Data model changes (50-70%; needs domain expert)
- Scope/timeline estimates (40-70%; too many unknowns)
- Deprecation recommendations (60-80%; requires human judgment)

### Exam Trap #5: Over-Confidence
**Wrong:** Scoring architecture recommendations at 95% confidence.
**Right:** Be honest about uncertainty. Architecture recommendations without organizational context are inherently 60-75%.

### Practice Question 5.5
*You've analyzed a codebase and recommend a database migration from MongoDB to PostgreSQL. You're confident about the technical correctness but uncertain about whether the team has PostgreSQL expertise and whether cost/timeline trade-offs align with org priorities. What confidence score and routing decision?*

A) 90% confidence, AUTONOMOUS_PROCEED; technical analysis is solid
B) 65% confidence, HUMAN_REVIEW_RECOMMENDED; organizational factors matter
C) 40% confidence, ESCALATE_IMMEDIATELY; you don't know enough
D) 75% confidence, AUTONOMOUS_PROCEED_WITH_FLAG; flag the org context unknowns

**Answer: B** — 65% is right. You have high technical confidence but medium organizational confidence. This warrants human review to validate assumptions. (A over-inflates confidence; C is too cautious; D proceeds with insufficient information.)

---

## Part 6: Information Provenance & Uncertainty (Task 5.6) — 10 min

### Source Attribution: Credibility Layers

**Rule 1: Always distinguish between types of knowledge:**

```
"This API endpoint returns a 200 status for success"
Source: Examined actual code + API response logs
Credibility: HIGH (observed directly)

"The API team plans to add pagination next quarter"
Source: Slack conversation from 2 weeks ago
Credibility: MEDIUM (reported, not current)

"The API is likely fast because it uses Redis caching"
Source: Architectural pattern inference from code structure
Credibility: MEDIUM (inference, not measurement)

"The API has 99.99% uptime"
Source: You did not examine monitoring data
Credibility: LOW (unsupported claim)
```

### Uncertainty Communication Patterns

**Pattern 1: Confidence Intervals**
```
Estimated refactor time: 3-5 days
Confidence: 70%
Reasoning: 2 engineers, familiar with code, 5 known subtasks, 1 unknown risk (third-party integration testing)

More likely: 4 days
Optimistic case: 2.5 days (if third-party integration is smooth)
Pessimistic case: 8 days (if integration requires rework)
```

**Pattern 2: Assumption Callouts**
```
Recommendation: Implement Redis caching layer

Assumptions:
- ✓ Verified: Your API returns large datasets (confirmed via code review)
- ✓ Verified: Users are willing to accept eventual consistency (mentioned in requirements)
- ? Unknown: Current latency baseline (not measured; estimates at 200-500ms)
- ? Unknown: Peak traffic patterns (no load test data available)

If assumptions change (e.g., needs strong consistency), recommendation would differ.
```

**Pattern 3: Confidence Decay**
```
Original finding (from code review, 1 day old):
"Database connection pool exhaustion occurs at 500 concurrent connections"
Confidence: HIGH

Derivative claim (not directly verified):
"Production will hit this limit during Black Friday"
Confidence: MEDIUM (depends on traffic forecasts we haven't seen)

Far-field claim:
"We should migrate to a serverless database"
Confidence: LOW (too many unknowns about cost, latency, team skill)
```

### Exam Trap #6: "Provenance Invisibility"
**Wrong:** Making claims without noting where they come from or what confidence level they deserve.
**Right:** Explicitly surface the source and confidence for every non-obvious claim. Let humans weight credibility themselves.

### Practice Question 5.6
*You're analyzing a codebase and find a comment saying "This function is called 10,000 times per second in production." You haven't verified this claim. How should you report it?*

A) "This function is called 10,000 times per second" (as stated)
B) "According to a code comment, this function may be called frequently (10,000 times/sec claimed, but unverified)"
C) "This function is likely a hot path based on the comment, but actual production metrics aren't available"
D) Ignore the comment; only report on what you can verify

**Answer: B or C** — Both surface the provenance and uncertainty. B preserves the exact claim; C interprets it. (A dangerously repeats an unverified claim; D throws away useful context.)

---

## Part 7: Session Summary & Key Takeaways

**Domain 5 Core Principle:** *Reliability comes from transparency, not perfection.*

| Task | Core Pattern | When It Matters |
|------|--------------|-----------------|
| **5.1** Context Preservation | Scratchpad summaries + handoff docs | Long conversations, multi-day projects |
| **5.2** Escalation Design | Structured ambiguity → human decision | High-impact ambiguities |
| **5.3** Error Propagation | Partial results + error context | Multi-agent workflows |
| **5.4** Codebase Exploration | Progressive scoping + per-file analysis | 100K+ LOC codebases |
| **5.5** Confidence Calibration | Explicit scoring + routing | Risk-aware automation |
| **5.6** Information Provenance | Source + confidence on every claim | Reducing downstream confusion |

**The One Thing to Remember:** In production systems, the most expensive failure is silent failure. Build visibility into every layer:
- Can you preserve context through the conversation?
- Do you know when to escalate vs. resolve?
- Are errors captured with full diagnostic context?
- Is uncertainty communicated clearly?

---

## Hands-On Lab Exercise

**Scenario:** You're building an automated code review system for a team. It should handle 100+ pull requests per sprint.

**Requirements:**
1. Analyze code for security, performance, and readability issues
2. Decide when to auto-comment vs. escalate for human review
3. Preserve context across multiple reviews
4. Surface confidence in recommendations
5. Avoid silent failures

**Your task (30 minutes):**

1. **Design the confidence scoring system** — What metrics determine whether a security recommendation goes to auto-comment vs. human review?

2. **Design the error handling** — If a review times out on file #3 of 5, how do you capture partial results and notify the user?

3. **Design the escalation format** — When should a recommendation escalate? Use the structured format from Task 5.2.

4. **Design context preservation** — How do you summarize a review session so a human can pick it up later?

**Deliverable:** A 1-page design document covering all 4 points.

**Debrief Questions:**
- How would your confidence scoring change if the team was analyzing security-critical code vs. internal tools?
- What would you do if 30% of reviews failed with timeout errors?

---

## Self-Assessment Quiz

**Question 1:** You're on exchange 45 of a long conversation. Should you proactively offer a context reset?
A) No; context isn't limited yet
B) Yes; you're at 90%+ of practical context limits
C) Only if the user explicitly asks
D) Only if you've hit a token limit error

**Answer: B** — Proactive management at 90% usage prevents degradation.

---

**Question 2:** Your team wants you to escalate every ambiguous user request to humans. Is this a good practice?
A) Yes; better to be safe
B) No; escalates too much and slows down the system
C) Only for high-risk domains like healthcare
D) Yes, except for technical implementation details

**Answer: B** — Over-escalation wastes human time. Distinguish solvable ambiguities (resolve) from high-impact ones (escalate).

---

**Question 3:** You're coordinating 10 data processing tasks. 8 succeed, 2 fail with "resource exhausted" errors. The 2 failures are independent. What should you do?
A) Fail the whole batch; can't proceed without all 10
B) Succeed with 8 results; silently drop the 2 failures
C) Retry the 2 failures once; if successful, return all 10; if failed, return 8 + flag
D) Return 8 results + confidence flag that 80% completed

**Answer: C** — Capture partial results, retry transient errors, and route intelligently.

---

**Question 4:** You're analyzing a 500-line file in a 50K-LOC codebase. You've used 15K of 50K tokens analyzing the file. Should you continue to the next file?
A) Yes; 35K tokens remain
B) No; save your analysis and start fresh in a new session
C) Yes, but scope explicitly to 2-3 more files then do integration pass
D) Ask the user which file to analyze next

**Answer: C** — Plan the full analysis, budget tokens carefully, synthesize at the end.

---

**Question 5:** Your security analysis identifies "potential SQL injection in 1 of 50 queries" but you can't verify it without running the application. Confidence?
A) 95% (you identified a potential issue)
B) 70% (you found a pattern match but can't verify)
C) 40% (you couldn't test it)
D) 10% (you didn't verify with actual exploitation)

**Answer: B** — Pattern-based detection is solid but unverified. Honest confidence is 60-75%.

---

**Question 6:** A user asks you to estimate how long a project will take. You have: code statistics but not the team's skill level or deployment constraints. Confidence?
A) 85% (lots of code data)
B) 60% (estimates, missing team/org factors)
C) 40% (too many unknowns)
D) 50% (moderate uncertainty)

**Answer: B** — Estimates without team/org context are inherently 50-70%. Be honest.

---

## Recommended Study Resources

**Review Materials:**
- **Domains 1-4 training sessions** — Context management builds on all prior concepts
- **Official exam guide, Domain 5 section** — Task statements 5.1-5.6
- **Claude documentation on tool use and multi-turn conversations** — Practical implementation patterns

**Key Concepts to Drill:**
- The difference between "solvable ambiguities" and "genuine escalations"
- Why silent failures are worse than reported partial failures
- Confidence scoring for different claim types
- Progressive codebase exploration patterns

---

## Course Wrap-Up: Preparing for Exam Day

### The 2-Week Study Plan

**Week 1: Deep Dive & Drill**

| Day | Focus | Time | Activity |
|-----|-------|------|----------|
| Mon | Domain 1 review | 1.5 hrs | Re-read Session 1, drill practice questions |
| Tue | Domain 2 review | 1.5 hrs | Re-read Session 2, practice prompt design |
| Wed | Domain 3 review | 1.5 hrs | Re-read Session 3, tool use patterns |
| Thu | Domain 4 review | 1.5 hrs | Re-read Session 4, multi-agent architectures |
| Fri | Domain 5 deep dive | 2 hrs | Complete hands-on lab, self-assessment quiz |
| Sat-Sun | Mixed review | 2 hrs total | Pick weak domains, do 10-15 additional practice questions |

**Week 2: Integration & Practice**

| Day | Focus | Time | Activity |
|-----|-------|------|----------|
| Mon | Cross-domain scenarios | 1.5 hrs | Practice "design a system" questions spanning 2+ domains |
| Tue | Domain 1-2 weak areas | 1 hr | Targeted drill on weak topics |
| Wed | Domain 3-4 weak areas | 1 hr | Targeted drill on weak topics |
| Thu | Domain 5 weak areas | 1 hr | Targeted drill; re-read error handling patterns |
| Fri | Full practice exam | 2 hrs | Timed mock exam (73 questions, 2 hours) |
| Sat | Review practice exam | 1.5 hrs | Analyze missed questions; identify final gaps |
| Sun | Final review | 1 hr | Skim all session summaries, final checklist |

**Total study time:** ~18 hours over 2 weeks (~2.5 hours per day)

### Exam Day Tips

1. **Time management:** 73 questions in 2 hours = ~1.6 minutes per question. Don't get stuck. Flag unclear questions, move on, return if time permits.

2. **Read carefully:** Trap answers are common. Re-read the question and all options before selecting.

3. **Confidence over memorization:** You'll see novel scenarios. Use the core principles to reason through them:
   - Prompt: How would you structure this?
   - Tool use: When would you use tools? How?
   - Multi-agent: Who decides? What if they disagree?
   - Context: Can you preserve this? How?
   - Reliability: What are the failure modes?

4. **The "Trap Answer" Pattern:** Often 1 answer is too cautious ("always escalate"), 1 is reckless ("proceed without checks"), 1 is correct ("route based on confidence + org context").

5. **On ambiguous questions:** Look for the most *complete* answer, not the simplest. "Handle partial results + flag uncertainty" beats "return all data" or "fail the task."

### Final Checklist: 30 Critical Concepts

**Domain 1: Prompt Engineering**
- [ ] System prompts vs. user prompts: use cases for each
- [ ] Multi-shot examples: when 1 example isn't enough
- [ ] Instruction clarity: be specific about format and constraints

**Domain 2: RAG & Knowledge**
- [ ] Retrieval quality matters more than quantity
- [ ] Summarization + retrieval: when to combine
- [ ] Handling outdated or conflicting information

**Domain 3: Tool Use**
- [ ] Tool definitions: format, parameters, error handling
- [ ] Chaining tools: serial vs. parallel dependencies
- [ ] Graceful fallback: when a tool fails

**Domain 4: Multi-Agent Systems**
- [ ] Coordinator patterns: centralized vs. decentralized
- [ ] Agent specialization: narrow roles beat generalists
- [ ] Handoff protocols: structured vs. unstructured

**Domain 5: Context & Reliability**
- [ ] Context window limits: plan for them
- [ ] Escalation vs. resolution: use the decision tree
- [ ] Error handling: preserve partial results + context
- [ ] Codebase exploration: scope explicitly, synthesize
- [ ] Confidence scoring: be honest about uncertainty
- [ ] Provenance: source every claim

---

## Final Exam Confidence Predictor

If you can answer all of the following **without** looking back at these notes, you're ready:

1. What are the 3 strategies for preserving context in long conversations?
2. Give an example of an ambiguity you would escalate vs. resolve.
3. Why is "silent failure" worse than "partial failure with diagnostics"?
4. How would you scope analysis of a 200K-LOC codebase to stay within context limits?
5. What confidence score would you give to "estimated project timeline without team skill data"?
6. Write a 2-line summary of a finding with source attribution and confidence.
7. Design a simple confidence-based routing system (3-4 decision rules).
8. Sketch the coordinator error handling pattern (input → processing → output).

If you can teach these concepts to someone else, you're more than ready.

---

**Good luck on the exam. You've got this.**

**Next Steps:**
- Complete all self-assessment quizzes (aim for 90%+)
- Work through the hands-on lab exercise
- Schedule your 2-week study sprint
- Take a full practice exam 3-4 days before the real exam
- Review your weak domains the day before

Remember: The CCA Foundations exam tests whether you can **design reliable systems that remain transparent and maintainable at scale**. Focus on that principle, and the answers will follow.

