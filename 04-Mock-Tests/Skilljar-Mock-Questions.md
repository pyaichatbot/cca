# Skilljar Courses – Mock Test Questions
## 35 Questions Covering: Intro to MCP | Subagents | Agent Skills | MCP Advanced Topics

> **Source:** Verified Skilljar course content (Intro MCP + MCP Advanced Topics) + Anthropic official docs (Subagents + Skills)
> **Focus:** Concepts from the 4 Skilljar courses NOT already covered in Gap-Coverage-Mock or other mock tests

---

## Questions

**Q1.** In the MCP architecture, a host application runs multiple MCP clients. What is the relationship between clients and servers?

A) Each client connects to multiple servers simultaneously
B) Each client maintains a 1:1 connection with a single server
C) All clients share a single connection to all servers
D) Servers decide which clients they connect to

---

**Q2.** During MCP initialization, the client sends `initialize` with its capabilities, the server responds with its capabilities, and the client sends `initialized`. A client wants to call tools on a server. What MUST be true?

A) The client must have declared `tools` in its capabilities
B) The server must have declared `tools` in its capabilities during initialization
C) The host must have a tools plugin installed
D) The server must send a `tools/ready` notification first

---

**Q3.** An MCP server exposes a database schema, a set of query tools, and a "generate SQL" prompt template. Which MCP primitive is each?

A) Resources, Tools, Prompts
B) Tools, Tools, Resources
C) Prompts, Resources, Tools
D) Resources, Resources, Prompts

---

**Q4.** A developer builds an MCP server that provides tools and resources. When describing these to a colleague, which statement accurately distinguishes them?

A) Tools are invoked by the user; resources are invoked by the model
B) Tools are model-controlled (the LLM decides when to call them); resources are application-controlled (the app decides when to attach them)
C) Tools return structured data; resources return unstructured text
D) Tools are read-only; resources can modify state

---

**Q5.** An MCP tool call returns the following result. What does the `isError: true` flag tell the model?

```json
{
  "content": [{ "type": "text", "text": "Account locked: too many failed attempts" }],
  "isError": true
}
```

A) The JSON-RPC transport failed and the message should be retried
B) The tool executed but encountered a business/domain error; the model should treat the content as an error message
C) The MCP server crashed and needs to be restarted
D) The tool schema was invalid

---

**Q6.** An MCP server reports `readOnlyHint: true` and `destructiveHint: false` in a tool's annotations. A host application uses these annotations to automatically skip its confirmation dialog. Is this a secure design?

A) Yes — annotations are protocol-enforced security guarantees
B) Yes — if both hints agree the tool is safe, no confirmation is needed
C) No — annotations are self-reported by the server and MUST be treated as untrusted; trust decisions should be based on server trustworthiness, not self-reported hints
D) No — annotations only apply to resource access, not tool calls

---

**Q7.** A production system needs to deploy an MCP server to a cloud environment behind a load balancer for horizontal scaling. Which MCP transport should be used?

A) stdio — it's the simplest and most reliable
B) Streamable HTTP — it supports remote deployment, HTTP-based communication, and stateless horizontal scaling
C) WebSocket — MCP's default cloud transport
D) gRPC — required for production MCP deployments

---

**Q8.** What is the key difference between stdio and Streamable HTTP transports in MCP?

A) stdio is faster; Streamable HTTP has higher latency but more features
B) stdio communicates via stdin/stdout with a local subprocess; Streamable HTTP communicates via HTTP POST and Server-Sent Events with a remote server
C) stdio supports only tools; Streamable HTTP supports all primitives
D) stdio is deprecated; Streamable HTTP is the only current transport

---

**Q9.** An MCP server needs to analyze data using an LLM but should NOT hold API keys for security reasons. Which MCP feature enables this?

A) Tool annotations with `openWorldHint: true`
B) Resource subscriptions
C) Sampling — the server sends a `sampling/createMessage` request to the client, which makes the LLM call and returns the result
D) Elicitation — the server asks the user to run the analysis manually

---

**Q10.** In MCP sampling, the server includes `modelPreferences` with `intelligencePriority: 0.9`, `speedPriority: 0.1`, `costPriority: 0.1`. What does this communicate?

A) The server demands a specific model be used
B) The server prefers the client use a highly capable model, with speed and cost being secondary concerns — but the client decides the final model
C) The client must use the most expensive model available
D) These preferences are binding and the client must comply exactly

---

**Q11.** An MCP server needs to ask the user for their preferred output format during a tool execution. Which MCP feature should be used?

A) Sampling — request an LLM call to determine the format
B) Elicitation — send an `elicitation/create` request with a schema for the expected input
C) Prompts — define a prompt template the user can select
D) Roots — declare the output directory

