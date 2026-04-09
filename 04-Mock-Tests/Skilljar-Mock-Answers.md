# Skilljar Courses – Mock Test Answers
## 35 Questions | Intro to MCP | Subagents | Agent Skills | MCP Advanced Topics

---

## Answer Key

| Q | Answer | Domain |
|---|--------|--------|
| 1 | B | D2 |
| 2 | B | D2 |
| 3 | A | D2 |
| 4 | B | D2 |
| 5 | B | D2 |
| 6 | C | D2 |
| 7 | B | D2 |
| 8 | B | D2 |
| 9 | C | D2 |
| 10 | B | D2 |
| 11 | B | D2 |
| 12 | C | D2 |
| 13 | C | D2 |
| 14 | B | D1 |
| 15 | B | D3 |
| 16 | B | D3 |
| 17 | B | D2 |
| 18 | B | D1 |
| 19 | B | D1 |
| 20 | C | D1 |
| 21 | B | D3 |
| 22 | B | D3 |
| 23 | B | D3 |
| 24 | B | D3 |
| 25 | B | D1 |
| 26 | B | D1 |
| 27 | B | D1 |
| 28 | B | D1 |
| 29 | B | D2 |
| 30 | B | D3 |
| 31 | B | D2 |
| 32 | B | D2 |
| 33 | B | D2 |
| 34 | B | D2 |
| 35 | B | D2 |

**Domain Distribution:**
- D1 (Agentic Architecture): 8 questions (Q14, Q18-20, Q25-28)
- D2 (Tool Design & MCP): 19 questions (Q1-13, Q17, Q29, Q31-35)
- D3 (Claude Code Config): 8 questions (Q15-16, Q21-24, Q30)

---

## Detailed Rationales

### Q1. Answer: B
**MCP architecture enforces 1:1 client-server connections.** A host can run multiple clients, but each client maintains exactly one connection to one server. This is a fundamental protocol design decision that enables clean capability negotiation and lifecycle management.

### Q2. Answer: B
**The server must declare tools capability during initialization.** MCP uses capability negotiation — if the server doesn't advertise `tools` in its response to `initialize`, the client MUST NOT attempt to call tools. This applies to all primitives: tools, resources, prompts, sampling, elicitation.

### Q3. Answer: A
**Database schema = Resource (application-controlled data), Query tools = Tools (model-invoked actions), SQL prompt template = Prompt (user-selected template).** The three MCP primitives are distinguished by who controls them: model (tools), application (resources), user (prompts).

### Q4. Answer: B
**Tools are model-controlled; resources are application-controlled.** This is the critical distinction. The LLM decides when to call tools (like function calling). The application decides when to attach resources (like injecting context). Users select prompts (like choosing slash commands).

### Q5. Answer: B
**`isError: true` indicates a tool execution error (business/domain error), not a protocol error.** The tool ran successfully at the transport level but encountered a business rule violation. The model should treat the `content` field as an error message and respond appropriately. This is distinct from JSON-RPC errors which indicate protocol-level failures.

### Q6. Answer: C
**Tool annotations are self-reported by the server and MUST be treated as untrusted.** The MCP specification explicitly states that trust decisions should be based on server trustworthiness, not self-reported hints. An unverified server could lie about `readOnlyHint` to bypass security checks.

### Q7. Answer: B
**Streamable HTTP supports remote deployment, HTTP communication, and horizontal scaling.** stdio requires the client to spawn the server as a local child process — it cannot work with cloud deployments or load balancers. Streamable HTTP uses HTTP POST + Server-Sent Events and supports session management via `Mcp-Session-Id` headers.

### Q8. Answer: B
**stdio uses stdin/stdout pipes with a local subprocess; Streamable HTTP uses HTTP POST and SSE for remote communication.** stdio is simpler and lower latency for local servers. Streamable HTTP is required for any remote, cloud, or horizontally-scaled deployment.

### Q9. Answer: C
**MCP Sampling** allows the server to request LLM completions through the client via `sampling/createMessage`. The server sends the request to the client, which handles the actual LLM call. This maintains the security boundary — the server never holds API keys, and the client controls which model is used.

### Q10. Answer: B
**Model preferences are hints, not requirements.** High `intelligencePriority` tells the client to prefer a capable model, but the client always makes the final decision. The server MUST NOT assume any specific model will be used.

### Q11. Answer: B
**Elicitation** is the MCP feature designed for servers to request structured input from users. The server sends `elicitation/create` with a message and `requestedSchema`, the client presents a form to the user, and returns the response (accept/decline/cancel).

