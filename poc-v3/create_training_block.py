"""
Hyrox Training Block Builder - Main Orchestrator
Goal-driven agentic system for creating complete training blocks
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, List

# For nice terminal output (optional - will work without these)
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich.json import JSON
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    print("Note: Install 'rich' for better output formatting: pip install rich")

from agents.block_strategist import BlockStrategistAgent
from agents.week_orchestrator import WeekOrchestratorAgent
from agents.week_assembler import WeekAssembler
from agents.block_validator import BlockValidatorAgent
from agents.running_coach import RunningCoach
from agents.strength_coach import StrengthCoach
from agents.strength_endurance_coach import StrengthEnduranceCoach
from agents.hyrox_combo_coach import HyroxComboCoach


class TrainingBlockBuilder:
    """Orchestrates the agentic system to create complete training blocks"""

    def __init__(self):
        self.console = Console() if HAS_RICH else None

        # Initialize agents
        self.block_strategist = BlockStrategistAgent()
        self.week_orchestrator = WeekOrchestratorAgent()
        self.week_assembler = WeekAssembler()
        self.block_validator = BlockValidatorAgent()

        # Initialize specialist coaches
        self.coaches = {
            "running_quality_coach": RunningCoach(),
            "max_strength_coach": StrengthCoach(),
            "strength_endurance_coach": StrengthEnduranceCoach(),
            "hyrox_combo_coach": HyroxComboCoach()
        }

    def _print(self, message: str, style: str = ""):
        """Print with or without rich formatting"""
        if self.console:
            self.console.print(message, style=style)
        else:
            print(message)

    def create_block(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration method - creates complete training block

        Args:
            user_input: User-provided data (athlete info, goals, constraints)

        Returns:
            Complete training block with all weeks and validation
        """
        self._print("\n[bold cyan]Hyrox Training Block Builder - v3 (Goal-Driven)[/bold cyan]\n")
        self._print("Starting agentic training block creation...\n")

        # STEP 1: Block Strategy
        self._print("[bold yellow]Step 1: Creating Block Strategy[/bold yellow]")
        self._print("  Agent: Block Strategist")
        self._print("  Task: Analyze athlete and create progression plan\n")

        block_strategy = self.block_strategist.execute(user_input)

        if "error" in block_strategy:
            self._print(f"[bold red]Error in Block Strategist: {block_strategy['error']}[/bold red]")
            return {"error": "Block strategy creation failed", "details": block_strategy}

        self._print("[green]✓ Block strategy created[/green]")
        self._print(f"  Total weeks: {block_strategy.get('blockMetadata', {}).get('totalWeeks', '?')}")
        self._print(f"  Block goal: {block_strategy.get('blockMetadata', {}).get('blockGoal', '?')}\n")

        # STEP 2: Create weeks iteratively
        self._print("[bold yellow]Step 2: Creating Weekly Plans[/bold yellow]")
        self._print("  Agent: Week Orchestrator + Specialist Coaches")
        self._print("  Task: Design detailed sessions for each week\n")

        weekly_plans = []
        previous_week = None

        total_weeks = len(block_strategy.get("weeklyFramework", []))

        for week_index, week_strategy in enumerate(block_strategy.get("weeklyFramework", []), 1):
            self._print(f"  [cyan]Week {week_index}/{total_weeks}[/cyan]")

            # Create week structure
            week_plan = self._create_week(
                week_strategy=week_strategy,
                user_input=user_input,
                previous_week=previous_week
            )

            if "error" in week_plan:
                self._print(f"    [red]✗ Failed: {week_plan['error']}[/red]")
                return {"error": f"Week {week_index} creation failed", "details": week_plan}

            weekly_plans.append(week_plan)
            previous_week = week_plan
            self._print(f"    [green]✓ Week {week_index} complete ({week_plan['weekMetrics']['totalSessions']} sessions)[/green]")

        self._print(f"\n[green]✓ All {total_weeks} weeks created[/green]\n")

        # STEP 3: Validate complete block
        self._print("[bold yellow]Step 3: Validating Training Block[/bold yellow]")
        self._print("  Agent: Block Validator")
        self._print("  Task: Safety and quality check\n")

        validation_input = {
            "blockMetadata": block_strategy.get("blockMetadata", {}),
            "athleteData": user_input.get("athleteData", {}),
            "weeklyPlans": weekly_plans
        }

        validation_result = self.block_validator.execute(validation_input)

        if "error" in validation_result:
            self._print(f"[yellow]⚠ Validation had issues: {validation_result['error']}[/yellow]")
        else:
            status = validation_result.get("validationStatus", "UNKNOWN")
            if status == "APPROVED":
                self._print(f"[bold green]✓ Block APPROVED[/bold green]")
            elif status == "APPROVED_WITH_NOTES":
                self._print(f"[bold yellow]✓ Block APPROVED WITH NOTES[/bold yellow]")
            else:
                self._print(f"[bold red]⚠ Block NEEDS REVISION[/bold red]")

        self._print()

        # STEP 4: Package final result
        complete_block = {
            "metadata": {
                "createdAt": datetime.now().isoformat(),
                "version": "v3-goal-driven",
                "totalWeeks": total_weeks
            },
            "blockStrategy": block_strategy,
            "weeklyPlans": weekly_plans,
            "validation": validation_result
        }

        # Save to file
        output_file = self._save_block(complete_block, user_input)
        self._print(f"[bold green]✓ Complete training block saved to: {output_file}[/bold green]\n")

        # Display summary
        self._display_summary(complete_block)

        return complete_block

    def _create_week(
        self,
        week_strategy: Dict[str, Any],
        user_input: Dict[str, Any],
        previous_week: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a single week's training plan"""

        week_number = week_strategy.get("weekNumber")

        # Prepare input for Week Orchestrator
        orchestrator_input = {
            "weekNumber": week_number,
            "weekStrategy": week_strategy,
            "availableDays": user_input.get("availableDays", []),
            "preferredRestDays": user_input.get("preferredRestDays", []),
            "athleteData": user_input.get("athleteData", {}),
            "previousWeek": previous_week
        }

        # Get session schedule from orchestrator
        session_schedule = self.week_orchestrator.execute(orchestrator_input)

        if "error" in session_schedule:
            return {"error": "Week orchestration failed", "details": session_schedule}

        # Design each session with specialist coaches
        designed_sessions = []

        for session in session_schedule.get("sessionSchedule", []):
            coach_name = session.get("coachAssigned")
            coach = self.coaches.get(coach_name)

            if not coach:
                return {"error": f"Unknown coach: {coach_name}", "session": session}

            # Prepare input for specialist coach
            coach_input = {
                "weekNumber": week_number,
                "dayOfWeek": session.get("dayOfWeek"),
                "sessionGoal": session.get("sessionGoal"),
                "sessionConstraints": session.get("sessionConstraints", {}),
                "progressionContext": session.get("progressionContext"),
                "athleteData": user_input.get("athleteData", {}),
                "previousWeek": previous_week
            }

            # Get workout design from coach
            workout_design = coach.execute(coach_input)

            if "error" in workout_design:
                return {"error": f"Coach {coach_name} failed", "details": workout_design}

            # Combine session metadata with workout design
            complete_session = {
                **session,
                "workout": workout_design.get("workout", workout_design)
            }

            designed_sessions.append(complete_session)

        # Assemble complete week
        complete_week = self.week_assembler.assemble(
            week_number=week_number,
            sessions=designed_sessions,
            week_strategy=week_strategy
        )

        return complete_week

    def _save_block(self, block: Dict[str, Any], user_input: Dict[str, Any]) -> str:
        """Save training block to file"""
        os.makedirs("output", exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        goal = user_input.get("blockGoal", "training")
        goal_slug = goal.lower().replace(" ", "_")[:30]

        filename = f"output/training_block_{goal_slug}_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(block, f, indent=2)

        return filename

    def _display_summary(self, block: Dict[str, Any]):
        """Display block summary"""
        self._print("[bold cyan]Training Block Summary[/bold cyan]\n")

        strategy = block.get("blockStrategy", {})
        metadata = strategy.get("blockMetadata", {})
        validation = block.get("validation", {})

        self._print(f"  [bold]Goal:[/bold] {metadata.get('blockGoal', 'N/A')}")
        self._print(f"  [bold]Phase:[/bold] {metadata.get('blockPhase', 'N/A')}")
        self._print(f"  [bold]Duration:[/bold] {metadata.get('totalWeeks', '?')} weeks")
        self._print(f"  [bold]Sessions/Week:[/bold] {metadata.get('sessionsPerWeek', '?')}")
        self._print(f"  [bold]Validation:[/bold] {validation.get('validationStatus', 'N/A')}\n")

        # Week-by-week overview
        self._print("[bold]Week-by-Week Overview:[/bold]")
        for week_plan in block.get("weeklyPlans", []):
            week_num = week_plan.get("weekNumber")
            week_strat = week_plan.get("weekStrategy", {})
            metrics = week_plan.get("weekMetrics", {})

            focus = week_strat.get("trainingFocus", "N/A")
            sessions = metrics.get("totalSessions", 0)
            duration = metrics.get("totalDurationMinutes", 0)

            self._print(f"  Week {week_num}: {focus} ({sessions} sessions, ~{duration}min)")

        self._print()


def main():
    """Example usage"""

    # Example user input
    user_input = {
        "athleteData": {
            "age": 41,
            "fitnessLevel": "intermediate",
            "hrMax": 188,
            "zone2HR": {"low": 113, "high": 131},
            "thresholdPaces": {
                "T1": "4:37/km",
                "T2": "4:17/km"
            },
            "estimatedMaxes": {
                "backSquat": "140kg",
                "deadlift": "160kg",
                "benchPress": "100kg"
            },
            "equipment": ["barbell", "dumbbells", "skierg", "rower", "sleds", "wall_balls", "sandbags"]
        },
        "raceDate": "2026-05-15",
        "blockGoal": "Build aerobic base and Hyrox station proficiency for first half of training cycle",
        "weeksInBlock": 6,
        "trainingDaysPerWeek": 5,
        "sessionsPerWeek": 5,
        "availableDays": ["tuesday", "wednesday", "thursday", "saturday", "sunday"],
        "preferredRestDays": ["monday", "friday"]
    }

    # Create the builder and generate block
    builder = TrainingBlockBuilder()
    training_block = builder.create_block(user_input)

    if "error" not in training_block:
        print("\n✓ Training block created successfully!")
    else:
        print(f"\n✗ Error creating training block: {training_block.get('error')}")


if __name__ == "__main__":
    main()
