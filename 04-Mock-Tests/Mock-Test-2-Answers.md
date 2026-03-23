# Mock Test 2 – Answer Key

| Q | Answer | Domain | Task |
|---|--------|--------|------|
| 1 | C | 1 | 1.1 |
| 2 | B | 1 | 1.2 |
| 3 | B | 2 | 2.1 |
| 4 | B | 1 | 1.3 |
| 5 | A | 3 | 3.3 |
| 6 | B | 4 | 4.3 |
| 7 | B | 2 | 2.1 |
| 8 | B | 5 | 5.2 |
| 9 | B | 3 | 3.1 |
| 10 | D | 4 | 4.1 |
| 11 | A | 1 | 1.4 |
| 12 | B | 3 | 3.2 |
| 13 | B | 4 | 4.2 |
| 14 | A | 4 | 4.3 |
| 15 | B | 2 | 2.2 |
| 16 | B | 1 | 1.3 |
| 17 | B | 3 | 3.2 |
| 18 | B | 3 | 3.3 |
| 19 | C | 4 | 4.3 |
| 20 | B | 3 | 3.1 |
| 21 | B | 1 | 1.1 |
| 22 | B | 2 | 2.3 |
| 23 | B | 4 | 4.1 |
| 24 | B | 4 | 4.3 |
| 25 | B | 3 | 3.2 |
| 26 | B | 3 | 3.1 |
| 27 | B | 2 | 2.1 |
| 28 | B | 5 | 5.1 |
| 29 | B | 5 | 5.3 |
| 30 | B | 5 | 5.3 |
| 31 | B | 2 | 2.1 |
| 32 | B | 3 | 3.2 |
| 33 | B | 1 | 1.3 |
| 34 | B | 3 | 3.2 |
| 35 | B | 4 | 4.1 |
| 36 | B | 4 | 4.2 |
| 37 | B | 3 | 3.3 |
| 38 | B | 3 | 3.1 |
| 39 | B | 3 | 3.1 |
| 40 | A | 4 | 4.1 |
| 41 | B | 5 | 5.2 |
| 42 | B | 4 | 4.3 |
| 43 | B | 2 | 2.1 |
| 44 | B | 3 | 3.2 |
| 45 | B | 5 | 5.1 |
| 46 | B | 3 | 3.3 |
| 47 | B | 5 | 5.3 |
| 48 | B | 3 | 3.2 |
| 49 | B | 4 | 4.3 |
| 50 | B | 3 | 3.1 |
| 51 | B | 1 | 1.3 |
| 52 | B | 3 | 3.2 |
| 53 | B | 4 | 4.1 |
| 54 | B | 1 | 1.2 |
| 55 | B | 5 | 5.2 |
| 56 | B | 5 | 5.3 |
| 57 | B | 3 | 3.2 |
| 58 | B | 4 | 4.1 |
| 59 | B | 2 | 2.1 |
| 60 | B | 3 | 3.2 |
| 61 | B | 1 | 1.1 |
| 62 | B | 4 | 4.1 |
| 63 | B | 5 | 5.2 |
| 64 | B | 1 | 1.2 |
| 65 | B | 5 | 5.3 |
| 66 | B | 3 | 3.1 |
| 67 | B | 3 | 3.3 |
| 68 | B | 5 | 5.3 |
| 69 | B | 2 | 2.2 |
| 70 | B | 4 | 4.3 |
| 71 | B | 3 | 3.2 |
| 72 | B | 4 | 4.1 |
| 73 | B | 3 | 3.2 |
| 74 | B | 1 | 1.2 |
| 75 | B | 5 | 5.1 |
| 76 | B | 4 | 4.1 |
| 77 | B | 1 | 1.2 |

---

## Detailed Explanations

**Q1. Correct Answer: C**
Iteration caps are safety nets, not primary control mechanisms, and apply globally. To prevent recursive tool use in a multi-agent system, use `allowedTools` gating in the Task definition, which restricts subagents to specific tools at runtime. This is the architectural pattern for role-based tool access control.

**Q2. Correct Answer: B**
`pause_turn` indicates the server-side iteration limit (default 10) was reached. The recovery is to append the pause_turn response and continue the conversation, allowing Claude to finish processing. This is distinct from timeouts or tool failures.

