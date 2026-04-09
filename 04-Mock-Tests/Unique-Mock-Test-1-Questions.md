# Claude Certified Architect - Foundations: Unique Mock Test 1

> 30 original questions | Target time: 35-45 minutes | Style: scenario-based

## Instructions
- Select the BEST answer for each question
- This mock is original and derived from concepts in your local study guides plus public Anthropic documentation
- Questions intentionally reuse core principles across different scenarios, because the real exam appears to do the same

---

## Questions

**Q1.** Your operations agent calls a customer lookup tool and Claude returns `stop_reason: "tool_use"`. What should your application do next?

A) End the conversation and return the tool call to the user as final output
B) Execute the requested tool, append the tool result to the conversation, and continue the loop
C) Retry the same model request without tools enabled
D) Start a brand new session so the tool result does not pollute context

---

**Q2.** A lead architect wants one coordinator agent to dispatch four independent research subtasks simultaneously. Which pattern best matches that requirement?

A) Run four Task calls in parallel so each subtask executes in its own context
B) Put all four subtasks into one long prompt and require one final answer
C) Use one shared scratchpad and one agent turn per subtask in sequence
D) Use fork_session only after all four subtasks complete

---

**Q3.** You set `tool_choice` to a forced mode for a critical approval tool. What behavior are you enforcing?

A) Claude may either answer normally or call several tools
B) Claude must call exactly one tool instead of replying with plain text
C) Claude must call at least two tools before ending its turn
D) Claude cannot call any tools until the user confirms

---

**Q4.** A support bot is asked, "I don't want automation. Transfer me to a person." What is the correct system behavior?

A) Try one more automated troubleshooting pass before escalation
B) Honor the explicit escalation request immediately
C) Ignore the request if confidence in the answer is high
D) Ask the user to restate the issue in technical terms first

---

**Q5.** Your team has instructions at the user, project, and directory levels. A rule in a subdirectory conflicts with a project-wide rule. Which one wins?

A) User-level rule, because it is loaded first
B) Project-level rule, because it applies to the whole repo
C) Directory-level rule, because the most specific scope takes precedence
D) Neither; conflicting rules always merge equally

---

**Q6.** A compliance rule should apply only to files under `payments/ledger/`. What is the cleanest way to scope it?

A) Put it in the project root so every file gets the rule
B) Put it in a path-filtered rule or directory-scoped instruction for that subtree
C) Add it manually to each prompt when reviewing ledger files
D) Disable project instructions and keep only user instructions

---

**Q7.** An MCP server exposes several tools. Claude often chooses the wrong one because they are named too generally. What should you improve first?

A) Increase model temperature so tool selection varies less
B) Rewrite tool descriptions to make purpose, inputs, outputs, and boundaries explicit
C) Force a tool choice on every request, even when not necessary
D) Combine all tools into one generic `process_data` tool

---

**Q8.** Your tool may fail due to malformed input or a transient network timeout. Which response shape best supports reliable downstream handling?

A) A plain string error message for every failure type
B) A stack trace plus HTTP status code only
C) Structured errors with fields like `errorCategory` and `isRetryable`
D) Silent retries inside the tool without telling the agent

---

**Q9.** A document extraction workflow runs in three passes because documents are too large for one context window. What preserves findings between passes best?

A) Rely on the model to remember prior outputs
B) Store intermediate findings in scratchpad files for later passes
C) Re-run the first pass every time the next pass starts
D) Put all previous outputs in environment variables

---

**Q10.** An agent extracts claims from reports and then uses the same model instance to verify its own claims. What is the main reliability issue?

A) The same instance may be biased toward confirming its own earlier work
B) The verifier cannot read its own prior messages
C) Self-review only works with batch processing enabled
D) Tool descriptions become unavailable in review mode

---

**Q11.** You need to process 8,000 evaluation prompts overnight and can wait for results. Why is the Message Batches API a strong fit?

A) It guarantees immediate results with higher priority than normal requests
B) It supports asynchronous large-scale processing with lower cost for non-urgent workloads
C) It automatically deduplicates repeated requests inside the batch
D) It replaces the need for request validation

---

**Q12.** Batch results return in a different order than the requests were submitted. What field should you rely on to match each result back to its original request?

A) `request_index`
B) `processing_status`
C) `custom_id`
D) `ended_at`

---

**Q13.** A developer asks Claude Code to modernize a legacy service spanning dozens of files. Why would Plan Mode be useful first?

A) It lowers token usage automatically
B) It helps clarify decomposition and approach before making changes
C) It disables tools that might be dangerous
D) It guarantees the refactor will happen in parallel

---

**Q14.** In a CI/CD validation workflow, a security check fails and provisioning must not continue. What should the validation step return?

A) A non-retryable structured error that downstream automation treats as a hard stop
B) An `end_turn` response with no text so the pipeline guesses what happened
C) A retryable error so the pipeline keeps attempting the deployment
D) A warning string in logs only

