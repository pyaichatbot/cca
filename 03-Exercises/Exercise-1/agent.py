"""
Exercise 1: Multi-Tool Customer Support Agent with Escalation Logic
Reinforces: Domain 1 (Agentic Architecture), Domain 2 (Tool Design), Domain 5 (Context Management)

Key Patterns:
- Tool orchestration with prerequisite gating
- Structured error handling with errorCategory and isRetryable
- Multi-concern request handling in a single agentic loop
- PostToolUse normalization hook
"""

import json
import anthropic
from typing import Any

# Initialize the Anthropic client
client = anthropic.Anthropic()

# ============================================================================
# TOOL DEFINITIONS (Domain 2: Tool Design & MCP Integration)
# ============================================================================

TOOLS = [
    {
        "name": "get_customer",
        "description": "Retrieve customer profile and basic information. Must be called before any customer-specific operations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The unique customer ID (e.g., 'CUST-12345')"
                }
            },
            "required": ["customer_id"]
        }
    },
    {
        "name": "lookup_order",
        "description": "Look up order details and status. Prerequisite: get_customer must be called first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer ID"
                },
                "order_id": {
                    "type": "string",
                    "description": "The order ID to look up"
                }
            },
            "required": ["customer_id", "order_id"]
        }
    },
    {
        "name": "process_refund",
        "description": "Process a refund for a customer. Prerequisite: get_customer AND lookup_order must be called first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer ID"
                },
                "order_id": {
                    "type": "string",
                    "description": "The order ID to refund"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for refund (e.g., 'defective', 'wrong_item', 'customer_request')"
                }
            },
            "required": ["customer_id", "order_id", "reason"]
        }
    },
    {
        "name": "escalate_to_human",
        "description": "Escalate the issue to a human support representative. Use when the issue is complex or requires human judgment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer ID"
                },
                "issue_summary": {
                    "type": "string",
                    "description": "A summary of the issue"
                },
                "urgency": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Urgency level"
                }
            },
            "required": ["customer_id", "issue_summary", "urgency"]
        }
    }
]

# ============================================================================
# MOCK TOOL IMPLEMENTATIONS
# ============================================================================

def get_customer(customer_id: str) -> dict:
    """Mock customer database lookup."""
    customers = {
        "CUST-001": {
            "id": "CUST-001",
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "account_status": "active",
            "lifetime_value": 2500.00,
            "registration_date": "2023-01-15"
        },
        "CUST-002": {
            "id": "CUST-002",
            "name": "Bob Smith",
            "email": "bob@example.com",
            "account_status": "active",
            "lifetime_value": 500.00,
            "registration_date": "2024-06-20"
        }
    }
    if customer_id in customers:
        return {
            "success": True,
            "data": customers[customer_id]
        }
    else:
        return {
            "success": False,
            "errorCategory": "NOT_FOUND",
            "isRetryable": False,
            "message": f"Customer {customer_id} not found"
        }

def lookup_order(customer_id: str, order_id: str) -> dict:
    """Mock order lookup."""
    orders = {
        "CUST-001": {
            "ORD-101": {
                "id": "ORD-101",
                "date": "2024-03-01",
                "total": 150.00,
                "status": "delivered",
                "items": [{"name": "Laptop Stand", "qty": 1, "price": 150.00}]
            },
            "ORD-102": {
                "id": "ORD-102",
                "date": "2024-03-10",
                "total": 45.00,
                "status": "in_transit",
                "items": [{"name": "USB Cable", "qty": 2, "price": 22.50}]
            }
        },
        "CUST-002": {
            "ORD-201": {
                "id": "ORD-201",
                "date": "2024-02-15",
                "total": 89.99,
                "status": "delivered",
                "items": [{"name": "Wireless Mouse", "qty": 1, "price": 89.99}]
            }
        }
    }

    if customer_id in orders and order_id in orders[customer_id]:
        return {
            "success": True,
            "data": orders[customer_id][order_id]
        }
    else:
        return {
            "success": False,
            "errorCategory": "NOT_FOUND",
            "isRetryable": False,
            "message": f"Order {order_id} not found for customer {customer_id}"
        }

