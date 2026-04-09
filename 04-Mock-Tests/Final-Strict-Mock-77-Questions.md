# Claude Certified Architect - Foundations: Final Strict Mock 77

> 77 original questions | 4-scenario simulation | Merges the strongest coverage from Strict Mock Test 1 and Strict Mock Test 2

## Alignment Notes
- Built to mirror the public guide's exam constraints: multiple choice, 1 correct answer out of 4, 4 scenarios selected from the published pool, and coverage across all 5 domains
- Scenario set used in this simulation:
  - Customer Support Agent
  - Multi-Agent Research System
  - Code Generation with Claude Code
  - Structured Data Extraction
- Domain coverage is weighted to approximate the public blueprint while also pulling in the previously undercovered guide topics from Strict Mock Test 2

## Instructions
- Select the BEST answer for each question
- One correct answer per question
- There is no guessing penalty

---

## Scenario 1: Customer Support Agent

**Q1.** Your support agent receives a response with `stop_reason: "tool_use"` after asking Claude how to handle a return request. What should the application do next?

A) Stop and show the tool call as the final answer
B) Execute the requested tool, append the result, and continue the loop
C) Start a new session before running the tool
D) Retry the model call with tools disabled

---

**Q2.** A customer writes, "I want a human, not a bot." What is the correct response pattern?

A) Try one more automated resolution attempt first
B) Honor the explicit request and escalate immediately
C) Continue if the model is highly confident
D) Ask the customer to explain the issue in more detail before escalating

---

**Q3.** Your refund workflow must never call `process_refund` before `get_customer` returns a verified identifier. What is the most reliable enforcement mechanism?

A) A programmatic precondition or hook that blocks the downstream tool call
B) A stronger system prompt telling Claude to behave carefully
C) A few-shot example showing the correct sequence once
D) A larger `max_tokens` value so Claude can plan better

---

**Q4.** Users asking about order status are often routed to `get_customer` instead of `lookup_order`. The tool descriptions are short and similar. What should you fix first?

A) Add sentiment analysis before tool choice
B) Expand the tool descriptions with inputs, examples, and boundaries
C) Merge both tools into one `lookup_entity` tool
D) Force `lookup_order` for every support request

---

**Q5.** Customers sometimes send one message containing a refund request, an address update, and a billing question. What architecture is most likely to improve reliability?

A) Handle only the first issue and ask the user to send the rest separately
B) Combine all related tools into a single universal support tool
C) Decompose the message into distinct items and resolve them separately before synthesizing the answer
D) Increase temperature so Claude explores more ways to route the request

---

**Q6.** Your `get_customer` tool returns three possible matches for a name search. What should the agent do before taking account-specific action?

A) Choose the customer with the most recent order
B) Ask for an additional identifier such as email, phone, or order number
C) Retry the same tool call with the same name
D) Escalate immediately without asking follow-up questions

---

**Q7.** A customer asks for a competitor price match, but company policy only covers price drops on your own site and says nothing about competitors. What should the agent do?

A) Deny the request automatically because it is not explicitly allowed
B) Approximate a discount using the internal policy threshold
C) Escalate because the request falls into a policy gap
D) Offer store credit as a generic fallback

---

**Q8.** Your support agent currently has 18 tools, including several that belong to fraud review, shipping operations, and finance. Tool misuse keeps increasing. What is the best fix?

A) Give the agent even more tools so it can compare alternatives better
B) Restrict the agent to a smaller, role-relevant toolset
C) Rename all tools to shorter names
D) Force a tool call on every turn

---

**Q9.** The agent escalates many simple cases and attempts policy exceptions autonomously. Which prompt change is the most proportional first fix?

A) Add explicit escalation criteria with few-shot examples
B) Ask Claude to self-rate confidence from 1 to 10
C) Use sentiment analysis to detect difficult customers
D) Replace the agent with a batch workflow

---

**Q10.** Some support tools return Unix timestamps, others return ISO 8601 strings, and others numeric status codes. What is the cleanest way to normalize them before reasoning?

