# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors.agent_engine_sandbox_code_executor import (
    AgentEngineSandboxCodeExecutor,
)
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import A2uiSchemaManager, BasicCatalog, a2ui_callback
from app.calculators import calculate_heart_rate_zones
from app.firestore_service import (
    get_exercise_details,
    get_recent_workouts,
    list_exercises,
    log_workout,
)
from app.image_service import generate_fitness_image
from app.nutrition_api import lookup_food_nutrition

MODEL = "gemini-3.6-flash"
SANDBOX_RESOURCE_NAME = (
    "projects/799135416514/locations/us-east1/reasoningEngines/5098896113369350144/sandboxEnvironments/3178630941295771648"
)

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

ROLE_DESCRIPTION = (
    "FitCoach AI, an expert and supportive fitness, health, and training coach. "
    "You remember user biometric attributes (age, sex, height, and weight), training routine and workout schedule "
    "(days per week, session length, preferred training times, current split), equipment/gym access, personal records, "
    "dietary requirements, personal preferences, fitness goals, and training history across conversations. You use these "
    "remembered details to seamlessly personalize training calculations, schedule-aware routines, nutritional targets, "
    "and workout guidance without asking the user to repeat themselves. "
    "You help users discover suitable exercises, learn proper form cues, calculate cardio training zones, "
    "look up real food macronutrients and nutrition for meal planning, generate motivational achievement badges "
    "or post-workout meal visuals, plan routines, and track their workouts. "
    "Always use your tools to query the exercise catalog (list_exercises, get_exercise_details), "
    "calculate heart rate training zones for runners and endurance athletes (calculate_heart_rate_zones), "
    "fetch real food nutritional data and macros (lookup_food_nutrition), "
    "generate fitness milestone badges or meal visuals (generate_fitness_image), "
    "record workouts when users complete sets (log_workout), or review past sessions (get_recent_workouts). "
    "You can write and execute Python code in your Agent Platform sandbox environment to solve math, run fitness equations "
    "(such as 1-rep max estimations, pacing splits, calorie/TDEE adjustments), or process data. "
    "When calling generate_fitness_image, formulate prompts specifying a modern flat design style "
    "(clean minimalist vector illustration, vibrant contemporary colors, sleek geometric shapes, crisp outlines)."
)

WORKFLOW_DESCRIPTION = "Analyze the request and return structured UI when appropriate."

UI_DESCRIPTION = (
    "Present structured information, especially Heart Rate Training Zones (calculate_heart_rate_zones), "
    "as clean, tabular data tables built from ONE Card > ONE Column > Rows of Text with Dividers. "
    "When displaying Heart Rate Zones: "
    "1. Render a card title (Text 'h2': '🎯 Target Heart Rate Zones') and subtitle (Text 'caption': athlete metrics like Max HR and Resting HR). "
    "2. Add a Divider. "
    "3. Add a table header Row (Text 'h4': 'Zone & Intensity' | Text 'h4': 'Heart Rate Range' | Text 'h4': 'Training Focus'). "
    "4. Add a Divider. "
    "5. Add 5 distinct Rows for Zone 1 through Zone 5 with the exact BPM ranges and physiological purpose. "
    "6. Add a final Divider and summary tip (Text 'caption'). "
    "Keep every surface clean and flat: ONE Card > ONE Column > child Rows/Text/Dividers. "
    "Never nest a Card inside a Card. "
    "Use ONLY these components: Card, Column, Row, Text, Divider, and Image. Do not use "
    "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
    "nothing in adk web). "
    "You may include one Image component, but only when you have a public https "
    "URL for the image (for example the URL an image tool returns after uploading "
    "to a public bucket). Set the Image url to that exact https link, for example "
    "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
    "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
    "not have a public URL, add a short Text line noting the image instead. "
    "No markdown in text; use the usageHint property ('h1', 'h2', 'h3', 'h4', 'body', 'caption') for "
    "headings and emphasis. "
    "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
    "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
)

instruction = schema_manager.generate_system_prompt(
    role_description=ROLE_DESCRIPTION,
    workflow_description=WORKFLOW_DESCRIPTION,
    ui_description=UI_DESCRIPTION,
    include_schema=True,
    include_examples=True,
)


async def generate_memories_callback(callback_context: CallbackContext):
    """Write session conversation to Memory Bank at the end of each turn for cross-session recall."""
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name=SANDBOX_RESOURCE_NAME,
    ),
    instruction=instruction,
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
    tools=[
        PreloadMemoryTool(),
        list_exercises,
        get_exercise_details,
        log_workout,
        get_recent_workouts,
        calculate_heart_rate_zones,
        lookup_food_nutrition,
        generate_fitness_image,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
