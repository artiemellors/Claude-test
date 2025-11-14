# Block Smith v2 - Phase-Aware Agentic Architecture

## Overview

This is Proof of Concept v2 demonstrating **phase-aware training block generation** using specialized AI agents. The key innovation is that each periodization phase (Base, Build, Peak, Taper) provides detailed **session guidelines** that direct specialist coaches on how to design workouts.

## Architecture Improvements from v1

### What's New:
1. **Global Context Agent** - Central data store (not LLM) for athlete profile and training rules
2. **Phase-Aware Session Guidelines** - Each periodization phase includes explicit guidance for:
   - Running Quality sessions (e.g., Zone 2 in Base → Threshold in Build → VO2 in Peak)
   - Max Strength sessions (e.g., 5-8 reps in Base → 3-5 reps in Build → 1-3 reps in Peak)
   - Strength Endurance sessions (e.g., separated in Base → alternating in Build → combined in Peak)
   - HYROX Combo sessions (e.g., separated format → alternating → full race simulation)
3. **Skeleton Agent** - Creates weekly structure before specialists design workouts
4. **Integration Agent** - Assembles specialist workouts into complete weekly plans
5. **Validation Agent** - Checks training blocks for safety and effectiveness

### Agent Flow:

```
User Input
    ↓
Periodization Agent → Creates 4-phase plan with session guidelines per phase
    ↓
[For each block:]
    ↓
Skeleton Agent → Creates weekly structure (which days = which session types)
    ↓
Specialist Coaches → Design workouts based on CURRENT PHASE GUIDELINES
    ├─ Running Quality Coach (phase-aware)
    ├─ Max Strength Coach (phase-aware)
    ├─ Strength Endurance Coach (phase-aware)
    └─ HYROX Combo Coach (phase-aware)
    ↓
Integration Agent → Assembles into complete weekly plan
    ↓
Validation Agent → Checks safety, intensity distribution, phase alignment
    ↓
Complete Training Block
```

## Directory Structure

```
poc-v2/
├── agents/
│   ├── base_agent.py                    # Base class with improved JSON parsing
│   ├── global_context_agent.py          # Data store (NOT LLM)
│   ├── hyrox_periodization_agent.py     # Creates phase plan + session guidelines
│   ├── skeleton_agent.py                # Creates weekly structure
│   ├── running_quality_coach.py         # Phase-aware running sessions
│   ├── max_strength_coach.py            # Phase-aware strength sessions
│   ├── strength_endurance_coach.py      # Phase-aware SE sessions
│   ├── hyrox_combo_coach.py             # Phase-aware combo sessions
│   ├── integration_agent.py             # Assembles weekly plans
│   └── validation_agent.py              # Validates training blocks
├── output/                               # Generated plans stored here
├── test_1_periodization.py              # Test: Create periodization plan
├── test_2_block1.py                     # Test: Create Base phase block
├── test_3_block2.py                     # Test: Create Build phase block
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. **Install dependencies:**
   ```bash
   cd poc-v2
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

3. **Create output directory:**
   ```bash
   mkdir -p output
   ```

## Running the Tests

### Test 1: Create Periodization Plan

Creates a complete 18-week Hyrox periodization plan with session guidelines for each phase.

```bash
python3 test_1_periodization.py
```

**What it demonstrates:**
- 4 phases: Base (6 weeks) → Build (6 weeks) → Peak (4 weeks) → Taper (2 weeks)
- Each phase includes detailed `sessionGuidelines` object
- Guidelines specify:
  - Running focus types (Zone 2 → Threshold → VO2)
  - Strength rep ranges (5-8 → 3-5 → 1-3)
  - Station integration (separated → alternating → combined)
  - Example sessions for each phase

**Output:** `output/periodization_plan_YYYYMMDD_HHMMSS.json`

### Test 2: Create Block 1 (Base Phase)

Creates a detailed training block for weeks 1-6 (Base phase).

```bash
python3 test_2_block1.py
```

**What it demonstrates:**
- Skeleton creates weekly structure (5 sessions/week)
- Running coach designs Zone 2 runs (60-70% effort)
- SE coach creates station work with separated format
- HYROX combo coach uses separated format (run, rest, stations)
- Integration assembles complete weekly plan
- Validation checks intensity distribution, recovery

**Output:** `output/block1_base_phase_YYYYMMDD_HHMMSS.json`

### Test 3: Create Block 2 (Build Phase)

Creates a detailed training block for weeks 7-12 (Build phase) with progression.

```bash
python3 test_3_block2.py
```

**What it demonstrates:**
- **Phase shift verification:**
  - Running: Zone 2 → Threshold intervals (T1/T2 work)
  - Strength: 5-8 reps @ 70-80% → 3-5 reps @ 80-87%
  - Stations: Separated → Alternating (run-station-run)
  - HYROX Combo: Separated → Alternating format
- Progressive overload from Block 1
- Max Strength coach now active (was optional in Base)
- Validation confirms phase alignment