---

**Q15.** You need Claude's tool calls to match a schema exactly when invoking a client tool. Which configuration improves conformance most directly?

A) Add more few-shot examples and hope the shape stays stable
B) Set `strict: true` on the tool definition
C) Ask Claude to "be careful with JSON"
D) Move the schema into a separate markdown file

---

**Q16.** A team starts tweaking prompts before deciding how success will be measured. According to prompt engineering best practice, what should come first?

A) Choosing the fastest model available
B) Defining clear success criteria and evaluation methods
C) Writing five few-shot examples before any testing
D) Splitting the prompt into XML sections immediately

---

**Q17.** A response format is inconsistent despite detailed written instructions. Which next step is usually more effective than adding even more prose?

A) Increase randomness so the model explores more formats
B) Use few-shot examples that demonstrate the exact desired structure
C) Remove all constraints so the model simplifies naturally
D) Avoid examples because they bias the model too much

---

**Q18.** A research system must prove which document supported each conclusion. What data structure best supports auditability?

A) One combined notes file with no tagging
B) Claim-source provenance mappings for each extracted finding
C) A final summary that omits intermediate evidence
D) A confidence score only, without source identifiers

---

**Q19.** You trim long agent conversations to manage token growth. What must be preserved during trimming?

A) Only the most recent three messages
B) Every message equally, regardless of relevance
C) Critical facts and decisions needed for current and future turns
D) Only tool outputs, never user instructions

---

**Q20.** Several tools return timestamps and status values in inconsistent formats. What is a good use of PostToolUse hooks?

A) Normalize tool outputs before the model reasons over them
B) Remove all metadata so outputs are shorter
C) Prevent Claude from seeing any tool result details
D) Replace all tool calls with direct user prompts

---

**Q21.** In a large repository, you want to find Python function definitions quickly without loading full files. Which Claude Code built-in tool is the best fit?

A) Read
B) Edit
C) Glob
D) Grep

---

**Q22.** A parent agent can launch subagents, and each subagent needs a different tool set. How should this be configured?

A) Every agent should share the same global allowedTools list
B) The parent should include Task, and each subagent should have domain-specific allowedTools
C) Subagents should auto-discover tools at runtime with no restrictions
D) Only the parent agent should be allowed to use tools

---

**Q23.** Enterprise customers may use billing and escalation tools, while Basic customers may not. What is the most scalable control pattern?

A) Maintain separate prompts for every customer tier and role combination
B) Filter allowed tools programmatically based on tier before each turn
C) Rename enterprise-only tools so Basic users do not notice them
D) Put all restrictions in the end-user message

---

**Q24.** A skill should continue from its parent workflow with relevant prior context. How should that be expressed?

A) Use `context: fork` so the skill inherits parent context appropriately
B) Use `--resume` inside the prompt text
C) Delete all previous context to avoid contamination
D) Skills always inherit context automatically without configuration

---

**Q25.** You want to know whether your agent's confidence statements match actual accuracy over time. What evaluation pattern supports that?

A) Let the same model grade its own confidence claims
B) Use independent review or separate instances to compare confidence against real outcomes
C) Increase output length so confidence explanations are longer
D) Add a mandatory `confidence_score` field and assume it is calibrated

---

**Q26.** A privacy-sensitive team is considering Message Batches API for bulk processing under a strict zero-data-retention policy. Which constraint matters here?

A) Batches require immediate synchronous retrieval
B) Batches are not eligible for zero data retention
C) Batches cannot include tool use requests
D) Batches only work with one model family

---

**Q27.** When `tool_choice` is not explicitly constrained, what most strongly influences which tool Claude selects?

A) Tool descriptions
B) Tool parameter count
C) The order of user messages only
D) The programming language of the client SDK

---

**Q28.** A validation tool reports that generated output is missing required fields, but the issue is fixable. What should the agent do next?

A) Stop immediately and ask a human to finish the task
B) Retry with explicit error feedback describing what is missing
C) Ignore the validation result if the output looks mostly correct
D) Delete the previous attempt from the conversation history

---

**Q29.** In a fact extraction pipeline, low-confidence findings should receive extra scrutiny. Which pattern best fits?

A) Drop all low-confidence findings automatically
B) Run a separate validation pass on low-confidence findings and preserve context between phases
C) Re-run the full workflow on every finding regardless of confidence
D) Ask the same extractor to reword the answer without new evidence

---

**Q30.** Claude finishes answering one item in a queue and returns `stop_reason: "end_turn"`. When you append the next item, it does not continue automatically. What is the most likely interpretation?

A) `end_turn` means the session is corrupt and must be discarded
B) `end_turn` means Claude completed its turn; you need to continue with the next turn intentionally
C) `end_turn` means tool use was required but blocked
D) `end_turn` only occurs when the context window is exhausted