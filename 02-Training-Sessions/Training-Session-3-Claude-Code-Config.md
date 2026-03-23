# Training Session 3: Claude Code Configuration & Workflows
## Claude Certified Architect – Foundations

**Duration:** 2 hours | **Domain Weight:** 20% (14 questions)
**Prerequisites:** Sessions 1-2 completed, Claude Code installed locally
**Level:** Intermediate

---

## Session Overview

Domain 3 shifts focus from Claude's core capabilities to **how we configure and orchestrate Claude Code** in production environments. This session covers the mechanics of configuration hierarchy, custom commands, path-specific rules, execution strategies, and CI/CD integration. By the end, you'll understand how to build scalable, maintainable Claude Code workflows that follow enterprise best practices.

**Key Theme:** Configuration is code. The same principles that make your application code maintainable—modularity, scoping, DRY, conditional logic—apply to Claude Code configuration.

---

## Learning Objectives

By the end of this session, you will be able to:

1. Design and implement multi-level CLAUDE.md hierarchies using @import
2. Create custom slash commands and skills with appropriate scoping and constraints
3. Configure path-specific rules using glob patterns and YAML frontmatter
4. Choose between plan mode and direct execution based on task complexity
5. Apply iterative refinement patterns to improve Claude Code outcomes
6. Integrate Claude Code into CI/CD pipelines with non-interactive modes
7. Identify exam trap scenarios and avoid common configuration mistakes

---

## Part 1: CLAUDE.md Hierarchy & Organization (30 min)

### The Three-Level Hierarchy

CLAUDE.md is not a single monolithic file. Claude Code respects a **three-level hierarchy** with clear precedence:

```
1. PROJECT-ROOT LEVEL    (lowest precedence)
   └── ./CLAUDE.md

2. SUBDIRECTORY LEVEL    (medium precedence)
   └── ./src/CLAUDE.md
   └── ./tests/CLAUDE.md
   └── ./docs/CLAUDE.md

3. USER-LEVEL            (highest precedence)
   └── ~/.claude/CLAUDE.md
```

**Precedence Rule:** When Claude Code is invoked in a subdirectory, it loads rules from the closest CLAUDE.md file first, then merges upward. If the same rule is defined at multiple levels, the **closest (lowest directory depth) wins**.

### @import for Modular Organization

Rather than maintaining massive CLAUDE.md files, use the `@import` directive to split configuration into focused modules:

```yaml
# ./CLAUDE.md (project root)
---
name: "MyProject"
version: "1.0"
---

@import "./claude-config/core-conventions.md"
@import "./claude-config/testing-rules.md"
@import "./claude-config/api-standards.md"
@import "./claude-config/security-policies.md"
```

The `@import` paths are **relative to the location of the CLAUDE.md file**, not the current working directory. This ensures portability when projects are cloned or moved.

### Scoping Rules and Precedence

Key precedence rules to memorize:

| Rule | Precedence | Example |
|------|-----------|---------|
| Closest CLAUDE.md file | Higher | `/src/CLAUDE.md` overrides `/CLAUDE.md` when working in `/src` |
| Explicit rules | Higher | A rule that says "use 4 spaces" overrides default 2-space indentation |
| Merged rules | Additive | Testing rules from one import + API rules from another = combined effect |
| User-level ~/.claude/CLAUDE.md | Highest | Always overrides project-level settings if defined |

**Exam Trap #1:** Many exam takers assume all imports merge equally. In reality, **scoping proximity matters more than import order**. A rule defined in `/src/CLAUDE.md` will override the same rule in `/CLAUDE.md` even if the root import came first.

### Code/Config Examples

**Directory structure:**
```
myproject/
├── CLAUDE.md                 # Project root config
├── .claude/
│   ├── core-conventions.md
│   ├── testing-rules.md
│   ├── api-standards.md
│   └── security-policies.md
├── src/
│   ├── CLAUDE.md            # Subdirectory override
│   └── services/
│       └── auth.ts
└── tests/
    ├── CLAUDE.md            # Testing-specific overrides
    └── integration.test.ts
```

**Root CLAUDE.md:**
```yaml
---
name: "MyProject"
version: "1.0"
description: "Enterprise data processing system"
---

@import "./.claude/core-conventions.md"
@import "./.claude/api-standards.md"
@import "./.claude/security-policies.md"

## General Conventions
- Use TypeScript for all backend code
- All files must have JSDoc comments
- Test coverage target: 85%
```

