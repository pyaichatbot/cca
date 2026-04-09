# Claude Certified Architect - Foundations: Strict Mock Test 2

> 32 original questions | Gap-focused supplement | Covers underrepresented sections from the guide rather than re-testing already strong coverage

## Focus Areas
- Session management: `--resume`, `fork_session`, stale context, fresh-session summaries
- MCP resources and prompts, not just tools
- `@path` imports and modular instruction design
- `.claude/rules/` as topical organization plus `paths` behavior
- Claude Code built-in tools beyond Grep/Glob: Read, Write, Edit, Bash, and fallback patterns
- Incremental investigation strategy
- `/compact` and `/memory`
- Message Batches API limitations and SLA planning
- Interview pattern, self-correction, and semantic validation patterns
- Structured state persistence and crash recovery

## Instructions
- Select the BEST answer for each question
- This is a coverage supplement, not a second weighted full-length simulation

---

## Scenario 1: Developer Productivity Tools

**Q1.** You need to inspect the full contents of a configuration file after Grep identifies it as relevant. Which built-in tool is the right next step?

A) Glob
B) Read
C) Edit
D) Bash

---

**Q2.** You need to create a brand-new file from scratch in Claude Code. Which built-in tool is designed for that?

A) Write
B) Edit
C) Grep
D) Read

---

**Q3.** You want to replace one specific snippet in an existing file when the target text is unique. Which tool is designed for that precise operation?

A) Read
B) Write
C) Edit
D) Glob

---

**Q4.** Edit fails because the target text appears in multiple places and the match is not unique. What is the recommended fallback pattern?

A) Retry Edit until it guesses correctly
B) Read the file, modify the full content, then Write the updated file
C) Switch to Glob because file patterns are more reliable than text matches
D) Ask Claude to describe the desired patch in prose only

---

**Q5.** You need to run `git`, `npm test`, and a build command from Claude Code. Which built-in tool is appropriate?

A) Bash
B) Grep
C) Read
D) Edit

---

**Q6.** Which investigation flow best matches the guide’s recommended incremental exploration strategy?

A) Read every file in the repository before forming any hypothesis
B) Grep for entry points, Read the relevant files, Grep for usages, then Read the consumers
C) Start with Write to create a temporary summary file, then inspect whatever seems interesting
D) Use Bash to dump the entire repository into one text file and scan it manually

---

**Q7.** A team keeps using Read on dozens of files before narrowing the question, causing context bloat. What principle are they violating?

A) Deterministic enforcement
B) Incremental investigation
C) Session isolation
D) Structured output

---

**Q8.** When should Glob be preferred over Grep?

A) When searching for a symbol inside file contents
B) When finding files by name or extension pattern
C) When editing a unique snippet in place
D) When executing shell commands

---

## Scenario 2: Claude Code Workflows and Configuration Gaps

**Q9.** Your root CLAUDE.md is becoming unwieldy. You want to split guidance into maintained files while keeping a single project-level entry point. What feature supports that directly?

A) `@path` imports in CLAUDE.md
B) `.mcp.json` environment substitution
C) `tool_choice: any`
D) `/compact`

---

**Q10.** Which statement about `@path` usage in CLAUDE.md is correct?

A) It only supports absolute paths
B) It imports external files to modularize instruction content
C) It only works inside skills, not CLAUDE.md
D) It replaces `.claude/rules/` entirely

---

**Q11.** Your team wants a maintainable structure for project-wide topics like testing, API conventions, and deployment. What is the best supported organizational pattern?

A) Put everything into one 1,000-line CLAUDE.md forever
B) Use separate topical files under `.claude/rules/`
C) Create one README per topic and assume Claude auto-loads them as rules
D) Store the guidance only in personal user-level memory

---

**Q12.** When should `.claude/rules/` with `paths` be preferred over directory-level CLAUDE.md?

A) When conventions apply across many directories by file type or pattern
B) Only when the repo has no subdirectories
C) Only when working with MCP servers
D) Never; directory CLAUDE.md is always better

---

**Q13.** When should directory-level CLAUDE.md usually be preferred over path-scoped rules?

A) When conventions are tied to a specific subtree and not broadly cross-cutting
B) When you need to apply a testing convention to files scattered across the repo
C) When you want slash commands to become available to the team
D) When you need structured JSON output in CI

---

**Q14.** A long brainstorm skill is polluting implementation work, but you still want the result summary. Which configuration is correct?

A) Put the skill under `.mcp.json`
B) Use `context: fork` so exploration happens in an isolated context
C) Add `temperature: 0`
D) Store the skill only in `~/.claude/commands/`

---

**Q15.** A developer wants project conventions to persist across sessions without repeating them manually each time. Which built-in Claude Code command is explicitly associated with managing that persisted memory/instruction surface?

A) `/compact`
B) `/memory`
C) `/resume`
D) `/rules`