def process_refund(customer_id: str, order_id: str, reason: str) -> dict:
    """Mock refund processing."""
    # Prerequisite check: In a real system, this would be enforced at the tool level
    if not customer_id or not order_id:
        return {
            "success": False,
            "errorCategory": "INVALID_REQUEST",
            "isRetryable": False,
            "message": "customer_id and order_id are required"
        }

    # Simulate refund processing
    return {
        "success": True,
        "data": {
            "refund_id": f"REF-{order_id}",
            "customer_id": customer_id,
            "order_id": order_id,
            "reason": reason,
            "status": "processed",
            "amount": 150.00,
            "estimated_arrival": "3-5 business days"
        }
    }

def escalate_to_human(customer_id: str, issue_summary: str, urgency: str) -> dict:
    """Mock escalation to human support."""
    return {
        "success": True,
        "data": {
            "ticket_id": f"TKT-{customer_id}-{hash(issue_summary) % 100000}",
            "customer_id": customer_id,
            "issue": issue_summary,
            "urgency": urgency,
            "status": "assigned",
            "assigned_to": "Support Agent - Emma",
            "message": "Your issue has been escalated to our support team. You'll receive an email shortly with your ticket number."
        }
    }

# ============================================================================
# TOOL EXECUTION & PREREQUISITE GATING
# ============================================================================

class ToolExecutor:
    """Executes tools with prerequisite validation and error handling."""

    def __init__(self):
        self.executed_tools = {}  # Track which tools have been executed

    def execute(self, tool_name: str, tool_input: dict) -> str:
        """
        Execute a tool with prerequisite checking.
        Returns normalized JSON response.
        """

        # PREREQUISITE GATING (Domain 1: Error Handling Pattern)
        prerequisites = {
            "lookup_order": ["get_customer"],
            "process_refund": ["get_customer", "lookup_order"],
            "escalate_to_human": [],
        }

        required_tools = prerequisites.get(tool_name, [])
        for required_tool in required_tools:
            if required_tool not in self.executed_tools:
                return json.dumps({
                    "success": False,
                    "errorCategory": "PREREQUISITE_NOT_MET",
                    "isRetryable": True,
                    "message": f"Tool '{tool_name}' requires '{required_tool}' to be called first",
                    "suggestedNextStep": f"Call {required_tool} first with customer_id"
                })

        # Execute the tool
        print(f"\n  🔧 Executing: {tool_name}")
        print(f"     Input: {json.dumps(tool_input, indent=2)}")

        if tool_name == "get_customer":
            result = get_customer(tool_input["customer_id"])
        elif tool_name == "lookup_order":
            result = lookup_order(tool_input["customer_id"], tool_input["order_id"])
        elif tool_name == "process_refund":
            result = process_refund(tool_input["customer_id"], tool_input["order_id"], tool_input["reason"])
        elif tool_name == "escalate_to_human":
            result = escalate_to_human(tool_input["customer_id"], tool_input["issue_summary"], tool_input["urgency"])
        else:
            result = {
                "success": False,
                "errorCategory": "UNKNOWN_TOOL",
                "isRetryable": False,
                "message": f"Unknown tool: {tool_name}"
            }

        # Track executed tool
        self.executed_tools[tool_name] = tool_input

        # POSTTOOLUSE NORMALIZATION HOOK (Domain 5: Context Management)
        # Normalize all tool responses to a consistent format
        normalized = self._normalize_response(result)

        print(f"     Result: {json.dumps(normalized, indent=2)}")
        return json.dumps(normalized)

    def _normalize_response(self, result: dict) -> dict:
        """Normalize tool responses to consistent format."""
        if result.get("success"):
            return {
                "status": "success",
                "data": result.get("data"),
                "timestamp": "2024-03-22T11:30:00Z"
            }
        else:
            return {
                "status": "error",
                "errorCategory": result.get("errorCategory", "UNKNOWN_ERROR"),
                "isRetryable": result.get("isRetryable", False),
                "message": result.get("message"),
                "suggestedNextStep": result.get("suggestedNextStep"),
                "timestamp": "2024-03-22T11:30:00Z"
            }

