"""Fitness, cardio, and physiological calculation tools."""

from typing import Any


def calculate_heart_rate_zones(
    age: int,
    resting_heart_rate: int = 60,
    max_heart_rate: int | None = None,
) -> dict[str, Any]:
    """Calculate personalized 5-zone cardiovascular training heart rate bands using the Karvonen formula.

    Args:
        age: The athlete's age in years (must be between 10 and 100).
        resting_heart_rate: Athlete's measured resting heart rate in BPM (default: 60).
        max_heart_rate: Optional measured maximum heart rate in BPM. If not provided, estimated as 220 - age.

    Returns:
        A dictionary with max heart rate, heart rate reserve, and min/max BPM thresholds for Zones 1 through 5.
    """
    if age < 10 or age > 110:
        return {"error": "Please provide a valid age between 10 and 110."}

    max_hr = max_heart_rate if max_heart_rate is not None and max_heart_rate > 0 else (220 - age)
    hrr = max_hr - resting_heart_rate

    def karvonen(pct: float) -> int:
        return round(resting_heart_rate + (pct * hrr))

    zones = {
        "athlete_stats": {
            "age": age,
            "resting_heart_rate_bpm": resting_heart_rate,
            "max_heart_rate_bpm": max_hr,
            "heart_rate_reserve_bpm": hrr,
        },
        "zones": [
            {
                "zone": "Zone 1",
                "name": "Active Recovery / Warmup",
                "intensity_pct": "50% - 60%",
                "min_bpm": karvonen(0.50),
                "max_bpm": karvonen(0.60),
                "purpose": "Promotes recovery, easy warm-up, conversational pace, burns mostly fat.",
            },
            {
                "zone": "Zone 2",
                "name": "Aerobic / Base Endurance",
                "intensity_pct": "60% - 70%",
                "min_bpm": karvonen(0.60),
                "max_bpm": karvonen(0.70),
                "purpose": "Builds mitochondrial density, cardiovascular endurance, and fat oxidation efficiency.",
            },
            {
                "zone": "Zone 3",
                "name": "Tempo / Aerobic Power",
                "intensity_pct": "70% - 80%",
                "min_bpm": karvonen(0.70),
                "max_bpm": karvonen(0.80),
                "purpose": "Improves cardiovascular efficiency and pacing endurance for moderate-to-hard continuous efforts.",
            },
            {
                "zone": "Zone 4",
                "name": "Lactate Threshold / Anaerobic Endurance",
                "intensity_pct": "80% - 90%",
                "min_bpm": karvonen(0.80),
                "max_bpm": karvonen(0.90),
                "purpose": "Increases lactate clearance threshold, sustainable speed, and hard interval endurance.",
            },
            {
                "zone": "Zone 5",
                "name": "VO2 Max / Maximum Effort",
                "intensity_pct": "90% - 100%",
                "min_bpm": karvonen(0.90),
                "max_bpm": max_hr,
                "purpose": "Develops peak sprinting speed, neuromuscular power, and maximal aerobic capacity (VO2 max).",
            },
        ],
    }
    return zones