A) Explain all formats in the system prompt and hope Claude remembers them
B) Use a PostToolUse hook to normalize the outputs
C) Ask the user to interpret the timestamps manually
D) Convert every tool output into prose after the model responds

---

**Q11.** A billing tool can fail because of timeouts, invalid invoice IDs, permission issues, or policy restrictions. Which response shape best supports recovery?

A) A plain string saying "Operation failed"
B) A stack trace with no classification
C) Structured errors with categories and retryability metadata
D) An empty result marked as success

---

**Q12.** Claude answers the first item in a support queue and returns `stop_reason: "end_turn"`. You append the next item and nothing happens automatically. What does that usually mean?

A) The session is invalid and must be recreated
B) Claude completed its turn; your application must explicitly continue with the next turn
C) A tool was required but blocked by the API
D) The conversation exceeded the context limit

---

**Q13.** A human escalation handoff should be self-contained because the human will not see the full transcript. Which content is most important?

A) Only the customer's emotional tone and the latest message
B) Only the root cause, because the rest can be inferred
C) The full raw transcript with no summary
D) Customer identity, issue summary, actions taken, current state, and recommended next action

---

**Q14.** You improved tool descriptions, but ambiguous requests like "help with my recent purchase" still misroute. Which prompting technique is most likely to help next?

A) Add targeted few-shot examples for ambiguous cases with rationale
B) Add ten examples for only the easiest cases
C) Increase temperature so the model explores more routes
D) Remove all tool descriptions and rely only on examples

---

**Q15.** A customer first sounds frustrated but does not explicitly request a human. Later they say, "No, I want a manager." What should happen at that point?

A) Continue automation because frustration alone should not change the route
B) Escalate immediately because the explicit request overrides continued automation
C) Ask the customer whether they really mean it
D) Return a policy summary and wait for another message

---

**Q16.** Production data shows Claude often requests `get_customer` and `lookup_order` in separate sequential turns even when both are needed. What low-overhead change is best to reduce loops?

A) Switch to Batch API for all support flows
B) Force only one tool call per turn
C) Remove `lookup_order` from the tool list
D) Instruct Claude to bundle related tool requests into a single turn when possible

---

**Q17.** Refunds above $500 require a guaranteed escalation path for compliance reasons. Which approach should you prefer?

A) A deterministic hook or precondition that blocks high-value refunds
B) A system prompt that says "always escalate large refunds"
C) A few-shot example with one large refund case
D) A higher-capability model with extended thinking

---

**Q18.** Which of the following is NOT a reliable primary escalation trigger by itself?

A) An explicit request to talk to a human
B) A policy exception or policy gap
C) Sentiment analysis showing the customer is angry
D) Inability to make progress after reasonable attempts

---

**Q19.** Basic-tier users should never see enterprise-only support tools. What is the most scalable mechanism?

A) Tell Claude in the prompt to ignore enterprise tools for Basic customers
B) Filter allowed tools programmatically by tier before each turn
C) Rename enterprise tools so they are less attractive to the model
D) Put enterprise tool rules in a README

---

## Scenario 2: Multi-Agent Research System

**Q20.** Why is coordinator-centered communication the standard hub-and-spoke pattern in a multi-agent research system?

A) It minimizes model token usage to zero
B) It gives one agent visibility into routing, errors, and aggregation decisions
C) It makes all subagents share the same memory automatically
D) It eliminates the need for structured outputs

---

**Q21.** A coordinator needs three independent subagents to work at the same time on separate research strands. What should the coordinator do?

A) Issue multiple Task calls in one turn with explicit context for each subagent
B) Ask one subagent to call the other two directly
C) Use one giant prompt containing all three subtasks
D) Switch the whole workflow to a resumed session first

---

**Q22.** Two credible sources report different figures for the same metric. What should the analysis agent do?

A) Pick the more recent figure and drop the older one
B) Average the figures into one compromise number
C) Escalate immediately and halt all work
D) Preserve both values with attribution and mark the conflict explicitly

