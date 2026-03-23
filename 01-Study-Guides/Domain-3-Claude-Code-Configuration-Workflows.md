# Domain 3: Claude Code Configuration & Workflows
## Claude Certified Architect – Foundations Study Guide

**Exam Weight:** 20% (14 questions)
**Estimated Study Time:** 3-4 hours
**Last Updated:** March 2026

---

## Table of Contents
1. [Domain Overview](#domain-overview)
2. [Task 3.1: CLAUDE.md Configuration Hierarchy](#task-31-claudemd-configuration-hierarchy)
3. [Task 3.2: Custom Slash Commands & Skills](#task-32-custom-slash-commands--skills)
4. [Task 3.3: Path-Specific Rules](#task-33-path-specific-rules)
5. [Task 3.4: Plan Mode vs Direct Execution](#task-34-plan-mode-vs-direct-execution)
6. [Task 3.5: Iterative Refinement Techniques](#task-35-iterative-refinement-techniques)
7. [Task 3.6: CI/CD Pipeline Integration](#task-36-cicd-pipeline-integration)
8. [Key Concepts Summary](#key-concepts-summary)
9. [Common Exam Traps](#common-exam-traps)
10. [Quick Reference Cheatsheet](#quick-reference-cheatsheet)

---

## Domain Overview

Domain 3 focuses on the practical tooling and workflow patterns for using Claude Code effectively in team environments. This domain bridges the gap between understanding Claude's capabilities and implementing them systematically at scale.

### Core Principles

1. **Configuration Layering**: Separate concerns across user-level, project-level, and directory-level configurations
2. **Automation & Extensibility**: Use custom commands and skills to encapsulate team workflows
3. **Context Efficiency**: Apply path-specific rules to load only relevant context
4. **Workflow Selection**: Match execution model to task complexity
5. **Progressive Improvement**: Use structured techniques for iterative enhancement
6. **System Integration**: Embed Claude Code into automated CI/CD workflows

### Why This Matters

Configuration errors cause silent failures in team environments. A developer using `~/.claude/CLAUDE.md` for standards that should be project-level won't share those standards with teammates, leading to inconsistent code quality. Understanding these patterns prevents costly rework and team friction.

---

## Task 3.1: CLAUDE.md Configuration Hierarchy

### Overview

CLAUDE.md files form a hierarchical configuration system that allows instructions to cascade, override, and specialize across different scopes.

### The Three-Level Hierarchy

```
User Level (~/.claude/CLAUDE.md)
    ↓ [applies to all projects]
Project Level (.claude/CLAUDE.md or /CLAUDE.md)
    ↓ [applies to this project]
Directory Level (./subdirectory/CLAUDE.md)
    ↓ [applies to files in this directory]
File Context
```

### Level Definitions & Scope

| Level | Path | Scope | Version Control | Use Case |
|-------|------|-------|-----------------|----------|
| **User** | `~/.claude/CLAUDE.md` | All projects on this machine | ❌ Local only | Personal preferences, global standards |
| **Project** | `.claude/CLAUDE.md` or `CLAUDE.md` | Entire project | ✅ Shared via git | Team standards, coding conventions |
| **Directory** | `./subdir/CLAUDE.md` | Files in this directory | ✅ Shared via git | Package-specific conventions |

### Critical Knowledge: Scope Isolation

**User-level settings are NOT shared with teammates.** This is a common source of exam questions:

```
WRONG APPROACH:
├── ~/.claude/CLAUDE.md (contains team standards)
└── team sees inconsistent behavior ❌

CORRECT APPROACH:
├── .claude/CLAUDE.md or /CLAUDE.md (checked into git)
└── all team members use same standards ✅
```

### Configuration Examples

#### User-Level Configuration (~/.claude/CLAUDE.md)

Use for personal workflows that shouldn't affect team standards:

```yaml
# ~/.claude/CLAUDE.md - Local personal settings

# Personal coding style preferences
anthropic_rules:
  - I prefer verbose variable names even if they exceed 80 chars
  - I prefer early returns over nested conditionals
  - I always add JSDoc comments for public functions

# Personal tool preferences
tool_preferences:
  - Prefer ripgrep (Grep tool) over manual file parsing
  - Use absolute paths to avoid working directory issues

# Personal skill locations
user_skills_dir: ~/.claude/skills
```

#### Project-Level Configuration (.claude/CLAUDE.md)

Use for team standards that must be consistent across developers:

```yaml
# .claude/CLAUDE.md - Shared team standards (committed to git)

project_name: "Acme API Service"
project_description: |
  REST API microservice handling order processing.
  Tech stack: Node.js 18+, TypeScript, Express, PostgreSQL

coding_standards:
  language: typescript
  style_guide: |
    - Use const for immutable values, let for mutable
    - All functions must have TypeScript type annotations
    - No implicit any types
    - Prefer interfaces over type aliases for object shapes
    - Use PascalCase for types, camelCase for variables

  testing:
    framework: jest
    coverage_minimum: 80%
    convention: "*.test.ts for unit tests, *.integration.ts for integration tests"
    fixtures: "test/fixtures/ directory"

  api_conventions:
    versioning: "URL path: /v1/, /v2/"
    response_format: |
      {
        "status": "success|error",
        "data": {},
        "error": {"code": "", "message": ""},
        "timestamp": "ISO-8601"
      }
    error_codes: |
      400: Bad Request (validation failed)
      401: Unauthorized (auth required)
      403: Forbidden (insufficient permissions)
      404: Not Found
      500: Internal Server Error

review_criteria:
  - All changes must include tests
  - No direct database queries; use query builder
  - No hardcoded credentials or secrets
  - Performance: SQL queries logged and analyzed
  - Security: Input validation on all endpoints

deployment:
  environments: ["dev", "staging", "production"]
  strategy: "Rolling deployment with 5-minute rollback window"

team_context: |
  @import .claude/rules/testing-standards.md
  @import .claude/rules/api-conventions.md
  @import .claude/rules/security-checklist.md
```

#### Directory-Level Configuration (./packages/api/CLAUDE.md)

Use for package-specific conventions within a monorepo:

```yaml
# ./packages/api/CLAUDE.md - API package specific rules

scope: "API package within monorepo"

package_context:
  owner: "platform-team"
  description: "Public REST API for third-party integrations"

conventions:
  - Endpoints must support both JSON and CSV response formats
  - Rate limiting: 1000 req/min per API key
  - Pagination: cursor-based, 50-item default page size
  - Webhook payloads must include signature verification

file_organization:
  - routes/: HTTP endpoint handlers
  - services/: Business logic
  - middleware/: Auth, logging, validation
  - types/: TypeScript type definitions
  - tests/: Jest test files

team_context:
  @import ../shared-rules/typescript.md
  @import ../shared-rules/testing.md
```

### The @import Syntax

Use @import to reference external configuration files and keep CLAUDE.md modular:

```yaml
# Root .claude/CLAUDE.md

base_standards: |
  @import .claude/rules/typescript-standards.md
  @import .claude/rules/testing-standards.md
  @import .claude/rules/security-checklist.md

package_specific: |
  For API package: @import .claude/rules/api-conventions.md
  For CLI package: @import .claude/rules/cli-conventions.md
  For Web UI: @import .claude/rules/react-standards.md
```

#### .claude/rules/ Directory Structure

Organize topic-specific rules as an alternative to monolithic CLAUDE.md:

```
.claude/
├── CLAUDE.md (main file with @imports)
├── rules/
│   ├── typescript-standards.md
│   ├── testing-standards.md
│   ├── api-conventions.md
│   ├── security-checklist.md
│   ├── deployment-standards.md
│   └── README.md (documents what each rule covers)
└── commands/
    └── (custom slash commands)
```

### Using the /memory Command

The `/memory` command verifies which configuration files are loaded:

```bash
# In Claude Code session
/memory

# Output shows:
# Loaded CLAUDE.md files:
# 1. ~/.claude/CLAUDE.md (user-level)
# 2. /projects/myapp/.claude/CLAUDE.md (project-level)
# 3. /projects/myapp/packages/api/CLAUDE.md (directory-level)
# 4. Imports from .claude/rules/ (7 files)
#
# Total context tokens: ~2,400
```

### Diagnosing Configuration Hierarchy Issues

**Common Problem: New team member doesn't follow team standards**

```
Symptom: Developer joins team, but Claude generates code that doesn't match team conventions

Diagnosis Steps:
1. Run /memory to check which CLAUDE.md files are loaded
2. Look for project-level config in wrong location
   - ❌ ~/.claude/CLAUDE.md (user-level, not shared)
   - ✅ ./.claude/CLAUDE.md (project-level, shared via git)
3. Check if new developer has correct git branch
4. Verify .gitignore doesn't exclude .claude/ directory
   - Add to .gitignore: /CLAUDE.md (only root level personal config)
   - Do NOT ignore: .claude/ (should be committed)

Resolution:
- Ensure .claude/CLAUDE.md is committed to git
- Add to contributing docs: "First run /memory to verify team standards"
```

### Best Practices for Configuration Hierarchy

| Scenario | Correct Level | Reasoning |
|----------|---------------|-----------|
| Team coding style | Project-level | All developers need same standards |
| Personal IDE preferences | User-level | Doesn't affect code output |
| Testing framework setup | Project-level | Team must use same test runner |
| Language-specific linting rules | Project-level | Shared via config files |
| Personal skill workflows | User-level | Personal productivity tools |
| API response format | Project-level | Required for API consistency |
| Security checklist | Project-level | Legal/compliance requirement |
| Debugging techniques | User-level | Personal preference |

---

## Task 3.2: Custom Slash Commands & Skills

### Overview

Custom commands and skills extend Claude Code's functionality with team-specific or project-specific workflows. Commands are quick aliases, while skills are structured workflows that can be shared and configured.

### Commands vs Skills

| Aspect | Commands | Skills |
|--------|----------|--------|
| **Purpose** | Quick aliases for frequent actions | Structured workflows with parameters |
| **Scope** | Project-scoped (.claude/commands/) or user-scoped (~/.claude/commands/) | Project-scoped (.claude/skills/) or user-scoped (~/.claude/skills/) |
| **Invocation** | `/commandname` | `/skillname` with optional arguments |
| **Configuration** | Simple text files | SKILL.md with YAML frontmatter |
| **Sharing** | Via version control if project-scoped | Via version control if project-scoped |
| **Complexity** | Simple, single-purpose | Multi-step workflows |

### Project-Scoped Commands (.claude/commands/)

Commands shared via git for team-wide availability:

```
.claude/
├── commands/
│   ├── format-pr-description.txt
│   ├── test-all.txt
│   ├── lint-and-fix.txt
│   └── security-audit.txt
```

#### Example Command: Format PR Description

```
# .claude/commands/format-pr-description.txt

You are a PR description formatter. When invoked, ask the user for:
1. Feature title (one line)
2. Description of changes (paragraph)
3. Testing performed (bullet points)
4. Screenshots/links (if applicable)

Format output as a markdown template ready for GitHub:

## Summary
[feature title]

## Changes
[description]

## Testing
[bullet points]

## Related Issues
Closes #[issue number]

## Screenshots
[if applicable]

Then output: "PR description ready to paste!"
```

#### Example Command: Test All Packages

```
# .claude/commands/test-all.txt

Run tests in all packages:
1. First, explore directory structure to find all package directories
2. For each package with a test script in package.json:
   - Report package name
   - Run tests using the project's testing setup
3. Summarize results:
   - ✅ Packages passed
   - ❌ Packages failed with error details
   - ⏭️ Packages skipped (no test script)
4. Recommend next steps

Invoke with: /test-all
```

### Skills with SKILL.md Configuration

Skills are structured workflows configured with YAML frontmatter in SKILL.md:

```
.claude/
└── skills/
    ├── code-review/
    │   └── SKILL.md
    ├── generate-tests/
    │   └── SKILL.md
    ├── performance-audit/
    │   └── SKILL.md
    └── security-scan/
        └── SKILL.md
```

#### Skill SKILL.md Frontmatter Options

```yaml
---
name: Code Review Assistant
description: Performs comprehensive code review with security and performance checks
version: 1.0.0
context: fork  # Options: fork, inline (default)
allowed-tools:
  - Read
  - Grep
  - Glob
argument-hint: |
  Usage: /code-review [file-path]
  Example: /code-review src/api/handlers.ts
---

# Skill Implementation

You are a code review specialist. When invoked with a file path, analyze the code for:

1. **Security Issues** (OWASP Top 10)
2. **Performance Problems** (N+1 queries, memory leaks)
3. **Best Practices** (design patterns, maintainability)
4. **Test Coverage** (unit tests, edge cases)

Provide:
- Critical issues (must fix)
- Important issues (should fix)
- Nice-to-have suggestions
- Overall assessment

Format output with severity levels and specific line numbers.
```

### Key Frontmatter Options

#### context: fork - Isolate Skill Output

`context: fork` runs the skill in an isolated sub-agent, preventing skill output from polluting the main conversation:

```yaml
---
name: Codebase Analyzer
description: Deep analysis of codebase structure and dependencies
context: fork  # Run in isolated sub-agent ✅
allowed-tools:
  - Read
  - Grep
  - Glob
---

# Verbose codebase analysis...
# Output won't clutter main conversation
# Results are returned as summary to main session
```

Use `context: fork` for:
- Verbose discovery/exploration (codebase analysis)
- Brainstorming alternatives (design discussions)
- Exploratory debugging (examining many files)
- Long-running operations (testing entire test suite)

Use inline context (default) for:
- Quick, focused tasks (single file edits)
- User-facing results (code generation)
- Direct feedback needed in conversation

#### allowed-tools - Restrict Tool Access

Limit which tools a skill can use for safety and cost control:

```yaml
---
name: Safe Test Generator
description: Generate tests without modifying source files
allowed-tools:
  - Read
  - Grep
  - Glob
  # Notably absent: Edit, Write, Bash, etc.
---

# This skill can ONLY read files, not modify them
# Prevents accidental code changes
```

Common tool restriction patterns:
- **Read-only skills**: [Read, Grep, Glob]
- **Code generation skills**: [Read, Grep, Glob, Write, Edit, Bash]
- **Analysis skills**: [Read, Grep, Glob]
- **Deployment skills**: [Bash, Read]

#### argument-hint - Parameter Prompting

Prompt developers for required parameters when invoked without arguments:

```yaml
---
name: Refactor Function
description: Refactor a function for readability and performance
argument-hint: |
  Required: file-path (path to file containing function)
  Required: function-name (name of function to refactor)
  Optional: constraints (e.g., "must maintain backward compatibility")

  Usage: /refactor-function src/utils.ts calculateTotal --constraints "backward-compatible"
---
```

When user runs `/refactor-function` without arguments, Claude prompts:
```
This skill requires:
- file-path: Path to file containing function
- function-name: Name of function to refactor

Example: /refactor-function src/utils.ts calculateTotal
```

### Personal Skill Customization

Create personal variants in `~/.claude/skills/` to customize behavior without affecting teammates:

```
~/.claude/skills/
├── my-code-review/
│   └── SKILL.md (strictest review standards, my personal preferences)
├── my-quick-format/
│   └── SKILL.md (opinionated code formatting)
└── my-debug-helper/
    └── SKILL.md (debugging workflow I invented)
```

Example: Personal variant of shared skill:

```yaml
# ~/.claude/skills/my-strict-review/SKILL.md
---
name: Strict Code Review (Personal)
description: My personal variant with highest standards
context: fork
---

# More strict than team version:
# - Require unit tests for ALL changes
# - Enforce 100% TypeScript coverage
# - Check for accessibility (a11y) issues
# - Performance must be <100ms for web endpoints
```

### Real-World Skill Examples

#### Example 1: Generate Tests with Test-Driven Iteration

```yaml
# .claude/skills/generate-tests/SKILL.md
---
name: Generate Test Suite
description: Generate comprehensive jest tests for a function
allowed-tools:
  - Read
  - Write
  - Grep
argument-hint: |
  Usage: /generate-tests src/services/OrderProcessor.ts processOrder
  Required: file-path and function-name
---

# Generate Test Suite Skill

You are a test generation specialist. When given a function:

1. **Analyze the function** for:
   - Input parameters and types
   - Return type and side effects
   - Edge cases (null, undefined, empty, boundary values)
   - Error conditions

2. **Write comprehensive tests** covering:
   - Happy path (normal operation)
   - Edge cases (empty input, null, boundary values)
   - Error conditions (validation failures, exceptions)
   - Performance expectations (if applicable)

3. **Use project testing patterns** from CLAUDE.md:
   - Framework: Jest
   - Conventions: *.test.ts naming
   - Fixtures: Use test/fixtures/ directory
   - Minimum coverage: 80%

4. **Provide detailed test output** with:
   - Test descriptions explaining what each test validates
   - Clear assertion messages
   - Example mock data used

Output test file in Jest format ready to be added to project.
```

#### Example 2: Code Review Skill with Context Fork

```yaml
# .claude/skills/code-review/SKILL.md
---
name: Comprehensive Code Review
description: Multi-dimensional code review including security, performance, and standards
context: fork
allowed-tools:
  - Read
  - Grep
  - Glob
argument-hint: |
  Usage: /code-review [file-or-directory-path]
  Analyzes code against team standards from CLAUDE.md
---

# Code Review Skill

Perform comprehensive code review on the provided file(s):

## Review Dimensions

### 1. Security Review
- OWASP Top 10 violations
- Input validation issues
- Authentication/authorization problems
- Secrets/credentials in code

### 2. Performance Review
- Database N+1 queries
- Missing indexes
- Memory leaks
- Algorithm efficiency (O(n) analysis)

### 3. Code Quality Review
- Follows CLAUDE.md standards
- Type safety (TypeScript)
- Test coverage
- Maintainability and clarity

### 4. Best Practices Review
- Design patterns correctly applied
- Error handling comprehensive
- Logging appropriate levels
- Deprecation warnings

## Output Format

For each issue found:
```
[SEVERITY] [CATEGORY] Line XX: [issue]
Explanation: [why this matters]
Suggestion: [how to fix]
```

Severities:
- 🔴 CRITICAL: Security risk, data loss risk, outage risk
- 🟠 HIGH: Performance problem, code smell, maintainability issue
- 🟡 MEDIUM: Minor issue, style inconsistency
- 🟢 LOW: Nice-to-have suggestion

End with:
- Summary: X critical, Y high, Z medium issues
- Risk assessment
- Recommended next steps
```

#### Example 3: Performance Audit Skill

```yaml
# .claude/skills/performance-audit/SKILL.md
---
name: Performance Audit
description: Analyze code for performance bottlenecks
context: fork
allowed-tools:
  - Read
  - Grep
  - Glob
---

# Performance Audit Skill

Analyze the provided file/directory for performance issues:

1. **Database Query Analysis**
   - Look for N+1 query patterns
   - Identify missing indexes
   - Check for inefficient query patterns

2. **Algorithm Complexity**
   - Analyze time complexity (O notation)
   - Identify unnecessary loops
   - Check for redundant computations

3. **Memory Usage**
   - Large object creation in loops
   - Memory leaks (event listeners, timers not cleaned up)
   - Unnecessary array copying

4. **Async/Parallel Opportunities**
   - Sequential operations that could be parallel
   - Missing Promise.all() optimizations
   - Blocking operations in event loop

5. **Caching Opportunities**
   - Expensive computations done repeatedly
   - Database queries that could be cached
   - Static data fetched on every request

For each issue: provide code example, impact analysis, and optimization suggestion.
```

### Choosing Between Skills and CLAUDE.md

| Use Case | Recommendation | Reasoning |
|----------|----------------|-----------|
| Always-loaded team standards | CLAUDE.md | Should be context for every interaction |
| On-demand code review workflow | Skill | Invoked when needed, doesn't clutter context |
| Verbose codebase analysis | Skill with context: fork | Isolates exploratory output |
| Testing framework conventions | CLAUDE.md | Team must always follow |
| Personal debugging workflow | Personal skill (~/.claude/skills/) | Individual preference |
| Project-specific command shortcuts | Commands | Quick access for repeated tasks |

---

## Task 3.3: Path-Specific Rules

### Overview

Path-specific rules use glob patterns to load configuration only when editing matching files, reducing irrelevant context and token usage.

### YAML Frontmatter with paths Field

Create `.claude/rules/` files with YAML frontmatter containing glob patterns:

```yaml
# .claude/rules/testing.md
---
name: Testing Standards
paths:
  - "**/*.test.ts"
  - "**/*.spec.ts"
  - "tests/**/*"
  - "test/**/*"
---

# Testing Standards (loaded only for test files)

## Test Structure
- One describe block per tested function
- Clear test descriptions (should_X_when_Y)
- Arrange-Act-Assert pattern

## Test Coverage
- Happy path tests
- Edge cases (null, undefined, empty)
- Error scenarios
- Performance (if applicable)

## Fixtures
Test data located in `test/fixtures/`:
```

### How Path-Specific Rules Work

Claude Code only loads rules matching the current file being edited:

```
Editing src/services/UserService.ts
├── Check: .claude/rules/testing.md (paths: **/*.test.ts) ❌ No match
└── Load other rules matching src/services/UserService.ts

Editing src/services/UserService.test.ts
├── Check: .claude/rules/testing.md (paths: **/*.test.ts) ✅ Match!
├── Load testing standards into context
└── Continue with other rules
```

### Real-World Path-Specific Rules Examples

#### Terraform Files

```yaml
# .claude/rules/terraform.md
---
name: Terraform Standards
paths:
  - "terraform/**/*.tf"
  - "infrastructure/**/*.tf"
---

# Terraform Conventions

## Naming
- Resources: snake_case
- Variables: snake_case
- Outputs: descriptive names
- Workspaces: dev, staging, prod

## Module Structure
```

#### React Components

```yaml
# .claude/rules/react-components.md
---
name: React Component Standards
paths:
  - "src/components/**/*.tsx"
  - "src/pages/**/*.tsx"
---

# React Component Standards

## Component Structure
- Functional components with hooks
- Props interface defined above component
- No prop drilling (use Context API for shared state)

## Hooks Rules
- Custom hooks extracted to /hooks directory
- No conditional hook calls
- Dependencies array always specified

## Performance
- Memoize with React.memo for expensive renders
- useCallback for event handlers
- useMemo for expensive computations
```

#### Database Migrations

```yaml
# .claude/rules/migrations.md
---
name: Database Migration Standards
paths:
  - "migrations/**/*.sql"
  - "db/migrations/**/*"
---

# Migration Standards

## Safety Requirements
- Always include rollback strategy
- Test migrations on production-like data
- No locking operations exceeding 30 seconds
- Add index concurrently: CREATE INDEX CONCURRENTLY

## Naming Convention
- Format: YYYYMMDD_HHmmss_description.sql
- Example: 20250322_143000_add_user_email_index.sql

## Contents
- Document: what changes, why, rollback strategy
- Test: verify idempotency (can run twice safely)
- Performance: check query plans before deploy
```

#### Configuration Files

```yaml
# .claude/rules/config-files.md
---
name: Configuration File Standards
paths:
  - ".env*"
  - "config/**/*"
  - "*.config.ts"
  - "*.config.js"
---

# Configuration File Standards

## .env Files
- Document all required environment variables
- Never commit .env with real values
- Use .env.example with placeholder values
- Load in this order: .env.local > .env.{NODE_ENV} > .env

## Config Objects
- Use TypeScript interfaces for type safety
- Validate at startup, fail fast
- Document all options
- Support environment variable overrides
```

### Glob Pattern Examples

| Pattern | Matches |
|---------|---------|
| `**/*.test.ts` | Any file ending in .test.ts, any directory depth |
| `tests/**/*` | All files in tests/ directory and subdirectories |
| `src/components/*.tsx` | Only .tsx files directly in src/components/ |
| `migrations/**/*.sql` | SQL migration files at any depth |
| `.env*` | .env, .env.local, .env.development, etc. |
| `terraform/**/*.tf` | Terraform files at any depth in terraform/ |
| `**/docker-compose.yml` | docker-compose.yml anywhere in project |

### Path-Specific Rules vs Directory-Level CLAUDE.md

When should you use each approach?

| Scenario | Approach | Reasoning |
|----------|----------|-----------|
| Rules apply to one directory | Directory CLAUDE.md | Simpler, cleaner |
| Rules apply to files scattered throughout codebase | Path-specific rules | Glob patterns handle scattered locations |
| Rules apply to specific file types regardless of location | Path-specific rules | `**/*.test.ts` is cleaner than multiple CLAUDE.md files |
| Deep nesting (packages > features > components) | Directory CLAUDE.md | Files are logically co-located |
| Monorepo with shared conventions | Path-specific rules | Apply same rules across multiple packages |

Example scenario:

```
Project Structure:
├── src/
│   ├── services/
│   │   ├── UserService.test.ts
│   │   └── OrderService.test.ts
├── tests/
│   ├── integration/
│   │   └── api.test.ts
└── packages/
    └── auth/
        ├── src/
        │   └── index.test.ts

Requirements: All test files (.test.ts) should follow same standards

❌ Directory-level CLAUDE.md:
- Need: src/services/CLAUDE.md (test standards)
- Need: tests/CLAUDE.md (test standards - duplicate)
- Need: packages/auth/src/CLAUDE.md (test standards - duplicate)
- Maintenance nightmare: update standards in 3 places

✅ Path-specific rules:
- Single: .claude/rules/testing.md with paths: ["**/*.test.ts"]
- Single source of truth
- Automatically applies everywhere
```

### Best Practices for Path-Specific Rules

1. **Organize by concern, not location**
   ```
   .claude/rules/
   ├── testing.md (all test files)
   ├── api-routes.md (all API endpoints)
   ├── database.md (all database-related)
   └── config.md (all config files)
   ```

2. **Keep paths simple and specific**
   ```yaml
   # GOOD - Clear, specific patterns
   paths:
     - "**/*.test.ts"
     - "**/*.spec.ts"

   # AVOID - Too broad, matches unintended files
   paths:
     - "**/*"  # This matches everything!
   ```

3. **Document the purpose in frontmatter**
   ```yaml
   ---
   name: Testing Standards
   description: |
     Applies to all unit and integration test files.
     Ensures consistent test structure, coverage requirements, and fixtures.
   paths:
     - "**/*.test.ts"
     - "tests/**/*"
   ---
   ```

4. **Order rules by specificity (most specific first)**
   ```yaml
   # Good: Most specific first
   paths:
     - "src/components/**/*.test.tsx"  # Component tests (specific)
     - "**/*.test.ts"                  # General tests (broad)
   ```

---

## Task 3.4: Plan Mode vs Direct Execution

### Overview

Plan mode and direct execution are two different workflows for different task types. Choosing correctly prevents rework and maintains team context.

### Key Distinction

| Aspect | Plan Mode | Direct Execution |
|--------|-----------|-----------------|
| **Best For** | Complex, multi-file, architectural decisions | Simple, single-file, clear scope |
| **Workflow** | 1) Plan, 2) Discuss, 3) Execute | Single phase: execute |
| **Risk** | Low (plans are validated before execution) | Can be high if scope is unclear |
| **Token Efficiency** | Moderate (discovery + plan + execution) | High for small tasks |
| **When Code Breaks** | Easier to diagnose (separate plan) | May need full rework |

### Plan Mode Workflow

**When to use Plan Mode:**

1. **Architectural implications** - Changes affect system design
   ```
   "Restructure microservices from monolith to distributed"
   "Migrate from REST to GraphQL across 45 endpoints"
   "Refactor authentication to support multi-tenancy"
   ```

2. **Multiple valid approaches** - Could be done several ways
   ```
   "Implement caching: Redis vs in-memory vs CDN?"
   "State management: Context API vs Redux vs Zustand?"
   "Database normalization vs denormalization trade-off"
   ```

3. **Large scale changes** - Affecting 20+ files
   ```
   "Update all API response formats project-wide"
   "Migrate from CommonJS to ESM modules"
   "Refactor test suite from Mocha to Jest"
   ```

4. **Unknown unknowns** - Unclear scope or dependencies
   ```
   "How do we handle backwards compatibility?"
   "What existing tests might break?"
   "Which files depend on this change?"
   ```

#### Plan Mode Execution

```
User: "Migrate our authentication system to support OAuth 2.0 SSO"

Claude Plan Mode:
1. DISCOVERY PHASE
   ├── Analyze current auth implementation
   ├── Identify all auth-dependent code
   ├── Check test coverage
   └── Understand OAuth requirements

2. PLAN PHASE
   ├── Propose approach:
   │   ✓ Keep existing token-based auth as fallback
   │   ✓ Add OAuth provider (Google, GitHub)
   │   ✓ Implement session mapping (OAuth → internal user)
   │   ✓ Add migration script for existing users
   │   └── Testing strategy
   │
   ├── Identify affected areas:
   │   ├── Authentication middleware (4 files)
   │   ├── User model (1 file)
   │   ├── Login UI (3 components)
   │   ├── Tests (15 test files)
   │   └── Configuration (2 env files)
   │
   └── Risk assessment:
       ├── Breaking changes: None (backwards compatible)
       ├── Migration path: Gradual opt-in
       └── Rollback: Keep old auth alongside new

3. USER DECISION
   "Does this plan work for you?"
   [User: "Yes, but add GitHub provider too"]
   Plan updated...

4. EXECUTION PHASE
   ├── Implement OAuth providers
   ├── Update authentication middleware
   ├── Add user migration script
   ├── Update tests
   └── Document for team
```

### Direct Execution Workflow

**When to use Direct Execution:**

1. **Simple, single-file changes** - Clear scope, one file
   ```
   "Add a null check in the validateUser function"
   "Fix off-by-one error in pagination"
   "Update error message text in form validation"
   ```

2. **Bug fixes with clear stack trace** - Root cause identified
   ```
   "Fix TypeError in UserService.processPayment (line 142)"
   Stack trace shows exact issue
   ```

3. **Adding single feature** - Isolated, doesn't interact with other systems
   ```
   "Add 'remember me' checkbox to login form"
   "Add sorting to product list"
   "Export data as CSV"
   ```

4. **Small improvements** - Well-understood changes
   ```
   "Add JSDoc comments to database module"
   "Update import statements to use barrel exports"
   "Add console logging to debugging section"
   ```

#### Direct Execution Example

```
User: "Add email validation to the registration form"

Claude Direct Execution:
1. Read registration form component
2. Identify validation logic
3. Add email regex pattern and validation
4. Update error message
5. Run tests to confirm nothing broke
6. Done!

[No separate planning phase needed]
```

### Combining Plan & Execute: Multi-Phase Approach

Use plan mode for investigation, then direct execution for implementation:

```
Phase 1: PLAN (isolated exploration)
├── User request: "Migrate database schema to support multi-tenancy"
├── Claude Plan Mode with Explore subagent:
│   ├── Analyze current schema
│   ├── Research multi-tenancy patterns
│   ├── Identify all affected queries
│   └── Return summary (verbose exploration hidden)
└── Plan: 3-step migration strategy

Phase 2: EXECUTE (direct implementation)
├── User: "Execute the plan"
├── Claude Direct Mode:
│   ├── Create migration script
│   ├── Update models
│   ├── Modify queries
│   └── Update tests
└── Complete
```

### The Explore Subagent for Complex Discovery

Use Explore to isolate verbose discovery output and return summaries:

```
User: "Help me understand if we should migrate from SQLAlchemy to Tortoise ORM.
I need to know compatibility impact, migration effort, and performance implications.
This is a big decision and I want thorough analysis."

Claude (using Explore Subagent):
1. Create isolated Explore subagent
2. Within Explore (verbose, exploratory):
   ├── Read SQLAlchemy models and configurations
   ├── Search for all ORM usage patterns
   ├── Compare both ORMs across 50+ dimensions
   ├── Check compatibility with existing code
   ├── Review migration guides
   ├── Analyze performance implications
   └── Generate detailed comparison matrix
3. Return to main conversation with summary:

EXECUTIVE SUMMARY:
- Migration effort: 2-3 weeks (45+ files)
- Performance: 15-20% improvement on complex queries
- Compatibility: 95% compatible, 3 breaking changes identified
- Recommendation: Doable, recommend incremental migration
- Risk: Medium (ORM is critical infrastructure)

[All verbose exploration stays in Explore subagent]
[Main conversation stays focused]
```

### Decision Tree: Plan vs Direct

```
Is the task clearly scoped and well-understood?
├─ YES (I know exactly what needs to happen)
│  └─→ Use DIRECT EXECUTION
│       Faster, more efficient for straightforward work
│
└─ NO (Multiple approaches, unclear impacts)
   └─→ Use PLAN MODE
       1. Create plan with Explore if very verbose
       2. Get approval
       3. Execute with confidence
```

### Real-World Scenarios

| Scenario | Approach | Reasoning |
|----------|----------|-----------|
| "Fix async bug in checkout causing race condition" | Direct | Clear bug, clear fix location |
| "Refactor state management architecture" | Plan | Multiple valid approaches, widespread impact |
| "Add dark mode toggle" | Direct | Isolated feature, straightforward implementation |
| "Migrate from REST to GraphQL API" | Plan | Affects entire API layer, multiple strategies |
| "Update all error messages to be consistent" | Direct | Large scope but straightforward pattern |
| "Design database schema for new feature" | Plan | Architectural decision, long-term impact |
| "Fix broken test in UserService.test.ts" | Direct | Single file, clear scope |
| "Restructure folder organization" | Plan | Affects project structure, impacts all imports |

---

## Task 3.5: Iterative Refinement Techniques

### Overview

Iterative refinement enables progressive improvement through concrete examples, test-driven approaches, and strategic questioning.

### Core Techniques

1. **Input/Output Examples** - Most effective for clarity
2. **Test-Driven Iteration** - Tests guide improvements
3. **Interview Pattern** - Surface design considerations
4. **Targeted Test Cases** - Fix specific edge cases
5. **Issue Batching** - Interacting problems together, independent separately

### Technique 1: Input/Output Examples

**When to use:** Natural language descriptions produce inconsistent results

Using prose alone creates ambiguity:
```
❌ Poor: "Transform the array to remove duplicates and sort it"
- What type of duplicates? (object identity vs equality)
- Sort ascending or descending?
- What about null/undefined values?
- Preserve type or convert to strings?

✅ Better: Concrete examples showing exact behavior
Input: [3, 1, null, 3, 1, 2]
Expected Output: [null, 1, 2, 3]

Input: [{id: 1, name: "Alice"}, {id: 1, name: "Bob"}]
Expected Output: [{id: 1, name: "Alice"}] or both? (unclear)

Input: ["b", "a", "B", "A"]
Expected Output: ["A", "B", "a", "b"] or ["A", "a", "B", "b"]?
```

#### Best Practices for Examples

Provide **2-3 concrete examples** covering:
- **Normal case**: Typical input producing expected output
- **Edge case**: Boundary condition (empty, null, single element)
- **Complex case**: Multiple interacting features

```
Requirement: "Generate slug from title"

EXAMPLES:
1. Normal case:
   Input: "Getting Started with TypeScript"
   Output: "getting-started-with-typescript"

2. Edge cases:
   Input: ""
   Output: "" (empty string)

   Input: "  Spaces  Around  "
   Output: "spaces-around" (trim spaces)

3. Complex case:
   Input: "Use @mention & symbols!!! 🎉"
   Output: "use-mention-symbols" (remove special chars, keep words)

Expected behavior now crystal clear ✓
```

#### Example: API Response Format

```
Ambiguous requirement:
"Return success response with data"

Concrete examples:
// Success case
{
  "status": "success",
  "data": {
    "userId": 123,
    "email": "user@example.com"
  },
  "timestamp": "2026-03-22T14:30:00Z"
}

// Error case
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email already in use",
    "details": [{
      "field": "email",
      "issue": "duplicate"
    }]
  },
  "timestamp": "2026-03-22T14:30:00Z"
}

// All edge cases covered
```

### Technique 2: Test-Driven Iteration

**When to use:** When implementation produces inconsistent results or misses edge cases

Workflow:
1. Write comprehensive test suite first
2. Share test failures with Claude
3. Claude iterates until tests pass
4. All edge cases covered by tests

#### Example: Test-Driven User Validation

```typescript
// Test suite FIRST (before implementation)
describe('UserValidator', () => {
  describe('validateEmail', () => {
    test('accepts valid email', () => {
      expect(UserValidator.validateEmail('user@example.com')).toBe(true);
    });

    test('rejects invalid email format', () => {
      expect(UserValidator.validateEmail('invalid-email')).toBe(false);
    });

    test('rejects empty string', () => {
      expect(UserValidator.validateEmail('')).toBe(false);
    });

    test('handles whitespace', () => {
      expect(UserValidator.validateEmail('  user@example.com  ')).toBe(true);
    });

    test('rejects null', () => {
      expect(UserValidator.validateEmail(null)).toBe(false);
    });
  });

  describe('validatePassword', () => {
    test('requires minimum 8 characters', () => {
      expect(UserValidator.validatePassword('short')).toBe(false);
      expect(UserValidator.validatePassword('eightchars1')).toBe(true);
    });

    test('requires uppercase, lowercase, number', () => {
      expect(UserValidator.validatePassword('onlylowercase1')).toBe(false);
      expect(UserValidator.validatePassword('MixedCase123')).toBe(true);
    });

    test('allows special characters', () => {
      expect(UserValidator.validatePassword('SecureP@ss1')).toBe(true);
    });
  });
});
```

User workflow:
```
User: "Run tests"

Output:
✗ UserValidator
  ✗ validateEmail
    ✓ accepts valid email
    ✗ rejects invalid email format
    ✗ rejects empty string
    ✗ handles whitespace
    ✗ rejects null
  ✗ validatePassword
    ✗ requires minimum 8 characters
    ✗ requires uppercase, lowercase, number
    ✗ allows special characters

Failures: 7/10

User: "Share these test failures with Claude"

Claude: [Reads failures, implements fixes]

Output:
✓ UserValidator
  ✓ validateEmail
    ✓ accepts valid email
    ✓ rejects invalid email format
    ✓ rejects empty string
    ✓ handles whitespace
    ✓ rejects null
  ✓ validatePassword
    ✓ requires minimum 8 characters
    ✓ requires uppercase, lowercase, number
    ✓ allows special characters

All tests passing ✓
```

### Technique 3: Interview Pattern

**When to use:** Unfamiliar domain or architectural decisions

Claude asks questions BEFORE implementing to surface considerations:

```
User: "Build a caching layer for our API responses"

Claude Interview:
"Before I implement, I need to understand your requirements:

1. Cache invalidation: When should cache entries expire?
   - TTL-based? (e.g., 5 minutes)
   - Event-based? (when data changes)
   - Manual? (admin triggers refresh)
   - Combination?

2. Cache backend: What's your preferred storage?
   - In-memory (fast but single-instance)
   - Redis (distributed, persistent)
   - Memcached (simple, distributed)

3. Cache key strategy: How do we identify cached responses?
   - URL + query params?
   - URL + sorted query params + user ID?
   - Custom key function?

4. Stale data handling: If cache entry is stale, what happens?
   - Return stale data immediately while refreshing?
   - Return error?
   - Block request until fresh?

5. Cache warming: Pre-populate cache?
   - On startup?
   - On-demand?
   - Never?

6. Monitoring: What metrics matter?
   - Hit rate?
   - Memory usage?
   - Eviction rates?

[Answering these prevents wrong implementation later]"
```

### Technique 4: Targeted Test Cases

**When to use:** Fix specific edge case handling

Provide test case with example input and expected output:

```
User: "The date migration script is failing on null dates. Add a test case
and fix it."

Test Case:
Input:
{
  id: 1,
  name: "Record without dates",
  created_at: null,
  updated_at: null
}

Expected Output:
Record skipped with warning: "Record 1: missing created_at, skipping migration"

Current Behavior:
TypeError: Cannot read property 'toISOString' of null

Claude: [Implements null check]

Test Result:
✓ Handles null dates gracefully
✓ Logs appropriate warning
✓ Continues processing other records
```

### Technique 5: Issue Batching Strategy

**When to use:** Multiple issues found, decide: batch or iterate?

| Situation | Approach | Reasoning |
|-----------|----------|-----------|
| Issues are **interrelated** | Fix together in one message | Changing one affects others |
| Issues are **independent** | Fix sequentially | Easier to validate each fix |
| Issues show **pattern** | Batch similar issues | Fix pattern, prevents future occurrences |
| Issues are **unrelated** | Sequential | Less context switching |

#### Interacting Issues Example

```
❌ WRONG APPROACH: Batch these independently
1. Change function signature from (a, b) to (a, b, c)
   → Breaks all 8 callers
2. Update error type from Exception to CustomError
   → Affects all catch blocks
3. Rename database column from user_id to userId
   → Breaks all queries

These issues are INTERACTING - changes affect each other.
Need coordinated approach.

✅ CORRECT APPROACH: Single detailed message
"Please:
1. Change function signature from (a, b) to (a, b, c)
2. Update all 8 callers to pass new parameter c
3. Update error type from Exception to CustomError in signature
4. Update all catch blocks handling this error
5. Rename column and update all queries (list provided below)

All changes together prevent broken intermediate state."
```

#### Independent Issues Example

```
✅ CORRECT: Fix sequentially
1. First: "Fix the null check in validateUser"
   [Test, verify working]

2. Then: "Add missing JSDoc comment to processOrder"
   [Independent of previous change]

3. Then: "Update console.log to use logger module"
   [Independent of previous changes]

Sequential iteration = clear success at each step
```

### Real-World Refinement Example

**Initial Request (Vague):**
```
User: "Create a function to process user data transformation"
```

**Step 1: Clarify with Examples**
```
Claude: "I need concrete examples to understand requirements:

INPUT:
{
  "firstName": "  John  ",
  "email": "JOHN@EXAMPLE.COM",
  "age": "25",
  "joinDate": "2025-01-15"
}

Expected OUTPUT:
[A] { firstName: "John", email: "john@example.com", age: 25, joinDate: Date }
[B] { firstName: "John", email: "john@example.com", age: 25, joinDate: "2025-01-15" }
[C] Something else?

Also, for edge cases:
- Empty firstName: reject or allow?
- Invalid email: throw error or skip?
- Age < 0: valid or invalid?
- Missing fields: required or optional?
"

User provides examples → clarity achieved
```

**Step 2: Interview for Requirements**
```
Claude: "Also need to understand:
- Should this mutate the input object or return new object?
- Are there data validation rules beyond type conversion?
- Error handling: throw on first error or collect all errors?
- Logging/debugging needed during transformation?
"

User answers → design locked in
```

**Step 3: Test-Driven Implementation**
```
User: "Here's the test suite..."
Claude: [Implements function to pass tests]

Tests catch edge cases iteratively
```

**Result:**
✓ Implemented exactly what was needed
✓ No rework due to misunderstandings
✓ All edge cases covered by tests
✓ Design considerations addressed beforehand

---

## Task 3.6: CI/CD Pipeline Integration

### Overview

Claude Code can be integrated into automated CI/CD workflows with specific flags and configurations to enable non-interactive operation and structured output.

### Key Flags and Options

| Flag | Purpose | Usage |
|------|---------|-------|
| `-p` or `--print` | Non-interactive mode | Run in CI without user input |
| `--output-format json` | Machine-readable output | Parse results programmatically |
| `--json-schema` | Enforce output structure | Validate results before posting |
| `--context` | Provide CLAUDE.md context | Apply project standards in CI |

### Flag 1: Non-Interactive Mode (-p / --print)

The `-p` or `--print` flag prevents interactive input hangs in automated pipelines:

```bash
# ❌ WRONG: Will hang waiting for input
claude code review src/api.ts

# ✅ CORRECT: Non-interactive, runs to completion
claude code review src/api.ts -p
```

Use case: CI/CD pipeline should never wait for user input

```yaml
# GitHub Actions example
- name: Code Review via Claude
  run: claude code review src/api.ts -p

# Never hangs, completes and returns exit code
```

### Flag 2: JSON Output Format

Use `--output-format json` with `--json-schema` to produce machine-parseable output:

```bash
# Output as JSON matching schema
claude analyze-security src/ \
  --output-format json \
  --json-schema '{
    "vulnerabilities": [
      {
        "type": "string",
        "severity": "critical|high|medium|low",
        "location": "string",
        "fix": "string"
      }
    ]
  }'
```

Output example:
```json
{
  "vulnerabilities": [
    {
      "type": "SQL Injection",
      "severity": "critical",
      "location": "src/api.ts:42",
      "fix": "Use parameterized query instead of string concatenation"
    },
    {
      "type": "Missing Input Validation",
      "severity": "high",
      "location": "src/handlers/user.ts:128",
      "fix": "Validate email format before processing"
    }
  ]
}
```

This allows automated tools to:
- Parse results programmatically
- Post inline PR comments
- Block merges based on severity
- Track metrics over time

### Flag 3: CLAUDE.md Context in CI

Provide project context via CLAUDE.md so CI-invoked Claude Code follows team standards:

```yaml
# .claude/CLAUDE.md (committed to git)
project_standards:
  testing:
    framework: jest
    coverage_minimum: 80%
    conventions: "*.test.ts for unit tests"
  code_review_criteria:
    - All changes must include tests
    - No hardcoded secrets
    - Performance review for database changes
  ci_expectations:
    - Security scanning required
    - Linting must pass
    - Tests must pass
```

When Claude Code runs in CI, it loads this context and applies standards automatically.

### Real-World CI/CD Integration Examples

#### Example 1: Automated Code Review on PR

```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review

on:
  pull_request:
    paths:
      - 'src/**'
      - 'tests/**'

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Claude Code Review
        run: |
          claude code-review \
            --context .claude/CLAUDE.md \
            --output-format json \
            --json-schema '{
              "issues": [
                {
                  "file": "string",
                  "line": "number",
                  "severity": "critical|high|medium|low",
                  "type": "security|performance|style|quality",
                  "message": "string",
                  "suggestion": "string"
                }
              ]
            }' \
            -p > review.json

      - name: Post Review Comments
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const review = JSON.parse(fs.readFileSync('review.json', 'utf8'));

            for (const issue of review.issues) {
              github.rest.pulls.createReviewComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                pull_number: context.issue.number,
                body: `**[${issue.severity.toUpperCase()}]** ${issue.type}\n${issue.message}\n\n**Suggestion:** ${issue.suggestion}`,
                commit_id: context.payload.pull_request.head.sha,
                path: issue.file,
                line: issue.line
              });
            }

      - name: Block if Critical Issues
        run: |
          critical=$(jq '[.issues[] | select(.severity=="critical")] | length' review.json)
          if [ $critical -gt 0 ]; then
            echo "❌ Found $critical critical issues"
            exit 1
          fi
```

#### Example 2: Automated Test Generation

```yaml
# .github/workflows/generate-tests.yml
name: Generate Tests for New Code

on:
  pull_request:
    paths:
      - 'src/**'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate Tests
        run: |
          # Get changed files
          changed_files=$(git diff origin/main...HEAD --name-only | grep "src/.*\.ts$" | grep -v ".test.ts")

          for file in $changed_files; do
            echo "Generating tests for $file"
            claude generate-tests \
              --context .claude/CLAUDE.md \
              --file "$file" \
              -p > "${file%.ts}.test.ts"
          done

      - name: Create Test Files PR Comment
        run: |
          generated_files=$(find src -name "*.test.ts" -newer .git 2>/dev/null || true)
          if [ ! -z "$generated_files" ]; then
            echo "### 🧪 Generated Tests" >> $GITHUB_STEP_SUMMARY
            echo "The following test files were generated:" >> $GITHUB_STEP_SUMMARY
            echo "$generated_files" | sed 's/^/- /' >> $GITHUB_STEP_SUMMARY
          fi
```

#### Example 3: Security Scanning in CI

```yaml
# .github/workflows/security-scan.yml
name: Security Scanning

on:
  push:
    branches: [main, develop]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Scan for Security Issues
        run: |
          claude security-scan src/ \
            --context .claude/CLAUDE.md \
            --output-format json \
            --json-schema '{
              "issues": [
                {
                  "type": "string",
                  "severity": "critical|high",
                  "file": "string",
                  "line": "number",
                  "details": "string"
                }
              ]
            }' \
            -p > security-report.json

      - name: Upload Security Report
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: security-report.json

      - name: Fail on Critical Issues
        run: |
          critical=$(jq '[.issues[] | select(.severity=="critical")] | length' security-report.json)
          if [ $critical -gt 0 ]; then
            echo "❌ CRITICAL SECURITY ISSUES FOUND"
            jq '.issues[] | select(.severity=="critical")' security-report.json
            exit 1
          fi
```

### Session Context Isolation in CI/CD

**Critical Understanding:** The same Claude session that generated code is less effective at reviewing its own changes.

Why?
- Session context is "contaminated" with implementation decisions
- Claude assumes its own code is correct
- Independent reviews catch issues current session missed

```
❌ WRONG APPROACH:
1. Claude generates code
2. Same Claude session reviews its own code
3. Misses its own bugs

✅ CORRECT APPROACH:
1. Claude generates code (Session A)
2. Fresh Claude instance reviews code (Session B)
3. Independent perspective catches issues
```

Implementation in CI:

```yaml
# Two separate jobs = two separate sessions
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate Code
        run: claude generate-api-endpoints --context .claude/CLAUDE.md -p > generated.ts

      - name: Commit Generated Code
        run: |
          git add generated.ts
          git commit -m "Auto-generated code"

  review:
    needs: generate  # Wait for generate to finish
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Review Generated Code
        run: |
          # Fresh session, independent review
          claude review-code generated.ts \
            --context .claude/CLAUDE.md \
            -p > review.json

          # Fails if review finds issues
          issues=$(jq '.issues | length' review.json)
          if [ $issues -gt 0 ]; then
            echo "❌ Review found $issues issues"
            exit 1
          fi
```

### Including Prior Review Findings

When re-running reviews after new commits, provide previous findings to avoid duplicate comments:

```bash
# First run (initial review)
claude code-review src/ \
  --context .claude/CLAUDE.md \
  -p > review-v1.json

# After developer makes changes...
# Run again, but tell Claude about prior findings

claude code-review src/ \
  --context .claude/CLAUDE.md \
  --prior-findings review-v1.json \
  --report-only-new-issues \
  -p > review-v2.json

# review-v2.json contains ONLY new issues, not repeats
```

### Avoiding Duplicate Test Suggestions

Provide existing test files in context so test generation avoids suggesting duplicate scenarios:

```bash
# Get existing tests
existing_tests=$(find src -name "*.test.ts" -type f)

# Generate new tests, but exclude existing coverage
claude generate-tests src/newFeature.ts \
  --context .claude/CLAUDE.md \
  --existing-tests "$existing_tests" \
  --avoid-duplicate-scenarios \
  -p > newFeature.test.ts
```

### Documentation: CLAUDE.md for CI

Document testing standards, valuable test criteria, and available fixtures:

```yaml
# .claude/CLAUDE.md - CI/CD section

ci_context:
  description: |
    This section describes testing standards and fixtures
    used when Claude Code runs in automated pipelines.

  testing_framework: jest
  test_location: "src/**/*.test.ts"

  fixtures:
    - name: users
      location: test/fixtures/users.json
      description: Sample user objects with various states

    - name: orders
      location: test/fixtures/orders.json
      description: Order objects at various stages

    - name: errors
      location: test/fixtures/errors.json
      description: Error scenarios and edge cases

  test_criteria:
    must_have:
      - Happy path test (normal operation)
      - At least one edge case (null, undefined, empty)
      - At least one error case

    valuable_additions:
      - Performance test (if operation expensive)
      - Integration test (if uses database)
      - Concurrency test (if uses async)

  ci_integration:
    - Code review runs on all PRs (src/ and tests/)
    - Tests must pass before merge
    - Coverage must be >= 80%
    - Security scan required for server code
    - Performance review for database changes
```

---

## Key Concepts Summary

### Essential Knowledge for Exam

#### Configuration Hierarchy
- **User-level** (~/.claude/CLAUDE.md): Personal only, not shared
- **Project-level** (.claude/CLAUDE.md): Team standards, shared via git
- **Directory-level** (./subdir/CLAUDE.md): Package-specific
- Use **@import** to modularize and reference external files
- Use **/memory command** to verify loaded configuration

#### Commands vs Skills
- **Commands**: Quick aliases in .claude/commands/
- **Skills**: Structured workflows in .claude/skills/ with SKILL.md
- **context: fork**: Run skill in isolated sub-agent
- **allowed-tools**: Restrict tool access in skills
- **argument-hint**: Prompt for required parameters

#### Path-Specific Rules
- Located in .claude/rules/ with YAML frontmatter
- Use **paths** field with glob patterns
- Load only when editing matching files
- More efficient than directory-level CLAUDE.md for scattered files

#### Plan vs Direct Execution
- **Plan Mode**: Architectural decisions, multiple approaches, large scope (20+ files)
- **Direct**: Simple changes, single file, clear scope
- Use **Explore subagent** to isolate verbose discovery
- **Session isolation**: Independent review sessions catch more issues

#### Iterative Refinement
- **Input/output examples**: Most effective for clarity
- **Test-driven**: Write tests first, iterate to pass
- **Interview pattern**: Ask questions before implementing
- **Targeted test cases**: Fix specific edge cases
- **Issue batching**: Interacting issues together, independent separately

#### CI/CD Integration
- **-p flag**: Non-interactive mode
- **--output-format json**: Machine-parseable output
- **--json-schema**: Enforce output structure
- **CLAUDE.md context**: Apply standards in CI
- **Session isolation**: Use separate sessions for generation and review
- **Prior findings**: Include previous reviews to avoid duplicates

---

## Common Exam Traps

### Trap 1: User-Level vs Project-Level Configuration

**Trap Statement:**
"A team member created CLAUDE.md in their ~/.claude/CLAUDE.md with comprehensive team standards. Other team members can now use these standards."

**Answer:** FALSE ❌

**Correct Understanding:**
User-level configuration (~/.claude/CLAUDE.md) is local to that user only. It's not shared via version control. Team standards must go in project-level configuration (.claude/CLAUDE.md or CLAUDE.md at project root).

**Related Questions Likely:**
- "Where should team coding standards be stored?" → .claude/CLAUDE.md (version controlled)
- "A new developer doesn't follow team conventions. What's the likely cause?" → Standards in user-level, not project-level

---

### Trap 2: Skills Execution Context

**Trap Statement:**
"When I create a skill with context: fork, the skill's output appears immediately in the main conversation."

**Answer:** FALSE ❌

**Correct Understanding:**
`context: fork` runs the skill in an isolated sub-agent. The verbose output stays in the sub-agent. Only the summary is returned to the main conversation. This preserves main conversation context.

**Related Questions Likely:**
- "Which skill frontmatter option prevents verbose output from polluting the main conversation?" → context: fork
- "When should you use context: fork?" → Exploratory analysis, verbose discovery, brainstorming alternatives

---

### Trap 3: Path-Specific Rules Scope

**Trap Statement:**
"Path-specific rules in .claude/rules/testing.md with paths: ['**/*.test.ts'] will load whenever ANY file in the project is edited."

**Answer:** FALSE ❌

**Correct Understanding:**
Path-specific rules only load when editing files matching the glob pattern. A rule with `paths: ['**/*.test.ts']` only loads when editing test files.

**Related Questions Likely:**
- "What's the advantage of path-specific rules over directory-level CLAUDE.md?" → Rules load only when relevant, reduce irrelevant context
- "How do path-specific rules affect token usage?" → More efficient, load only when needed

---

### Trap 4: Plan Mode vs Direct Execution

**Trap Statement:**
"Plan mode should always be used because it reduces the risk of making mistakes."

**Answer:** FALSE ❌

**Correct Understanding:**
Plan mode adds overhead. Direct execution is more efficient for simple, well-scoped changes. Plan mode is for complex changes with multiple valid approaches.

**Related Questions Likely:**
- "When should you use direct execution?" → Simple, single-file, clear scope
- "What's the main benefit of plan mode?" → Validate approach before implementation, prevent rework
- "A developer asks: 'Should I use plan mode for adding a single validation check?' " → No, direct execution is appropriate

---

### Trap 5: CI/CD Session Context

**Trap Statement:**
"Use the same Claude session for both code generation and code review in CI to maintain consistency."

**Answer:** FALSE ❌

**Correct Understanding:**
Independent review sessions catch more issues. The generating session has contaminated context and assumes its own code is correct. Use separate CI jobs (separate sessions) for generation and review.

**Related Questions Likely:**
- "Why is independent review more effective than self-review?" → Fresh perspective catches issues generating session missed
- "How should code review be structured in CI?" → Separate job = separate session

---

### Trap 6: @import Syntax

**Trap Statement:**
"The @import syntax in CLAUDE.md only works for internal .claude/rules/ files."

**Answer:** FALSE ❌

**Correct Understanding:**
@import can reference any external file, not just .claude/rules/. You can import from shared standards files, external documentation, etc.

```yaml
# Both valid
@import .claude/rules/testing.md              # Internal rule
@import /docs/team-standards.md               # External doc
@import ../shared-rules/typescript.md          # Relative path
```

---

### Trap 7: Skill Tool Restrictions

**Trap Statement:**
"If a skill's allowed-tools includes Read and Grep, it can also use Write and Edit."

**Answer:** FALSE ❌

**Correct Understanding:**
`allowed-tools` is restrictive, not permissive. Only listed tools are allowed. If Edit isn't listed, the skill cannot modify files.

---

### Trap 8: Iterative Refinement Ordering

**Trap Statement:**
"When fixing multiple issues, always batch all issues in a single message for efficiency."

**Answer:** FALSE ❌

**Correct Understanding:**
Batch interacting issues (changes affect each other). Fix independent issues sequentially (clearer validation at each step).

---

## Quick Reference Cheatsheet

### Configuration File Locations

```
User Level (Local)
├── ~/.claude/CLAUDE.md
├── ~/.claude/commands/
├── ~/.claude/skills/
└── [NOT version controlled]

Project Level (Shared)
├── .claude/CLAUDE.md (or /CLAUDE.md)
├── .claude/commands/
├── .claude/skills/
├── .claude/rules/
└── [Committed to git]

Directory Level (Scoped)
├── ./packages/api/CLAUDE.md
├── ./src/services/CLAUDE.md
└── [Committed to git]
```

### Directory Structure Template

```
.claude/
├── CLAUDE.md                    # Main config with @imports
├── commands/
│   ├── format-pr.txt
│   └── test-all.txt
├── skills/
│   ├── code-review/
│   │   └── SKILL.md
│   ├── generate-tests/
│   │   └── SKILL.md
│   └── performance-audit/
│       └── SKILL.md
└── rules/
    ├── README.md                # Documents each rule
    ├── typescript-standards.md
    ├── testing-standards.md
    ├── api-conventions.md
    ├── security-checklist.md
    └── deployment-standards.md
```

### CLAUDE.md Structure

```yaml
# Root configuration
project_name: "Project Name"
project_description: |
  Brief description

base_standards: |
  @import .claude/rules/typescript-standards.md
  @import .claude/rules/testing-standards.md
  @import .claude/rules/security-checklist.md

coding_standards:
  language: typescript
  style_guide: |
    [standards]
  testing:
    framework: jest
    coverage: 80%
  api_conventions: |
    [conventions]

review_criteria:
  - [criteria 1]
  - [criteria 2]

deployment:
  environments: [dev, staging, prod]
  strategy: "Rolling deployment"

ci_context:
  testing_framework: jest
  fixtures:
    - name: [fixture]
      location: [path]
```

### SKILL.md Frontmatter Template

```yaml
---
name: Skill Name
description: What the skill does
version: 1.0.0
context: fork  # or inline
allowed-tools:
  - Read
  - Grep
  - Glob
argument-hint: |
  Usage: /skillname [args]
  Example: /skillname example
---

# Skill implementation here
```

### Path-Specific Rule Template

```yaml
# .claude/rules/rule-name.md
---
name: Rule Name
description: When and why this rule applies
paths:
  - "**/*.test.ts"
  - "tests/**/*"
---

# Rule content here
```

### CLI Flags Quick Reference

```bash
# Non-interactive mode
claude [command] -p
claude [command] --print

# JSON output
claude [command] --output-format json

# JSON schema validation
claude [command] --json-schema '{...}'

# Context
claude [command] --context .claude/CLAUDE.md

# Combined
claude analyze-security src/ \
  -p \
  --output-format json \
  --context .claude/CLAUDE.md
```

### Decision Trees

**Plan vs Direct:**
```
Task well-scoped and clear?
├─ YES → Direct Execution
└─ NO → Plan Mode (+ Explore if verbose)
```

**Configuration Level:**
```
Should all team members see this?
├─ YES → .claude/CLAUDE.md (project-level)
└─ NO → ~/.claude/CLAUDE.md (user-level)
```

**Rules Organization:**
```
Do rules apply to scattered files across codebase?
├─ YES → .claude/rules/ with glob patterns
└─ NO → Directory-level CLAUDE.md
```

**Issue Batching:**
```
Do issues interact with each other?
├─ YES → Fix together in one message
└─ NO → Fix sequentially
```

### Exam Format Reminders

- **20% of exam** (14 questions)
- Mix of **scenario-based** and **knowledge** questions
- Focus on **practical application** in team settings
- Watch for **team sharing vs personal** scenarios
- Pay attention to **scope and level** of configuration
- Understand **when/why** to use each approach

---

## Practice Scenarios

### Scenario 1: New Team Member Not Following Standards

**Situation:**
A new developer joins the team. Claude Code is generating code that doesn't follow the team's established conventions for function naming, error handling, and testing patterns.

**Question:**
What's the most likely cause and how do you fix it?

**Expected Answer:**
The team standards are probably in ~/.claude/CLAUDE.md (user-level) instead of .claude/CLAUDE.md (project-level). User-level config isn't shared via git, so new team members don't get it.

Fix: Move standards to .claude/CLAUDE.md and commit to git. Run `/memory` to verify loading.

---

### Scenario 2: Monorepo with Scattered Test Files

**Situation:**
You have a monorepo with test files scattered across multiple packages:
```
packages/api/src/services/user.test.ts
packages/api/tests/integration/user.integration.ts
packages/web/src/components/__tests__/Button.test.tsx
packages/auth/tests/...
```

All should follow the same testing conventions. Should you create CLAUDE.md files in each packages/ subdirectory or use path-specific rules?

**Expected Answer:**
Use path-specific rules in .claude/rules/testing.md with:
```yaml
paths:
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/tests/**/*"
```

This is cleaner than creating multiple CLAUDE.md files with duplicate conventions.

---

### Scenario 3: Complex API Migration

**Situation:**
Your REST API needs to migrate to GraphQL. This affects:
- 45 endpoint files
- 60 test files
- Database schema integration
- Client SDK
- Documentation

Should you use plan mode or direct execution?

**Expected Answer:**
Plan mode. This is:
- Large scope (100+ files)
- Architectural decision
- Multiple valid approaches
- Unclear dependencies

Steps:
1. Use plan mode to explore current implementation
2. Propose migration strategy
3. Get approval
4. Execute with separate sessions for independence

---

### Scenario 4: Skill Design Decision

**Situation:**
You want to create a skill that performs deep codebase analysis, examining imports, dependencies, and usage patterns across 50+ files. The analysis output will be verbose and exploratory. How should you configure the skill?

**Expected Answer:**
Use `context: fork` to run in isolated sub-agent:
```yaml
---
name: Codebase Structure Analyzer
description: Deep analysis of codebase dependencies
context: fork  # ← Key decision
allowed-tools:
  - Read
  - Grep
  - Glob
---
```

This prevents verbose discovery output from polluting the main conversation while returning a useful summary.

---

### Scenario 5: CI/CD Review Duplication

**Situation:**
Your CI/CD pipeline runs code review on every commit. After the first review found 5 issues and the developer fixed 3 of them, you want to run review again. The concern: the next review will report the 3 already-fixed issues again, creating duplicate PR comments.

How do you prevent duplicate review comments?

**Expected Answer:**
Include prior review findings:
```bash
claude code-review src/ \
  --context .claude/CLAUDE.md \
  --prior-findings review-v1.json \
  --report-only-new-issues \
  -p > review-v2.json
```

This tells Claude to only report new or still-unaddressed issues, avoiding duplicates.

---

## Final Tips for Exam Success

1. **Focus on scope and sharing:**
   - User-level = personal only
   - Project-level = team shared
   - This distinction appears in many questions

2. **Understand the "why" not just the "what":**
   - Why use plan mode? (Validate before expensive changes)
   - Why use path-specific rules? (Reduce token usage)
   - Why use context: fork? (Isolate verbose output)

3. **Watch for team collaboration scenarios:**
   - New team member scenarios
   - Configuration not being shared
   - Inconsistent behavior across team

4. **Know the CLI flags:**
   - `-p` for non-interactive
   - `--output-format json` for CI
   - `--json-schema` for validation

5. **Understand session isolation:**
   - Same session reviewing own code is less effective
   - CI should use separate sessions
   - Independent reviews catch more issues

6. **Be familiar with real-world patterns:**
   - What a well-organized .claude/ directory looks like
   - How to use @import for modularity
   - When to batch issues vs iterate sequentially

7. **Pay attention to scalability:**
   - How do you handle monorepos?
   - How do you manage 100+ files?
   - How do you share configuration across teams?

---

## Additional Resources

### Key Command References

```bash
# View loaded configuration
/memory

# List available skills
/list-skills

# Run skill in non-interactive mode
/skillname arg1 arg2 -p

# Generate with JSON output
claude analyze-code src/ --output-format json -p
```

### Configuration Validation Checklist

Before committing configuration:
- [ ] Team standards are in `.claude/CLAUDE.md` (not `~/.claude/CLAUDE.md`)
- [ ] `.claude/` directory is committed to git
- [ ] `.gitignore` doesn't exclude `.claude/`
- [ ] @imports reference correct file paths
- [ ] Skills have clear argument-hint documentation
- [ ] Path-specific rules use valid glob patterns
- [ ] Commands are in `.claude/commands/` for team sharing
- [ ] `/memory` shows all expected configuration files

### Exam Study Checklist

- [ ] Understand 3-level configuration hierarchy
- [ ] Know when to use commands vs skills
- [ ] Can identify when to use path-specific rules
- [ ] Understand plan mode vs direct execution decision
- [ ] Know iterative refinement techniques
- [ ] Understand CI/CD integration patterns
- [ ] Can diagnose configuration hierarchy issues
- [ ] Know what `-p` flag does
- [ ] Understand session context isolation
- [ ] Know common exam traps (review above section)

---

**Last updated:** March 2026
**Exam version:** Claude Certified Architect – Foundations (2025-2026)
**Domain weight:** 20% (14 questions)