**src/CLAUDE.md (subdirectory override):**
```yaml
---
scope: "src/**"
priority: "high"
---

## Service Layer Conventions
- Services must implement dependency injection
- All async operations must have timeout handlers
- Use Result<T, E> pattern for error handling (no exceptions)

## Code style for /src
- Indent: 2 spaces (overrides project default of 4)
- Max line length: 100 characters in src/, 120 elsewhere
```

**tests/CLAUDE.md:**
```yaml
---
scope: "tests/**"
---

## Testing Conventions
- Use Jest as test framework
- Test file naming: *.test.ts
- Mock external dependencies
- No real API calls in unit tests
```

**.claude/security-policies.md:**
```yaml
## Security Rules
- Never commit secrets to version control
- All API endpoints must validate input
- Use HTTPS for external communications
- Encrypt sensitive data at rest
```

### Practice Question

**Scenario:** You have `/CLAUDE.md` with "indent: 4 spaces" and `/src/CLAUDE.md` with "indent: 2 spaces". You're working on a file at `/src/services/auth.ts`. Which indentation rule applies?

A) 4 spaces (project root always wins)
B) 2 spaces (closest CLAUDE.md wins)
C) Both apply (merged)
D) User-level ~/.claude/CLAUDE.md decides

**Answer:** B. The closest CLAUDE.md file wins. Since you're in `/src`, the `/src/CLAUDE.md` rule (2 spaces) takes precedence.

---

## Part 2: Custom Slash Commands & Skills (25 min)

### Commands vs Skills

Claude Code provides two mechanisms for extending functionality:

**Commands** (lightweight, fast):
- Live in `./commands/` directory
- Execute immediately in Claude's current context
- Good for quick utilities, formatting, suggestions
- Limited isolation
- Example: `/format-json`, `/summarize`, `/generate-test`

**Skills** (robust, isolated):
- Live in `./skills/` directory
- Execute with `context: fork` (isolated environment)
- Maintain state, complex logic, tool access control
- Slower startup but safer
- Example: `/deploy`, `/audit-security`, `/generate-migration`

### The context: fork Mechanism

When a skill runs with `context: fork`, Claude Code creates an **isolated execution context**:

- Separate memory/state from parent session
- Tool access restrictions via `allowed-tools`
- No access to parent session's variables
- Can fail independently without crashing parent
- Useful for untrusted or risky operations

### Skill File Structure

Every skill is a markdown file with YAML frontmatter plus execution logic:

```markdown
---
name: "Security Audit"
description: "Scan codebase for security vulnerabilities"
context: fork
allowed-tools:
  - read
  - grep
  - bash
  - llm-api-call

argument-hint: "directory path (e.g., '/src')"
---

# Security Audit Skill

## Execution

1. Scan for hardcoded secrets using regex patterns
2. Check for SQL injection vulnerabilities in database code
3. Validate API authentication mechanisms
4. Generate audit report in JSON format

## Parameters

- `target_dir`: Directory to audit (required)
- `severity_level`: minimal|standard|strict (default: standard)
```

### Creating Custom Commands

Commands are simpler—no frontmatter, just markdown:

```markdown
# Format JSON

Formats JSON with proper indentation and validation.

Usage: /format-json <input-file>

This command:
1. Validates JSON syntax
2. Pretty-prints with 2-space indentation
3. Reports any parsing errors
```

Commands execute synchronously and should complete quickly (< 5 seconds).

**Exam Trap #2:** Candidates often confuse `commands/` and `skills/`. Remember: **commands are instant utilities**, **skills are full programs**. If your tool needs tool access control (`allowed-tools`) or might take > 5 seconds, it's a skill.

### Practice Question

**Scenario:** You need to create a tool that:
- Reads sensitive credentials from environment
- Deploys to production servers
- Takes 2-3 minutes to complete
- Should be isolated from parent session

Should this be a command or a skill?

A) Command (faster)
B) Skill with context: fork (isolated execution)
C) Command with allowed-tools restriction
D) Neither, use plain Claude Code

**Answer:** B. This requires isolation (`context: fork`), tool restrictions (`allowed-tools`), and long runtime. Only skills provide these capabilities.

---

