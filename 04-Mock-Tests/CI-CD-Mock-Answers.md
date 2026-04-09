# Claude Code for Continuous Integration – Answer Key

| Q | Answer | Domain | Topic |
|---|--------|--------|-------|
| 1 | C | D3 | Headless/non-interactive flag |
| 2 | B | D3 | Structured output flag |
| 3 | B | D3 | JSON schema enforcement |
| 4 | C | D4 | Incremental review context |
| 5 | C | D4 | Inline reasoning for triage speed (no-filtering constraint) |
| 6 | A | D3 | Permissions + audit hook |
| 7 | B | D3 | Project-level hook config |
| 8 | B | D3 | Secret management in CI |
| 9 | B | D1 | Stale file snapshot issue |
| 10 | B | D4 | Test generation context |
| 11 | B | D1 | Parallel execution |
| 12 | B | D1 | PreToolUse safety hook |
| 13 | C | D4 | Actionable prompt design |
| 14 | B | D3 | Exit code gating |
| 15 | C | D4 | Scope enforcement |
| 16 | B | D4 | Extended thinking for debugging |
| 17 | B | D4 | Context window management |
| 18 | B | D2 | MCP transport for airgapped CI |
| 19 | B | D5 | Minimal footprint + human gates |
| 20 | B | D4 | Internal library context |
| 21 | B | D1 | Idempotency in CI |
| 22 | B | D3 | Convention reuse via CLAUDE.md / skills |
| 23 | A | D4 | Few-shot for false positive reduction |
| 24 | B | D3 | Project slash commands |
| 25 | C | D1 | Adaptive CI architecture |

---

## Detailed Rationales

### Q1. Answer: C — `-p` (or `--print`)
`-p` / `--print` runs Claude Code in **non-interactive, headless mode**. Without it, Claude Code may pause and wait for user permission on tool calls or other prompts, causing the CI job to hang indefinitely. `--resume` loads a prior session; `--compact` summarizes context; neither prevents blocking prompts.

---

### Q2. Answer: B — `--output-format json`
`--output-format json` switches Claude Code's output to a machine-readable JSON envelope. Plain text output mixes prose with findings, making downstream parsing fragile. `--verbose` adds more human-readable debug output, making parsing harder, not easier.

---

### Q3. Answer: B — `--output-format json` combined with `--json-schema`
`--output-format json` alone does not guarantee a specific shape — the model still chooses its JSON structure. Adding `--json-schema` provides a schema file that constrains the output to the exact fields and types you declare. Option A (prose example) is unreliable; option C overstates what the flag alone does; option D (regex) is fragile and brittle.

---

### Q4. Answer: C — Prior review findings with incremental instruction
Passing prior findings plus an explicit instruction to report only new or still-open issues is the recommended pattern for incremental CI reviews. Starting fresh every time causes the same issues to be re-flagged. Passing only the diff without prior context loses the ability to distinguish new vs. known issues. Temperature has no effect on this.

---

### Q5. Answer: C — Inline reasoning and confidence per finding
**Critical trap:** The constraint "without filtering any findings" rules out option B (tiered categories that imply hiding lower-tier items from the review). Tiered categorization also does not reduce investigation time — it reorganizes workflow structure but developers still have to click into each finding to understand the model's reasoning before deciding. The correct fix is to include reasoning and confidence **inline**: each finding already contains why Claude flagged it and how confident it is, so developers can triage in seconds without opening each item. This is the exam's key distinction — reducing investigation time ≠ reducing the number of findings shown.

---

### Q6. Answer: A — `--dangerously-skip-permissions` + PostToolUse hook
In automated CI environments where human approval is impossible, `--dangerously-skip-permissions` removes interactive permission prompts. Pairing it with a **PostToolUse hook** that logs every tool call maintains an audit trail. This is the documented pattern for CI usage. Disabling all tools (option C) defeats the purpose of agentic review; `--resume` does not transfer permissions.

---

### Q7. Answer: B — Project-level `.claude/settings.json`
Hooks placed in the project-level `.claude/settings.json` (committed to the repo) apply automatically to every contributor and CI runner that uses that project — no personal config required. User-level `~/.claude/settings.json` only affects individual machines. Environment variables and YAML aliases are not the hook configuration mechanism.