### Q12. Answer: C
**Elicitation schemas are restricted to flat objects with primitive properties only.** The specification intentionally excludes nested objects, arrays, and complex JSON Schema features to simplify client implementation. Supported types: string, number/integer, boolean, enum.

### Q13. Answer: C
**Cancel** means the user dismissed without making an explicit choice (closed dialog, clicked outside, pressed Escape). This is distinct from **decline** (user explicitly said no) and **accept** (user submitted data). Servers should handle cancel differently — e.g., prompt again later.

### Q14. Answer: B
**Explore uses Haiku (fast, low-latency) with read-only tools only.** It's denied access to Write and Edit tools. Claude delegates to Explore for codebase search and analysis, keeping exploration results out of the main conversation context.

### Q15. Answer: B
**Project-level (`.claude/agents/`) has higher priority than user-level (`~/.claude/agents/`).** The priority order is: CLI flag (1) > project (2) > user (3) > plugin (4). When multiple subagents share the same name, the higher-priority location wins.

### Q16. Answer: B
**`disallowedTools` is applied first, removing Bash. Then `tools` resolves against the remaining pool.** Since Bash was removed by the denylist, the effective tool set is Read, Grep, Glob. When both fields are set, `disallowedTools` takes precedence.

### Q17. Answer: B
**Inline MCP server definitions in subagent frontmatter** connect when the subagent starts and disconnect when it finishes. This keeps MCP tool descriptions out of the main conversation context entirely. The subagent gets the tools; the parent conversation does not.

### Q18. Answer: B
**`tools: Agent(worker, researcher)` creates an allowlist** restricting which subagent types can be spawned. If the agent tries to spawn any other type, the request fails. This is specifically for agents running as the main thread with `claude --agent`.

### Q19. Answer: B
**Background subagents auto-deny non-pre-approved permissions.** Before launching a background subagent, Claude Code prompts for permissions it will need. Once running, it inherits those permissions and auto-denies anything not pre-approved. The subagent continues without that tool's result.

### Q20. Answer: C
**Subagents cannot spawn other subagents.** This is a fundamental constraint. If your workflow requires nested delegation, use skills or chain subagents from the main conversation. The `Agent(agent_type)` restriction in the `tools` field has no effect in subagent definitions for this reason.

### Q21. Answer: B
**`disable-model-invocation: true` means only the user can invoke it.** The skill is removed from Claude's context entirely — Claude cannot trigger it automatically. Use this for skills with side effects like deploy, commit, or send-slack-message where you want to control timing.

### Q22. Answer: B
**`user-invocable: false` hides the skill from the `/` menu but Claude can still invoke it automatically.** This is for background knowledge that isn't a meaningful user action. The skill's description remains in Claude's context for auto-matching.

### Q23. Answer: B
**The `!`command`` syntax is preprocessing.** Shell commands run BEFORE the skill content is sent to Claude. The command output replaces the placeholder. Claude only sees the final result (actual PR comments), not the command itself. This enables dynamic context injection.

### Q24. Answer: B
**`context: fork` creates a new isolated context.** The specified agent type (Explore) receives the skill content as its prompt, runs independently with its own context window, and returns a summary to the main conversation. The skill becomes the task for the subagent.

### Q25. Answer: B
**Exit code 2 on PreToolUse blocks the tool call.** The stderr message is fed back to Claude as an error message. This is the primary mechanism for deterministic tool blocking via hooks. Exit 0 = allow, exit 2 = block, other = non-blocking error.

### Q26. Answer: B
**`decision: "block"` on a Stop event prevents Claude from stopping.** Claude continues the conversation with the reason as guidance. This is used for quality gates — e.g., ensuring tests pass before Claude finishes. The `stop_hook_active` field prevents infinite loops by indicating a Stop hook is already active.

### Q27. Answer: B
**`permissionDecision: "allow"` skips the permission prompt, and `updatedInput` modifies the tool's input before execution.** The combined effect is: the original command is replaced with `npm run lint --fix` and executed without user confirmation. `updatedInput` replaces the entire input object.

### Q28. Answer: B
**`PostToolUse` with `async: true` runs in the background after a Write.** Async hooks run without blocking Claude — they CANNOT return decisions. Only `type: "command"` hooks support `async`. This is perfect for test suites or linting that shouldn't slow down Claude's work.

### Q29. Answer: B
**`mcp__.*__write.*` matches any MCP tool** with "write" in its name from any server. MCP tools follow the pattern `mcp__<server>__<tool>`. The `.*` before the double underscore matches any server name.

