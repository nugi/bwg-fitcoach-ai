#!/usr/bin/env python3
"""Seed initial exercise catalog into Firestore."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-5c6554ad3943"

EXERCISES = [
    {
        "id": "barbell-back-squat",
        "name": "Barbell Back Squat",
        "muscle_group": "legs",
        "equipment": "barbell",
        "difficulty": "intermediate",
        "form_cues": "Keep chest up, knees tracking over toes, break parallel, drive through mid-foot.",
        "target_muscles": ["quadriceps", "glutes", "hamstrings"],
        "calories_per_min": 8.0,
    },
    {
        "id": "push-up",
        "name": "Push-up",
        "muscle_group": "chest",
        "equipment": "bodyweight",
        "difficulty": "beginner",
        "form_cues": "Elbows angled 45 degrees from torso, keep core tight and hips level, full lockout at top.",
        "target_muscles": ["pectoralis major", "triceps", "anterior deltoids"],
        "calories_per_min": 6.0,
    },
    {
        "id": "pull-up",
        "name": "Pull-up",
        "muscle_group": "back",
        "equipment": "pull-up bar",
        "difficulty": "intermediate",
        "form_cues": "Engage lats before pulling, lead with chest toward the bar, full control on descent.",
        "target_muscles": ["latissimus dorsi", "biceps", "rhomboids"],
        "calories_per_min": 7.0,
    },
    {
        "id": "dumbbell-romanian-deadlift",
        "name": "Dumbbell Romanian Deadlift",
        "muscle_group": "hamstrings",
        "equipment": "dumbbells",
        "difficulty": "beginner",
        "form_cues": "Hinge backwards at hips with soft knees, keep dumbbells close to shins, flat back.",
        "target_muscles": ["hamstrings", "glutes", "lower back"],
        "calories_per_min": 6.5,
    },
    {
        "id": "dumbbell-overhead-press",
        "name": "Dumbbell Overhead Press",
        "muscle_group": "shoulders",
        "equipment": "dumbbells",
        "difficulty": "beginner",
        "form_cues": "Press dumbbells overhead without hyperextending lower back, brace abs throughout.",
        "target_muscles": ["anterior deltoids", "lateral deltoids", "triceps"],
        "calories_per_min": 5.5,
    },
    {
        "id": "plank",
        "name": "Plank",
        "muscle_group": "core",
        "equipment": "bodyweight",
        "difficulty": "beginner",
        "form_cues": "Hold a rigid line from head to heels, squeeze glutes and brace abdominal wall.",
        "target_muscles": ["rectus abdominis", "transverse abdominis", "obliques"],
        "calories_per_min": 4.0,
    },
]


def seed_database():
    print(f"Connecting to Firestore for project: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection("exercises")

    for item in EXERCISES:
        doc_id = item["id"]
        collection.document(doc_id).set(item)
        print(f"Seeded exercise: {item['name']} (ID: {doc_id})")

    print(f"Successfully seeded {len(EXERCISES)} exercises into Firestore!")


if __name__ == "__main__":
    seed_database()
