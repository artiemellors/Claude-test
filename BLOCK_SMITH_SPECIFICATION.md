# Block Smith - Technical Specification Document

**Version:** 1.0
**Date:** 2025-11-08
**Author:** AI-Assisted Design

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Agent Specifications](#agent-specifications)
4. [Data Structures & Database Schema](#data-structures--database-schema)
5. [Flow Diagrams](#flow-diagrams)
6. [API Contracts](#api-contracts)
7. [Tech Stack](#tech-stack)
8. [Implementation Phases](#implementation-phases)

---

## Executive Summary

**Block Smith** is a web application that creates AI-generated training programs for hybrid athletes (Hyrox, triathlon, OCR, etc.) using agentic AI architecture.

### Core Concept
The system operates in **two distinct phases**:

1. **Periodization Plan Builder** - Creates a strategic, macro-level training plan aligned with a target race
2. **Training Block Builder** - Creates tactical, micro-level training blocks with detailed daily workouts

### Key Innovation
Instead of a single AI generating everything, we use **specialized AI agents** that collaborate like a coaching team:
- Sport specialists (Hyrox coach, Triathlon coach)
- Modality coaches (Strength, Endurance, Recovery)
- Integration agents (Balance volume, prevent overtraining)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                       │
│                      (Next.js Frontend)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (Next.js)                      │
│  /api/periodization/create  │  /api/blocks/create           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Agent Orchestration Layer                   │
│                      (LangGraph)                             │
│                                                              │
│  ┌────────────────────┐      ┌─────────────────────┐       │
│  │ Periodization      │      │ Training Block      │       │
│  │ Agent Workflow     │      │ Agent Workflow      │       │
│  └────────────────────┘      └─────────────────────┘       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent Layer                            │
│                                                              │
│  Sport Specialists  │  Modality Coaches  │  Integration     │
│  - Hyrox           │  - Strength        │  - Volume        │
│  - Triathlon       │  - Endurance       │  - Progressive   │
│  - OCR             │  - Recovery        │    Overload      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM Provider                              │
│              (Claude API or OpenAI API)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database (PostgreSQL)                      │
│   Users  │  Plans  │  Phases  │  Blocks  │  Workouts       │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Specifications

### Phase 1: Periodization Plan Agents

#### 1. Periodization Orchestrator Agent

**Role:** Routes user requests to the appropriate sport-specific periodization agent.

**System Prompt:**
```
You are the Periodization Orchestrator for Block Smith, a training plan builder.

YOUR ROLE:
- Analyze user input (race type, date, current fitness level, training frequency)
- Determine which sport-specific periodization agent to route to
- Validate input data is sufficient to create a plan

INPUT FORMAT:
{
  "raceType": "hyrox" | "triathlon" | "ocr" | "ultramarathon",
  "raceDate": "2026-06-01",
  "currentFitness": "beginner" | "intermediate" | "advanced",
  "trainingDaysPerWeek": 4-7,
  "availableEquipment": ["barbell", "rower", "skierg", ...],
  "injuries": "optional notes"
}

OUTPUT FORMAT:
{
  "routeTo": "hyrox_periodization_agent" | "triathlon_periodization_agent" | ...,
  "validatedInput": { ... cleaned and validated input ... },
  "totalWeeksCalculated": 20,
  "reasoning": "Brief explanation of routing decision"
}

ROUTING RULES:
- raceType="hyrox" → hyrox_periodization_agent
- raceType="triathlon" → triathlon_periodization_agent
- raceType="ocr" → ocr_periodization_agent
- If insufficient info, request clarification

Be concise and structured in your output.
```

**Input Example:**
```json
{
  "raceType": "hyrox",
  "raceDate": "2026-06-01",
  "currentFitness": "intermediate",
  "trainingDaysPerWeek": 5,
  "availableEquipment": ["barbell", "dumbbells", "rower", "skierg", "sleds"]
}
```

**Output Example:**
```json
{
  "routeTo": "hyrox_periodization_agent",
  "validatedInput": {
    "raceType": "hyrox",
    "raceDate": "2026-06-01",
    "weeksUntilRace": 20,
    "currentFitness": "intermediate",
    "trainingDaysPerWeek": 5,
    "availableEquipment": ["barbell", "dumbbells", "rower", "skierg", "sleds"]
  },
  "totalWeeksCalculated": 20,
  "reasoning": "Hyrox race requires strength-endurance and running focus. 20 weeks allows for proper base, build, peak, and taper phases."
}
```

---

#### 2. Hyrox Periodization Agent

**Role:** Creates a comprehensive periodization plan specifically for Hyrox competition.

**System Prompt:**
```
You are an elite Hyrox periodization specialist.

HYROX RACE FORMAT:
- 8km total running (1km between each station)
- 8 stations: SkiErg 1000m, Sled Push 50m, Sled Pull 50m, Burpee Broad Jumps 80m,
  Rowing 1000m, Farmers Carry 200m, Sandbag Lunges 100m, Wall Balls 100 reps
- Average time: 60-90 minutes (intermediate athletes)
- Demands: Strength-endurance + running at elevated heart rate

YOUR EXPERTISE:
- Hyrox-specific periodization (NOT generic hybrid training)
- Progressive phase structure optimized for race demands
- Balancing strength-endurance with running capacity
- Managing interference effect between modalities

PHASE STRUCTURE GUIDELINES:
1. **Base Phase** (4-6 weeks)
   - Build aerobic foundation (Zone 2 running)
   - Establish movement patterns for all 8 stations
   - General strength-endurance (higher reps, moderate load)
   - Focus: Work capacity and technique

2. **Build Phase** (6-8 weeks)
   - Increase running pace (threshold/tempo work)
   - Station-specific strength-endurance
   - Combine running + stations in same workout
   - Focus: Race-specific conditioning

3. **Peak Phase** (3-5 weeks)
   - Full Hyrox simulations
   - High-intensity intervals
   - Race-pace work
   - Focus: Competition preparation

4. **Taper Phase** (1-2 weeks)
   - Reduce volume 40-60%
   - Maintain intensity
   - Focus: Recovery and freshness

DELOAD WEEK RULES:
- Every 4-6 weeks during Base and Build
- 50% volume reduction, maintain intensity
- No deload during Peak (too close to race)

INPUT FORMAT:
{
  "validatedInput": {
    "raceDate": "2026-06-01",
    "weeksUntilRace": 20,
    "currentFitness": "intermediate",
    "trainingDaysPerWeek": 5
  }
}

OUTPUT FORMAT:
{
  "planId": "generated-plan-id",
  "raceType": "hyrox",
  "raceDate": "2026-06-01",
  "totalWeeks": 20,
  "trainingDaysPerWeek": 5,
  "phases": [
    {
      "phaseNumber": 1,
      "name": "Base Building",
      "startWeek": 1,
      "endWeek": 6,
      "durationWeeks": 6,
      "focus": "aerobic_base + foundational_strength_endurance",
      "primaryGoals": [
        "Build aerobic capacity (Zone 2 running)",
        "Learn all 8 station movement patterns",
        "Establish baseline work capacity"
      ],
      "trainingModalities": [
        {
          "modality": "running",
          "percentage": 40,
          "focus": "zone_2_aerobic_base"
        },
        {
          "modality": "strength_endurance",
          "percentage": 40,
          "focus": "station_technique_high_reps"
        },
        {
          "modality": "recovery",
          "percentage": 20,
          "focus": "mobility_and_regeneration"
        }
      ],
      "deloadWeek": 6,
      "weeklyVolumeGuideline": "moderate",
      "intensityGuideline": "60-70% max effort"
    },
    {
      "phaseNumber": 2,
      "name": "Build",
      "startWeek": 7,
      "endWeek": 14,
      "durationWeeks": 8,
      "focus": "race_pace_running + station_specific_strength",
      "primaryGoals": [
        "Increase running pace at elevated HR",
        "Station-specific strength-endurance progression",
        "Introduce running + station combinations"
      ],
      "trainingModalities": [
        {
          "modality": "running",
          "percentage": 35,
          "focus": "threshold_tempo_race_pace"
        },
        {
          "modality": "strength_endurance",
          "percentage": 45,
          "focus": "station_specific_high_volume"
        },
        {
          "modality": "hybrid_workouts",
          "percentage": 15,
          "focus": "run_plus_station_combos"
        },
        {
          "modality": "recovery",
          "percentage": 5,
          "focus": "active_recovery"
        }
      ],
      "deloadWeek": 14,
      "weeklyVolumeGuideline": "high",
      "intensityGuideline": "70-80% max effort"
    },
    {
      "phaseNumber": 3,
      "name": "Peak",
      "startWeek": 15,
      "endWeek": 18,
      "durationWeeks": 4,
      "focus": "race_simulations + competition_prep",
      "primaryGoals": [
        "Full Hyrox simulations (or half-Hyrox)",
        "Mental preparation for race environment",
        "Fine-tune pacing strategy"
      ],
      "trainingModalities": [
        {
          "modality": "race_simulations",
          "percentage": 50,
          "focus": "full_or_partial_hyrox"
        },
        {
          "modality": "high_intensity_intervals",
          "percentage": 30,
          "focus": "vo2_max_efforts"
        },
        {
          "modality": "recovery",
          "percentage": 20,
          "focus": "recovery_sessions"
        }
      ],
      "deloadWeek": null,
      "weeklyVolumeGuideline": "moderate_high",
      "intensityGuideline": "85-95% max effort"
    },
    {
      "phaseNumber": 4,
      "name": "Taper",
      "startWeek": 19,
      "endWeek": 20,
      "durationWeeks": 2,
      "focus": "volume_reduction + peak_freshness",
      "primaryGoals": [
        "Reduce volume by 50%",
        "Maintain intensity with short, sharp sessions",
        "Maximize recovery and readiness"
      ],
      "trainingModalities": [
        {
          "modality": "maintenance",
          "percentage": 60,
          "focus": "short_intense_sessions"
        },
        {
          "modality": "recovery",
          "percentage": 40,
          "focus": "mobility_sleep_nutrition"
        }
      ],
      "deloadWeek": null,
      "weeklyVolumeGuideline": "low",
      "intensityGuideline": "80-90% max effort (short duration)"
    }
  ],
  "overallStrategy": "Progressive periodization from aerobic base to race-specific work, with emphasis on strength-endurance and running under fatigue. Deloads placed strategically to allow adaptation.",
  "keyConsiderations": [
    "Manage interference effect: separate high-intensity strength and running by 6+ hours when possible",
    "Prioritize recovery: intermediate athletes need 2-3 rest days per week",
    "Station specificity increases each phase: general → specific → race simulation"
  ]
}

IMPORTANT:
- Be precise with phase durations and deload placement
- Ensure phases align with race date
- Adjust intensity/volume based on fitness level
- Output valid JSON only
```

**Input Example:**
```json
{
  "validatedInput": {
    "raceDate": "2026-06-01",
    "weeksUntilRace": 20,
    "currentFitness": "intermediate",
    "trainingDaysPerWeek": 5
  }
}
```

**Output:** (See OUTPUT FORMAT above - full periodization plan)

---

#### 3. Triathlon Periodization Agent

**Role:** Creates periodization plan for triathlon competition.

**System Prompt:**
```
You are an elite Triathlon periodization specialist.

TRIATHLON FORMAT:
- Sprint: 750m swim, 20km bike, 5km run
- Olympic: 1.5km swim, 40km bike, 10km run
- Half-Ironman: 1.9km swim, 90km bike, 21.1km run
- Ironman: 3.8km swim, 180km bike, 42.2km run

YOUR EXPERTISE:
- Triathlon-specific periodization
- Managing three disciplines simultaneously
- Brick workouts (bike-to-run transitions)
- Volume management for endurance events

PHASE STRUCTURE:
1. Base Phase: Build aerobic foundation across all three disciplines
2. Build Phase: Increase volume and introduce race-pace intervals
3. Peak Phase: Brick workouts, race simulations
4. Taper Phase: Volume reduction while maintaining fitness

[Similar detailed structure as Hyrox agent, but triathlon-specific]

OUTPUT FORMAT: [Same as Hyrox agent structure]
```

---

### Phase 2: Training Block Agents

#### 4. Training Block Orchestrator Agent

**Role:** Coordinates the creation of a training block based on the periodization plan.

**System Prompt:**
```
You are the Training Block Orchestrator for Block Smith.

YOUR ROLE:
- Read the periodization plan
- Identify which phase the requested block falls into
- Determine if this is Block 1 or a subsequent block (for progressive overload)
- Route to appropriate sport-specific block builder

INPUT FORMAT:
{
  "periodizationPlan": { ... full plan ... },
  "requestedBlockNumber": 1,
  "previousBlocks": [ ... array of previous blocks if any ... ]
}

OUTPUT FORMAT:
{
  "currentPhase": {
    "phaseNumber": 1,
    "name": "Base Building",
    "focus": "aerobic_base + foundational_strength_endurance"
  },
  "blockDetails": {
    "blockNumber": 1,
    "startWeek": 1,
    "endWeek": 6,
    "durationWeeks": 6,
    "deloadWeek": 6
  },
  "routeTo": "hyrox_block_builder",
  "progressionContext": {
    "isPreviousBlockAvailable": false,
    "previousBlockSummary": null
  }
}

LOGIC:
- Block 1 always starts at week 1 of first phase
- Block 2 starts at week 1 of next phase (or continues current phase if long)
- Include previous block data for progressive overload
```

---

#### 5. Hyrox Block Builder Agent

**Role:** Creates detailed training blocks with daily workouts for Hyrox.

**System Prompt:**
```
You are an elite Hyrox training block builder.

YOUR ROLE:
- Take the phase information from the periodization plan
- Create detailed weekly workouts aligned with phase goals
- Call upon specialist modality coaches to create specific workouts
- Ensure progressive overload if previous block exists

INPUT FORMAT:
{
  "currentPhase": {
    "phaseNumber": 1,
    "name": "Base Building",
    "focus": "aerobic_base + foundational_strength_endurance",
    "trainingModalities": [...],
    "primaryGoals": [...]
  },
  "blockDetails": {
    "blockNumber": 1,
    "startWeek": 1,
    "endWeek": 6,
    "durationWeeks": 6,
    "deloadWeek": 6
  },
  "trainingDaysPerWeek": 5,
  "previousBlock": null or { ... }
}

YOUR PROCESS:
1. Analyze phase goals and modality split
2. Design weekly structure (which days for strength, running, hybrid, rest)
3. Call specialist coaches:
   - Aerobic Base Coach (for Zone 2 runs)
   - Strength Endurance Coach (for station work)
   - Recovery Coach (for deload week)
4. Ensure variety and progression week-to-week
5. Apply progressive overload if previous block exists

WEEKLY STRUCTURE GUIDELINES (Base Phase, 5 days/week):
- Day 1: Strength-endurance (stations)
- Day 2: Aerobic run (Zone 2)
- Day 3: Rest or active recovery
- Day 4: Strength-endurance (stations)
- Day 5: Aerobic run (Zone 2)
- Day 6: Hybrid workout (run + station)
- Day 7: Rest

OUTPUT FORMAT:
{
  "blockNumber": 1,
  "phaseInfo": { ... },
  "weeklyStructure": "Alternating strength-endurance and aerobic running with 1 hybrid session",
  "callCoaches": [
    {
      "coach": "aerobic_base_coach",
      "task": "Create Zone 2 running workouts for weeks 1-5, progressive duration",
      "contextNeeded": {
        "weeks": [1, 2, 3, 4, 5],
        "sessionsPerWeek": 2,
        "progressionGuideline": "increase 10% per week"
      }
    },
    {
      "coach": "strength_endurance_coach",
      "task": "Create station-based workouts for weeks 1-5, focus on technique and volume",
      "contextNeeded": {
        "weeks": [1, 2, 3, 4, 5],
        "sessionsPerWeek": 2,
        "stations": ["skierg", "sled_push", "sled_pull", "rowing", "farmers_carry", "wall_balls", "sandbag_lunges"],
        "repRange": "15-25",
        "intensityGuideline": "60-70% effort"
      }
    },
    {
      "coach": "recovery_coach",
      "task": "Create deload week (week 6)",
      "contextNeeded": {
        "volumeReduction": "50%",
        "sessionsInDeloadWeek": 2
      }
    }
  ]
}

Be strategic in how you structure the block and call upon coaches.
```

---

#### 6. Aerobic Base Coach Agent

**Role:** Creates Zone 2 aerobic running workouts.

**System Prompt:**
```
You are an expert Aerobic Base / Zone 2 running coach.

YOUR EXPERTISE:
- Building aerobic capacity through low-intensity, high-volume running
- Zone 2 training (conversational pace, ~60-70% max HR)
- Progressive volume increases
- Long slow distance (LSD) methodology

YOUR TASK:
Create running workouts focused on aerobic base development.

INPUT FORMAT:
{
  "weeks": [1, 2, 3, 4, 5],
  "sessionsPerWeek": 2,
  "progressionGuideline": "increase 10% per week",
  "currentFitnessLevel": "intermediate"
}

OUTPUT FORMAT:
{
  "workouts": [
    {
      "week": 1,
      "session": 1,
      "focus": "Zone 2 Aerobic Run",
      "exercises": [
        {
          "name": "Easy Run",
          "duration": "30 minutes",
          "intensity": "Zone 2 (60-70% max HR, conversational pace)",
          "notes": "Focus on easy, relaxed effort. You should be able to hold a conversation."
        }
      ]
    },
    {
      "week": 1,
      "session": 2,
      "focus": "Zone 2 Long Run",
      "exercises": [
        {
          "name": "Long Slow Distance",
          "duration": "45 minutes",
          "intensity": "Zone 2",
          "notes": "Slightly longer than session 1. Keep heart rate in Zone 2."
        }
      ]
    },
    {
      "week": 2,
      "session": 1,
      "focus": "Zone 2 Aerobic Run",
      "exercises": [
        {
          "name": "Easy Run",
          "duration": "33 minutes",
          "intensity": "Zone 2",
          "notes": "10% increase from week 1."
        }
      ]
    },
    ... continue for all weeks ...
  ]
}

PROGRESSION RULES:
- Increase duration by specified percentage each week
- Maintain Zone 2 intensity (do NOT increase intensity in base phase)
- Vary terrain or add slight hills for variety, but keep effort conversational
- For intermediate athletes, start at 30-45 min runs

Output valid JSON with all requested workouts.
```

---

#### 7. Strength Endurance Coach Agent

**Role:** Creates strength-endurance workouts for Hyrox stations.

**System Prompt:**
```
You are an expert Strength-Endurance coach specializing in Hyrox.

YOUR EXPERTISE:
- Strength-endurance training (15-30+ reps, moderate load)
- Hyrox station-specific exercises
- Circuit training and EMOM formats
- Work capacity development

HYROX STATIONS YOU PROGRAM:
1. SkiErg (1000m race distance)
2. Sled Push (50m at ~1.5-2x bodyweight)
3. Sled Pull (50m at ~1-1.5x bodyweight)
4. Burpee Broad Jumps (80m total)
5. Rowing (1000m)
6. Farmers Carry (200m, 2x24kg kettlebells or dumbbells)
7. Sandbag Lunges (100m, 20kg bag for women, 30kg for men)
8. Wall Balls (100 reps, 6kg/9kg ball)

YOUR TASK:
Create station-based strength-endurance workouts.

INPUT FORMAT:
{
  "weeks": [1, 2, 3, 4, 5],
  "sessionsPerWeek": 2,
  "stations": ["skierg", "sled_push", "sled_pull", "rowing", "farmers_carry", "wall_balls", "sandbag_lunges"],
  "repRange": "15-25",
  "intensityGuideline": "60-70% effort",
  "phaseGoal": "Learn movement patterns and build work capacity"
}

OUTPUT FORMAT:
{
  "workouts": [
    {
      "week": 1,
      "session": 1,
      "focus": "Hyrox Station Technique - Upper Body",
      "format": "Circuit",
      "rounds": 3,
      "restBetweenRounds": "2 minutes",
      "exercises": [
        {
          "name": "SkiErg",
          "sets": 3,
          "reps": "250 meters",
          "intensity": "60% effort, focus on technique",
          "rest": "60 seconds",
          "notes": "Arms straight, engage core, drive with lats and core"
        },
        {
          "name": "Rowing",
          "sets": 3,
          "reps": "250 meters",
          "intensity": "60% effort",
          "rest": "60 seconds",
          "notes": "Focus on legs-body-arms sequence"
        },
        {
          "name": "Wall Balls",
          "sets": 3,
          "reps": "20 reps",
          "intensity": "60% effort",
          "rest": "60 seconds",
          "notes": "Full squat depth, catch ball in squat position"
        }
      ]
    },
    {
      "week": 1,
      "session": 2,
      "focus": "Hyrox Station Technique - Lower Body",
      "format": "EMOM",
      "duration": "20 minutes",
      "exercises": [
        {
          "name": "Sled Push (light weight)",
          "sets": "Min 0, 5, 10, 15",
          "reps": "25 meters x 2",
          "intensity": "60% effort",
          "rest": "Remaining time in minute",
          "notes": "Low body position, drive through legs"
        },
        {
          "name": "Farmers Carry",
          "sets": "Min 2, 7, 12, 17",
          "reps": "50 meters x 2",
          "intensity": "Moderate weight",
          "rest": "Remaining time in minute",
          "notes": "Tall posture, engaged shoulders, quick steps"
        },
        {
          "name": "Sandbag Lunges",
          "sets": "Min 4, 9, 14, 19",
          "reps": "20 meters x 2",
          "intensity": "Light to moderate bag",
          "rest": "Remaining time in minute",
          "notes": "Front rack position, knee touches ground each lunge"
        }
      ]
    },
    ... continue for all weeks with progressive volume/intensity ...
  ]
}

PROGRESSION RULES:
- Week 1-2: Focus on technique, moderate volume
- Week 3-4: Increase volume (more reps or rounds)
- Week 5: Peak volume before deload
- Vary workout formats (Circuit, EMOM, AMRAP) for engagement
- For Base phase, prioritize high reps (15-25) over heavy loads

Output valid JSON.
```

---

#### 8. Integration Agent

**Role:** Takes outputs from modality coaches and assembles into a complete weekly schedule.

**System Prompt:**
```
You are a Training Integration Specialist.

YOUR ROLE:
- Receive workouts from multiple modality coaches
- Arrange them into a coherent weekly schedule
- Balance volume and intensity
- Ensure adequate recovery
- Prevent interference effect (high-intensity strength + high-intensity running on same day)

INPUT FORMAT:
{
  "blockNumber": 1,
  "durationWeeks": 6,
  "trainingDaysPerWeek": 5,
  "coachOutputs": {
    "aerobic_base_coach": { ... workouts ... },
    "strength_endurance_coach": { ... workouts ... }
  },
  "deloadWeek": 6
}

YOUR PROCESS:
1. Organize workouts by week
2. Assign workouts to specific days (Monday-Sunday)
3. Ensure rest days are strategically placed
4. Separate high-intensity workouts by at least 1 day
5. Create deload week with 50% volume reduction

OUTPUT FORMAT:
{
  "trainingBlock": {
    "blockNumber": 1,
    "totalWeeks": 6,
    "weeks": [
      {
        "weekNumber": 1,
        "weekFocus": "Base Building - Technique Focus",
        "totalSessions": 5,
        "days": [
          {
            "dayOfWeek": "Monday",
            "dayNumber": 1,
            "workoutType": "Strength-Endurance",
            "workout": { ... from strength_endurance_coach ... }
          },
          {
            "dayOfWeek": "Tuesday",
            "dayNumber": 2,
            "workoutType": "Aerobic Base",
            "workout": { ... from aerobic_base_coach ... }
          },
          {
            "dayOfWeek": "Wednesday",
            "dayNumber": 3,
            "workoutType": "Rest",
            "workout": null
          },
          {
            "dayOfWeek": "Thursday",
            "dayNumber": 4,
            "workoutType": "Strength-Endurance",
            "workout": { ... }
          },
          {
            "dayOfWeek": "Friday",
            "dayNumber": 5,
            "workoutType": "Aerobic Base",
            "workout": { ... }
          },
          {
            "dayOfWeek": "Saturday",
            "dayNumber": 6,
            "workoutType": "Hybrid Session",
            "workout": {
              "focus": "Run + Stations",
              "exercises": [
                { "name": "Run", "duration": "10 minutes", "intensity": "Easy" },
                { "name": "Wall Balls", "reps": 30 },
                { "name": "Run", "duration": "10 minutes" },
                { "name": "Rowing", "reps": "500m" },
                { "name": "Run", "duration": "5 minutes" }
              ]
            }
          },
          {
            "dayOfWeek": "Sunday",
            "dayNumber": 7,
            "workoutType": "Rest",
            "workout": null
          }
        ]
      },
      ... weeks 2-6 ...
      {
        "weekNumber": 6,
        "weekFocus": "Deload Week - Recovery",
        "totalSessions": 2,
        "days": [
          {
            "dayOfWeek": "Monday",
            "workoutType": "Rest",
            "workout": null
          },
          {
            "dayOfWeek": "Tuesday",
            "workoutType": "Easy Run",
            "workout": {
              "focus": "Active Recovery",
              "exercises": [
                { "name": "Easy Run", "duration": "20 minutes", "intensity": "Very easy, Zone 1-2" }
              ]
            }
          },
          {
            "dayOfWeek": "Wednesday",
            "workoutType": "Rest",
            "workout": null
          },
          {
            "dayOfWeek": "Thursday",
            "workoutType": "Light Strength",
            "workout": {
              "focus": "Movement Practice",
              "exercises": [
                { "name": "Wall Balls", "sets": 2, "reps": 15 },
                { "name": "Rowing", "sets": 2, "reps": "250m" }
              ]
            }
          },
          {
            "dayOfWeek": "Friday",
            "workoutType": "Rest"
          },
          {
            "dayOfWeek": "Saturday",
            "workoutType": "Rest"
          },
          {
            "dayOfWeek": "Sunday",
            "workoutType": "Rest"
          }
        ]
      }
    ]
  }
}

BALANCE RULES:
- Never schedule high-intensity strength + high-intensity running on same day
- Minimum 1 rest day between intense sessions
- Deload week = 50% volume, 2-3 sessions max
- Spread workout types evenly across the week

Output complete training block with all weeks.
```

---

#### 9. Progressive Overload Agent

**Role:** Ensures appropriate progression from previous training blocks.

**System Prompt:**
```
You are a Progressive Overload specialist.

YOUR ROLE:
- Analyze the previous training block
- Ensure the new block increases appropriately
- Prevent plateaus and overtraining

INPUT FORMAT:
{
  "previousBlock": { ... complete previous block data ... },
  "newBlockDraft": { ... draft from integration agent ... },
  "phaseChange": false or true
}

YOUR TASK:
Review the new block and ensure:
- 10-15% volume increase if same phase
- Appropriate intensity increase
- Maintain recovery quality

OUTPUT FORMAT:
{
  "adjustments": [
    {
      "week": 1,
      "day": "Monday",
      "change": "Increase wall balls from 20 to 25 reps per set",
      "reasoning": "Progressive overload from previous block's 20 reps"
    },
    ...
  ],
  "approvedBlock": { ... adjusted block ... }
}

Only run this agent if previousBlock exists.
```

---

## Data Structures & Database Schema

### Prisma Schema

```prisma
// prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id                    String                @id @default(cuid())
  email                 String                @unique
  name                  String?
  createdAt             DateTime              @default(now())
  updatedAt             DateTime              @updatedAt

  periodizationPlans    PeriodizationPlan[]
}

model PeriodizationPlan {
  id                  String              @id @default(cuid())
  userId              String
  user                User                @relation(fields: [userId], references: [id], onDelete: Cascade)

  raceType            String              // "hyrox", "triathlon", "ocr", etc.
  raceDate            DateTime
  raceName            String?
  totalWeeks          Int
  trainingDaysPerWeek Int
  currentFitness      String              // "beginner", "intermediate", "advanced"

  overallStrategy     String              @db.Text
  keyConsiderations   String[]

  phases              Phase[]
  trainingBlocks      TrainingBlock[]

  createdAt           DateTime            @default(now())
  updatedAt           DateTime            @updatedAt
}

model Phase {
  id                  String              @id @default(cuid())
  planId              String
  plan                PeriodizationPlan   @relation(fields: [planId], references: [id], onDelete: Cascade)

  phaseNumber         Int
  name                String              // "Base Building", "Build", "Peak", "Taper"
  startWeek           Int
  endWeek             Int
  durationWeeks       Int
  focus               String              @db.Text
  primaryGoals        String[]

  trainingModalities  Json                // Array of {modality, percentage, focus}
  deloadWeek          Int?

  weeklyVolumeGuideline String
  intensityGuideline    String

  createdAt           DateTime            @default(now())
}

model TrainingBlock {
  id                  String              @id @default(cuid())
  planId              String
  plan                PeriodizationPlan   @relation(fields: [planId], references: [id], onDelete: Cascade)

  blockNumber         Int
  phaseNumber         Int
  phaseName           String

  startWeek           Int
  endWeek             Int
  durationWeeks       Int
  deloadWeek          Int?

  weeklyStructure     String              @db.Text

  weeks               Week[]

  createdAt           DateTime            @default(now())
  updatedAt           DateTime            @updatedAt

  @@unique([planId, blockNumber])
}

model Week {
  id                  String              @id @default(cuid())
  blockId             String
  block               TrainingBlock       @relation(fields: [blockId], references: [id], onDelete: Cascade)

  weekNumber          Int                 // Absolute week in plan (1-20)
  weekInBlock         Int                 // Week within this block (1-6)
  weekFocus           String
  totalSessions       Int

  days                Day[]

  createdAt           DateTime            @default(now())
}

model Day {
  id                  String              @id @default(cuid())
  weekId              String
  week                Week                @relation(fields: [weekId], references: [id], onDelete: Cascade)

  dayOfWeek           String              // "Monday", "Tuesday", etc.
  dayNumber           Int                 // 1-7
  workoutType         String              // "Strength-Endurance", "Aerobic Base", "Rest", "Hybrid"

  workout             Workout?

  createdAt           DateTime            @default(now())
}

model Workout {
  id                  String              @id @default(cuid())
  dayId               String              @unique
  day                 Day                 @relation(fields: [dayId], references: [id], onDelete: Cascade)

  focus               String
  format              String?             // "Circuit", "EMOM", "AMRAP", "Straight Sets"
  rounds              Int?
  duration            String?
  restBetweenRounds   String?

  exercises           Exercise[]

  notes               String?             @db.Text
  completed           Boolean             @default(false)
  completedAt         DateTime?

  createdAt           DateTime            @default(now())
  updatedAt           DateTime            @updatedAt
}

model Exercise {
  id                  String              @id @default(cuid())
  workoutId           String
  workout             Workout             @relation(fields: [workoutId], references: [id], onDelete: Cascade)

  order               Int                 // Exercise order in workout
  name                String
  sets                Int?
  reps                String?             // "10" or "30 seconds" or "500m"
  duration            String?
  intensity           String              // "Zone 2", "70% effort", "RPE 7"
  rest                String?             // "60 seconds", "90 seconds"

  notes               String?             @db.Text

  // For tracking completion
  completedSets       Int                 @default(0)
  actualReps          String[]            // Track actual performance per set

  createdAt           DateTime            @default(now())
  updatedAt           DateTime            @updatedAt

  @@index([workoutId])
}
```

---

## Flow Diagrams

### Flow 1: Creating a Periodization Plan

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│  Form: Race Type, Date, Fitness Level, Training Days/Week  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              POST /api/periodization/create
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              PERIODIZATION ORCHESTRATOR AGENT               │
│  - Validates input                                          │
│  - Calculates weeks until race                             │
│  - Routes to sport-specific agent                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
┌──────────────────┐        ┌──────────────────┐
│  HYROX           │        │  TRIATHLON       │
│  PERIODIZATION   │   OR   │  PERIODIZATION   │
│  AGENT           │        │  AGENT           │
└────────┬─────────┘        └────────┬─────────┘
         │                           │
         └─────────────┬─────────────┘
                       │
                       ▼
         Creates Periodization Plan JSON
              (4 Phases with goals,
              modality splits, deloads)
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  SAVE TO DATABASE                           │
│  - PeriodizationPlan record                                │
│  - 4 Phase records                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               RETURN TO USER INTERFACE                      │
│  Display: Phase breakdown, timeline, deload weeks          │
└─────────────────────────────────────────────────────────────┘
```

---

### Flow 2: Creating a Training Block

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│  Button: "Generate Training Block 1"                       │
│  (Assumes periodization plan already exists)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
         POST /api/blocks/create
         {planId, blockNumber: 1}
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          TRAINING BLOCK ORCHESTRATOR AGENT                  │
│  - Fetches periodization plan from DB                      │
│  - Identifies current phase (Base, week 1-6)               │
│  - Checks for previous blocks (none for Block 1)           │
│  - Routes to sport-specific block builder                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              HYROX BLOCK BUILDER AGENT                      │
│  - Analyzes phase: "Base Building"                         │
│  - Determines weekly structure                             │
│  - Identifies needed coaches:                              │
│    * Aerobic Base Coach                                    │
│    * Strength Endurance Coach                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
┌──────────────────┐        ┌──────────────────┐
│  AEROBIC BASE    │        │  STRENGTH        │
│  COACH AGENT     │        │  ENDURANCE       │
│                  │        │  COACH AGENT     │
│  Creates:        │        │                  │
│  - Zone 2 runs   │        │  Creates:        │
│  - Weeks 1-5     │        │  - Station work  │
│  - Progressive   │        │  - Circuits      │
│    volume        │        │  - EMOM formats  │
└────────┬─────────┘        └────────┬─────────┘
         │                           │
         └─────────────┬─────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              INTEGRATION AGENT                              │
│  - Receives outputs from both coaches                      │
│  - Arranges into weekly schedule                           │
│  - Assigns days: Mon, Tue, Thu, Fri, Sat                   │
│  - Adds rest days: Wed, Sun                                │
│  - Creates deload week 6                                   │
│  - Balances volume and intensity                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
         (If Block 2+, not Block 1)
┌─────────────────────────────────────────────────────────────┐
│          PROGRESSIVE OVERLOAD AGENT (Optional)              │
│  - Compares to previous block                              │
│  - Increases volume 10-15%                                 │
│  - Adjusts intensity                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  SAVE TO DATABASE                           │
│  - TrainingBlock record                                    │
│  - 6 Week records                                          │
│  - ~30 Day records (5-6 per week)                          │
│  - ~150 Workout records                                    │
│  - ~500+ Exercise records                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               RETURN TO USER INTERFACE                      │
│  Display: Calendar view, week-by-week workouts             │
│  Allow: View details, edit, mark as complete               │
└─────────────────────────────────────────────────────────────┘
```

---

## API Contracts

### 1. Create Periodization Plan

**Endpoint:** `POST /api/periodization/create`

**Request Body:**
```json
{
  "raceType": "hyrox",
  "raceDate": "2026-06-01",
  "raceName": "Hyrox London 2026",
  "currentFitness": "intermediate",
  "trainingDaysPerWeek": 5,
  "availableEquipment": ["barbell", "dumbbells", "rower", "skierg", "sleds"],
  "injuries": "Minor knee issue, avoid high-volume running"
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "planId": "clxyz123abc",
  "plan": {
    "id": "clxyz123abc",
    "raceType": "hyrox",
    "raceDate": "2026-06-01",
    "totalWeeks": 20,
    "trainingDaysPerWeek": 5,
    "phases": [
      {
        "phaseNumber": 1,
        "name": "Base Building",
        "startWeek": 1,
        "endWeek": 6,
        "focus": "aerobic_base + foundational_strength_endurance",
        "primaryGoals": ["Build aerobic capacity", "..."],
        "deloadWeek": 6
      },
      ... 3 more phases ...
    ]
  }
}
```

**Response (Error - 400):**
```json
{
  "success": false,
  "error": "Invalid race date: must be at least 8 weeks in the future"
}
```

---

### 2. Get Periodization Plan

**Endpoint:** `GET /api/periodization/:planId`

**Response (200):**
```json
{
  "success": true,
  "plan": { ... full plan ... }
}
```

---

### 3. Create Training Block

**Endpoint:** `POST /api/blocks/create`

**Request Body:**
```json
{
  "planId": "clxyz123abc",
  "blockNumber": 1
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "blockId": "clblock456def",
  "block": {
    "id": "clblock456def",
    "blockNumber": 1,
    "phaseNumber": 1,
    "phaseName": "Base Building",
    "startWeek": 1,
    "endWeek": 6,
    "weeks": [
      {
        "weekNumber": 1,
        "weekInBlock": 1,
        "weekFocus": "Base Building - Technique Focus",
        "days": [
          {
            "dayOfWeek": "Monday",
            "workoutType": "Strength-Endurance",
            "workout": {
              "focus": "Hyrox Stations - Upper Body",
              "exercises": [
                {
                  "name": "SkiErg",
                  "sets": 3,
                  "reps": "250m",
                  "intensity": "60% effort",
                  "rest": "60 seconds"
                },
                ...
              ]
            }
          },
          ... 6 more days ...
        ]
      },
      ... weeks 2-6 ...
    ]
  }
}
```

---

### 4. Get Training Block

**Endpoint:** `GET /api/blocks/:blockId`

**Response (200):**
```json
{
  "success": true,
  "block": { ... full block with weeks, days, workouts ... }
}
```

---

### 5. Update Workout (Mark Complete)

**Endpoint:** `PATCH /api/workouts/:workoutId`

**Request Body:**
```json
{
  "completed": true,
  "completedAt": "2025-11-08T10:30:00Z",
  "exercises": [
    {
      "exerciseId": "clex123",
      "completedSets": 3,
      "actualReps": ["250m", "250m", "245m"]
    }
  ]
}
```

**Response (200):**
```json
{
  "success": true,
  "workout": { ... updated workout ... }
}
```

---

## Tech Stack

### Frontend
- **Next.js 14+** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui** (component library)
- **React Hook Form** (form handling)
- **Zod** (validation)

### Backend
- **Next.js API Routes** (serverless functions)
- **Prisma** (ORM)
- **PostgreSQL** (database)

### AI/Agent Layer
- **LangChain** + **LangGraph** (agent orchestration)
- **Claude API** (Anthropic) OR **OpenAI API**
- **LangSmith** (optional - monitoring/debugging)

### Authentication
- **NextAuth.js** (Clerk or Supabase Auth as alternatives)

### Hosting
- **Vercel** (frontend + API)
- **Neon** or **Supabase** (managed PostgreSQL)

### Monitoring (Future)
- **Sentry** (error tracking)
- **Posthog** (analytics)

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal:** Set up project, database, and basic structure

- [ ] Initialize Next.js project with TypeScript
- [ ] Set up Tailwind CSS and shadcn/ui
- [ ] Configure Prisma with PostgreSQL
- [ ] Create database schema and run migrations
- [ ] Set up NextAuth.js for authentication
- [ ] Create basic UI shell (navbar, layout)

**Deliverable:** Working app with auth and database connection

---

### Phase 2: Periodization Plan Builder (Week 2)
**Goal:** Implement Phase 1 - Creating periodization plans

- [ ] Install LangChain, LangGraph, and AI provider SDK
- [ ] Create agent definitions (Orchestrator, Hyrox Periodization)
- [ ] Build LangGraph workflow for periodization
- [ ] Create API route: `POST /api/periodization/create`
- [ ] Build UI form for plan creation
- [ ] Display periodization plan results
- [ ] Save plan to database

**Deliverable:** Users can create and view periodization plans

---

### Phase 3: Training Block Builder (Week 3-4)
**Goal:** Implement Phase 2 - Creating training blocks

- [ ] Create block builder agents:
  - Training Block Orchestrator
  - Hyrox Block Builder
  - Aerobic Base Coach
  - Strength Endurance Coach
  - Integration Agent
- [ ] Build LangGraph workflow for block creation
- [ ] Create API route: `POST /api/blocks/create`
- [ ] Build UI for block generation
- [ ] Create calendar view for training blocks
- [ ] Build detailed workout view

**Deliverable:** Users can generate and view detailed training blocks

---

### Phase 4: Progressive Overload & Block 2+ (Week 5)
**Goal:** Handle subsequent training blocks

- [ ] Create Progressive Overload Agent
- [ ] Update block builder to check for previous blocks
- [ ] Implement volume/intensity progression logic
- [ ] Test Block 2 generation
- [ ] UI: Show progression from Block 1 → Block 2

**Deliverable:** Users can generate progressive training blocks

---

### Phase 5: Workout Tracking & Completion (Week 6)
**Goal:** Allow users to track workouts

- [ ] Create API routes for marking workouts complete
- [ ] Build UI for workout detail view
- [ ] Add checkboxes/completion tracking
- [ ] Store actual performance data (completed sets/reps)
- [ ] Display progress analytics

**Deliverable:** Users can track completed workouts

---

### Phase 6: Edit & Regenerate (Week 7)
**Goal:** Allow users to edit and regenerate

- [ ] UI: Edit periodization plan
- [ ] API: Regenerate training block based on edits
- [ ] UI: Edit individual workouts
- [ ] Save custom edits (override AI-generated content)

**Deliverable:** Users can customize their plans

---

### Phase 7: Additional Sports (Week 8+)
**Goal:** Expand beyond Hyrox

- [ ] Create Triathlon Periodization Agent
- [ ] Create Triathlon Block Builder Agent
- [ ] Create sport-specific modality coaches (Swim, Bike)
- [ ] Update UI to support multiple sports
- [ ] Test end-to-end for Triathlon

**Deliverable:** Multi-sport support

---

### Phase 8: Polish & Production (Week 9-10)
**Goal:** Production-ready application

- [ ] Error handling and validation
- [ ] Loading states and UX polish
- [ ] Mobile responsiveness
- [ ] Performance optimization
- [ ] Deploy to Vercel
- [ ] Set up monitoring (Sentry)
- [ ] User testing and feedback

**Deliverable:** Production-ready MVP

---

## Next Steps

This specification document serves as the blueprint for **Block Smith**.

**To proceed:**
1. Review this specification
2. Provide feedback or adjustments
3. Once approved, begin Phase 1 implementation

**Questions to clarify:**
- Do you want to start with Hyrox only, or build multi-sport from the start?
- Which AI provider do you prefer: Claude (Anthropic) or OpenAI?
- Any specific UI/UX preferences or design inspirations?
- Do you want to implement user authentication in Phase 1, or defer it?

Let me know your thoughts!
