"""
Test 1: Create Phase-Aware Periodization Plan
"""
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel

from agents.global_context_agent import GlobalContextAgent
from agents.hyrox_periodization_agent import HyroxPeriodizationAgent

load_dotenv()

console = Console()


def test_periodization():
    """Create a phase-aware periodization plan"""
    console.print("\n[bold cyan]Block Smith v2 - Phase-Aware Periodization Plan[/bold cyan]\n")

    # User input
    race_date = (datetime.now() + timedelta(weeks=18)).strftime("%Y-%m-%d")

    athlete_profile = {
        "age": 41,
        "currentFitnessLevel": "intermediate",
        "physiologicalData": {
            "hrMax": 188,
            "zone2HR": {"low": 113, "high": 131},
            "thresholdPaces": {
                "T1": "4:37/km",
                "T2": "4:17/km"
            }
        },
        "equipment": {
            "gym": {
                "available": True,
                "equipment": ["barbell", "dumbbells", "skierg", "rower", "sleds", "wall_balls", "sandbags"]
            },
            "home": {
                "available": True,
                "equipment": ["exercise_bike", "wall_ball", "kettlebells", "sandbag"]
            }
        }
    }

    block_configuration = {
        "sessionsPerWeek": 5,
        "availableDays": ["tuesday", "wednesday", "thursday", "saturday", "sunday"]
    }

    user_input = {
        "raceType": "hyrox",
        "raceDate": race_date,
        "currentFitness": "intermediate",
        "trainingDaysPerWeek": 5,
        "athleteProfile": athlete_profile
    }

    console.print(Panel(JSON(json.dumps(user_input, indent=2)), title="User Input"))

    # Create Global Context
    console.print("\n[bold yellow]Creating Global Context[/bold yellow]")
    global_context = GlobalContextAgent(athlete_profile, block_configuration)
    context = global_context.get_context()

    console.print("[green]✓ Global Context created[/green]")
    console.print(f"  HR Zones calculated: {list(context['calculatedZones'].keys())}")

    # Create Periodization Plan
    console.print("\n[bold yellow]Creating Hyrox Periodization Plan[/bold yellow]")

    periodization_agent = HyroxPeriodizationAgent()
    periodization_plan = periodization_agent.execute(user_input)

    console.print(Panel(
        JSON(json.dumps(periodization_plan, indent=2)),
        title="Periodization Plan with Session Guidelines",
        border_style="green"
    ))

    # Save to file
    output_file = f"output/periodization_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("output", exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(periodization_plan, f, indent=2)

    console.print(f"\n[bold green]✓ Plan saved to: {output_file}[/bold green]")

    # Summary
    console.print("\n[bold cyan]Plan Summary:[/bold cyan]")
    if "phases" in periodization_plan:
        for phase in periodization_plan["phases"]:
            console.print(f"\n  [bold]Phase {phase.get('phaseNumber')}: {phase.get('phaseName')}[/bold]")
            console.print(f"    Weeks: {phase.get('startWeek')}-{phase.get('endWeek')}")
            console.print(f"    Focus: {phase.get('phaseFocus', 'N/A')}")
            console.print(f"    Progression: {phase.get('primaryProgressionFocus', 'N/A')}")

            if "selectedArchetypes" in phase:
                console.print(f"    Selected Archetypes ({len(phase['selectedArchetypes'])} total):")
                for archetype in phase["selectedArchetypes"]:
                    console.print(f"      - {archetype.get('archetypeName')} ({archetype.get('sessionRole', 'N/A')}): {archetype.get('frequency', 'N/A')}")

    return periodization_plan, global_context


if __name__ == "__main__":
    try:
        plan, context = test_periodization()

        if plan and "phases" in plan:
            console.print("\n[bold green]✓ Phase-aware periodization plan generation successful![/bold green]")
            console.print("\n[bold cyan]Key Achievement:[/bold cyan]")
            console.print("  Each phase now has detailed session guidelines that will")
            console.print("  direct specialist coaches on HOW to design sessions.")
            console.print("\nNext: Run test_2_block1.py to create Base phase training block")
        else:
            console.print("\n[bold red]✗ Periodization plan generation failed[/bold red]")

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
