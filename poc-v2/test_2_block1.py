"""
Test 2: Create Block 1 (Base Phase, Weeks 1-6)
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel

from agents.global_context_agent import GlobalContextAgent
from agents.skeleton_agent import SkeletonAgent
from agents.running_quality_coach import RunningQualityCoach
from agents.strength_endurance_coach import StrengthEnduranceCoach
from agents.hyrox_combo_coach import HyroxComboCoach
from agents.integration_agent import IntegrationAgent
from agents.validation_agent import ValidationAgent

load_dotenv()

console = Console()


def load_periodization_plan():
    """Load the most recent periodization plan"""
    output_dir = "output"
    files = [f for f in os.listdir(output_dir) if f.startswith("periodization_plan_")]
    if not files:
        raise FileNotFoundError("No periodization plan found. Run test_1_periodization.py first.")

    latest_file = sorted(files)[-1]
    with open(os.path.join(output_dir, latest_file), "r") as f:
        return json.load(f)


def test_block1():
    """Create Block 1 for Base phase (weeks 1-6)"""
    console.print("\n[bold cyan]Block Smith v2 - Create Block 1 (Base Phase)[/bold cyan]\n")

    # Load periodization plan
    console.print("[yellow]Loading periodization plan...[/yellow]")
    periodization_plan = load_periodization_plan()
    console.print("[green]✓ Periodization plan loaded[/green]")

    # Get Base phase (Phase 1)
    base_phase = periodization_plan["phases"][0]
    console.print(f"\n[bold]Phase: {base_phase['phaseName']}[/bold]")
    console.print(f"  Weeks: {base_phase['startWeek']}-{base_phase['endWeek']}")
    console.print(f"  Focus: {base_phase['phaseFocus']}")

    # Setup athlete profile and configuration
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
            }
        },
        "estimatedMaxes": {
            "backSquat": "140kg",
            "deadlift": "160kg",
            "benchPress": "100kg"
        }
    }

    block_configuration = {
        "sessionsPerWeek": 5,
        "availableDays": ["tuesday", "wednesday", "thursday", "saturday", "sunday"]
    }

    # Create Global Context
    global_context = GlobalContextAgent(athlete_profile, block_configuration)
    console.print("[green]✓ Global Context created[/green]")

    # Step 1: Create skeleton (weekly structure)
    console.print("\n[bold yellow]Step 1: Creating Weekly Skeleton[/bold yellow]")
    skeleton_input = {
        "blockDetails": {
            "blockNumber": 1,
            "startWeek": base_phase["startWeek"],
            "endWeek": base_phase["endWeek"],
            "durationWeeks": base_phase["durationWeeks"]
        },
        "currentPhase": base_phase,
        "trainingConfiguration": block_configuration
    }

    skeleton_agent = SkeletonAgent()
    skeleton = skeleton_agent.execute(skeleton_input)
    console.print("[green]✓ Skeleton created[/green]")

    # Step 2: Specialist coaches design workouts
    console.print("\n[bold yellow]Step 2: Specialist Coaches Designing Workouts[/bold yellow]")

    running_coach = RunningQualityCoach()
    se_coach = StrengthEnduranceCoach()
    combo_coach = HyroxComboCoach()

    # Process Week 1 as example (in production, loop through all weeks)
    week1_structure = skeleton.get("weeklyStructure", [])[0] if skeleton.get("weeklyStructure") else None

    if not week1_structure:
        console.print("[red]✗ No weekly structure found in skeleton[/red]")
        return None

    console.print(f"\n[cyan]Designing Week 1 sessions:[/cyan]")

    week1_workouts = {}
    previous_week = None  # First week has no previous

    for session in week1_structure.get("sessions", []):
        day = session["dayOfWeek"]
        session_type = session["sessionType"]

        console.print(f"  - {day.capitalize()}: {session_type}")

        # Build input for specialist coach
        coach_input = {
            "weekNumber": 1,
            "sessionFocus": session["focus"],
            "currentPhase": {
                "phaseName": base_phase["phaseName"],
                "phaseNumber": base_phase["phaseNumber"],
                "selectedArchetypes": base_phase["selectedArchetypes"],
                "archetypeSchedulingGuidance": base_phase["archetypeSchedulingGuidance"],
                "progressionGuidelines": base_phase["progressionGuidelines"]
            },
            "athleteContext": {
                "zone2HR": athlete_profile["physiologicalData"]["zone2HR"],
                "thresholdPaces": athlete_profile["physiologicalData"]["thresholdPaces"],
                "equipment": athlete_profile["equipment"]["gym"]["equipment"],
                "estimatedMaxes": athlete_profile.get("estimatedMaxes", {})
            },
            "previousWeek": previous_week
        }

        # Add station focus for SE sessions
        if session_type == "strengthEndurance":
            coach_input["stationFocus"] = ["skierg", "wall_balls", "rowing"]

        # Route to appropriate coach
        if session_type == "runningQuality":
            workout = running_coach.execute(coach_input)
        elif session_type == "strengthEndurance":
            workout = se_coach.execute(coach_input)
        elif session_type == "hyroxCombo":
            coach_input["athleteContext"]["targetRacePace"] = "5:00/km"
            coach_input["athleteContext"]["zone2Pace"] = "5:30/km"
            workout = combo_coach.execute(coach_input)
        else:
            workout = {"placeholder": f"{session_type} workout"}

        week1_workouts[day] = {
            "sessionType": session_type,
            "workout": workout
        }

    console.print("[green]✓ Week 1 workouts designed[/green]")

    # Step 3: Integration
    console.print("\n[bold yellow]Step 3: Integrating Week 1 into Complete Plan[/bold yellow]")

    integration_input = {
        "weekNumber": 1,
        "weeklyStructure": week1_workouts,
        "phaseInfo": {
            "phaseName": base_phase["phaseName"],
            "weekNumber": 1,
            "targetIntensityDistribution": base_phase["targetIntensityDistribution"]
        }
    }

    integration_agent = IntegrationAgent()
    integrated_week1 = integration_agent.execute(integration_input)
    console.print("[green]✓ Week 1 integrated[/green]")

    # Step 4: Validation
    console.print("\n[bold yellow]Step 4: Validating Training Block[/bold yellow]")

    validation_input = {
        "blockNumber": 1,
        "phaseInfo": {
            "phaseName": base_phase["phaseName"],
            "phaseNumber": base_phase["phaseNumber"],
            "targetIntensityDistribution": base_phase["targetIntensityDistribution"],
            "selectedArchetypes": base_phase["selectedArchetypes"]
        },
        "weeklyPlans": [integrated_week1],
        "athleteProfile": athlete_profile
    }

    validation_agent = ValidationAgent()
    validation_result = validation_agent.execute(validation_input)
    console.print(f"[green]✓ Validation complete: {validation_result.get('validationStatus', 'UNKNOWN')}[/green]")

    # Save outputs
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    outputs = {
        "skeleton": skeleton,
        "week1_integrated": integrated_week1,
        "validation": validation_result
    }

    output_file = f"output/block1_base_phase_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(outputs, f, indent=2)

    console.print(f"\n[bold green]✓ Block 1 saved to: {output_file}[/bold green]")

    # Display summary
    console.print("\n[bold cyan]Block 1 Summary:[/bold cyan]")
    console.print(f"  Phase: {base_phase['phaseName']}")
    console.print(f"  Duration: {base_phase['durationWeeks']} weeks")
    console.print(f"  Sessions per week: 5")
    console.print(f"  Validation: {validation_result.get('validationStatus', 'UNKNOWN')}")

    if "weeklyLoadMetrics" in integrated_week1:
        metrics = integrated_week1["weeklyLoadMetrics"]
        console.print(f"\n  Week 1 Metrics:")
        console.print(f"    Total time: {metrics.get('totalTrainingMinutes', 0)} minutes")
        console.print(f"    Rest days: {metrics.get('restDays', 0)}")

    return outputs


if __name__ == "__main__":
    try:
        result = test_block1()

        if result:
            console.print("\n[bold green]✓ Block 1 (Base Phase) creation successful![/bold green]")
            console.print("\n[bold cyan]Key Achievements:[/bold cyan]")
            console.print("  1. Skeleton created weekly structure")
            console.print("  2. Specialist coaches designed phase-appropriate workouts")
            console.print("  3. Integration agent assembled complete weekly plan")
            console.print("  4. Validation agent checked safety and effectiveness")
            console.print("\nNext: Run test_3_block2.py to create Build phase block with progression")
        else:
            console.print("\n[bold red]✗ Block 1 creation failed[/bold red]")

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