## Part 3: Path-Specific Rules (20 min)

### .claude/rules/ Directory

Path-specific rules live in `.claude/rules/` and automatically apply when Claude Code operates in matching file patterns:

```
.claude/
├── rules/
│   ├── test-files.yaml
│   ├── api-endpoints.yaml
│   ├── database-migrations.yaml
│   └── frontend-components.yaml
```

### YAML Frontmatter for Conditional Loading

Each rule file uses glob patterns in frontmatter to determine when it applies:

```yaml
---
name: "Testing Conventions"
glob:
  - "**/*.test.ts"
  - "**/*.spec.ts"
  - "tests/**/*.ts"
apply-mode: "merge"
priority: "high"
---

## Rules that apply only to test files

### Testing Framework
- Framework: Jest
- Assertion library: chai
- Mock library: sinon
- Coverage target: 85%

### Test Structure
- One test per file
- Describe blocks for grouping
- Setup/teardown in beforeEach/afterEach
- Async/await for promises

### Naming Conventions
- Test files: *.test.ts or *.spec.ts
- Test cases: describe("ClassName", () => {})
- Assertions: use chai expect() syntax
```

Another example for API rules:

```yaml
---
name: "API Endpoint Standards"
glob:
  - "src/routes/**/*.ts"
  - "src/api/**/*.ts"
apply-mode: "strict"
---

## API Conventions

### Request/Response
- All endpoints return JSON
- Use standard HTTP status codes
- Include error details in response body

### Authentication
- Bearer token in Authorization header
- Validate on every request
- Return 401 for invalid tokens

### Validation
- Validate input with Joi or Zod
- Return 400 with error details
- Log validation failures
```

### Glob Pattern Matching

Common glob patterns:

| Pattern | Matches |
|---------|---------|
| `*.test.ts` | All .test.ts files in current directory |
| `**/*.test.ts` | All .test.ts files recursively |
| `src/**` | Everything under src/ |
| `src/api/*.ts` | All .ts files directly in src/api/ |
| `tests/**/*.spec.ts` | All .spec.ts files under tests/ |
| `!src/generated/**` | Everything except generated/ |

### Config Examples

**Directory structure:**
```
myproject/
├── .claude/
│   ├── rules/
│   │   ├── test-files.yaml
│   │   ├── migrations.yaml
│   │   └── components.yaml
```

**migrations.yaml:**
```yaml
---
name: "Database Migration Rules"
glob:
  - "db/migrations/**/*.ts"
  - "migrations/**/*.sql"
priority: "high"
---

## Migration Standards

### Naming
- Up migrations: YYYYMMDD_HHmmss_description.ts
- Down migrations: reverse of up

### Content
- Must include both up() and down() functions
- Document schema changes
- Include rollback strategy

### Validation
- Test reversibility before committing
- Never drop columns without backup
```

### Practice Question

**Scenario:** You define a rule file at `.claude/rules/frontend.yaml` with glob pattern `src/components/**/*.tsx`. You're now editing `src/utils/helpers.ts`. Will the frontend rules apply?

A) Yes, because it's in src/
B) No, because helpers.ts doesn't match **/*.tsx
C) Partially (some rules apply)
D) Only if context: fork

**Answer:** B. Glob patterns are precise. `src/components/**/*.tsx` does not match `src/utils/helpers.ts`. The rule file doesn't apply.

---

## Part 4: Plan Mode vs Direct Execution (20 min)

### When to Use Plan Mode

**Plan Mode** (`claude-code --plan`): Claude outlines strategy before executing.

Use plan mode when:
- ✅ Exploring a complex codebase you don't fully understand
- ✅ Planning a large refactoring (> 20 files)
- ✅ Risk of unintended side effects (data migrations, deletions)
- ✅ Stakeholder approval needed before execution
- ✅ Learning what Claude Code would do (audit trail)

Example:
```bash
$ claude-code --plan "refactor authentication system to use OAuth2"
```

Claude responds with:
```
PLAN:
1. Analyze current auth implementation (estimate: 5 files)
2. Design OAuth2 integration points
3. Create new OAuth2 provider module
4. Update login/logout flows
5. Migrate existing sessions
6. Add tests for new flows
7. Update documentation

Estimated time: 3 hours
Risk level: Medium (affects auth, requires testing)
Approval required: Yes
```