**Q3. Correct Answer: B**
Tool descriptions must prevent disambiguation issues. Explicit input format constraints help Claude select the right tool without reasoning overload—vague descriptions force Claude to reason through multiple options, wasting tokens and causing errors.

**Q4. Correct Answer: B**
Parallel Task calls execute subagents concurrently. The coordinator must synchronize on completion by checking Task status and ensuring all complete before proceeding. Sequencing them defeats the purpose; prompting for parallelization relies on lucky Claude behavior.

**Q5. Correct Answer: A**
PostToolUse hooks normalize output, enforce constraints, and filter sensitive data BEFORE Claude processes tool results. Placing enforcement in CLAUDE.md or descriptions is guidance, not enforcement; hooks provide actual runtime gating.

**Q6. Correct Answer: B**
For 99% accuracy, combine JSON schema (format enforcement), few-shot examples (format consistency), and retry-on-error feedback loops (semantic validation). Tool_choice forced is too rigid; self-review is unreliable for extraction tasks.

**Q7. Correct Answer: B**
Ambiguous tools need explicit input format constraints in descriptions to guide Claude. Tool removal hurts functionality; tool_choice forced prevents flexibility; post-validation doesn't prevent wrong calls, just catches them.

**Q8. Correct Answer: B**
Explicit human escalation honors the human judgment priority. Automatic re-runs waste resources; silent acceptance ignores confidence signals; confidence scores alone don't drive decisions—humans should explicitly decide whether to escalate.

**Q9. Correct Answer: B**
`fork_session` creates isolated context by design. The subagent doesn't inherit the parent's CLAUDE.md. You must explicitly re-include rules, though @import doesn't help in fork_session isolation—you must manually include the rule.

**Q10. Correct Answer: D**
Structured outputs compile JSON schemas into grammar constraints during token generation, enforcing validity at the source. This is the core difference from prompting for JSON, which often fails. Streaming, validation, and optional fields are possible.

**Q11. Correct Answer: A**
Dynamic decomposition via Task spawning excels when subtasks are unknown until runtime (dependent on analysis). Prompt chaining is simpler for predetermined decompositions; neither is universally "better."

**Q12. Correct Answer: B**
`--resume` checkpoints CI/CD workflows, allowing restart from the last completed step rather than re-running everything. This saves computation and time for interrupted builds.

**Q13. Correct Answer: B**
Append the error + failed output to the conversation, letting Claude reason about retry appropriateness. Don't auto-retry; don't escalate reflexively. Claude now has context to decide: retry with different ID, escalate, or proceed differently.

**Q14. Correct Answer: A**
Batch API's primary benefit is 50% cost savings + asynchronous processing over 24 hours, enabling high-volume processing without real-time latency constraints. Faster responses are not guaranteed.

**Q15. Correct Answer: B**
Respect the `errorCategory: "retryable"` field even though HTTP 200—it's domain-specific error information that the tool provider uses to signal retryability. HTTP status alone is insufficient.

**Q16. Correct Answer: B**
Hub-and-spoke requires all communication through the coordinator to maintain clear information flow and decision authority. Direct subagent-to-subagent communication violates the architectural pattern and creates hidden dependencies.

**Q17. Correct Answer: B**
Edit requires exact `old_string` match. Always Read the file first to get precise content, then Edit with the exact string. This is the safe, reliable pattern even though it seems redundant.

**Q18. Correct Answer: B**
Interacting tasks must be batched together in a single request to ensure sequential execution within one API call, preventing race conditions. Parallel execution, different paths, or sleeps don't prevent conflicts at the fundamental level.

**Q19. Correct Answer: C**
For 50 complex fields, combine multiple targeted few-shot examples (different examples for different field types), JSON schema validation (format constraints), and retry loops (semantic validation). Single examples and pure schema are insufficient.

**Q20. Correct Answer: B**
YAML frontmatter in `.claude/rules/` files configures runtime context loading behavior—which rules apply, in what order, and under what conditions. It's not just documentation; it controls Claude's actual behavior.

**Q21. Correct Answer: B**
Parallel Task calls with isolated context budgets prevent overload. Shared context with subagents risks exceeding limits; sequential defeats parallelism; no configuration leaves you unprotected.

**Q22. Correct Answer: B**
Use `${ENV_VAR}` syntax for project-scoped environment variable substitution in `.mcp.json`. Hard-coding is unsafe; CLI args are less portable; separate secrets files require additional configuration.

