# Hyrox Training Block Builder - v3 (Goal-Driven)

A multi-agent system for creating personalized Hyrox training blocks using AI coaches.

## Architecture

### Goal-Driven Approach
Instead of using predefined archetypes, this system uses **training goals** and **session objectives** to drive workout design. Specialist coaches receive clear goals and design workouts to achieve them.

### Agent Flow

```
User Input (athlete data, goals, constraints)
    ↓
┌─────────────────────────────────────┐
│ 1. BLOCK STRATEGIST                 │
│ - Analyzes athlete needs            │
│ - Plans progression strategy        │
│ - Sets weekly objectives            │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. WEEK ORCHESTRATOR (per week)     │
│ - Creates session schedule          │
│ - Assigns session goals             │
│ - Routes to specialist coaches      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. SPECIALIST COACHES (parallel)    │
│ - Running Coach                     │
│ - Strength Coach                    │
│ - Strength Endurance Coach          │
│ - Hyrox Combo Coach                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. WEEK ASSEMBLER                   │
│ - Collects designed workouts        │
│ - Organizes into week structure     │
└─────────────────────────────────────┘
    ↓ (repeat for all weeks)
    ↓
┌─────────────────────────────────────┐
│ 5. BLOCK VALIDATOR                  │
│ - Safety and quality checks         │
│ - Progressive overload validation   │
│ - Intensity distribution review     │
└─────────────────────────────────────┘
    ↓
Complete Training Block → User
```

## Agents

### 1. Block Strategist Agent
**Role:** Strategic planner
**Input:** Athlete data, race date, training goals
**Output:** Week-by-week progression strategy with objectives

**Key Responsibilities:**
- Analyze athlete strengths and limiters
- Plan volume/intensity progression
- Determine deload week placement
- Set training objectives for each week

### 2. Week Orchestrator Agent
**Role:** Weekly session scheduler
**Input:** Week strategy, athlete data, previous week context
**Output:** Day-by-day session schedule with goals

**Key Responsibilities:**
- Map objectives to specific days
- Ensure proper intensity distribution
- Route sessions to appropriate coaches
- Maintain recovery patterns

### 3. Specialist Coaches
**Role:** Workout designers
**Input:** Session goals, constraints, athlete context
**Output:** Detailed workout design

**Coaches:**
- **Running Coach:** Zone 2 runs, threshold intervals, VO2max, long runs
- **Strength Coach:** Maximal strength, explosive power work
- **Strength Endurance Coach:** Station practice, EMOM/AMRAP circuits
- **Hyrox Combo Coach:** Combined run + station sessions

### 4. Week Assembler
**Role:** Data organizer (non-LLM)
**Input:** All designed sessions for a week
**Output:** Structured week with metadata

**Key Responsibilities:**
- Sort sessions by day
- Calculate week-level metrics
- Organize data structure

### 5. Block Validator Agent
**Role:** Quality assurance
**Input:** Complete training block
**Output:** Validation report with recommendations

**Key Responsibilities:**
- Check progressive overload
- Validate intensity distribution (80/20 rule)
- Identify safety concerns
- Provide improvement recommendations

## Usage

### Basic Example

```python
from create_training_block import TrainingBlockBuilder

user_input = {
    "athleteData": {
        "age": 41,
        "fitnessLevel": "intermediate",
        "hrMax": 188,
        "zone2HR": {"low": 113, "high": 131},
        "thresholdPaces": {"T1": "4:37/km", "T2": "4:17/km"},
        "estimatedMaxes": {
            "backSquat": "140kg",
            "deadlift": "160kg"
        },
        "equipment": ["barbell", "dumbbells", "skierg", "rower", "sleds", "wall_balls"]
    },
    "raceDate": "2026-05-15",
    "blockGoal": "Build aerobic base and Hyrox station proficiency",
    "weeksInBlock": 6,
    "trainingDaysPerWeek": 5,
    "sessionsPerWeek": 5,
    "availableDays": ["tuesday", "wednesday", "thursday", "saturday", "sunday"],
    "preferredRestDays": ["monday", "friday"]
}

builder = TrainingBlockBuilder()
training_block = builder.create_block(user_input)
```

### Running the Example

```bash
cd poc-v3
python create_training_block.py
```

## Required Environment

### Python Dependencies
```bash
pip install anthropic
pip install rich  # Optional, for better terminal output
```

### Environment Variables
Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Output

The system generates a JSON file containing:

```json
{
  "metadata": {
    "createdAt": "2025-01-17T...",
    "version": "v3-goal-driven",
    "totalWeeks": 6
  },
  "blockStrategy": {
    "blockMetadata": {...},
    "athleteAnalysis": {...},
    "progressionStrategy": {...},
    "weeklyFramework": [...]
  },
  "weeklyPlans": [
    {
      "weekNumber": 1,
      "weekStrategy": {...},
      "sessions": [
        {
          "dayOfWeek": "tuesday",
          "sessionType": "runningQuality",
          "sessionGoal": "...",
          "workout": {
            "name": "Zone 2 Aerobic Base Run",
            "warmup": {...},
            "mainSet": {...},
            "cooldown": {...}
          }
        }
      ],
      "weekMetrics": {...}
    }
  ],
  "validation": {
    "validationStatus": "APPROVED",
    "progressionAnalysis": {...},
    "recommendations": [...]
  }
}
```

## Key Features

✅ **Goal-Driven:** Coaches design workouts to achieve specific training objectives, not implement templates
✅ **Progressive:** Each week builds on previous with intelligent progression
✅ **Safe:** Validator checks for overtraining, injury risks, recovery patterns
✅ **Personalized:** Adapts to athlete's age, fitness level, equipment, schedule
✅ **Hyrox-Specific:** Specialized for Hyrox race demands (8km run + 8 stations)
✅ **Context-Aware:** Coaches see previous week for intelligent progression

## Design Philosophy

1. **Simplicity over complexity:** Removed archetype abstraction layer
2. **Goals over templates:** Coaches solve training problems, not fill templates
3. **AI where it helps:** LLMs for creative workout design, simple code for data organization
4. **Progressive context:** Each week sees previous week for smart progression
5. **Safety first:** Validation checks prevent overtraining and injury risk

## Comparison to v2

| Aspect | v2 (Archetype-Driven) | v3 (Goal-Driven) |
|--------|----------------------|------------------|
| Approach | Periodization plan → Archetypes → Sessions | Goals → Sessions |
| Complexity | High (460-line periodization prompts) | Medium (focused prompts) |
| Flexibility | Constrained by archetype definitions | High - coaches design freely |
| Overhead | Multi-layer abstraction | Direct goal-to-workout |
| Testing | Requires periodization plan first | Standalone block creation |

## Future Enhancements

- [ ] Add recovery/mobility coach
- [ ] Support for athlete feedback between weeks (adaptive progression)
- [ ] Multi-block planning (entire training cycle)
- [ ] Integration with training logs (analyze actual vs planned)
- [ ] Support for different race types (not just Hyrox)
- [ ] Web interface for user input
- [ ] PDF output with formatted training plans

## License

Internal POC - Not for distribution