---

**Q12.** An MCP server sends an elicitation request with a `requestedSchema` that includes a nested object with arrays. What happens?

A) The client generates a complex multi-page form
B) The nested structure is flattened automatically
C) The request should fail or behave unexpectedly — elicitation schemas are restricted to flat objects with primitive properties only (string, number, boolean, enum)
D) Nested objects are supported but arrays are not

---

**Q13.** A user receives an elicitation dialog from an MCP server and clicks the X button to close it without responding. What action should the client report to the server?

A) `accept` with empty content
B) `decline`
C) `cancel` — the user dismissed without making an explicit choice
D) No response is sent; the server times out

---

**Q14.** Claude Code includes a built-in subagent called "Explore." What are its characteristics?

A) Uses Opus model, has full tool access including Write and Edit
B) Uses Haiku model, read-only tools (no Write/Edit), optimized for fast codebase search
C) Uses Sonnet model, has Bash access for running tests
D) Uses the parent conversation's model with all tools

---

**Q15.** A developer creates a custom subagent defined in `.claude/agents/security-reviewer.md`. Another subagent with the same name exists in `~/.claude/agents/`. Which one takes effect?

A) The user-level (`~/.claude/agents/`) subagent wins
B) The project-level (`.claude/agents/`) subagent wins because it has higher priority
C) Both run simultaneously
D) Claude asks the user which one to use

---

**Q16.** A subagent frontmatter includes:
```yaml
tools: Read, Grep, Glob, Bash
disallowedTools: Bash
```
What tools does this subagent have access to?

A) Read, Grep, Glob, Bash (tools field wins)
B) Read, Grep, Glob (disallowedTools is applied first, removing Bash, then tools resolves against the remaining pool)
C) Only Bash (disallowedTools inverts to become an allowlist)
D) No tools (conflicting fields cancel each other out)

---

**Q17.** A team wants a subagent that can use a Playwright MCP server for browser testing, but they don't want Playwright tools showing up in the main conversation. What's the correct approach?

A) Define the Playwright server in `.mcp.json` and restrict it with permission rules
B) Define the Playwright server inline in the subagent's `mcpServers` frontmatter field — inline servers connect when the subagent starts and disconnect when it finishes
C) Install Playwright globally and use Bash to run it
D) Create a separate `.mcp.json` for the subagent

---

**Q18.** A coordinator agent needs to delegate tasks to a "worker" and "researcher" subagent but should NOT be able to spawn any other subagent type. How is this configured?

A) `disallowedTools: Agent`
B) `tools: Agent(worker, researcher), Read, Bash` — this allowlist restricts spawning to only the named subagents
C) `permissionMode: plan`
D) Add a list of blocked agents in settings.json

---

**Q19.** A subagent is launched in background mode. During execution, it encounters a tool call that requires user permission which was NOT pre-approved. What happens?

A) The subagent pauses and prompts the user
B) The tool call is auto-denied; the subagent continues without that tool's result
C) The entire subagent is terminated
D) The permission is auto-granted for background tasks

---

**Q20.** Can a subagent spawn another subagent?

A) Yes — subagents can spawn unlimited nested subagents
B) Yes — but only up to 3 levels deep
C) No — subagents cannot spawn other subagents. Chain subagents from the main conversation instead
D) Only if the parent grants the `Agent` tool explicitly

---

**Q21.** A skill named "deploy" has `disable-model-invocation: true` in its frontmatter. What does this mean?

A) The skill cannot be used at all
B) Only the user can invoke it via `/deploy`; Claude cannot trigger it automatically
C) Only Claude can invoke it; the user cannot
D) The skill runs but produces no output

---

**Q22.** A developer creates a skill at `.claude/skills/api-conventions/SKILL.md` with `user-invocable: false`. How does this skill work?

A) It's completely disabled
B) It's hidden from the `/` menu, but Claude can still load it automatically when relevant
C) Only the user can invoke it
D) It's deleted on next session start

---

**Q23.** A skill includes this line in its content:
```
PR comments: !`gh pr view --comments`
```
What happens when the skill is invoked?

A) Claude sees the literal text `!gh pr view --comments` and decides whether to run it
B) The `gh pr view --comments` command runs BEFORE the skill content is sent to Claude; Claude sees the command output, not the command itself
C) The command runs in a sandbox with no real access
D) Nothing — the `!` backtick syntax is not valid

---

**Q24.** A skill has `context: fork` and `agent: Explore` in its frontmatter. What happens when it's invoked?