**Q23. Correct Answer: B**
JSON schema enforcement + few-shot guidance work together. The schema requires the field; examples showing only required fields teach Claude not to waste tokens on optionals. Both constraints together drive consistent behavior.

**Q24. Correct Answer: B**
Use `custom_id` for lookup—your tracking mechanism for retrieving specific batch results. Polling every hour is inefficient; re-running wastes resources; email delivery is not how Batch API returns results.

**Q25. Correct Answer: B**
Compact at ~60% capacity (before critical tasks) to maintain accuracy. Compacting at start wastes early context; 90% is too late; and compression preserves information when done strategically.

**Q26. Correct Answer: B**
`.claude/commands/` defines custom slash commands (what `/analyze` does); `.claude/skills/` are reusable code modules/workflows. Commands are for user-triggered actions; skills are building blocks.

**Q27. Correct Answer: B**
Tool descriptions' input format constraints enable disambiguation when tools overlap (e.g., when success conditions differ). Claude reads descriptions to decide which tool fits; overlapping names require explicit description differences.

**Q28. Correct Answer: B**
Case facts blocks anchor findings to specific evidence sources. This preserves claim-source provenance, enabling later verification. Ignoring prevents accountability; self-review is unreliable for catching speculation; human review for everything is inefficient.

**Q29. Correct Answer: B**
For 150k tokens, proactively compact at 60% (~90k) and maintain scratchpad files for cross-phase findings. Automatic handling is insufficient; infinite context doesn't exist; many short sessions lose continuity.

**Q30. Correct Answer: B**
Stratified accuracy analysis (grouping by field type) reveals that dates/phones are 80% accurate while others are 95%. Single aggregate score masks this critical insight; self-review can't measure ground truth; user feedback alone is slow.

**Q31. Correct Answer: B**
MCP resources allow Claude to discover and browse available tools dynamically, enabling smart selection without reasoning overload. It prevents Claude from reasoning about unavailable tools.

**Q32. Correct Answer: B**
Plan mode for architectural decisions (design reasoning before code); direct mode for small, isolated changes. They're not equivalent; direct mode is appropriate for focused work.

**Q33. Correct Answer: B**
Check Task completion status and implement explicit synchronization before proceeding. Assuming completion invites failures; nested prompts lack clarity; natural language signals are unreliable.

**Q34. Correct Answer: B**
Grep with glob filtering targets relevant files efficiently (e.g., `--glob "*.py"` to exclude binary/config files). Sequential Read is O(n) scalability nightmare; Find + Read is redundant; custom scripts reinvent the wheel.

**Q35. Correct Answer: B**
Few-shot examples, JSON schema constraints, and tool_choice configurations enforce format consistency together. Examples alone are suggestions; the model doesn't invent formats randomly, but needs all three layers for reliability.

**Q36. Correct Answer: B**
Append error message + failed output + original input. This gives Claude full context to decide: retry (different approach), escalate, or proceed differently. Don't hide failures or auto-retry.

**Q37. Correct Answer: B**
Sequential fixes targeting specific issues from the first pass (e.g., "fix error X, improve performance Y"). Rewriting loses prior work; accepting skips refinement; unrelated questions waste context.

**Q38. Correct Answer: B**
More specific rules (child directory) override broader ones (parent/global). This precedence prevents conflicts; you don't manually resolve—hierarchy does it automatically.

**Q39. Correct Answer: B**
`fork_session` isolates context completely by design. The subagent doesn't see the parent's CLAUDE.md. You must explicitly pass instructions; @import doesn't bridge fork_session isolation.

**Q40. Correct Answer: A**
Structured outputs with schema constraints actively prevent invalid output—Claude's token generation is constrained to reject invalid SKUs during inference. The output cannot be invalid; it's regenerated if needed.

**Q41. Correct Answer: B**
Honor the finding explicitly and update the coordinator's mental model. Suppression is deception; auto-escalation skips reasoning; retry-until-agreement corrupts the subagent's integrity.

**Q42. Correct Answer: B**
50% cost savings (lower pricing tier) + asynchronous processing (spread over 24 hours) are the primary advantages. Response speed is not guaranteed; error handling is still required.

