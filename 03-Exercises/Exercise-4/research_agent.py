#!/usr/bin/env python3
"""
Exercise 4: Multi-Agent Research System with Coordinator Pattern

Demonstrates:
- Domain 1: Agentic Architecture (coordinator-subagent pattern, task decomposition, iterative loops)
- Domain 2: Tool Design (scoped tool access, error structures)
- Domain 5: Context Management (context passing, provenance tracking, graceful degradation)

Run: python research_agent.py
"""

import json
import os
from datetime import datetime
from typing import Any, Optional
import anthropic

# ============================================================================
# TOOL IMPLEMENTATIONS (Mocked - no real API calls)
# ============================================================================

def mock_web_search(query: str, num_results: int = 5) -> dict:
    """Mock web search tool - returns synthetic search results with provenance."""
    print(f"  [TOOL] web_search('{query}')")

    # Synthetic search results with provenance
    results = [
        {
            "title": "Framework for AI Safety: Interpretability and Alignment",
            "url": "https://example-research.org/ai-safety-frameworks-2025",
            "snippet": "Recent advances in mechanistic interpretability enable safer AI systems...",
            "confidence": 0.95,
            "retrieved_at": datetime.now().isoformat(),
        },
        {
            "title": "Regulatory Approaches to AI Governance",
            "url": "https://example-policy.org/ai-governance-2025",
            "snippet": "The EU AI Act and emerging regulations focus on high-risk systems...",
            "confidence": 0.93,
            "retrieved_at": datetime.now().isoformat(),
        },
        {
            "title": "Industry Adoption of AI Safety Standards",
            "url": "https://example-industry.org/safety-standards",
            "snippet": "Leading tech companies are implementing safety frameworks...",
            "confidence": 0.88,
            "retrieved_at": datetime.now().isoformat(),
        },
    ]

    return {
        "status": "success",
        "data": results[:num_results],
        "count": len(results[:num_results]),
        "query": query,
    }


def mock_fetch_url(url: str) -> dict:
    """Mock fetch URL tool - returns content from a URL."""
    print(f"  [TOOL] fetch_url('{url}')")

    # Synthetic document content
    content_map = {
        "ai-safety-frameworks": {
            "title": "Framework for AI Safety: Interpretability and Alignment",
            "sections": [
                {
                    "heading": "Mechanistic Interpretability",
                    "content": "Understanding neural network features at a detailed level...",
                    "page": 3,
                },
                {
                    "heading": "Alignment Research",
                    "content": "Ensuring AI systems pursue intended goals...",
                    "page": 5,
                },
            ],
        },
        "ai-governance": {
            "title": "Regulatory Approaches to AI Governance",
            "sections": [
                {
                    "heading": "EU AI Act",
                    "content": "Classifies AI systems by risk level with corresponding requirements...",
                    "page": 2,
                },
                {
                    "heading": "Risk-Based Regulation",
                    "content": "High-risk systems require extensive testing and documentation...",
                    "page": 4,
                },
            ],
        },
    }

    # Determine which content to return
    if "safety-frameworks" in url or "ai-safety" in url:
        content = content_map["ai-safety-frameworks"]
    else:
        content = content_map["ai-governance"]

    return {
        "status": "success",
        "data": {
            "url": url,
            "content": content,
            "word_count": 1200,
        },
        "provenance": {
            "source_url": url,
            "retrieved_at": datetime.now().isoformat(),
            "confidence": 0.92,
        },
    }