---

**Q23.** A document-analysis subagent times out after parsing half a document. What is the best error propagation behavior?

A) Return structured failure context, including the attempted action and any partial results
B) Return an empty success response so the coordinator can keep moving
C) Throw an exception that terminates the whole workflow
D) Retry forever until it works

---

**Q24.** A web research tool is named `analyze_content` and a document-analysis tool is named `analyze_document`. Misrouting remains high. What is the most direct fix?

A) Add more tools so the coordinator has more choices
B) Rename the overlapping tool to something purpose-specific and rewrite its description
C) Force document analysis first for all research requests
D) Move both tools into the same subagent

---

**Q25.** A report on "AI in creative industries" only covers visual arts because the coordinator delegated "digital art," "graphic design," and "photography" subtasks. What is the root cause?

A) The synthesis agent is failing to merge results correctly
B) The web-search agent did not search deeply enough
C) The coordinator decomposed the task too narrowly
D) The context window was too small to include music and film

---

**Q26.** The synthesis agent often needs simple fact checks like dates and names. What is the best least-privilege design?

A) Give it a limited-scope verification tool for simple checks while keeping deeper research with the coordinator
B) Give it the full web-search toolset used by the research agent
C) Ban all verification during synthesis
D) Force it to restart synthesis every time verification is needed

---

**Q27.** A web-search subagent reports one source category as "0 results" and another as "connection timeout." Why should the coordinator treat these differently?

A) Both are identical failures and should trigger the same retry policy
B) A timeout means the query was semantically wrong, while 0 results means no permission
C) A timeout is an access failure; 0 results may be a valid outcome
D) 0 results always means the search tool is broken

---

**Q28.** Aggregated research input is long, and the synthesis agent misses important mid-stream findings. What restructuring helps most?

A) Put a key-findings summary at the top and organize detailed results with explicit sections
B) Put all detailed results first and the summary last
C) Randomize the order of agent outputs across runs
D) Remove all headings so the model reads naturally

---

**Q29.** Upstream agents return bulky reasoning traces and full pages, making synthesis slow and unstable. What change addresses the problem closest to the source?

A) Require upstream agents to return structured facts, quotes, and relevance rather than full verbose dumps
B) Add a larger synthesis model so it can absorb everything
C) Run synthesis three times and vote on the result
D) Append all outputs into a scratchpad without filtering

---

**Q30.** Web-search and document-analysis agents frequently duplicate effort by researching the same subtopics. What should the coordinator do?

A) Partition the research space before delegation
B) Let both agents run freely and deduplicate only at the end
C) Force sequential execution to reduce overlap
D) Give both agents a shared scratchpad and hope they coordinate implicitly

---

**Q31.** A synthesis agent keeps misusing a general-purpose `fetch_url` tool for ad hoc search. What design principle is being violated?

A) The synthesis agent has too little context
B) The agent has broader tools than its role requires
C) The batch window is too long
D) The system prompt is too short

---

**Q32.** When a subagent experiences a transient failure, what is the preferred recovery pattern?

A) Abort the workflow immediately
B) Return a generic failure string to the coordinator
C) Retry internally forever and never report the failure
D) Attempt limited local recovery, then propagate structured context if unresolved

---

**Q33.** Your final report must clearly distinguish stable findings from disputed ones. What structure best supports that?

A) One seamless narrative that hides disagreements
B) A table of numbers only
C) A report that separates confirmed conclusions from disputed findings with attribution
D) A conclusion section with no citations

---

**Q34.** A subagent is asked to "analyze the document" with no other context. Why is this risky?

A) Subagents automatically inherit too much parent context
B) The tool_choice parameter will be ignored
C) Subagents do not inherit needed context unless it is explicitly passed
D) The coordinator cannot receive any result from a subagent without a scratchpad file

---

**Q35.** A resumed research session contains old search results, but the sources and repository changed materially overnight. What is often the better choice?

