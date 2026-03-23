# Claude Certified Architect – Foundations: Mock Test 2

> 77 questions | Time: ~90 minutes | Passing score: 720/1000 (~69%)

## Instructions
- Select the BEST answer for each question
- Unanswered questions scored as incorrect
- No penalty for guessing

---

## Questions

**Q1.** You're building a multi-agent customer support system where a dispatcher agent routes tickets to specialized subagents (billing, technical, returns). The dispatcher needs to prevent subagents from calling tools recursively. Which pattern best prevents this cascading tool use?

A) Set `tool_choice: "any"` on the dispatcher and `tool_choice: "none"` on subagents
B) Use iteration caps of 3 on subagents and 10 on the dispatcher
C) Implement allowedTools gating at the subagent level in the Task definition
D) Require all subagent calls to use `stop_reason: "end_turn"`

---

**Q2.** In your Code Generation system, Claude encounters a `pause_turn` stop_reason after 5 tool calls. What does this signal, and what is the correct recovery action?

A) The session has timed out; restart with `fork_session`
B) Claude hit the server-side iteration limit; append the pause_turn response and continue the conversation
C) The task requires optimization; use `@import` to break it into modules
D) Tool execution failed; automatically retry without user intervention

---

**Q3.** You're designing an MCP server for a code review workflow. The tool descriptions must help Claude select the right tool without causing reasoning overload. Which principle is MOST critical?

A) Include verbose explanations of all edge cases in tool descriptions
B) Make input format constraints explicit in descriptions to enable unambiguous tool selection
C) List all possible output formats in the description for maximum flexibility
D) Combine multiple tools into single endpoints to reduce cognitive load

---

**Q4.** Your Multi-Agent Research System has three subagents that can run in parallel: data gathering, analysis, and synthesis. You want them to start simultaneously and wait for all to complete before the coordinator proceeds. Which approach is architecturally correct?

A) Call them sequentially with explicit await between each
B) Make three parallel Task calls and synchronize on completion
C) Use a single Task with `parallel_processing: true`
D) Nest them in the coordinator's prompt and rely on Claude to parallelize

---

**Q5.** In a Production Claude Code CI/CD workflow, you need to enforce a rule that all database queries must include a timeout. Where should this enforcement logic live?

A) In a PostToolUse hook that validates and rejects queries without timeouts
B) In the CLAUDE.md file as a broad guideline
C) In the tool description as a suggestion
D) In a separate validation script outside Claude Code

---

**Q6.** Your structured data extraction system must extract product information with 99% accuracy. Which combination of techniques is most reliable?

A) Use natural language prompting with iteration caps
B) Pair JSON schema output formatting with few-shot examples and retry-on-error feedback loops
C) Use tool_choice: "forced" with a single extraction tool
D) Implement self-review where Claude checks its own output

---

**Q7.** You're integrating a customer support agent with an MCP server for ticket management. The server supports both `list_tickets` and `get_ticket_details`. Claude sometimes calls the wrong tool when both are available. How do you fix this?

A) Remove one tool to eliminate ambiguity
B) Make input format constraints in descriptions more explicit to disambiguate
C) Use `tool_choice: "forced"` to hardcode the correct tool
D) Implement post-tool validation to reject wrong tool calls

---

**Q8.** In your Multi-Agent Research System, a subagent completes its task but returns low-confidence results. The coordinator should verify these before proceeding. Which handoff pattern is best?

A) Silent acceptance—the coordinator always trusts subagent outputs
B) Explicit human escalation for any confidence below 85%
C) Automatic re-run of the subagent without user involvement
D) Append a confidence score to the response for coordinator evaluation

---

**Q9.** Your CLAUDE.md file specifies a rule: "Always use snake_case for variable names." A subagent running in a `fork_session` should inherit this rule. What happens by default?

A) The rule automatically applies due to CLAUDE.md inheritance
B) `fork_session` creates isolation; the subagent doesn't see the parent's CLAUDE.md
C) You must explicitly re-include the rule in the subagent's instructions
D) The rule applies only if you use `@import` in the subagent's session

---