def mock_extract_data_points(content: str) -> dict:
    """Mock extract data points tool - identifies key insights from content."""
    print(f"  [TOOL] extract_data_points(...)")

    insights = [
        {
            "insight": "Interpretability is critical for understanding AI system behavior",
            "confidence": 0.95,
            "evidence_type": "research_finding",
        },
        {
            "insight": "Alignment ensures AI systems pursue intended human goals",
            "confidence": 0.93,
            "evidence_type": "research_finding",
        },
        {
            "insight": "Risk-based regulation is emerging as the primary governance approach",
            "confidence": 0.88,
            "evidence_type": "industry_trend",
        },
        {
            "insight": "EU AI Act mandates extensive testing for high-risk systems",
            "confidence": 0.97,
            "evidence_type": "regulatory_requirement",
        },
    ]

    return {
        "status": "success",
        "data": {"insights": insights, "total_extracted": len(insights)},
        "extraction_confidence": 0.92,
    }


def mock_summarize_content(content: str) -> dict:
    """Mock summarize content tool - creates concise summaries."""
    print(f"  [TOOL] summarize_content(...)")

    return {
        "status": "success",
        "data": {
            "summary": "This comprehensive document covers AI safety frameworks including "
                      "interpretability approaches, alignment research, and regulatory governance. "
                      "Key focus areas include mechanistic interpretability, risk-based regulation, "
                      "and industry standards adoption.",
            "key_topics": [
                "Interpretability",
                "Alignment",
                "Governance",
                "Risk Assessment",
                "Industry Standards",
            ],
            "estimated_reading_time_minutes": 8,
        },
    }


def mock_compile_report(insights: list, sources: list) -> dict:
    """Mock compile report tool - creates structured research report."""
    print(f"  [TOOL] compile_report(...insights, ...sources)")

    sections = [
        {
            "title": "AI Safety Frameworks Overview",
            "content": "Contemporary AI safety research focuses on interpretability and alignment...",
            "subsections": 2,
        },
        {
            "title": "Regulatory Landscape",
            "content": "Global regulatory approaches to AI include the EU AI Act and emerging standards...",
            "subsections": 3,
        },
        {
            "title": "Industry Adoption",
            "content": "Leading companies are implementing safety frameworks in production systems...",
            "subsections": 2,
        },
    ]

    return {
        "status": "success",
        "data": {
            "report_id": "report_2026_03_22_001",
            "sections": sections,
            "total_sections": len(sections),
            "estimated_pages": 8,
        },
    }


def mock_verify_fact(claim: str, sources: list) -> dict:
    """Mock verify fact tool - checks claims against sources."""
    print(f"  [TOOL] verify_fact('{claim[:50]}...', ...sources)")

    verification_results = {
        "claim": claim,
        "verified": True,
        "confidence": 0.91,
        "supporting_sources": 2,
        "notes": "Claim supported by multiple peer-reviewed sources",
    }

    return {
        "status": "success",
        "data": verification_results,
    }


# ============================================================================
# COORDINATOR AND SUBAGENT IMPLEMENTATION
# ============================================================================

