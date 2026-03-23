# Exercise 2: Configure Claude Code for Team Development

## Overview

This exercise walks you through building a **production-ready Claude Code configuration** for a team development environment. You'll implement advanced features from both Domain 3 (Claude Code Configuration & Workflows) and Domain 2 (Tool Design & MCP Integration).

By completing this exercise, you'll understand:
- How to structure CLAUDE.md files across project hierarchy
- How to use @import for referencing external standards
- How to create conditional rule loading with .claude/rules/
- How to build custom slash commands and skills
- How to configure MCP servers at the project level
- Decision frameworks for plan mode vs direct execution

**Time to complete:** 45-60 minutes
**Prerequisites:** Basic understanding of Claude Code, MCP, and directory-based configuration

---

## What You'll Build

A mock team development project with:
- **Project structure** for a TypeScript backend application
- **Multi-level CLAUDE.md hierarchy** with environment-aware configuration
- **5 custom rules files** with conditional loading based on project context
- **Custom slash commands** for PR reviews and code scanning
- **Reusable skills** for common development tasks
- **MCP server configuration** with GitHub and database integration
- **Tool design patterns** demonstrating best practices

---

## Directory Structure

```
team-dev-project/
├── README.md (project overview)
├── CLAUDE.md (root configuration)
│
├── .claude/ (Claude Code configuration directory)
│   ├── CLAUDE.md (project-level configuration)
│   ├── rules/
│   │   ├── backend-standards.yaml (backend coding rules)
│   │   ├── testing-standards.yaml (testing requirements)
│   │   ├── security-standards.yaml (security rules)
│   │   ├── documentation-standards.yaml (doc rules)
│   │   └── performance-standards.yaml (performance rules)
│   ├── commands/
│   │   ├── review-pr.md (slash command for PR reviews)
│   │   ├── scan-security.md (slash command for security scanning)
│   │   └── generate-docs.md (slash command for doc generation)
│   ├── skills/
│   │   ├── code-review/
│   │   │   └── SKILL.md (code review skill)
│   │   ├── api-design/
│   │   │   └── SKILL.md (API design skill)
│   │   └── testing/
│   │       └── SKILL.md (testing skill)
│   └── .mcp.json (MCP server configuration)
│
├── src/ (backend source code)
│   ├── api/
│   ├── services/
│   ├── middleware/
│   └── utils/
│
├── tests/ (test directory with CLAUDE.md)
│   ├── CLAUDE.md (test-specific rules)
│   ├── unit/
│   └── integration/
│
├── docs/ (documentation with CLAUDE.md)
│   ├── CLAUDE.md (documentation guidelines)
│   └── api-reference.md
│
└── package.json
```

---

## Configuration Walkthrough

### Step 1: Root CLAUDE.md (`/CLAUDE.md`)

The root configuration provides global context for the entire workspace.

**Key concepts:**
- Acts as the "catch-all" configuration when no more specific CLAUDE.md exists
- Should be minimal and only include workspace-wide standards
- Uses @import to reference external standards files from .claude/rules/
- Sets environment-level defaults

**Why it matters:**
- Provides consistency across all directories
- Allows centralized updates without editing multiple files
- Demonstrates hierarchy principle: specific > general

### Step 2: Project-Level CLAUDE.md (`.claude/CLAUDE.md`)

More specific than root, this configuration is for the .claude/ directory and overrides root settings.

**Key concepts:**
- Imports specific rules from .claude/rules/ subdirectory
- Uses conditional loading to apply rules based on context
- References the MCP configuration (.mcp.json)
- Explains slash commands and skills defined in this project

**Why it matters:**
- Centralizes configuration management
- Shows how rules can be conditionally applied
- Demonstrates MCP integration at project level

### Step 3: Subdirectory-Specific CLAUDE.md (e.g., `tests/CLAUDE.md`)

Directory-specific configurations override parent configurations.

**Key concepts:**
- `tests/CLAUDE.md`: Relaxes documentation standards, emphasizes test coverage
- `docs/CLAUDE.md`: Enforces strict documentation standards
- Inherits parent rules but can override with @import of different rule sets

