# Claude Certified Architect – Foundations: Mock Test 1

> 77 questions | Time: ~90 minutes | Passing score: 720/1000 (~69%)

## Instructions
- Select the BEST answer for each question
- Unanswered questions scored as incorrect
- No penalty for guessing

---

## Questions

**Q1.** Your customer support agent receives a batch of inquiries. After Claude processes the first inquiry and returns `stop_reason: "end_turn"`, you append the next inquiry to the conversation. However, the agent produces no new response. What is the most likely cause and appropriate resolution?

A) The agent has exhausted its maximum turns per session; you must create a fork_session
B) Claude naturally completed its turn; you should check if the next inquiry requires context from the previous response before continuing
C) The agent requires explicit tool_use directive; add tool_choice: "forced" to the next message
D) The conversation context exceeds 200K tokens; implement context trimming via PostToolUse hook

---

**Q2.** In a multi-agent research system, you need to decompose a complex query into 5 parallel subtasks. Each subtask should execute independently and report back. Which approach best implements this architecture?

A) Chain the subtasks sequentially using fork_session after each completes
B) Use the Task tool with allowedTools containing all 5 subtask definitions and call them in parallel within a single agent turn
C) Create 5 separate sessions with --resume flag and coordinate results in a parent script
D) Implement a manual queue system with Redis to serialize subtask execution

---

**Q3.** Your code generation workflow uses Claude Code to generate functions. The generated code sometimes lacks proper type annotations. You want to enforce this requirement programmatically. Which gating mechanism is most efficient?

A) Use prerequisite gating in the agent configuration to check generated code before returning
B) Add a PostToolUse hook that validates type annotations and triggers a retry_with_error_feedback loop
C) Implement prompt-based instruction asking Claude to "always include type annotations"
D) Deploy a separate linting tool that Claude must call before finalizing code

---

**Q4.** When designing an MCP server for your customer support agent, you want to filter tools shown to Claude based on the support tier. The tool descriptions must remain consistent, but visibility should vary. What is the best approach?

A) Use tool_choice: "any" with conditional tool descriptions in the MCP configuration
B) Implement tool filtering logic in your MCP server's tool listing endpoint and leverage tool descriptions as the primary selection mechanism
C) Create separate MCP servers per support tier and switch via allowedTools
D) Use CLAUDE.md with conditional imports based on support tier

---

**Q5.** A developer productivity agent uses the Claude Code built-in tools: Grep, Read, Glob, and Edit. The agent must search for all function definitions in a large codebase. Which built-in tool is most efficient for this task?

A) Read the entire codebase file by file
B) Use Grep with a regex pattern for function definitions and filter by file type
C) Use Glob to list all files, then Read each one to find definitions
D) Use Edit to tag all functions, then query tagged locations

---

**Q6.** Your CI/CD workflow uses Claude Code with the `-p` flag to validate deployment configurations. You need structured JSON output for downstream systems. Which approach ensures proper formatting?

A) Use `--output-format json` flag and rely on Claude's natural JSON generation
B) Specify a `--json-schema` parameter that Claude must validate against before returning
C) Implement tool_choice: "forced" for JSON serialization tools
D) Use the Batch API with 50% cost savings and custom validation

---

**Q7.** In a structured data extraction pipeline, you process legal documents to extract case facts. The documents vary in structure and length, but some exceed context window limits. Which strategy minimizes lost context and maintains extraction accuracy?

A) Use the Lost in the Middle strategy: place most important sections in the middle of the prompt
B) Implement stratified accuracy analysis with separate extraction passes for different document sections
C) Use a scratchpad file to accumulate extracted facts across multiple passes, enabling cross-phase persistence
D) Apply Batch API with automatic chunking and 50% pricing reduction

---

**Q8.** You're implementing error handling for a tool that sometimes fails due to network issues (retryable) and sometimes fails due to invalid input (non-retryable). How should this be structured in the error response?