class ResearchCoordinator:
    """
    Coordinator agent that orchestrates specialized subagents.

    Demonstrates:
    - Task decomposition
    - Delegation to isolated subagents
    - Result aggregation
    - Iterative refinement with quality gates
    - Safety limits (max iterations)
    """

    def __init__(self, query: str):
        self.query = query
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-3-5-sonnet-20241022"
        self.iteration = 0
        self.max_iterations = 3
        self.results = {
            "search_phase": None,
            "analysis_phase": None,
            "synthesis_phase": None,
            "refinements": [],
        }
        self.all_sources = []

    def print_section(self, title: str, level: int = 1):
        """Print formatted section headers."""
        if level == 1:
            print(f"\n{'=' * 70}")
            print(f"{title.center(70)}")
            print(f"{'=' * 70}\n")
        else:
            print(f"\n{'-' * 70}")
            print(f"{title}")
            print(f"{'-' * 70}\n")

    def decompose_task(self) -> dict:
        """
        Use Claude to analyze the query and decide which subagents to delegate to.
        Demonstrates: Domain 1 - Task decomposition
        """
        print("[COORDINATOR] Analyzing query and decomposing task...")

        decomposition_prompt = f"""Analyze this research query and provide a task decomposition plan.

Query: {self.query}

Respond in JSON format with:
{{
    "primary_research_areas": ["area1", "area2", ...],
    "subagents_needed": ["search", "analysis", "synthesis"],
    "focus_areas": ["focus1", "focus2", ...],
    "estimated_complexity": "simple|moderate|complex",
    "notes": "..."
}}

Be specific about what each research area should cover."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": decomposition_prompt,
                }
            ],
        )

        response_text = response.content[0].text
        # Extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            plan = json.loads(json_match.group())
        else:
            plan = {
                "primary_research_areas": ["frameworks", "regulations", "industry"],
                "subagents_needed": ["search", "analysis", "synthesis"],
                "focus_areas": ["interpretability", "alignment", "governance"],
                "estimated_complexity": "moderate",
            }

        print(f"Task Analysis:")
        print(f"  Research areas: {', '.join(plan.get('primary_research_areas', []))}")
        print(f"  Subagents: {', '.join(plan.get('subagents_needed', []))}")
        print(f"  Focus: {', '.join(plan.get('focus_areas', []))}")
        print(f"  Complexity: {plan.get('estimated_complexity', 'N/A')}\n")

        return plan

    def delegate_to_search_subagent(self, task_plan: dict) -> dict:
        """
        Delegate to search subagent with isolated context.

        Demonstrates:
        - Domain 1: Delegation to isolated subagent
        - Domain 2: Scoped tool access (only web_search, fetch_url)
        - Domain 5: Context passing (not conversation history)
        """
        print("[COORDINATOR] Delegating to SEARCH subagent...")

        # Create isolated context (NOT the full conversation history)
        isolated_context = {
            "task": f"Find authoritative sources about: {', '.join(task_plan.get('primary_research_areas', []))}",
            "focus_areas": task_plan.get('focus_areas', []),
            "iteration": self.iteration,
            "required_depth": "comprehensive",
        }

        print(f"[SEARCH SUBAGENT] Isolated context: {json.dumps(isolated_context, indent=2)}\n")

        # Subagent system prompt - receives isolated context, not full history
        search_system_prompt = f"""You are a specialized search agent responsible for finding high-quality sources.

Your task: {isolated_context['task']}
Focus areas: {', '.join(isolated_context['focus_areas'])}
Iteration: {isolated_context['iteration']}

Use web_search to find sources, then fetch_url to get content.
Return structured results with URLs and summaries.
Do NOT have access to the full conversation history - only this task context."""

        # Search subagent tools (scoped - only these)
        search_tools = [
            {
                "name": "web_search",
                "description": "Search the web for sources related to the research query",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "num_results": {"type": "integer", "description": "Number of results (default 5)"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "fetch_url",
                "description": "Fetch full content from a URL",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to fetch"},
                    },
                    "required": ["url"],
                },
            },
        ]

        # Simulate search subagent execution
        print("[SEARCH SUBAGENT] Executing tool calls...")
        search_results = mock_web_search(f"AI safety frameworks and regulations")
        fetch_results = mock_fetch_url(search_results["data"][0]["url"])

        # Structured handoff with provenance
        search_output = {
            "status": "success",
            "phase": "search",
            "sources_found": len(search_results["data"]),
            "sources": search_results["data"],
            "content_samples": fetch_results["data"],
            "provenance": fetch_results["provenance"],
            "iteration": self.iteration,
        }

        print(f"[SEARCH SUBAGENT] Found {search_output['sources_found']} sources\n")

        self.all_sources.extend(search_results["data"])
        return search_output

    def delegate_to_analysis_subagent(self, search_results: dict, task_plan: dict) -> dict:
        """
        Delegate to analysis subagent with explicitly passed search results.

        Demonstrates:
        - Domain 1: Isolated subagent with explicit context passing
        - Domain 2: Scoped tools (only extract_data_points, summarize_content)
        - Domain 5: Structured handoff of search results (not raw data)
        """
        print("[COORDINATOR] Delegating to ANALYSIS subagent...")

        # Create isolated context with search results explicitly passed
        isolated_context = {
            "task": "Extract key insights and quotes from search results",
            "search_results": search_results["sources"],  # Explicit handoff
            "focus_areas": task_plan.get('focus_areas', []),
            "iteration": self.iteration,
        }

        print(f"[ANALYSIS SUBAGENT] Isolated context with {len(search_results['sources'])} sources\n")

        # Analysis subagent system prompt
        analysis_system_prompt = f"""You are a specialized analysis agent.

