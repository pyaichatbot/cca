#!/bin/bash

# Exercise 2: Team Development Configuration Setup
# This script creates a complete, production-ready Claude Code configuration
# for team development. It demonstrates Domain 3 and Domain 2 concepts.

set -e

PROJECT_DIR="team-dev-project"

echo "Creating team development project structure..."

# Create root directories
mkdir -p "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR/.claude/rules"
mkdir -p "$PROJECT_DIR/.claude/commands"
mkdir -p "$PROJECT_DIR/.claude/skills/code-review"
mkdir -p "$PROJECT_DIR/.claude/skills/api-design"
mkdir -p "$PROJECT_DIR/.claude/skills/testing"
mkdir -p "$PROJECT_DIR/src/api"
mkdir -p "$PROJECT_DIR/src/services"
mkdir -p "$PROJECT_DIR/src/middleware"
mkdir -p "$PROJECT_DIR/src/utils"
mkdir -p "$PROJECT_DIR/tests/unit"
mkdir -p "$PROJECT_DIR/tests/integration"
mkdir -p "$PROJECT_DIR/docs"

# ============================================================================
# ROOT CLAUDE.MD - Global workspace configuration
# ============================================================================
cat > "$PROJECT_DIR/CLAUDE.md" << 'EOF'
# Root Configuration for Team Development Project

## Overview
This is the root CLAUDE.md file. It provides workspace-level standards that apply
to all files unless overridden by more specific CLAUDE.md files in subdirectories.

## Role Hierarchy
Root CLAUDE.md is the lowest priority. More specific configurations override it.

## Imported Standards
We use @import to reference external rule files, keeping this file focused on
high-level guidance rather than detailed standards.

## Core Principles
- **Code Quality**: Write readable, maintainable code
- **Testing**: All features must have tests
- **Documentation**: API endpoints and complex logic must be documented
- **Security**: No secrets in code, use environment variables
- **Performance**: Consider performance implications of changes

## Applicable Standards
Standards are imported from .claude/rules/ using @import directives.

## Directory-Specific Overrides
- /src/api/CLAUDE.md: API-specific standards
- /tests/CLAUDE.md: Testing-specific relaxed standards
- /docs/CLAUDE.md: Documentation-focused standards

## When to Ask for Help
- Architectural decisions affecting multiple services
- Security-related changes
- Database schema changes
- Changes to deployment process

When in doubt, ask for code review from the team.
EOF

# ============================================================================
# PROJECT-LEVEL CLAUDE.MD - .claude/CLAUDE.md configuration
# ============================================================================
cat > "$PROJECT_DIR/.claude/CLAUDE.md" << 'EOF'
# Project-Level Configuration

## About This Directory
The .claude/ directory contains all Claude Code project configuration.
This CLAUDE.md is more specific than root and applies to Claude operations.

## Configuration Structure

### Rules Files (.claude/rules/)
We maintain separate YAML rule files for different domains:
- **backend-standards.yaml**: TypeScript/JavaScript backend coding standards
- **testing-standards.yaml**: Testing requirements and conventions
- **security-standards.yaml**: Security best practices and checks
- **documentation-standards.yaml**: Documentation requirements
- **performance-standards.yaml**: Performance optimization guidelines

Each rule file uses YAML frontmatter with path specifications for conditional loading.

### Slash Commands (.claude/commands/)
Available commands for quick access to common workflows:
- **/review-pr**: Comprehensive pull request review
- **/scan-security**: Security vulnerability scanning
- **/generate-docs**: Automatic documentation generation

Access via `/help` in Claude Code.

### Skills (.claude/skills/)
Reusable task templates with controlled tool access:
- **code-review/SKILL.md**: Structured code review process
- **api-design/SKILL.md**: API design validation and best practices
- **testing/SKILL.md**: Test suite analysis and recommendations

Skills use forked context for isolation and restricted tool access.

### MCP Configuration
See .mcp.json for MCP server configurations (GitHub, Database APIs).

## Environment-Specific Settings
The .mcp.json file uses environment variable expansion:
- ${GITHUB_TOKEN}: GitHub API authentication
- ${GITHUB_OWNER}: Repository owner
- ${DATABASE_URL}: Database connection string

Set these before running Claude Code:
```bash
export GITHUB_TOKEN=your_token_here
export GITHUB_OWNER=yourorg
export DATABASE_URL=postgres://...
```

