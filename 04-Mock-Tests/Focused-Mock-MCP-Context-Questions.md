# Claude Certified Architect - Focused Mock: MCP and Reliability

> 24 original questions | Focus domains: Tool Design & MCP Integration, Context Management & Reliability

## Instructions
- Select the BEST answer for each question
- This focused mock concentrates on two weak areas: MCP/tool design and context/reliability
- Scenarios are intentionally varied while testing the same underlying principles

---

## Questions

**Q1.** Two MCP tools are named `analyze_data` and `process_data`, and Claude keeps choosing the wrong one. What change is most likely to improve tool routing?

A) Increase temperature so Claude explores alternatives
B) Replace vague names and descriptions with clearly differentiated purpose-specific ones
C) Hide one tool from Claude at random each turn
D) Put both tools behind a single wrapper tool

---

**Q2.** A tool returns an authentication failure because the API key is invalid. How should this error generally be marked?

A) Retryable, because all network-connected tools should be retried first
B) Non-retryable, because the input credentials must change before retrying
C) Retryable only if the model is confident
D) Silent, because auth failures confuse the agent

---

**Q3.** Your MCP tool descriptions are excellent, but a system prompt says, "Always use web_search first when in doubt." What risk does that create?

A) It can override otherwise good tool selection behavior with a blunt heuristic
B) It guarantees correct tool use because system prompts always improve routing
C) It disables all server-side tools automatically
D) It removes the need for allowedTools filtering

---

**Q4.** A tool validation error says a required field is missing from the input. What is the best recovery pattern?

A) Retry with error feedback after correcting the missing field
B) Retry the exact same call three times without changes
C) Mark the tool as unreliable and remove it entirely
D) Convert the validation error into a success response

---

**Q5.** An internal support tool should only be exposed to Enterprise-tier customers, while its description remains unchanged. Where should that control live?

A) In the MCP server's tool listing/filtering logic
B) In the answer key for the mock exam
C) In the end-user prompt only
D) In the tool name itself by prefixing it with `enterprise_`

---

**Q6.** What is the strongest reason to prefer specialized tools over one giant generic tool?

A) Specialized tools create clearer selection boundaries and reduce ambiguity
B) Generic tools are incompatible with Claude
C) Specialized tools always execute faster at runtime
D) Generic tools cannot accept JSON input

---

**Q7.** A tool fails because the upstream service timed out. Which structured error metadata is most useful?

A) `errorCategory` plus `isRetryable: true`
B) A stack trace only
C) A note saying "something went wrong"
D) No error metadata, just an empty result

---

**Q8.** A large extraction workflow keeps losing important facts between phases. What is the best mitigation?

A) Ask the model to remember better
B) Use scratchpad persistence for extracted facts and key evidence
C) Lower the max token count so responses are shorter
D) Use only one pass, even if the document is too large

---

**Q9.** Why is self-review a weak verification strategy for extracted claims?

A) The same instance tends to anchor on and defend its previous reasoning
B) Claude cannot read earlier tool results
C) Self-review only works in VS Code, not in the API
D) Verification requires Batch API specifically

---

**Q10.** A long-running customer workflow is approaching context limits. Which information is most important to preserve during summarization?

A) Every exploratory thought the agent ever produced
B) Root decisions, current state, constraints, and unresolved issues
C) Only the very first user message
D) Only the last tool result

---

**Q11.** You want consistent timestamps, status fields, and provenance metadata across tool outputs before Claude reasons over them. Where should you do this?

A) In PostToolUse normalization hooks
B) In the user prompt after the tool finishes
C) In a README file for the repository
D) In batch polling logic only

---

**Q12.** An agent keeps catching tool exceptions and returning friendly text without any machine-readable failure signal. What anti-pattern is this?

A) Context amplification
B) Silent error suppression
C) Prompt chaining
D) Strict tool use

---

**Q13.** A downstream workflow receives `isRetryable: false` from a validation tool. What should it do?

A) Retry until the tool succeeds
B) Fail or escalate gracefully without automatic retry
C) Drop the error and continue the workflow
D) Convert it to `true` if the request is urgent

---

**Q14.** Your analysis output must be fully auditable later. What should each finding include?

A) A summary only
B) Provenance metadata tying the finding to its source and extraction path
C) A higher temperature setting
D) A second copy of the final answer

---

**Q15.** When context gets large in an agentic workflow, what is the core goal of trimming?

A) Remove as much as possible, even if decisions are lost
B) Remove redundancy while retaining decision-critical context
C) Keep only user messages and discard all tool outputs
D) Avoid trimming because it always harms accuracy

---

**Q16.** A support workflow has repeated ambiguous user requests that could trigger refunds or account changes. What should happen before action is taken?

A) Choose the most likely interpretation and proceed quickly
B) Ask targeted clarifying questions when ambiguity affects the decision
C) Escalate every ambiguous request immediately with no attempt to clarify
D) Ignore ambiguous details if prior cases looked similar

---

**Q17.** You suspect extraction accuracy drops mainly on complex documents, not simple ones. What analysis pattern helps confirm that?

A) Stratified accuracy analysis by document complexity
B) Randomly deleting half the documents
C) Reviewing only the highest-confidence outputs
D) Running all documents through the same single-pass prompt again

---

**Q18.** A low-confidence classification may affect a compliance decision. Which workflow is safest?

A) Accept the answer if the wording sounds reasonable
B) Route low-confidence cases to an additional validation or human review pass
C) Remove confidence scores from outputs entirely
D) Ask the same model to answer the same question again with no new context

---

**Q19.** A tool set contains overlapping capabilities. Besides better descriptions, what design move often helps most?

A) Split the overlapping tool into narrower, purpose-specific tools
B) Add more optional parameters to the generic tool
C) Put all capabilities behind one `do_everything` endpoint
D) Force tool use on all requests regardless of need

---

**Q20.** A rate-limit failure occurs on a server-dependent tool. What is the appropriate immediate behavior?

A) Stop permanently because rate limits are always fatal
B) Retry with backoff if the error is marked retryable
C) Treat it as a permission error
D) Clear the whole conversation and start over

---

**Q21.** A production agent must justify every answer with evidence and uncertainty markings. Which design principle does this support?

A) Provenance and explicit uncertainty handling
B) Fewer tool descriptions
C) One-shot prompting only
D) Context-free summarization

---

**Q22.** Your team wants an MCP-integrated tool to return the same generic error payload for every failure. What is the main downside?

A) Claude will automatically expand it into richer metadata
B) The agent cannot distinguish retryable, permission, validation, and business-rule failures
C) Generic errors improve recovery because they are shorter
D) MCP does not support any error payloads

---

**Q23.** A long investigation should retain a concise checkpoint summary plus recent turns. Why is that pattern useful?

A) It preserves high-value context while avoiding unbounded growth
B) It guarantees the model never hallucinates
C) It removes the need for tool results
D) It allows skipping source tracking entirely

---

**Q24.** You want one mock focused on your weak domains and a score breakdown by domain. Which validator capability supports that best?

A) Per-domain scoring derived from the answer key's Domain column
B) Randomized answer ordering in the user sheet
C) Automatic answer filling based on confidence
D) A validator that only prints total score