Your task: Extract key insights and quotes from the provided search results.
Focus areas: {', '.join(task_plan.get('focus_areas', []))}
Iteration: {isolated_context['iteration']}

You have access ONLY to: extract_data_points, summarize_content
You do NOT have: web_search, compile_report
You receive ONLY the search results from the coordinator, not full conversation history."""

        # Analysis subagent tools (scoped)
        analysis_tools = [
            {
                "name": "extract_data_points",
                "description": "Extract key insights and data points from content",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Content to analyze"},
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "summarize_content",
                "description": "Create a concise summary of content",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Content to summarize"},
                    },
                    "required": ["content"],
                },
            },
        ]

        # Simulate analysis subagent execution
        print("[ANALYSIS SUBAGENT] Executing tool calls...")
        extraction_results = mock_extract_data_points(json.dumps(search_results["sources"]))
        summary_results = mock_summarize_content(json.dumps(search_results["sources"]))

        # Structured handoff with provenance
        analysis_output = {
            "status": "success",
            "phase": "analysis",
            "insights_extracted": extraction_results["data"]["total_extracted"],
            "insights": extraction_results["data"]["insights"],
            "summary": summary_results["data"]["summary"],
            "key_topics": summary_results["data"]["key_topics"],
            "iteration": self.iteration,
            "source_count": len(search_results["sources"]),
        }

        print(f"[ANALYSIS SUBAGENT] Extracted {analysis_output['insights_extracted']} insights\n")

        return analysis_output

    def delegate_to_synthesis_subagent(self, search_results: dict, analysis_results: dict) -> dict:
        """
        Delegate to synthesis subagent to compile final report.

        Demonstrates:
        - Domain 1: Isolated subagent receiving aggregated results
        - Domain 2: Scoped tools (compile_report, verify_fact)
        - Domain 5: Complete handoff of all previous phases (structured)
        """
        print("[COORDINATOR] Delegating to SYNTHESIS subagent...")

        # Create isolated context with results from previous phases
        isolated_context = {
            "task": "Compile comprehensive research report",
            "search_phase_results": {
                "sources_count": len(search_results["sources"]),
                "summary": "Search phase completed",
            },
            "analysis_phase_results": {
                "insights_count": analysis_results["insights_extracted"],
                "topics": analysis_results["key_topics"],
            },
            "iteration": self.iteration,
        }

        print(f"[SYNTHESIS SUBAGENT] Isolated context with aggregated results\n")

        # Synthesis subagent system prompt
        synthesis_system_prompt = f"""You are a specialized synthesis agent.

Your task: Compile a comprehensive research report from search and analysis results.
Insights available: {analysis_results['insights_extracted']}
Sources available: {len(search_results['sources'])}
Iteration: {isolated_context['iteration']}

