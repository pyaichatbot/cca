# Claude Code for Continuous Integration – Focused Mock Test

> **Scenario:** You are integrating Claude Code into your CI/CD pipeline. The system runs automated code reviews, generates test cases, and provides feedback on pull requests. You need to design prompts that provide actionable feedback and minimize false positives.
>
> **Coverage:** 31 questions across all 5 domains, weighted toward the practical CI/CD integration topics tested in the exam.
>
> **v2 update:** 6 questions added / revised based on real exam failures: classification consistency, prompt specificity, Batch API limitations, sync vs. batch decision, inline reasoning for triage, and few-shot for output format.

## Instructions
- Select the BEST answer for each question
- One correct answer per question
- No guessing penalty

---

**Q1.** Your CI job launches Claude Code and it hangs indefinitely because it is waiting for permission prompts. Which flag prevents this?

A) `--resume`
B) `--compact`
C) `-p` (or `--print`)
D) `--strict-mode`

---

**Q2.** A CI step calls Claude Code with `-p` and pipes the output into a downstream parsing script. The output includes the model's reasoning text mixed with the findings. What flag produces structured output the parser can reliably consume?

A) `--verbose`
B) `--output-format json`
C) `--silent`
D) `--context-limit low`

---

**Q3.** You want the automated PR review to return findings in a JSON array where each entry has `file`, `line`, `severity`, and `suggestion`. What is the most reliable way to enforce that exact shape?

A) Add an example JSON block in a prose prompt and hope Claude follows it
B) Use `--output-format json` combined with `--json-schema` pointing to your schema file
C) Use `--output-format json` alone, which guarantees the shape
D) Filter the model's free-text output with a regex in your shell script

---

**Q4.** After the automated review runs on a PR, a developer pushes two follow-up commits. On the next CI run, you want Claude Code to report only new issues — not re-flag already-acknowledged ones. What should you include in the next run's context?

A) Nothing; always start fresh so no prior findings bias the model
B) Only the new commit diff, with no mention of prior runs
C) The prior review findings with an instruction to report only new or still-open issues
D) A lower temperature setting to suppress repeated comments

---

**Q5.** Your automated PR review averages 15 findings per pull request. Developers spend significant time investigating each finding before deciding whether to address or dismiss it. You need to reduce that investigation time **without filtering any findings from the output**. What change best achieves this?

A) Increase `max_tokens` so the model can explain each finding in more detail
B) Categorize findings as "blocking issues" versus "suggestions" with tiered review requirements
C) Require Claude to include its reasoning and confidence assessment inline with each finding
D) Run the review twice and only surface findings that appear in both outputs

---

**Q6.** Your CI pipeline needs Claude Code to analyze files it has not seen before without asking for permissions on each tool call. Which approach lets CI proceed without interactive prompts while keeping a record of what tools were used?

A) Pass `--dangerously-skip-permissions` and log all tool calls via a PostToolUse hook
B) Rename tools so they sound less dangerous
C) Disable all tools and pass file contents manually in the prompt
D) Use `--resume` to inherit permissions from a previous session

---

**Q7.** A PostToolUse hook runs after every `Bash` call in the CI pipeline. What is the correct place to configure this hook so it applies to all team members running CI without requiring personal config?

A) In each developer's `~/.claude/settings.json`
B) In the project-level `.claude/settings.json` committed to the repository
C) In an environment variable `CLAUDE_HOOKS`
D) Inline in the CI YAML as a shell alias

---

**Q8.** Your GitHub Actions workflow passes the `ANTHROPIC_API_KEY` to Claude Code. A junior engineer proposes storing the key directly in the project's `.mcp.json` for convenience. Why is this wrong?

A) `.mcp.json` only supports stdio transport, not API keys
B) `.mcp.json` is committed to version control, exposing the secret to anyone who clones the repo
C) Claude Code ignores `.mcp.json` in CI environments
D) MCP servers cannot access environment variables in GitHub Actions

---

**Q9.** Claude Code's automated review flags a function for "missing error handling" on every run, even after a developer adds a try/catch. The false positive persists because Claude cannot read the updated file. What is the most likely root cause?

A) The model temperature is too high
B) The CI step is running Claude Code against a stale file snapshot, not the current HEAD
C) The `--json-schema` flag is too strict
D) The system prompt is missing a few-shot example

---

**Q10.** You are designing a prompt for automated test generation. The CI job should generate unit tests for any new function added in a PR diff. What context must be included in the prompt to produce useful, runnable tests?

A) The PR title and the name of the branch only
B) The function diff, the file's imports, and the existing test file conventions in the project
C) The full repository history and all open issues
D) The number of lines changed and the contributor's username

---

**Q11.** The automated test-generation step takes 4 minutes per PR because it runs sequentially across 8 changed files. What change best reduces wall-clock time?

A) Use `--compact` to reduce context between files
B) Use the Batch API or parallel Claude Code invocations — one per changed file — and aggregate results
C) Use a lower-capability model with fewer tokens
D) Increase `max_tokens` so each run covers more files