**Q10.** You're building a developer productivity tool that generates code snippets. To ensure consistent formatting, you decide to use JSON schema structured output. Which is a KEY constraint of structured outputs?

A) They work with streaming responses
B) They require manual validation after generation
C) They cannot include optional fields in the schema
D) They enforce constraints at token-generation time via compiled grammar

---

**Q11.** In the code generation workflow, you want to compare two approaches: iterative refinement via prompt chaining vs. dynamic decomposition via Task spawning. When is dynamic decomposition clearly better?

A) When the subtasks are unknown until runtime based on analysis
B) When you want simpler, more maintainable code
C) When performance is not a constraint
D) Always, because it's more sophisticated

---

**Q12.** You're implementing the `--resume` flag in a CI/CD Claude Code workflow to restart interrupted builds. What is the PRIMARY benefit?

A) It re-runs the entire pipeline from scratch
B) It allows resuming from the last checkpoint, avoiding redundant work
C) It prevents concurrent builds
D) It bypasses all validation rules

---

**Q13.** Your Customer Support Resolution Agent encounters an error while calling the refund tool. The error indicates the transaction ID doesn't exist. Which retry strategy should you use?

A) Immediately retry with the same parameters
B) Append the error message and failed output to the conversation, let Claude reason about retry
C) Skip the retry and escalate to a human
D) Modify the transaction ID and retry automatically

---

**Q14.** You're using the Batch API to process 10,000 support tickets for consistent response quality. Which benefit is MOST significant?

A) 50% cost savings and asynchronous processing
B) Guaranteed faster response times
C) Automatic error correction
D) No need for structured output validation

---

**Q15.** In your MCP integration, the tool returns an errorCategory field set to "retryable" but the API response was HTTP 200. How should Claude respond?

A) Ignore the errorCategory since the HTTP status was 200
B) Respect the errorCategory and retry the operation
C) Log the conflict and escalate to engineering
D) Use `tool_choice: "none"` to disable further tool calls

---

**Q16.** Your Multi-Agent Research System uses a coordinator-subagent hub-and-spoke pattern. A subagent needs to pass findings to another subagent. What's the architectural issue?

A) It's fine; subagents can communicate directly
B) Direct subagent-to-subagent communication violates the hub-and-spoke pattern; route through coordinator
C) You need to implement inter-subagent MCP servers
D) Use `fork_session` for each subagent independently

---

**Q17.** In Claude Code, you want to check if a file exists before modifying it. The Edit tool requires knowing the exact old_string to replace. What's the safest approach?

A) Use Edit without reading first and catch errors
B) Always Read the file first to get the exact content for Edit to match
C) Use Glob to find the file, then assume its structure
D) Skip reading and write a new file instead

---

**Q18.** You're building a workflow in Claude Code where multiple tasks interact (e.g., one task reads a file, another modifies it). Which approach prevents race conditions?

A) Run tasks in parallel and hope they don't conflict
B) Batch interacting tasks together in a single request for sequential execution
C) Use different file paths for each task
D) Add sleep statements between tasks

---

**Q19.** In the Structured Data Extraction scenario, you need to extract 50 product fields with different validation rules. How do you ensure accuracy across all fields?

A) Include all rules in the main prompt
B) Use a single comprehensive few-shot example
C) Multiple focused few-shot examples for different field types + JSON schema validation + retry loops
D) Trust the model and skip validation

---

**Q20.** Your Developer Productivity tool uses Claude Code with a `.claude/rules/` directory. How does the YAML frontmatter in these files affect Claude's behavior?

A) It's just documentation; the content doesn't affect behavior
B) It configures the context loading and precedence of rules at runtime
C) It controls tool access permissions
D) It enables GitHub integration

---

**Q21.** In a Multi-Agent Research System, you want subagents to run in parallel but ensure they don't exceed context limits individually. Which configuration prevents context overload?

A) Single large CLAUDE.md for all subagents
B) Separate Task calls with isolated context for each subagent
C) Force sequential execution to save tokens
D) No special configuration needed; Claude handles it automatically

---

**Q22.** You're configuring an MCP server in `.mcp.json` and need to pass environment-specific values. How do you safely reference environment variables?

