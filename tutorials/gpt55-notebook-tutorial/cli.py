"""GPT-5.5 Interactive CLI — converts notebook tutorial to an interactive command-line tool."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Load .env if present
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

app = typer.Typer(help="GPT-5.5 Interactive CLI — Enterprise Agent Architecture Tutorial")
console = Console()


class Decision(str, Enum):
    ALLOW = "allow"
    ALLOW_WITH_CHECKS = "allow_with_checks"
    HUMAN_REVIEW = "human_review"
    BLOCK = "block"


@dataclass
class Improvement:
    rank: int
    name: str
    pattern: str
    enterprise_value: str
    required_control: str


IMPROVEMENTS: List[Improvement] = [
    Improvement(1, "Earlier task understanding", "Intent detection + task decomposition", "Less prompt scaffolding", "Intent logging and ambiguity checks"),
    Improvement(2, "Less guidance required", "Reduced user handholding", "Better adoption by non-experts", "Confidence thresholds"),
    Improvement(3, "More effective tool use", "Tool orchestration", "End-to-end workflow automation", "Tool allowlists and approval gates"),
    Improvement(4, "Self-checking behavior", "Draft → verify → revise", "Higher quality outputs", "External evals; do not rely only on self-checks"),
    Improvement(5, "Persistence through completion", "Continue until done", "Useful for multi-step work", "Step budgets and stop conditions"),
    Improvement(6, "Stronger coding support", "Generate, debug, refactor, test", "Engineering acceleration", "CI tests, code review, sandboxing"),
    Improvement(7, "Better research and synthesis", "Collect, compare, summarize", "Analyst productivity", "Citation and source-quality checks"),
    Improvement(8, "Improved data-analysis workflows", "Notebook + spreadsheet + report generation", "Data science acceleration", "Reproducibility checks"),
    Improvement(9, "Better agent benchmark performance", "Computer-use / task benchmarks", "More credible agent pilots", "Pilot with domain-specific evals"),
    Improvement(10, "Deployment-safety emphasis", "Evaluate, monitor, improve", "Safer scaling", "Monitoring, red teaming, incident review"),
]

ARCHITECTURE_BACKLOG = {
    "Capability": [
        "Task intake classifier",
        "Planner",
        "Tool registry",
        "Execution sandbox",
        "Verifier / evaluator",
        "Audit log",
        "Human approval gate",
        "Risk scoring layer",
        "Regression eval suite",
        "Production monitoring dashboard",
    ],
    "Why it matters": [
        "Routes work by intent, risk, and required tools.",
        "Breaks a broad request into executable steps.",
        "Defines which tools the agent may use.",
        "Prevents unsafe or uncontrolled execution.",
        "Checks correctness against explicit criteria.",
        "Records decisions, sources, tool calls, and outputs.",
        "Escalates sensitive or irreversible actions.",
        "Scores user request, tool risk, data sensitivity, and action risk.",
        "Prevents quality regressions as prompts/tools change.",
        "Tracks quality, safety, cost, latency, and incidents.",
    ],
    "Maps to improvements": [
        "1, 2",
        "1, 5",
        "3",
        "3, 6, 8",
        "4, 8, 9",
        "3, 4, 10",
        "3, 5, 10",
        "3, 10",
        "4, 9, 10",
        "5, 9, 10",
    ],
}

EVAL_CHECKLIST = {
    "Area": [
        "Task success",
        "Factuality",
        "Tool correctness",
        "Safety",
        "Data privacy",
        "Observability",
        "Human escalation",
        "Cost and latency",
        "Regression testing",
        "Incident response",
    ],
    "Question": [
        "Does the agent complete the intended workflow end-to-end?",
        "Are claims supported by reliable sources or internal data?",
        "Are tool calls valid, minimal, and reversible where possible?",
        "Does the system avoid prohibited or unsafe actions?",
        "Does it avoid exposing sensitive data?",
        "Can we trace prompts, decisions, tool calls, and outputs?",
        "Are high-risk tasks routed to humans?",
        "Is the workflow economically viable at expected volume?",
        "Do changes to prompts/tools/models preserve quality?",
        "Can failures be detected, triaged, and remediated?",
    ],
    "Suggested metric": [
        "Task completion rate",
        "Citation accuracy / groundedness score",
        "Tool-call success and rollback rate",
        "Policy violation rate",
        "PII leakage rate",
        "Trace coverage %",
        "Escalation precision/recall",
        "Cost per successful task; p95 latency",
        "Golden-set pass rate",
        "MTTD / MTTR",
    ],
}


@app.command()
def improvements(
    improvement_number: Optional[int] = typer.Option(None, "--number", "-n", help="Show specific improvement by number"),
    pattern: Optional[str] = typer.Option(None, "--pattern", "-p", help="Filter by pattern keyword"),
) -> None:
    """Display the 10 GPT-5.5 improvements with optional filtering."""
    results = IMPROVEMENTS

    if improvement_number:
        results = [i for i in results if i.rank == improvement_number]
        if not results:
            console.print(f"[red]No improvement found with number {improvement_number}[/red]")
            return
    elif pattern:
        results = [
            i for i in results
            if pattern.lower() in i.name.lower() or pattern.lower() in i.pattern.lower()
        ]
        if not results:
            console.print(f"[yellow]No improvements matching pattern '{pattern}'[/yellow]")
            return

    table = Table(title="GPT-5.5 Improvements")
    table.add_column("#", style="cyan bold", width=3)
    table.add_column("Improvement", style="green")
    table.add_column("Pattern", style="blue")
    table.add_column("Enterprise Value", style="magenta")
    table.add_column("Required Control", style="yellow")

    for imp in results:
        table.add_row(
            str(imp.rank),
            imp.name,
            imp.pattern,
            imp.enterprise_value,
            imp.required_control,
        )

    console.print(table)


@app.command()
def model() -> None:
    """Display the mental model: from chat model to execution model."""
    content = """[bold]Mental Model: From Chat Model to Execution Model[/bold]

