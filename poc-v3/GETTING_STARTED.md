# Getting Started with Hyrox Training Block Builder v3

## Quick Start

### 1. Install Dependencies

```bash
cd poc-v3
pip install -r requirements.txt
```

Required packages:
- `anthropic` - Claude API client
- `rich` - Terminal formatting (optional but recommended)
- `python-dotenv` - Environment variable management

### 2. Set Up API Key

Create a `.env` file in the `poc-v3` directory:

```bash
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

Or set the environment variable directly:

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

### 3. Run the Example

```bash
python create_training_block.py
```

This will create a 6-week training block and save it to `output/training_block_*.json`

## Customizing Your Training Block

Edit the `user_input` dictionary in `create_training_block.py`:

```python
user_input = {
    "athleteData": {
        "age": 41,                          # Your age
        "fitnessLevel": "intermediate",     # beginner/intermediate/advanced
        "hrMax": 188,                       # Maximum heart rate
        "zone2HR": {                        # Zone 2 heart rate range
            "low": 113,
            "high": 131
        },
        "thresholdPaces": {                 # Lactate threshold paces
            "T1": "4:37/km",
            "T2": "4:17/km"
        },
        "estimatedMaxes": {                 # Estimated 1-rep maxes
            "backSquat": "140kg",
            "deadlift": "160kg",
            "benchPress": "100kg"
        },
        "equipment": [                      # Available equipment
            "barbell", "dumbbells", "skierg",
            "rower", "sleds", "wall_balls", "sandbags"
        ]
    },
    "raceDate": "2026-05-15",              # Your target race date
    "blockGoal": "Build aerobic base",      # What you want to achieve
    "weeksInBlock": 6,                      # How many weeks (4-8 typical)
    "trainingDaysPerWeek": 5,               # Days you can train
    "sessionsPerWeek": 5,                   # Sessions per week
    "availableDays": [                      # Days you can train
        "tuesday", "wednesday", "thursday",
        "saturday", "sunday"
    ],
    "preferredRestDays": [                  # Days you prefer to rest
        "monday", "friday"
    ]
}
```

## Understanding the Output

The system creates a JSON file with three main sections:

### 1. Block Strategy
The high-level plan created by the Block Strategist:
- Weekly objectives
- Volume/intensity progression
- Training focus per week

### 2. Weekly Plans
Detailed workouts for each week:
- Day-by-day session schedule
- Complete workout designs
- Coaching cues and rationale

### 3. Validation Report
Safety and quality check:
- Progressive overload analysis
- Intensity distribution review
- Safety recommendations

## Example Workflow

1. **Input your data** - age, fitness level, goals, schedule
2. **Block Strategist** analyzes your needs and creates strategy
3. **Week Orchestrator** schedules sessions for each week
4. **Specialist Coaches** design each workout:
   - Running Coach: Running sessions
   - Strength Coach: Strength work
   - Strength Endurance Coach: Station practice
   - Hyrox Combo Coach: Run + station combos
5. **Block Validator** checks safety and quality
6. **Output** Complete 6-week training block as JSON

## Common Block Goals

- "Build aerobic base and station proficiency" (Base phase)
- "Develop race-pace threshold and power" (Build phase)
- "Peak for race performance" (Peak phase)
- "Maintain fitness while tapering" (Taper phase)

## Typical Block Lengths

- **4 weeks**: Micro-cycle, specific focus
- **6 weeks**: Standard block (recommended)
- **8 weeks**: Extended block for major adaptations

## What's Different from v2?

**v2 (Archetype-Driven):**
- Required periodization plan first
- Archetypes as intermediate layer
- More complex, more structured

**v3 (Goal-Driven):**
- Direct block creation
- Goals → Workouts (no archetype layer)
- Simpler, more flexible
- Coaches design freely to achieve goals

## Troubleshooting

**"No module named 'anthropic'"**
```bash
pip install anthropic
```

**"API key not found"**
- Check `.env` file exists
- Verify `ANTHROPIC_API_KEY` is set
- Make sure `.env` is in the `poc-v3` directory

**"Agent execution failed"**
- Check API key is valid
- Ensure you have API credits
- Review error message in output

## Next Steps

1. Run the example to see how it works
2. Customize with your own data
3. Review the generated training block
4. Adjust goals and re-run if needed
5. Export to your preferred training log format

## Support

This is a POC. For issues:
1. Check the README.md for architecture details
2. Review agent system prompts in `agents/` directory
3. Examine output JSON for errors

## Tips for Best Results

- **Be accurate with fitness data** - HR zones, threshold paces matter
- **Set realistic goals** - match your current training phase
- **Trust the progression** - the system builds conservatively
- **Follow the deload week** - recovery is essential for adaptation
- **Track your actual performance** - compare planned vs actual

Happy training! 🏃‍♂️💪