## Plan Mode Guidance
Use --plan true for:
- Structural refactoring changes
- Multiple file modifications
- Configuration updates affecting team
- Destructive operations (file deletion)

Use direct execution for:
- Single file changes
- Bug fixes with clear scope
- Adding new features following patterns
- Analysis and reading tasks

## Tool Restrictions
When running skills or commands, only approved tools are available.
This prevents accidental side effects and ensures safety.

## Contact & Escalation
- Security issues: Security team (@security-team)
- Architecture questions: Architects (@architecture)
- General questions: Your team lead
EOF

# ============================================================================
# RULE FILE 1: Backend Standards
# ============================================================================
cat > "$PROJECT_DIR/.claude/rules/backend-standards.yaml" << 'EOF'
---
path: "src/**/*.ts,src/**/*.js"
conditions:
  - directory: src/utils
    not: true
---

# Backend Code Standards

## TypeScript Configuration
- Use strict mode in tsconfig.json
- No implicit `any` types
- Prefer explicit return types on functions
- Use `interface` for object contracts, `type` for unions

## Code Style
- Use camelCase for variables and functions
- Use PascalCase for classes and types
- Use UPPER_SNAKE_CASE for constants
- Line length: max 100 characters
- Use 2-space indentation

## API Conventions
- RESTful endpoints follow: /api/v1/resource[/id]
- Use HTTP methods correctly: GET (read), POST (create), PUT (update), DELETE
- Return proper status codes: 200 (success), 201 (created), 400 (bad request), 404 (not found), 500 (error)
- Include error messages with status code

## Error Handling
- Always catch Promise rejections
- Use try/catch for async operations
- Return meaningful error messages
- Log errors with context (request ID, user, timestamp)
- Don't expose internal error details to clients

## Logging
- Use structured logging (JSON format)
- Include request ID for traceability
- Log at INFO level for normal operations
- Log at ERROR level for exceptions
- Include context: userId, operation, duration

## Comments
- Comment the "why", not the "what"
- Keep comments in sync with code changes
- Use JSDoc for public APIs
- Explain non-obvious logic

## Dependencies
- Review all new dependencies for security
- Keep dependencies up to date
- Use npm audit to check for vulnerabilities
- Pin major versions, allow minor/patch updates
EOF

# ============================================================================
# RULE FILE 2: Testing Standards
# ============================================================================
cat > "$PROJECT_DIR/.claude/rules/testing-standards.yaml" << 'EOF'
---
path: "tests/**/*.ts,tests/**/*.js"
---

# Testing Standards

## Test Organization
- Follow AAA pattern: Arrange, Act, Assert
- One assertion per test (or logically related assertions)
- Test names describe the scenario and expected outcome
- Example: "should return 404 when user not found"

## Coverage Requirements
- Minimum 80% code coverage for critical paths
- 100% coverage for security-sensitive code
- Cover happy path, error cases, and edge cases
- Integration tests cover end-to-end flows

## Unit Tests
- Mock external dependencies
- Test behavior, not implementation
- Use descriptive test names
- Setup/teardown in beforeEach/afterEach

## Integration Tests
- Use test database or in-memory database
- Test actual database interactions
- Verify external API calls
- Clean up data after each test

## Mocking Strategy
- Mock external APIs and services
- Don't mock code you control
- Mock at service boundaries
- Keep mocks realistic and updated

## Test Tools
- Jest for unit testing
- Supertest for API testing
- ts-node for TypeScript execution
- jest.setup.ts for global configuration

## Performance Testing
- Benchmark critical paths
- Track performance regressions
- Set performance baselines
- Alert on significant deviations
EOF

# ============================================================================
# RULE FILE 3: Security Standards
# ============================================================================
cat > "$PROJECT_DIR/.claude/rules/security-standards.yaml" << 'EOF'
---
path: "src/**/*.ts,src/**/*.js"
---

# Security Standards

## Secrets Management
- NEVER hardcode secrets, API keys, or credentials
- Use environment variables for all secrets
- Use .env.example to document required variables
- Use GITHUB_TOKEN, DATABASE_PASSWORD, API_KEY pattern

## Input Validation
- Validate all user inputs
- Use schema validation libraries (joi, zod)
- Sanitize inputs before database queries
- Validate API request bodies

## SQL Injection Prevention
- Use parameterized queries (prepared statements)
- Never concatenate user input into SQL
- Use ORM when possible
- Validate and escape data