A) Hard-code all values in `.mcp.json`
B) Use `${ENV_VAR}` syntax for project-scoped environment variable substitution
C) Pass them as command-line arguments
D) Store in a separate secrets file

---

**Q23.** Your structured output uses JSON schema with optional fields. A few-shot example doesn't include these optional fields. What happens during inference?

A) Claude always includes all fields in the output
B) Claude follows the schema and includes only required fields, as shown in examples
C) The output is invalid because the schema wasn't complete
D) Claude generates random optional fields

---

**Q24.** In a Batch API workflow, you submit 1,000 requests with custom_id for tracking. After 24 hours, the batch completes. How do you retrieve specific results?

A) Poll the API every hour
B) Fetch results using the custom_id for lookup
C) Re-run the entire batch
D) Results are automatically sent to your email

---

**Q25.** You're implementing the /compact command in Claude Code to reduce context usage. When is this MOST valuable?

A) At the start of every session
B) After accumulated context exceeds 60% capacity, before critical analysis
C) Never; compression always loses information
D) Only if the session is failing

---

**Q26.** Your Customer Support Agent has a `.claude/commands/` directory with custom slash commands. How do these differ from `.claude/skills/`?

A) Commands are faster; skills are for complex logic
B) Commands define available slash commands; skills are reusable code modules or workflows
C) They're identical; just different naming conventions
D) Commands run in the background; skills require user invocation

---

**Q27.** In the code generation scenario, Claude needs to choose between three similar tools: `create_file`, `write_file`, and `generate_code_file`. What makes tool_description the PRIMARY factor in selection?

A) It's the only thing Claude reads
B) Input format constraints in descriptions enable disambiguation when tools overlap
C) Claude ignores descriptions and picks randomly
D) Tool names are more important than descriptions

---

**Q28.** Your Multi-Agent Research System has a subagent that sometimes generates speculative claims without evidence. Which Context Management pattern helps catch this?

A) Ignore it; subagents are always right
B) Use case facts blocks in coordinator to anchor findings to specific evidence sources
C) Trust the model's self-review
D) Implement human review for every claim

---

**Q29.** You're building a long-running developer productivity session that will consume ~150k tokens. Which proactive strategy prevents context collapse?

A) No special measures; Claude handles it automatically
B) Compact at ~60% capacity and maintain scratchpad files for cross-phase findings
C) Increase the context window indefinitely
D) Split into many short sessions

---

**Q30.** In your Structured Data Extraction workflow, you test the system and find that 95% of extractions are correct, but specific field types (dates, phone numbers) are only 80% accurate. Which analysis reveals this?

A) Single aggregate accuracy score
B) Stratified accuracy analysis segmented by field type
C) Self-review by the model
D) User feedback only

---

**Q31.** Your MCP resources feature allows Claude to discover available tools. Why is this important for tool selection?

A) It eliminates the need for tool descriptions
B) It enables Claude to browse available resources and select appropriate tools without reasoning overload
C) It's just for documentation
D) It replaces JSON schemas

---

**Q32.** In Claude Code, you're working on a bug fix in a feature. Which mode is most appropriate: plan mode or direct mode?

A) Plan mode for everything
B) Direct mode for small, targeted changes; plan mode for architectural changes
C) They're equivalent; choose arbitrarily
D) Only use direct mode; plan mode is deprecated

---

**Q33.** Your multi-agent system's coordinator needs to validate that all subagents completed successfully before proceeding. Which pattern is architecturally correct?

A) Assume all tasks complete automatically
B) Check Task completion status and implement explicit synchronization points
C) Use a single prompt that describes all subagents
D) Rely on natural language completion signals

---

**Q34.** You're using Grep in Claude Code to search for "api_key" across 10,000 files. Which approach is most efficient?

A) Read every file sequentially
B) Use Grep with glob filtering to target only relevant files
C) Use Find and Read for each result
D) Write a custom search script

---

**Q35.** In the Structured Data Extraction scenario, your few-shot examples show the correct format for product descriptions. During inference, Claude sometimes deviates. Why?

