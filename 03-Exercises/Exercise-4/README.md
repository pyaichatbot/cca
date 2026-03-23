# Exercise 4: Multi-Agent Research System with Coordinator Pattern

## Architecture Overview

### ASCII Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER QUERY                              │
│              "Research AI safety frameworks"                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COORDINATOR AGENT                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Decompose task                                       │  │
│  │  2. Plan subagent delegation                            │  │
│  │  3. Aggregate results                                   │  │
│  │  4. Evaluate synthesis quality                          │  │
│  │  5. Request additional research if gaps detected        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Tools: task_planner, quality_evaluator, delegation_logger     │
└────────┬─────────────────────┬──────────────────────────┬──────┘
         │                     │                          │
         ▼                     ▼                          ▼
    ┌─────────────┐      ┌──────────────┐          ┌──────────────┐
    │   SEARCH    │      │   ANALYSIS   │          │ SYNTHESIS    │
    │   SUBAGENT  │      │   SUBAGENT   │          │ SUBAGENT     │
    ├─────────────┤      ├──────────────┤          ├──────────────┤
    │ Isolated    │      │ Isolated     │          │ Isolated     │
    │ context     │      │ context      │          │ context      │
    │             │      │              │          │              │
    │ Tools:      │      │ Tools:       │          │ Tools:       │
    │ • web_search│      │ • extract    │          │ • compile    │
    │ • fetch_url │      │   _data      │          │   _report    │
    │             │      │ • summarize  │          │ • verify_fact│
    └─────────────┘      │   _content   │          └──────────────┘
         │                └──────────────┘               │
         │                     │                        │
         │ Results: URLs,      │ Results: Key           │ Results:
         │ summaries           │ insights, quotes       │ structured
         │                     │                        │ report
         └─────────────────────┼────────────────────────┘
                               │
                      ┌────────▼──────────┐
                      │ Structured        │
                      │ Handoff Summary   │
                      │ (provenance data) │
                      └───────────────────┘
                               │
                               ▼
                      ┌────────────────────┐
                      │ Coordinator        │
                      │ Quality Gate       │
                      │ Approve or         │
                      │ Re-delegate?       │
                      └────────────────────┘
                               │
                         ┌─────┴──────┐
                         │            │
                    APPROVED      REDELEGATE
                         │            │
                         ▼            ▼
                    FINAL REPORT  (ITERATION)