**Why it matters:**
- Shows how configuration adapts to different project contexts
- Demonstrates the "specificity cascade"
- Critical for large projects with diverse requirements

### Step 4: Rules Files with YAML Frontmatter (`.claude/rules/*.yaml`)

Each rule file uses YAML frontmatter with a `path` field for conditional loading.

**YAML Frontmatter Structure:**
```yaml
---
path: "*.ts,*.js"  # Apply to TypeScript/JavaScript files
conditions:        # Optional conditions for activation
  - directory: src/api
    not: true      # Don't apply in src/api
---
```

**Example: backend-standards.yaml**
```yaml
---
path: "src/**/*.ts"  # Apply to all TypeScript in src/
---

# Rule content describing coding standards
```

**Why it matters:**
- Allows precise control over which rules apply where
- Reduces cognitive load by showing only relevant rules
- Supports complex projects with different standards per area

### Step 5: Custom Slash Commands (`.claude/commands/*.md`)

Slash commands provide quick shortcuts for common tasks.

**Structure:**
```markdown
---
name: "review-pr"
description: "Review a pull request for code quality, design, and security"
argument-hint: "PR number or branch name"
---

# Implementation and instructions
```

**Key concepts:**
- Each slash command is a markdown file in .claude/commands/
- YAML frontmatter provides metadata
- Commands shown in the /help menu
- Can be context-aware (reference MCP servers for GitHub integration)

**Why it matters:**
- Accelerates common workflows
- Provides consistent, vetted processes
- Can be chained with other commands or skills

### Step 6: Skills (`.claude/skills/*/SKILL.md`)

Skills are reusable task templates with context control and tool restrictions.

**Skill Frontmatter:**
```yaml
---
name: "Code Review"
description: "Conduct thorough code review"
context: "fork"          # Run in isolated context
allowed-tools:           # Restrict tool usage
  - read_file
  - grep
  - bash
argument-hint: "file path or PR link"
---
```

**Key frontmatter fields:**
- `context: fork` - Runs in isolated context, doesn't affect main session
- `context: inherit` - Inherits current session context
- `allowed-tools` - Whitelist of tools the skill can use
- `argument-hint` - Help text for skill arguments
- `requires-confirmation` - Ask before executing dangerous operations

**Why it matters:**
- Provides safety boundaries for automated tasks
- Allows controlled delegation of complex workflows
- Demonstrates trust model and risk management

### Step 7: Project-Level .mcp.json

Configures MCP servers with environment variable expansion.

**Key concepts:**
- Located in .claude/ directory
- Defines available MCP servers (GitHub, database, etc.)
- Supports environment variable substitution (`${VAR_NAME}`)
- Tool descriptions follow best practices

**MCP Server Configuration Example:**
```json
{
  "mcp_servers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "GITHUB_OWNER": "${GITHUB_OWNER}",
        "GITHUB_REPO": "${GITHUB_REPO}"
      }
    }
  }
}
```

**Tool Description Best Practices:**
- Clear, concise descriptions (< 100 words)
- Include input/output specifications
- Document required parameters and environment variables
- Explain error conditions and how to handle them
- Provide examples when non-obvious

**Why it matters:**
- Centralizes tool configuration
- Supports environment-specific settings
- Allows secure credential handling through env vars

---

## Plan Mode vs Direct Execution Decision Guide

### When to Use Plan Mode

**Plan mode** has Claude create a detailed plan before executing:

```
claude code --plan true [task]
```

**Use plan mode when:**
- Making structural changes to project (new directories, refactoring)
- Deleting or modifying configuration files
- Running scripts that affect multiple systems
- Making decisions with lasting impact
- First time executing a new workflow
- Task involves uncertainty about best approach

**Example:**
```bash
claude code --plan true "Reorganize project structure for microservices"
```

### When to Use Direct Execution

**Direct execution** immediately performs the task:

```
claude code [task]
```

**Use direct execution when:**
- Making localized changes to a single file
- Bug fixes with clear scope
- Adding new features to established patterns
- Running analysis/reading tasks
- Using skills specifically designed for automation
- Task is reversible and low-risk

