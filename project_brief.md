# My agent: FitCoach AI
One-liner: A conversational agent that helps fitness enthusiasts and everyday movers plan personalized workouts and track progress with a catalog of exercises and training routines.

Tool coverage:
- Memory: User goals (endurance, hypertrophy, weight loss), injury history, available workout equipment, and weekly scheduling preferences.
- Tools: Exercise database lookup (`lookup_exercises`), workout logger (`log_workout`), and nutrition/calorie calculator (`calculate_macros`).
- Catalog/UI: Exercise cards (name, target muscles, form cues, difficulty) and weekly training schedule tables rendered via A2UI.
- Image & Video gen: Motivational milestone badges, post-workout meals, and short exercise form videos via Google Omni (`gemini-omni-flash-preview`).
- Sandbox: Code sandbox for running physiological formulas (Heart Rate training zones, 1-Rep Max estimations, pace calculations).

Recommended for every project: memory, storage, tools, image & video generation, A2UI
Agent-specific / stretch (pick what fits): Code sandbox for training calculations, Cloud Trace for observability