### Direct Execution (default)

Use direct execution when:
- ✅ Task is straightforward and low-risk
- ✅ You've already approved the strategy
- ✅ Tight deadline (plan adds 5-10 min overhead)
- ✅ Iterative work (write, test, refine immediately)
- ✅ Generating code, not modifying existing code

Example:
```bash
$ claude-code "add TypeScript types to auth.js"
```

Claude immediately starts implementing.

### Tradeoffs

| Aspect | Plan Mode | Direct |
|--------|-----------|--------|
| Safety | High (review before execute) | Medium (instant execution) |
| Speed | Slow (+ planning overhead) | Fast (immediate action) |
| Approval | Explicit | Implicit |
| Feedback Loop | Slower | Faster |
| Learning | Better (see reasoning) | Faster execution |

**Exam Trap #3:** Many candidates think plan mode is always better. Wrong. For routine tasks (fixing a bug in one file, adding a function), plan mode adds unnecessary delay. Use plan mode only for complex, risky, or exploratory tasks.

### Practice Question

**Scenario:** You need to fix a typo in a single function. The task is "change `getFoo()` to `getBar()` in services/auth.ts". Plan mode or direct execution?

A) Plan mode (always safer)
B) Direct execution (simple, low-risk task)
C) Plan mode first, then direct
D) Depends on context

**Answer:** B. This is a routine fix in a single file. Direct execution is appropriate. Plan mode would waste time.

---

## Part 5: Iterative Refinement Techniques (15 min)

Claude Code excels at **iterative workflows**. Rather than asking for the perfect solution once, guide Claude through multiple cycles of feedback and improvement.

### Feedback Loops in Claude Code

```
Cycle 1: Initial Implementation
├─ Issue: "Generate CRUD API endpoints"
└─ Result: Basic endpoints created

Cycle 2: Add validation
├─ Issue: "Add input validation to endpoints"
└─ Result: Validation middleware added

Cycle 3: Improve error handling
├─ Issue: "Better error messages and HTTP status codes"
└─ Result: Error handling enhanced

Cycle 4: Tests
├─ Issue: "Add unit tests for endpoints"
└─ Result: Test suite created

Cycle 5: Performance
├─ Issue: "Add caching for read endpoints"
└─ Result: Redis caching implemented
```

Each cycle is independent. Claude maintains context and doesn't re-implement previous work.

### Revision Strategies

**Strategy 1: Nested Questions**
```
Cycle 1: "Generate the base function"
Cycle 2: "Make it async and handle errors"
Cycle 3: "Add logging and monitoring"
```

**Strategy 2: Requirement Stacking**
```
Cycle 1: "Create API with validation"
Cycle 2: "Add authentication"
Cycle 3: "Add rate limiting"
Cycle 4: "Add response caching"
```

**Strategy 3: Quality Gates**
```
Cycle 1: Implementation
Cycle 2: Linting and code style
Cycle 3: Test coverage
Cycle 4: Documentation
Cycle 5: Performance review
```

### Practice Question

**Scenario:** You ask Claude Code to "generate a database schema" and receive a schema that's partially correct but missing constraints. What's the best next step?

A) Start over with a more detailed prompt
B) Say "add constraints and validation"
C) Rewrite the entire schema yourself
D) Accept it and move on

**Answer:** B. Iterative refinement is designed for this. A simple follow-up request is more efficient than starting over.

---

## Part 6: Claude Code in CI/CD Pipelines (20 min)

### The -p Flag for Non-Interactive Mode

Claude Code supports **non-interactive (headless) mode** via the `-p` flag, perfect for CI/CD:

```bash
claude-code -p "Run security audit on src/"
```

In this mode:
- No prompts or interactive input
- Reads from stdin if needed
- Returns exit code (0 = success, non-zero = failure)
- Suitable for `git hooks`, CI/CD pipelines, scheduled jobs
- Timeout configurable via environment variable

### --output-format json for Structured Output

Return machine-readable output:

```bash
claude-code -p --output-format json "Audit src/ for security issues"
```

Response:
```json
{
  "status": "completed",
  "duration_seconds": 45,
  "results": {
    "vulnerabilities": 3,
    "warnings": 7,
    "info": 12,
    "critical_issues": [
      {
        "file": "src/auth.ts",
        "line": 42,
        "issue": "Hardcoded secret detected",
        "severity": "critical"
      }
    ]
  },
  "output": "Full audit report...",
  "exit_code": 0
}
```

