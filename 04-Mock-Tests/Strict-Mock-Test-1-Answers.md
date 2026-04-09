# Strict Mock Test 1 - Answer Key

| Q | Answer | Domain | Rationale |
|---|--------|--------|-----------|
| 1 | B | Domain 1 | `tool_use` means run the tool, append the result, and continue the loop. |
| 2 | B | Domain 5 | Explicit human requests should be honored immediately. |
| 3 | A | Domain 1 | Deterministic preconditions are safer than prompt guidance for required ordering. |
| 4 | B | Domain 2 | Tool descriptions are the primary selection mechanism. |
| 5 | C | Domain 1 | Multi-issue requests are more reliable when decomposed before resolution. |
| 6 | B | Domain 5 | Multiple customer matches require clarification, not guessing. |
| 7 | C | Domain 5 | Policy gaps should be escalated instead of invented by the agent. |
| 8 | B | Domain 2 | Smaller, role-relevant toolsets improve selection reliability. |
| 9 | A | Domain 4 | Explicit criteria plus examples improves escalation calibration. |
| 10 | B | Domain 1 | PostToolUse normalization is the right deterministic mechanism. |
| 11 | C | Domain 2 | Structured errors enable retries, corrections, or escalation decisions. |
| 12 | B | Domain 1 | `end_turn` means the model finished; your app must drive the next turn. |
| 13 | D | Domain 1 | Handoffs must include identity, state, actions, and the next recommendation. |
| 14 | A | Domain 4 | Few-shot examples help most when ambiguity remains after clearer descriptions. |
| 15 | B | Domain 5 | Once the user explicitly asks for a human, escalation should happen immediately. |
| 16 | D | Domain 1 | Claude can bundle multiple related tool requests in one turn when instructed well. |
| 17 | A | Domain 1 | High-stakes compliance constraints belong in hooks or preconditions. |
| 18 | C | Domain 5 | Sentiment alone is not a reliable escalation trigger. |
| 19 | B | Domain 2 | Tier-based tool filtering should be handled programmatically. |
| 20 | A | Domain 4 | Evaluator-optimizer style self-critique improves completeness consistently. |
| 21 | B | Domain 1 | The coordinator centralizes routing, aggregation, and error handling. |
| 22 | A | Domain 1 | Parallel Task calls with explicit context are the standard pattern. |
| 23 | D | Domain 5 | Conflicting values should be preserved with attribution, not collapsed. |
| 24 | A | Domain 5 | Coordinators need structured failure context and partial progress. |
| 25 | B | Domain 2 | Renaming and clarifying overlapping tools fixes the root ambiguity. |
| 26 | C | Domain 1 | Overly narrow decomposition caused the coverage gap. |
| 27 | A | Domain 1 | A limited verification tool applies least privilege while reducing round-trips. |
| 28 | C | Domain 5 | A timeout and a valid empty result are semantically different outcomes. |
| 29 | B | Domain 5 | Key findings at the top and sections mitigate lost-in-the-middle effects. |
| 30 | A | Domain 4 | Returning structured facts instead of verbose dumps improves downstream synthesis. |
| 31 | A | Domain 1 | Partitioning the space upfront avoids duplicated effort. |
| 32 | B | Domain 2 | The synthesis agent has more tool access than its role actually requires. |
| 33 | D | Domain 5 | Limited local recovery plus structured propagation is the preferred pattern. |
| 34 | B | Domain 4 | Good synthesis separates confirmed and disputed findings explicitly. |
| 35 | C | Domain 1 | Subagents need required context passed explicitly in the prompt. |
| 36 | B | Domain 1 | Open-ended tasks fit adaptive decomposition based on findings. |
| 37 | A | Domain 1 | Predictable workflows fit prompt chaining / fixed pipelines. |
| 38 | C | Domain 2 | Transient, validation, business, and permission are the useful operational categories. |
| 39 | B | Domain 4 | Per-file passes plus an integration pass address attention dilution directly. |
| 40 | A | Domain 4 | Stratified evaluation exposes weak segments hidden by strong aggregate metrics. |
| 41 | A | Domain 3 | User-level instructions are not shared with new teammates. |
| 42 | B | Domain 3 | Path-scoped `.claude/rules/` files are meant for this exact problem. |
| 43 | A | Domain 3 | Project commands live in `.claude/commands/` under version control. |
| 44 | C | Domain 3 | `context: fork` isolates verbose skill output from the main session. |
| 45 | B | Domain 3 | `argument-hint` prompts for missing required parameters. |
| 46 | A | Domain 3 | Personal variants should use a different command name under user scope. |
| 47 | A | Domain 3 | Planning mode is for large, ambiguous, architecture-heavy work. |
| 48 | B | Domain 3 | Direct execution fits simple, bounded changes with a clear cause. |
| 49 | D | Domain 3 | `-p` is the correct non-interactive Claude Code mode for CI. |
| 50 | A | Domain 3 | `--output-format json` with `--json-schema` gives reliable structured CI output. |
| 51 | C | Domain 3 | Prior findings let Claude report only new or still-open issues. |
| 52 | B | Domain 3 | On-demand skills keep specialized examples out of unrelated sessions. |
| 53 | D | Domain 3 | Project `.mcp.json` with env vars is the shared, safe team setup. |
| 54 | A | Domain 3 | Explore-style subagents protect the main context from discovery overload. |
| 55 | B | Domain 4 | Independent review is better than self-review after generation. |
| 56 | B | Domain 3 | Keep universal guidance always loaded and workflow-specific guidance on demand. |
| 57 | B | Domain 2 | `allowed-tools` restricts the skill’s operational surface area. |
| 58 | A | Domain 1 | Deterministic sequencing requires programmatic enforcement, not prompt-only rules. |
| 59 | C | Domain 1 | Focused passes reduce attention dilution on large multi-file tasks. |
| 60 | C | Domain 4 | Optional or nullable fields reduce fabricated values when data is absent. |
| 61 | B | Domain 4 | `other` or `unclear` plus detail preserves extensibility honestly. |
| 62 | C | Domain 4 | Strict schema-based tool use primarily eliminates syntax and shape errors. |
| 63 | B | Domain 4 | Specific validation feedback is the right retry input when the issue is fixable. |
| 64 | C | Domain 4 | Retries cannot recover information that simply is not in the source. |
| 65 | A | Domain 4 | Message Batches are for asynchronous, non-urgent, lower-cost processing. |
| 66 | C | Domain 4 | `custom_id` supports correlation and selective resubmission. |
| 67 | B | Domain 2 | `any` guarantees a tool call while still letting Claude choose among tools. |
| 68 | A | Domain 2 | `strict: true` improves exact adherence to the tool schema. |
| 69 | B | Domain 2 | Clear purpose and boundaries are the first fix for overlapping tools. |
| 70 | B | Domain 2 | Retryability and error category are the key structured signals. |
| 71 | B | Domain 2 | Programmatic filtering by document type is the cleanest control point. |
| 72 | C | Domain 2 | Glob is for finding files by pattern such as `*.pdf`. |
| 73 | B | Domain 1 | A fixed, repeatable sequence is a prompt-chaining pipeline. |
| 74 | C | Domain 1 | Discovery-driven branching is dynamic adaptive decomposition. |
| 75 | B | Domain 5 | Low-confidence high-impact fields should route to more review, not less. |
| 76 | A | Domain 5 | Source links, quotes, and dates preserve provenance through synthesis. |
| 77 | B | Domain 1 | Coordinators should aggregate structured chunk outputs and preserve provenance. |

## Domain Distribution

- Domain 1: 21 questions
- Domain 2: 14 questions
- Domain 3: 15 questions
- Domain 4: 15 questions
- Domain 5: 12 questions