## Authentication
- Require HTTPS in production
- Use secure session management
- Implement rate limiting on auth endpoints
- Never log passwords or tokens

## Authorization
- Verify user has permission before operation
- Implement role-based access control
- Check ownership (user can only access their data)
- Audit authorization failures

## Dependency Security
- Run npm audit regularly
- Address critical and high vulnerabilities
- Update dependencies monthly
- Review changelogs for security fixes

## Error Messages
- Don't expose system details in errors
- Avoid disclosing valid vs invalid usernames
- Log full errors server-side
- Return generic errors to client

## CORS & Headers
- Configure CORS for known domains only
- Add security headers (X-Frame-Options, CSP, etc.)
- Validate content-type headers
- Implement CSRF tokens for state-changing operations
EOF

# ============================================================================
# RULE FILE 4: Documentation Standards
# ============================================================================
cat > "$PROJECT_DIR/.claude/rules/documentation-standards.yaml" << 'EOF'
---
path: "src/**/*.ts,src/**/*.js,docs/**/*.md"
---

# Documentation Standards

## Code Documentation
- Document all public APIs with JSDoc comments
- Include @param, @returns, @throws tags
- Provide usage examples in comments
- Document edge cases and limitations

## API Documentation
- Document all endpoints with method, path, parameters
- Include request and response examples
- Document error responses and status codes
- Explain authentication requirements
- Document rate limits

## README Files
- Start with project overview
- Include setup instructions
- Explain architecture and key components
- Document deployment process
- Include troubleshooting section

## Changelog
- Document all user-facing changes
- Use semantic versioning
- Group changes by type (features, fixes, breaking changes)
- Include migration instructions for breaking changes

## Architecture Docs
- Explain key design decisions
- Diagram system components and interactions
- Explain trade-offs and why decisions were made
- Document interfaces between major components

## Configuration
- Document all environment variables
- Explain what each variable controls
- Provide default values and acceptable ranges
- Include examples for common scenarios
EOF

# ============================================================================
# RULE FILE 5: Performance Standards
# ============================================================================
cat > "$PROJECT_DIR/.claude/rules/performance-standards.yaml" << 'EOF'
---
path: "src/**/*.ts,src/**/*.js"
---

# Performance Standards

## Database Performance
- Add indexes on frequently queried columns
- Use database query analysis tools
- Avoid N+1 query problems
- Use connection pooling
- Monitor slow query logs

## Caching Strategy
- Cache frequently accessed data
- Set appropriate TTLs based on data freshness
- Invalidate cache when data changes
- Monitor cache hit rates
- Document what is cached and why

## API Response Times
- Target response time < 200ms (p95)
- Target response time < 1s (p99)
- Monitor response times in production
- Identify and optimize slow endpoints

## Memory Management
- Monitor memory usage
- Identify and fix memory leaks
- Use streaming for large datasets
- Clean up resources in finally blocks

## Load Testing
- Load test before production deployment
- Test with expected peak load
- Identify bottlenecks and optimize
- Monitor resource utilization
- Have scaling strategy

## Monitoring & Alerts
- Monitor CPU, memory, disk usage
- Set alerts for threshold violations
- Track request latency percentiles
- Monitor error rates
- Alert on anomalies
EOF

# ============================================================================
# SLASH COMMAND 1: Review PR
# ============================================================================
cat > "$PROJECT_DIR/.claude/commands/review-pr.md" << 'EOF'
---
name: "review-pr"
description: "Conduct a comprehensive pull request review covering code quality, design patterns, testing, security, and performance"
argument-hint: "GitHub PR URL, PR number, or branch name"
---

# Pull Request Review Command

## Overview
This command performs a comprehensive code review of a pull request using Claude.

## Execution Steps

1. **Fetch PR Information**
   - Get PR title, description, and branch names
   - List all changed files

2. **Code Quality Review**
   - Check code style consistency
   - Verify following backend-standards.yaml
   - Look for code smells and anti-patterns
   - Check naming conventions and clarity

3. **Design Review**
   - Evaluate API design and consistency
   - Check for proper separation of concerns
   - Verify no circular dependencies
   - Assess code reusability

4. **Testing Review**
   - Verify test coverage for changes
   - Check test quality and completeness
   - Verify tests follow testing-standards.yaml
   - Ensure edge cases are covered

5. **Security Review**
   - Check for security-standards.yaml violations
   - Verify no secrets are hardcoded
   - Check input validation
   - Verify authentication/authorization correct