A) Return all errors with max_retries: 3 parameter
B) Use errorCategory and isRetryable fields in a structured error response to enable proper retry-with-error-feedback behavior
C) Implement silent error suppression by catching exceptions internally
D) Create a separate endpoint for each error type

---

**Q9.** Your research system needs to review extracted claims against their source documents for accuracy verification. You want to use multiple Claude instances for parallel review to catch inconsistencies. What is the limitation you must account for?

A) Multiple instances cannot access the same files simultaneously
B) Self-review limitation: a single Claude instance cannot review its own work reliably; use separate instances for extraction and review
C) Batch API cannot process verification requests
D) Parallel execution requires shared session state via fork_session

---

**Q10.** When designing CLAUDE.md configuration files across your project, you have settings at the user level (~/.claude/config), project level (project/.claude/config), and directory level (src/.claude/config). How should conflicting settings be resolved?

A) User level settings always take precedence
B) Project level settings override user level; directory level overrides project level (hierarchy)
C) The most specific configuration file location wins; directory > project > user
D) All configurations merge with tool-level settings taking absolute precedence

---

**Q11.** Your customer support agent encounters an escalation request from a user who states "Please connect me to a human agent." The agent has a general response protocol. What is the correct approach?

A) Ignore the escalation and apply standard troubleshooting based on the issue type
B) Honor explicit escalation requests and route to human agents rather than continuing automated resolution
C) Synthesize a response that addresses the escalation request within the automated workflow
D) Log the request and randomly decide whether to escalate

---

**Q12.** In a CI/CD pipeline, Claude Code performs deployment validation. After validating, it must halt deployment and report errors without proceeding. Which behavior ensures this safety gate?

A) Use tool_choice: "forced" to prevent further tool calls
B) Return structured error with isRetryable: false and ensure downstream pipeline respects the stop condition
C) Implement silent error suppression to prevent cascading failures
D) Use Batch API to defer execution until manual approval

---

**Q13.** You configure an MCP server with environment variable expansion (e.g., `${ENV_VAR}`). In your .mcp.json file, you need the database connection string to use an environment variable. How should this be structured?

A) Use direct environment variable references: `"connection": "${DATABASE_URL}"`
B) Hard-code the URL and set it via tool parameters
C) Use conditional imports in CLAUDE.md to load different MCP configs per environment
D) Store variables in a separate config file and reference via path expansion

---

**Q14.** A code generation workflow produces output that must conform to a specific schema. You've tried using detailed prompts, but consistency is still an issue. What is the most reliable approach?

A) Use tool_use with a guaranteed schema enforcement tool rather than relying on prompt-based instructions
B) Implement few-shot examples in the system prompt showing desired output format
C) Use tool_choice: "any" to let Claude select formatting tools
D) Apply Batch API for higher accuracy through batch processing

---

**Q15.** Your agent operates in a high-stakes environment where confidence matters. Before returning a response, you want to measure how well-calibrated the agent's confidence is with actual accuracy. What strategy enables this?

A) Use self-review: have the same instance review its confidence
B) Implement confidence calibration with separate instances; compare claimed confidence against actual accuracy across multiple runs
C) Add a confidence_score parameter to all tool outputs
D) Use Batch API to process confidence metrics in parallel

---

**Q16.** In your multi-agent research system, one subagent produces a finding that contradicts information from another subagent. You need to track which source each claim came from. What is the best approach?

A) Merge all findings into a single document and manually track sources
B) Implement claim-source provenance mappings: tag each claim with its originating agent and source reference
C) Have a parent agent re-evaluate all findings
D) Discard contradictory findings as unreliable

---

**Q17.** Your developer productivity agent uses Claude Code with multiple CLAUDE.md files at different levels. A sensitive rule must apply only within the /src/security directory. How should this be configured?

A) Define the rule in ~/.claude/rules/security.yaml with YAML frontmatter paths filter
B) Add the rule to the project-level CLAUDE.md so all directories inherit it
C) Hard-code the rule in the agent's system prompt
D) Create a separate agent instance for the security directory

---

**Q18.** When implementing a fork_session for a skill, you want the forked session to inherit the parent's context. How should this be configured?