A) The skill runs inline in the main conversation using the Explore model
B) A new isolated context is created; the Explore subagent receives the skill content as its prompt, runs independently, and returns a summary to the main conversation
C) The Explore agent reads the skill but doesn't execute anything
D) The skill is converted to a permanent subagent definition

---

**Q25.** A Claude Code hook has `matcher: "Bash"` and uses exit code 2 on a PreToolUse event. What happens?

A) The Bash tool call is logged but executed normally
B) The Bash tool call is blocked. The stderr message is fed back to Claude as an error
C) The session terminates
D) The exit code is ignored for PreToolUse events

---

**Q26.** A hook on the `Stop` event returns `{ "decision": "block", "reason": "Tests not verified" }`. What happens?

A) Claude's response is deleted
B) Claude is prevented from stopping and continues the conversation with the reason as its next instruction
C) The session terminates with an error
D) The hook result is ignored because Stop can't be blocked

---

**Q27.** A `PreToolUse` hook returns:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "updatedInput": { "command": "npm run lint --fix" }
  }
}
```
What effect does this have?

A) The original tool call is blocked
B) The tool call proceeds with the MODIFIED input (`npm run lint --fix` instead of the original command), and the permission prompt is skipped
C) The tool call proceeds with the original input
D) Two tool calls execute: the original and the modified one

---

**Q28.** A team wants to run tests automatically in the background every time Claude writes a file, without blocking Claude's work. Which hook configuration achieves this?

A) `PreToolUse` with `matcher: "Write"` and `exit 0`
B) `PostToolUse` with `matcher: "Write"`, `type: "command"`, and `"async": true`
C) `Stop` hook that runs tests before Claude finishes
D) `SessionStart` hook that starts a file watcher

---

**Q29.** MCP tools in Claude Code hooks follow the naming pattern `mcp__<server>__<tool>`. A team wants to validate ALL write operations from ANY MCP server. Which matcher pattern achieves this?

A) `mcp__write`
B) `mcp__.*__write.*`
C) `*.write`
D) `mcp_write_*`

---

**Q30.** A skill and a subagent both need to work together. The skill provides API conventions, and the subagent implements endpoints. Which configuration correctly preloads the skill into the subagent?

A) Reference the skill in the subagent's system prompt markdown
B) Add the skill name to the subagent's `skills` frontmatter field — the full skill content is injected into the subagent's context at startup
C) Add `context: fork` to the skill
D) Create a shared `.claude/skills/` directory that both can read

---

**Q31.** A team needs to deploy an MCP server for horizontal scaling behind a load balancer. They don't need server-initiated requests, sampling, or progress notifications. Which StreamableHTTP setting should they enable?

A) `json_response=True` — returns plain JSON instead of SSE
B) `stateless_http=True` — eliminates session coordination, no server→client requests, enables horizontal scaling
C) `stateful_http=True` — adds session persistence across instances
D) `load_balanced=True` — built-in load balancer support

---

**Q32.** In MCP's StreamableHTTP transport, a tool call is in progress and the server needs to send both progress updates and the final tool result. How does StreamableHTTP handle this?

A) All messages go through a single HTTP connection
B) The server uses TWO separate SSE connections: a Primary SSE Connection (for server-initiated requests, stays open indefinitely) and a Tool-Specific SSE Connection (per tool call, closes when result is sent)
C) Progress updates are sent via WebSocket while results use HTTP POST
D) Progress updates are queued and sent after the tool result

---

**Q33.** A developer defines roots for an MCP server using the Python SDK. They set roots to `file:///project/src`. A tool in the server attempts to read `/etc/passwd`. What happens?

A) The SDK automatically blocks the read because it's outside the declared root
B) The read succeeds — the SDK does NOT automatically enforce root restrictions. The developer must implement `is_path_allowed()` checks themselves
C) The server crashes with a permission error
D) The client intercepts and blocks the read before it reaches the server

---

**Q34.** An MCP server tool function needs to log a progress message during a long-running operation. Using the Python MCP SDK, which is the correct approach?

A) `print("Processing file 3 of 10...")`
B) `await context.info("Processing file 3 of 10...")` for log messages and `await context.report_progress(current=3, total=10)` for progress tracking
C) `logging.info("Processing file 3 of 10...")`
D) `return {"progress": "3/10"}` as an intermediate tool result

---

**Q35.** In MCP sampling, the server calls `ctx.session.create_message()` with a prompt and `max_tokens`. What is the primary reason the server uses sampling instead of calling an LLM API directly?

A) Sampling provides better response quality than direct API calls
B) The server shifts responsibility and cost of text generation to the client — no API keys needed on the server, perfect for public servers where each client pays for their own AI usage
C) Sampling is faster than direct API calls because it uses caching
D) The MCP protocol requires all LLM calls to go through sampling

---