```

## Exercise Overview

### Learning Objectives

This exercise teaches you how to architect sophisticated multi-agent systems where:

1. **Coordinator agents** decompose complex tasks and orchestrate specialized subagents
2. **Subagents operate in isolated contexts** — they receive only the information they need, not the full conversation history
3. **Tool access is scoped** — each agent role gets precisely the tools required for its function
4. **Results are aggregated** with provenance information (source tracking)
5. **Quality gates** enable iterative refinement and graceful degradation on failures

### Exam Domains Covered

| Domain | Concepts | Exercise Relevance |
|--------|----------|-------------------|
| **Domain 1: Agentic Architecture** | Hub-and-spoke pattern, task decomposition, delegation, iterative loops, session management, safety limits | Coordinator orchestration, subagent isolation, loop control, max-iterations |
| **Domain 2: Tool Design** | Scoped access, error structures, tool descriptions, tool_choice | Each subagent's tool set, error categories, tool routing |
| **Domain 5: Context Management** | Context passing, provenance tracking, error propagation, graceful degradation | Structured handoff summaries, source tracking, partial results on failure |

---

## Code Structure Walkthrough

### 1. **Coordinator Agent** (`ResearchCoordinator` class)

The coordinator is the orchestrator. It:

- **Analyzes the user query** and decides which subagents to invoke
- **Delegates tasks** with explicitly provided context (no inherited history)
- **Aggregates results** from all subagents
- **Evaluates synthesis quality** — checks for gaps and missing areas
- **Implements a refinement loop** — re-delegates if gaps are detected
- **Enforces safety limits** — max 3 iterations to prevent runaway loops

Key methods:
- `decompose_task()` — Break down the research query
- `delegate_to_subagent()` — Send work to a specific subagent with isolated context
- `aggregate_results()` — Combine subagent outputs
- `evaluate_synthesis_quality()` — Check for gaps
- `run()` — Main loop implementing the full workflow

### 2. **Subagent Functions** (Search, Analysis, Synthesis)

Each subagent is a function that:

- Receives **explicit context** in its system prompt (no access to coordinator's history)
- Gets **only its required tools**
- Returns **structured results with provenance**
- Handles errors gracefully, returning partial results

#### Search Subagent
- **Purpose**: Find relevant sources and summaries
- **Tools**: `web_search`, `fetch_url`
- **Input**: Research question
- **Output**: List of sources with URLs, snippets, summaries

#### Analysis Subagent
- **Purpose**: Extract key insights and quotes
- **Tools**: `extract_data_points`, `summarize_content`
- **Input**: Raw search results and documents
- **Output**: Structured insights, key quotes, citations

#### Synthesis Subagent
- **Purpose**: Compile a coherent research report
- **Tools**: `compile_report`, `verify_fact`
- **Input**: Insights from search and analysis
- **Output**: Structured research report with fact verification

### 3. **Tool Implementations**

All tools are mocked (no real API calls). They return realistic synthetic data to demonstrate:

- Tool routing logic
- Error responses with structured categories
- Provenance data (URLs, page numbers, document names)
- Tool failures and graceful degradation

Example tool response structure:
```json
{
  "status": "success",
  "data": {...},
  "provenance": {
    "source_url": "...",
    "retrieved_at": "...",
    "confidence": 0.95
  }
}
```

### 4. **Context Passing Pattern**

Subagents receive context via a structured handoff:

```python
{
  "task": "Find frameworks for AI safety",
  "previous_findings": [...],
  "coordinator_notes": "Focus on interpretability",
  "iteration": 1,
  "required_depth": "comprehensive"
}
```

This is **different from** passing the full conversation history. Each subagent gets only what it needs.

### 5. **Iterative Refinement Loop**

The coordinator:

1. **Synthesizes** initial results
2. **Evaluates** the synthesis for gaps (missing domains, shallow coverage, etc.)
3. **Detects gaps** → re-delegates to search/analysis with guidance
4. **Loop control** → max 3 iterations to prevent infinite loops
5. **Delivers final report** → combines all iterations

This pattern ensures comprehensive coverage while avoiding resource waste.

---

## Key Patterns and Exam Relevance

### Pattern 1: Hub-and-Spoke Architecture

**Exam Question:**
> "A coordinator agent needs to orchestrate three specialized subagents. What's the key benefit of using isolated contexts for subagents instead of passing the full conversation history?"

**Answer:**
- Subagents stay focused on their specific task
- Reduced token usage (no irrelevant history)
- Isolation prevents cross-contamination (one agent's errors don't corrupt another's reasoning)
- Easier testing and debugging of individual components
- Better security/privacy boundaries

**Code Example:**
```python
# Coordinator passes ONLY task-specific context
context = {
    "task": user_query,
    "iteration": current_iteration,
    "focus_areas": identified_gaps
}
# Subagent receives this context, not the full conversation
subagent_prompt = f"Your task: {context['task']}\nFocus on: {context['focus_areas']}"
```

### Pattern 2: Scoped Tool Access

**Exam Question:**
> "Why should the search subagent not have access to the `compile_report` tool, and the synthesis subagent not have `web_search`?"

**Answer:**
- **Prevents misrouting** — agents use tools outside their domain
- **Enforces role boundaries** — each agent does one thing well
- **Reduces token costs** — tool descriptions are shorter
- **Improves security** — limits what each agent can do
- **Easier to debug** — if a tool fails, you know which agent to check

**Code Pattern:**
```python
# Search subagent tools
search_tools = [
    {"name": "web_search", ...},
    {"name": "fetch_url", ...}
]

# Synthesis subagent tools (no web_search)
synthesis_tools = [
    {"name": "compile_report", ...},
    {"name": "verify_fact", ...}
]

# Claude API call with scoped tools
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    tools=search_tools,  # Only these tools available
    messages=[...]
)
```

### Pattern 3: Structured Error Responses

**Exam Question:**
> "A subagent fails to find sources for a topic. How should the coordinator handle this while providing partial results?"

**Answer:**
- Return partial results with error context
- Include `errorCategory` (network, not_found, access_denied, etc.)
- Include `isRetryable` flag (true = try different search, false = skip)
- Include `suggestedNextStep` (ask user, use cached results, etc.)

**Code Pattern:**
```python
error_response = {
    "status": "partial",
    "data": {"found_sources": 2},
    "error": {
        "category": "insufficient_results",
        "message": "Only found 2 sources for this topic",
        "isRetryable": True,
        "suggestedNextStep": "Try broader search terms"
    }
}

# Coordinator uses partial results and decides next action
if error_response["error"]["isRetryable"]:
    redelegate_search_with_broader_terms()
else:
    use_cached_results()