A) Use context: fork parameter to inherit parent context in the skill
B) Manually copy all parent messages to the forked session
C) Sessions automatically inherit context through the fork operation
D) Use --resume flag instead of fork_session

---

**Q19.** Your structured data extraction pipeline processes documents in two phases: initial extraction and confidence validation. Between phases, you need to preserve extracted data across multiple model calls. What is the most efficient approach?

A) Store results in environment variables
B) Use scratchpad files for cross-phase persistence of intermediate results
C) Re-process the entire document in phase 2
D) Use Batch API to process both phases in a single batch

---

**Q20.** In planning your agent's approach to a complex task, when should you use Plan Mode versus direct execution?

A) Always use Plan Mode for safety
B) Use Plan Mode for complex, multi-step tasks requiring decomposition strategy clarification; use direct execution for straightforward tasks
C) Plan Mode is deprecated; always use direct execution
D) Plan Mode only applies to Claude Code workflows

---

**Q21.** A CI/CD workflow using Claude Code must handle both success and error cases gracefully. You've set up error handling but some errors still occur silently in logs without triggering appropriate responses. What is the anti-pattern you've fallen into?

A) Using tool_choice: "forced" too aggressively
B) Silent error suppression: errors are caught but not properly surfaced for handling
C) Returning errors with max_retries parameter
D) Using Batch API for time-sensitive operations

---

**Q22.** Your customer support agent needs to provide consistent responses to similar inquiries. You've noticed response quality varies. Which approach ensures better consistency without sacrificing accuracy?

A) Use explicit criteria for each response type and few-shot examples demonstrating desired output
B) Rely solely on detailed system prompts
C) Increase temperature parameter for more variability
D) Use tool_choice: "forced" for all responses

---

**Q23.** In a multi-agent research system, Agent A must call Agent B as a task. You want to ensure Agent B can call tools specific to its domain. How should allowedTools be configured?

A) Use a single allowedTools list shared by all agents
B) Define domain-specific allowedTools per agent; include Task tool in parent agent's allowedTools for subagent calls
C) Create separate allowedTools configuration files per agent
D) Let each agent auto-discover its tools via MCP

---

**Q24.** When using the Batch API for processing 1000 documents overnight, what is the key financial and operational advantage?

A) Unlimited concurrent processing
B) 50% cost reduction on token pricing with a 24-hour processing window for non-urgent workloads
C) Automatic deduplication of requests
D) Priority processing in Anthropic's queue

---

**Q25.** Your agent's tool descriptions are critical for Claude's tool selection behavior. How much control does this provide over which tools are called?

A) Tool descriptions are secondary; tool_choice parameter is the primary mechanism
B) Tool descriptions serve as the primary selection mechanism when tool_choice is not specified
C) Descriptions have no impact on tool selection
D) Tool descriptions only affect the UI display of available tools

---

**Q26.** A customer support agent generates responses that sometimes lack necessary information. You want to ensure completeness before returning responses. What retry strategy is most effective?

A) Ask Claude to "be thorough" in the system prompt
B) Implement retry-with-error-feedback loop: identify missing information, feed back error details, and have Claude revise
C) Use tool_choice: "forced" to enforce completeness checks
D) Increase token limits to allow longer responses

---

**Q27.** In a code generation workflow using Claude Code, you need to ensure generated functions are properly tested. Which architectural approach is most sound?

A) Generate test cases in the same agent turn as code generation
B) Use parallel Task calls to generate code and tests simultaneously, then validate consistency
C) Manually write tests after code generation
D) Skip testing for generated code

---

**Q28.** Your agent uses multiple tools to accomplish tasks. You notice it sometimes calls unnecessary tools. How should tool selection be controlled to improve efficiency?

A) Remove optional tools from the environment
B) Use tool_choice: auto (default) or any for flexible selection; "forced" when a specific tool is required
C) Randomize tool availability
D) Require explicit tool_choice in every message

---

**Q29.** A customer support workflow needs different tool sets based on customer tier (Basic, Pro, Enterprise). Supporting this with minimal configuration overhead, what is the best approach?