**Output:** `output/block2_build_phase_YYYYMMDD_HHMMSS.json`

## Key Concepts

### Phase-Aware Programming

Each phase has distinct characteristics:

| Phase | Weeks | Running | Strength | Stations | HYROX Combo |
|-------|-------|---------|----------|----------|-------------|
| **Base** | 1-6 | Zone 2, easy pace | 5-8 reps @ 70-80% | Separated | Separated format |
| **Build** | 7-12 | Threshold intervals | 3-5 reps @ 80-87% | Alternating | Alternating format |
| **Peak** | 13-16 | VO2 max, race pace | 1-3 reps @ 87-95% | Combined | Full race simulation |
| **Taper** | 17-18 | Short, sharp efforts | 2-3 reps @ 80-85% | Minimal | Partial race rehearsal |

### Session Guidelines Structure

Each phase includes `sessionGuidelines` that specialists query:

```json
{
  "sessionGuidelines": {
    "runningQuality": {
      "focusTypes": ["Zone 2", "easy pace"],
      "intensityRange": "60-70%",
      "exampleSession": "60min Z2 @ 5:30/km"
    },
    "maxStrength": {
      "repRange": "5-8 reps",
      "loadRange": "70-80% 1RM",
      "frequency": "2x per week"
    },
    "strengthEndurance": {
      "workRestRatio": "1:1 or 2:1",
      "cardioIntegration": "Separate or minimal"
    },
    "hyroxCombo": {
      "format": "Separated (run, then stations with rest)",
      "intensityRange": "65-75% effort"
    }
  }
}
```

### Progressive Overload

Specialists handle their own week-to-week progression:

- **Running Coach:** Increases duration OR pace OR reduces rest
- **Strength Coach:** Increases load OR reps (not both)
- **SE Coach:** Increases volume OR reduces rest OR adds cardio integration
- **HYROX Coach:** Progresses format complexity (separated → alternating → full race)

### No Separate Progression Agent

Unlike v1, we **do NOT have a separate Progression Agent**. Instead:
- Each specialist receives `previousWeek` data
- Applies domain-specific progression logic
- Makes expertise-driven decisions (not generic "+10%")

## Expected Results

### Test 1 Output:
- Complete 18-week periodization plan
- 4 phases with detailed session guidelines
- Deload weeks at Week 6 and Week 11
- Clear intensity progression across phases

### Test 2 Output:
- Week 1 of Base phase
- 5 sessions: 2x Running, 2x SE, 1x HYROX Combo
- Zone 2 running focus
- Separated station work
- ~6-7 hours total training time

### Test 3 Output:
- Week 7 of Build phase
- 5 sessions: 2x Running, 1x Max Strength, 1x SE, 1x HYROX Combo
- Threshold running intervals
- 3-5 rep strength work
- Alternating run-station format
- Clear progression from Base phase

## Validation Checks

The Validation Agent checks:
1. **Intensity Distribution:** 70% easy, 20% moderate, 10% hard (Base phase)
2. **Recovery Adequacy:** Minimum 2 rest days per week
3. **Volume Progression:** <15% increase per week
4. **Phase Alignment:** Sessions match phase guidelines
5. **Overtraining Risk:** Total hours appropriate for fitness level
6. **Session Spacing:** 48+ hours between hard sessions

## Model Used

All agents use: `claude-sonnet-4-20250514`

## Troubleshooting

**JSON parsing errors:**
- The `base_agent.py` includes improved JSON parsing with multiple fallback strategies
- If LLM response includes explanatory text, it will extract the JSON portion

**Missing periodization plan:**
- Run `test_1_periodization.py` first
- Check that `output/` directory exists

**API errors:**
- Verify ANTHROPIC_API_KEY in `.env`
- Check you have API credits

## Next Steps

After validating this PoC works:
1. Extend to generate full 6-week blocks (currently only Week 1 and Week 7)
2. Add more specialist coaches (Recovery Coach, Nutrition Coach)
3. Build web interface for user input
4. Add database persistence
5. Implement user feedback loop

## Architecture Benefits

1. **Phase-Aware:** Workouts automatically adapt to current training phase
2. **Expertise-Driven:** Each coach specializes in their domain
3. **Scalable:** Easy to add new sports (Triathlon, OCR) or coaches
4. **Progressive:** Natural progression from Base → Build → Peak → Taper
5. **Safe:** Validation checks prevent overtraining
6. **Transparent:** Clear rationale for every workout decision

## Comparison to v1

| Feature | v1 | v2 |
|---------|----|----|
| Phase awareness | Implicit | **Explicit with session guidelines** |
| Context management | Per-agent | **Global Context Agent** |
| Weekly structure | Ad-hoc | **Skeleton Agent** |
| Workout assembly | Manual | **Integration Agent** |
| Safety checks | None | **Validation Agent** |
| Progression | Separate agent | **Specialist-driven** |
| Cardio integration | Fixed | **Phase-dependent** |

## Contact

For questions about this PoC, refer to the main Block Smith specification document.
