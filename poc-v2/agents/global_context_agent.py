"""
Global Context Agent - Central data store for athlete profile and training rules
NOT an LLM agent - pure data structure that all other agents query
"""
from typing import Dict, Any


class GlobalContextAgent:
    """Stores global context that all agents can query"""

    def __init__(self, athlete_profile: Dict[str, Any], block_configuration: Dict[str, Any]):
        self.athlete_profile = athlete_profile
        self.block_configuration = block_configuration
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

    def get_context(self) -> Dict[str, Any]:
        """Return complete global context"""
        return {
            "athleteProfile": self.athlete_profile,
            "blockConfiguration": self.block_configuration,
            "trainingRules": self.training_rules,
            "calculatedZones": self.calculated_zones
        }

    def get_athlete_data(self, key: str) -> Any:
        """Query specific athlete data"""
        return self.athlete_profile.get(key)

    def get_training_rule(self, key: str) -> Any:
        """Query specific training rule"""
        return self.training_rules.get(key)
