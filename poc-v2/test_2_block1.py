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

    training_config = {
        "sessionsPerWeek": 5,
        "availableDays": ["tuesday", "wednesday", "thursday", "saturday", "sunday"]
    }

    # Create Global Context with periodization plan as single source of truth
    global_context = GlobalContextAgent(athlete_profile, training_config, periodization_plan)
    console.print("[green]✓ Global Context created with periodization plan[/green]")

    # Step 1: Create skeleton (weekly structure)
    console.print("\n[bold yellow]Step 1: Creating Weekly Skeleton[/bold yellow]")

    # Skeleton Agent queries GlobalContext for what it needs
    skeleton_input = {
        "blockDetails": {
            "blockNumber": 1,
            "startWeek": base_phase["startWeek"],
            "endWeek": base_phase["endWeek"],
            "durationWeeks": base_phase["durationWeeks"]
        },
        "currentPhase": base_phase,  # Still pass phase for now (can optimize later)
        "trainingConfig": {
            "sessionsPerWeek": global_context.get_sessions_per_week(),
            "availableDays": global_context.get_available_days()
        }
    }

    skeleton_agent = SkeletonAgent()
    skeleton = skeleton_agent.execute(skeleton_input)
    console.print("[green]✓ Skeleton created[/green]")

    # Step 2: Specialist coaches design workouts
    console.print("\n[bold yellow]Step 2: Specialist Coaches Designing Workouts[/bold yellow]")

    running_coach = RunningQualityCoach()
    se_coach = StrengthEnduranceCoach()
    combo_coach = HyroxComboCoach()

    # Get all weekly structures from skeleton
    weekly_structures = skeleton.get("weeklyStructure", [])

    if not weekly_structures:
        console.print("[red]✗ No weekly structure found in skeleton[/red]")
        return None

    # Process ALL weeks in the block (Base phase: weeks 1-6)
    all_integrated_weeks = []
    previous_week = None

    for week_idx, week_structure in enumerate(weekly_structures):
        week_number = week_idx + 1
        console.print(f"\n[cyan]Designing Week {week_number} sessions:[/cyan]")

        week_workouts = {}

        for session in week_structure.get("sessions", []):
            day = session["dayOfWeek"]
            session_type = session["sessionType"]

            console.print(f"  - {day.capitalize()}: {session_type}")

            # Build input for specialist coach
            coach_input = {
                "weekNumber": week_number,
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

            week_workouts[day] = {
                "sessionType": session_type,
                "workout": workout
            }

        console.print(f"[green]✓ Week {week_number} workouts designed[/green]")

        # Step 3: Integration for this week
        integration_input = {
            "weekNumber": week_number,
            "weeklyStructure": week_workouts,
            "phaseInfo": {
                "phaseName": base_phase["phaseName"],
                "weekNumber": week_number,
                "targetIntensityDistribution": base_phase["targetIntensityDistribution"]
            }
        }

        integration_agent = IntegrationAgent()
        integrated_week = integration_agent.execute(integration_input)
        all_integrated_weeks.append(integrated_week)

        # Store this week for next week's progression
        previous_week = integrated_week

        console.print(f"[green]✓ Week {week_number} integrated[/green]")

    console.print(f"\n[bold green]✓ All {len(all_integrated_weeks)} weeks designed and integrated[/bold green]")

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
        "weeklyPlans": all_integrated_weeks,
        "athleteProfile": athlete_profile
    }

    validation_agent = ValidationAgent()
    validation_result = validation_agent.execute(validation_input)
    console.print(f"[green]✓ Validation complete: {validation_result.get('validationStatus', 'UNKNOWN')}[/green]")

    # Save outputs
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    outputs = {
        "skeleton": skeleton,
        "all_weeks": all_integrated_weeks,
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
    console.print(f"  Total weeks generated: {len(all_integrated_weeks)}")
    console.print(f"  Sessions per week: 5")
    console.print(f"  Validation: {validation_result.get('validationStatus', 'UNKNOWN')}")

    if all_integrated_weeks and "weeklyLoadMetrics" in all_integrated_weeks[0]:
        console.print(f"\n  Sample Metrics (Week 1):")
        metrics = all_integrated_weeks[0]["weeklyLoadMetrics"]
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