# ============================================================================
# AGENTIC LOOP (Domain 1: Agentic Architecture & Orchestration)
# ============================================================================

def run_agent(user_request: str, customer_id: str) -> str:
    """
    Main agentic loop with tool use, error handling, and multi-concern resolution.

    Key Domain 1 concepts:
    - Iterate until stop_reason is 'end_user_message' or 'tool_use'
    - Handle tool results and feed back into the loop
    - Track stop_reason to understand agent intent
    """

    print(f"\n{'='*70}")
    print(f"CUSTOMER REQUEST: {user_request}")
    print(f"CUSTOMER ID: {customer_id}")
    print(f"{'='*70}\n")

    tool_executor = ToolExecutor()
    messages = [
        {
            "role": "user",
            "content": f"[Customer ID: {customer_id}]\n\n{user_request}"
        }
    ]

    system_prompt = """You are a customer support agent. Your goal is to resolve customer issues efficiently and accurately.

Guidelines:
1. Always start by calling get_customer to verify and load the customer profile
2. For order-related issues, call lookup_order to understand the situation
3. For refund requests, call process_refund with appropriate reasons
4. If an issue is complex or beyond your authority, escalate_to_human
5. If a tool call fails due to PREREQUISITE_NOT_MET, acknowledge and call the prerequisite tool
6. Provide clear, customer-friendly responses
7. Handle multiple concerns in a single request (e.g., "I have two issues")

When responding, be empathetic and professional. Summarize actions taken."""

    iteration = 0
    max_iterations = 10  # Safety limit

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- ITERATION {iteration} ---")

        # Call Claude with tools
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        print(f"Stop Reason: {response.stop_reason}")

        # Process response content
        assistant_message = {
            "role": "assistant",
            "content": response.content
        }
        messages.append(assistant_message)

        # Check if agent wants to use tools
        if response.stop_reason == "tool_use":
            # Find and execute tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    # Execute the tool
                    result = tool_executor.execute(tool_name, tool_input)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result
                    })

            # Add tool results to messages
            messages.append({
                "role": "user",
                "content": tool_results
            })

        elif response.stop_reason == "end_user_message":
            # Agent has finished - extract final response
            final_response = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_response = block.text
                    break

            print(f"\n{'='*70}")
            print("AGENT RESPONSE:")
            print(f"{'='*70}")
            print(final_response)
            print(f"{'='*70}\n")

            return final_response

        else:
            print(f"Unexpected stop_reason: {response.stop_reason}")
            break

    return "Agent loop exceeded maximum iterations"

# ============================================================================
# MAIN - TEST SCENARIOS (Multi-Concern Handling)
# ============================================================================

if __name__ == "__main__":
    # Scenario 1: Single concern - Simple refund request
    print("\n\n" + "="*70)
    print("SCENARIO 1: Simple Refund Request")
    print("="*70)
    run_agent(
        user_request="I want to return order ORD-101 because the stand doesn't fit my desk.",
        customer_id="CUST-001"
    )

    # Scenario 2: Multi-concern - Multiple issues in one request
    print("\n\n" + "="*70)
    print("SCENARIO 2: Multi-Concern Request (2 issues)")
    print("="*70)
    run_agent(
        user_request="I have two issues: (1) I haven't received my order ORD-102 yet, and (2) I want to return ORD-101 because it's defective.",
        customer_id="CUST-001"
    )

    # Scenario 3: Error handling - Invalid customer
    print("\n\n" + "="*70)
    print("SCENARIO 3: Error Handling - Invalid Customer")
    print("="*70)
    run_agent(
        user_request="I need to return my order",
        customer_id="CUST-999"
    )