---

### Q8. Answer: B — `.mcp.json` is committed to version control
`.mcp.json` is a project configuration file intended to be committed to the repository. Embedding API keys or secrets directly in it exposes them to anyone who can read the repo. The correct pattern is to store credentials in environment variables (e.g., GitHub Actions secrets) and reference them via `${ENV_VAR}` substitution in `.mcp.json`.

---

### Q9. Answer: B — Stale file snapshot
If the CI step provides Claude Code with a cached or stale copy of the files rather than the current HEAD, changes committed by the developer will be invisible to the model. The false positive persists not because of model limitations but because the input is wrong. Always ensure Claude Code operates on the checked-out HEAD in the CI workspace.

---

### Q10. Answer: B — Function diff + imports + existing test conventions
Useful test generation requires the model to understand: (1) what the function does (the diff), (2) its dependencies (imports), and (3) how tests are structured in this project (existing test conventions). PR title and branch name are insufficient. The full repository history is overkill and wastes context budget.

---

### Q11. Answer: B — Batch API or parallel invocations
Sequential processing across 8 files is the bottleneck. The solution is to parallelize — either via the **Batch API** (for asynchronous, cost-efficient processing) or by launching multiple Claude Code subprocess calls concurrently and aggregating results. `--compact` and `max_tokens` adjustments do not address the sequential structure.

---

### Q12. Answer: B — PreToolUse hook scanning for secrets
A **PreToolUse hook** on `Write` or `Bash` can scan the content *before* it is written to disk or executed. If it detects secret patterns (e.g., connection strings, API URLs), it can block the operation and surface a warning. A stronger system prompt is advisory; it does not intercept the write. Post-commit scanning is too late.

---

### Q13. Answer: C — Specific, structured review instruction
The ideal CI review prompt specifies: what to look for, the output format (file, line, description, severity, fix), and what to explicitly ignore. Option C does all of this. Options A and B are vague and produce unstructured prose. Option D ("be thorough") encourages over-flagging and noise, which is the opposite of minimizing false positives.

---

### Q14. Answer: B — Parse JSON output and set exit code in post-processing
Claude Code does not have a built-in `--fail-on-findings` flag (option A is a trap — this does not exist). The correct pattern is: parse the structured JSON output in a shell or Python script, check for any entry with `severity: blocking`, and call `exit 1` to fail the CI job. This is the standard pattern for integrating AI findings into CI gates.

---

### Q15. Answer: C — Explicit scope in the system prompt
The most reliable mechanism to constrain review scope is to **explicitly state in the system prompt** what Claude should and should not comment on. Trusting the model's judgment (option A) is unpredictable. Reformatting code first (option B) does not prevent style comments on logic. Limiting tools (option D) affects *what data Claude can access*, not *what it comments on*.

---

### Q16. Answer: B — Extended thinking with thinking blocks in output
When extended thinking is enabled via the API and thinking blocks are included in the output, the model's chain-of-thought is preserved and can be logged for debugging. `--verbose` prints execution metadata, not model reasoning. `--resume` stores session context but not reasoning traces. Temperature does not produce reasoning explanations.

---

### Q17. Answer: B — Diff of changed files + targeted context
The correct context strategy is **targeted**: pass only the diff of changed files plus relevant imports and test files discovered by a preceding search step. Passing all 300 files (option A) wastes the context window and may exceed limits. PR title only (option C) is too sparse. Full git log (option D) is irrelevant noise.

---

### Q18. Answer: B — stdio
In a network-isolated (airgapped) environment, **stdio** is the correct MCP transport because it runs the MCP server as a local subprocess — no outbound network connections are required. Streamable HTTP, WebSocket, and gRPC all require network connectivity to reach a remote server.

---

### Q19. Answer: B — Minimal footprint + human review gates
Claude Code agents operating in CI should follow the **minimal footprint** principle: prefer read-only operations, avoid irreversible actions without review, and do not push changes to protected branches autonomously. A CI job that directly commits to `main` without a review gate violates this principle regardless of the flags used.

---

