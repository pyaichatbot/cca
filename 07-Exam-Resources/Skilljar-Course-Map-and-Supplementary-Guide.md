# Anthropic Skilljar Course Map & Supplementary Study Guide
## Claude Certified Architect – Foundations Exam Preparation

**Purpose:** Maps all 15 Anthropic Academy courses to CCA exam domains, identifies content gaps in our study kit, and provides supplementary material to fill those gaps.

**Last Updated:** March 2026

---

## Part 1: Skilljar Course → Exam Domain Mapping

### Tier 1: Directly Exam-Relevant (Must Complete)

| Course | URL | CCA Domains Covered | Priority |
|--------|-----|---------------------|----------|
| **Claude Code in Action** | anthropic.skilljar.com/claude-code-in-action | D1 (hooks), D2 (MCP config), D3 (CLAUDE.md, commands, plan mode, CI/CD) | **Critical** |
| **Building with the Claude API** | anthropic.skilljar.com/claude-with-the-anthropic-api | D1 (agentic loops, tool_use), D4 (prompts, structured output, batch), D5 (context) | **Critical** |
| **Introduction to Model Context Protocol** | anthropic.skilljar.com/introduction-to-model-context-protocol | D2 (MCP primitives, server building, tool/resource/prompt selection) | **Critical** |
| **Introduction to Subagents** | anthropic.skilljar.com/introduction-to-subagents | D1 (coordinator-subagent, context passing, task delegation) | **Critical** |
| **Introduction to Agent Skills** | anthropic.skilljar.com/introduction-to-agent-skills | D3 (custom skills, SKILL.md, plugin distribution) | **High** |
| **MCP Advanced Topics** | anthropic.skilljar.com/model-context-protocol-advanced-topics | D2 (transport, sampling, roots, production scaling) | **High** |

### Tier 2: Supportive Context

| Course | URL | Relevance |
|--------|-----|-----------|
| **Claude 101** | anthropic.skilljar.com/claude-101 | Foundation — skip if experienced |
| **AI Fluency: Framework & Foundations** | anthropic.skilljar.com/ai-fluency-framework-and-foundations | General AI literacy — low exam relevance |
| **Claude with Amazon Bedrock** | anthropic.skilljar.com/claude-in-amazon-bedrock | Platform-specific — not directly tested |
| **Claude with Google Cloud's Vertex AI** | anthropic.skilljar.com/claude-with-google-vertex | Platform-specific — not directly tested |
| **Introduction to Claude Cowork** | anthropic.skilljar.com/introduction-to-claude-cowork | Cowork-specific — not on exam |
| **AI Fluency for Educators/Students/Nonprofits** | anthropic.skilljar.com | Audience-specific — not exam relevant |

### Tier 3: Not Exam Relevant

Teaching AI Fluency, Driving Enterprise Adoption — skip for exam prep.

---

## Part 2: Gap Analysis — What Skilljar Covers That Our Kit Needs

After cross-referencing the 6 Tier-1 Skilljar courses against our existing study guides, training sessions, and exercises, here are the identified gaps:

### Gap 1: MCP Transport Mechanisms (MCP Advanced Topics)
**Status:** Partially covered in Domain 2 study guide, but lacking depth on transport selection

Our kit covers MCP tool/resource/prompt primitives and `.mcp.json` configuration well. However, the MCP Advanced Topics course covers **transport-layer decisions** that could appear in exam scenarios about production deployment:

**Supplementary Content:**

#### Stdio vs StreamableHTTP Transport

**Stdio transport** is the default for local MCP servers. The client spawns the server as a child process, and they communicate through stdin/stdout pipes.

```json
// .mcp.json — stdio transport (local)
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/project"]
    }
  }
}
```

**StreamableHTTP transport** enables remote MCP servers over HTTP with Server-Sent Events for server→client streaming. Required for production deployments where the MCP server runs on a separate host.

```python
# StreamableHTTP server setup
from mcp.server import Server
from mcp.server.streamable_http import StreamableHTTPServerTransport

app = Server("production-mcp")
transport = StreamableHTTPServerTransport(app)
# Runs on HTTP endpoint, supports horizontal scaling
```

**Exam Trap:** The exam may ask when to use stdio vs HTTP transport. Stdio is simpler and lower latency for local servers. StreamableHTTP is required for remote/cloud deployment and horizontal scaling behind load balancers.