A) Keep resuming until the model notices the drift
B) Start a fresh session with a structured summary of verified prior findings
C) Delete the task history and continue from memory only
D) Force the same synthesis step again without updating context

---

**Q36.** What is `fork_session` best for in a research workflow?

A) Replacing Task-based subagents completely
B) Creating independent investigation branches from shared context
C) Guaranteeing lower latency for synthesis
D) Persisting project rules across repositories

---

**Q37.** What is the key risk when using `--resume` carelessly in a changed research environment?

A) Tool definitions are deleted from the session
B) Previously gathered tool results may be stale relative to current reality
C) The model loses the ability to cite sources
D) Resume forces batch processing mode

---

**Q38.** You are tackling an open-ended investigation where each new finding changes what should be explored next. What decomposition style fits best?

A) A fixed pipeline with identical steps every time
B) Dynamic adaptive decomposition based on intermediate results
C) One-pass synthesis over all available context
D) Batch processing with no retries

---

## Scenario 3: Code Generation with Claude Code

**Q39.** Three developers say Claude follows an instruction, but a new teammate in the same repository does not get it. What is the most likely cause?

A) The instruction lives in user-level CLAUDE.md instead of project-level configuration
B) The teammate is using the wrong model family
C) CLAUDE.md only works after manual indexing
D) The teammate needs to clear a hidden Claude cache

---

**Q40.** Your root CLAUDE.md is becoming unwieldy. You want to split guidance into maintained files while keeping a single project entry point. What feature supports that directly?

A) `.mcp.json` environment substitution
B) `@path` imports in CLAUDE.md
C) `tool_choice: any`
D) `/compact`

---

**Q41.** Tests are spread throughout the repo, and you want shared test conventions to load only when editing test files. What is the best setup?

A) A directory-level CLAUDE.md in the repository root
B) `.claude/rules/` files with YAML frontmatter `paths` patterns
C) A README section describing testing standards
D) A personal skill under `~/.claude/skills/`

---

**Q42.** When should path-scoped `.claude/rules/` files usually be preferred over directory-level CLAUDE.md?

A) When conventions apply across many directories by file type or pattern
B) Only when the repo has no subdirectories
C) Only when the work is happening in CI
D) Never; directory CLAUDE.md is always simpler and better

---

**Q43.** Your team wants a shared `/review` command available to everyone who clones the repository. Where should it live?

A) In `.claude/commands/` inside the project
B) In `~/.claude/commands/` for each developer
C) In the root README
D) In `.mcp.json`

---

**Q44.** A skill produces lots of verbose exploration output and pollutes the main session. Which frontmatter setting best isolates that work?

A) `model: haiku`
B) `argument-hint: ...`
C) `context: fork`
D) `temperature: 0`

---

**Q45.** Developers often run a migration skill without passing a migration name. What frontmatter feature is designed to improve that?

A) `allowed-tools`
B) `argument-hint`
C) `context: root`
D) `paths`

---

**Q46.** You need to restructure a legacy service touching 50 files with multiple plausible implementation strategies. What is the correct first mode?

A) Planning mode
B) Direct execution
C) Headless print mode
D) Batch mode

---

**Q47.** You have a single-file fix with a clear stack trace and a known root cause. What is the better execution mode?

A) Planning mode because it is always safer
B) Direct execution because the change is simple and well-bounded
C) Batch processing because it is cheaper
D) A resumed session from a prior unrelated task

---

**Q48.** Your CI job hangs because Claude Code waits for interactive input. What flag should the job use?

A) `--compact`
B) `--resume`
C) `--strict`
D) `-p`

---

**Q49.** You want PR review findings as machine-readable JSON with file path, line, severity, and fix. What is the best CLI configuration?

A) `--output-format json` with `--json-schema`
B) A long prose prompt that asks for valid JSON
C) Only `--output-format json`
D) A project README with an example JSON block

---

**Q50.** You rerun automated review after new commits and want only new or unresolved findings. What should you include in the next run?

