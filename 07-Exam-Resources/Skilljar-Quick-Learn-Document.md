# Skilljar Courses – Quick-Learn Document
## CCA Exam Cram: 4 Courses in 1 Document

**Covers:** Introduction to MCP | Introduction to Subagents | Introduction to Agent Skills | MCP Advanced Topics  
**Source:** Verified Skilljar course content (Intro MCP + MCP Advanced Topics) + Anthropic official docs (Subagents + Skills)  
**Purpose:** Exam-critical concepts from the 4 Skilljar courses, distilled for rapid review.

> **Verification Note:** Courses 1 & 2 content verified against authenticated Skilljar. Courses 3 & 4 sourced from official Anthropic docs (code.claude.com) — same material Skilljar courses are based on.

---

## Course 1: Introduction to Model Context Protocol (MCP)

### 1.1 Architecture — Host / Client / Server

MCP uses a three-layer architecture:

| Component | Role | Example |
|-----------|------|---------|
| **Host** | Application the user interacts with | Claude Desktop, VS Code, IDE |
| **Client** | Protocol connector inside the host; maintains 1:1 connection with a server | Built into the host |
| **Server** | Exposes capabilities (tools, resources, prompts) to the client | Filesystem server, GitHub server |

**Key rule:** One host can run multiple clients, each connected to one server. Clients and servers negotiate capabilities during initialization.

### 1.2 Protocol Layer — JSON-RPC 2.0

All MCP messages use JSON-RPC 2.0:
- **Requests** have `id`, `method`, `params`
- **Responses** have `id`, `result` (or `error`)
- **Notifications** have `method`, `params` but NO `id` (fire-and-forget)

### 1.3 Lifecycle — Initialize → Operate → Shutdown

1. **Initialize**: Client sends `initialize` with its capabilities → Server responds with its capabilities → Client sends `initialized` notification
2. **Operate**: Normal message exchange (tool calls, resource reads, etc.)
3. **Shutdown**: Either side sends `close` or transport disconnects

**Exam trap:** Capability negotiation happens at initialization. If a server doesn't declare `tools` capability, the client MUST NOT try to call tools on it.

### 1.4 The Three Server Primitives

| Primitive | Controlled By | Discovery Method | Use Case |
|-----------|--------------|-----------------|----------|
| **Tools** | Model-controlled | `tools/list` | Actions the LLM decides to call (API calls, calculations, DB queries) |
| **Resources** | Application-controlled | `resources/list` | Data the app exposes to the LLM (files, DB records, API responses) |
| **Prompts** | User-controlled | `prompts/list` | Pre-built templates the user selects (slash commands, workflows) |

**Critical distinction for exam:**
- **Tools** = Model decides when to invoke (like function calling)
- **Resources** = Application decides when to attach (like context injection)
- **Prompts** = User explicitly selects (like slash commands)

### 1.5 Tools — Deep Dive

**Tool definition schema:**
```json
{
  "name": "get_weather",
  "description": "Get current weather for a city",
  "inputSchema": {
    "type": "object",
    "properties": {
      "city": { "type": "string" }
    },
    "required": ["city"]
  }
}
```

**Tool call flow:**
1. Client discovers tools via `tools/list`
2. Model decides to call a tool → Client sends `tools/call` with `name` + `arguments`
3. Server executes → Returns `content` array (text, image, or embedded resource)

