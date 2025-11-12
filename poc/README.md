# Block Smith - Proof of Concept

This is a standalone proof of concept to test the AI agent architecture for Block Smith before building the full application.

## What This Tests

This PoC validates:
1. **Periodization Plan Generation** - Can the agents create a quality 20-week training plan?
2. **Training Block Generation** - Can the agents create detailed weekly workouts?
3. **Agent Collaboration** - Do the specialist agents work well together?
4. **Output Quality** - Are the workouts realistic, progressive, and Hyrox-specific?

## Architecture

### Agents Included

**Phase 1: Periodization Agents**
- `PeriodizationOrchestrator` - Routes to sport-specific agents
- `HyroxPeriodizationAgent` - Creates Hyrox periodization plans (Base → Build → Peak → Taper)

**Phase 2: Training Block Agents**
- `HyroxBlockBuilderAgent` - Designs block structure and coordinates coaches
- `AerobicBaseCoach` - Creates Zone 2 running workouts
- `StrengthEnduranceCoach` - Creates Hyrox station strength workouts

## Setup

### Prerequisites

- Python 3.9+
- An API key from either:
  - **Anthropic** (Claude) - Recommended
  - **OpenAI** (GPT-4)

### Installation

1. **Navigate to the PoC directory:**
   ```bash
   cd poc
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

5. **Edit `.env` and add your API key:**
   ```bash
   # For Claude (Recommended)
   ANTHROPIC_API_KEY=your_key_here
   AI_PROVIDER=anthropic

   # OR for OpenAI
   # OPENAI_API_KEY=your_key_here
   # AI_PROVIDER=openai
   ```

## Usage

### Test 1: Generate a Periodization Plan

This tests if the agents can create a comprehensive 20-week Hyrox training plan.

```bash
python test_periodization.py
```

**What it does:**
1. Takes user input (race type, date, fitness level)
2. Routes to `HyroxPeriodizationAgent`
3. Generates a 4-phase plan (Base, Build, Peak, Taper)
4. Saves output to `output/periodization_plan_*.json`

**What to look for:**
- ✅ Does it create 4 distinct phases?
- ✅ Are deload weeks strategically placed?
- ✅ Do phase durations make sense (Base: 4-6w, Build: 6-8w, etc.)?
- ✅ Are goals Hyrox-specific (station work, running with fatigue)?
- ✅ Are modality percentages balanced?

### Test 2: Generate a Training Block

This tests if the agents can create detailed weekly workouts for the Base phase.

```bash
python test_block_builder.py
```

**What it does:**
1. Loads the latest periodization plan
2. Extracts the first phase (Base Building)
3. Calls `HyroxBlockBuilderAgent` to design block structure
4. Calls specialist coaches:
   - `AerobicBaseCoach` - Creates Zone 2 runs
   - `StrengthEnduranceCoach` - Creates station workouts
5. Saves output to `output/training_block_*.json`

**What to look for:**
- ✅ Are workouts detailed (exercises, sets, reps, intensity)?
- ✅ Do running workouts progressively increase volume?
- ✅ Do strength workouts target all 8 Hyrox stations?
- ✅ Is intensity appropriate for Base phase (60-70%)?
- ✅ Are exercise notes helpful and technique-focused?

## Output Files

All outputs are saved in `poc/output/`:
- `periodization_plan_YYYYMMDD_HHMMSS.json` - Full periodization plan
- `training_block_YYYYMMDD_HHMMSS.json` - Detailed training block with workouts

## Evaluating Results

### Good Signs ✅
- Plans are Hyrox-specific (mentions stations, running with fatigue)
- Progressive overload is evident (volume increases week to week)
- Phase goals are clear and distinct
- Workouts include specific exercises, not just "strength training"
- Intensity guidelines are appropriate for each phase
- Deload weeks are included

### Red Flags ❌
- Generic advice (could apply to any sport)
- No mention of Hyrox stations
- Workouts are vague ("3 sets of strength exercises")
- No progression between weeks
- Intensity too high in Base phase or too low in Peak
- Missing deload weeks

## Iterating on Agents

If output quality isn't good:

1. **Adjust agent prompts** in `agents/*.py`:
   - Make constraints more specific
   - Add more examples
   - Emphasize Hyrox-specific requirements

2. **Test different fitness levels:**
   - Edit `test_periodization.py` line 33: change `"currentFitness": "beginner"` or `"advanced"`

3. **Test different phases:**
   - Edit `test_block_builder.py` line 42: change `[0]` to `[1]` for Build phase

4. **Adjust LLM temperature:**
   - Edit `agents/base_agent.py` line 24: change `temperature=0.7` (higher = more creative, lower = more focused)

## Next Steps

Once you're satisfied with the output quality:

1. **Build the full application** - Implement Next.js + database + UI
2. **Add more agents** - Triathlon, OCR, etc.
3. **Add Integration Agent** - Properly schedule workouts into weekly calendar
4. **Add Progressive Overload Agent** - Compare blocks and ensure progression
5. **Add user editing** - Allow manual adjustments to AI-generated plans

## Cost Estimates

**Per test run:**
- Periodization plan: ~$0.05-0.15 (depending on provider and model)
- Training block: ~$0.10-0.30 (3 agent calls)

**Total for 5 test iterations:** ~$1-2

## Troubleshooting

**Error: "API key not found"**
- Make sure you've created `.env` file (not `.env.example`)
- Check that your API key is correct and has credits

**Error: "Module not found"**
- Make sure you're in the `poc` directory
- Activate the virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**JSON parsing errors**
- The agent may not be outputting valid JSON
- Check `agents/base_agent.py` line 56 for parsing logic
- Add more emphasis in agent prompts: "Output ONLY valid JSON"

**Output quality is poor**
- Try Claude instead of OpenAI (or vice versa)
- Adjust agent prompts to be more specific
- Lower temperature for more focused output

## Questions?

Review the main specification: `../BLOCK_SMITH_SPECIFICATION.md`

## License

Internal PoC for Block Smith development
