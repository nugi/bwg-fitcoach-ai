"""Firestore client and tool implementations for FitCoach AI."""

import datetime
from typing import Any

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

PROJECT_ID = "qwiklabs-gcp-03-5c6554ad3943"

_db = None


def get_db() -> firestore.Client:
    """Lazy initialize Firestore client with explicit project ID."""
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db


def list_exercises(muscle_group: str = "", equipment: str = "") -> list[dict[str, Any]]:
    """Look up available exercises from the exercise catalog.

    Args:
        muscle_group: Optional filter by muscle group (e.g. 'legs', 'chest', 'back', 'core', 'shoulders').
        equipment: Optional filter by equipment required (e.g. 'bodyweight', 'dumbbells', 'barbell', 'pull-up bar').

    Returns:
        A list of exercises matching the criteria.
    """
    db = get_db()
    query = db.collection("exercises")

    if muscle_group:
        query = query.where(filter=FieldFilter("muscle_group", "==", muscle_group.lower().strip()))
    if equipment:
        query = query.where(filter=FieldFilter("equipment", "==", equipment.lower().strip()))

    docs = query.stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        results.append(data)
    return results


def get_exercise_details(exercise_name: str) -> dict[str, Any]:
    """Retrieve in-depth form cues, muscle targets, and instructions for a specific exercise.

    Args:
        exercise_name: The name or slug of the exercise (e.g. 'Barbell Back Squat', 'Push-up').

    Returns:
        Exercise information including form cues and target muscles, or a message if not found.
    """
    db = get_db()
    slug = exercise_name.lower().strip().replace(" ", "-")

    # Try document by ID first
    doc = db.collection("exercises").document(slug).get()
    if doc.exists:
        return doc.to_dict()

    # Search by matching name case-insensitively
    docs = db.collection("exercises").stream()
    for d in docs:
        data = d.to_dict()
        if data.get("name", "").lower() == exercise_name.lower().strip():
            return data

    return {"error": f"Exercise '{exercise_name}' not found in the catalog."}


def log_workout(
    exercise_name: str,
    sets: int,
    reps: int,
    weight_lbs: float = 0.0,
    notes: str = "",
) -> str:
    """Log a completed workout set to the athlete's workout history in Firestore.

    Args:
        exercise_name: Name of the exercise performed (e.g. 'Barbell Back Squat').
        sets: Number of completed sets.
        reps: Number of reps per set.
        weight_lbs: Weight used in pounds (0.0 for bodyweight exercises).
        notes: Optional athlete notes, RPE, or feelings about the set.

    Returns:
        A confirmation message with the saved workout record ID.
    """
    db = get_db()
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    doc_ref = db.collection("workout_logs").document()

    record = {
        "id": doc_ref.id,
        "exercise_name": exercise_name,
        "sets": sets,
        "reps": reps,
        "weight_lbs": weight_lbs,
        "notes": notes,
        "logged_at": timestamp,
    }
    doc_ref.set(record)
    return f"Logged workout successfully: {sets} sets x {reps} reps of {exercise_name} (Record ID: {doc_ref.id})"


def get_recent_workouts(limit: int = 5) -> list[dict[str, Any]]:
    """Retrieve the athlete's recently logged workouts.

    Args:
        limit: Maximum number of recent workout entries to return (default: 5).

    Returns:
        A list of recent workout logs ordered by timestamp.
    """
    db = get_db()
    docs = (
        db.collection("workout_logs")
        .order_by("logged_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    results = [doc.to_dict() for doc in docs]
    return results