A) Nothing from the prior review; the model should start clean
B) Only the latest commit diff, excluding all prior context
C) Prior review findings in context and an instruction to report only new or still-open issues
D) A lower temperature so the same comments repeat consistently

---

**Q51.** Full endpoint examples improve generation quality, but only when creating endpoints, not for debugging or review. What is the best way to load them on demand?

A) Put them in root CLAUDE.md so they are always active
B) Create a generation-focused skill that loads the examples only when invoked
C) Put them in `.mcp.json`
D) Paste them into every prompt manually

---

**Q52.** Your team wants a shared GitHub MCP server configuration without committing credentials. What is the preferred setup?

A) Store personal tokens directly in `.mcp.json`
B) Use a wrapper script that hardcodes the token and commit it for everyone
C) Put the server only in each user's personal config and avoid project setup entirely
D) Put the server in project `.mcp.json` and reference credentials via environment variables

---

**Q53.** A developer wants project conventions to persist across sessions without repeating them manually each time. Which built-in Claude Code command is explicitly associated with managing that persisted memory or instruction surface?

A) `/compact`
B) `/memory`
C) `/resume`
D) `/rules`

---

**Q54.** You used Grep to find a likely configuration file and now need to inspect its full contents. Which built-in tool is the correct next step?

A) Write
B) Read
C) Edit
D) Bash

---

**Q55.** Edit fails because the target text appears in multiple places and the match is not unique. What is the recommended fallback?

A) Retry Edit until it picks one deterministically
B) Read the full file, modify the content, then Write the updated file
C) Switch to Glob because file matching is more reliable than text matching
D) Remove the duplicate blocks first and retry later

---

**Q56.** What is the main tradeoff of using `/compact` in very long Claude Code sessions?

A) It disables tools after compaction
B) It can compress away precise details like dates, percentages, and exact values
C) It forces the model into headless mode
D) It writes to project memory automatically

---

**Q57.** Discovery across a 120-file codebase is filling the main context before design and implementation begin. What is the most effective fix?

A) Use an Explore-style subagent to isolate verbose discovery and return a concise summary
B) Increase context size and keep discovery in the main thread
C) Disable file-reading tools until implementation starts
D) Use `/memory` to store every file verbatim

---

## Scenario 4: Structured Data Extraction

**Q58.** A field is not always present in source documents. How should you model it in a schema to reduce hallucinated values?

A) Mark it required anyway so the model always fills it
B) Omit it from the schema completely
C) Make it optional or nullable when absence is legitimate
D) Convert it to free-form prose outside the schema

---

**Q59.** Your category list is mostly known, but some values will not fit the predefined enum. What is the best schema design?

A) Use a strict enum with no fallback values
B) Add `other` or `unclear` plus a detail field when needed
C) Make the category field an unbounded paragraph
D) Remove validation so the model can improvise

---

**Q60.** What do strict JSON-schema-based tool calls prevent most directly?

A) Semantic errors like wrong totals
B) Conflicting interpretations across documents
C) JSON syntax and shape violations
D) Model bias in source selection

---

**Q61.** You want the pipeline to detect internal contradictions in invoice extraction. Which design best supports that?

A) Extract only the stated total and trust it
B) Extract both `stated_total` and `calculated_total` and compare them
C) Remove totals from the schema to avoid mismatch
D) Use only few-shot examples without validation

---

**Q62.** Extracted line items do not add up to the stated total. What is the best next step?

A) Accept the mismatch if the rest of the record looks correct
B) Retry with explicit validation feedback and the original document context
C) Delete the total field from the result
D) Switch to a weaker model so it generalizes more freely

---

**Q63.** When is retry-with-feedback least likely to help?

A) When a date format is wrong
B) When a field is placed in the wrong part of the structure
C) When the required information simply is not present in the source
D) When a sum does not reconcile

---

**Q64.** You have 10,000 invoices to process overnight and no need for immediate answers. Why is the Message Batches API appropriate?