---

**Q12.** A CI step generates test cases and immediately creates a commit. The generated tests contain a hardcoded production database URL. What safety mechanism would have caught this before commit?

A) A stronger system prompt asking Claude to avoid hardcoding secrets
B) A PreToolUse hook on the `Bash` or `Write` tool that scans for secret patterns before writing files
C) Running the generated tests in a sandboxed environment after commit
D) A PostToolUse hook that retries the generation if any output is over 500 lines

---

**Q13.** Your CI review prompt currently reads: *"Review this code and tell me if there are any problems."* Developers complain the output is vague. What rewrite best produces actionable PR feedback?

A) "Review this code."
B) "Look at this PR and identify any bugs."
C) "Review the following diff. For each issue found, state: the file and line number, a one-sentence description of the problem, the severity (blocking / warning / suggestion), and a concrete fix or alternative. Do not flag issues that have no impact on correctness, security, or performance."
D) "Provide feedback on this code. Be thorough and cover all possible issues."

---

**Q14.** The CI job exits with code 0 even when Claude Code finds critical security issues. The downstream gate never blocks the PR. What should you change?

A) Add a `--fail-on-findings` flag (which does not exist — this is a trap)
B) Parse the structured JSON output in a post-processing step and set exit code 1 when any `blocking` finding exists
C) Increase the model's `max_tokens` so it explains issues more thoroughly
D) Use `--resume` to persist findings to the next run

---

**Q15.** You want the automated review to focus exclusively on security and never comment on style, formatting, or naming. What is the most reliable way to enforce this scope?

A) Trust the model's judgment to filter irrelevant findings naturally
B) Use a separate formatter tool before Claude Code runs so there are no style issues left
C) Explicitly specify the review scope in the system prompt: list what Claude should check and what it should ignore
D) Give Claude Code access only to security-related tools

---

**Q16.** A developer wants to see why Claude Code flagged a specific line. The CI job only stored the final JSON output, not the model's reasoning. What configuration would have preserved the chain-of-thought for debugging?

A) `--verbose` flag, which prints the model's internal reasoning to stderr
B) Extended thinking enabled in the API call, with the thinking blocks included in the output
C) A higher temperature so the model explains itself more
D) `--resume` mode, which stores reasoning in the session history

---

**Q17.** You are running automated PR review across a monorepo with 300 files. The PR touches 12 files. What context strategy avoids filling the context window while still giving Claude enough information?

A) Pass all 300 files in the prompt to ensure no context is missing
B) Pass only the diff of changed files plus relevant imports and test files identified by a preceding Grep/Glob step
C) Pass only the PR title and commit message
D) Pass the full git log for the past 30 days

---

**Q18.** Claude Code is integrated into a CI pipeline on a self-hosted runner that has no outbound internet access. The team wants to use an MCP server for code linting. What transport must the MCP server use in this environment?

A) Streamable HTTP, because it scales best
B) stdio, because it runs as a local subprocess with no network dependency
C) WebSocket, because it supports bidirectional streaming
D) gRPC, because it is the default MCP production transport

---

**Q19.** A CI job runs Claude Code with `-p` and the prompt instructs it to "fix all bugs." The job makes unreviewed changes directly to the main branch. What principle of CI integration is being violated?

A) Claude Code should never run in `-p` mode
B) Automated agents in CI should operate with minimal footprint and human review gates for code changes to protected branches
C) The prompt is missing a temperature setting
D) The `--output-format json` flag should always be used with bug-fixing prompts

---

**Q20.** The automated review consistently flags valid use of a project-specific internal library as "undefined reference." The library is not in the standard index. What is the best fix?

A) Tell developers to remove uses of the internal library to eliminate the noise
B) Add a brief description of the internal library's interface to the system prompt or CLAUDE.md context
C) Disable the review step for files that import the internal library
D) Switch to a larger model that may have seen the library in training data

---

**Q21.** Your CI pipeline generates a code review comment for every PR. The comment is posted via a GitHub MCP tool. After running in production for a week, you notice duplicate comments on some PRs. What is the likely cause and fix?

A) The model temperature is too low; increase it to reduce repetition
B) The CI job runs twice on some triggers (e.g., `push` + `pull_request` events); add idempotency logic to check if a review comment already exists before posting
C) The MCP server is misconfigured; restart it before each run
D) Use `--resume` to prevent the same context from being processed twice

---

**Q22.** You want the test-generation step to follow the project's existing test style — for example, using `pytest` fixtures, specific naming conventions, and a particular mock library. What is the most maintainable way to enforce this?

A) Describe the style verbatim in every CI prompt
B) Capture conventions in a CLAUDE.md section or a dedicated skill that the CI step invokes, so conventions stay in sync with any updates
C) Rely on the model's training knowledge of pytest conventions
D) Paste five example test files directly into the prompt on every run

---

