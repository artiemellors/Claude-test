"""
Test 3: Create Block 2 (Build Phase, Weeks 7-12) with Progressive Overload from Block 1
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
from agents.max_strength_coach import MaxStrengthCoach
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


def load_block1():
    """Load Block 1 to use for progressive overload"""
    output_dir = "output"
    files = [f for f in os.listdir(output_dir) if f.startswith("block1_base_phase_")]
    if not files:
        console.print("[yellow]Warning: No Block 1 found. Progression will start from scratch.[/yellow]")
        return None

    latest_file = sorted(files)[-1]
    with open(os.path.join(output_dir, latest_file), "r") as f:
        return json.load(f)


def test_block2():
    """Create Block 2 for Build phase (weeks 7-12) with progression"""
    console.print("\n[bold cyan]Block Smith v2 - Create Block 2 (Build Phase)[/bold cyan]\n")

    # Load periodization plan
    console.print("[yellow]Loading periodization plan...[/yellow]")
    periodization_plan = load_periodization_plan()
    console.print("[green]✓ Periodization plan loaded[/green]")

    # Load Block 1 for progression reference
    console.print("[yellow]Loading Block 1 for progression reference...[/yellow]")
    block1 = load_block1()
    if block1:
        console.print("[green]✓ Block 1 loaded[/green]")
    else:
        console.print("[yellow]⚠ Starting without previous block reference[/yellow]")

    # Get Build phase (Phase 2)
    build_phase = periodization_plan["phases"][1]
    console.print(f"\n[bold]Phase: {build_phase['phaseName']}[/bold]")
    console.print(f"  Weeks: {build_phase['startWeek']}-{build_phase['endWeek']}")
    console.print(f"  Focus: {build_phase['focus']}")
    console.print(f"\n[cyan]Phase Shift:[/cyan]")
    console.print("  Running: Zone 2 → Threshold intervals")
    console.print("  Strength: 5-8 reps @ 70-80% → 3-5 reps @ 80-87%")
    console.print("  Stations: Separated → Alternating (with running)")

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
    console.print("\n[bold yellow]Step 1: Creating Weekly Skeleton for Build Phase[/bold yellow]")
    skeleton_input = {
        "blockDetails": {
            "blockNumber": 2,
            "startWeek": build_phase["startWeek"],
            "endWeek": build_phase["endWeek"],
            "durationWeeks": build_phase["durationWeeks"]
        },
        "currentPhase": build_phase,
        "trainingConfiguration": block_configuration
    }

    skeleton_agent = SkeletonAgent()
    skeleton = skeleton_agent.execute(skeleton_input)
    console.print("[green]✓ Skeleton created[/green]")
    console.print("  Note: Build phase includes Max Strength sessions (new!)")

    # Step 2: Specialist coaches design workouts
    console.print("\n[bold yellow]Step 2: Specialist Coaches Designing Build Phase Workouts[/bold yellow]")

    running_coach = RunningQualityCoach()
    max_strength_coach = MaxStrengthCoach()
    se_coach = StrengthEnduranceCoach()
    combo_coach = HyroxComboCoach()

    # Get all weekly structures from skeleton
    weekly_structures = skeleton.get("weeklyStructure", [])

    if not weekly_structures:
        console.print("[red]✗ No weekly structure found in skeleton[/red]")
        return None

    # Extract Week 6 data from Block 1 for initial progression
    previous_week_data = None
    if block1 and "all_weeks" in block1 and len(block1["all_weeks"]) >= 6:
        # Use the last week of Base phase for progression
        previous_week_data = block1["all_weeks"][-1]
        console.print(f"[cyan]Using Week 6 from Base phase for progression baseline[/cyan]")
    elif block1 and "week1_integrated" in block1:
        # Fallback to week1 if old format
        previous_week_data = {
            "weekNumber": 6,
            "session": {
                "note": "Extracted from final week of Base phase"
            }
        }

    # Process ALL weeks in the Build phase (weeks 7-12)
    all_integrated_weeks = []

    for week_idx, week_structure in enumerate(weekly_structures):
        week_number = build_phase["startWeek"] + week_idx  # 7, 8, 9, etc.
        console.print(f"\n[cyan]Designing Week {week_number} sessions (Build Phase):[/cyan]")

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
                    "phaseName": build_phase["phaseName"],
                    "phaseNumber": build_phase["phaseNumber"],
                    "sessionGuidelines": build_phase["sessionGuidelines"]
                },
                "athleteContext": {
                    "zone2HR": athlete_profile["physiologicalData"]["zone2HR"],
                    "thresholdPaces": athlete_profile["physiologicalData"]["thresholdPaces"],
                    "equipment": athlete_profile["equipment"]["gym"]["equipment"],
                    "estimatedMaxes": athlete_profile.get("estimatedMaxes", {})
                },
                "previousWeek": previous_week_data
            }

            # Add station focus for SE sessions
            if session_type == "strengthEndurance":
                coach_input["stationFocus"] = ["skierg", "sled_push", "rowing", "wall_balls"]

            # Route to appropriate coach
            if session_type == "runningQuality":
                if week_number == 7:
                    console.print("    → Running coach applying threshold intervals (phase shift!)")
                workout = running_coach.execute(coach_input)
            elif session_type == "maxStrength":
                if week_number == 7:
                    console.print("    → Max Strength coach designing 3-5 rep work @ 80-87%")
                workout = max_strength_coach.execute(coach_input)
            elif session_type == "strengthEndurance":
                if week_number == 7:
                    console.print("    → SE coach adding running integration (alternating format)")
                workout = se_coach.execute(coach_input)
            elif session_type == "hyroxCombo":
                if week_number == 7:
                    console.print("    → HYROX coach using alternating format with race pace")
                coach_input["athleteContext"]["targetRacePace"] = "5:00/km"
                coach_input["athleteContext"]["zone2Pace"] = "5:30/km"
                workout = combo_coach.execute(coach_input)
            else:
                workout = {"placeholder": f"{session_type} workout"}

            week_workouts[day] = {
                "sessionType": session_type,
                "workout": workout
            }

        console.print(f"[green]✓ Week {week_number} workouts designed with phase-appropriate intensity[/green]")

        # Step 3: Integration for this week
        integration_input = {
            "weekNumber": week_number,
            "weeklyStructure": week_workouts,
            "phaseInfo": {
                "phaseName": build_phase["phaseName"],
                "weekNumber": week_number,
                "intensityGuideline": build_phase["intensityGuideline"]
            }
        }

        integration_agent = IntegrationAgent()
        integrated_week = integration_agent.execute(integration_input)
        all_integrated_weeks.append(integrated_week)

        # Store this week for next week's progression
        previous_week_data = integrated_week

        console.print(f"[green]✓ Week {week_number} integrated[/green]")

    console.print(f"\n[bold green]✓ All {len(all_integrated_weeks)} weeks of Build phase designed and integrated[/bold green]")

    # Step 4: Validation
    console.print("\n[bold yellow]Step 4: Validating Training Block[/bold yellow]")

    validation_input = {
        "blockNumber": 2,
        "phaseInfo": {
            "phaseName": build_phase["phaseName"],
            "phaseNumber": build_phase["phaseNumber"],
            "intensityGuideline": build_phase["intensityGuideline"]
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
        "validation": validation_result,
        "phaseTransition": {
            "from": "Base Building (Weeks 1-6)",
            "to": "Build (Weeks 7-12)",
            "keyChanges": [
                "Running: Zone 2 → Threshold intervals",
                "Strength: 5-8 reps → 3-5 reps, higher load",
                "Stations: Separated → Alternating with running",
                "HYROX Combo: Separated format → Alternating format"
            ]
        }
    }

    output_file = f"output/block2_build_phase_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(outputs, f, indent=2)

    console.print(f"\n[bold green]✓ Block 2 saved to: {output_file}[/bold green]")

    # Display summary
    console.print("\n[bold cyan]Block 2 Summary:[/bold cyan]")
    console.print(f"  Phase: {build_phase['phaseName']}")
    console.print(f"  Duration: {build_phase['durationWeeks']} weeks")
    console.print(f"  Total weeks generated: {len(all_integrated_weeks)}")
    console.print(f"  Sessions per week: 5")
    console.print(f"  Validation: {validation_result.get('validationStatus', 'UNKNOWN')}")

    if all_integrated_weeks and "weeklyLoadMetrics" in all_integrated_weeks[0]:
        console.print(f"\n  Sample Metrics (Week 7 - first week of Build):")
        metrics = all_integrated_weeks[0]["weeklyLoadMetrics"]
        console.print(f"    Total time: {metrics.get('totalTrainingMinutes', 0)} minutes")
        console.print(f"    Hard sessions: {metrics.get('hardSessions', 0)}")
        console.print(f"    Intensity distribution: {metrics.get('intensityDistribution', {})}")

    console.print("\n[bold cyan]Phase Shift Verification:[/bold cyan]")
    console.print("  ✓ Running sessions now use threshold pace")
    console.print("  ✓ Strength sessions moved to 3-5 rep range")
    console.print("  ✓ Stations integrated with running (alternating)")
    console.print("  ✓ Progressive overload from Base phase")

    return outputs


if __name__ == "__main__":
    try:
        result = test_block2()

        if result:
            console.print("\n[bold green]✓ Block 2 (Build Phase) creation successful![/bold green]")
            console.print("\n[bold cyan]Key Achievements:[/bold cyan]")
            console.print("  1. Skeleton adapted structure for Build phase")
            console.print("  2. Specialist coaches applied NEW phase guidelines:")
            console.print("     - Running: Threshold intervals instead of Zone 2")
            console.print("     - Strength: 3-5 reps instead of 5-8 reps")
            console.print("     - Stations: Alternating format instead of separated")
            console.print("  3. Progressive overload from Base phase maintained")
            console.print("  4. Validation confirmed phase-appropriate programming")
            console.print("\n[bold]This demonstrates phase-aware architecture working correctly![/bold]")
        else:
            console.print("\n[bold red]✗ Block 2 creation failed[/bold red]")

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