**Example:**
```bash
claude code "Add error handling to api/routes.ts"
```

### Decision Framework

```
Is this a critical system change?
├─ YES → Use plan mode (--plan true)
└─ NO → Is it easily reversible?
    ├─ YES → Direct execution OK
    └─ NO → Consider plan mode
```

---

## Domain 3 Exam Preparation: Key Patterns

### Pattern 1: CLAUDE.md Hierarchy

**Concept:** Files are resolved by proximity (most specific wins)

**Resolution order:**
1. `path/to/file/CLAUDE.md` (if exists)
2. `path/to/CLAUDE.md` (if exists)
3. `path/CLAUDE.md` (if exists)
4. `CLAUDE.md` (root)

**Exam question example:**
> You have a CLAUDE.md in /src/api/ that conflicts with the root CLAUDE.md. Which takes precedence?

**Answer:** The /src/api/CLAUDE.md takes precedence because it's more specific to the file location.

### Pattern 2: @import with External Standards

**Concept:** Reference external rule files to keep CLAUDE.md clean

**Example:**
```yaml
# In .claude/CLAUDE.md
standards:
  backend: "@import .claude/rules/backend-standards.yaml"
  testing: "@import .claude/rules/testing-standards.yaml"
```

**Benefits:**
- Separates concerns (one rule per file)
- Allows rule reuse across projects
- Makes rules discoverable in .claude/rules/

**Exam question example:**
> How would you share testing standards across 5 different projects?

**Answer:** Create a centralized testing-standards.yaml and @import it in each project's CLAUDE.md.

### Pattern 3: Conditional Rule Loading

**Concept:** Rules activate only for matching file types/directories

**YAML frontmatter:**
```yaml
---
path: "src/**/*.ts"           # TypeScript files in src/
conditions:
  - directory: src/api
    not: true                 # But NOT in src/api/
---
```

**Exam question example:**
> You want stricter linting for API files but looser rules for utilities. How do you implement this?

**Answer:** Create two rule files with different path and conditions in YAML frontmatter.

### Pattern 4: Custom Slash Commands

**Concept:** Quick-launch workflows from /help menu

**Structure:**
```markdown
---
name: "review-pr"
description: "Comprehensive PR review"
argument-hint: "PR number"
---

[Instructions for Claude to execute]
```

**Exam question example:**
> A team wants a /deploy command that checks security first. How do you implement this?

**Answer:** Create .claude/commands/deploy.md with security checks in the implementation section.

### Pattern 5: Skills with Context Isolation

**Concept:** Reusable tasks with controlled tool access

**Frontmatter:**
```yaml
---
name: "Code Review"
context: fork              # Isolated execution
allowed-tools:             # Explicit tool whitelist
  - read_file
  - grep
---
```

**Exam question example:**
> Why would you use `context: fork` for a code review skill?

**Answer:** To prevent the review from modifying files or accessing unauthorized tools, maintaining trust boundaries.

---

## Domain 2 Exam Preparation: Key Patterns

### Pattern 1: MCP Server Configuration

**Concept:** Project-level .mcp.json defines available tools

**Structure:**
```json
{
  "mcp_servers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

**Exam question example:**
> You need to securely pass database credentials to an MCP server. What's the best approach?

**Answer:** Use environment variables in the MCP configuration: `"DATABASE_URL": "${DATABASE_URL}"` and set the variable in your shell before running Claude Code.

### Pattern 2: Tool Description Best Practices

**Concept:** Clear tool documentation enables better tool use

**Good description:**
```
List GitHub issues for the current repository.

Inputs:
- repository: string (owner/repo format)
- state: string (open|closed|all, default: open)
- labels: string (comma-separated label names)

Returns: Array of issue objects with title, number, state, labels

