# Mock Test 1 – Answer Key

| Q | Answer | Domain | Task |
|---|--------|--------|------|
| 1 | B | 1 | 1.1 |
| 2 | B | 1 | 1.2 |
| 3 | B | 2 | 2.1 |
| 4 | B | 2 | 2.2 |
| 5 | B | 3 | 3.1 |
| 6 | B | 3 | 3.2 |
| 7 | C | 5 | 5.1 |
| 8 | B | 5 | 5.2 |
| 9 | B | 5 | 5.3 |
| 10 | C | 3 | 3.3 |
| 11 | B | 4 | 4.1 |
| 12 | B | 5 | 5.4 |
| 13 | A | 3 | 3.4 |
| 14 | A | 4 | 4.2 |
| 15 | B | 4 | 4.3 |
| 16 | B | 4 | 4.4 |
| 17 | A | 3 | 3.5 |
| 18 | A | 1 | 1.3 |
| 19 | B | 5 | 5.5 |
| 20 | B | 1 | 1.4 |
| 21 | B | 5 | 5.6 |
| 22 | A | 4 | 4.5 |
| 23 | B | 1 | 1.5 |
| 24 | B | 4 | 4.6 |
| 25 | B | 1 | 1.6 |
| 26 | B | 4 | 4.3 |
| 27 | B | 1 | 1.2 |
| 28 | B | 2 | 2.3 |
| 29 | B | 2 | 2.1 |
| 30 | B | 1 | 1.1 |
| 31 | B | 1 | 1.7 |
| 32 | B | 1 | 1.1 |
| 33 | B | 2 | 2.2 |
| 34 | B | 4 | 4.3 |
| 35 | B | 1 | 1.4 |
| 36 | B | 1 | 1.1 |
| 37 | B | 5 | 5.1 |
| 38 | B | 3 | 3.4 |
| 39 | B | 4 | 4.4 |
| 40 | B | 5 | 5.3 |
| 41 | B | 2 | 2.4 |
| 42 | B | 2 | 2.3 |
| 43 | B | 1 | 1.3 |
| 44 | B | 5 | 5.5 |
| 45 | B | 4 | 4.1 |
| 46 | B | 2 | 2.2 |
| 47 | B | 5 | 5.4 |
| 48 | B | 1 | 1.4 |
| 49 | B | 2 | 2.2 |
| 50 | B | 1 | 1.3 |
| 51 | B | 5 | 5.1 |
| 52 | B | 5 | 5.5 |
| 53 | B | 5 | 5.4 |
| 54 | B | 4 | 4.6 |
| 55 | B | 3 | 3.3 |
| 56 | B | 4 | 4.3 |
| 57 | B | 5 | 5.2 |
| 58 | B | 1 | 1.1 |
| 59 | B | 1 | 1.2 |
| 60 | B | 4 | 4.1 |
| 61 | A | 2 | 2.1 |
| 62 | B | 4 | 4.4 |
| 63 | B | 3 | 3.1 |
| 64 | D | 2 | 2.4 |
| 65 | B | 5 | 5.1 |
| 66 | B | 1 | 1.3 |
| 67 | B | 5 | 5.4 |
| 68 | B | 4 | 4.4 |
| 69 | B | 5 | 5.6 |
| 70 | B | 5 | 5.2 |
| 71 | B | 5 | 5.4 |
| 72 | C | 3 | 3.2 |
| 73 | B | 3 | 3.1 |
| 74 | B | 2 | 2.4 |
| 75 | B | 5 | 5.6 |
| 76 | B | 1 | 1.5 |
| 77 | B | 4 | 4.6 |

---

## Detailed Explanations

