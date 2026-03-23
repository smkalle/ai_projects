#!/usr/bin/env python3
"""
CLI runner for the Code Eval Workbench.

Usage:
  python run_eval.py                          # Run all examples, all scorers
  python run_eval.py --category arithmetic    # Filter by category
  python run_eval.py --difficulty easy        # Filter by difficulty
  python run_eval.py --ids bug_001 bug_002    # Run specific examples
  python run_eval.py --no-llm                 # Skip LLM judge (fast mode)
  python run_eval.py --no-prog                # Skip programmatic scorer
  python run_eval.py --output results.json    # Save results to file
  python run_eval.py --threshold 0.70         # Exit non-zero if score < threshold
"""
import argparse
import sys
import uuid
from datetime import datetime

from dotenv import load_dotenv
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich import print as rprint

from dataset import get_dataset
from scorer import composite_score
from task import fix_code_bug
from utils import (
    EvalResult,
    RunSummary,
    ScoreBreakdown,
    save_run,
    score_color,
    score_emoji,
)

load_dotenv()
console = Console()


# ─── CLI argument parsing ─────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Code Eval Workbench — evaluate Claude's bug-fixing ability",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--category", nargs="+", help="Filter by category")
    parser.add_argument("--difficulty", nargs="+", help="Filter by difficulty (easy/medium/hard)")
    parser.add_argument("--ids", nargs="+", help="Run specific example IDs only")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM-as-judge scorer")
    parser.add_argument("--no-prog", action="store_true", help="Skip programmatic scorer")
    parser.add_argument("--no-lev", action="store_true", help="Skip Levenshtein scorer")
    parser.add_argument("--output", default=None, help="JSON output path (default: auto-save)")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.0,
        help="Exit with code 1 if composite score < threshold (default: 0.0 = disabled)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Show full outputs")
    return parser.parse_args()


# ─── Display helpers ──────────────────────────────────────────────────────────

def make_score_cell(score: float | None, width: int = 6) -> str:
    if score is None:
        return "[dim]  n/a  [/dim]"
    color = score_color(score)
    emoji = score_emoji(score)
    return f"[{color}]{score:.3f} {emoji}[/{color}]"


def print_header(n_examples: int, scorers: list[str]):
    console.print()
    console.print(
        Panel(
            f"[bold cyan]Code Eval Workbench[/bold cyan]\n"
            f"[dim]Model: claude-opus-4-6 + adaptive thinking[/dim]\n"
            f"[dim]Examples: {n_examples}  |  Scorers: {', '.join(scorers)}[/dim]",
            expand=False,
            border_style="cyan",
        )
    )
    console.print()


def print_results_table(results: list[EvalResult], use_llm: bool, use_prog: bool, use_lev: bool):
    table = Table(
        title="[bold]Evaluation Results[/bold]",
        show_header=True,
        header_style="bold magenta",
        border_style="dim",
        expand=False,
    )
    table.add_column("ID", style="dim", width=10)
    table.add_column("Category", width=18)
    table.add_column("Diff", width=6)
    if use_llm:
        table.add_column("LLM Judge", justify="center", width=12)
    if use_prog:
        table.add_column("Prog Tests", justify="center", width=12)
    if use_lev:
        table.add_column("Similarity", justify="center", width=12)
    table.add_column("Composite", justify="center", width=12)

    for r in results:
        row = [r.id, r.category, r.difficulty]
        if use_llm:
            row.append(make_score_cell(r.scores.llm_judge))
        if use_prog:
            prog_cell = make_score_cell(r.scores.programmatic)
            if r.passed_tests is not None and r.total_tests is not None:
                prog_cell += f"[dim] ({r.passed_tests}/{r.total_tests})[/dim]"
            row.append(prog_cell)
        if use_lev:
            row.append(make_score_cell(r.scores.levenshtein))
        row.append(make_score_cell(r.scores.composite))
        table.add_row(*row)

    console.print(table)


def print_summary(results: list[EvalResult], run_id: str):
    composites = [r.scores.composite for r in results]
    avg = sum(composites) / len(composites) if composites else 0.0

    color = score_color(avg)

    # Score distribution
    buckets = {"≥0.8": 0, "0.6-0.8": 0, "0.4-0.6": 0, "<0.4": 0}
    for s in composites:
        if s >= 0.8:
            buckets["≥0.8"] += 1
        elif s >= 0.6:
            buckets["0.6-0.8"] += 1
        elif s >= 0.4:
            buckets["0.4-0.6"] += 1
        else:
            buckets["<0.4"] += 1

    dist_str = "  ".join(
        f"[{'green' if k == '≥0.8' else 'yellow' if k == '0.6-0.8' else 'orange3' if k == '0.4-0.6' else 'red'}]"
        f"{k}: {v}[/]"
        for k, v in buckets.items()
    )

    console.print()
    console.print(
        Panel(
            f"[bold {color}]FINAL COMPOSITE SCORE: {avg:.3f}  {score_emoji(avg)}[/bold {color}]\n"
            f"{dist_str}\n"
            f"[dim]Run ID: {run_id}[/dim]",
            title="[bold]Summary[/bold]",
            border_style=color,
            expand=False,
        )
    )
    console.print()
    return avg