**Q23.** A security scan step uses Claude Code to look for SQL injection patterns. It flags a parameterized query as vulnerable. This is a false positive. What context addition most directly helps the model distinguish parameterized queries from vulnerable string concatenation?

A) A few-shot example showing a vulnerable pattern and a safe parameterized pattern side by side, with explicit labeling
B) A higher `max_tokens` budget
C) Removing the SQL-related tools from the toolset
D) Running the scan twice and only reporting findings that appear both times

---

**Q24.** The CI review prompt is 8,000 tokens long due to repeated boilerplate. Developers keep duplicating the prompt across multiple workflow files. What Claude Code feature best centralizes and reuses this prompt?

A) Store the prompt in an environment variable and export it to all jobs
B) Create a project slash command in `.claude/commands/` that contains the review prompt, and call it from CI with `claude -p "/review"`
C) Use `--resume` to cache the prompt across runs
D) Store the prompt in `.mcp.json` as a resource

---

**Q25.** You want the CI review to be fast (under 30 seconds) for small PRs but thorough (extended thinking enabled) for PRs touching security-sensitive files. What is the best architecture?

A) Always use extended thinking; accept slower performance for small PRs
B) Use a single fixed prompt with temperature 0 for all PRs
C) Detect which files changed in the PR before invoking Claude Code; use a lightweight prompt for small PRs and an extended-thinking-enabled call for security-sensitive paths
D) Run two parallel reviews for every PR and pick the faster result

---

**Q26.** Your automated review shows inconsistent severity ratings — similar issues are sometimes flagged as `critical` and other times as `minor` across different PRs. The prompt currently says: *"Assign a severity to each finding."* What change most directly fixes the inconsistency?

A) Request that Claude include its reasoning for each severity assignment, then manually calibrate the ratings during human review
B) Run the review three times and pick the most common severity rating for each finding
C) Switch to a higher-capability model that is better calibrated on severity
D) Include explicit severity criteria in your prompt with concrete code examples for each severity level

---

**Q27.** Your automated review analyzes comments and docstrings for accuracy. The current prompt instructs Claude to *"flag any misleading or incorrect comments."* The review produces too many false positives (TODO notes, descriptive comments) and misses comments that describe behavior the code no longer implements. What change fixes both problems?

A) Pre-filter the file to remove TODO, FIXME, and descriptive comment patterns before sending to Claude
B) Split the task: one prompt for TODO/FIXME, a separate prompt for misleading comments
C) Use a lower temperature so the model is more conservative about flagging
D) Specify explicit criteria: flag comments only when their claimed behavior contradicts the actual code behavior

---

**Q28.** Your code review component works iteratively: Claude analyzes a changed file, calls a `run_tests` tool to check if the file compiles, then uses the result to complete its analysis. A teammate proposes migrating this step to the Message Batches API to reduce costs. Why would this migration break the workflow?

A) The Batch API does not support tool definitions in request parameters
B) The Batch API's asynchronous model prevents executing tools mid-request and returning results for Claude to continue analysis
C) The Batch API requires a minimum of 100 requests to be cost-effective
D) Tool calls in batch mode are limited to read-only operations

---

**Q29.** Your CI/CD system performs three types of Claude-powered analysis: (1) quick style checks on every PR that block the merge button, (2) nightly test generation for new code committed that day, and (3) weekly security audits across the full codebase. How should you allocate synchronous calls versus Message Batches API?

A) Use synchronous calls for PR style checks and nightly test generation; use Message Batches only for weekly security audits
B) Use synchronous calls for all three — consistency is more important than cost savings
C) Use Message Batches for all three — the cost savings always outweigh latency concerns
D) Use synchronous calls for PR style checks; use Message Batches for both nightly test generation and weekly security audits

---

**Q30.** Your automated reviews identify valid issues, but developers report the feedback style is inconsistent — sometimes Claude gives vague observations like "this could be improved," other times it gives a specific diff. Instructions alone have not fixed it. What technique most reliably achieves a consistent output format?

A) Add 3–4 few-shot examples showing the exact format: issue identified, code location, specific fix suggestion
B) Use a two-pass approach where one prompt identifies issues and a second prompt generates fixes
C) Increase temperature so the model explores more phrasing styles until one converges
D) Add a final instruction: "Always respond in exactly the same format as the previous response"

---

**Q31.** You need Claude to assign severity labels (`critical`, `high`, `medium`, `low`) to security findings in an automated scan. You notice the same class of SQL injection vulnerability is sometimes labeled `critical` and sometimes `high` across different PRs. What is the correct fix?

A) Tune the temperature down to 0 so the model is deterministic
B) Add a post-processing script that normalizes all SQL injection findings to `critical`
C) Define each severity level with an example vulnerability in the prompt — show one `critical` SQL injection and one `high` SQL injection with explicit reasoning for the difference
D) Ask Claude to rate its confidence in each label and only accept `critical` labels when confidence exceeds 90%