6. **Performance Review**
   - Check for potential performance issues
   - Review database queries
   - Identify caching opportunities
   - Check for memory/resource leaks

7. **Documentation Review**
   - Verify updated documentation
   - Check API docs are current
   - Verify comments explain the why

## Output Format
- Summary of findings
- Issues by severity (critical, major, minor)
- Suggestions for improvement
- Approval decision with reasoning

## Usage Examples

```
/review-pr https://github.com/org/repo/pull/42
/review-pr 42
/review-pr feature/new-api
```

## Related Skills
- code-review: For detailed code review in isolation
- testing: For focused testing analysis
EOF

# ============================================================================
# SLASH COMMAND 2: Security Scan
# ============================================================================
cat > "$PROJECT_DIR/.claude/commands/scan-security.md" << 'EOF'
---
name: "scan-security"
description: "Scan codebase for security vulnerabilities including secrets, injection vulnerabilities, and insecure patterns"
argument-hint: "Directory path (optional, defaults to src/)"
---

# Security Scan Command

## Overview
Performs a security-focused code scan to identify vulnerabilities and insecure patterns.

## Execution Steps

1. **Secrets Detection**
   - Search for hardcoded credentials
   - Find exposed API keys or tokens
   - Check for database passwords in code
   - Identify private key files

2. **Input Validation**
   - Check all user input is validated
   - Look for missing sanitization
   - Verify schema validation

3. **SQL Injection Prevention**
   - Verify use of parameterized queries
   - Check for string concatenation in queries
   - Identify potential injection points

4. **Authentication/Authorization**
   - Verify authentication is enforced
   - Check authorization checks exist
   - Review permission logic

5. **Dependency Check**
   - List all dependencies
   - Report any with known vulnerabilities
   - Suggest updates for security fixes

6. **Configuration**
   - Verify no secrets in .env.example
   - Check CORS is properly configured
   - Verify security headers are set

## Output Format
- Vulnerabilities found (with severity)
- Recommendations for fixes
- References to security standards
- Priority fixes for immediate attention

## Usage Examples

```
/scan-security
/scan-security src/
/scan-security src/api/
```
EOF

# ============================================================================
# SLASH COMMAND 3: Generate Docs
# ============================================================================
cat > "$PROJECT_DIR/.claude/commands/generate-docs.md" << 'EOF'
---
name: "generate-docs"
description: "Generate or update API documentation from code comments and type definitions"
argument-hint: "Directory or file path (optional)"
---

# Generate Documentation Command

## Overview
Automatically generates documentation from JSDoc comments and TypeScript types.

## Execution Steps

1. **Analyze Type Definitions**
   - Extract interfaces and types
   - Document parameters and return types
   - Identify complex types needing explanation

2. **Extract API Endpoints**
   - Find all route definitions
   - Extract HTTP method, path, parameters
   - Identify request/response schemas

3. **Generate API Docs**
   - Create endpoint documentation
   - Include request examples
   - Document response format
   - Explain status codes

4. **Generate Type Docs**
   - Document interfaces
   - Document type unions
   - Explain validation rules

5. **Update Examples**
   - Create usage examples
   - Include curl commands
   - Add code samples

## Output
- Updated API documentation
- Type reference documentation
- Example usage guide

## Usage Examples

```
/generate-docs
/generate-docs src/api/
```
EOF

# ============================================================================
# SKILL 1: Code Review
# ============================================================================
cat > "$PROJECT_DIR/.claude/skills/code-review/SKILL.md" << 'EOF'
---
name: "Code Review"
description: "Conduct a detailed code review in an isolated context with controlled tool access"
context: "fork"
allowed-tools:
  - read_file
  - grep
  - bash
argument-hint: "File path or directory to review"
requires-confirmation: false
---

# Code Review Skill

## Purpose
This skill performs detailed code review of specified files or directories.
It runs in a forked context (isolated) to prevent modification of files.

## Tool Access
This skill has access to:
- **read_file**: Read source files
- **grep**: Search for patterns
- **bash**: Execute analysis commands

This skill CANNOT:
- Modify files
- Execute arbitrary commands
- Access tools outside the allowed list

## Review Process

1. **Read the target files**
2. **Check against backend-standards.yaml**
3. **Verify testing-standards.yaml compliance**
4. **Check security-standards.yaml**
5. **Review documentation**
6. **Assess performance implications**

## Output
- List of issues by severity
- Code quality score
- Suggestions for improvement
- References to applicable standards