#### MCP Sampling

Sampling allows MCP servers to request LLM completions through the connected client — the server doesn't call the LLM directly; it sends a sampling request back to the client.

```python
@app.tool()
async def analyze_with_ai(ctx, data: str) -> str:
    # Server requests an LLM call through the client
    result = await ctx.session.create_message(
        messages=[{"role": "user", "content": data}],
        max_tokens=500
    )
    return result.content
```

**Key Concept:** Sampling maintains the security boundary — the MCP server never holds API keys. The client controls which models are used and applies any content filtering.

#### MCP Roots

Roots define the file system boundaries an MCP server can access. They're permission scopes that clients expose to servers.

```python
# Client declares which directories the server may access
roots = [
    {"uri": "file:///project/src", "name": "Source Code"},
    {"uri": "file:///project/docs", "name": "Documentation"}
]
```

**Exam Trap:** Roots are declared by the client, not the server. The server can request root access, but the client decides what to grant. This is a security boundary pattern that parallels tool access scoping in Domain 2.

---

### Gap 2: Claude Code SDK & Hooks Deep Dive (Claude Code in Action)
**Status:** Hooks covered in Domain 1 (Task 1.5) and Domain 3, but SDK integration patterns need reinforcement

The Skilljar course includes a dedicated section on the Claude Code SDK that bridges hooks, subagents, and programmatic Claude Code usage. Key supplementary concepts:

#### Hook Event Types — Complete Reference

```json
// .claude/hooks.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "node .claude/hooks/lint-before-write.js"
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "command": "python .claude/hooks/normalize-output.py"
      }
    ],
    "UserPromptSubmit": [
      {
        "command": "python .claude/hooks/prompt-classifier.py"
      }
    ],
    "Stop": [
      {
        "command": "python .claude/hooks/session-summary.py"
      }
    ]
  }
}
```

| Hook | Fires When | Use Case | Deterministic? |
|------|-----------|----------|---------------|
| **PreToolUse** | Before a tool executes | Block dangerous operations, validate params | Yes |
| **PostToolUse** | After a tool returns | Normalize data, log results, format output | Yes |
| **UserPromptSubmit** | User sends a message | Classify intent, inject context, route | Yes |
| **Stop** | Agent completes turn | Save summaries, trigger follow-up actions | Yes |

**Exam Trap:** Hooks provide **deterministic guarantees** — they always execute. Prompt instructions are probabilistic. When the exam asks about enforcing compliance rules (e.g., blocking refunds > $500), hooks are the correct answer, not system prompts.

#### SDK Programmatic Usage

```python
# Using Claude Code SDK programmatically
from claude_code import claude_code

# Run Claude Code as a subprocess with structured output
result = claude_code(
    prompt="Review this PR for security issues",
    options={
        "output_format": "json",
        "max_turns": 5,
        "system_prompt": "You are a security reviewer..."
    }
)
```

**Key Concept:** The `-p` flag (non-interactive/pipe mode) and `--output-format json` are essential for CI/CD integration. The SDK wraps this into a programmatic interface.

---

### Gap 3: Agent Skills Architecture (Introduction to Agent Skills)
**Status:** Skills mentioned in Domain 3 (Task 3.2) but Skilljar course reveals deeper patterns

#### SKILL.md Frontmatter Structure

```markdown
---
name: code-reviewer
description: Reviews code changes for security vulnerabilities and best practices
allowed-tools: Read, Grep, Glob, Bash
---

# Code Review Skill

When reviewing code, follow these steps:
1. Read the changed files
2. Check for security vulnerabilities (OWASP Top 10)
3. Verify error handling patterns
4. Report findings with severity ratings
```

**Key Concepts from Skilljar:**

**Trigger matching** — Claude matches skills to tasks using the `description` field. A vague description causes false triggers or missed activations. This directly parallels tool description design in Domain 2.

**Progressive disclosure** — Skills can organize instructions in layers. Top-level instructions execute always; nested sections activate only when relevant sub-tasks arise.

**Distribution hierarchy:**
1. **Repository commit** — `.claude/skills/` directory, shared via git
2. **Plugin packaging** — Bundled as installable plugin for cross-repo sharing
3. **Enterprise managed settings** — Org-wide deployment by admins