A) Create three separate agents
B) Implement prerequisite gating that checks tier and programmatically filters allowedTools before each turn
C) Modify tool descriptions to indicate tier requirements
D) Use a separate CLAUDE.md file per tier

---

**Q30.** When Claude reaches `stop_reason: "tool_use"`, what is the required next step in the agentic loop?

A) Return the response to the user immediately
B) Execute the requested tool(s), append results to messages, and continue the loop
C) Escalate to a human for approval
D) Clear the conversation history and start fresh

---

**Q31.** Your multi-agent system has a coordination layer that must track which agents have completed their tasks. Agent status updates arrive asynchronously. What is the critical consideration for maintaining system consistency?

A) Assume all agents complete within the same turn
B) Implement explicit status tracking with timeout handling and retry logic for failed agents
C) Have agents report completion via a shared database
D) Use fork_session to synchronize agent states

---

**Q32.** In designing a Customer Support Agent (exam scenario), you want to deflect out-of-scope inquiries without escalating. How should this be configured?

A) Train Claude to refuse all off-topic requests
B) Use allowedTools to exclude escalation tools for certain inquiry types, combined with explicit prompt instructions for deflection
C) Always escalate off-topic inquiries
D) Remove escalation capabilities entirely

---

**Q33.** A Code Generation workflow (exam scenario) needs to validate generated code against a specific style guide. This validation is complex and best done by a separate system. Which approach integrates validation most cleanly?

A) Claude performs all validation internally
B) Use tool_use to call an external validation tool; track validation results and retry with error feedback if needed
C) Skip validation and rely on generated code quality
D) Implement validation via CLAUDE.md rules only

---

**Q34.** Your Multi-Agent Research System (exam scenario) discovers two conflicting facts from different sources. You need confidence in the resolution. What approach provides the best accuracy?

A) Pick the first source encountered
B) Use multiple instances to review both sources independently, then use stratified accuracy analysis to determine reliability
C) Trust the most detailed source
D) Average the claims together

---

**Q35.** In a Developer Productivity agent (exam scenario), the user asks Claude Code to "refactor this legacy code." The code spans 50 files. How should this be decomposed?

A) Refactor everything in a single agent turn
B) Use Plan Mode to assess scope, then decompose into task-based subagents that refactor components in parallel with cross-phase scratchpad persistence
C) Refactor files one at a time sequentially
D) Ask the user to refactor manually

---

**Q36.** A Claude Code for CI/CD workflow (exam scenario) validates deployment configurations before provisioning. If validation fails, the pipeline must halt immediately. How is this safety guaranteed?

A) Return stop_reason: "end_turn" and rely on pipeline to check status
B) Use structured error response with isRetryable: false to signal pipeline halt; respect this signal downstream
C) Log errors and continue anyway
D) Manual approval gates after each step

---

**Q37.** In a Structured Data Extraction workflow (exam scenario), you're extracting facts from 200-page legal documents. Some documents exceed token limits. What strategy handles this efficiently?

A) Process only the first 100 pages
B) Use multiple passes with scratchpad files tracking extracted facts, implementing cross-phase persistence with stratified accuracy analysis
C) Reject documents exceeding limits
D) Use Batch API without consideration for chunking

---

**Q38.** When configuring .mcp.json for external tool integration in a distributed system, database credentials must not be hardcoded. How should this be handled?

A) Hard-code all credentials in the JSON
B) Use `${ENV_VAR}` expansion for sensitive values like `"password": "${DB_PASSWORD}"`
C) Store credentials in tool descriptions
D) Rely on OS-level environment variable access without MCP configuration

---

**Q39.** Your agent produces analysis that references specific facts from source materials. You need to prove which sources support which claims for compliance purposes. What structure enables this audit trail?

A) Store all sources in a single list
B) Implement claim-source provenance mappings: each claim tagged with source reference and extraction method
C) Assume sources are obvious from context
D) Don't track sources; focus on accuracy

---