### Integration Patterns

**Pattern 1: Pre-commit Hook**

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running Claude Code security check..."
claude-code -p --output-format json "Quick security scan of staged files" > /tmp/scan.json

if grep -q "critical_issues" /tmp/scan.json; then
  echo "Security issues found. Commit blocked."
  cat /tmp/scan.json
  exit 1
fi

echo "✓ Security check passed"
exit 0
```

**Pattern 2: GitHub Actions Workflow**

```yaml
name: Claude Code Analysis
on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Claude Code
        run: npm install -g claude-code

      - name: Run code quality checks
        run: |
          claude-code -p --output-format json \
            "Audit src/ for code quality issues" > audit.json

      - name: Parse results
        run: |
          ISSUES=$(jq '.results.issues | length' audit.json)
          echo "Found $ISSUES issues"

      - name: Comment on PR
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            const audit = require('./audit.json');
            github.rest.issues.createComment({
              ...context.repo,
              issue_number: context.issue.number,
              body: `Claude Code found ${audit.results.issues.length} issues`
            });
```

**Pattern 3: Scheduled Daily Audit**

```yaml
# .claude-code/scheduled-audit.yaml
name: "Daily Security Audit"
schedule: "0 2 * * *"  # 2 AM daily
command: "claude-code -p --output-format json \"Full security audit of codebase\""
output-handler: |
  Parse JSON output
  Log critical issues
  Send Slack notification if issues > 0
```

### Config Examples

**.claude-code/ci-config.yaml:**
```yaml
---
name: "CI/CD Configuration"
context: ci-pipeline
---

## Non-interactive Mode Defaults
timeout: 300  # 5 minutes max
exit-on-first-error: true
log-level: "info"

## Tool Restrictions for CI
allowed-tools:
  - read
  - grep
  - bash
  - analyze

blocked-tools:
  - shell-execute  # Dangerous in pipelines
  - modify-production  # Prevent accidental changes

## Output Format
default-output: "json"
json-schema:
  version: "1.0"
  required-fields:
    - status
    - duration_seconds
    - results