**Q43. Correct Answer: B**
Explicit input format constraints + success conditions in descriptions disambiguate overlapping tools. Listing outputs doesn't help; removing tools sacrifices functionality; identical descriptions defeat the purpose.

**Q44. Correct Answer: B**
Read safely retrieves file content. Edit requires exact matches; Glob finds files; Bash is low-level. Read is the safe starting point for safe manipulation.

**Q45. Correct Answer: B**
Claim-source provenance mappings connect decisions to evidence. Transparent reasoning enables verification. More tool calls don't add clarity; implicit trust is risky; removing escalation removes a safety valve.

**Q46. Correct Answer: B**
Multi-pass focused reviews (structure → logic → tests) catch different error categories. Single comprehensive reviews suffer attention dilution (trying to catch everything at once often misses things); trusting output without verification risks bugs.

**Q47. Correct Answer: B**
Scratchpad files preserve findings across context resets, enabling later accuracy validation stratified by source. They're critical for long conversations where context resets happen. Ephemeral findings are lost.

**Q48. Correct Answer: B**
Explore subagents are valuable for verbose discovery of complex structures (e.g., discovering all helper functions in a module). Use them when you need comprehensive discovery, not for every task.

**Q49. Correct Answer: B**
Query failed results by `custom_id` and retry only those. Retrying the entire batch wastes resources; ignoring wastes data; manual inspection doesn't scale to 100k documents.

**Q50. Correct Answer: B**
Later imports override earlier ones; imports are resolved sequentially. This allows gradual specification: global rules, then project-specific overrides, then user overrides.

**Q51. Correct Answer: B**
Parallel Task calls to all subagents with synchronization before coordinator proceeds. Sequential calls waste the speed advantage; nested prompts lack clarity; fork_session in series defeats parallelism.

**Q52. Correct Answer: B**
Read the file to get exact content (including whitespace), then use that exact string in Edit. This fallback prevents edit failures due to formatting mismatches.

**Q53. Correct Answer: B**
Few-shot examples must show edge cases and optional field handling to establish format consistency. Irrelevant fields clutter; comments aren't necessary; personal notes are noise.

**Q54. Correct Answer: B**
`allowedTools` in Task definitions gates tool access at runtime—subagents literally cannot call unlisted tools. This is actual enforcement, not just documentation.

**Q55. Correct Answer: B**
Silent error suppression causes Claude to make decisions based on false assumptions about success. Errors must be visible so Claude can reason appropriately.

**Q56. Correct Answer: B**
Retain key findings + decisions at start (lost-in-the-middle mitigation), discard verbose exploration. Starting fresh loses context; retaining everything wastes tokens.

**Q57. Correct Answer: B**
Use fork_session or temporary branches to test changes in isolation. Direct application risks the codebase; trust alone is insufficient; manual review doesn't scale.

**Q58. Correct Answer: B**
`--output-format json` guarantees parseable output structure, enabling reliable downstream processing. Parsing doesn't fail; no manual error handling for parse errors.

**Q59. Correct Answer: B**
Tool descriptions with explicit input format constraints make it clear which tool applies to each use case. No constraints force Claude to guess; descriptions prevent the need to remove tools.

**Q60. Correct Answer: B**
Write creates a new file with specified content. Read on a non-existent file fails; Edit can't replace non-existent content; Bash is lower-level.

**Q61. Correct Answer: B**
Isolated Task context (fork_session) + explicit context budgets in Task definitions prevent overload. Shared context risks exceeding limits; sequential removes parallelism.

**Q62. Correct Answer: B**
Schema constraints enforce required fields; examples guide format for optional fields. Schema enforcement + example guidance work together.

**Q63. Correct Answer: B**
When explicit human instructions indicate escalation is needed (e.g., "escalate if X"), Claude should honor that immediately. Never requires automatic escalation (humans decide); decision-making can't be fully abdicated.

**Q64. Correct Answer: B**
PostToolUse hooks normalize output (extract data), enforce constraints (validate format), and trim sensitive data (PII removal) before Claude processes results. User display and request modification are outside hook scope.

**Q65. Correct Answer: B**
Per-finding confidence + labeled ground truth enable accuracy analysis by confidence bucket (stratified analysis). Aggregate scores mask segments; no tracking prevents analysis.

**Q66. Correct Answer: B**
Claude invokes `/analyze` when the user types it OR when Claude decides it's needed (if designed that way). It's not automatic on every message; it's not background; user invocation is primary.

