# Gap Coverage Mock Test - Answer Key

> Source: Gaps identified from daronyondem/claude-architect-exam-guide vs existing mock tests

| Q | Answer | Gap Covered | Rationale |
|---|--------|-------------|-----------|
| 1 | B | Uncertain State (Write-Op Timeout) | When a side-effecting operation times out and the outcome is unknown, the tool must communicate uncertainty explicitly and advise against retry. Marking it transient/retryable risks double-charging. Marking it permanent/failed is inaccurate — the charge may have succeeded. |
| 2 | B | Uncertain State — retryable anti-pattern | Marking `retryable: true` for an uncertain outcome causes the agent to retry, potentially sending duplicate notifications. The correct approach is `retryable: false` with a message that the operation may have already completed. |
| 3 | B | Exceptions vs Structured Error Returns | When a tool throws an exception, the agent framework catches it and presents a generic error to the model, stripping the business context (error type, retryable flag, customer explanation) the model needs to respond intelligently. |
| 4 | B | Exceptions vs Structured Error Returns | Errors should be returned as structured data in the tool's `content` field with `isError: true`. This preserves error type, retryability, and customer-facing explanations for the model. Exceptions lose this detail. |
| 5 | B | Lookup-Then-Act Pattern | The lookup-then-act pattern resolves entity ambiguity: a search tool returns matching records with unique IDs, and the action tool operates on a specific ID. This eliminates the model guessing which "Sarah" to use. |
| 6 | B | Two-Tool Token Safety — preview:boolean anti-pattern | A single tool with `preview: boolean` creates a code path where the agent can call the tool with `preview: false`, bypassing review entirely. The unsafe path should be structurally impossible, not merely discouraged. |
| 7 | C | Two-Tool Token Safety Pattern | Two separate tools — preview generates a single-use approval token, execute requires that token — make it structurally impossible to execute without review. System prompt instructions (A) are unreliable. Annotations (D) are hints only. A boolean parameter (B) can be skipped. |
| 8 | B | System Prompt Dilution Over Conversation Length | System prompt influence degrades even in relatively short conversations. As assistant responses accumulate, they create a behavioral pattern that overrides the original system prompt instructions. This is not a token-limit issue — it happens well within capacity. |
| 9 | B | System Prompt Dilution Mitigation | Few-shot examples in the system prompt concretely demonstrate desired behavior and are more resilient to dilution than abstract written rules. Emphatic language (A) does not guarantee compliance. Sending the prompt only once (D) is a bug — it must be in every request. |
| 10 | B | General Principles vs Exhaustive Conditionals | Exhaustive conditionals cause prompt dilution — each additional rule reduces attention to all others. Replacing related conditionals with general principles preserves instruction salience. Only safety-critical rules (must fire deterministically) should stay as explicit conditionals. |
| 11 | B | Principles vs Conditionals — When to Keep Explicit | Rules that must fire deterministically for safety (medical emergencies → call 911) must remain as explicit conditionals. Rules requiring judgment or interpretation (adapting tone, matching knowledge level) work better as general principles. |
| 12 | C | Structured State Objects for Preference Tracking | When users iteratively refine preferences, a structured JSON state object capturing current truth is more reliable than relying on the model to identify the most recent value from a conversation history where old and new values coexist. |
| 13 | B | Context Strategy Selection — Retrieval vs Summarization | Progressive summarization loses precision on numerical data, specific IDs, and exact quotes. When precision recall is required, a structured fact database with retrieval is the correct strategy. Summaries are for general context, not exact figures. |
| 14 | B | MCP Negative Knowledge — What MCP Does NOT Do | MCP is a protocol for tool discovery and invocation. It does not provide automatic authentication handling, built-in retry logic, rate limiting, or performance optimization. These are the developer's responsibility. |
| 15 | B | MCP Tool Annotations Are Untrusted | MCP tool annotations like `readOnlyHint` are self-reported by the server. A tool claiming to be read-only might not actually be read-only. Trust decisions should be based on assessment of the server's trustworthiness, not its self-reported metadata. |
| 16 | B | Interdependent Parameter Constraints → Split Tools | When valid parameter values depend on each other (payment method depends on currency), splitting into separate tools where each structurally enforces its own constraints prevents invalid combinations. The invalid parameter simply doesn't exist in the specialized tool. |
| 17 | B | External Updates via Webhooks | When external updates arrive during an active conversation, appending the update to the next user message before calling the API makes it part of the natural conversation flow. This is cleaner than modifying the system prompt or relying on the agent to query separately. |
| 18 | C | Graceful Degradation / Partial Resolution | When a tool fails mid-workflow but partial work has value, the agent should maximize what it can deliver: confirm eligibility (verified), be transparent about the system issue, and offer alternatives. Don't immediately escalate when partial resolution is possible, and don't assume success. |
| 19 | B | Prompt Versioning for Multi-Session Conversations | Updating a system prompt between sessions can cause the model to contradict prior statements because the new instructions conflict with behavioral patterns in the historical conversation context. Prompt versioning strategies are needed for multi-session continuity. |
| 20 | B | Programmatic Enforcement Spectrum | Emphatic language ("CRITICAL", "NEVER", "ALWAYS") may slightly increase compliance but does not guarantee it. Business rules with legal or financial consequences must be enforced programmatically — via hooks or middleware that intercept tool calls and block execution. The model is removed from the compliance decision entirely. |

## Gap-to-Question Mapping

| Gap # | Gap Description | Questions |
|-------|----------------|-----------|
| 1 | Uncertain State (Write-Operation Timeout) | Q1, Q2 |
| 2 | Exceptions vs Structured Error Returns | Q3, Q4 |
| 3 | Lookup-Then-Act Pattern | Q5 |
| 4 | Two-Tool Token Safety Pattern | Q6, Q7 |
| 5 | System Prompt Dilution | Q8, Q9 |
| 6 | Principles vs Exhaustive Conditionals | Q10, Q11 |
| 7 | Context Management Strategy Selection | Q12, Q13 |
| 8 | MCP Negative Knowledge | Q14 |
| 9 | MCP Annotations Untrusted | Q15 |
| 10 | Interdependent Parameter Constraints | Q16 |
| 11 | External Updates via Webhooks | Q17 |
| 12 | Graceful Degradation / Partial Resolution | Q18 |
| 13 | Prompt Versioning Multi-Session | Q19 |
| 14 | Programmatic Enforcement Spectrum | Q20 |

## Domain Distribution

- **Tool Design & Error Handling**: Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q16 (8 questions — 40%)
- **System Prompt Engineering**: Q8, Q9, Q10, Q11, Q19, Q20 (6 questions — 30%)
- **Context Management**: Q12, Q13, Q17, Q18 (4 questions — 20%)
- **MCP Protocol**: Q14, Q15 (2 questions — 10%)