---

**Q16.** What is the main tradeoff of using `/compact` in very long sessions?

A) It disables tools after compaction
B) It can compress away precise details like dates, percentages, and exact values
C) It forces the model into headless mode
D) It writes to user memory automatically

---

**Q17.** A resumed session contains stale assumptions because files changed significantly since the last run. According to the guide, what is often the better option?

A) Always keep resuming until the model notices the drift
B) Start a fresh session with a structured summary of prior findings
C) Delete all CLAUDE.md files and rely on memory instead
D) Force the model to ignore the new file state

---

**Q18.** What is `fork_session` best for?

A) Replacing all slash commands in a project
B) Creating independent branches of investigation from shared context
C) Guaranteeing structured JSON output in CI
D) Storing long-term memory between workspaces

---

**Q19.** What is the key risk when using `--resume` carelessly in a changed codebase?

A) Tool definitions are deleted from the session
B) Previously gathered tool results may be stale relative to current files
C) The model loses access to system prompts entirely
D) Resume forces batch processing mode

---

## Scenario 3: MCP and Batch Gaps

**Q20.** MCP defines more than tools. Which set correctly names the three primary MCP resource types discussed in the guide?

A) Tools, resources, prompts
B) Tools, sessions, batches
C) Commands, hooks, prompts
D) Files, tools, schemas

---

**Q21.** Why are MCP resources useful in agent workflows?

A) They let the model take actions directly without tools
B) They provide readable context like docs, schemas, or catalogs without exploratory action calls
C) They replace CLAUDE.md hierarchy entirely
D) They are only for authentication metadata

---

**Q22.** What are MCP prompts intended for?

A) Persistent long-term memory between sessions
B) Predefined prompt templates for common tasks
C) Replacing JSON schemas in tool definitions
D) Forcing tool visibility rules by tier

---

**Q23.** Which statement about Message Batches API is a critical limitation for iterative tool-calling workflows?

A) It cannot process more than one request total
B) It does not support multi-turn tool calling within a single logical request
C) It cannot return JSONL results
D) It costs more than synchronous calls

---

**Q24.** A blocking pre-merge check must finish quickly, while a nightly report can wait until morning. How should they map to API choices?

A) Both should use Message Batches for cost savings
B) The blocking check should stay synchronous; the nightly report can use batches
C) Both should stay synchronous because batch ordering is not guaranteed
D) The nightly report should be synchronous and the pre-merge check batched

---

**Q25.** What does the guide emphasize about the Message Batches API processing window?

A) It provides a strict low-latency SLA for all batch jobs
B) It can take up to 24 hours and should be planned against deadlines accordingly
C) It always finishes in less than five minutes
D) It only matters when using Opus models

---

**Q26.** A team wants to use batch processing for a workflow that depends on Claude requesting a tool, receiving the tool result, and then continuing analysis in the same logical interaction. What is the correct conclusion?

A) Batch processing is ideal because it supports tool loops more cheaply
B) Batch processing is incompatible with that workflow shape
C) Batch processing works if you add `strict: true`
D) Batch processing works only if you remove `custom_id`

---

## Scenario 4: Prompt Engineering and Reliability Gaps

**Q27.** Before implementing a caching subsystem, Claude asks clarifying questions about invalidation, stale data tolerance, and scope. Which prompt pattern is this?

A) Lost-in-the-middle mitigation
B) Interview pattern
C) Coverage annotation
D) Forked skill execution

---

**Q28.** When is the interview pattern most valuable?

A) When the task is trivial and implementation is obvious
B) When the domain is unfamiliar or multiple viable approaches depend on hidden constraints
C) Only when the user asks for a human
D) Only in CI/CD pipelines

---

**Q29.** You want the model to detect internal contradictions in invoice extraction. Which self-correction design best matches the guide?

A) Extract only the stated total and trust it
B) Extract both `stated_total` and `calculated_total` and compare them
C) Remove totals from the schema to avoid mismatch
D) Use only few-shot examples without validation

---

**Q30.** Why is this self-correction pattern useful?

A) It eliminates all semantic errors automatically
B) It creates a structured way to detect contradictions the workflow can act on
C) It replaces schema validation entirely
D) It avoids the need for source documents

---

**Q31.** A long-running multi-agent workflow crashes halfway through. What guide concept most directly supports reliable recovery?

A) Structured state persistence to known files or manifests
B) Temperature tuning for resilience
C) Re-running the entire workflow from the beginning every time
D) Deleting all prior summaries before restart

---

**Q32.** What is the best reason to persist agent state such as completed steps, key findings, coverage, and remaining gaps?

A) To let the coordinator resume intelligently instead of rediscovering everything from scratch
B) To guarantee the same answer regardless of new evidence
C) To avoid using subagents in future runs
D) To eliminate the need for provenance tracking