You have access ONLY to: compile_report, verify_fact
You do NOT have: web_search, fetch_url, extract_data_points
You receive ONLY aggregated results from coordinator, not raw data or history."""

        # Synthesis subagent tools (scoped)
        synthesis_tools = [
            {
                "name": "compile_report",
                "description": "Compile insights into a structured research report",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "insights": {"type": "array", "description": "Key insights"},
                        "sources": {"type": "array", "description": "Source list"},
                    },
                    "required": ["insights", "sources"],
                },
            },
            {
                "name": "verify_fact",
                "description": "Verify a claim against sources",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "claim": {"type": "string", "description": "Claim to verify"},
                        "sources": {"type": "array", "description": "Sources to check"},
                    },
                    "required": ["claim", "sources"],
                },
            },
        ]

        # Simulate synthesis subagent execution
        print("[SYNTHESIS SUBAGENT] Executing tool calls...")
        compilation_results = mock_compile_report(
            analysis_results["insights"],
            search_results["sources"],
        )

        # Verify key facts
        verification_results = mock_verify_fact(
            "AI safety focuses on interpretability and alignment",
            search_results["sources"],
        )

        # Structured handoff
        synthesis_output = {
            "status": "success",
            "phase": "synthesis",
            "report_id": compilation_results["data"]["report_id"],
            "sections": compilation_results["data"]["sections"],
            "total_sections": compilation_results["data"]["total_sections"],
            "verified_facts": 1,
            "fact_verification": verification_results["data"],
            "iteration": self.iteration,
        }

        print(f"[SYNTHESIS SUBAGENT] Generated report with {synthesis_output['total_sections']} sections\n")

        return synthesis_output

    def evaluate_synthesis_quality(self, synthesis_output: dict) -> dict:
        """
        Evaluate synthesis quality and identify gaps for refinement.

        Demonstrates:
        - Domain 1: Quality gate in iterative loop
        - Domain 5: Error assessment for graceful degradation
        """
        print("[COORDINATOR] Evaluating synthesis quality...")

        evaluation_prompt = f"""Evaluate the quality of this research synthesis:

Sections: {len(synthesis_output['sections'])}
Verified facts: {synthesis_output['verified_facts']}
Iteration: {synthesis_output['iteration']}

Original query: {self.query}