```

### Practice Questions

**Question 1:** You want Claude Code to run in a GitHub Actions workflow without any user interaction. Which flag(s) do you use?

A) Just --output-format json
B) -p flag only
C) -p and --output-format json
D) No special flags needed

**Answer:** C. The `-p` flag enables non-interactive mode, and `--output-format json` makes output parseable by other tools.

**Question 2:** Your CI/CD pipeline has a 5-minute timeout, and Claude Code is taking 10 minutes. Where do you configure the timeout?

A) In the shell script calling Claude Code
B) In CLAUDE.md with timeout: 300
C) In ~/.claude/config.yaml
D) Via environment variable CLAUDE_TIMEOUT

**Answer:** B or D are most likely, depending on the setup. Configuration in CLAUDE.md is cleaner for project-specific timeouts.

**Exam Trap #4:** Candidates often forget that `-p` is **required** for CI/CD pipelines. Without it, Claude Code waits for interactive input and the pipeline hangs. Always use `-p --output-format json` together in pipelines.

---

## Session Summary & Key Takeaways

| Concept | Key Point |
|---------|-----------|
| **CLAUDE.md Hierarchy** | Closest file wins. Use @import for modularity. |
| **Scope & Precedence** | Subdirectory rules override parent rules. User-level is highest. |
| **Commands vs Skills** | Commands: quick utilities. Skills: isolated, robust programs. |
| **context: fork** | Isolates skill execution. Use for risky operations. |
| **Path-Specific Rules** | .claude/rules/ with glob patterns apply automatically. |
| **Plan Mode** | Use for complex/risky tasks. Skip for routine work. |
| **Iterative Refinement** | Multiple cycles beat one-shot perfection. |
| **CI/CD Integration** | Always use -p and --output-format json in pipelines. |

---

## Hands-On Lab Exercise

**Time: 30 minutes**

### Lab Scenario

You're building a TypeScript microservice project. Configure Claude Code to:

1. **CLAUDE.md Hierarchy** (10 min)
   - Create project-root CLAUDE.md with general conventions
   - Create src/CLAUDE.md with stricter rules for service layer
   - Create tests/CLAUDE.md with testing conventions
   - Use @import to modularize configuration

2. **Custom Skill** (10 min)
   - Create a skill at `skills/run-tests.md`
   - Use `context: fork`
   - Restrict allowed-tools to: bash, read
   - Document the skill's purpose and usage

3. **Path-Specific Rules** (10 min)
   - Create `.claude/rules/test-files.yaml`
   - Apply to `**/*.test.ts` files
   - Add testing conventions (framework, assertions, coverage)

### Deliverables

- [ ] Project directory structure with all CLAUDE.md files
- [ ] Verified that closest CLAUDE.md wins when working in subdirectories
- [ ] Custom skill file with proper frontmatter
- [ ] Path-specific rule file with glob patterns

---

## Self-Assessment Quiz

**Question 1:** You have CLAUDE.md at both `/` and `/src/`. When editing `/src/services/auth.ts`, which CLAUDE.md applies?

A) Both, merged equally
B) Only /src/CLAUDE.md
C) Only /CLAUDE.md
D) Depends on import order

**Answer:** B. Closest file wins. /src/CLAUDE.md takes precedence when working in /src.

---

**Question 2:** What's the primary difference between a command and a skill?

A) Commands are faster
B) Skills have context: fork isolation
C) Commands can't access tools
D) All of the above

**Answer:** D. Commands are lightweight utilities; skills are isolated, full-featured programs.

---

**Question 3:** When should you use plan mode?

A) Always (safest)
B) Never (wastes time)
C) For complex, risky, or exploratory tasks
D) Only in CI/CD pipelines

**Answer:** C. Plan mode adds overhead. Use it strategically for high-risk or complex tasks.

---

**Question 4:** Which command runs Claude Code in a CI/CD pipeline without user interaction?

A) claude-code "task"
B) claude-code -i "task"
C) claude-code -p "task"
D) claude-code --headless "task"

**Answer:** C. The -p flag enables non-interactive mode.

---

**Question 5:** A path-specific rule with glob pattern `src/api/**/*.ts` applies to which files?

A) All .ts files in src/api/ (including subdirectories)
B) Only .ts files directly in src/api/
C) All files in src/api/ regardless of extension
D) All .ts files in src/

**Answer:** A. The ** pattern matches all subdirectories recursively.

---

**Question 6:** Your skill needs to validate JSON and write results. Which tools should be in allowed-tools?

A) Just "bash"
B) "bash" and "write"
C) "read", "bash", "write"
D) All tools (no restrictions)

**Answer:** C. The skill needs to read input (read), validate it (bash), and write results (write). Principle of least privilege: allow only necessary tools.

---

**Question 7:** In iterative refinement, if Claude Code makes a mistake in Cycle 1, what's the best approach?

A) Start over with a detailed new prompt
B) Use a simple follow-up request to fix it
C) Rewrite the code manually
D) Accept it and move on

**Answer:** B. Iterative refinement is designed for this. A targeted follow-up is more efficient.

---

**Question 8:** What output format should you use when parsing Claude Code results in a CI/CD pipeline?

A) Plain text
B) Markdown
C) JSON
D) CSV

**Answer:** C. JSON is structured and parseable by other tools. Always use --output-format json in CI/CD.

---

## Recommended Study Resources

### Official Documentation
- Claude Code Configuration Guide (Anthropic docs)
- CLAUDE.md Specification
- Skill Development Best Practices

### Hands-On Practice
- Build a multi-module CLAUDE.md hierarchy in a real project
- Create at least 3 custom skills with different allowed-tools configurations
- Set up a GitHub Actions workflow using claude-code -p
- Experiment with path-specific rules on different file patterns

### Key Concepts to Drill
- The three-level CLAUDE.md hierarchy and precedence rules
- Difference between context: fork and inline execution
- When to use plan mode (complex/risky) vs direct execution (simple/routine)
- CI/CD integration with -p and --output-format json
- Glob pattern matching in path-specific rules

### Common Exam Traps to Review
1. Closest CLAUDE.md wins, not project root
2. Commands ≠ Skills (different use cases)
3. Plan mode is optional, not mandatory
4. -p flag is required for CI/CD, not optional
5. Glob patterns are precise (not wildcards)

---

**End of Training Session 3**

*Next: Domain 4 - Advanced Patterns & Production Deployment*
