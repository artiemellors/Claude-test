# POC v3 Implementation Summary

## What Was Built

A **goal-driven multi-agent system** for creating personalized Hyrox training blocks.

## Architecture Decision: Goal-Driven vs Archetype-Driven

After discussion, we chose **Goal-Driven (Option B)** over archetype-driven approach because:

✅ **Simpler** - Fewer abstraction layers
✅ **More flexible** - AI coaches design creatively to solve problems
✅ **Better for POC** - Faster to test and iterate
✅ **More like real coaching** - Coaches think in goals, not templates
✅ **Standalone** - No dependency on complex periodization plans

## Agent System

### 5 Core Agents

1. **BlockStrategistAgent** (LLM)
   - Analyzes athlete data
   - Creates week-by-week progression strategy
   - Sets training objectives for each week
   - Plans deload timing

2. **WeekOrchestratorAgent** (LLM)
   - Takes week strategy + previous week context
   - Creates day-by-day session schedule
   - Routes sessions to specialist coaches
   - Ensures proper intensity distribution

3. **Specialist Coaches** (4 LLM agents)
   - **RunningCoach**: Zone 2, threshold, VO2max, long runs
   - **StrengthCoach**: Maximal strength, explosive power
   - **StrengthEnduranceCoach**: Station practice, conditioning
   - **HyroxComboCoach**: Combined run + station sessions

4. **WeekAssembler** (Non-LLM)
   - Pure Python data organizer
   - Collects designed sessions into week structure
   - Calculates metrics

5. **BlockValidatorAgent** (LLM)
   - Safety and quality checks
   - Progressive overload validation
   - Intensity distribution analysis
   - Recommendations for improvement

## Files Created

```
poc-v3/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py              # Base class for all LLM agents
│   ├── block_strategist.py        # Creates block strategy
│   ├── week_orchestrator.py       # Schedules weekly sessions
│   ├── week_assembler.py          # Non-LLM data organizer
│   ├── block_validator.py         # Safety validator
│   ├── running_coach.py           # Running workout designer
│   ├── strength_coach.py          # Strength workout designer
│   ├── strength_endurance_coach.py # Station practice designer
│   └── hyrox_combo_coach.py       # Hybrid session designer
├── create_training_block.py       # Main orchestrator
├── test_structure.py              # Structure test (no API needed)
├── requirements.txt               # Python dependencies
├── README.md                      # Complete documentation
├── GETTING_STARTED.md            # Quick start guide
└── IMPLEMENTATION_SUMMARY.md     # This file
```

## How It Works

```
User provides:
- Athlete data (age, fitness, HR zones, paces, maxes)
- Race date and goal
- Training schedule (days available, sessions per week)
- Block length (4-8 weeks)

        ↓

Block Strategist analyzes and creates strategy:
- Week-by-week objectives
- Volume/intensity progression
- Deload week placement

        ↓

For each week:
    Week Orchestrator creates session schedule
        ↓
    Specialist Coaches design workouts (in parallel)
        ↓
    Week Assembler organizes into structure

        ↓

Block Validator checks complete block:
- Progressive overload
- Recovery patterns
- Safety concerns

        ↓

Complete training block → JSON output
```

## Key Features

✅ **Progressive Context**: Each week sees previous week for smart progression
✅ **Goal-Driven**: Coaches design workouts to achieve objectives, not fill templates
✅ **Safety-First**: Validator prevents overtraining and injury risk
✅ **Hyrox-Specific**: Designed for 8km run + 8 stations race format
✅ **Personalized**: Adapts to age, fitness level, equipment, schedule
✅ **Standalone**: No complex periodization plan needed

## Example Input

```python
{
    "athleteData": {
        "age": 41,
        "fitnessLevel": "intermediate",
        "hrMax": 188,
        "zone2HR": {"low": 113, "high": 131},
        "thresholdPaces": {"T1": "4:37/km", "T2": "4:17/km"},
        "estimatedMaxes": {"backSquat": "140kg", "deadlift": "160kg"},
        "equipment": ["barbell", "skierg", "rower", "sleds", "wall_balls"]
    },
    "raceDate": "2026-05-15",
    "blockGoal": "Build aerobic base and station proficiency",
    "weeksInBlock": 6,
    "trainingDaysPerWeek": 5,
    "sessionsPerWeek": 5,
    "availableDays": ["tuesday", "wednesday", "thursday", "saturday", "sunday"],
    "preferredRestDays": ["monday", "friday"]
}
```

## Example Output

Complete 6-week training block with:
- Detailed workout designs for each day
- Specific paces, loads, reps, rest periods
- Coaching cues and rationale
- Progressive week-to-week adaptation
- Safety validation report

## Comparison to v2

| Aspect | v2 | v3 |
|--------|----|----|
| Approach | Periodization → Archetypes → Sessions | Goals → Sessions |
| Complexity | High (460-line prompts) | Medium (focused) |
| Dependencies | Requires periodization plan | Standalone |
| Flexibility | Constrained by archetypes | High - creative design |
| Abstraction Layers | 3-4 layers | 2 layers |
| Coach Thinking | "Implement archetype X" | "Achieve goal Y" |

## What's Better in v3

1. **Simpler mental model** - Goals are intuitive
2. **Faster iteration** - No periodization plan needed first
3. **More flexible** - Coaches design freely
4. **Better for POC** - Easier to test and debug
5. **Still structured** - Block strategy ensures progression
6. **AI where it helps** - LLMs solve problems, not fill templates

## To Use

1. Install dependencies: `pip install -r requirements.txt`
2. Set API key: `export ANTHROPIC_API_KEY="..."`
3. Run: `python create_training_block.py`
4. Review output in `output/training_block_*.json`

## Future Enhancements

- [ ] Multi-block planning (full training cycle)
- [ ] Adaptive progression based on athlete feedback
- [ ] PDF export with formatted plans
- [ ] Web interface for user input
- [ ] Integration with training logs
- [ ] Support for other race types

## Status

✅ Complete and ready to test
⏳ Requires: `anthropic`, `rich` packages + API key
📦 All code committed to `claude/investigate-file-poc-0157izyCVXWVwa3tEq7i73G9`

## Next Steps

1. Install dependencies
2. Run with your own athlete data
3. Review generated training blocks
4. Iterate on prompts based on output quality
5. Consider adding recovery/mobility coach
6. Build out multi-block support for full training cycles