```

### Pattern 4: Provenance Tracking

**Exam Question:**
> "Why is tracking source URLs, document names, and page numbers important in a multi-agent research system?"

**Answer:**
- Enables users to verify claims (audit trail)
- Helps coordinator assess result quality
- Allows filtering by source reliability
- Prevents hallucinated citations
- Required for compliance/regulatory work

**Code Pattern:**
```python
source_with_provenance = {
    "content": "AI safety focuses on interpretability",
    "provenance": {
        "source_url": "https://example.com/article",
        "document_name": "AI_Safety_Overview.pdf",
        "page_number": 3,
        "retrieved_at": "2026-03-22T10:30:00Z",
        "confidence": 0.95
    }
}
```

### Pattern 5: Graceful Degradation

**Exam Question:**
> "If the synthesis subagent fails, what should the coordinator do?"

**Answer:**
- Return results from search and analysis phases
- Mark unavailable synthesis as "pending"
- Provide a degraded report (good enough for user)
- Suggest retry or alternative approaches
- Never fail completely; always deliver something useful

**Code Pattern:**
```python
try:
    synthesis = synthesis_subagent(...)
except SubagentFailureError as e:
    synthesis = {
        "status": "degraded",
        "raw_insights": analysis_results,
        "error": str(e),
        "message": "Synthesis failed but analysis results available"
    }

final_report = {
    "search_phase": search_results,
    "analysis_phase": analysis_results,
    "synthesis_phase": synthesis,  # Degraded but present
    "overall_status": "partial_success"
}
```

---

## Session Management Concepts (Exam Relevant)

### Pattern: `--resume` for Long-Running Workflows

```python
# In a real scenario, coordinator could save state between runs
if coordinator_state_exists("research_task_v2"):
    # Resume from saved state
    coordinator = ResearchCoordinator.resume("research_task_v2")
    coordinator.run_iteration(iteration=3)
else:
    # Start fresh
    coordinator = ResearchCoordinator(query)
    coordinator.run()
```

### Pattern: `fork_session` for Parallel Subagent Branches

```python
# Coordinator could fork separate sessions for each subagent
# to improve parallelization and isolation
search_fork = session.fork(name="search_branch")
analysis_fork = session.fork(name="analysis_branch")

search_result = search_subagent(fork=search_fork, ...)
analysis_result = analysis_subagent(fork=analysis_fork, ...)

# Results from forked sessions can't interfere with each other
```

---

## Expected Output

When you run the exercise, you'll see:

```
========================================
MULTI-AGENT RESEARCH SYSTEM
========================================

USER QUERY: Research emerging AI safety frameworks and regulations

------------ ITERATION 1 ------------

[COORDINATOR] Decomposing task...
Task: Research frameworks | Subagents needed: search, analysis, synthesis
Safety research focus areas: interpretability, alignment, governance

[COORDINATOR] Delegating to SEARCH subagent...
[SEARCH SUBAGENT] Finding sources on AI safety frameworks
Result: 5 sources found (URLs with summaries)

[COORDINATOR] Delegating to ANALYSIS subagent...
[ANALYSIS SUBAGENT] Extracting key insights from sources
Result: 12 key insights extracted with quotes

[COORDINATOR] Delegating to SYNTHESIS subagent...
[SYNTHESIS SUBAGENT] Compiling research report
Result: Structured report generated (5 sections)

[COORDINATOR] Evaluating synthesis quality...
Quality score: 0.72/1.00
Gaps detected:
  - Regulatory frameworks (coverage: low)
  - Industry adoption (coverage: medium)

------------ ITERATION 2 (REFINEMENT) ------------

[COORDINATOR] Gaps detected. Re-delegating for deeper research...

[SEARCH SUBAGENT] Finding sources on regulatory frameworks
Result: 3 additional sources found

[COORDINATOR] Final synthesis pass...

------------ FINAL REPORT ------------

RESEARCH REPORT: Emerging AI Safety Frameworks and Regulations
Generated: 2026-03-22 | Iterations: 2

SECTION 1: Safety Frameworks
- Interpretability Research
  Source: https://example.com/interpretability
  Key insight: "Mechanistic interpretability enables..."

SECTION 2: Regulatory Landscape
- EU AI Act
  Source: https://example.com/eu-ai-act
  Key insight: "The EU AI Act classifies systems..."

...