Respond in JSON:
{{
    "quality_score": 0.0,
    "coverage_percentage": 0,
    "gaps_detected": ["gap1", "gap2"],
    "needs_refinement": true/false,
    "recommended_focus": ["area1", "area2"]
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": evaluation_prompt,
                }
            ],
        )

        response_text = response.content[0].text
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            evaluation = json.loads(json_match.group())
        else:
            # Default evaluation
            evaluation = {
                "quality_score": 0.75,
                "coverage_percentage": 75,
                "gaps_detected": ["regulatory_frameworks"],
                "needs_refinement": True,
                "recommended_focus": ["EU regulations", "industry standards"],
            }

        print(f"Quality Score: {evaluation['quality_score']:.2f}/1.00")
        print(f"Coverage: {evaluation['coverage_percentage']}%")
        if evaluation.get("gaps_detected"):
            print(f"Gaps: {', '.join(evaluation['gaps_detected'])}")
        print(f"Refinement needed: {evaluation['needs_refinement']}\n")

        return evaluation

    def run(self) -> dict:
        """
        Main coordination loop implementing multi-agent orchestration.

        Demonstrates:
        - Domain 1: Hub-and-spoke architecture with iterative refinement
        - Domain 1: Safety limits (max_iterations)
        - Domain 2: Error handling and graceful degradation
        - Domain 5: Complete context management workflow
        """
        self.print_section("MULTI-AGENT RESEARCH SYSTEM")
        print(f"USER QUERY: {self.query}\n")

        # Phase 1: Task Decomposition
        task_plan = self.decompose_task()

        # Phase 2-4: Main loop with refinement
        while self.iteration < self.max_iterations:
            self.print_section(f"ITERATION {self.iteration + 1}", level=2)
            self.iteration += 1

            try:
                # Delegate to search
                search_output = self.delegate_to_search_subagent(task_plan)
                self.results["search_phase"] = search_output

                # Delegate to analysis
                analysis_output = self.delegate_to_analysis_subagent(search_output, task_plan)
                self.results["analysis_phase"] = analysis_output

                # Delegate to synthesis
                synthesis_output = self.delegate_to_synthesis_subagent(search_output, analysis_output)
                self.results["synthesis_phase"] = synthesis_output

            except Exception as e:
                # Graceful degradation on subagent failure
                print(f"[ERROR] Subagent failed: {e}")
                self.results["synthesis_phase"] = {
                    "status": "degraded",
                    "error": str(e),
                    "available_results": "search and analysis phases completed",
                }
                break

            # Evaluate quality
            evaluation = self.evaluate_synthesis_quality(synthesis_output)

            # Check if refinement is needed
            if not evaluation.get("needs_refinement", False) or self.iteration >= self.max_iterations:
                print("[COORDINATOR] Synthesis quality acceptable. Finalizing report.\n")
                break

            # Log refinement request
            self.results["refinements"].append({
                "iteration": self.iteration,
                "gaps": evaluation.get("gaps_detected", []),
                "recommended_focus": evaluation.get("recommended_focus", []),
            })

            print(f"[COORDINATOR] Gaps detected. Re-delegating for refinement...\n")

        # Generate final report
        return self.generate_final_report()

    def generate_final_report(self) -> dict:
        """Generate and display the final research report."""
        self.print_section("FINAL RESEARCH REPORT")

        synthesis = self.results.get("synthesis_phase", {})
        analysis = self.results.get("analysis_phase", {})
        search = self.results.get("search_phase", {})

        print(f"RESEARCH REPORT: {self.query}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Iterations: {self.iteration}\n")

        # Display sections
        if "sections" in synthesis:
            for section in synthesis["sections"]:
                print(f"SECTION: {section['title']}")
                print(f"  Content: {section['content']}")
                print(f"  Subsections: {section['subsections']}\n")

        # Display sources
        print("SOURCES:")
        for i, source in enumerate(self.all_sources, 1):
            print(f"  {i}. {source['title']}")
            print(f"     URL: {source['url']}")
            print(f"     Confidence: {source.get('confidence', 'N/A')}\n")

        # Display summary stats
        print("REPORT SUMMARY:")
        print(f"  Search phase: {search.get('sources_found', 0)} sources found")
        print(f"  Analysis phase: {analysis.get('insights_extracted', 0)} insights extracted")
        print(f"  Synthesis: {synthesis.get('total_sections', 0)} sections compiled")
        print(f"  Fact verifications: {synthesis.get('verified_facts', 0)} verified")
        print(f"  Refinement iterations: {len(self.results.get('refinements', []))}")

        overall_status = "✓ Comprehensive" if synthesis.get("status") == "success" else "⚠ Partial"
        print(f"\nOverall Status: {overall_status}\n")

        return self.results


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Example research query
    USER_QUERY = "Research emerging AI safety frameworks and how they're being adopted in industry"

    # Create and run coordinator
    coordinator = ResearchCoordinator(USER_QUERY)
    results = coordinator.run()

    print("\n" + "=" * 70)
    print("EXERCISE COMPLETE")
    print("=" * 70)
    print("\nKey Concepts Demonstrated:")
    print("  ✓ Hub-and-spoke coordinator-subagent architecture")
    print("  ✓ Task decomposition (coordinator analyzes query)")
    print("  ✓ Isolated subagent contexts (no conversation history inheritance)")
    print("  ✓ Scoped tool access (search, analysis, synthesis each have specific tools)")
    print("  ✓ Context passing via structured handoffs")
    print("  ✓ Provenance tracking (source URLs, confidence, timestamps)")
    print("  ✓ Iterative refinement with quality gates")
    print("  ✓ Safety limits (max 3 iterations)")
    print("  ✓ Graceful degradation on failures")
    print("\nExtensions:")
    print("  • Add session.resume() to checkpoint and restart long workflows")
    print("  • Implement parallel subagent execution with threading")
    print("  • Add cost/token tracking per subagent")
    print("  • Implement tool_choice='required' for refinement phases")
    print("=" * 70)