Example: List all open issues with "bug" label
```

**Poor description:**
```
Get issues from GitHub
```

**Why it matters:**
- Claude uses descriptions to decide when to use tools
- Clear I/O specifications reduce errors
- Examples guide appropriate usage

**Exam question example:**
> Your MCP server tool isn't being called even though it should apply. What's likely the issue?

**Answer:** The tool description is unclear or doesn't explain what it does, so Claude doesn't know when to use it.

### Pattern 3: Environment Variable Expansion

**Concept:** Use ${VAR_NAME} for dynamic configuration

**Example:**
```json
"env": {
  "GITHUB_TOKEN": "${GITHUB_TOKEN}",
  "DATABASE_URL": "${DATABASE_URL}",
  "API_KEY": "${API_KEY}"
}
```

**Benefits:**
- No hardcoded secrets
- Configuration adapts to environment (dev/staging/prod)
- Different team members can use different credentials

**Exam question example:**
> How do you configure an MCP server for both development and production without duplicating .mcp.json?

**Answer:** Use environment variables: `"API_URL": "${API_URL}"` and set different values per environment.

---

## Exam Questions & Answers

### Question 1 (Domain 3)
**Q: You have a CLAUDE.md at the project root and another at /src/api/. How does Claude Code determine which rules to apply to /src/api/routes.ts?**

**A:** Claude uses proximity-based resolution. It will first check for /src/api/CLAUDE.md (most specific), then /src/CLAUDE.md, then /CLAUDE.md. For the routes.ts file in /src/api/, the /src/api/CLAUDE.md (if it exists) takes precedence.

### Question 2 (Domain 3)
**Q: Describe the three key reasons to use @import for external rule files.**

**A:**
1. **Separation of concerns** - Each rule file focuses on one domain (backend, testing, security)
2. **Reusability** - Rules can be referenced from multiple projects without duplication
3. **Maintainability** - Updating a standard affects all projects that import it

### Question 3 (Domain 3)
**Q: You want to enforce stricter naming conventions in API files but not in utility files. How would you configure this?**

**A:** Create a naming-standards.yaml rule file with YAML frontmatter:
```yaml
---
path: "src/api/**/*.ts"
conditions:
  - directory: src/utils
    not: true
