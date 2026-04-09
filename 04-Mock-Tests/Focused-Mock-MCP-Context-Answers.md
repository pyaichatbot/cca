# Focused Mock - MCP and Reliability: Answer Key

| Q | Answer | Domain | Rationale |
|---|--------|--------|-----------|
| 1 | B | Tool Design & MCP Integration | Specific tool naming and descriptions reduce routing ambiguity. |
| 2 | B | Tool Design & MCP Integration | Invalid credentials are not transient; the input must change first. |
| 3 | A | Tool Design & MCP Integration | Overly broad system heuristics can distort otherwise good tool selection. |
| 4 | A | Context Management & Reliability | Validation failures should trigger targeted retry-with-error-feedback. |
| 5 | A | Tool Design & MCP Integration | Tool visibility by tier belongs in server-side listing/filtering logic. |
| 6 | A | Tool Design & MCP Integration | Specialized tools provide clearer boundaries for the model. |
| 7 | A | Tool Design & MCP Integration | Retryability and error category drive appropriate recovery behavior. |
| 8 | B | Context Management & Reliability | Scratchpad persistence preserves findings across multi-pass flows. |
| 9 | A | Context Management & Reliability | Self-review is weaker because the same model may confirm prior reasoning. |
| 10 | B | Context Management & Reliability | Summaries should preserve state, decisions, constraints, and open issues. |
| 11 | A | Context Management & Reliability | PostToolUse hooks are the right place for normalization and metadata. |
| 12 | B | Context Management & Reliability | Friendly text without explicit failure propagation is silent suppression. |
| 13 | B | Context Management & Reliability | Non-retryable errors should halt or escalate, not loop. |
| 14 | B | Context Management & Reliability | Auditability requires source-linked provenance for each finding. |
| 15 | B | Context Management & Reliability | Good trimming removes redundancy while preserving essentials. |
| 16 | B | Context Management & Reliability | Ambiguity that changes action should trigger clarifying questions. |
| 17 | A | Context Management & Reliability | Stratifying by complexity helps isolate where failures cluster. |
| 18 | B | Context Management & Reliability | Low-confidence cases need additional validation or human review. |
| 19 | A | Tool Design & MCP Integration | Narrower tools often reduce overlap more effectively than parameter sprawl. |
| 20 | B | Context Management & Reliability | Rate-limit failures are usually retryable with backoff if marked so. |
| 21 | A | Context Management & Reliability | Evidence traceability and uncertainty markings support trustworthy outputs. |
| 22 | B | Tool Design & MCP Integration | Uniform generic errors remove the information needed for correct recovery. |
| 23 | A | Context Management & Reliability | Checkpoint summaries plus recent turns manage growth without losing substance. |
| 24 | A | Tool Design & MCP Integration | Domain-aware scoring depends on parsing the Domain column from the key. |

## Domain Mix

- Tool Design & MCP Integration: Q1, Q2, Q3, Q5, Q6, Q7, Q19, Q22, Q24
- Context Management & Reliability: Q4, Q8, Q9, Q10, Q11, Q12, Q13, Q14, Q15, Q16, Q17, Q18, Q20, Q21, Q23