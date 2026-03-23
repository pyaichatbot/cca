# Claude Certified Architect – Foundations
## Complete Exam Preparation Repository

**Exam:** 77 MCQ | Scaled 100–1,000 | Pass: 720 (~69%) | 4 of 6 scenarios per sitting

---

## Repository Structure

```
CCA/
├── 01-Study-Guides/          Domain-by-domain deep dives
├── 02-Training-Sessions/      Instructor-led training (5 sessions)
├── 03-Exercises/              Hands-on coding exercises
├── 04-Mock-Tests/             2 full-length practice exams
├── 05-Review-Reports/         Content quality & gap analysis
├── 06-Blog/                   Blog post on exam preparation
├── 07-Exam-Resources/         Official exam guide & practice exam
└── README.md                  This file
```

---

## 01-Study-Guides

Comprehensive study material covering every task statement from the official exam guide. Each guide includes conceptual explanations, code examples, exam traps, and quick-reference cheatsheets.

| File | Domain | Weight |
|------|--------|--------|
| Domain-1-Agentic-Architecture-Orchestration.md | Agentic Architecture & Orchestration | 27% |
| Domain-2-Tool-Design-MCP-Integration.md | Tool Design & MCP Integration | 18% |
| Domain-3-Claude-Code-Configuration-Workflows.md | Claude Code Configuration & Workflows | 20% |
| Domain-4-Prompt-Engineering-Structured-Output.md | Prompt Engineering & Structured Output | 20% |
| Domain-5-Context-Management-Reliability.md | Context Management & Reliability | 15% |
| Claude_Certified_Architect_Study_Guide.docx | Original consolidated study guide | — |

---

## 02-Training-Sessions

Five standalone training sessions designed for instructor-led or self-paced delivery. Each includes learning objectives, timed sections, code walkthroughs, practice questions, hands-on labs, and self-assessment quizzes.

| File | Topic | Duration |
|------|-------|----------|
| Training-Session-1-Agentic-Architecture.md | Agentic loops, multi-agent coordination, hooks, session management | 2.5 hrs |
| Training-Session-2-Tool-Design-MCP.md | Tool descriptions, structured errors, tool_choice, MCP config | 2 hrs |
| Training-Session-3-Claude-Code-Config.md | CLAUDE.md hierarchy, commands/skills, rules, plan mode, CI/CD | 2 hrs |
| Training-Session-4-Prompt-Engineering.md | Explicit criteria, few-shot, JSON schemas, batch API, multi-pass | 2 hrs |
| Training-Session-5-Context-Management.md | Context preservation, escalation, error propagation, provenance | 1.5 hrs |

---

## 03-Exercises

Hands-on coding exercises that reinforce key concepts through building real systems.

| Folder | Exercise | Key Files |
|--------|----------|-----------|
| Exercise-1/ | Customer Support Agent (Agentic Architecture) | agent.py, setup.sh |
| Exercise-2/ | Team Config Setup (Claude Code Configuration) | team-config-setup.sh |
| Exercise-3/ | Structured Data Extraction Pipeline (Prompt Engineering) | extraction_pipeline.py |
| Exercise-4/ | Multi-Agent Research System (Context Management) | research_agent.py |

---

## 04-Mock-Tests

Two full-length practice exams simulating the real test format — 77 questions each, scenario-based, covering all 5 domains proportionally.

| File | Description |
|------|-------------|
| Mock-Test-1-Questions.md | Practice Exam 1 — Questions |
| Mock-Test-1-Answers.md | Practice Exam 1 — Detailed Answer Key |
| Mock-Test-2-Questions.md | Practice Exam 2 — Questions |
| Mock-Test-2-Answers.md | Practice Exam 2 — Detailed Answer Key |

---

## 05-Review-Reports

Quality assurance reports validating study content against the official exam guide.

| File | Description |
|------|-------------|
| Content-Review-Report.md | Full content audit — coverage vs exam guide |
| Critical-Gaps-Quick-Fix.md | Targeted fixes for identified gaps |
| Review-Executive-Summary.md | High-level review findings |
| REVIEW-INDEX.md | Master index of all review activities |

---

## 06-Blog

Blog post written in Praveen's personal writing style, presenting a practical guide to CCA exam preparation and certification strategy.

| File | Description |
|------|-------------|
| Blog-CCA-Exam-Preparation.md | How to Prepare for and Crack the CCA Certification |

---

## 07-Exam-Resources

Official exam materials and interactive practice tools.

| File | Description |
|------|-------------|
| CCA-Exam-Guide.pdf | Official Anthropic Exam Guide (all 30 task statements) |
| Claude Certification Exam.md | Full practice exam with domain-task index |
| cert-exam.skill | Interactive exam runner skill |
| Skilljar-Course-Map-and-Supplementary-Guide.md | Anthropic Academy course map + gap analysis + supplementary content |
| README.md | Exam folder documentation |

---

## Suggested Study Path

1. **Read** the Exam Guide in `07-Exam-Resources/` to understand scope
2. **Complete** Anthropic Skilljar courses in order (see `07-Exam-Resources/Skilljar-Course-Map-and-Supplementary-Guide.md`)
3. **Study** domains in weight order: D1 (27%) → D4 (20%) → D3 (20%) → D2 (18%) → D5 (15%)
4. **Complete** the training sessions in `02-Training-Sessions/` for structured learning
5. **Build** the exercises in `03-Exercises/` for hands-on practice
6. **Test** yourself with mock exams in `04-Mock-Tests/`
7. **Review** gaps using reports in `05-Review-Reports/`
8. **Review** supplementary Skilljar content for advanced topics
9. **Pass** the exam

---

*Built by Praveen Yellamaraju — March 2026*