A) Few-shot examples are just suggestions
B) Format consistency is enforced by combining few-shot training + JSON schema + tool_choice constraints
C) The model always invents new formats
D) You need to use `tool_choice: "forced"`

---

**Q36.** You're implementing a retry-with-error-feedback loop for a data extraction task. After Claude's first attempt fails validation, what's the correct next step?

A) Give up and escalate
B) Append the error message + the failed output + original input to the conversation
C) Completely change the prompt
D) Automatically override with a default value

---

**Q37.** Your Developer Productivity tool uses interviews to refine results iteratively. In the first pass, Claude proposes a solution. What should the second pass focus on?

A) Completely rewriting the solution
B) Sequential fixes targeting specific issues from the first pass
C) Accepting the solution as-is
D) Asking unrelated questions

---

**Q38.** In your `.claude/rules/` directory, you have a rule about API response handling. Another rule in a child directory contradicts it. Which takes precedence?

A) The global rule always wins
B) The most specific (child directory) rule takes precedence
C) You must manually resolve conflicts
D) Both rules apply simultaneously

---

**Q39.** You're setting up a Customer Support Agent in a `fork_session`. The parent session had a CLAUDE.md enforcing a specific response tone. Does the subagent inherit this?

A) Yes, automatically via CLAUDE.md inheritance
B) No; fork_session isolates context completely
C) Only if you explicitly pass it in the task prompt
D) Only if you use `@import` in the fork_session

---

**Q40.** Your structured output schema defines a "product_sku" field as required with pattern validation. During inference, Claude generates an invalid SKU. What happens?

A) Claude's output is rejected; it regenerates to match the schema
B) The invalid output passes through; you validate afterwards
C) The field becomes optional
D) An error is logged but the request succeeds

---

**Q41.** In a Multi-Agent Research System, a subagent discovers a critical finding that contradicts the coordinator's initial hypothesis. What's the correct pattern?

A) Suppress the finding to maintain consistency
B) Honor the finding explicitly; update the coordinator's model
C) Automatically escalate to human review
D) Retry the subagent until it agrees

---

**Q42.** Your Batch API workflow processes 5,000 requests over 24 hours. Compared to synchronous API calls, what's the primary advantage?

A) Guaranteed faster responses
B) 50% cost reduction + ability to spread processing time
C) No need for error handling
D) Automatic retries for all failures

---

**Q43.** You're designing MCP tool descriptions for a research system. The tools `search_database` and `query_index` both accept text inputs. To prevent Claude from selecting the wrong one, what's critical?

A) List all possible outputs for each
B) Include explicit input format constraints and success conditions in descriptions
C) Remove one tool entirely
D) Use identical descriptions to avoid confusion

---

**Q44.** In Claude Code, you're working on a file that's already in use by another process. Which tool ensures safe read access without errors?

A) Edit (always succeeds)
B) Read (safely retrieves content for manipulation)
C) Glob (finds the file)
D) Bash (direct filesystem access)

---

**Q45.** Your customer support workflow sometimes escalates to human review with unclear reasoning. Which pattern improves decision transparency?

A) Add more tool calls
B) Implement claim-source provenance mappings that connect decisions to evidence
C) Trust the model's reasoning implicitly
D) Remove escalation entirely

---

**Q46.** In the Code Generation scenario, Claude Code needs to refactor a class. You want to ensure it doesn't introduce bugs. Which verification strategy is most reliable?

A) Trust Claude's output
B) Multi-pass focused reviews: first pass for structure, second for logic, third for tests
C) Single comprehensive review
D) No verification needed

---

**Q47.** Your Multi-Agent Research System's coordinator maintains a scratchpad file to track findings across subagents. Why is this critical for long conversations?

A) It's just documentation
B) It preserves key findings across context resets and enables accuracy analysis later
C) It slows down processing
D) Unnecessary if you have a large context window

---

**Q48.** You're implementing an Explore subagent to help with discovery in your Code Generation system. When is Explore most valuable?

A) For every task
B) When you need verbose discovery of complex file structures or patterns
C) Never; it slows things down
D) Only at the start of a session

---