GPT-5.5 should be treated less like a one-shot responder and more like an [bold green]agentic work system[/bold green]:

[cyan]Goal → Plan → Tool Use → Intermediate Checks → Final Output → Evaluation → Monitoring[/cyan]

For production use, the critical design question is not only:
[yellow]"Can the model answer?"[/yellow]

It is:
[bold yellow]"Can the full system complete the task safely, observably, and repeatably?"[/bold yellow]"""
    console.print(Panel(content, expand=False))


@app.command()
def backlog() -> None:
    """Display the architecture backlog mapping improvements to system capabilities."""
    table = Table(title="Architecture Backlog: Improvement → System Capability")
    table.add_column("Capability", style="green bold")
    table.add_column("Why it matters", style="white")
    table.add_column("Maps to improvements", style="cyan")

    for i in range(len(ARCHITECTURE_BACKLOG["Capability"])):
        table.add_row(
            ARCHITECTURE_BACKLOG["Capability"][i],
            ARCHITECTURE_BACKLOG["Why it matters"][i],
            ARCHITECTURE_BACKLOG["Maps to improvements"][i],
        )

    console.print(table)


def score_task(task: str, uses_tools: bool, irreversible: bool, sensitive_data: bool) -> dict:
    """Toy risk scorer for agentic AI tasks."""
    task_lower = task.lower()
    risk = 0

    if uses_tools:
        risk += 2
    if irreversible:
        risk += 4
    if sensitive_data:
        risk += 3
    if any(word in task_lower for word in ["delete", "send", "purchase", "transfer", "deploy"]):
        risk += 3
    if any(word in task_lower for word in ["summarize", "draft", "analyze", "classify"]):
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
    }


@app.command()
def score(
    task: Optional[str] = typer.Option(None, "--task", "-t", help="Task description"),
    uses_tools: Optional[bool] = typer.Option(None, "--tools/--no-tools", help="Task uses tools"),
    irreversible: Optional[bool] = typer.Option(None, "--irreversible/--reversible", help="Action is irreversible"),
    sensitive_data: Optional[bool] = typer.Option(None, "--sensitive/--no-sensitive", help="Involves sensitive data"),
    interactive: bool = typer.Option(True, "--interactive/--non-interactive", help="Interactive mode"),
) -> None:
    """Run the agent-control risk scoring simulation.

    In interactive mode, prompts for each parameter.
    In non-interactive mode, uses provided CLI options.
    """
    if interactive:
        console.print(Panel("[bold]Agent Risk Scorer[/bold] — Enter task parameters", expand=False))
        task = Prompt.ask("[cyan]Task description[/cyan]")
        uses_tools = Confirm.ask("[cyan]Does the task use tools?[/cyan]", default=False)
        irreversible = Confirm.ask("[cyan]Is the action irreversible?[/cyan]", default=False)
        sensitive_data = Confirm.ask("[cyan]Does it involve sensitive data?[/cyan]", default=False)

    if not task:
        console.print("[red]Error: task description is required[/red]")
        raise typer.Abort()

    result = score_task(task, uses_tools or False, irreversible or False, sensitive_data or False)

    decision_color = {
        "allow": "green",
        "allow_with_checks": "yellow",
        "human_review": "red",
        "block": "bold red",
    }.get(result["decision"], "white")

    table = Table(title="Risk Score Result", show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Task", result["task"])
    table.add_row("Risk Score", str(result["risk_score"]))
    table.add_row("Decision", f"[{decision_color}]{result['decision']}[/{decision_color}]")

    console.print(table)

    if result["decision"] == Decision.HUMAN_REVIEW.value:
        console.print("\n[bold red]⚠ High-risk task detected![/bold red] Recommend human review before execution.")
    elif result["decision"] == Decision.ALLOW_WITH_CHECKS.value:
        console.print("\n[bold yellow]⚠ Medium-risk task.[/bold yellow] Implement additional verification steps.")


@app.command()
def examples() -> None:
    """Show pre-built examples of the risk scoring simulation."""
    examples_list = [
        ("Summarize this document", False, False, False),
        ("Analyze customer churn data and create charts", True, False, True),
        ("Send the final pricing email to the customer", True, True, False),
        ("Deploy this change to production", True, True, False),
    ]

    results = [score_task(*x) for x in examples_list]

    table = Table(title="Risk Scoring Examples")
    table.add_column("Task", style="white")
    table.add_column("Risk Score", style="cyan", justify="center")
    table.add_column("Decision", style="yellow")

    for r in results:
        table.add_row(r["task"], str(r["risk_score"]), r["decision"])

    console.print(table)


@app.command()
def eval() -> None:
    """Display the pre-production evaluation checklist."""
    table = Table(title="GPT-5.5 Deployment Evaluation Checklist")
    table.add_column("Area", style="green bold")
    table.add_column("Question", style="white")
    table.add_column("Suggested Metric", style="cyan")

    for i in range(len(EVAL_CHECKLIST["Area"])):
        table.add_row(
            EVAL_CHECKLIST["Area"][i],
            EVAL_CHECKLIST["Question"][i],
            EVAL_CHECKLIST["Suggested metric"][i],
        )

    console.print(table)


@app.command()
def exercise(
    workflow: Optional[int] = typer.Option(None, "--workflow", "-w", help="Select workflow number (1-5)"),
) -> None:
    """Guided team exercise for evaluating an agent workflow.

    Walks through 8 assessment questions for a selected workflow.
    """
    workflows = [
        "Customer-support refund assistant",
        "Credit-card dispute summarizer",
        "AIOps incident triage agent",
        "Internal policy Q&A assistant",
        "Code-review assistant",
    ]

    if workflow:
        if workflow < 1 or workflow > 5:
            console.print("[red]Invalid workflow number. Choose 1-5.[/red]")
            return
        selected = workflows[workflow - 1]
    else:
        console.print(Panel("[bold]Team Exercise: Agent Workflow Assessment[/bold]\nSelect a workflow:", expand=False))
        for i, w in enumerate(workflows, 1):
            console.print(f"  [cyan]{i}[/cyan]. {w}")
        choice = Prompt.ask("\n[cyan]Enter workflow number (1-5)[/cyan]", default="1")
        try:
            selected = workflows[int(choice) - 1]
        except (ValueError, IndexError):
            console.print("[red]Invalid selection[/red]")
            return

    console.print(Panel(f"[bold green]Workflow:[/bold green] {selected}", expand=False))

    questions = [
        "What task does the agent complete?",
        "What tools does it need?",
        "What can go wrong?",
        "What data is sensitive?",
        "Which actions require human approval?",
        "What is the golden test set?",
        "What telemetry must be captured?",
        "What is the rollback path?",
    ]

    console.print("\n[bold]Answer the following questions:[/bold]")
    answers = {}
    for i, q in enumerate(questions, 1):
        answer = Prompt.ask(f"\n[cyan]{i}.[/cyan] {q}")
        answers[q] = answer

    console.print("\n[bold]Your Assessment Summary:[/bold]")
    summary_table = Table(show_header=False, box=None)
    summary_table.add_column("Question", style="cyan")
    summary_table.add_column("Answer", style="white")
    for q, a in answers.items():
        summary_table.add_row(q, a)
    console.print(summary_table)

    console.print(f"\n[bold green]✓ Assessment complete for:[/bold green] {selected}")


@app.command()
def summary() -> None:
    """Display the executive summary."""
    content = """[bold]Executive Summary[/bold]

GPT-5.5 represents a practical shift from [yellow]answer generation[/yellow] to [bold green]work execution[/bold green].

[bold]The strongest enterprise opportunity[/bold] is not replacing workers with a chatbot.
It is building controlled agent workflows where the model can:
• understand the goal
• plan the work
• use tools
• verify intermediate outputs
• escalate risky steps
• complete useful tasks with traceability

[bold red]The strongest enterprise risk[/bold red] is also not ordinary hallucination.
It is [bold red]confident multi-step execution with insufficient external controls[/bold red].

[bold]Key rule:[/bold] Do not deploy an agent solely because the model is stronger.
Deploy only when the surrounding [bold]operating system[/bold] is strong enough:
scoped tools, auditable traces, domain evals, rollback paths, and human approval for irreversible actions."""
    console.print(Panel(content, expand=False))


@app.command()
def all() -> None:
    """Display everything: improvements, model, backlog, examples, eval checklist, and summary."""
    console.print(Panel("[bold cyan]GPT-5.5 Interactive Tutorial[/bold cyan]", expand=False))
    improvements()
    console.print()
    model()
    console.print()
    backlog()
    console.print()
    examples()
    console.print()
    eval()
    console.print()
    summary()


if __name__ == "__main__":
    app()
