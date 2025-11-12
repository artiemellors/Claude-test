"""
Test script for Periodization Plan generation
Simple version without LangGraph - just orchestrates agents sequentially
"""
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from agents.periodization_orchestrator import PeriodizationOrchestrator
from agents.hyrox_periodization import HyroxPeriodizationAgent

# Load environment variables
load_dotenv()

console = Console()


def test_periodization_plan():
    """
    Test the periodization plan generation workflow
    """
    console.print("\n[bold cyan]Block Smith - Periodization Plan PoC[/bold cyan]\n")

    # Calculate race date 20 weeks from now
    race_date = (datetime.now() + timedelta(weeks=20)).strftime("%Y-%m-%d")

    # User input
    user_input = {
        "raceType": "hyrox",
        "raceDate": race_date,
        "currentFitness": "intermediate",
        "trainingDaysPerWeek": 5,
        "availableEquipment": ["barbell", "dumbbells", "rower", "skierg", "sleds"],
        "injuries": None
    }

    console.print(Panel(JSON(json.dumps(user_input, indent=2)), title="User Input"))

    # Step 1: Periodization Orchestrator
    console.print("\n[bold yellow]Step 1: Periodization Orchestrator[/bold yellow]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Routing to sport-specific agent...", total=None)

        orchestrator = PeriodizationOrchestrator()
        orchestrator_output = orchestrator.execute(user_input)

        progress.stop()

    console.print(Panel(
        JSON(json.dumps(orchestrator_output, indent=2)),
        title="Orchestrator Output",
        border_style="green"
    ))

    # Step 2: Hyrox Periodization Agent
    if orchestrator_output.get("routeTo") == "hyrox_periodization_agent":
        console.print("\n[bold yellow]Step 2: Hyrox Periodization Agent[/bold yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating Hyrox periodization plan...", total=None)

            hyrox_agent = HyroxPeriodizationAgent()
            periodization_plan = hyrox_agent.execute(orchestrator_output)

            progress.stop()

        console.print(Panel(
            JSON(json.dumps(periodization_plan, indent=2)),
            title="Hyrox Periodization Plan",
            border_style="green"
        ))

        # Save to file
        output_file = f"poc/output/periodization_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, "w") as f:
            json.dump(periodization_plan, f, indent=2)

        console.print(f"\n[bold green]✓ Plan saved to: {output_file}[/bold green]")

        # Summary
        console.print("\n[bold cyan]Plan Summary:[/bold cyan]")
        if "phases" in periodization_plan:
            for phase in periodization_plan["phases"]:
                console.print(f"  • Phase {phase.get('phaseNumber')}: {phase.get('name')} "
                            f"(Weeks {phase.get('startWeek')}-{phase.get('endWeek')})")
                console.print(f"    Focus: {phase.get('focus')}")
                if phase.get('deloadWeek'):
                    console.print(f"    Deload: Week {phase.get('deloadWeek')}")
                console.print()

        return periodization_plan
    else:
        console.print("[bold red]Error: Orchestrator did not route correctly[/bold red]")
        return None


if __name__ == "__main__":
    try:
        plan = test_periodization_plan()

        if plan:
            console.print("\n[bold green]✓ Periodization plan generation successful![/bold green]")
            console.print("\nNext step: Run 'python test_block_builder.py' to create a training block")
        else:
            console.print("\n[bold red]✗ Periodization plan generation failed[/bold red]")

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