**Q40.** A research agent reviews its own extracted findings for accuracy before reporting. What is the critical limitation of this approach?

A) It's redundant; findings are already accurate
B) Self-review limitation: the same instance cannot reliably verify its own work; use separate instances for extraction and review
C) It takes too long
D) It requires additional API calls

---

**Q41.** When managing context in long-running agent workflows, you notice token usage grows and performance degrades. You've added a PostToolUse hook for context trimming. What should this hook validate?

A) Only trim very old context (oldest-first)
B) Implement business rule enforcement AND context trimming; validate that important context is preserved while removing redundancy
C) Never trim context
D) Use Lost in the Middle strategy only

---

**Q42.** In your agent configuration, you've set tool_choice: "forced" for a critical operation. What does this enforce?

A) The agent must call at least one tool
B) The agent MUST call exactly one tool and cannot refuse or generate text without tool use
C) The agent can freely choose tools
D) Tool use is disabled

---

**Q43.** A skill within Claude Code needs to inherit the parent workflow's conversation context. How is this configured?

A) Create a brand new session with no context
B) Use context: fork to inherit parent context in the skill definition
C) Manually pass context as parameters
D) Skills automatically get full context without configuration

---

**Q44.** Your structured extraction pipeline shows high accuracy in phase 1 but inconsistent results in phase 2 validation. You suspect the validation model sees results in isolation without original document context. What should you preserve between phases?

A) Only store extracted facts
B) Use scratchpad files containing extracted facts, original document snippets, and confidence scores for cross-phase persistence
C) Re-process entire document in phase 2
D) Trust phase 1 results entirely

---

**Q45.** When a customer escalates with an explicit request ("I need to speak to a human"), your agent should:

A) Ignore the request per standard protocol
B) Honor explicit escalation requests and immediately route to human agents without continued automation
C) Attempt to resolve the issue first, then escalate
D) Ask the customer to confirm escalation request

---

**Q46.** In your MCP tool selection design, you want Claude to select tools primarily based on what factor?

A) Tool names only
B) Tool descriptions: use clear, detailed descriptions as the primary mechanism for tool selection
C) Tool parameter count
D) Random selection

---

**Q47.** A code validation tool returns errorCategory: "validation_failed" with isRetryable: true. What should the agent do?

A) Give up immediately
B) Implement a retry-with-error-feedback loop: modify the input/approach based on error details and retry
C) Report error to user without retry
D) Escalate to human

---

**Q48.** Your agent operates in Plan Mode for a complex architectural decision. What is the primary benefit of this approach?

A) Faster execution
B) Clarifies the decomposition strategy before execution, reducing errors in multi-step tasks
C) Lower token usage
D) Automatic parallelization

---

**Q49.** A customer support agent uses multiple tools to resolve issues. You notice it sometimes doesn't use the most relevant tool first. How should this be optimized?

A) Remove less relevant tools
B) Improve tool descriptions and order them by relevance; leverage tool descriptions as the primary selection mechanism
C) Specify tool_choice: "forced" for each tool
D) Manually choose tools for the agent

---

**Q50.** When implementing a fork_session within a skill, what context should the forked session have access to?

A) No context from parent
B) Selective context: use context: fork parameter to inherit parent context appropriately
C) All context from parent automatically
D) Only the current message

---

**Q51.** Your extraction pipeline needs confidence scores for each extracted fact. Before returning to users, facts with confidence < 0.7 should trigger a validation pass. Which pattern implements this?

A) Extract once and report all findings
B) Implement stratified accuracy analysis with separate validation pass for low-confidence facts, using scratchpad persistence to track confidence scores
C) Manually review all findings
D) Discard low-confidence findings silently

---

**Q52.** In a multi-step workflow using Claude Code, you're concerned about lost context when documents are processed across multiple passes. What strategy preserves important information?

A) Hope the model remembers context
B) Use scratchpad files as persistent storage across phases; track key facts, decisions, and references that feed into subsequent phases
C) Process everything in a single pass
D) Store context only in memory

---

