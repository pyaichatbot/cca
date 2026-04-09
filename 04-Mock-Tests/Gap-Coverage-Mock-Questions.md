# Claude Certified Architect - Gap Coverage Mock Test

> 20 questions | Covers gaps identified from daronyondem/claude-architect-exam-guide
> Focus: Uncertain state errors, exceptions vs structured returns, lookup-then-act, two-tool token safety, system prompt dilution, principles vs conditionals, context management strategies, MCP negative knowledge, interdependent parameter constraints, external updates, enforcement spectrum, graceful degradation, prompt versioning

## Instructions
- Select the BEST answer for each question
- Every question targets a specific gap not adequately covered in prior mock tests
- Scenarios are drawn strictly from the daronyondem exam preparation guide

---

## Questions

**Q1.** An agent tool calls a payment API to charge a customer $200. The HTTP request times out during the write operation. The tool cannot determine whether the charge was applied. What should the tool return?

A) `{ "error_type": "transient", "retryable": true, "message": "Timeout, please retry" }`
B) `{ "error_type": "uncertain_state", "retryable": false, "message": "Status unknown. The charge may have been applied. Do not retry." }`
C) `{ "error_type": "permanent", "retryable": false, "message": "Payment failed" }`
D) Throw an exception so the framework can handle the timeout

---

**Q2.** A notification tool sends an email to a customer. The upstream SMTP server times out during delivery. The tool does not know if the email was actually sent. The tool marks the error as `retryable: true`. What is the most likely consequence?

A) The agent will correctly wait and retry once
B) The agent may retry, causing duplicate notifications to the customer
C) The agent will escalate to a human immediately
D) The framework will suppress the duplicate automatically

---

**Q3.** A tool encounters a business rule violation ("Insufficient funds"). The developer implements this as a thrown Python exception inside the tool function. What happens when the exception reaches the agent framework?

A) The framework catches it and passes the full exception details to the model
B) The framework catches it and presents a generic error message to the model, stripping away the business context the model needs
C) The model receives the exact stack trace and can parse the error type
D) The exception is silently ignored and the tool appears to succeed

---

**Q4.** What is the recommended way for a tool to report a business rule error to the agent model?

A) Throw a custom exception with an error code
B) Return the error as structured data in the tool's `content` field with the `isError` flag set to true
C) Log the error to a file and return an empty response
D) Return a plain text string "Error occurred"

---

**Q5.** Users refer to contacts by name (e.g., "Send the report to Sarah"), but the CRM has multiple people named "Sarah." A single `send_report(recipient_name, report_id)` tool frequently picks the wrong contact. What is the best tool design fix?

A) Add a disclaimer to the tool description saying "Names may be ambiguous"
B) Split into two tools: `search_contacts(name)` returns matching contacts with IDs, then `send_report(contact_id, report_id)` acts on a specific ID
C) Add a `confirm: boolean` parameter to the send_report tool
D) Require users to always type the full email address instead of a name

---

**Q6.** An agent tool provisions cloud infrastructure — an expensive, irreversible operation. The team implements a single tool `provision_infra(specs, preview: boolean)`. Why is this design problematic for safety?

A) The tool is too complex for the model to understand
B) The model can skip the preview step by setting `preview: false`, creating a path where the destructive action executes without review
C) Boolean parameters are not supported in tool schemas
D) Preview mode will always be slower than direct execution

---

**Q7.** What is the most reliable structural pattern to prevent an agent from executing a destructive operation without prior review?

A) Add "ALWAYS preview before executing" to the system prompt
B) Use a single tool with a `preview: boolean` parameter
C) Use two separate tools: a preview tool that returns a single-use approval token, and an execute tool that requires that token
D) Use tool annotations with `destructiveHint: true`

---

**Q8.** A 40-turn customer service conversation is underway. The system prompt instructs the agent to "always verify the customer's identity before accessing account details." At turn 38, the agent accesses account details without verifying identity. What is the most likely cause?

A) The system prompt was deleted after the first request
B) System prompt influence dilutes as the conversation grows and accumulated assistant responses create a behavioral pattern that overrides original instructions
C) The context window was exceeded, so the system prompt was truncated
D) The model randomly ignores instructions regardless of conversation length

---

**Q9.** Which mitigation is most effective against system prompt dilution in extended conversations?

A) Writing the instruction in ALL CAPS with "CRITICAL" prefix
B) Including few-shot examples in the system prompt that concretely demonstrate the desired behavior
C) Making the system prompt shorter so it's easier to read
D) Sending the system prompt only with the first API request

---

**Q10.** A system prompt contains 15 detailed conditional rules: "If user says X, do Y." The model increasingly fails to follow specific rules as more conditionals are added. What is the best approach to improve compliance?

A) Add more conditionals to cover the missed edge cases
B) Replace groups of related conditionals with general principles that let the model exercise judgment, keeping only safety-critical rules as explicit conditionals
C) Remove the system prompt entirely and rely on the model's defaults
D) Duplicate each conditional three times in the prompt for emphasis