**Exam Trap:** Skills are markdown files that Claude reads and follows — they're NOT executable code. They influence behavior through prompt injection into context, not through programmatic execution. This distinguishes them from hooks (which are executable scripts).

---

### Gap 4: Subagent Context Isolation (Introduction to Subagents)
**Status:** Covered in Domain 1 (Task 1.3) but Skilljar reveals practical patterns worth reinforcing

#### The /agents Command Pattern

```markdown
<!-- .claude/agents/security-reviewer.md -->
---
name: security-reviewer
description: Reviews code for security vulnerabilities
allowed-tools: Read, Grep, Glob
---

You are a security reviewer. Analyze code for:
- SQL injection vulnerabilities
- XSS attack surfaces
- Authentication bypass risks
- Secrets in source code

Return findings as structured JSON with severity levels.
```

**Key Concepts from Skilljar:**

**Context isolation is the default** — Subagents get a fresh context window. They don't inherit the parent's conversation history. Any context they need must be explicitly passed in the invocation prompt.

**Structured output contracts** — Well-designed subagents return structured results (JSON, specific markdown format) so the coordinator can reliably parse and aggregate responses.

**Obstacle reporting** — Subagents should report what they couldn't accomplish, not just what they did. The coordinator needs failure context to decide whether to retry, reassign, or escalate.

**Tool access limits** — Subagents should only get tools relevant to their role. A `security-reviewer` agent doesn't need Write or Edit — only Read and Grep.

---

### Gap 5: Building with Claude API — Extended Thinking & Prompt Caching
**Status:** Partially covered in Domain 4, but Skilljar course reveals exam-relevant API features

#### Extended Thinking Mode

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # Dedicated thinking budget
    },
    messages=[{"role": "user", "content": "Analyze this architecture..."}]
)

# Response contains both thinking and text blocks
for block in response.content:
    if block.type == "thinking":
        print(f"Reasoning: {block.thinking}")
    elif block.type == "text":
        print(f"Answer: {block.text}")
```

**Key Concept:** Extended thinking gives Claude a dedicated "scratchpad" for complex reasoning before responding. The `budget_tokens` parameter controls how much thinking is allowed. This is relevant to Domain 5 (context management) and Domain 4 (prompt engineering for complex tasks).

#### Prompt Caching

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "You are a legal document analyzer...",
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[{"role": "user", "content": "Analyze clause 7.2..."}]
)
```

**Key Concept:** Prompt caching reduces costs by caching frequently-reused context (system prompts, large documents). Cached input tokens cost 90% less. This is a production optimization that combines Domain 4 (prompt design) and Domain 5 (context efficiency).

**Exam Trap:** Prompt caching works with `cache_control: {"type": "ephemeral"}` on system messages. The cache is per-model, per-prompt-prefix. Changing any token before the cached block invalidates the entire cache.

#### Batch API

```python
# Create batch request — 50% cost reduction
batch = client.batches.create(
    requests=[
        {
            "custom_id": "review-file-1",
            "params": {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": "Review file 1..."}]
            }
        },
        {
            "custom_id": "review-file-2",
            "params": {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": "Review file 2..."}]
            }
        }
    ]
)
# Results arrive within 24 hours, matched by custom_id
```

**Key Concept:** Batch API provides 50% cost savings for non-time-sensitive workloads. Results are matched back using `custom_id`. Maximum 24-hour processing window. This is the correct answer when the exam asks about cost optimization for bulk processing tasks.

---

## Part 3: Recommended Skilljar Study Sequence for CCA

Complete these courses in this order to maximize exam readiness:

| Week | Day | Course | Duration | Exam Domains |
|------|-----|--------|----------|-------------|
| 1 | Mon-Tue | Building with the Claude API | 4-5 hrs | D1, D4, D5 |
| 1 | Wed | Introduction to Model Context Protocol | 2-3 hrs | D2 |
| 1 | Thu-Fri | Claude Code in Action | 4-5 hrs | D1, D2, D3 |
| 2 | Mon | Introduction to Subagents | 1-2 hrs | D1 |
| 2 | Tue | Introduction to Agent Skills | 1-2 hrs | D3 |
| 2 | Wed | MCP Advanced Topics | 2-3 hrs | D2 |
| 2 | Thu-Fri | Review study guides + mock tests | 4-6 hrs | All |

