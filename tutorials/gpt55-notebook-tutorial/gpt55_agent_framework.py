"""
GPT-5.5 Enterprise Agent Framework
===================================

A Python application demonstrating GPT-5.5 improvements translated into
deployable AI-agent patterns based on OpenAI's official GPT-5.5 System Card
and Deployment Safety Hub.

Based on: https://deploymentsafety.openai.com/gpt-5-5
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import json


# =============================================================================
# Core Data Models
# =============================================================================

@dataclass
class Improvement:
    """Represents a documented GPT-5.5 improvement with enterprise implications."""
    rank: int
    name: str
    pattern: str
    enterprise_value: str
    required_control: str

    def to_dict(self) -> Dict:
        return {
            "rank": self.rank,
            "name": self.name,
            "pattern": self.pattern,
            "enterprise_value": self.enterprise_value,
            "required_control": self.required_control,
        }


# =============================================================================
# Decision Engine
# =============================================================================

class Decision(str, Enum):
    """Control decisions for agentic task routing."""
    ALLOW = "allow"
    ALLOW_WITH_CHECKS = "allow_with_checks"
    HUMAN_REVIEW = "human_review"
    BLOCK = "block"


class TaskScorer:
    """
    Toy risk scorer for agentic AI tasks.
    
    Demonstrates how enterprise agent wrappers can decide whether a task should be:
    - allowed directly
    - allowed with checks
    - escalated to human review
    - blocked
    """
    
    HIGH_RISK_WORDS = ["delete", "send", "purchase", "transfer", "deploy", "approve", "release"]
    LOW_RISK_WORDS = ["summarize", "draft", "analyze", "classify", "review", "generate", "extract"]
    
    def __init__(self, tool_weight: int = 2, irreversible_weight: int = 4, 
                 sensitive_weight: int = 3, action_weight: int = 3):
        self.tool_weight = tool_weight
        self.irreversible_weight = irreversible_weight
        self.sensitive_weight = sensitive_weight
        self.action_weight = action_weight
    
    def score_task(
        self,
        task: str,
        uses_tools: bool = False,
        irreversible: bool = False,
        sensitive_data: bool = False
    ) -> Dict:
        """Calculate risk score and determine appropriate decision."""
        task_lower = task.lower()
        risk = 0
        
        if uses_tools:
            risk += self.tool_weight
        if irreversible:
            risk += self.irreversible_weight
        if sensitive_data:
            risk += self.sensitive_weight
        if any(word in task_lower for word in self.HIGH_RISK_WORDS):
            risk += self.action_weight
        if any(word in task_lower for word in self.LOW_RISK_WORDS):
            risk -= 1
        
        risk = max(risk, 0)
        
        if risk >= 8:
            decision = Decision.HUMAN_REVIEW
        elif risk >= 5:
            decision = Decision.ALLOW_WITH_CHECKS
        else:
            decision = Decision.ALLOW
        
        return {
            "task": task,
            "risk_score": risk,
            "decision": decision.value,
            "details": {
                "uses_tools": uses_tools,
                "irreversible": irreversible,
                "sensitive_data": sensitive_data,
            }
        }


# =============================================================================
# Agent Control System
# =============================================================================

class AgentControlSystem:
    """
    Enterprise agent control system demonstrating the recommended control-plane design:
    
    User Request → Intent/Risk Classifier → Planner → Policy/Guardrail Layer
    → Tool Execution Layer → Verifier/Evaluator → Human Review if Needed
    → Final Response/Action → Telemetry + Monitoring + Eval Store
    """
    
    def __init__(self):
        self.scorer = TaskScorer()
        self.execution_log: List[Dict] = []
    
    def process_task(
        self,
        task: str,
        uses_tools: bool = False,
        irreversible: bool = False,
        sensitive_data: bool = False
    ) -> Dict:
        """Process a task through the control system."""
        score_result = self.scorer.score_task(task, uses_tools, irreversible, sensitive_data)
        
        result = {
            "task": task,
            "risk_assessment": score_result,
            "control_actions": [],
            "executed": False,
        }
        
        decision = score_result["decision"]
        
        if decision == Decision.ALLOW.value:
            result["control_actions"].append("Direct execution authorized")
            result["executed"] = True
            
        elif decision == Decision.ALLOW_WITH_CHECKS.value:
            result["control_actions"].append("Execution with verification checks")
            result["control_actions"].append("Log all intermediate outputs")
            result["executed"] = True
            
        elif decision == Decision.HUMAN_REVIEW.value:
            result["control_actions"].append("ESCALATION: Requires human approval")
            result["control_actions"].append("Capture justification for review")
            result["executed"] = False
            
        elif decision == Decision.BLOCK.value:
            result["control_actions"].append("BLOCKED: Task exceeds risk tolerance")
            result["executed"] = False
        
        self.execution_log.append(result)
        return result
    
    def get_execution_log(self) -> List[Dict]:
        """Return the execution history."""
        return self.execution_log


# =============================================================================
# Architecture Backlog
# =============================================================================

@dataclass
class ArchitectureCapability:
    """Maps improvements to system capabilities."""
    capability: str
    why_it_matters: str
    maps_to_improvements: str
    
    def to_dict(self) -> Dict:
        return {
            "capability": self.capability,
            "why_it_matters": self.why_it_matters,
            "maps_to_improvements": self.maps_to_improvements,
        }


def get_architecture_backlog() -> List[ArchitectureCapability]:
    """Returns the architecture backlog from GPT-5.5 improvements."""
    return [
        ArchitectureCapability("Task intake classifier", "Routes work by intent, risk, and required tools.", "1, 2"),
        ArchitectureCapability("Planner", "Breaks a broad request into executable steps.", "1, 5"),
        ArchitectureCapability("Tool registry", "Defines which tools the agent may use.", "3"),
        ArchitectureCapability("Execution sandbox", "Prevents unsafe or uncontrolled execution.", "3, 6, 8"),
        ArchitectureCapability("Verifier / evaluator", "Checks correctness against explicit criteria.", "4, 8, 9"),
        ArchitectureCapability("Audit log", "Records decisions, sources, tool calls, and outputs.", "3, 4, 10"),
        ArchitectureCapability("Human approval gate", "Escalates sensitive or irreversible actions.", "3, 5, 10"),
        ArchitectureCapability("Risk scoring layer", "Scores request, tool, data, and action risk.", "3, 10"),
        ArchitectureCapability("Regression eval suite", "Prevents quality regressions as prompts/tools change.", "4, 9, 10"),
        ArchitectureCapability("Production monitoring dashboard", "Tracks quality, safety, cost, latency, and incidents.", "5, 9, 10"),
    ]


# =============================================================================
# Evaluation Checklist
# =============================================================================

@dataclass
class EvalChecklistItem:
    """Pre-production evaluation gate item."""
    area: str
    question: str
    suggested_metric: str
    
    def to_dict(self) -> Dict:
        return {
            "area": self.area,
            "question": self.question,
            "suggested_metric": self.suggested_metric,
        }


def get_eval_checklist() -> List[EvalChecklistItem]:
    """Returns the evaluation checklist for GPT-5.5-style deployments."""
    return [
        EvalChecklistItem("Task success", "Does the agent complete the intended workflow end-to-end?", "Task completion rate"),
        EvalChecklistItem("Factuality", "Are claims supported by reliable sources or internal data?", "Citation accuracy / groundedness score"),
        EvalChecklistItem("Tool correctness", "Are tool calls valid, minimal, and reversible where possible?", "Tool-call success and rollback rate"),
        EvalChecklistItem("Safety", "Does the system avoid prohibited or unsafe actions?", "Policy violation rate"),
        EvalChecklistItem("Data privacy", "Does it avoid exposing sensitive data?", "PII leakage rate"),
        EvalChecklistItem("Observability", "Can we trace prompts, decisions, tool calls, and outputs?", "Trace coverage %"),
        EvalChecklistItem("Human escalation", "Are high-risk tasks routed to humans?", "Escalation precision/recall"),
        EvalChecklistItem("Cost and latency", "Is the workflow economically viable at expected volume?", "Cost per successful task; p95 latency"),
        EvalChecklistItem("Regression testing", "Do changes to prompts/tools/models preserve quality?", "Golden-set pass rate"),
        EvalChecklistItem("Incident response", "Can failures be detected, triaged, and remediated?", "MTTD / MTTR"),
    ]


# =============================================================================
# Workflow Evaluation
# =============================================================================

@dataclass
class WorkflowEvaluation:
    """Team exercise for evaluating candidate workflows."""
    workflow_name: str
    task_description: str
    required_tools: List[str]
    potential_failures: List[str]
    sensitive_data: List[str]
    required_approvals: List[str]
    golden_test_cases: List[str]
    required_telemetry: List[str]
    rollback_path: str
    
    def to_dict(self) -> Dict:
        return {
            "workflow_name": self.workflow_name,
            "task_description": self.task_description,
            "required_tools": self.required_tools,
            "potential_failures": self.potential_failures,
            "sensitive_data": self.sensitive_data,
            "required_approvals": self.required_approvals,
            "golden_test_cases": self.golden_test_cases,
            "required_telemetry": self.required_telemetry,
            "rollback_path": self.rollback_path,
        }


# =============================================================================
# Main Application Functions
# =============================================================================

def get_improvements() -> List[Improvement]:
    """Returns the 10 documented GPT-5.5 improvements."""
    return [
        Improvement(1, "Earlier task understanding", "Intent detection + task decomposition", 
                   "Less prompt scaffolding", "Intent logging and ambiguity checks"),
        Improvement(2, "Less guidance required", "Reduced user handholding", 
                   "Better adoption by non-experts", "Confidence thresholds"),
        Improvement(3, "More effective tool use", "Tool orchestration", 
                   "End-to-end workflow automation", "Tool allowlists and approval gates"),
        Improvement(4, "Self-checking behavior", "Draft → verify → revise", 
                   "Higher quality outputs", "External evals; do not rely only on self-checks"),
        Improvement(5, "Persistence through completion", "Continue until done", 
                   "Useful for multi-step work", "Step budgets and stop conditions"),
        Improvement(6, "Stronger coding support", "Generate, debug, refactor, test", 
                   "Engineering acceleration", "CI tests, code review, sandboxing"),
        Improvement(7, "Better research and synthesis", "Collect, compare, summarize", 
                   "Analyst productivity", "Citation and source-quality checks"),
        Improvement(8, "Improved data-analysis workflows", "Notebook + spreadsheet + report generation", 
                   "Data science acceleration", "Reproducibility checks"),
        Improvement(9, "Better agent benchmark performance", "Computer-use / task benchmarks", 
                   "More credible agent pilots", "Pilot with domain-specific evals"),
        Improvement(10, "Deployment-safety emphasis", "Evaluate, monitor, improve", 
                   "Safer scaling", "Monitoring, red teaming, incident review"),
    ]


def print_improvements_table():
    """Print formatted improvements table."""
    improvements = get_improvements()
    print("\n" + "="*100)
    print("GPT-5.5: 1–10 Documented Improvements")
    print("="*100)
    print(f"{'#':<3} {'Improvement':<30} {'Pattern':<30} {'Enterprise Value':<25}")
    print("-"*100)
    for imp in improvements:
        print(f"{imp.rank:<3} {imp.name:<30} {imp.pattern:<30} {imp.enterprise_value:<25}")


def print_architecture_backlog():
    """Print formatted architecture backlog."""
    backlog = get_architecture_backlog()
    print("\n" + "="*100)
    print("Architecture Translation: Improvement → System Capability")
    print("="*100)
    print(f"{'Capability':<25} {'Why it matters':<45} {'Maps to #'}")
    print("-"*100)
    for cap in backlog:
        print(f"{cap.capability:<25} {cap.why_it_matters:<45} {cap.maps_to_improvements}")


def print_eval_checklist():
    """Print formatted evaluation checklist."""
    checklist = get_eval_checklist()
    print("\n" + "="*100)
    print("Pre-Production Evaluation Checklist")
    print("="*100)
    print(f"{'Area':<20} {'Question':<50} {'Metric'}")
    print("-"*100)
    for item in checklist:
        print(f"{item.area:<20} {item.question:<50} {item.suggested_metric}")


def demo_agent_control():
    """Demonstrate the agent control system with sample tasks."""
    control = AgentControlSystem()
    
    examples = [
        ("Summarize this document", False, False, False),
        ("Analyze customer churn data and create charts", True, False, True),
        ("Send the final pricing email to the customer", True, True, False),
        ("Deploy this change to production", True, True, False),
    ]
    
    print("\n" + "="*100)
    print("Agent Control System Demo")
    print("="*100)
    print(f"{'Task':<45} {'Risk Score':<12} {'Decision'}")
    print("-"*100)
    
    for task, tools, irr, sensitive in examples:
        result = control.process_task(task, tools, irr, sensitive)
        assessment = result["risk_assessment"]
        print(f"{task:<45} {assessment['risk_score']:<12} {assessment['decision']}")
    
    print("\n" + "-"*100)
    print("Control Actions Summary:")
    for log in control.get_execution_log():
        print(f"\n  Task: {log['task']}")
        for action in log['control_actions']:
            print(f"    → {action}")


def demo_workflow_evaluation():
    """Demonstrate workflow evaluation for common enterprise use cases."""
    workflows = [
        WorkflowEvaluation(
            workflow_name="Customer-support refund assistant",
            task_description="Process customer refund requests through validation and processing",
            required_tools=["CRM API", "Payment processor", "Email client"],
            potential_failures=["Incorrect refund amount", "Duplicate requests", "Fraud detection miss"],
            sensitive_data=["Customer PII", "Payment details", "Conversation history"],
            required_approvals=["Refunds over $500", "VIP customers", "Disputed charges"],
            golden_test_cases=[
                "Valid refund under $100",
                "Refund requiring manager approval",
                "Potential fraud flagged for review"
            ],
            required_telemetry=["Request timestamp", "Agent ID", "Tool calls made", "Final decision"],
            rollback_path="Reverse payment transaction, log incident, notify supervisor"
        ),
        WorkflowEvaluation(
            workflow_name="AIOps incident triage agent",
            task_description="Classify and route infrastructure incidents to appropriate teams",
            required_tools=["Monitoring system", "Ticketing system", "Knowledge base"],
            potential_failures=["Wrong team routing", "Severity miscalculation", "Alert fatigue"],
            sensitive_data=["System topology", "Customer impact data", "SLA information"],
            required_approvals=["Severity P1 incidents", "Customer-facing announcements"],
            golden_test_cases=[
                "Database connection timeout",
                "API latency spike",
                "Security scan triggered"
            ],
            required_telemetry=["Classification confidence", "Routing accuracy", "Resolution time"],
            rollback_path="Reassign ticket, escalate to on-call manager"
        ),
    ]
    
    print("\n" + "="*100)
    print("Workflow Evaluation Exercises")
    print("="*100)
    
    for wf in workflows:
        print(f"\n📋 {wf.workflow_name}")
        print("-"*60)
        print(f"  Task: {wf.task_description}")
        print(f"  Tools: {', '.join(wf.required_tools)}")
        print(f"  Sensitive Data: {', '.join(wf.sensitive_data)}")
        print(f"  Required Approvals: {', '.join(wf.required_approvals)}")
        print(f"  Rollback Path: {wf.rollback_path}")


def export_json(output_path: Optional[str] = None):
    """Export all data structures to JSON."""
    data = {
        "improvements": [i.to_dict() for i in get_improvements()],
        "architecture_backlog": [a.to_dict() for a in get_architecture_backlog()],
        "eval_checklist": [e.to_dict() for e in get_eval_checklist()],
    }
    
    json_str = json.dumps(data, indent=2)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(json_str)
        print(f"Exported to {output_path}")
    else:
        print(json_str)
    
    return data


# =============================================================================
# Entry Point
# =============================================================================

def main():
    """Main entry point demonstrating all GPT-5.5 framework components."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GPT-5.5 Enterprise Agent Framework")
    parser.add_argument("--export-json", metavar="PATH", help="Export data to JSON file")
    parser.add_argument("--demo", choices=["all", "improvements", "architecture", "eval", "agent", "workflows"],
                       default="all", help="Which demo to run")
    args = parser.parse_args()
    
    if args.export_json:
        export_json(args.export_json)
        return
    
    if args.demo in ("all", "improvements"):
        print_improvements_table()
    
    if args.demo in ("all", "architecture"):
        print_architecture_backlog()
    
    if args.demo in ("all", "eval"):
        print_eval_checklist()
    
    if args.demo in ("all", "agent"):
        demo_agent_control()
    
    if args.demo in ("all", "workflows"):
        demo_workflow_evaluation()
    
    if args.demo == "all":
        print("\n" + "="*100)
        print("KEY RULE: Do not deploy an agent solely because the model is stronger.")
        print("Deploy only when the SURROUNDING OPERATING SYSTEM is strong enough:")
        print("  - Scoped tools")
        print("  - Auditable traces")
        print("  - Domain evals")
        print("  - Rollback paths")
        print("  - Human approval for irreversible actions")
        print("="*100 + "\n")


if __name__ == "__main__":
    main()