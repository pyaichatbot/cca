# Strict Mock Test 2 - Answer Key

| Q | Answer | Domain | Rationale |
|---|--------|--------|-----------|
| 1 | B | Domain 2 | Read is for loading full file contents once a file is identified. |
| 2 | A | Domain 2 | Write is the built-in tool for creating new files from scratch. |
| 3 | C | Domain 2 | Edit is for precise snippet replacement when the match is unique. |
| 4 | B | Domain 2 | The documented fallback is Read + modify + Write when Edit is ambiguous. |
| 5 | A | Domain 2 | Bash is the correct tool for shell commands like git or test runs. |
| 6 | B | Domain 2 | The guide recommends progressive exploration: Grep, Read, Grep usages, Read consumers. |
| 7 | B | Domain 2 | Reading too much too early violates the incremental investigation strategy. |
| 8 | B | Domain 2 | Glob is for discovering files by name or pattern. |
| 9 | A | Domain 3 | `@path` lets CLAUDE.md import external files for modular organization. |
| 10 | B | Domain 3 | `@path` is specifically for modularizing instruction content. |
| 11 | B | Domain 3 | `.claude/rules/` is the supported topical modular organization pattern. |
| 12 | A | Domain 3 | Path-scoped rules are best for cross-cutting conventions spread across many folders. |
| 13 | A | Domain 3 | Directory CLAUDE.md is best when conventions are truly local to one subtree. |
| 14 | B | Domain 3 | `context: fork` isolates exploration context from the main thread. |
| 15 | B | Domain 3 | `/memory` is the built-in command associated with persisted Claude Code memory. |
| 16 | B | Domain 5 | `/compact` can lose exact details during summarization. |
| 17 | B | Domain 1 | A fresh session with a summary is often better when resumed tool data is stale. |
| 18 | B | Domain 1 | `fork_session` creates independent branches from shared context. |
| 19 | B | Domain 1 | Resumed sessions can carry stale tool outputs after code changes. |
| 20 | A | Domain 2 | MCP defines tools, resources, and prompts. |
| 21 | B | Domain 2 | Resources provide context without requiring exploratory actions. |
| 22 | B | Domain 2 | MCP prompts are predefined templates for common tasks. |
| 23 | B | Domain 4 | Batches do not support iterative multi-turn tool calling inside a single interaction. |
| 24 | B | Domain 4 | Blocking checks stay synchronous; non-urgent nightly work can use batches. |
| 25 | B | Domain 4 | The 24-hour window matters for deadline planning because there is no latency SLA. |
| 26 | B | Domain 4 | Tool-loop workflows are fundamentally incompatible with one-shot batch execution. |
| 27 | B | Domain 4 | Asking clarifying questions before implementation is the interview pattern. |
| 28 | B | Domain 4 | The interview pattern fits ambiguous tasks with hidden constraints and multiple viable paths. |
| 29 | B | Domain 4 | Extracting both stated and calculated values enables contradiction checks. |
| 30 | B | Domain 4 | Self-correction creates structured discrepancy detection, not guaranteed correctness. |
| 31 | A | Domain 5 | Structured state persistence supports crash recovery and intelligent resume. |
| 32 | A | Domain 5 | Persisted state prevents redundant rediscovery and supports coordinated recovery. |

## Notes

- This supplement targets guide sections that Strict Mock Test 1 undercovered.
- It is meant to close concept gaps, not mirror the weighted 77-question exam blueprint again.