**Q49.** In the Structured Data Extraction scenario, you're extracting from 100,000 documents. Using Batch API with `custom_id`, how do you handle partial failures?

A) Retry the entire batch
B) Query failed results via `custom_id` and retry only those
C) Ignore failures and proceed
D) Manually inspect each failure

---

**Q50.** Your CLAUDE.md file imports rules from multiple sources using `@import`. In what order are imports resolved?

A) Random order
B) Sequential order; later imports can override earlier ones
C) All simultaneously
D) Only the first import is used

---

**Q51.** You're building a hub-and-spoke multi-agent system where the coordinator must broadcast information to 5 subagents. What's the most efficient pattern?

A) Sequential Task calls to each subagent
B) Parallel Task calls to all subagents, synchronizing before coordinator continues
C) Single nested prompt describing all relationships
D) Use fork_session for each subagent in series

---

**Q52.** In Claude Code, the Edit tool requires an exact `old_string` match. If the file has whitespace variations, what's the fallback?

A) Manual string replacement
B) Read the full file, get exact context, then Edit with precise match
C) Use Find to locate the string first
D) Rewrite the entire file

---

**Q53.** Your structured data extraction uses few-shot examples. Which detail is MOST critical to include in examples?

A) Irrelevant fields that might appear
B) Edge cases and optional field handling to establish format consistency
C) Comments explaining why the format is chosen
D) Personal notes from the engineer

---

**Q54.** You want to limit a subagent's tool access. You've defined `allowedTools: ["tool_a", "tool_b"]` in the Task. What's the primary benefit?

A) Documentation only
B) Actual runtime gating that prevents the subagent from calling unlisted tools
C) Improves performance marginally
D) Speeds up tool selection

---

**Q55.** In your customer support workflow, you implement silent error suppression (catching errors without telling Claude). What's the danger?

A) Silent errors are always fine
B) Claude becomes unaware of failures and makes incorrect decisions based on invalid data
C) Errors are immediately escalated
D) Errors are logged to external systems automatically

---

**Q56.** Your long-context research session has consumed 70% of the available context. You decide to use `/compact`. What should you retain?

A) Everything automatically
B) Key findings + decisions at the start (address lost-in-the-middle); discard verbose exploration
C) Nothing; start fresh
D) Only the most recent turns

---

**Q57.** In your developer productivity tool, Claude proposes a refactoring. You want to validate it in isolation without affecting the codebase. Which approach is safest?

A) Apply directly to the codebase
B) Use fork_session or a temporary branch to test the change
C) Trust Claude's output
D) Manual inspection only

---

**Q58.** Your Batch API request specifies `--output-format json`. What's the primary benefit for reliability?

A) Faster processing
B) Guaranteed parseable output that downstream systems can consume without error handling
C) Larger context window
D) Automatic error correction

---

**Q59.** You're designing a tool for a Multi-Agent Research System. The tool's input schema has overlapping parameters with a similar tool. How do tool descriptions prevent disambiguation issues?

A) They don't; remove one tool
B) Explicit input format constraints make it clear which tool applies to each use case
C) Use the same description for both
D) Let Claude guess

---

**Q60.** In Claude Code, you discover that a file you wanted to edit actually doesn't exist yet. Instead of Edit, what's the correct tool?

A) Read (it will fail gracefully)
B) Write (creates a new file with specified content)
C) Edit (will handle missing files)
D) Bash (use text commands)

---

**Q61.** Your multi-agent coordinator needs to ensure subagents don't exceed a per-request context budget. What's the mechanism?

A) Hope they self-regulate
B) Isolated fork_session context + explicit context budgets in Task definitions
C) Single shared context for all
D) No mechanism needed

---

**Q62.** In structured output with JSON schema, you mark a field as required but forget to include it in all few-shot examples. What happens during inference?

A) The field is sometimes optional
B) Schema constraints + examples work together; schema enforces inclusion, examples guide format
C) The field is always optional
D) Inference fails

---

**Q63.** Your customer support agent escalates decisions to humans sometimes. When should escalation happen automatically WITHOUT Claude deciding?