---
[Strict naming convention rules]
```

### Question 4 (Domain 3)
**Q: What's the difference between a slash command and a skill? When would you use each?**

**A:**
- **Slash commands** are quick launchers from the /help menu. Use for frequently needed workflows that don't need tool restrictions.
- **Skills** are reusable task templates with controlled context and tool access. Use for complex, automated tasks that need safety boundaries.

### Question 5 (Domain 3)
**Q: When would you use `context: fork` vs `context: inherit` in a skill?**

**A:**
- `context: fork`: Use for potentially risky automated tasks (code generation, deployment) or when you don't want side effects affecting the main session.
- `context: inherit`: Use for skills that need to reference current session state or build on previous work.

### Question 6 (Domain 2)
**Q: Your MCP server needs access to GitHub credentials. How should you provide them in .mcp.json?**

**A:** Use environment variable expansion:
```json
"env": {
  "GITHUB_TOKEN": "${GITHUB_TOKEN}"
}
```
Set the GITHUB_TOKEN in your shell environment before running Claude Code.

### Question 7 (Domain 2)
**Q: Explain three key components of a well-written tool description.**

**A:**
1. **Clear purpose** - One sentence explaining what the tool does
2. **Input/output specification** - Document parameters and return values
3. **Examples** - Show how to use the tool in practical scenarios

### Question 8 (Domain 3)
**Q: You want to run a configuration update that might affect multiple files. Should you use plan mode? Why?**

**A:** Yes, use `--plan true`. This is a structural change with lasting impact, so you should review the plan first before execution to catch any issues.

### Question 9 (Domain 2)
**Q: How would you configure an MCP server to work in both development (localhost) and production environments?**

**A:** Use environment variables for the server configuration:
```json
{
  "mcp_servers": {
    "api": {
      "type": "stdio",
      "command": "node",
      "args": ["server.js"],
      "env": {
        "API_URL": "${API_URL}",
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

### Question 10 (Domain 3)
**Q: Describe the file resolution order for CLAUDE.md in Claude Code.**

**A:** Claude resolves CLAUDE.md based on proximity (most specific wins):
1. CLAUDE.md in the same directory as the file
2. CLAUDE.md in parent directory
3. CLAUDE.md in grandparent directory
4. ... (continuing up the tree)
5. Root CLAUDE.md

---

## Setup Instructions

### Running the Setup Script

The `team-config-setup.sh` script creates a complete example project structure:

```bash
chmod +x team-config-setup.sh
./team-config-setup.sh
```

This creates a `team-dev-project/` directory with all the configurations described in this exercise.

### Manual Verification

After running the setup script, verify the structure:

```bash
# Check directory structure
find team-dev-project -type f -name "*.md" -o -name "*.yaml" -o -name "*.json" | head -20

# Check CLAUDE.md files
find team-dev-project -name "CLAUDE.md" -type f

# Check rule files
ls team-dev-project/.claude/rules/

# Check custom commands
ls team-dev-project/.claude/commands/

# Check skills
find team-dev-project/.claude/skills -name "SKILL.md"
```

### Exploration Tasks

1. **Read the root CLAUDE.md** and understand the workspace-level rules
2. **Compare root vs .claude/CLAUDE.md** and identify differences
3. **Examine backend-standards.yaml** and understand the YAML frontmatter
4. **Review the /review-pr command** and understand how it would work
5. **Check the code-review skill** and explain why it uses `context: fork`
6. **Inspect .mcp.json** and identify environment variables

---

## Common Mistakes to Avoid

### Mistake 1: Creating CLAUDE.md at Every Level
**Wrong:** CLAUDE.md in every single directory
**Right:** Only create CLAUDE.md where rules change significantly

### Mistake 2: Putting All Rules in CLAUDE.md
**Wrong:** 500-line CLAUDE.md with all rules inline
**Right:** Use @import to reference separate rule files

### Mistake 3: Overly Broad Rule Paths
**Wrong:** `path: "**/*.ts"` (applies everywhere)
**Right:** `path: "src/**/*.ts"` (specific to src/)

### Mistake 4: Not Documenting Tool Requirements
**Wrong:** MCP tool with no description or input specs
**Right:** Clear description with input/output and examples

### Mistake 5: Hardcoding Sensitive Data
**Wrong:** `"API_KEY": "sk-12345..."` in .mcp.json
**Right:** `"API_KEY": "${API_KEY}"` in .mcp.json, set env var

### Mistake 6: Using Skills Without Tool Restrictions
**Wrong:** Skill with `allowed-tools: "*"`
**Right:** Skill with explicit `allowed-tools: [read_file, grep, bash]`

---

## Real-World Application

This exercise prepares you for:

**DevOps/Platform Teams:**
- Configuring standardized development environments
- Ensuring all team members follow the same coding standards
- Automating common infrastructure tasks via skills

**Security Teams:**
- Enforcing security standards across projects
- Controlling tool access through skill configurations
- Auditing MCP server configurations

**Development Teams:**
- Onboarding new developers quickly (run setup script)
- Ensuring consistent code quality and documentation
- Automating code review and testing workflows

**Enterprise Architects:**
- Standardizing Claude Code usage across organization
- Creating reusable rule libraries for multiple projects
- Managing different rules for different departments

---

## Next Steps

After completing this exercise:

1. **Adapt to your project** - Use this structure in your actual team repo
2. **Create domain-specific rules** - Add rules for your tech stack
3. **Build team skills** - Create skills for your common workflows
4. **Iterate on MCP servers** - Add integration with your tools (Jira, Slack, etc.)
5. **Document team patterns** - Record why you chose specific configurations

---

## Additional Resources

- [Claude Code Documentation](https://claude.com/docs/claude-code)
- [MCP Specification](https://modelcontextprotocol.io/)
- [YAML Syntax Reference](https://yaml.org/spec/1.2/spec.html)
- [Best Practices for Tool Design](https://example.com/tool-design)

---

## Feedback & Questions

This exercise is designed to be self-contained but should raise questions:

- How do you handle conflicting rules from different CLAUDE.md files?
- When should you override parent rules vs creating new files?
- What's the optimal number of rule files for a large project?
- How do you version control CLAUDE.md updates?

These are exactly the questions you'll face in the exam and in real practice.