## Why `context: fork`?
Running in a forked context ensures:
- Review cannot modify code
- Side effects are isolated
- Safe for automated review workflows
- Prevents accidental changes

## Usage
```
/code-review-skill src/api/users.ts
```

Or use the slash command:
```
/review-pr 42
```
EOF

# ============================================================================
# SKILL 2: API Design
# ============================================================================
cat > "$PROJECT_DIR/.claude/skills/api-design/SKILL.md" << 'EOF'
---
name: "API Design"
description: "Validate API design against REST principles and team standards"
context: "inherit"
allowed-tools:
  - read_file
  - grep
  - write_file
argument-hint: "API route file path"
requires-confirmation: true
---

# API Design Skill

## Purpose
Validates API design decisions and suggests improvements based on REST principles
and team conventions.

## Tool Access
- **read_file**: Read API definitions
- **grep**: Find related endpoints
- **write_file**: Create design documentation

Note: Requires confirmation before making changes.

## Validation Checks

1. **REST Compliance**
   - Correct HTTP methods for operations
   - Proper resource naming (plural nouns)
   - Correct status codes

2. **Consistency**
   - Follows /api/v1/resource pattern
   - Parameter naming consistent
   - Response format consistent

3. **Documentation**
   - All endpoints documented
   - Parameters explained
   - Response schema provided

4. **Error Handling**
   - Error responses documented
   - Status codes for all error cases
   - Error message format consistent

## Output
- Design assessment
- Issues found
- Suggestions for improvement
- Updated documentation (if approved)

## Why `context: inherit`?
Uses inherited context to:
- Reference existing API patterns
- Maintain consistency with current codebase
- Build on previous analysis

## Usage
```
/api-design-skill src/api/users.ts
```
EOF

# ============================================================================
# SKILL 3: Testing
# ============================================================================
cat > "$PROJECT_DIR/.claude/skills/testing/SKILL.md" << 'EOF'
---
name: "Testing"
description: "Analyze test coverage and recommend additional tests based on code analysis"
context: "fork"
allowed-tools:
  - read_file
  - grep
  - bash
argument-hint: "Source file to generate tests for"
requires-confirmation: false
---

# Testing Skill

## Purpose
Analyzes source code and identifies test gaps, recommends test cases and improvements.

## Tool Access
- **read_file**: Read source and test files
- **grep**: Find existing tests
- **bash**: Run test commands

Cannot modify test files (readonly mode).

## Analysis Steps

1. **Code Analysis**
   - Identify functions and methods
   - Find edge cases and error conditions
   - Identify dependencies and mocks needed

2. **Current Test Coverage**
   - Find existing tests
   - Identify coverage gaps
   - Assess test quality

3. **Recommendations**
   - Suggest additional test cases
   - Identify untested code paths
   - Recommend mock strategy

4. **Coverage Analysis**
   - Calculate coverage percentage
   - Identify low-coverage areas
   - Suggest priority for new tests

## Output
- Coverage analysis
- List of missing test cases
- Test case templates
- Estimated effort to reach target coverage

## Why `context: fork`?
Isolated context allows:
- Detailed code analysis
- Safe testing recommendations
- No unintended side effects
- Focus on analysis without changes

## Usage
```
/testing-skill src/api/users.ts
```
EOF

