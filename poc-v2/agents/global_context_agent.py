"""
Global Context Agent - Central data store for athlete profile, training config, and periodization plan
NOT an LLM agent - pure data structure that all other agents query

This is the SINGLE SOURCE OF TRUTH for all training data.
All agents should query this context rather than receiving data directly.
"""
from typing import Dict, Any, Optional


class GlobalContextAgent:
    """Stores global context that all agents can query - single source of truth"""

    def __init__(
        self,
        athlete_profile: Dict[str, Any],
        training_config: Dict[str, Any],
        periodization_plan: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Global Context

        Args:
            athlete_profile: Age, fitness level, physiological data, equipment
            training_config: sessionsPerWeek, availableDays
            periodization_plan: Complete periodization plan (optional, can be set later)
        """
        self.athlete_profile = athlete_profile
        self.training_config = training_config
        self.periodization_plan = periodization_plan
        self.training_rules = self._establish_training_rules()
        self.calculated_zones = self._calculate_hr_zones()

    def _establish_training_rules(self) -> Dict[str, Any]:
        """Define training rules based on sport science"""
        return {
            "intensityDistribution": {
                "easy": 0.70,      # 70% of total time
                "moderate": 0.20,  # 20% of total time
                "hard": 0.10       # 10% of total time
            },
            "hyroxStations": [
                "skierg_1000m",
                "sled_push_50m",
                "sled_pull_50m",
                "burpee_broad_jumps_80m",
                "rowing_1000m",
                "farmers_carry_200m",
                "sandbag_lunges_100m",
                "wall_balls_100reps"
            ],
            "recoveryGuidelines": {
                "hardSessionGap": "48_hours_minimum",
                "deloadFrequency": "every_4_6_weeks",
                "taperDuration": "1_2_weeks"
            },
            "progressionRules": {
                "volumeIncrease": "10_percent_per_week_max",
                "intensityProgression": "conservative_during_base_aggressive_during_build"
            }
        }

    def _calculate_hr_zones(self) -> Dict[str, Any]:
        """Calculate heart rate zones from athlete profile"""
        physiological_data = self.athlete_profile.get("physiologicalData", {})
        hr_max = physiological_data.get("hrMax")

        if not hr_max:
            return {}

        return {
            "zone1": {
                "name": "Recovery",
                "low": int(hr_max * 0.50),
                "high": int(hr_max * 0.60),
                "purpose": "Active recovery"
            },
            "zone2": {
                "name": "Aerobic Base",
                "low": int(hr_max * 0.60),
                "high": int(hr_max * 0.70),
                "purpose": "Endurance building",
                "description": "Easy conversational pace"
            },
            "zone3": {
                "name": "Tempo",
                "low": int(hr_max * 0.70),
                "high": int(hr_max * 0.80),
                "purpose": "Lactate threshold development"
            },
            "zone4": {
                "name": "Threshold",
                "low": int(hr_max * 0.80),
                "high": int(hr_max * 0.90),
                "purpose": "Race pace work"
            },
            "zone5": {
                "name": "VO2 Max",
                "low": int(hr_max * 0.90),
                "high": hr_max,
                "purpose": "Maximum aerobic capacity"
            }
        }

    def set_periodization_plan(self, plan: Dict[str, Any]) -> None:
        """Set the periodization plan after initialization"""
        self.periodization_plan = plan

    def get_context(self) -> Dict[str, Any]:
        """Return complete global context"""
        return {
            "athleteProfile": self.athlete_profile,
            "trainingConfig": self.training_config,
            "periodizationPlan": self.periodization_plan,
            "trainingRules": self.training_rules,
            "calculatedZones": self.calculated_zones
        }

    # ===== Training Configuration Queries =====

    def get_sessions_per_week(self) -> int:
        """Get number of training sessions per week"""
        return self.training_config.get("sessionsPerWeek", 5)

    def get_available_days(self) -> list:
        """Get available training days"""
        return self.training_config.get("availableDays", [])

    # ===== Periodization Plan Queries =====

    def get_current_phase(self, week_number: int) -> Optional[Dict[str, Any]]:
        """Get the phase for a given week number"""
        if not self.periodization_plan or "phases" not in self.periodization_plan:
            return None

        for phase in self.periodization_plan["phases"]:
            if phase["startWeek"] <= week_number <= phase["endWeek"]:
                return phase
        return None

    def get_phase_by_number(self, phase_number: int) -> Optional[Dict[str, Any]]:
        """Get a phase by its phase number"""
        if not self.periodization_plan or "phases" not in self.periodization_plan:
            return None

        for phase in self.periodization_plan["phases"]:
            if phase["phaseNumber"] == phase_number:
                return phase
        return None

    def get_archetype_guidance(self, phase_number: int) -> Optional[Dict[str, Any]]:
        """Get archetype scheduling guidance for a specific phase"""
        phase = self.get_phase_by_number(phase_number)
        if phase:
            return phase.get("archetypeSchedulingGuidance")
        return None

    def get_selected_archetypes(self, phase_number: int) -> list:
        """Get selected archetypes for a specific phase"""
        phase = self.get_phase_by_number(phase_number)
        if phase:
            return phase.get("selectedArchetypes", [])
        return []

    def get_progression_guidelines(self, phase_number: int) -> Optional[str]:
        """Get progression guidelines for a specific phase"""
        phase = self.get_phase_by_number(phase_number)
        if phase:
            return phase.get("progressionGuidelines")
        return None

    # ===== Athlete Profile Queries =====

    def get_athlete_data(self, key: str) -> Any:
        """Query specific athlete data"""
        return self.athlete_profile.get(key)

    def get_hr_zones(self) -> Dict[str, Any]:
        """Get calculated HR zones"""
        return self.calculated_zones

    def get_hr_zone(self, zone_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific HR zone by name (e.g., 'zone2')"""
        return self.calculated_zones.get(zone_name)

    def get_threshold_paces(self) -> Optional[Dict[str, str]]:
        """Get athlete's threshold paces"""
        return self.athlete_profile.get("physiologicalData", {}).get("thresholdPaces")

    def get_equipment(self) -> Optional[Dict[str, Any]]:
        """Get athlete's available equipment"""
        return self.athlete_profile.get("equipment")

    def get_estimated_maxes(self) -> Optional[Dict[str, str]]:
        """Get athlete's estimated 1RM maxes"""
        return self.athlete_profile.get("estimatedMaxes")

    # ===== Training Rules Queries =====

    def get_training_rule(self, key: str) -> Any:
        """Query specific training rule"""
        return self.training_rules.get(key)