**Total estimated time:** 18-26 hours across 2 weeks

---

## Part 4: Concepts Tested That Only Appear in Skilljar (Not in Exam Guide PDF)

Based on cross-referencing the Skilljar courses with the official exam guide, these concepts appear in course materials and are fair game for exam questions, even though the exam guide describes them only at the task-statement level:

1. **StreamableHTTP vs Stdio transport selection** — MCP Advanced Topics
2. **MCP Sampling pattern** (server requesting LLM calls through client) — MCP Advanced Topics
3. **MCP Roots permission model** — MCP Advanced Topics
4. **SKILL.md frontmatter and trigger matching** — Agent Skills
5. **`/agents` command for custom subagent definitions** — Subagents
6. **Obstacle reporting pattern in subagents** — Subagents
7. **Extended thinking `budget_tokens` parameter** — Building with Claude API
8. **Prompt caching `cache_control` mechanics** — Building with Claude API
9. **Hook event types: UserPromptSubmit, Stop** — Claude Code in Action
10. **Claude Code SDK programmatic interface** — Claude Code in Action
11. **`# ` shortcut for adding memory to CLAUDE.md** — Claude Code in Action
12. **Progressive disclosure in skill organization** — Agent Skills

---

## Part 5: Quick-Fire Exam Q&A from Skilljar Content

**Q: An MCP server needs to call Claude to analyze data it received. How should this be implemented?**
A: Use MCP sampling — the server sends a `create_message` request to the client, which handles the LLM call. The server never holds API keys.

**Q: Your team deploys an MCP server to a cloud environment behind a load balancer. Which transport should you use?**
A: StreamableHTTP. Stdio requires the client to spawn the server as a child process (local only). HTTP transport supports stateless horizontal scaling.

**Q: A CI/CD pipeline needs to run Claude Code for automated code review. What flags are required?**
A: `-p` (pipe/non-interactive mode) and `--output-format json` for machine-parseable output.

**Q: You want to ensure all file writes pass a linter before Claude saves them. What's the most reliable approach?**
A: PreToolUse hook with matcher `Write|Edit` that runs the linter. Hooks are deterministic — they always execute. System prompt instructions can be skipped.

**Q: How does prompt caching reduce costs for a document analysis system that processes many queries against the same document?**
A: Place the document in the system message with `cache_control: {"type": "ephemeral"}`. Cached input tokens cost 90% less. All subsequent queries reuse the cached prefix.

**Q: A custom skill isn't triggering when expected. What's the most likely cause?**
A: The skill's `description` field doesn't match the task pattern. Improve the description with specific trigger phrases and edge case examples — this parallels tool description design.

**Q: Your subagent returns a vague "analysis complete" message. How do you improve it?**
A: Define a structured output contract in the subagent's prompt — require JSON with specific fields (findings, severity, confidence). Also require obstacle reporting for anything the subagent couldn't analyze.

**Q: When should you use extended thinking vs standard responses?**
A: Extended thinking for complex multi-step reasoning (architecture analysis, mathematical proofs, complex code review). Standard for simple queries and structured extraction. Extended thinking costs more tokens but improves accuracy on hard problems.

---

## Sources

- [Anthropic Academy — Course Catalog](https://anthropic.skilljar.com/)
- [Claude Code in Action](https://anthropic.skilljar.com/claude-code-in-action)
- [Building with the Claude API](https://anthropic.skilljar.com/claude-with-the-anthropic-api)
- [Introduction to Model Context Protocol](https://anthropic.skilljar.com/introduction-to-model-context-protocol)
- [MCP Advanced Topics](https://anthropic.skilljar.com/model-context-protocol-advanced-topics)
- [Introduction to Subagents](https://anthropic.skilljar.com/introduction-to-subagents)
- [Introduction to Agent Skills](https://anthropic.skilljar.com/introduction-to-agent-skills)
- [How to Become a Claude Certified Architect — LowCode Agency](https://www.lowcode.agency/blog/how-to-become-claude-certified-architect)
- [CCA Exam Technical Roadmap — DEV Community](https://dev.to/mcrolly/how-to-prepare-for-the-claude-certified-architect-exam-a-technical-roadmap-2jgi)