**Q53.** Your agent's error handling returns structured errors with isRetryable and errorCategory. A downstream system receives a non-retryable error. What should it do?

A) Retry anyway
B) Respect the non-retryable designation and escalate or fail gracefully without automatic retry
C) Log and ignore
D) Assume all errors are transient

---

**Q54.** When configuring the Batch API for processing 10,000 extraction requests, what is the CRITICAL processing window constraint you must plan for?

A) Results arrive within 1 hour
B) 24-hour window: requests must be submitted and completed within 24 hours
C) Results are immediate
D) No time constraint

---

**Q55.** In your CLAUDE.md configuration hierarchy, you have conflicting rules at the user level and project level. Which takes precedence according to the architecture?

A) User level always wins
B) Most specific location wins: project level > user level
C) They merge with project level override
D) Tool-level settings override both

---

**Q56.** A research agent classifies documents by confidence level. You want to validate the classification against human judgment. What is the safest approach?

A) Trust the agent's classification
B) Use separate instances: one instance classifies, another instance independently reviews classifications to catch systematic biases
C) Have the agent review its own work
D) Spot-check only 10% of classifications

---

**Q57.** Your agent uses tools that sometimes fail transiently (network timeout, rate limit) and sometimes permanently (invalid input). How should the tool responses differ?

A) Return the same error for both cases
B) Return structured error with errorCategory and isRetryable: true for transient; errorCategory and isRetryable: false for permanent failures
C) Don't distinguish error types
D) Always retry

---

**Q58.** A DevOps engineer uses Claude Code to manage infrastructure as code (CI/CD scenario). The validation step must not proceed to provisioning if security checks fail. This is implemented via structured error with isRetryable: false. How does the downstream CI/CD system handle this?

A) Ignore the error and continue
B) Respect the isRetryable: false signal and halt pipeline without proceeding to provisioning
C) Automatically retry
D) Log and continue anyway

---

**Q59.** Your multi-agent system requires agents to work in parallel on independent subagents of a complex problem. Each Task call should execute in its own context. How is this configured?

A) Call tasks sequentially
B) Use multiple Task tool calls within a single agent turn to invoke subagents in parallel with independent execution
C) Create separate agents manually
D) Use fork_session for each task

---

**Q60.** When implementing a customer support chatbot with escalation capability, explicit user requests to speak with humans should be handled how?

A) Deny escalation if the issue seems solvable
B) Honor explicit escalation requests immediately regardless of issue solvability
C) Offer automated solutions first, then escalate
D) Log the request for later review

---

**Q61.** A code generation tool in Claude Code produces functions without docstrings. You want to enforce this requirement without rebuilding the entire workflow. What is the most efficient gate?

A) Use a PostToolUse hook to validate docstrings and trigger retry-with-error-feedback if missing
B) Ask Claude to "remember to add docstrings"
C) Manually add docstrings after generation
D) Ignore the requirement

---

**Q62.** Your agent processes sensitive data and must maintain an audit trail of which sources provided which facts. This is critical for compliance. What structure enables this audit trail?

A) Store all facts in one list
B) Implement claim-source provenance mappings: tag each fact with source URL, extraction timestamp, and confidence score
C) Keep sources separate from facts
D) Don't track sources

---

**Q63.** When using Grep built-in tool in Claude Code to search a large codebase, what is the primary advantage over Read?

A) Grep can read entire files; Read cannot
B) Grep efficiently searches by pattern without loading entire files; provides focused results
C) Read is more efficient
D) They're equivalent

---

**Q64.** In a complex agent workflow, you implement context trimming via PostToolUse hook to manage token usage. What must this hook preserve while trimming?

A) Everything (don't trim)
B) All messages equally
C) Recent messages only
D) Critical context needed for current and future turns while removing redundancy and low-value information

---

**Q65.** Your structured extraction workflow processes documents with varying complexity. Simple documents extract cleanly, but complex documents show inconsistencies. What analysis would help identify the root cause?

