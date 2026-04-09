# Final Strict Mock 77 - Answer Key

| Q | Answer | Domain | Rationale |
|---|--------|--------|-----------|
| 1 | B | Domain 1 | `tool_use` means execute the tool, append the result, and continue the loop. |
| 2 | B | Domain 5 | An explicit request for a human should be honored immediately. |
| 3 | A | Domain 1 | Deterministic preconditions are safer than prompt guidance for required sequencing. |
| 4 | B | Domain 2 | Tool descriptions are the primary selection mechanism and should clarify scope and inputs. |
| 5 | C | Domain 1 | Multi-issue support requests are more reliable when decomposed before resolution. |
| 6 | B | Domain 5 | Multiple customer matches require clarification rather than guessing. |
| 7 | C | Domain 5 | Policy gaps should be escalated rather than improvised by the agent. |
| 8 | B | Domain 2 | Smaller, role-relevant toolsets improve selection reliability. |
| 9 | A | Domain 4 | Explicit escalation criteria plus examples improves calibration. |
| 10 | B | Domain 1 | Deterministic output normalization belongs in a hook or equivalent post-tool processing layer. |
| 11 | C | Domain 2 | Structured errors enable retries, corrections, and escalation decisions. |
| 12 | B | Domain 1 | `end_turn` means the model finished; the application must drive the next turn. |
| 13 | D | Domain 1 | Good human handoffs include identity, issue summary, actions taken, current state, and the next recommendation. |
| 14 | A | Domain 4 | Few-shot examples are most useful when ambiguity remains after descriptions are improved. |
| 15 | B | Domain 5 | Once the user explicitly asks for a human, escalation should occur immediately. |
| 16 | D | Domain 1 | Prompting Claude to bundle related tool requests can reduce avoidable loop iterations. |
| 17 | A | Domain 1 | Compliance-critical constraints should be enforced programmatically, not only by prompting. |
| 18 | C | Domain 5 | Sentiment alone is not a reliable escalation trigger. |
| 19 | B | Domain 2 | Programmatic tool filtering by tier is the cleanest control mechanism. |
| 20 | B | Domain 1 | The coordinator centralizes routing, aggregation, and error handling decisions. |
| 21 | A | Domain 1 | Parallel subagent execution is done via multiple Task calls with explicit context. |
| 22 | D | Domain 5 | Conflicting source values should be preserved with attribution rather than collapsed. |
| 23 | A | Domain 5 | Coordinators need structured failure context and any partial progress that exists. |
| 24 | B | Domain 2 | Distinct names and descriptions reduce overlapping tool ambiguity. |
| 25 | C | Domain 1 | The coordinator decomposed the research space too narrowly, causing systematic coverage gaps. |
| 26 | A | Domain 2 | Least-privilege tool design gives synthesis only the narrow verification it actually needs. |
| 27 | C | Domain 5 | A timeout is a failure state; 0 results may be a valid business outcome. |
| 28 | A | Domain 4 | Structuring the synthesis input with key findings first is a prompt-design tactic that reduces missed mid-context information. |
| 29 | A | Domain 4 | Returning structured facts instead of verbose dumps fixes the context problem at the source. |
| 30 | A | Domain 1 | Upfront partitioning reduces duplicate work and improves delegation quality. |
| 31 | B | Domain 2 | The synthesis agent has a broader tool surface than its role requires. |
| 32 | D | Domain 5 | Limited local recovery plus structured propagation is the preferred resilience pattern. |
| 33 | C | Domain 4 | Reports should separate confirmed and disputed findings with attribution. |
| 34 | C | Domain 1 | Subagents do not inherit the parent's needed context unless it is explicitly passed. |
| 35 | B | Domain 1 | A fresh session with a structured summary is often safer than resuming with stale results. |
| 36 | B | Domain 1 | `fork_session` supports parallel branches from shared context. |
| 37 | B | Domain 1 | Resume is risky when prior tool outputs may be stale relative to the current environment. |
| 38 | B | Domain 1 | Open-ended investigations fit dynamic adaptive decomposition based on findings. |
| 39 | A | Domain 3 | User-level CLAUDE.md is not shared with teammates through version control. |
| 40 | B | Domain 3 | `@path` is the supported way to modularize CLAUDE.md with external files. |
| 41 | B | Domain 3 | `.claude/rules/` with `paths` is designed for conditional loading by file pattern. |
| 42 | A | Domain 3 | Path-scoped rules work best for cross-cutting conventions spread across the repository. |
| 43 | A | Domain 3 | Project slash commands belong in `.claude/commands/` so the team shares them. |
| 44 | C | Domain 3 | `context: fork` isolates verbose skill output from the main session. |
| 45 | B | Domain 3 | `argument-hint` is the feature meant to prompt for missing invocation arguments. |
| 46 | A | Domain 3 | Planning mode is the right start for large, ambiguous, architecture-heavy work. |
| 47 | B | Domain 3 | Direct execution is best for simple, bounded fixes with a known root cause. |
| 48 | D | Domain 3 | `-p` runs Claude Code in non-interactive headless mode for CI. |
| 49 | A | Domain 3 | `--output-format json` plus `--json-schema` gives reliably parseable structured output. |
| 50 | C | Domain 3 | Prior findings let Claude report only new or unresolved issues on reruns. |
| 51 | B | Domain 3 | On-demand skills keep specialized examples out of unrelated tasks. |
| 52 | D | Domain 3 | Project `.mcp.json` plus environment variables is the shared and secure team setup. |
| 53 | B | Domain 3 | `/memory` is the built-in command associated with persisted Claude Code memory or instructions. |
| 54 | B | Domain 2 | Read is the right tool after Grep identifies a relevant file. |
| 55 | B | Domain 2 | The documented fallback for ambiguous Edit operations is Read, modify, then Write. |
| 56 | B | Domain 5 | `/compact` can save context but may lose precise details during summarization. |
| 57 | A | Domain 5 | Isolating verbose discovery in a subagent protects the main context for design and implementation. |
| 58 | C | Domain 4 | Optional or nullable fields reduce hallucinated values when absence is legitimate. |
| 59 | B | Domain 4 | `other` or `unclear` plus detail preserves extensibility honestly. |
| 60 | C | Domain 4 | Strict schemas prevent syntax and shape violations, not all semantic errors. |
| 61 | B | Domain 4 | Extracting both stated and calculated totals creates a structured contradiction check. |
| 62 | B | Domain 4 | Specific validation feedback plus the original source is the best retry input. |
| 63 | C | Domain 4 | Retries cannot recover information that simply does not exist in the source. |
| 64 | A | Domain 4 | Message Batches fit asynchronous, cost-sensitive, non-urgent processing. |
| 65 | B | Domain 4 | The guide highlights the up-to-24-hour window and lack of latency SLA. |
| 66 | B | Domain 4 | One-shot batches do not support iterative tool-calling loops in the same interaction. |
| 67 | B | Domain 4 | Asking clarifying questions before design is the interview pattern. |
| 68 | B | Domain 5 | Low-confidence, high-impact fields should route to further validation or human review. |
| 69 | B | Domain 2 | `any` guarantees a tool call while still letting Claude choose among available tools. |
| 70 | A | Domain 2 | `strict: true` improves conformance to the declared schema. |
| 71 | B | Domain 2 | Clear purpose and boundaries are the first fix for overlapping tools. |
| 72 | B | Domain 2 | MCP resources provide readable context such as catalogs or schemas without taking action. |
| 73 | B | Domain 2 | MCP prompts are predefined templates for common tasks. |
| 74 | B | Domain 1 | A stable, repeatable sequence of extraction stages is prompt chaining or a fixed pipeline. |
| 75 | C | Domain 1 | Discovery-driven branching based on the document structure is dynamic adaptive decomposition. |
| 76 | A | Domain 1 | Chunk agents need explicit context and metadata because subagents do not inherit parent context automatically. |
| 77 | B | Domain 1 | The coordinator should aggregate structured chunk outputs and manage final synthesis with attribution intact. |

## Domain Distribution

- Domain 1: 21 questions
- Domain 2: 14 questions
- Domain 3: 15 questions
- Domain 4: 15 questions
- Domain 5: 12 questions

## Notes

- This final mock is original.
- It intentionally combines the stronger exam-style questions from the first strict simulation with the guide-gap topics added in the second one.