### Q20. Answer: B — Add library description to system prompt / CLAUDE.md
The model cannot know about a non-public internal library from training data. The fix is to provide a brief description of the library's interface — its exports, types, and purpose — in the system prompt or in a project CLAUDE.md file that Claude Code reads automatically. Disabling the review or removing library use are not acceptable engineering solutions.

---

### Q21. Answer: B — Duplicate CI triggers + idempotency fix
Duplicate comments are typically caused by the CI workflow triggering on both `push` and `pull_request` events for the same commit. The fix is **idempotency**: before posting a review comment, check if one already exists (e.g., via the GitHub API) and skip posting if it does. Temperature and MCP restarts do not affect trigger logic.

---

### Q22. Answer: B — CLAUDE.md or skills for convention reuse
The maintainable pattern is to capture project test conventions in a **CLAUDE.md section** or a dedicated **skill** that the CI step invokes. This ensures conventions are version-controlled and kept in sync — when the project adopts a new test pattern, updating CLAUDE.md propagates to all CI runs automatically. Pasting examples into every prompt (option D) creates maintenance debt.

---

### Q23. Answer: A — Few-shot example with safe vs. vulnerable patterns
The most effective way to teach the model to distinguish parameterized queries from vulnerable string concatenation is a **few-shot example** showing both patterns side by side with explicit labels. This gives the model a concrete reference to anchor its judgment. Higher `max_tokens`, removing tools, and running twice do not address the model's classification criterion.

---

### Q24. Answer: B — Project slash command in `.claude/commands/`
Project slash commands stored in `.claude/commands/` are version-controlled, shared across the team, and callable from CI via `claude -p "/review"`. This centralizes the prompt in one place. Environment variables (option A) are not the Claude Code mechanism for this; `--resume` does not cache prompts; `.mcp.json` stores server config, not prompts.

---

### Q25. Answer: C — Pre-detect changed files and branch on sensitivity
The optimal architecture detects which files changed *before* invoking Claude Code, then selects the appropriate review mode: lightweight for small/non-sensitive PRs, extended-thinking for security-sensitive paths. This is the standard adaptive CI pattern. Always using extended thinking (option A) wastes cost and time on trivial PRs. Two parallel reviews (option D) doubles cost with no quality benefit for small PRs.

---

---

### Q26. Answer: D — Explicit severity criteria with concrete code examples
Requesting reasoning (option A) shifts the calibration burden to human reviewers — it adds transparency but does not fix the automated inconsistency. The root cause is that the prompt gives the model no reference point for what makes something `critical` vs. `minor`. Concrete code examples per severity level act as anchors: the model can compare the current finding against the examples and produce consistent labels. This is a classification consistency technique, not just a formatting improvement.

---

### Q27. Answer: D — Explicit criteria: flag only when behavior contradicts code
Option A (pre-filtering) addresses only false positives on benign patterns while completely ignoring false negatives on stale behavior descriptions. Option B (splitting prompts) adds pipeline complexity without fixing the definition of "misleading." The root cause is the vague instruction "flag any misleading comment." Replacing it with a precise, falsifiable criterion — "flag only when the comment's claimed behavior contradicts what the code actually does" — eliminates both problem types by defining exactly what constitutes a real issue.

---

### Q28. Answer: B — Batch API async model prevents mid-request tool execution
**The Batch API fully supports tool definitions** (option A is false and a common trap). The fundamental constraint is architectural: the Batch API is fire-and-forget — you submit a request, it processes asynchronously, and you poll for results. There is no mechanism to intercept the request mid-flight, execute a tool, inject the result, and resume generation. Iterative tool-calling workflows (analyze → call tool → use result → continue analysis) require synchronous, turn-by-turn API calls.

---

### Q29. Answer: D — Sync for PR checks; Batch for nightly + weekly
**PR style checks block the merge button** — developers are waiting. These must be synchronous. **Nightly test generation** runs on a schedule with no one waiting for results — it easily tolerates the up-to-24-hour batch window and saves 50% on cost. **Weekly security audits** are also scheduled, non-urgent tasks that fit the Batch API perfectly. Option A (nightly = sync) misses the cost savings available on nightly generation. The rule: if a developer or CI gate is waiting → synchronous; if it runs on a schedule with flexible timing → Batch API.

---