**Tool result errors — TWO types:**
1. **Protocol error**: JSON-RPC error in the response (server couldn't process the request)
2. **Tool execution error**: `isError: true` in the result content (tool ran but hit a business error)

```json
{
  "content": [{ "type": "text", "text": "Insufficient funds for transfer" }],
  "isError": true
}
```

**Tool annotations** (metadata hints — NOT security guarantees):
| Annotation | Meaning |
|-----------|---------|
| `readOnlyHint` | Tool doesn't modify state |
| `destructiveHint` | Tool may make irreversible changes |
| `idempotentHint` | Safe to call multiple times with same args |
| `openWorldHint` | Tool interacts with external entities |

**CRITICAL:** Annotations are self-reported by the server. They MUST be treated as untrusted. Hosts should NOT make security decisions based solely on annotations.

**Dynamic tool updates:** Servers can notify clients when tools change via `notifications/tools/list_changed`. The client then re-fetches the tool list.

### 1.6 Resources — Deep Dive

Resources use URIs for identification:
```
file:///project/src/main.py
postgres://db/users/schema
screen://localhost/display1
```

**Resource templates** use URI templates for dynamic resources:
```json
{
  "uriTemplate": "file:///{path}",
  "name": "Project Files",
  "mimeType": "application/octet-stream"
}
```

**Resource subscriptions:** Clients can subscribe to specific resources. When the resource changes, the server sends `notifications/resources/updated`. The client then re-reads the resource.

**Resource annotations** provide hints:
- `audience`: Who this resource is for (e.g., `["user"]`, `["assistant"]`, or both)
- `priority`: Importance hint (0.0 = lowest, 1.0 = highest)

### 1.7 Prompts — Deep Dive

Prompts are user-controlled templates:
```json
{
  "name": "code_review",
  "description": "Review code for best practices",
  "arguments": [
    { "name": "language", "description": "Programming language", "required": true }
  ]
}
```

**Prompt results** return `PromptMessage` objects with `role` (user/assistant) and `content` (text, image, or embedded resource). Prompts can embed resources directly in their content.

---

## Course 2: MCP Advanced Topics

### 2.1 Transports — stdio vs Streamable HTTP

| Feature | stdio | Streamable HTTP |
|---------|-------|----------------|
| **Communication** | stdin/stdout pipes | HTTP POST + Server-Sent Events |
| **Deployment** | Local subprocess only | Remote servers, cloud, load balancers |
| **Session management** | Implicit (process lifecycle) | Explicit via `Mcp-Session-Id` header |
| **When to use** | Local tools, dev environments | Production, horizontal scaling, remote |
| **Resumability** | No | Yes (via Last-Event-ID header) |

**Exam rule:** If the question asks about deploying an MCP server behind a load balancer or to the cloud → Streamable HTTP. If it asks about a local CLI tool → stdio.

**stdio detail (from Skilljar):** Client launches server as subprocess, communicates via stdin/stdout. Only works when client and server on SAME machine. Connection uses 3-message handshake: Initialize Request → Initialize Result → Initialized Notification.

**StreamableHTTP key settings (Skilljar-specific):**
| Setting | Default | When enabled |
|---------|---------|-------------|
| `stateless_http` | `False` | No session IDs, no server→client requests, no sampling, no progress, no subscriptions. Enables horizontal scaling. Client initialization no longer required. |
| `json_response` | `True` | Disables SSE streaming for POST responses. Only final JSON returned, no intermediate progress/log. |

**TWO SSE Connections pattern (Skilljar StreamableHTTP in depth):**
- **Primary SSE Connection**: For server-initiated requests, stays open indefinitely
- **Tool-Specific SSE Connection**: Per tool call, closes when tool result is sent
- `stateless_http=True` or `json_response=True` breaks this SSE workaround

**When to use stateless:** Horizontal scaling, no server→client needed, no sampling, minimal overhead  
**When to use json_response:** No streaming needed, simpler responses, integrating with plain JSON systems  
**Exam tip:** Test with SAME transport you'll deploy to production

### 2.2 Sampling — Server Requesting LLM Completions

Sampling flips the normal flow: the **server** asks the **client** to make an LLM call.

```
Server → sampling/createMessage → Client → LLM → Client → Response → Server
```

**The Problem Sampling Solves (from Skilljar):**
- Option 1: Give MCP server direct API access → own API key, auth, costs, code complexity
- Option 2: Use sampling → server generates prompt, asks client "Could you call Claude for me?"
- **Key benefit:** Shifts cost burden to client. Perfect for **public servers** (don't want public server racking up AI costs)

**How It Works (Skilljar 6-step flow):**
1. Server completes its work (e.g., fetching Wikipedia articles)
2. Server creates a prompt asking for text generation
3. Server sends a sampling request to the client
4. Client calls Claude with the provided prompt
5. Client returns the generated text to the server
6. Server uses the generated text in its response

**Server-side Python implementation:**
```python
@mcp.tool()
async def summarize(text_to_summarize: str, ctx: Context):
    prompt = f"Please summarize the following text: {text_to_summarize}"
    result = await ctx.session.create_message(
        messages=[SamplingMessage(role="user", content=TextContent(type="text", text=prompt))],
        max_tokens=4000,
        system_prompt="You are a helpful research assistant",
    )
    if result.content.type == "text":
        return result.content.text
    else:
        raise ValueError("Sampling failed")
```

**Client-side Python implementation:**
```python
async def sampling_callback(context: RequestContext, params: CreateMessageRequestParams):
    text = await chat(params.messages)
    return CreateMessageResult(
        role="assistant",
        model=model,
        content=TextContent(type="text", text=text),
    )

# Pass callback when initializing client session:
async with ClientSession(read, write, sampling_callback=sampling_callback) as session:
    await session.initialize()
```

**Model preferences** in sampling requests:
- `intelligencePriority` (0-1)
- `speedPriority` (0-1)
- `costPriority` (0-1)
- `hints`: Array of model name preferences

**Security rules:**
- Human-in-the-loop: Clients SHOULD allow users to review/modify before sending
- Server MUST NOT assume a specific model will be used
- Server MUST NOT use sampling to manipulate the user

### 2.3 Roots — Filesystem Boundaries

Roots are client-declared filesystem boundaries that tell the server where it can operate:

```json
{ "uri": "file:///project/src", "name": "Source Code" }
```

**Key facts:**
- Roots are **informational** — servers SHOULD respect them but the protocol doesn't enforce
- Clients declare roots; servers request them via `roots/list`
- Only `file://` URIs are supported
- Dynamic updates via `notifications/roots/list_changed`

**Skilljar-specific insight:** The SDK does NOT automatically enforce root restrictions — YOU must implement `is_path_allowed()` yourself. Roots are a permission hint: "Hey MCP server, you can access these files."

**Use case (from Skilljar):** User asks Claude to "convert video.mp4" but Claude doesn't know the location → With roots, Claude calls `list_roots` → `read_dir` → finds the file → calls tool with full path.

### 2.3b Log and Progress Notifications (from Skilljar)

Help users understand what's happening during long-running operations.

**Server-side API:**
```python
# Log messages
await context.info("Processing file 3 of 10...")

# Progress tracking
await context.report_progress(current=3, total=10)
```

**Client-side:** Provide `logging_callback` when creating `ClientSession`, `progress_callback` per tool call.

**Presentation varies by platform:** CLI (print), Web (WebSockets/SSE/polling), Desktop (progress bars/UI). Entirely optional — you can ignore them, show some types, or present however.

### 2.4 Elicitation — Server Requesting User Input

Elicitation allows servers to request structured input from users through the client:

```json
{
  "method": "elicitation/create",
  "params": {
    "message": "Please provide your GitHub username",
    "requestedSchema": {
      "type": "object",
      "properties": {
        "name": { "type": "string" }
      },
      "required": ["name"]
    }
  }
}
```

**Three response actions:**
| Action | Meaning |
|--------|---------|
| `accept` | User submitted data (content field has the data) |
| `decline` | User explicitly said no |
| `cancel` | User dismissed without choosing (closed dialog, pressed Escape) |

**Schema restrictions:** Flat objects with primitive properties only (string, number, boolean, enum). NO nested objects or arrays.

**Security:** Servers MUST NOT request sensitive information. Clients SHOULD show which server is requesting and allow declining.

**Exam trap:** Elicitation is a CLIENT feature (declared in client capabilities), even though the SERVER initiates the request.

### 2.5 Completion — Autocompletion for Arguments

Servers can provide autocomplete suggestions for prompt arguments and resource URI templates:

```json
{
  "method": "completion/complete",
  "params": {
    "ref": { "type": "ref/prompt", "name": "code_review" },
    "argument": { "name": "language", "value": "py" }
  }
}
```

Response: `{ "values": ["python", "pytorch", "pyside"], "total": 10, "hasMore": true }`

**Rules:** Max 100 suggestions per response. Two ref types: `ref/prompt` and `ref/resource`.

---

## Course 3: Introduction to Subagents

### 3.1 Built-in Subagents

| Subagent | Model | Tools | Purpose |
|----------|-------|-------|---------|
| **Explore** | Haiku (fast) | Read-only (no Write/Edit) | Codebase search, file discovery |
| **Plan** | Inherits | Read-only | Planning, architecture analysis |
| **General-purpose** | Inherits | Inherits all | Flexible delegation |

Claude delegates to Explore when it needs to search/analyze without changes. This keeps exploration out of your main context window.

### 3.2 Subagent Definition — YAML Frontmatter + Markdown

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. Analyze code and provide specific, actionable feedback.
```

The frontmatter configures the subagent. The markdown body becomes the **system prompt**. Subagents receive ONLY this system prompt (plus basic environment details), NOT the full Claude Code system prompt.

### 3.3 Subagent Scopes (Priority Order)

| Scope | Location | Priority |
|-------|----------|----------|
| `--agents` CLI flag | JSON in CLI command | 1 (highest) |
| Project | `.claude/agents/` | 2 |
| User | `~/.claude/agents/` | 3 |
| Plugin | Plugin's `agents/` directory | 4 (lowest) |

**Plugin subagent restriction:** Plugin subagents do NOT support `hooks`, `mcpServers`, or `permissionMode` (security reasons). Copy to `.claude/agents/` if you need those features.

### 3.4 Key Frontmatter Fields

| Field | Required? | Description |
|-------|-----------|-------------|
| `name` | Yes | Unique ID (lowercase + hyphens) |
| `description` | Yes | When Claude should delegate (used for auto-delegation) |
| `tools` | No | Allowlist of tools. Inherits all if omitted |
| `disallowedTools` | No | Denylist. Removed from inherited set |
| `model` | No | `sonnet`, `opus`, `haiku`, full model ID, or `inherit` |
| `permissionMode` | No | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | No | Max agentic turns before stopping |
| `skills` | No | Skills to preload into context at startup |
| `mcpServers` | No | MCP servers scoped to this subagent |
| `hooks` | No | Lifecycle hooks scoped to this subagent |
| `memory` | No | Persistent memory: `user`, `project`, or `local` |
| `background` | No | `true` to always run as background task |
| `isolation` | No | `worktree` for isolated git worktree |
| `effort` | No | `low`, `medium`, `high`, `max` |
| `initialPrompt` | No | Auto-submitted first user turn when running as main agent |

### 3.5 Tool Access Control

**Allowlist (tools field):**
```yaml
tools: Read, Grep, Glob, Bash
```
Only these tools are available. No Write, Edit, or MCP tools.

**Denylist (disallowedTools field):**
```yaml
disallowedTools: Write, Edit
```
Everything EXCEPT Write and Edit is available.

**If both set:** `disallowedTools` is applied first, then `tools` resolves against the remaining pool.

**Restricting subagent spawning:**
```yaml
tools: Agent(worker, researcher), Read, Bash
```
Only `worker` and `researcher` subagents can be spawned. Omit `Agent` entirely to prevent spawning any subagents.

### 3.6 Scoping MCP Servers to Subagents

```yaml
mcpServers:
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  - github  # Reference to already-configured server
```

Inline MCP servers are connected when the subagent starts and disconnected when it finishes. This keeps MCP tool descriptions out of the main conversation context.

### 3.7 Critical Constraints

- **Subagents CANNOT spawn other subagents.** If you need nested delegation, chain subagents from the main conversation.
- **Foreground subagents** block the main conversation. Permission prompts pass through to the user.
- **Background subagents** run concurrently. They auto-deny any permissions not pre-approved before launch.
- **Subagent context is isolated.** They don't inherit the parent's conversation history. Context must be explicitly passed.

### 3.8 Invoking Subagents

| Method | How | When |
|--------|-----|------|
| Natural language | "Use the code-reviewer to check my changes" | Claude decides whether to delegate |
| @-mention | `@"code-reviewer (agent)" review auth changes` | Guarantees the specific subagent runs |
| `--agent` flag | `claude --agent code-reviewer` | Entire session runs as that subagent |

### 3.9 Persistent Memory

```yaml
memory: project  # Stores in .claude/agent-memory/<name>/
```

| Scope | Location | Use When |
|-------|----------|----------|
| `user` | `~/.claude/agent-memory/<name>/` | Knowledge applies across all projects |
| `project` | `.claude/agent-memory/<name>/` | Project-specific, shareable via git |
| `local` | `.claude/agent-memory-local/<name>/` | Project-specific, NOT in git |

When memory is enabled, the first 200 lines / 25KB of `MEMORY.md` is auto-loaded into context.

### 3.10 Resuming Subagents

Completed subagents can be resumed via `SendMessage` with the agent ID. Resumed subagents retain their full conversation history. Transcripts are stored at `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl`.

---

## Course 4: Introduction to Agent Skills

### 4.1 What Are Skills?

Skills are SKILL.md files that extend Claude's capabilities. They're **prompt-based** — they give Claude instructions and let it orchestrate work using tools. Skills are NOT executable code (unlike hooks).

**Skill = YAML frontmatter + Markdown instructions**

```markdown
---
name: code-reviewer
description: Reviews code changes for security vulnerabilities
allowed-tools: Read, Grep, Glob
---

When reviewing code, check for:
1. SQL injection / XSS
2. Authentication bypass
3. Secrets in source code
```

### 4.2 Bundled Skills (Built-in)

| Skill | Purpose |
|-------|---------|
| `/batch <instruction>` | Orchestrate large-scale parallel changes (5-30 workers in isolated worktrees) |
| `/claude-api` | Load Claude API reference for your language |
| `/debug [description]` | Enable debug logging, troubleshoot issues |
| `/loop [interval] <prompt>` | Run a prompt repeatedly (polling, monitoring) |
| `/simplify [focus]` | Review recent changes for code reuse/quality issues |

### 4.3 Skill Locations (Priority Order)

| Level | Location | Scope |
|-------|----------|-------|
| Enterprise | Managed settings | All users in org |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Where plugin is enabled |

**Priority:** enterprise > personal > project. Plugin skills use namespaced names (`plugin-name:skill-name`) so they never conflict.

**Note:** `.claude/commands/` still works. If a skill and command share the same name, the skill wins.

### 4.4 Frontmatter Fields

| Field | Purpose |
|-------|---------|
| `name` | Display name and `/slash-command` |
| `description` | When to use it (Claude uses this for auto-invocation) |
| `disable-model-invocation` | `true` = only user can invoke (e.g., `/deploy`) |
| `user-invocable` | `false` = hide from `/` menu (background knowledge only) |
| `allowed-tools` | Tools Claude can use without asking permission |
| `model` | Model override when skill is active |
| `effort` | Effort level override |
| `context` | `fork` = run in a forked subagent context |
| `agent` | Which subagent type executes the forked skill |
| `hooks` | Lifecycle hooks scoped to this skill |
| `paths` | Glob patterns for conditional activation |
| `argument-hint` | Autocomplete hint (e.g., `[issue-number]`) |

### 4.5 Invocation Control — Key Exam Concept

| Setting | You can invoke? | Claude can invoke? |
|---------|----------------|-------------------|
| (default) | Yes | Yes |
| `disable-model-invocation: true` | Yes | No |
| `user-invocable: false` | No | Yes |

**When to use each:**
- `disable-model-invocation: true` → Skills with side effects: `/deploy`, `/commit`, `/send-slack`
- `user-invocable: false` → Background knowledge Claude should know but isn't a meaningful user action

### 4.6 String Substitutions

| Variable | Meaning |
|----------|---------|
| `$ARGUMENTS` | All arguments passed after `/skill-name` |
| `$ARGUMENTS[0]` or `$0` | First argument by position |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_SKILL_DIR}` | Directory containing the skill's SKILL.md |

### 4.7 Dynamic Context Injection — `!` backtick syntax

The `!`command`` syntax runs shell commands BEFORE the skill content is sent to Claude:

```markdown
---
name: pr-summary
context: fork
agent: Explore
---

## PR Context
- PR diff: !`gh pr diff`
- Changed files: !`gh pr diff --name-only`

Summarize this pull request.
```

This is **preprocessing** — Claude only sees the output, not the command itself.

### 4.8 Running Skills in a Subagent (context: fork)

```yaml
context: fork
agent: Explore
```

The skill content becomes the prompt for the subagent. The subagent runs in isolation and returns results to the main conversation.

**Important:** `context: fork` only makes sense for skills with explicit task instructions. A guidelines-only skill (e.g., "use these API conventions") will return without meaningful output because the subagent has no actionable prompt.

**Skills vs Subagents — Two Directions:**

| Pattern | System Prompt Source | Task Source |
|---------|---------------------|-------------|
| Skill with `context: fork` | Agent type (Explore, Plan) | SKILL.md content |
| Subagent with `skills` field | Subagent's markdown body | Claude's delegation message |

### 4.9 Supporting Files

```
my-skill/
├── SKILL.md           # Main instructions (required)
├── reference.md       # Detailed API docs
├── examples.md        # Usage examples
└── scripts/
    └── helper.py      # Utility script
```

Keep SKILL.md under 500 lines. Move detailed reference material to separate files and reference them from SKILL.md.

---

## Course 4B: Hooks — Complete Reference (from MCP Advanced Topics & Claude Code in Action)

### Hook Event Lifecycle

Hooks fire at specific points during Claude Code sessions. Four hook handler types:

| Type | How It Works |
|------|-------------|
| `command` | Runs a shell command; input via stdin, output via stdout/exit code |
| `http` | Sends HTTP POST; input as request body, output as response body |
| `prompt` | Single-turn LLM evaluation; returns `{ "ok": true/false }` |
| `agent` | Multi-turn subagent with tool access; returns `{ "ok": true/false }` |

### Complete Hook Events Table

| Event | When It Fires | Can Block? | Matcher |
|-------|--------------|-----------|---------|
| **SessionStart** | Session begins/resumes | No | startup, resume, clear, compact |
| **InstructionsLoaded** | CLAUDE.md/.claude/rules loaded | No | load reason |
| **UserPromptSubmit** | User submits prompt | Yes | (none) |
| **PreToolUse** | Before tool executes | Yes | tool name |
| **PermissionRequest** | Permission dialog shown | Yes | tool name |
| **PostToolUse** | After tool succeeds | Feedback only | tool name |
| **PostToolUseFailure** | After tool fails | Feedback only | tool name |
| **Notification** | Notification sent | No | notification type |
| **SubagentStart** | Subagent spawned | No | agent type |
| **SubagentStop** | Subagent finishes | Yes | agent type |
| **TaskCreated** | Task being created | Yes | (none) |
| **TaskCompleted** | Task marked complete | Yes | (none) |
| **Stop** | Claude finishes responding | Yes | (none) |
| **StopFailure** | Turn ends due to API error | No | error type |
| **TeammateIdle** | Teammate about to go idle | Yes | (none) |
| **ConfigChange** | Config file changes | Yes | config source |
| **CwdChanged** | Working directory changes | No | (none) |
| **FileChanged** | Watched file changes | No | filename |
| **WorktreeCreate** | Worktree being created | Replaces default | (none) |
| **WorktreeRemove** | Worktree being removed | No | (none) |
| **PreCompact** | Before compaction | No | manual, auto |
| **PostCompact** | After compaction | No | manual, auto |
| **Elicitation** | MCP server requests user input | Yes | MCP server name |
| **ElicitationResult** | User responds to elicitation | Yes | MCP server name |
| **SessionEnd** | Session terminates | No | exit reason |

### Exit Code Semantics

| Exit Code | Meaning | Effect |
|-----------|---------|--------|
| 0 | Success | Proceed; parse stdout for JSON |
| 2 | Blocking error | Block action; stderr fed to Claude |
| Other | Non-blocking error | Continue; stderr shown in verbose mode |

### PreToolUse Decision Control (Most Exam-Relevant)

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Approved by policy",
    "updatedInput": { "command": "npm run lint" },
    "additionalContext": "Running in production environment"
  }
}
```

Three decisions: `allow` (skip permission prompt), `deny` (block tool call), `ask` (prompt user).

`updatedInput` can modify tool parameters before execution.

### MCP Tool Matching in Hooks

MCP tools follow naming: `mcp__<server>__<tool>`
- `mcp__memory__create_entities` → Memory server's create tool
- `mcp__.*__write.*` → Any write tool from any server

### Hook Location Priority

| Location | Scope |
|----------|-------|
| `~/.claude/settings.json` | All projects |
| `.claude/settings.json` | Single project (committable) |
| `.claude/settings.local.json` | Single project (gitignored) |
| Managed policy settings | Organization-wide |
| Plugin `hooks/hooks.json` | Where plugin is enabled |
| Skill/agent frontmatter | While component is active |

### Async Hooks

```json
{
  "type": "command",
  "command": "/path/to/run-tests.sh",
  "async": true,
  "timeout": 120
}
```

Async hooks run in background — they CANNOT block tool calls or return decisions. Only `type: "command"` supports `async`.

---

## Exam-Critical Mnemonics

### MCP Primitives (T-R-P)
- **T**ools = Model-controlled (LLM decides)
- **R**esources = Application-controlled (app decides)
- **P**rompts = User-controlled (user selects)

### Client Features (S-E-R)
- **S**ampling = Server asks client to call LLM
- **E**licitation = Server asks client for user input
- **R**oots = Client tells server filesystem boundaries

### Hook Exit Codes (0-2-other)
- **0** = Success, parse JSON
- **2** = Block the action
- **Other** = Non-blocking error, continue

### Subagent Constraints
- **Cannot nest** — Subagents can't spawn subagents
- **Background auto-denies** — Pre-approve permissions before launch
- **Context is fresh** — No parent conversation history inherited

### Tool Annotations — UNTRUSTED
- Self-reported by server
- NEVER make security decisions based on annotations alone
- Always verify through server trustworthiness assessment

---

## 10 Most Likely Exam Questions from These Courses

1. When should you use Streamable HTTP vs stdio transport? (And what do `stateless_http` / `json_response` control?)
2. What is MCP sampling and who holds the API keys? (Server asks client; cost shifts to client)
3. Who declares MCP roots — client or server? (Client. SDK doesn't auto-enforce — developer must implement)
4. What distinguishes tools from resources from prompts? (Control dimension: model / app / user)
5. Are tool annotations security guarantees? (NO — self-reported, untrusted)
6. Can subagents spawn other subagents? (NO — chain from main conversation)
7. What's the difference between `tools` and `disallowedTools` in subagent config?
8. When should you use `disable-model-invocation: true` on a skill? (Side-effect skills: deploy, commit)
9. Which hook event blocks tool calls? (PreToolUse with exit code 2)
10. How does elicitation work — who initiates, who responds? (Server initiates, client mediates, user responds)

---

*Document compiled from: Verified Skilljar courses (Intro MCP, MCP Advanced Topics — authenticated access), code.claude.com/docs/en/sub-agents, code.claude.com/docs/en/skills, code.claude.com/docs/en/hooks*

---

## Appendix: Skilljar Assessment Questions (Actual Exam-Style)

### MCP Advanced Topics Assessment (10/10 scored)

1. Server needs Claude for summarizing but shouldn't handle API costs → **Sampling**
2. "Call Tool Request" expecting results back = what message pattern? → **Request-result message**
3. StreamableHTTP sends progress without server-initiated HTTP? → **Server-Sent Events (SSE) connections**
4. User asks to "convert video.mp4" but Claude doesn't know location → **Roots**
5. Simpler HTTP responses, final result as plain JSON? → **json_response=True**
6. Simplest local dev testing on same machine? → **Stdio transport**
7. Which transport requires same machine? → **Stdio transport**
8. What are roots in MCP? → **System that tells MCP servers what files/folders it can access**
9. Correct initialization sequence? → **Initialize Request → Initialize Result → Initialized Notification**
10. What is sampling in MCP? → **Way for servers to access language models through connected MCP clients**

### Introduction to MCP Assessment (7/7 scored)

1. What does MCP stand for? → **Model Context Protocol**
2. What are the three MCP server primitives? → **Tools, Resources, Prompts**
3. Who controls tool invocation? → **The model (LLM decides when to call)**
4. Who controls resource attachment? → **The application (app decides when to attach)**
5. Who controls prompt selection? → **The user (user explicitly selects)**
6. What is the role of an MCP client? → **Protocol connector inside the host; maintains 1:1 connection with a server**
7. What format does MCP use for messages? → **JSON-RPC 2.0**