Overall Status: ✓ Comprehensive
Coverage: 89% (improved from 72%)
Verified Facts: 15/15 ✓
Sources: 8 total
```

---

## Exam Questions This Exercise Prepares You For

### Question 1: Coordinator Pattern
**Q: You're building a multi-agent system where a coordinator delegates to 3 specialized subagents. Should you pass the coordinator's full conversation history to each subagent? Why or why not?**

**Answer:** No. Subagents should receive only task-specific context:
- Reduces token usage and costs
- Keeps agents focused on their specialized role
- Prevents information leakage between subagents
- Makes debugging easier (isolated failures)
- Better security boundaries

Pass explicit, minimal context instead:
```
{
  "task": "Find X",
  "focus_areas": [...],
  "previous_findings": [...only relevant parts...]
}
```

### Question 2: Scoped Tools
**Q: A search subagent has access to `web_search`, `fetch_url`, AND `compile_report`. Is this a good design? Explain.**

**Answer:** No, this is poor design because:
- `compile_report` is for synthesis, not search
- Agent might misuse `compile_report` when it should fetch more sources
- Violates separation of concerns
- Increases token costs (longer tool descriptions)
- Makes monitoring and debugging harder

Better design: Search subagent gets ONLY `web_search` and `fetch_url`.

### Question 3: Error Handling
**Q: The search subagent fails to find any sources. What should the coordinator do?**

**Answer:** Implement graceful degradation:
1. Capture the error with context: `{"category": "no_results", "isRetryable": true}`
2. Return partial results (if any were found before failure)
3. Decide: retry with different terms, OR skip to analysis phase with degraded input
4. Log the failure for user visibility
5. Final report should show "partial coverage" rather than complete failure

### Question 4: Context Management
**Q: Explain how provenance tracking works in a multi-agent system. Why is it important?**

**Answer:** Provenance = tracking the origin and path of every piece of information:
- Each source carries metadata: URL, page number, confidence, retrieval time
- When results aggregate up from subagent → coordinator → user, provenance travels with it
- Enables verification: user can trace any claim back to original source
- Allows filtering: "show me only results with >90% confidence"
- Prevents hallucination: no source = no claim
- Required for compliance/auditable AI

### Question 5: Iterative Refinement
**Q: The synthesis subagent produces a report with only 60% coverage of the requested topic. What should happen next?**

**Answer:** Implement refinement loop:
1. Coordinator evaluates synthesis: "coverage_score: 0.60, gaps: [topic_A, topic_B]"
2. Coordinator identifies gaps via quality evaluation tool
3. Coordinator re-delegates to search/analysis: "Focus on missing areas: topic_A, topic_B"
4. Results loop back through analysis and synthesis
5. Loop control: max 3 iterations to prevent infinite loops
6. If gaps persist after max iterations: return "best effort" with gaps noted

---

## How to Run the Exercise

### Prerequisites
```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key-here"
```

### Run the Code
```bash
python research_agent.py
```

### What Happens
1. Coordinator receives a research query
2. Decomposes the task and identifies subagents needed
3. Delegates to search subagent (with isolated context)
4. Delegates to analysis subagent (isolated context, search results passed explicitly)
5. Delegates to synthesis subagent (isolated context, analysis results passed)
6. Evaluates synthesis quality
7. If gaps detected: re-delegates for refinement (iteration loop)
8. Final report shows all phases and provenance

### Output Files
- Console output showing inter-agent communication
- Detailed logs of context passing (no history inheritance)
- Final report with provenance data

### Customization
Edit the `USER_QUERY` variable at the bottom to test different research topics:

```python
USER_QUERY = "Research your own question here"
coordinator = ResearchCoordinator(USER_QUERY)
results = coordinator.run()
```

---

## Advanced Learning Extensions

### Extension 1: Implement Session Management
Save and resume coordinator state:
```python
coordinator.save_state("research_v2")
coordinator = ResearchCoordinator.resume("research_v2")
```

### Extension 2: Add Parallel Subagent Execution
Instead of sequential delegation, invoke multiple subagents in parallel (simulated with threading)

### Extension 3: Implement Tool Routing
Use `tool_choice="any"` for flexible routing, then `tool_choice="required"` to force specific tools in refinement phases

### Extension 4: Add Cost Tracking
Track tokens/cost per subagent to optimize delegation decisions

### Extension 5: Implement Fact-Checking Loop
Add a verification phase where synthesis results are cross-checked against original sources

---

## Summary

This exercise demonstrates:

✓ Hub-and-spoke coordinator architecture
✓ Subagent isolation with explicit context passing
✓ Scoped tool access for security and focus
✓ Provenance tracking across agents
✓ Graceful degradation on failures
✓ Iterative refinement with quality gates
✓ Safety limits on agentic loops
✓ Session management concepts

Study this exercise thoroughly to master multi-agent system design patterns required for the Claude Certified Architect exam.