# ============================================================================
# MCP CONFIGURATION - .mcp.json
# ============================================================================
cat > "$PROJECT_DIR/.claude/.mcp.json" << 'EOF'
{
  "version": "1.0",
  "description": "MCP server configuration for team development project",
  "mcp_servers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "GITHUB_OWNER": "${GITHUB_OWNER}",
        "GITHUB_REPO": "${GITHUB_REPO}"
      },
      "description": "GitHub API integration for PR reviews, issue management, and repository operations"
    },
    "database": {
      "type": "stdio",
      "command": "node",
      "args": [
        "mcp-servers/database-server.js"
      ],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}",
        "DATABASE_USER": "${DATABASE_USER}",
        "DATABASE_PASSWORD": "${DATABASE_PASSWORD}",
        "DATABASE_HOST": "${DATABASE_HOST}",
        "DATABASE_PORT": "${DATABASE_PORT:5432}"
      },
      "description": "Database query and schema inspection tool for development database operations"
    }
  },
  "toolDescriptions": {
    "listRepositories": {
      "description": "List all repositories accessible with the provided GitHub token",
      "inputs": {
        "owner": {
          "type": "string",
          "description": "GitHub organization or user name"
        }
      },
      "outputs": {
        "type": "array",
        "description": "List of repository objects with name, description, URL, and visibility"
      },
      "example": "List all repositories owned by the organization to find the target repo"
    },
    "getPullRequest": {
      "description": "Fetch detailed information about a specific pull request",
      "inputs": {
        "pr_number": {
          "type": "number",
          "description": "The pull request number to retrieve"
        }
      },
      "outputs": {
        "type": "object",
        "description": "PR object with title, description, changed files, commits, and reviews"
      },
      "example": "Get PR #42 to review code changes and comments"
    },
    "queryDatabase": {
      "description": "Execute a SELECT query against the development database",
      "inputs": {
        "query": {
          "type": "string",
          "description": "SQL SELECT query to execute (parameterized queries only)",
          "constraints": "Must use parameterized queries. Raw user input will be rejected."
        },
        "parameters": {
          "type": "array",
          "description": "Parameters for parameterized query placeholders",
          "example": ["value1", "value2"]
        }
      },
      "outputs": {
        "type": "array",
        "description": "Array of result rows matching the query"
      },
      "errorCases": {
        "SQL_INJECTION_DETECTED": "Raw SQL or unparameterized queries will be rejected",
        "CONNECTION_ERROR": "Database connection failed. Check DATABASE_URL and credentials",
        "QUERY_TIMEOUT": "Query took too long. Optimize the query or check database performance"
      },
      "example": "Query users table: queryDatabase('SELECT * FROM users WHERE id = $1', [42])"
    },
    "getSchema": {
      "description": "Fetch the schema (tables, columns, types) for the development database",
      "inputs": {},
      "outputs": {
        "type": "object",
        "description": "Complete database schema with tables, columns, types, and constraints"
      },
      "example": "Get the full schema to understand data structure before writing queries"
    }
  },
  "environmentVariables": {
    "GITHUB_TOKEN": {
      "required": true,
      "description": "GitHub personal access token for API authentication",
      "example": "ghp_abcd1234..."
    },
    "GITHUB_OWNER": {
      "required": true,
      "description": "GitHub organization or user name that owns the repository",
      "example": "myorganization"
    },
    "GITHUB_REPO": {
      "required": true,
      "description": "Repository name (without owner)",
      "example": "team-dev-project"
    },
    "DATABASE_URL": {
      "required": true,
      "description": "Full database connection string",
      "example": "postgresql://user:password@localhost:5432/dev_db"
    },
    "DATABASE_USER": {
      "required": false,
      "description": "Database user if not included in DATABASE_URL",
      "example": "postgres"
    },
    "DATABASE_PASSWORD": {
      "required": false,
      "description": "Database password if not included in DATABASE_URL",
      "example": "secure_password_here"
    },
    "DATABASE_HOST": {
      "required": false,
      "description": "Database host if not included in DATABASE_URL",
      "example": "localhost"
    },
    "DATABASE_PORT": {
      "required": false,
      "description": "Database port (default: 5432)",
      "example": "5432"
    }
  },
  "setupInstructions": [
    "Set required environment variables before running Claude Code:",
    "export GITHUB_TOKEN=your_github_token",
    "export GITHUB_OWNER=your_org_name",
    "export GITHUB_REPO=your_repo_name",
    "export DATABASE_URL=postgresql://user:pass@host:port/db",
    "",
    "Verify setup with:",
    "echo $GITHUB_TOKEN  # Should not be empty",
    "echo $DATABASE_URL  # Should show connection string"
  ]
}
EOF

# ============================================================================
# SUBDIRECTORY: API-Specific CLAUDE.md
# ============================================================================
cat > "$PROJECT_DIR/src/api/CLAUDE.md" << 'EOF'
# API-Specific Configuration

## Scope
This configuration applies to files in src/api/ and takes precedence over parent CLAUDE.md files.

## API Standards
All APIs must follow REST conventions:
- Use proper HTTP methods: GET, POST, PUT, DELETE
- Resource names are plural nouns: /users, /posts, /comments
- Use hierarchical paths for relationships: /users/:id/posts
- Version the API: /api/v1/...

## Endpoint Requirements
Every endpoint must:
1. Have clear documentation with JSDoc
2. Validate all inputs
3. Return appropriate HTTP status codes
4. Include error handling

## Authentication
All endpoints must:
- Verify user authentication (except public endpoints)
- Check user authorization
- Include auth error handling

