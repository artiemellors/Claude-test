"""
Test script for Training Block generation
Simple version without LangGraph - orchestrates agents sequentially
"""
import os
import json
import glob
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from agents.hyrox_block_builder import HyroxBlockBuilderAgent
from agents.aerobic_base_coach import AerobicBaseCoach
from agents.strength_endurance_coach import StrengthEnduranceCoach

# Load environment variables
load_dotenv()

console = Console()


def load_latest_periodization_plan():
    """Load the most recent periodization plan"""
    plan_files = glob.glob("poc/output/periodization_plan_*.json")

    if not plan_files:
        console.print("[bold red]No periodization plan found![/bold red]")
        console.print("Please run 'python test_periodization.py' first")
        return None

    latest_file = max(plan_files, key=os.path.getctime)
    console.print(f"[dim]Loading plan from: {latest_file}[/dim]\n")

    with open(latest_file, "r") as f:
        return json.load(f)


def test_training_block():
    """
    Test the training block generation workflow
    """
    console.print("\n[bold cyan]Block Smith - Training Block Builder PoC[/bold cyan]\n")

    # Load periodization plan
    periodization_plan = load_latest_periodization_plan()
    if not periodization_plan:
        return None

    # For this test, we'll create Block 1 (Base Phase)
    first_phase = periodization_plan.get("phases", [])[0]

    block_input = {
        "currentPhase": first_phase,
        "blockDetails": {
            "blockNumber": 1,
            "startWeek": first_phase.get("startWeek"),
            "endWeek": first_phase.get("endWeek"),
            "durationWeeks": first_phase.get("durationWeeks"),
            "deloadWeek": first_phase.get("deloadWeek")
        },
        "trainingDaysPerWeek": periodization_plan.get("trainingDaysPerWeek", 5),
        "previousBlock": None
    }

    console.print(Panel(JSON(json.dumps(block_input, indent=2)), title="Block Input"))

    # Step 1: Hyrox Block Builder
    console.print("\n[bold yellow]Step 1: Hyrox Block Builder[/bold yellow]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing phase and creating block structure...", total=None)

        block_builder = HyroxBlockBuilderAgent()
        block_structure = block_builder.execute(block_input)

        progress.stop()

    console.print(Panel(
        JSON(json.dumps(block_structure, indent=2)),
        title="Block Structure",
        border_style="green"
    ))

    # Step 2: Call Modality Coaches
    coach_outputs = {}

    # Aerobic Base Coach
    if "aerobic_base_coach" in block_structure.get("coachRequirements", {}):
        console.print("\n[bold yellow]Step 2a: Aerobic Base Coach[/bold yellow]")

        aerobic_input = block_structure["coachRequirements"]["aerobic_base_coach"]
        aerobic_input["currentFitnessLevel"] = "intermediate"

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating aerobic running workouts...", total=None)

            aerobic_coach = AerobicBaseCoach()
            aerobic_workouts = aerobic_coach.execute(aerobic_input)

            progress.stop()

        console.print(Panel(
            JSON(json.dumps(aerobic_workouts, indent=2)),
            title="Aerobic Base Workouts",
            border_style="blue"
        ))

        coach_outputs["aerobic_base_coach"] = aerobic_workouts

    # Strength Endurance Coach
    if "strength_endurance_coach" in block_structure.get("coachRequirements", {}):
        console.print("\n[bold yellow]Step 2b: Strength Endurance Coach[/bold yellow]")

        strength_input = block_structure["coachRequirements"]["strength_endurance_coach"]
        strength_input["phaseGoal"] = first_phase.get("focus")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating strength-endurance workouts...", total=None)

            strength_coach = StrengthEnduranceCoach()
            strength_workouts = strength_coach.execute(strength_input)

            progress.stop()

        console.print(Panel(
            JSON(json.dumps(strength_workouts, indent=2)),
            title="Strength Endurance Workouts",
            border_style="magenta"
        ))

        coach_outputs["strength_endurance_coach"] = strength_workouts

    # Step 3: Combine into final training block
    console.print("\n[bold yellow]Step 3: Integration (Manual for PoC)[/bold yellow]")

    final_block = {
        "blockNumber": 1,
        "phaseInfo": block_structure.get("phaseInfo"),
        "totalWeeks": block_structure.get("totalWeeks"),
        "weeklyStructure": block_structure.get("weeklyStructure"),
        "coachOutputs": coach_outputs,
        "deloadWeek": block_structure.get("deloadWeek")
    }

    # Save to file
    output_file = f"poc/output/training_block_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(final_block, f, indent=2)

    console.print(f"\n[bold green]✓ Training block saved to: {output_file}[/bold green]")

    # Summary
    console.print("\n[bold cyan]Training Block Summary:[/bold cyan]")
    console.print(f"  • Block Number: {final_block['blockNumber']}")
    console.print(f"  • Phase: {final_block['phaseInfo'].get('name')}")
    console.print(f"  • Duration: {final_block['totalWeeks']} weeks")
    console.print(f"  • Weekly Structure: {final_block['weeklyStructure']}")

    if "aerobic_base_coach" in coach_outputs:
        console.print(f"\n  • Aerobic Workouts: {len(coach_outputs['aerobic_base_coach'].get('workouts', []))} total")

    if "strength_endurance_coach" in coach_outputs:
        console.print(f"  • Strength Workouts: {len(coach_outputs['strength_endurance_coach'].get('workouts', []))} total")

    return final_block


if __name__ == "__main__":
    try:
        block = test_training_block()

        if block:
            console.print("\n[bold green]✓ Training block generation successful![/bold green]")
            console.print("\n[bold cyan]Next steps:[/bold cyan]")
            console.print("  1. Review the generated workouts in poc/output/")
            console.print("  2. Evaluate quality and adjust agent prompts if needed")
            console.print("  3. Test with different fitness levels and phases")
        else:
            console.print("\n[bold red]✗ Training block generation failed[/bold red]")

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