# ─── Main eval loop ───────────────────────────────────────────────────────────

def run_eval(args) -> float:
    # Build dataset
    data = get_dataset(
        categories=args.category,
        difficulties=args.difficulty,
    )
    if args.ids:
        data = [d for d in data if d["id"] in args.ids]

    if not data:
        console.print("[red]No examples matched the filters.[/red]")
        return 0.0

    # Determine active scorers
    use_llm = not args.no_llm
    use_prog = not args.no_prog
    use_lev = not args.no_lev
    scorers_active = []
    if use_llm:
        scorers_active.append("LLM-as-judge")
    if use_prog:
        scorers_active.append("Programmatic")
    if use_lev:
        scorers_active.append("Levenshtein")

    print_header(len(data), scorers_active)

    results: list[EvalResult] = []
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Evaluating...", total=len(data))

        for item in data:
            progress.update(task, description=f"[cyan]{item['id']}[/cyan] — fixing bug...")

            # 1. Run the task (Claude fixes the bug)
            try:
                output = fix_code_bug(item["input"])
            except Exception as e:
                console.print(f"[red]Task error on {item['id']}: {e}[/red]")
                output = ""

            progress.update(task, description=f"[cyan]{item['id']}[/cyan] — scoring...")

            # 2. Score
            score_dict = composite_score(
                output=output,
                input_dict=item["input"],
                reference=item["reference_output"],
                test_code=item.get("test_code", ""),
                use_llm_judge=use_llm,
                use_programmatic=use_prog,
                use_levenshtein=use_lev,
            )

            result = EvalResult(
                id=item["id"],
                category=item["category"],
                difficulty=item["difficulty"],
                output=output,
                scores=ScoreBreakdown(
                    llm_judge=score_dict.get("llm_judge"),
                    programmatic=score_dict.get("programmatic"),
                    levenshtein=score_dict.get("levenshtein"),
                    composite=score_dict["composite"],
                ),
                reasoning=score_dict.get("reasoning", ""),
                passed_tests=score_dict.get("passed_tests"),
                total_tests=score_dict.get("total_tests"),
            )
            results.append(result)

            # Live score print
            composite_val = score_dict["composite"]
            color = score_color(composite_val)
            console.print(
                f"  [{color}]●[/{color}] {item['id']:10s} "
                f"composite=[{color}]{composite_val:.3f}[/{color}] "
                + (f"llm={score_dict['llm_judge']:.3f} " if score_dict.get("llm_judge") is not None else "")
                + (f"prog={score_dict['programmatic']:.3f} " if score_dict.get("programmatic") is not None else "")
                + (f"lev={score_dict['levenshtein']:.3f}" if score_dict.get("levenshtein") is not None else "")
            )

            if args.verbose and output:
                console.print(f"  [dim]Output preview: {output[:200].replace(chr(10), ' ')}...[/dim]")

            progress.advance(task)

    # Print final table & summary
    console.print()
    print_results_table(results, use_llm, use_prog, use_lev)
    final_score = print_summary(results, run_id)

    # Persist results
    run_summary = RunSummary(
        run_id=run_id,
        timestamp=datetime.now().isoformat(),
        avg_composite=round(final_score, 4),
        avg_llm_judge=round(
            sum(r.scores.llm_judge for r in results if r.scores.llm_judge is not None)
            / max(1, sum(1 for r in results if r.scores.llm_judge is not None)),
            4,
        ),
        avg_programmatic=round(
            sum(r.scores.programmatic for r in results if r.scores.programmatic is not None)
            / max(1, sum(1 for r in results if r.scores.programmatic is not None)),
            4,
        ),
        avg_levenshtein=round(
            sum(r.scores.levenshtein for r in results if r.scores.levenshtein is not None)
            / max(1, sum(1 for r in results if r.scores.levenshtein is not None)),
            4,
        ),
        n_examples=len(results),
        scorers_used=scorers_active,
        results=results,
    )

    save_path = save_run(run_summary)
    console.print(f"[dim]Results saved → {save_path}[/dim]")

    if args.output:
        from pathlib import Path
        Path(args.output).write_text(run_summary.model_dump_json(indent=2))
        console.print(f"[dim]Also exported → {args.output}[/dim]")

    return final_score


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    try:
        final_score = run_eval(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        sys.exit(1)

    if args.threshold > 0 and final_score < args.threshold:
        console.print(
            f"[red bold]FAIL:[/red bold] Score {final_score:.3f} < threshold {args.threshold:.3f}"
        )
        sys.exit(1)

    console.print(f"[green bold]PASS:[/green bold] Score {final_score:.3f}")


if __name__ == "__main__":
    main()