## Testing
All API endpoints must have:
- Unit tests for business logic
- Integration tests for HTTP handling
- Error case testing
- Load testing for performance critical endpoints

## Example
See /docs/api-reference.md for endpoint patterns.
EOF

# ============================================================================
# SUBDIRECTORY: Testing CLAUDE.md
# ============================================================================
cat > "$PROJECT_DIR/tests/CLAUDE.md" << 'EOF'
# Testing Configuration

## Scope
This configuration applies to test files and takes precedence over parent settings.

## Test Standards (Different from src/ due to nature of tests)
- Tests don't need to follow all documentation standards
- Focus on behavior coverage, not implementation details
- Use descriptive test names that explain scenarios
- Keep tests focused (one concept per test)

## Mock Strategy
- Mock external APIs
- Use test database (in-memory when possible)
- Keep mocks simple and realistic

## Coverage Goals
- Target 80% overall coverage
- 100% coverage for critical paths (auth, payments)
- Include happy path, error cases, edge cases

## Test Organization
```
tests/
├── unit/           # Unit tests for individual functions
├── integration/    # Integration tests for features
├── fixtures/       # Test data and mocks
└── setup.ts        # Global test configuration
```
EOF

# ============================================================================
# SUBDIRECTORY: Documentation CLAUDE.md
# ============================================================================
cat > "$PROJECT_DIR/docs/CLAUDE.md" << 'EOF'
# Documentation Configuration

## Scope
This configuration applies to documentation files.

## Documentation Standards
- All public APIs must be documented
- Include usage examples
- Document error cases
- Keep docs in sync with code
- Use consistent formatting

## Required Docs
- API reference (all endpoints)
- Architecture overview
- Setup instructions
- Deployment guide
- Troubleshooting guide

## Documentation Quality
- Clear, concise writing
- Active voice
- Real examples from codebase
- Update when code changes
EOF

# ============================================================================
# PROJECT README
# ============================================================================
cat > "$PROJECT_DIR/README.md" << 'EOF'
# Team Development Project

Example project demonstrating Claude Code configuration best practices for team development.

## Quick Start

1. **Clone and setup**
   ```bash
   git clone <repo>
   cd team-dev-project
   npm install
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   export GITHUB_TOKEN=your_token
   export GITHUB_OWNER=your_org
   export DATABASE_URL=postgres://...
   ```

3. **Run Claude Code**
   ```bash
   claude code "Review my code"
   /help              # See available commands
   ```

## Project Structure

- **src/**: Backend application code
  - **api/**: API endpoints following REST conventions
  - **services/**: Business logic and services
  - **middleware/**: Express middleware
  - **utils/**: Utility functions

- **.claude/**: Claude Code configuration
  - **rules/**: Coding standards (YAML files)
  - **commands/**: Custom slash commands
  - **skills/**: Reusable task templates
  - **.mcp.json**: MCP server configuration

- **tests/**: Test suite
  - **unit/**: Unit tests
  - **integration/**: Integration tests

- **docs/**: Documentation
  - **api-reference.md**: API endpoint documentation

## Available Commands

Use `/help` in Claude Code to see all available commands:

- **/review-pr**: Comprehensive PR review
- **/scan-security**: Security vulnerability scan
- **/generate-docs**: Generate API documentation

## Available Skills

Skills provide reusable task templates:

- **code-review**: Detailed code review in isolated context
- **api-design**: API design validation
- **testing**: Test coverage analysis

## Configuration

All configuration is in the `.claude/` directory:

