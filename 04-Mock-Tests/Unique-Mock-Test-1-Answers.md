# Unique Mock Test 1 - Answer Key

| Q | Answer | Domain | Rationale |
|---|--------|--------|-----------|
| 1 | B | 1 | `tool_use` means execute the tool, append results, and continue the loop. |
| 2 | A | 1 | Parallel Task calls give independent execution contexts for subtasks. |
| 3 | B | 2 | Forced tool choice requires exactly one tool call instead of plain-text completion. |
| 4 | B | 5 | Explicit human escalation requests should be honored immediately. |
| 5 | C | 3 | The most specific scope overrides broader configuration levels. |
| 6 | B | 3 | Path-scoped rules are the clean way to target one subtree. |
| 7 | B | 2 | Tool descriptions are the primary selection mechanism and should be specific. |
| 8 | C | 2 | Structured error fields enable correct retry vs fail behavior. |
| 9 | B | 5 | Scratchpad persistence preserves intermediate findings across passes. |
| 10 | A | 5 | Self-review is weaker because the same instance may confirm its own work. |
| 11 | B | 4 | Batches are cost-efficient and asynchronous for large, non-urgent workloads. |
| 12 | C | 4 | `custom_id` is the reliable way to map out-of-order batch results. |
| 13 | B | 3 | Plan Mode is for clarifying multi-step decomposition before execution. |
| 14 | A | 5 | A non-retryable error is the correct hard-stop signal for downstream systems. |
| 15 | B | 2 | `strict: true` improves exact schema conformance for tool calls. |
| 16 | B | 4 | Prompt engineering starts with success criteria and evals, not random tweaking. |
| 17 | B | 4 | Few-shot examples are often better than more prose for consistency. |
| 18 | B | 4 | Provenance mappings are necessary for evidence-backed audit trails. |
| 19 | C | 5 | Trimming should remove redundancy while preserving decision-critical context. |
| 20 | A | 5 | PostToolUse hooks are ideal for normalization before model reasoning. |
| 21 | D | 3 | Grep searches patterns efficiently without loading full file contents. |
| 22 | B | 1 | Parent agents need Task, and subagents need restricted, domain-specific tool sets. |
| 23 | B | 2 | Programmatic tool filtering by tier scales better than prompt-only controls. |
| 24 | A | 1 | `context: fork` is the explicit way to inherit parent context for a skill. |
| 25 | B | 4 | Confidence calibration needs independent comparison against actual outcomes. |
| 26 | B | 4 | Message Batches are not eligible for zero data retention. |
| 27 | A | 2 | Absent stronger constraints, descriptions most strongly guide selection. |
| 28 | B | 5 | Retry-with-error-feedback is the right response to a fixable validation failure. |
| 29 | B | 5 | Low-confidence findings should go through targeted validation with persistence. |
| 30 | B | 1 | `end_turn` means the model deliberately completed its turn; continuation is your app's job. |

## Notes

- This mock is original and not copied from any existing question bank.
- It intentionally recycles high-frequency exam concepts across different scenarios.