---

**Q11.** Which type of rule should remain as an explicit conditional in a system prompt rather than being replaced by a general principle?

A) "Match financial detail to the user's demonstrated knowledge level"
B) "If the user describes symptoms of a medical emergency, always direct them to call emergency services"
C) "Be helpful and concise in your responses"
D) "Adapt your tone based on the user's communication style"

---

**Q12.** A travel booking agent tracks a user's evolving preferences (budget, dates, destinations) across a 30-turn conversation. Old preferences and new conflicting preferences coexist in the history. The model sometimes uses an outdated budget figure. What is the most reliable strategy?

A) Use a sliding window that keeps only the last 5 turns
B) Use progressive summarization to compress older turns
C) Maintain a structured JSON state object capturing the current preferences and include it in every request
D) Increase the context window size

---

**Q13.** A researcher needs to recall the exact sample size of Study #3 from a dataset discussed 25 turns ago. The conversation uses progressive summarization. The summary says "sample sizes ranged from 200-500." Why does this fail, and what strategy should have been used?

A) Summarization is fine; the model should be able to infer the exact number from the range
B) Summaries lose precision on numerical data; a structured fact database with retrieval should be used for precision-dependent recall
C) The sliding window should have been larger to keep all 25 turns
D) The model should be prompted with "remember all numbers exactly"

---

**Q14.** A team builds an MCP server for their internal code analysis tooling. A colleague asks: "Does MCP handle retrying failed tool calls and rate-limiting requests automatically?" What is the correct answer?

A) Yes, MCP provides built-in retry logic and rate limiting as part of the protocol
B) No. MCP is a protocol for tool discovery and invocation. Authentication, retries, rate limiting, and caching are the developer's responsibility
C) MCP handles retries but not rate limiting
D) MCP handles rate limiting but not retries

---

**Q15.** An MCP tool from an unverified third-party server reports `readOnlyHint: true` in its annotations. The host application considers bypassing its confirmation prompt for this tool since it claims to be read-only. What is the risk?

A) No risk — MCP annotations are security guarantees enforced by the protocol
B) The annotation is self-reported by the server and may not be accurate. Trust decisions should be based on server trustworthiness, not self-reported annotations
C) The annotation is verified by a certificate authority before being served
D) Read-only tools cannot modify data regardless of the annotation

---

**Q16.** A tool accepts `create_payment(amount, currency, payment_method)`. Valid payment methods depend on the currency (e.g., iDEAL only works for EUR, UPI only for INR). The model frequently passes invalid combinations. What is the best structural fix?

A) Add a long description explaining all valid currency-method combinations
B) Split into separate tools per payment type where each enforces its own constraints structurally (e.g., `create_bank_transfer(amount, iban, bic)`, `create_ideal_payment(amount, iban)`)
C) Add an enum listing all payment methods regardless of currency
D) Add a `validate: boolean` parameter that checks combinations before executing

---

**Q17.** During an active customer service conversation, the system receives a webhook notification that the customer's pending order has shipped. What is the cleanest way to incorporate this update into the conversation?

A) Store the webhook data in a database and hope the agent queries it
B) Append the update to the next user message before calling the API, making it part of the natural conversation flow
C) Send a separate API request with only the webhook data
D) Update the system prompt to include the shipping status

---

**Q18.** An agent verifies that a customer qualifies for a free account upgrade, but the tool that applies the upgrade returns a timeout error. What is the best agent behavior?

A) Immediately escalate to a human agent without telling the customer anything
B) Tell the customer the upgrade was applied (optimistic assumption)
C) Confirm the customer's eligibility, be transparent about the system issue, and offer alternatives (retry later, escalation)
D) Silently retry the upgrade 10 times in a loop

---

**Q19.** A system prompt for a financial advisor chatbot is updated between sessions. Returning customers now see the agent contradict advice it gave in previous sessions. What caused this?

A) The model has a memory bug
B) The updated system prompt conflicts with patterns in the historical conversation context from prior sessions, causing contradictions
C) The API changed its behavior between sessions
D) The customer is misremembering the prior advice

---

**Q20.** A business rule states: "Wire transfers exceeding $10,000 must be approved by a compliance officer." The team implements this as an emphatic system prompt instruction: "CRITICAL: ALWAYS require compliance officer approval for wire transfers over $10,000. NEVER skip this step." Is this implementation sufficient?

A) Yes — emphatic language like "CRITICAL" and "NEVER" guarantees 100% compliance
B) No — emphatic language may slightly increase compliance but does not guarantee it. This rule must be enforced programmatically via a hook or middleware that intercepts the tool call and blocks execution if the amount exceeds the threshold
C) Yes — system prompt instructions are always followed for financial rules
D) No — the threshold should be lowered to $5,000 instead

---