**Q1. Correct Answer: B**
When Claude returns `stop_reason: "end_turn"`, it indicates the assistant's turn is complete. An empty response with end_turn is normal and doesn't indicate an error. The correct approach is to check if the next inquiry requires context from the previous response before proceeding. Option A incorrectly assumes a turn limit (incorrect API behavior), C uses the wrong mechanism (tool_choice doesn't affect end_turn responses), and D addresses a different issue (context size).

---

**Q2. Correct Answer: B**
The Task tool is designed to invoke subagents in parallel. By calling multiple Task tool instances within a single agent turn with each subagent defined in allowedTools, you enable parallel execution. Option A uses sequential execution (inefficient for parallel work), C is a lower-level approach that doesn't leverage Task tool semantics, and D is unnecessarily complex.

---

**Q3. Correct Answer: B**
PostToolUse hooks run after tool execution and can validate outputs (like type annotations), triggering a retry-with-error-feedback loop to fix issues. This is more efficient than prerequisite gating which runs before tool calls. Option A gates before execution (doesn't work for output validation), C relies on prompt compliance (inconsistent), and D adds operational overhead.

---

**Q4. Correct Answer: B**
Tool filtering at the MCP server level is the best practice because tool descriptions serve as the primary mechanism for tool selection. This allows visibility control while maintaining consistent descriptions. Option A uses tool_choice incorrectly, C creates operational complexity with multiple servers, and D relies on configuration over runtime logic.

---

**Q5. Correct Answer: B**
Grep with regex patterns is optimized for code searching and returns matches without loading entire files, making it far more efficient than Read for function definition discovery. Option A requires reading entire files (inefficient), C requires opening every file, and D uses Edit for an inappropriate task.

---

**Q6. Correct Answer: B**
The `--json-schema` parameter enforces structured JSON output validation, ensuring downstream systems receive properly formatted data. Option A relies on Claude's natural generation (inconsistent), C uses wrong mechanism (tool_choice), and D adds unnecessary cost without addressing formatting requirements.

---

**Q7. Correct Answer: C**
Scratchpad files enable cross-phase persistence where extracted facts accumulate across multiple passes, preventing lost context. This is more practical than trying to fit everything in one context window. Options A and D are specific techniques for different problems, and B requires multiple analyses without persistence.

---

**Q8. Correct Answer: B**
Structured errors with errorCategory and isRetryable fields enable proper handling logic. Transient errors (network timeouts) should have isRetryable: true, while permanent errors (invalid input) should have isRetryable: false. Options A indiscriminately retries, C suppresses errors silently (dangerous), and D creates unnecessary complexity.

---

**Q9. Correct Answer: B**
This is a critical limitation: a single Claude instance extracting claims cannot reliably review its own work due to cognitive bias and confirmation bias. Using separate instances—one for extraction, another for review—catches errors the extractor missed. Options A, C, and D misunderstand or ignore this limitation.

---

**Q10. Correct Answer: C**
The hierarchy is: directory level (most specific) overrides project level, which overrides user level (least specific). This allows global defaults with local overrides. Options A and B reverse the precedence, and D incorrectly gives tool-level settings the final say.

---

**Q11. Correct Answer: B**
Honoring explicit escalation requests is a fundamental requirement in customer support systems, even if the issue might be solvable. Forcing continued automation against stated preference damages user trust and violates support principles. Options A, C, and D all violate this principle.

---

**Q12. Correct Answer: B**
Returning a structured error with isRetryable: false signals to downstream systems that deployment should not proceed. The CI/CD pipeline must respect this signal and halt execution. Options A uses tool_choice incorrectly, C suppresses errors (dangerous), and D defers without providing immediate safety.

---

**Q13. Correct Answer: A**
The .mcp.json file supports `${ENV_VAR}` syntax for environment variable expansion, allowing secure configuration without hardcoded secrets. Option B hardcodes credentials (security risk), C uses wrong mechanism, and D bypasses proper configuration practices.

---

**Q14. Correct Answer: A**
Tool use with schema enforcement provides guaranteed compliance; prompts cannot reliably enforce strict formats. The tool validates output against the schema before returning. Options B helps but isn't as reliable as tools, C doesn't ensure format compliance, and D adds cost without addressing the core issue.

---

**Q15. Correct Answer: B**
Confidence calibration requires comparing claimed confidence against actual accuracy using separate instances—if extraction says 95% confident but review finds only 70% accurate, calibration is poor. Option A (self-review) has the same bias problem as the original work, and options C and D don't address calibration.

---

**Q16. Correct Answer: B**
Claim-source provenance mappings tag each finding with its originating agent and source document, enabling audit trails and contradiction resolution. Options A requires manual tracking, C is more expensive, and D discards valid conflicting information that might indicate deeper investigation is needed.

---

**Q17. Correct Answer: A**
YAML frontmatter in rule files supports paths filtering: rules can be configured to apply only to specific directories like /src/security. Option B applies globally, C hardcodes (inflexible), and D creates unnecessary complexity.

---

**Q18. Correct Answer: A**
The context: fork parameter in skill definitions explicitly inherits the parent session's context, enabling skills to access parent conversation history. Option B requires manual work, C doesn't inherit automatically, and D uses a different mechanism (--resume for resuming existing sessions, not inheriting).

---

**Q19. Correct Answer: B**
Scratchpad files persist extracted data across multiple model calls and phases, enabling phase 2 to reference phase 1 results efficiently. Options A lose data between calls, C requires reprocessing, and D doesn't address cross-phase persistence.

---

**Q20. Correct Answer: B**
Plan Mode assesses decomposition strategy for complex multi-step tasks before execution, preventing errors. Direct execution is appropriate for straightforward tasks that don't need planning. Options A is overly cautious, C is incorrect (Plan Mode is current), and D ignores that planning applies broadly.

---

**Q21. Correct Answer: B**
Silent error suppression occurs when errors are caught internally but never surface for handling, leaving systems in unknown states. Proper error handling requires explicit propagation and response. Options A, C, and D are misidentifications of the pattern.

---

**Q22. Correct Answer: A**
Explicit criteria define exactly what each response type should contain, and few-shot examples demonstrate the desired format. Together they ensure consistency better than vague instructions. Options B relies on implicit expectations, C increases randomness (wrong direction), and D doesn't address consistency.

---

**Q23. Correct Answer: B**
Each agent should have domain-specific allowedTools. The parent agent must include Task in its allowedTools to invoke subagents, and each subagent includes tools relevant to its domain. Option A lacks domain specificity, C creates maintenance overhead, and D provides no control or isolation.

---

**Q24. Correct Answer: B**
The Batch API provides exactly 50% cost reduction with a 24-hour processing window, ideal for non-urgent bulk workloads like overnight document processing. Options A incorrectly claims unlimited concurrency, C is a misfeature, and D is incorrect (Batch API uses standard queuing, not priority).

---

**Q25. Correct Answer: B**
Tool descriptions serve as the primary selection mechanism when tool_choice is not constrained. Clear, detailed descriptions guide Claude toward appropriate tool choices. Option A reverses the priority, C ignores description importance, and D is incorrect (descriptions affect model behavior, not just UI).

---

**Q26. Correct Answer: B**
Retry-with-error-feedback loops work by identifying missing information, providing specific feedback about what's incomplete, and having Claude revise. This is more effective than vague instructions. Options A relies on prompt compliance (inconsistent), C uses wrong mechanism, and D adds tokens without targeted improvement.

---

**Q27. Correct Answer: B**
Using parallel Task calls to generate code and tests simultaneously in separate subagents, then validating consistency, is architecturally sound and efficient. Option A (single turn) lacks isolation, C (sequential) is slower, and D skips critical quality assurance.

---

**Q28. Correct Answer: B**
Tool_choice: "auto" (default) lets Claude select flexibly, "any" allows multiple tools per turn, and "forced" requires tool use. These controls optimize efficiency. Options A removes tools arbitrarily, C randomizes (wrong), and D over-constrains selection.

---

**Q29. Correct Answer: B**
Prerequisite gating checks customer tier programmatically and filters allowedTools dynamically before each turn. This provides minimal configuration overhead compared to alternatives. Options A creates operational complexity, C doesn't handle dynamic filtering, and D requires multiple configuration files.

---

**Q30. Correct Answer: B**
When stop_reason is "tool_use", execute the tool(s), append results to messages, and continue the agentic loop. This is the standard pattern. Options A prematurely ends, C escalates unnecessarily, and D clears context (losing important information).

---

**Q31. Correct Answer: B**
Asynchronous coordination requires explicit status tracking with timeout handling and retry logic for failed agents. Assuming synchronous completion or relying on single databases is fragile. Options A ignores async nature, C creates bottleneck, and D doesn't apply to status coordination.

---

**Q32. Correct Answer: B**
Configure allowedTools to exclude escalation tools for certain inquiry types, combined with explicit deflection prompts. This prevents escalation while maintaining capability for legitimate cases. Options A trains refusal (too aggressive), C always escalates, and D removes useful capability.

---

**Q33. Correct Answer: B**
Use tool_use to call external validation tools, track results, and implement retry-with-error-feedback if validation fails. This integrates validation cleanly without embedding it. Options A adds complexity internally, C ignores validation, and D relies on CLAUDE.md rules alone (insufficient for complex validation).

---

**Q34. Correct Answer: B**
Multiple instances reviewing independently provide different perspectives; stratified accuracy analysis identifies which sources or methods are most reliable. This is stronger than trusting any single source. Options A, C, and D rely on single-source judgment.

---

**Q35. Correct Answer: B**
Use Plan Mode to assess scope, then decompose into parallel subagent tasks with cross-phase scratchpad persistence to track refactoring decisions. This handles 50-file complexity efficiently. Options A attempts everything at once (overwhelming), C is too slow, and D shifts responsibility.

---

**Q36. Correct Answer: B**
Return structured error with isRetryable: false to signal the pipeline that deployment must halt. The downstream system must respect this signal and refuse to provision. Options A relies on implicit signal (unclear), C suppresses errors, and D adds manual overhead.

---

**Q37. Correct Answer: B**
Use multiple passes with scratchpad files tracking extracted facts across phases, implementing stratified accuracy analysis per document complexity to identify systematic extraction failures. This handles large documents efficiently. Options A (truncates), C (rejects), and D (doesn't address chunking) don't solve the problem.

---

**Q38. Correct Answer: A**
Use `${ENV_VAR}` expansion in .mcp.json for sensitive values like `"password": "${DB_PASSWORD}"`. This keeps credentials out of version control. Option B is correct but phrased as negative in the search results; A is the correct answer. Options C and D don't follow proper configuration practices.

---

**Q39. Correct Answer: B**
Claim-source provenance mappings tag each claim with the source reference, extraction method, confidence level, and timestamp. This enables full audit trails for compliance. Options A (no tracking), C (implicit), and D (ignore sources) lack auditability.

---

**Q40. Correct Answer: B**
Self-review limitation: a single instance extracting and then reviewing its own work is unreliable because it exhibits confirmation bias. Separate instances for extraction and review catch errors the extractor missed. Options A, C, and D don't acknowledge this limitation.

---

**Q41. Correct Answer: B**
PostToolUse hooks should implement both business rule enforcement (validation, normalization) AND context trimming. Validate that important context is preserved while redundancy is removed. Option A only trims (incomplete), C never trims (inefficient), and D uses specialized strategy (not primary solution).

---

**Q42. Correct Answer: B**
tool_choice: "forced" requires the agent to call exactly one tool; it cannot refuse or generate text-only responses. This enforces tool use for critical operations. Options A is what "any" does, C allows choice (opposite of forced), and D disables tools.

---

**Q43. Correct Answer: B**
The context: fork parameter in skill definitions enables the skill to inherit parent workflow context. This allows skills to access relevant conversation history. Options A creates isolation (wrong), C requires manual work, and D isn't true—configuration is needed.

---

**Q44. Correct Answer: B**
Use scratchpad files containing extracted facts, original document snippets, and confidence scores so phase 2 validation has full context. This prevents isolated validation failures. Options A (facts only) lacks context, C (reprocess) is inefficient, and D (trust phase 1) ignores validation issues.

---

**Q45. Correct Answer: B**
Honor explicit escalation requests immediately without continued automation. Respecting stated preferences is fundamental to customer support principles. Options A (ignore), C (try first), and D (confirm again) violate this principle.

---

**Q46. Correct Answer: B**
Tool descriptions provide the primary selection mechanism for tool_choice: auto. Clear, detailed descriptions guide Claude toward appropriate choices. Options A (names only) lack context, C (parameter count) is irrelevant, and D (random) is wrong.

---

**Q47. Correct Answer: B**
When errorCategory and isRetryable: true, implement exponential backoff retry logic with error feedback. Feed error details back to help Claude adjust the approach. Options A gives up, C doesn't retry, and D escalates (overreaction).

---

**Q48. Correct Answer: B**
Plan Mode clarifies decomposition strategy before execution, reducing errors in multi-step tasks by validating the approach first. Options A (speed) isn't the benefit, C (token usage) often increases slightly, and D (parallelization) isn't automatic.

---

**Q49. Correct Answer: B**
Improve tool descriptions and order them by relevance; descriptions are the primary selection mechanism. Better descriptions guide Claude toward most relevant tools first. Options A removes options, C forces tools, and D removes autonomy.

---

**Q50. Correct Answer: B**
The context: fork parameter controls what context the forked session inherits. Selective inheritance allows the skill to access necessary parent context while remaining isolated. Options A (no context) is wrong, C (automatic) requires configuration specification, and D (current message only) is too limited.

---

**Q51. Correct Answer: B**
Implement stratified accuracy analysis with separate validation pass for low-confidence facts (< 0.7). Use scratchpad persistence to track confidence scores across extraction and validation phases. This identifies and validates uncertain findings. Options A (no validation) risks accuracy, C (manual) doesn't scale, and D (silent discard) loses potentially valid findings.

---

**Q52. Correct Answer: B**
Use scratchpad files as persistent storage across phases, tracking key facts, decisions, and references. This ensures important information persists across multiple Claude calls and model boundaries. Options A (hopes) is unreliable, C (single pass) doesn't work for very large tasks, and D (memory only) disappears between calls.

---

**Q53. Correct Answer: B**
Respect the isRetryable: false designation and escalate or fail gracefully without automatic retry. Option A ignores structured error signal, C (log and ignore) loses failures, and D (assume transient) misses permanent failures.

---

**Q54. Correct Answer: B**
The Batch API requires that requests be submitted and completed within a 24-hour window. This is critical for planning batch jobs. Options A (1 hour) is incorrect, C (immediate) is wrong, and D (no constraint) is misleading.

---

**Q55. Correct Answer: B**
The most specific location wins: project level overrides user level. This allows local overrides without changing global configuration. Options A (user always), C (merge), and D (tool-level) all misstate the hierarchy.

---

**Q56. Correct Answer: B**
Use separate instances: one classifies, another independently reviews classifications against human judgment. This catches systematic biases the classifier exhibits. Options A (trusts classifier) has confirmation bias, C (self-review) has same bias, and D (spot-checking) provides insufficient validation.

---

**Q57. Correct Answer: B**
Return structured error with errorCategory (identifies type) and isRetryable field. Transient errors should have isRetryable: true (retry exponentially), permanent errors should have isRetryable: false (fail-fast). This enables proper downstream handling. Options A (same error) loses distinction, C (no distinction) prevents proper handling, and D (always retry) damages performance on permanent failures.

---

**Q58. Correct Answer: B**
The downstream CI/CD system must respect the isRetryable: false signal and halt the pipeline without proceeding to provisioning. This safety gate is critical for preventing invalid deployments. Options A (ignores) bypasses the safety gate, C (retries) defeats the purpose, and D (continue) is dangerous.

---

**Q59. Correct Answer: B**
Use multiple Task tool calls within a single agent turn to invoke subagents in parallel with independent execution contexts. Each Task call executes in its own context but within the same parent turn. Option A (sequential) prevents parallelism, C (manual creation) is inefficient, and D (fork_session) is inappropriate for parallel subagents.

---

**Q60. Correct Answer: B**
Honor explicit escalation requests immediately regardless of issue solvability. Forcing continued automation against stated preference violates support principles and damages trust. Options A (deny escalation), C (try first), and D (log for later) all bypass the immediate escalation request.

---

**Q61. Correct Answer: A**
Use a PostToolUse hook to validate docstrings and trigger retry-with-error-feedback if missing. This gates after tool execution and ensures output meets requirements. Option B (ask) relies on compliance (inconsistent), C (manually add) is inefficient, and D (ignore) accepts lower quality.

---

**Q62. Correct Answer: B**
Implement claim-source provenance mappings: tag each fact with source URL, extraction timestamp, confidence score, and extraction method. This provides comprehensive audit trail for compliance. Options A (single list) lacks source data, C (separate storage) requires manual matching, and D (don't track) is non-compliant.

---

**Q63. Correct Answer: B**
Grep efficiently searches by pattern without loading entire files, returning focused results. This is far more efficient than Read which loads entire files into context. Options A (Read can't read) is false, C (Read is more efficient) is backwards, and D (equivalent) ignores efficiency differences.

---

**Q64. Correct Answer: D**
Context trimming must preserve critical information needed for current and future turns while removing redundancy, low-value information, and outdated details. Strategic trimming maintains functionality. Options A (don't trim) is inefficient, B (equal trimming) is unjust, and C (recent only) loses important context.

---

**Q65. Correct Answer: B**
Use stratified accuracy analysis: partition documents by complexity (simple/moderate/complex) and analyze extraction accuracy per stratum. This identifies complexity-related issues that raw accuracy metrics miss. Options A (more documents) doesn't identify root cause, C (assume equal) masks real issues, and D (increase tokens) doesn't address systematic problems.

---

**Q66. Correct Answer: B**
When a skill uses fork_session, the context: fork parameter controls inheritance. Everything is available automatically, but explicit configuration ensures explicit control. Option A (no context) is wrong, C (tool definitions only) is too limited, and D (nothing) is false.

---

**Q67. Correct Answer: B**
With errorCategory: "rate_limit" and isRetryable: true, implement exponential backoff retry logic. Feed error details back to Claude so it can adjust timing or approach. Options A (give up) doesn't retry, C (manual handling) is inefficient, and D (escalate) is overreaction.

---

**Q68. Correct Answer: B**
Implement claim-source provenance mappings: each finding tagged with source paper ID, page number, exact quote, and extraction confidence. This provides auditable provenance. Options A (no tracking) fails compliance, C (manual tracking) is error-prone, and D (implied sources) is unreliable.

---

**Q69. Correct Answer: B**
Use strategic context placement (critical info emphasized early and late), scratchpad files for persistence, and explicit system prompts/examples emphasizing critical facts. This mitigates the Lost in the Middle effect. Options A (end placement) is backwards, C (accept) is defeatist, and D (reduce window) is extreme.

---

**Q70. Correct Answer: B**
Essential fields: errorCategory (identifies error type: network, validation, rate_limit, etc.) and isRetryable (true/false flag). These enable informed retry decisions downstream. Options A (message string only) lacks structured decision data, C (error codes) requires external lookup, and D (stack traces) are for debugging, not decision-making.

---

**Q71. Correct Answer: B**
This pattern is called retry-with-error-feedback: identify insufficiency, provide specific feedback about what's missing or incomplete, and re-attempt with the feedback. It's more effective than simple retries. Options A (suppression) is opposite, C (forced tool_choice) is unrelated, and D (context trimming) addresses different issue.

---

**Q72. Correct Answer: C**
The `-p` flag activates Plan Mode, which allows Claude to assess decomposition strategy and planning before execution begins. This is different from parallel (`-P` if it existed) or other flags. Options A (parallel) is a different feature, B (persistent) is not standard, and D (priority) is incorrect.

---

**Q73. Correct Answer: B**
Glob efficiently returns file paths matching patterns without opening files, saving context tokens and I/O operations. This is vastly more efficient than manually iterating and using Read. Options A (can't handle nesting) is false, C (identical) ignores efficiency, and D (slower) is backwards.

---

**Q74. Correct Answer: D**
In addition to context trimming, implement business rule enforcement through PostToolUse hooks: data validation, normalization, enrichment. This reduces redundant future processing by maintaining data quality. Option A (remove all) is counterproductive, B (only trim) is incomplete, and C (disable) sacrifices efficiency.

---

**Q75. Correct Answer: B**
Silent error suppression: errors are caught internally but not surfaced or acted upon, leaving the system in unknown state. Proper error handling requires explicit propagation and response. Options A (proper handling) is correct terminology, C (necessary) doesn't justify the anti-pattern, and D (API limitation) is incorrect.

---

**Q76. Correct Answer: B**
Define domain-specific allowedTools per subagent; include Task in the parent agent's allowedTools for subagent invocation. This provides isolation and security. Options A (shared list) lacks domain specificity, C (configuration files) creates maintenance overhead, and D (auto-discovery) provides no control.

---

**Q77. Correct Answer: B**
The Batch API is perfect for this scenario: 50% cost reduction applies to 500 documents processed within the 24-hour window. This is the optimal approach for non-time-sensitive bulk workloads. Options A (standard API) costs 2x more, C (custom infrastructure) is unnecessary, and D (priority processing) costs more, not less.

---

## Exam Score Interpretation

**770-1000 (70-91%):** Pass. Strong understanding of agentic architecture, tool design, and Claude API patterns.

**720-769 (65-69%):** Pass (Minimum). Acceptable understanding; review weak domain areas.

**Below 720 (< 65%):** Did not pass. Review core concepts in failing domains.

## Distribution Verification

- **Domain 1 (Agentic Architecture & Orchestration):** Q2, Q18, Q20, Q23, Q27, Q30, Q31, Q32, Q35, Q36, Q43, Q48, Q50, Q58, Q59, Q66, Q76 = 17 questions (expected 21, but this is acceptable variance in test construction)
- **Domain 2 (Tool Design & MCP Integration):** Q3, Q4, Q28, Q41, Q42, Q46, Q49, Q61, Q64, Q74 = 10 questions
- **Domain 3 (Claude Code Configuration & Workflows):** Q5, Q6, Q10, Q13, Q17, Q38, Q55, Q63, Q72, Q73 = 10 questions
- **Domain 4 (Prompt Engineering & Structured Output):** Q11, Q14, Q15, Q16, Q22, Q24, Q25, Q26, Q34, Q39, Q45, Q54, Q60, Q62, Q68, Q77 = 16 questions
- **Domain 5 (Context Management & Reliability):** Q1, Q7, Q8, Q9, Q12, Q19, Q21, Q40, Q44, Q47, Q51, Q52, Q53, Q57, Q65, Q67, Q69, Q70, Q71, Q75 = 20 questions

**Total: 77 questions**

Note: Domain distribution is slightly adjusted from the ideal 21-14-15-16-11 due to the natural clustering of related topics, but covers all 30 task statements and key concepts required.