A) Process more documents
B) Use stratified accuracy analysis: partition documents by complexity and analyze accuracy per stratum to identify complexity-related issues
C) Assume all documents are equally complex
D) Increase token limits

---

**Q66.** A skill within Claude Code receives `fork_session` as its execution model. What about the parent's context is inherited by default?

A) No context
B) Everything automatically, with context: fork parameter enabling explicit control over what is inherited
C) Only tool definitions
D) Nothing; skills are isolated

---

**Q67.** When your agent encounters a tool response with `errorCategory: "rate_limit"` and `isRetryable: true`, what is the appropriate immediate action?

A) Give up immediately
B) Implement exponential backoff retry logic; feed error details back and re-attempt the tool call
C) Manually handle rate limiting
D) Escalate to human

---

**Q68.** Your research team uses Claude to extract findings from 50 papers. Each finding must cite its source document. How should you structure this to ensure provenance is captured?

A) Extract all findings without source tracking
B) Implement claim-source provenance mappings: each finding tagged with source paper ID, page number, and exact quote
C) Manual source tracking after extraction
D) Trust that sources are implied

---

**Q69.** When managing long workflows in Claude Code, you notice the Lost in the Middle effect where important instructions in the middle of context are sometimes ignored. What mitigation should you employ?

A) Put all critical information at the end
B) Use strategic context placement, scratchpad files for persistence, and explicit emphasis on critical facts through system prompts and examples
C) Accept lost context as inevitable
D) Reduce context window

---

**Q70.** A tool in your agent system can fail due to various reasons. To enable proper error handling downstream, your tool must return structured errors with specific fields. Which fields are essential for robust retry logic?

A) Just an error message string
B) errorCategory (identifies error type) and isRetryable (true/false) to enable informed retry decisions
C) Only error code numbers
D) Exception stack traces

---

**Q71.** Your customer support agent sometimes provides incomplete answers due to token constraints. You implement a PostToolUse hook that checks response completeness and triggers retry when needed. What is this pattern called?

A) Silent error suppression
B) Retry-with-error-feedback: identify insufficiency, provide specific feedback, and re-attempt
C) Forced tool_choice
D) Context trimming

---

**Q72.** In a CI/CD pipeline using Claude Code, the `-p` flag is used for what purpose?

A) Parallel execution
B) Persistent mode
C) Plan mode: allows Claude to assess decomposition strategy before execution
D) Priority processing

---

**Q73.** When using Glob in Claude Code to find all Python files in a deeply nested directory, how does Glob differ from manually iterating and opening files?

A) Glob can't handle deep nesting
B) Glob efficiently returns file paths matching patterns without opening files, saving tokens and I/O
C) They're identical
D) Glob is slower

---

**Q74.** Your agent's workflow shows high token usage that scales poorly with input size. You've implemented context trimming but it's not sufficient. What additional optimization targets PostToolUse hooks?

A) Remove all context
B) Implement business rule enforcement alongside trimming: enforce data validation, normalization, and enrichment to reduce redundant future processing
C) Disable context trimming
D) Use Batch API only

---

**Q75.** A production agent must handle failures gracefully and never silently drop errors. You've noticed some tool errors are logged but not acted upon. What anti-pattern is this?

A) Proper error handling
B) Silent error suppression: errors are caught but not surfaced for handling; implement explicit error propagation
C) Necessary for stability
D) Batch API limitation

---

**Q76.** Your multi-agent system uses Task tool calls to invoke subagents. Each subagent requires a specific set of tools. How should this be configured to ensure isolation?

A) All agents share a global allowedTools list
B) Define domain-specific allowedTools per subagent; include Task in parent's allowedTools for subagent invocation
C) Subagents auto-discover all available tools
D) No configuration needed

---

**Q77.** In implementing end-to-end agent workflows, you want to batch-process 500 documents for extraction and analysis with non-urgent completion within 24 hours. What API approach optimizes cost?

A) Standard API with immediate processing
B) Batch API: 50% cost reduction with 24-hour processing window suitable for non-time-sensitive bulk workloads
C) Custom infrastructure
D) Real-time API with priority processing
