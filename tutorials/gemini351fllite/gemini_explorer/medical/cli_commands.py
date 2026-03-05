"""Click CLI commands for the medical diagnostic workbench.

EDUCATIONAL DEMO ONLY — NOT FOR CLINICAL USE.
"""

import asyncio
import json
import time

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .cases import SAMPLE_CASES
from .schemas import PatientIntake, Vitals
from .tools import check_hardcoded_red_flags, lookup_drug_interaction

console = Console()

DISCLAIMER_BANNER = Panel(
    "[bold red]EDUCATIONAL DEMO ONLY — NOT FOR CLINICAL USE[/]\n"
    "All outputs are AI-generated simulations.\n"
    "Do not use for medical decisions.",
    style="red",
)


def _print_disclaimer():
    console.print(DISCLAIMER_BANNER)
    console.print()


def register_medical_commands(medical_group):
    """Register all medical CLI commands onto the Click group."""

    @medical_group.command()
    @click.argument("description", required=False)
    @click.option("--age", type=int, help="Patient age")
    @click.option("--sex", type=click.Choice(["male", "female", "other"]), help="Patient sex")
    @click.option("--case", "case_name", type=click.Choice(list(SAMPLE_CASES)), help="Load a sample case")
    @click.option("--output", "output_fmt", type=click.Choice(["rich", "json"]), default="rich")
    def diagnose(description, age, sex, case_name, output_fmt):
        """Run the full 5-stage ADK diagnostic pipeline."""
        _print_disclaimer()

        if case_name:
            case = SAMPLE_CASES[case_name]
            console.print(f"[dim]Loaded sample case: {case.case_name}[/]")
        elif description and age and sex:
            case = PatientIntake(
                patient_id="cli_user",
                age=age,
                sex=sex,
                chief_complaint=description,
                symptoms=description.split(","),
                medical_history=[],
                current_medications=[],
                allergies=[],
                case_name="CLI Case",
            )
        else:
            console.print("[red]Provide --case OR (DESCRIPTION --age --sex)[/]")
            return

        # Check red flags first
        red_flags = check_hardcoded_red_flags(case.symptoms, case.chief_complaint)
        if red_flags:
            for flag in red_flags:
                console.print(Panel(f"[bold red]{flag['message']}[/]", title="RED FLAG", style="red"))

        console.print(f"[bold]Running pipeline for: {case.case_name}[/]")
        console.print("[dim]Stages: Triage → Parallel Analysis → Diagnosis Loop → Specialist → Summary[/]")
        console.print()

        from .agents import MedicalPipelineRunner

        runner = MedicalPipelineRunner()
        start = time.time()

        # Run async pipeline
        events = []
        async def _run():
            async for event in runner.run_async(case):
                events.append(event)

        asyncio.run(_run())
        elapsed = time.time() - start

        # Get final state
        state = asyncio.run(runner.get_state(case.patient_id))

        if output_fmt == "json":
            console.print_json(json.dumps({k: str(v) for k, v in state.items()}, indent=2))
        else:
            # Rich output — stage overview table
            stage_labels = {
                "triage_result": ("1. Triage", "cyan"),
                "symptom_analysis": ("2a. Symptoms", "green"),
                "imaging_findings": ("2b. Imaging", "green"),
                "differential_dx": ("3. Diagnosis", "yellow"),
                "specialist_opinion": ("4. Specialist", "magenta"),
                "case_summary": ("5. Summary", "bold"),
            }

            table = Table(title=f"Pipeline Results — {case.case_name}")
            table.add_column("Stage", style="cyan", min_width=15)
            table.add_column("Output Preview", max_width=80)

            for key, (label, style) in stage_labels.items():
                value = state.get(key, "—")
                preview = str(value).strip()
                # Strip markdown code fences if present
                if preview.startswith("```"):
                    preview = preview.split("\n", 1)[1] if "\n" in preview else preview[3:]
                    preview = preview.rsplit("```", 1)[0].strip()
                # For JSON outputs, extract a key detail
                try:
                    parsed = json.loads(preview)
                    if key == "triage_result" and "urgency_level" in parsed:
                        preview = f"[bold]{parsed['urgency_level']}[/] — {parsed.get('category', '')} (confidence: {parsed.get('confidence', '?')})"
                    elif key == "differential_dx" and "diagnoses" in parsed:
                        top = parsed["diagnoses"][:2]
                        preview = "; ".join(f"{d.get('condition', '?')} ({d.get('probability_pct', '?')}%)" for d in top)
                        preview += f" [dim](confidence: {parsed.get('overall_confidence', '?')})[/]"
                    elif key == "case_summary" and "assessment" in parsed:
                        preview = str(parsed["assessment"])[:200] + "..."
                    elif len(preview) > 200:
                        preview = preview[:200] + "..."
                except (json.JSONDecodeError, TypeError):
                    if len(preview) > 200:
                        preview = preview[:200] + "..."

                table.add_row(f"[{style}]{label}[/]", preview)

            console.print(table)
            console.print(f"\n[dim]Total time: {elapsed:.1f}s | Events: {len(events)}[/]")

            # Print case summary — parse JSON for readable display
            summary = state.get("case_summary", "")
            if summary:
                try:
                    # Strip markdown code fences if present
                    raw = str(summary).strip()
                    if raw.startswith("```"):
                        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                        raw = raw.rsplit("```", 1)[0]
                    parsed = json.loads(raw.strip())
                    lines = []
                    for key in ("subjective", "objective", "assessment", "plan"):
                        if key in parsed:
                            lines.append(f"**{key.upper()}**\n{parsed[key]}\n")
                    if "medications" in parsed:
                        lines.append("**MEDICATIONS**\n" + "\n".join(f"- {m}" for m in parsed["medications"]) + "\n")
                    if "follow_up" in parsed:
                        lines.append(f"**FOLLOW-UP**\n{parsed['follow_up']}\n")
                    if "disclaimer" in parsed:
                        lines.append(f"\n*{parsed['disclaimer']}*")
                    console.print(Panel(Markdown("\n".join(lines)), title="Case Summary (SOAP)", style="green"))
                except (json.JSONDecodeError, TypeError):
                    console.print(Panel(Markdown(str(summary)[:2000]), title="Case Summary", style="green"))

        _print_disclaimer()

    @medical_group.command()
    @click.argument("complaint")
    @click.option("--age", type=int, required=True, help="Patient age")
    @click.option("--sex", type=click.Choice(["male", "female", "other"]), required=True)
    def triage(complaint, age, sex):
        """Quick triage classification (Stage 1 only)."""
        _print_disclaimer()

        case = PatientIntake(
            patient_id="triage_user",
            age=age,
            sex=sex,
            chief_complaint=complaint,
            symptoms=complaint.split(","),
            medical_history=[],
            current_medications=[],
            allergies=[],
            case_name="Triage",
        )

        # Hardcoded red flags first
        red_flags = check_hardcoded_red_flags(case.symptoms, case.chief_complaint)
        if red_flags:
            for flag in red_flags:
                console.print(Panel(f"[bold red]{flag['message']}[/]", title="RED FLAG", style="red"))

        # Run just triage via direct API call (faster than full ADK pipeline)
        from gemini_explorer.client import MODEL, get_client, make_config, traced_generate
        from .prompts import TRIAGE_PROMPT

        client = get_client()
        prompt = TRIAGE_PROMPT.replace("{patient_intake}", case.model_dump_json())
        config = make_config(thinking_level="low")

        console.print("[dim]Running triage...[/]")
        response = traced_generate(client, MODEL, prompt, config)

        urgency_colors = {
            "EMERGENT": "red",
            "URGENT": "yellow",
            "SEMI-URGENT": "bright_yellow",
            "NON-URGENT": "green",
        }

        text = response.text or ""
        # Try to detect urgency level in output
        for level, color in urgency_colors.items():
            if level in text.upper():
                console.print(Panel(f"[bold {color}]{level}[/]", title="Urgency Level"))
                break

        console.print(Markdown(text))
        _print_disclaimer()

    @medical_group.command("analyze-image")
    @click.argument("image_path", type=click.Path(exists=True))
    @click.option("--prompt", default="Analyze this medical image. Describe findings, apply ABCDE criteria if skin lesion.")
    @click.option("--level", type=click.Choice(["low", "medium", "high"]), default="medium")
    def analyze_image(image_path, prompt, level):
        """Analyze a medical image using Gemini vision."""
        _print_disclaimer()

        from PIL import Image

        from gemini_explorer.client import MODEL, extract_response_parts, get_client, get_usage, make_config, traced_generate

        client = get_client()
        config = make_config(thinking_level=level)
        img = Image.open(image_path)

        console.print(f"[dim]Analyzing: {image_path}[/]")
        response = traced_generate(client, MODEL, [img, prompt], config)
        thoughts, answer = extract_response_parts(response)

        if thoughts:
            console.print(Panel(thoughts, title="Thoughts", style="dim"))
        console.print(Markdown(answer))

        usage = get_usage(response)
        console.print(f"[dim]Tokens: {usage['total_tokens']}[/]")
        _print_disclaimer()

    @medical_group.command("drug-check")
    @click.argument("drug_a")
    @click.argument("drug_b")
    def drug_check(drug_a, drug_b):
        """Check drug interaction between two medications (mock data)."""
        _print_disclaimer()

        result = json.loads(lookup_drug_interaction(drug_a, drug_b))

        severity_colors = {
            "MAJOR": "red",
            "CONTRAINDICATED": "bold red",
            "MODERATE": "yellow",
            "MINOR": "green",
            "UNKNOWN": "dim",
        }

        color = severity_colors.get(result.get("severity", ""), "white")

        table = Table(title=f"Drug Interaction: {drug_a} + {drug_b}")
        table.add_column("Field", style="cyan")
        table.add_column("Value")

        table.add_row("Severity", f"[{color}]{result.get('severity', 'N/A')}[/]")
        table.add_row("Description", result.get("description", ""))
        table.add_row("Clinical Significance", result.get("clinical_significance", ""))
        table.add_row("Action Required", str(result.get("action_required", "")))
        table.add_row("Disclaimer", result.get("disclaimer", ""))

        console.print(table)