### Q30. Answer: B
**The `skills` frontmatter field injects full skill content into the subagent's context at startup.** The subagent doesn't need to discover or load skills during execution — they're preloaded. Note: subagents don't inherit skills from the parent conversation; you must list them explicitly.

### Q31. Answer: B
**`stateless_http=True` eliminates session coordination for horizontal scaling.** When enabled: no session IDs, no server→client requests, no sampling, no progress notifications, no subscriptions. Client initialization is no longer required. Use this when you need horizontal scaling and don't need server-initiated features. (Verified from Skilljar "State and StreamableHTTP" lesson)

### Q32. Answer: B
**StreamableHTTP uses TWO separate SSE connections** to work around HTTP's limitation (server can't initiate requests to clients). The Primary SSE Connection handles server-initiated requests and stays open indefinitely. The Tool-Specific SSE Connection is created per tool call and closes when the tool result is sent. Setting `stateless_http=True` or `json_response=True` breaks this SSE mechanism. (Verified from Skilljar "StreamableHTTP in depth" lesson)

### Q33. Answer: B
**The SDK does NOT automatically enforce root restrictions.** Roots are informational. The developer must implement `is_path_allowed()` checks in their server code. This is a critical Skilljar teaching point — many assume roots are auto-enforced. (Verified from Skilljar "Roots" lesson)

### Q34. Answer: B
**`context.info()` sends log messages and `context.report_progress()` tracks progress.** The Context argument is automatically provided to tool functions. The client receives these via `logging_callback` and `progress_callback`. Presentation varies: CLI (print), Web (WebSockets/SSE/polling), Desktop (progress bars). These are entirely optional. (Verified from Skilljar "Log and progress notifications" lesson)

### Q35. Answer: B
**Sampling shifts responsibility and cost to the client.** The server never holds API keys, and each client pays for their own AI usage. This is especially valuable for publicly accessible MCP servers. The server calls `ctx.session.create_message()` with a prompt; the client handles the actual LLM call and returns the result. (Verified from Skilljar "Sampling" lesson)

---

## Concept Coverage Map

| Concept | Questions | Source Course |
|---------|-----------|---------------|
| MCP Architecture (host/client/server) | Q1, Q2 | Intro to MCP |
| MCP Primitives (tools/resources/prompts) | Q3, Q4 | Intro to MCP |
| Tool result errors (isError) | Q5 | Intro to MCP |
| Tool annotations (untrusted) | Q6 | Intro to MCP |
| Transports (stdio vs Streamable HTTP) | Q7, Q8 | MCP Advanced Topics |
| Sampling (server → client LLM call) | Q9, Q10 | MCP Advanced Topics |
| Elicitation (server → user input) | Q11, Q12, Q13 | MCP Advanced Topics |
| Built-in subagents (Explore) | Q14 | Intro to Subagents |
| Subagent scope priority | Q15 | Intro to Subagents |
| tools vs disallowedTools | Q16 | Intro to Subagents |
| MCP servers scoped to subagents | Q17 | Intro to Subagents |
| Agent spawning restrictions | Q18, Q20 | Intro to Subagents |
| Background subagent permissions | Q19 | Intro to Subagents |
| disable-model-invocation | Q21 | Agent Skills |
| user-invocable: false | Q22 | Agent Skills |
| Dynamic context injection (!`cmd`) | Q23 | Agent Skills |
| context: fork + agent field | Q24 | Agent Skills |
| Hook exit codes (PreToolUse) | Q25 | MCP Advanced Topics |
| Stop hook blocking | Q26 | Claude Code in Action |
| PreToolUse decision + updatedInput | Q27 | Claude Code in Action |
| Async hooks | Q28 | Claude Code in Action |
| MCP tool matching in hooks | Q29 | MCP Advanced Topics |
| Preloading skills into subagents | Q30 | Agent Skills |
| stateless_http for horizontal scaling | Q31 | MCP Advanced Topics (Skilljar) |
| TWO SSE connections pattern | Q32 | MCP Advanced Topics (Skilljar) |
| Root enforcement (SDK vs developer) | Q33 | MCP Advanced Topics (Skilljar) |
| Log and progress notifications API | Q34 | MCP Advanced Topics (Skilljar) |
| Sampling cost-shifting rationale | Q35 | MCP Advanced Topics (Skilljar) |

---

*Answers based on: Verified Skilljar courses (Intro MCP, MCP Advanced Topics) + code.claude.com/docs/en/sub-agents, code.claude.com/docs/en/skills, code.claude.com/docs/en/hooks*