A) It supports lower-cost asynchronous processing for non-urgent workloads
B) It guarantees interactive latency under one second
C) It automatically solves all validation errors inside the batch
D) It eliminates the need for correlation IDs

---

**Q65.** What does the guide emphasize about the Message Batches API processing window?

A) It provides a strict low-latency SLA for all batch jobs
B) It can take up to 24 hours and should be planned against deadlines accordingly
C) It always finishes in less than five minutes
D) It only matters when using Opus models

---

**Q66.** A team wants to use batch processing for a workflow that depends on Claude requesting a tool, receiving the tool result, and then continuing analysis in the same logical interaction. What is the correct conclusion?

A) Batch processing is ideal because it supports tool loops more cheaply
B) Batch processing is incompatible with that workflow shape
C) Batch processing works if you add `strict: true`
D) Batch processing works only if you remove `custom_id`

---

**Q67.** Before finalizing an extraction schema for a new contract family, Claude asks about missing fields, conflict resolution, and which uncertainties must trigger review. Which prompt pattern is this?

A) Lost-in-the-middle mitigation
B) Interview pattern
C) Coverage annotation
D) Batch decomposition

---

**Q68.** Some extracted fields are low-confidence and could affect legal or financial decisions. What is the safest routing choice?

A) Accept all low-confidence outputs if the JSON is valid
B) Route low-confidence high-impact fields to validation or human review
C) Delete confidence values from the output
D) Retry the same prompt until confidence rises above a threshold

---

**Q69.** You have multiple extraction tools and need guaranteed structured output, but the model should still choose the best extraction tool itself. Which `tool_choice` setting fits?

A) `auto`
B) `any`
C) `none`
D) Omit tools entirely

---

**Q70.** You want tool calls to conform exactly to the declared schema whenever Claude invokes a client tool. What setting improves that most directly?

A) `strict: true`
B) `max_tokens: 1`
C) `temperature: 1`
D) `context: fork`

---

**Q71.** Two extraction tools overlap too much: one is for OCR snippets and one is for structured document sections, but both are vaguely described as "extracts data." What is the best fix?

A) Add more overlapping tools
B) Rewrite descriptions to make purpose and boundaries distinct
C) Force the first tool for all documents
D) Remove schemas from both tools

---

**Q72.** You want the model to see a document-type catalog and field reference tables without taking any action. Which MCP component is designed for that?

A) Tools
B) Resources
C) Prompts
D) Sessions

---

**Q73.** You want reusable extraction kickoff templates for common jobs like invoice review or contract analysis. What are MCP prompts intended for?

A) Persistent long-term memory across sessions
B) Predefined prompt templates for common tasks
C) Replacing JSON schemas in tools
D) Forcing tool visibility rules by tier

---

**Q74.** Your extraction pipeline always follows the same stages: metadata extraction, field extraction, validation, enrichment, final output. What decomposition style is this?

A) Dynamic adaptive decomposition
B) Fixed pipeline or prompt chaining
C) Context-free summarization
D) Human-only review

---

**Q75.** An extraction workflow begins by mapping the document set, then decides whether to chunk by section, by annex, or by table based on what it finds. What decomposition style is this?

A) Fixed pipeline
B) Direct execution only
C) Dynamic adaptive decomposition
D) Forced one-shot prompting

---

**Q76.** You split long contracts into chunk-level extraction subagents. What must the coordinator include in each subagent prompt?

A) Explicit chunk context and relevant document metadata, because subagents do not inherit parent context automatically
B) Only the raw chunk text, because metadata biases the model
C) Nothing beyond the tool name, because the coordinator session is shared
D) A request to infer missing context from neighboring chunks

---

**Q77.** You split a long document into chunks handled by separate extraction subagents. What is the coordinator's best role?

A) Let subagents communicate directly and merge their own outputs
B) Aggregate structured chunk outputs, preserve attribution, and coordinate the final synthesis
C) Remove chunk boundaries before sending anything to synthesis
D) Skip explicit context passing because all chunk agents share the same task