**Q67. Correct Answer: B**
Gather specific feedback (tests fail, performance issue, unclear logic) and fix sequentially. Rewriting loses prior work; no second pass skips refinement.

**Q68. Correct Answer: B**
Detailed scratchpad mapping findings to sources enables later accuracy validation and claim-source provenance. Ephemeral findings are lost; user feedback alone doesn't provide ground truth.

**Q69. Correct Answer: B**
Respect the `isError` field—it's domain-specific error information. HTTP 200 is transport-level success; `isError` is application-level. Trust the service's error indication.

**Q70. Correct Answer: B**
Results are available immediately upon completion. 24 hours is the maximum—processing can complete earlier. Withholding results is not how Batch API works.

**Q71. Correct Answer: B**
Plan mode outputs detailed reasoning and proposed architecture before implementation. This allows review before proceeding to direct mode. It's not just thinking; it's a deliverable review step.

**Q72. Correct Answer: B**
Required schema fields force inclusion; few-shot examples show complete extraction; validation loops enforce completeness. Schema alone is insufficient; pure model trust is unreliable.

**Q73. Correct Answer: B**
`--json-schema` validation flag enables output validation against the schema; failures trigger prompts to fix. It's not just documentation; it's runtime validation.

**Q74. Correct Answer: B**
Define task prerequisites explicitly so dependencies are clear. Spawn new Tasks as needed for additional analysis. Restarting wastes work; manual re-prompting is error-prone.

**Q75. Correct Answer: B**
Place critical decision points at the start (after case facts block) and end of context to maximize recall (lost-in-the-middle mitigation). Middle position loses salience; perfect recall is mythical.

**Q76. Correct Answer: B**
JSON schema enforces output format; few-shot examples + retry loops ensure semantic correctness. Format validation is necessary but insufficient.

**Q77. Correct Answer: B**
Explicit task prerequisites define data dependencies programmatically, preventing downstream tasks from running with incomplete input. Execution order always matters for dependent tasks; prerequisites make this explicit.

---

## Domain & Task Distribution Summary

**Domain 1: Agentic Architecture & Orchestration (21 questions)**
- Task 1.1 (stop_reason, iteration caps): Q1, Q21, Q61
- Task 1.2 (end_turn, tool_use, pause_turn): Q2, Q54, Q64, Q77
- Task 1.3 (coordinator-subagent, hub-spoke, Task spawning): Q4, Q16, Q33, Q51
- Task 1.4 (prompt chaining vs dynamic decomposition): Q11

**Domain 2: Tool Design & MCP Integration (14 questions)**
- Task 2.1 (tool descriptions drive selection, overlap disambiguation): Q3, Q7, Q27, Q31, Q43, Q59
- Task 2.2 (errorCategory, isRetryable): Q15, Q69
- Task 2.3 (MCP .mcp.json, environment variables): Q22

**Domain 3: Claude Code Configuration & Workflows (15 questions)**
- Task 3.1 (CLAUDE.md hierarchy, rules YAML, frontmatter): Q9, Q20, Q26, Q38, Q39, Q50, Q66
- Task 3.2 (Read/Edit/Glob, --resume, plan vs direct, Explore): Q12, Q17, Q25, Q32, Q34, Q44, Q48, Q52, Q57, Q71, Q73
- Task 3.3 (PostToolUse hooks, iterative refinement, sequential fixes): Q5, Q18, Q37, Q46, Q64, Q67

**Domain 4: Prompt Engineering & Structured Output (16 questions)**
- Task 4.1 (few-shot, tool_choice, JSON schema): Q6, Q10, Q23, Q35, Q40, Q53, Q58, Q62, Q72, Q76
- Task 4.2 (retry-with-error-feedback): Q13, Q36
- Task 4.3 (Batch API, custom_id, costs): Q14, Q24, Q42, Q49, Q70

**Domain 5: Context Management & Reliability (11 questions)**
- Task 5.1 (case facts, lost-in-the-middle, claim-source provenance): Q28, Q45, Q75
- Task 5.2 (explicit human escalation, error suppression anti-pattern): Q8, Q41, Q55, Q63
- Task 5.3 (scratchpad files, stratified accuracy, confidence calibration): Q29, Q30, Q47, Q56, Q65, Q68
