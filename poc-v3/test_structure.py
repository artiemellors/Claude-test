"""
Test script to verify agent structure without making API calls
"""
import sys

def test_imports():
    """Test that all agent modules can be imported"""
    print("Testing agent imports...")

    try:
        from agents.block_strategist import BlockStrategistAgent
        print("  ✓ BlockStrategistAgent")
    except Exception as e:
        print(f"  ✗ BlockStrategistAgent: {e}")
        return False

    try:
        from agents.week_orchestrator import WeekOrchestratorAgent
        print("  ✓ WeekOrchestratorAgent")
    except Exception as e:
        print(f"  ✗ WeekOrchestratorAgent: {e}")
        return False

    try:
        from agents.week_assembler import WeekAssembler
        print("  ✓ WeekAssembler")
    except Exception as e:
        print(f"  ✗ WeekAssembler: {e}")
        return False

    try:
        from agents.block_validator import BlockValidatorAgent
        print("  ✓ BlockValidatorAgent")
    except Exception as e:
        print(f"  ✗ BlockValidatorAgent: {e}")
        return False

    try:
        from agents.running_coach import RunningCoach
        print("  ✓ RunningCoach")
    except Exception as e:
        print(f"  ✗ RunningCoach: {e}")
        return False

    try:
        from agents.strength_coach import StrengthCoach
        print("  ✓ StrengthCoach")
    except Exception as e:
        print(f"  ✗ StrengthCoach: {e}")
        return False

    try:
        from agents.strength_endurance_coach import StrengthEnduranceCoach
        print("  ✓ StrengthEnduranceCoach")
    except Exception as e:
        print(f"  ✗ StrengthEnduranceCoach: {e}")
        return False

    try:
        from agents.hyrox_combo_coach import HyroxComboCoach
        print("  ✓ HyroxComboCoach")
    except Exception as e:
        print(f"  ✗ HyroxComboCoach: {e}")
        return False

    print("\n✓ All agent imports successful!\n")
    return True


def test_week_assembler():
    """Test WeekAssembler functionality (no API needed)"""
    print("Testing WeekAssembler (non-LLM agent)...")

    from agents.week_assembler import WeekAssembler

    assembler = WeekAssembler()

    # Mock session data
    mock_sessions = [
        {
            "dayOfWeek": "tuesday",
            "sessionType": "runningQuality",
            "workout": {
                "totalDuration": "45min"
            }
        },
        {
            "dayOfWeek": "saturday",
            "sessionType": "maxStrength",
            "workout": {
                "totalDuration": "70min"
            }
        }
    ]

    mock_week_strategy = {
        "weekObjectives": ["Test objective"],
        "trainingFocus": "Test focus"
    }

    result = assembler.assemble(
        week_number=1,
        sessions=mock_sessions,
        week_strategy=mock_week_strategy
    )

    # Verify structure
    assert result["weekNumber"] == 1
    assert len(result["sessions"]) == 2
    assert result["weekMetrics"]["totalSessions"] == 2
    assert "tuesday" in [s["dayOfWeek"] for s in result["sessions"]]

    print("  ✓ WeekAssembler.assemble() works correctly")
    print(f"  ✓ Calculated total duration: {result['weekMetrics']['totalDurationMinutes']}min")
    print(f"  ✓ Identified rest days: {result['weekMetrics']['restDays']}")

    print("\n✓ WeekAssembler functional test passed!\n")
    return True


def show_agent_system_overview():
    """Display the agent system structure"""
    print("=" * 60)
    print("HYROX TRAINING BLOCK BUILDER - AGENT SYSTEM")
    print("=" * 60)
    print()
    print("AGENT ARCHITECTURE:")
    print()
    print("1. BlockStrategistAgent")
    print("   Role: Analyzes athlete, creates progression strategy")
    print("   Type: LLM Agent")
    print()
    print("2. WeekOrchestratorAgent")
    print("   Role: Creates weekly session schedule")
    print("   Type: LLM Agent")
    print()
    print("3. Specialist Coaches (4 agents):")
    print("   - RunningCoach: Designs running workouts")
    print("   - StrengthCoach: Designs strength sessions")
    print("   - StrengthEnduranceCoach: Designs station work")
    print("   - HyroxComboCoach: Designs run+station combos")
    print("   Type: LLM Agents")
    print()
    print("4. WeekAssembler")
    print("   Role: Organizes sessions into week structure")
    print("   Type: Non-LLM (pure Python)")
    print()
    print("5. BlockValidatorAgent")
    print("   Role: Safety and quality validation")
    print("   Type: LLM Agent")
    print()
    print("=" * 60)
    print()
    print("WORKFLOW:")
    print("  User Input → Block Strategist → Week Orchestrator")
    print("            → Specialist Coaches → Week Assembler")
    print("            → (repeat for all weeks)")
    print("            → Block Validator → Complete Block")
    print()
    print("=" * 60)
    print()


if __name__ == "__main__":
    show_agent_system_overview()

    success = True

    if not test_imports():
        success = False

    if not test_week_assembler():
        success = False

    if success:
        print("=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("To run the full system:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Set ANTHROPIC_API_KEY environment variable")
        print("  3. Run: python create_training_block.py")
        print()
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        sys.exit(1)