- **CLAUDE.md**: Project-level configuration
- **rules/**: Coding standards files
- **commands/**: Slash command definitions
- **skills/**: Reusable task templates
- **.mcp.json**: MCP server and tool configuration

## Environment Variables

Create a `.env` file with:
```
GITHUB_TOKEN=your_github_token
GITHUB_OWNER=your_organization
GITHUB_REPO=your_repository
DATABASE_URL=postgresql://user:pass@localhost:5432/dev
```

## Development Workflow

1. **Create a branch** for your feature
2. **Make changes** following the standards in `.claude/CLAUDE.md`
3. **Run tests** to ensure coverage
4. **Create a PR** and use `/review-pr` command
5. **Address feedback** from code review
6. **Merge** after approval

## Testing

```bash
npm test                      # Run all tests
npm run test:unit             # Run unit tests
npm run test:integration      # Run integration tests
npm run test:coverage         # Generate coverage report
```

## Documentation

API documentation is in `/docs/api-reference.md`.

To generate updated docs:
```
/generate-docs
```

## Learning Resources

See the [Exercise 2 README](../Exercise-2/README.md) for detailed explanations of:
- CLAUDE.md hierarchy
- Rule file configuration
- Slash commands and skills
- MCP server setup
- Exam preparation questions
EOF

# ============================================================================
# ENVIRONMENT EXAMPLE FILE
# ============================================================================
cat > "$PROJECT_DIR/.env.example" << 'EOF'
# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_OWNER=your_organization_name
GITHUB_REPO=team-dev-project

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dev_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Application Configuration
NODE_ENV=development
API_PORT=3000
API_URL=http://localhost:3000

# Logging
LOG_LEVEL=info
EOF

# ============================================================================
# PACKAGE.JSON
# ============================================================================
cat > "$PROJECT_DIR/package.json" << 'EOF'
{
  "name": "team-dev-project",
  "version": "1.0.0",
  "description": "Team development project with Claude Code configuration",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts",
    "test": "jest",
    "test:unit": "jest --testPathPattern=unit",
    "test:integration": "jest --testPathPattern=integration",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/**/*.ts",
    "format": "prettier --write src/**/*.ts"
  },
  "devDependencies": {
    "@types/jest": "^29.0.0",
    "@types/node": "^20.0.0",
    "jest": "^29.0.0",
    "prettier": "^3.0.0",
    "ts-jest": "^29.0.0",
    "ts-node": "^10.0.0",
    "typescript": "^5.0.0"
  },
  "dependencies": {
    "dotenv": "^16.0.0",
    "joi": "^17.0.0"
  }
}
EOF

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo "=========================================="
echo "Project Created Successfully!"
echo "=========================================="
echo ""
echo "Location: $(pwd)/$PROJECT_DIR"
echo ""
echo "Directory Structure Created:"
echo "  .claude/"
echo "    ├── CLAUDE.md (project configuration)"
echo "    ├── .mcp.json (MCP server config)"
echo "    ├── rules/ (5 YAML rule files)"
echo "    ├── commands/ (3 slash commands)"
echo "    └── skills/ (3 reusable skills)"
echo ""
echo "  src/ (source code)"
echo "  tests/ (test suite)"
echo "  docs/ (documentation)"
echo ""
echo "Files Created:"
echo "  ✓ CLAUDE.md (root configuration)"
echo "  ✓ .claude/CLAUDE.md (project configuration)"
echo "  ✓ src/api/CLAUDE.md (API-specific config)"
echo "  ✓ tests/CLAUDE.md (testing config)"
echo "  ✓ docs/CLAUDE.md (documentation config)"
echo "  ✓ .claude/rules/backend-standards.yaml"
echo "  ✓ .claude/rules/testing-standards.yaml"
echo "  ✓ .claude/rules/security-standards.yaml"
echo "  ✓ .claude/rules/documentation-standards.yaml"
echo "  ✓ .claude/rules/performance-standards.yaml"
echo "  ✓ .claude/commands/review-pr.md"
echo "  ✓ .claude/commands/scan-security.md"
echo "  ✓ .claude/commands/generate-docs.md"
echo "  ✓ .claude/skills/code-review/SKILL.md"
echo "  ✓ .claude/skills/api-design/SKILL.md"
echo "  ✓ .claude/skills/testing/SKILL.md"
echo "  ✓ .claude/.mcp.json (MCP configuration)"
echo "  ✓ README.md (project documentation)"
echo "  ✓ package.json (dependencies)"
echo "  ✓ .env.example (environment template)"
echo ""
echo "Next Steps:"
echo "  1. cd $PROJECT_DIR"
echo "  2. cp .env.example .env"
echo "  3. Update .env with your actual values"
echo "  4. npm install"
echo "  5. Explore the configuration:"
echo "     - Read .claude/CLAUDE.md"
echo "     - Review rules in .claude/rules/"
echo "     - Check commands in .claude/commands/"
echo "     - Examine skills in .claude/skills/"
echo "     - Study .mcp.json structure"
echo ""
echo "For detailed explanation, see README.md in the exercise directory."
echo ""
EOF

chmod +x "$PROJECT_DIR/team-config-setup.sh" 2>/dev/null || true

echo "Setup script completed successfully!"
echo "Project directory: $(pwd)/$PROJECT_DIR"