### Q30. Answer: A — 3–4 few-shot examples showing exact output format
When prompt instructions alone produce variable output format, **few-shot examples are the most reliable fix**. They give the model a concrete pattern to imitate rather than an abstract rule to interpret. Option B (two-pass) adds architectural complexity and cost but does not solve why the single prompt produces inconsistent format — the second prompt inherits the same ambiguity. Option D ("same format as previous") fails in new sessions and has no reference when there is no prior response.

---

### Q31. Answer: C — Define each severity level with an example vulnerability
This is the same pattern as Q26, applied to security findings. Temperature 0 (option A) makes outputs deterministic for a given input but does not make the *classification criterion* consistent across different inputs describing similar vulnerabilities — the model still has no shared definition of what makes one SQL injection `critical` vs. `high`. Option B (post-processing normalization) overwrites all nuance and is wrong for vulnerabilities that genuinely differ in severity. Concrete examples per severity level give the model anchors to compare against.

---

## Answer Key (Updated)

| Q | Answer | Domain | Topic |
|---|--------|--------|-------|
| 1 | C | D3 | Headless/non-interactive flag |
| 2 | B | D3 | Structured output flag |
| 3 | B | D3 | JSON schema enforcement |
| 4 | C | D4 | Incremental review context |
| 5 | C | D4 | Inline reasoning for triage (no-filter constraint) |
| 6 | A | D3 | Permissions + audit hook |
| 7 | B | D3 | Project-level hook config |
| 8 | B | D3 | Secret management in CI |
| 9 | B | D1 | Stale file snapshot issue |
| 10 | B | D4 | Test generation context |
| 11 | B | D1 | Parallel execution |
| 12 | B | D1 | PreToolUse safety hook |
| 13 | C | D4 | Actionable prompt design |
| 14 | B | D3 | Exit code gating |
| 15 | C | D4 | Scope enforcement |
| 16 | B | D4 | Extended thinking for debugging |
| 17 | B | D4 | Context window management |
| 18 | B | D2 | MCP transport for airgapped CI |
| 19 | B | D5 | Minimal footprint + human gates |
| 20 | B | D4 | Internal library context |
| 21 | B | D1 | Idempotency in CI |
| 22 | B | D3 | Convention reuse via CLAUDE.md / skills |
| 23 | A | D4 | Few-shot for false positive reduction |
| 24 | B | D3 | Project slash commands |
| 25 | C | D1 | Adaptive CI architecture |
| 26 | D | D4 | Classification consistency — concrete severity examples |
| 27 | D | D4 | Prompt specificity — explicit flag criteria |
| 28 | B | D1 | Batch API async limitation with iterative tool calls |
| 29 | D | D1 | Sync vs. Batch API decision for CI task types |
| 30 | A | D4 | Few-shot for output format consistency |
| 31 | C | D4 | Classification consistency — per-severity anchors |

## Domain Distribution (31 questions)
- Domain 1 (Agentic Architecture & Loops): 8 — Q9, Q11, Q12, Q19, Q21, Q25, Q28, Q29
- Domain 2 (Tool & MCP Design): 1 — Q18
- Domain 3 (Claude Code Configuration): 8 — Q1, Q2, Q3, Q6, Q7, Q8, Q22, Q24
- Domain 4 (Prompting & Output): 13 — Q4, Q5, Q10, Q13, Q15, Q16, Q17, Q20, Q23, Q26, Q27, Q30, Q31
- Domain 5 (Trust, Safety & Escalation): 1 — Q19

## Key Distinctions This Test Drills

| Trap pair | When to choose which |
|---|---|
| Tiered categorization vs. inline reasoning | Categorization = reduces what appears in CI gate. Inline reasoning = reduces per-finding investigation time when all findings must stay visible. |
| Few-shot examples vs. two-pass prompts | Few-shot = best first fix for format inconsistency. Two-pass = adds pipeline complexity without fixing the classification criterion. |
| Sync API vs. Batch API | Sync = anything blocking a human (PR gate, interactive). Batch = scheduled, non-urgent, cost-sensitive (nightly, weekly). |
| Batch API limitations | Batch supports tool definitions but cannot do iterative mid-request tool calls. |
| Explicit criteria vs. pre-filtering | Pre-filtering only fixes false positives. Explicit criteria fixes both false positives AND false negatives. |