A) Never; let Claude always decide
B) When explicit human instructions indicate escalation is needed
C) Always escalate
D) Randomly

---

**Q64.** You implement a PostToolUse hook in your agentic system. What's a valid use case for this?

A) Hook can display tool results to the user
B) Normalize tool output, enforce format constraints, trim sensitive data before Claude sees it
C) Change Claude's response
D) Modify the original tool request

---

**Q65.** In your research system, you maintain confidence scores for subagent findings. To enable stratified accuracy analysis, what data structure is most useful?

A) Single aggregate score
B) Per-finding confidence + labeled ground truth to analyze accuracy by confidence bucket
C) No tracking needed
D) User ratings only

---

**Q66.** Your `.claude/commands/` defines a custom `/analyze` command. How does Claude invoke it?

A) Automatically on every message
B) When the user types `/analyze` or Claude decides to use it
C) Only manually by the user
D) In a separate process

---

**Q67.** You're building a code generation workflow with iterative refinement. In the first iteration, Claude generates a function. The second pass should focus on what?

A) Completely rewriting from scratch
B) Gathering specific feedback and fixing targeted issues sequentially
C) No second pass needed
D) Adding random features

---

**Q68.** Your Multi-Agent Research System has a coordinator that receives findings from 3 subagents. To prepare for accuracy validation later, what should you preserve?

A) Only final conclusions
B) Detailed scratchpad mapping each finding to its source subagent and evidence
C) User feedback only
D) Nothing; findings are ephemeral

---

**Q69.** In an MCP integration, the tool returns both an HTTP 200 AND an `isError: true` field. How should Claude interpret this?

A) Success, because HTTP is 200
B) Error, because isError indicates failure; respect the domain-specific error signal
C) Ignore both signals
D) Ask the user to clarify

---

**Q70.** Your Batch API workflow has 10,000 requests. You set a 24-hour timeout. What happens if processing completes earlier?

A) Results are withheld until 24 hours pass
B) Results are available immediately upon completion; 24 hours is just the maximum
C) All requests are cancelled
D) A random subset is processed

---

**Q71.** In Claude Code, you're working in plan mode to propose an architecture. What's the expected output before actual implementation?

A) Nothing; plan mode is just for thinking
B) A detailed plan with reasoning that you can review before proceeding to direct mode
C) Immediate code changes
D) Random suggestions

---

**Q72.** Your structured data extraction sometimes misses fields because the JSON schema allows them as optional. To enforce extraction of all available data, what should you combine?

A) Schema alone
B) Required schema fields + few-shot examples showing complete extraction + validation loops
C) No enforcement possible
D) Trust the model

---

**Q73.** You implement a --json-schema validation flag in your Claude Code workflow. What does this enable?

A) Just documentation
B) Direct output validation against the schema; failures trigger prompts for correction
C) Automatic schema generation
D) No real effect

---

**Q74.** In a Multi-Agent Research System, a subagent completes but the coordinator realizes it needs additional analysis. What's the cleanest approach?

A) Restart everything from scratch
B) Design task prerequisites so dependencies are explicit and spawn new Tasks as needed
C) Manually re-prompt the subagent
D) Ignore the need for additional analysis

---

**Q75.** Your long-context analysis is approaching 85% utilization. Using lost-in-the-middle patterns, where should critical decision points appear?

A) Anywhere; location doesn't matter
B) At the start (after case facts) and end of context to maximize recall
C) Buried in the middle
D) Doesn't matter because the model has perfect recall

---

**Q76.** In your Customer Support Agent, you're extracting structured data from unstructured user messages. JSON schema enforces the output format, but how do you ensure semantic correctness?

A) Schema guarantees everything
B) JSON schema guarantees format; few-shot + retry loops ensure semantic correctness
C) No validation possible
D) Manual review everything

---

**Q77.** Your multi-agent coordinator uses explicit task prerequisites to ensure subagent A completes before subagent B starts. What's the primary benefit?

A) No real benefit; execution order doesn't matter
B) Defines data dependencies programmatically; prevents downstream tasks from running with incomplete input
C) Slows down processing
D) Makes code harder to understand
