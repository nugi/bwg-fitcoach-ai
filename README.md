# 🏋️ FitCoach AI

> **Your intelligent conversational fitness coach and workout companion powered by Google Gemini, Google Agent Development Kit (ADK), and Agent Platform.**

Built during **Build with Gemini: World Tour (Track 3: Agent-First Apps)**.

---

## 🌟 Overview

**FitCoach AI** is a conversational AI agent designed to help fitness enthusiasts and everyday movers plan personalized workout routines, discover exercises with form cues and target muscles, log completed sessions, and compute physiological metrics (such as heart rate zones and 1-rep max estimations).

### ✨ Key Features & Architecture

- 🤖 **Agent Core (ADK + Gemini)**: Autonomous reasoning loop built with Google ADK and deployed to Agent Runtime on Google Cloud.
- 🗄️ **Exercise Catalog & Firestore Data**: Structured database lookup for workouts and exercises (`lookup_exercises`, `log_workout`, `calculate_macros`).
- 🪟 **Agent-to-User Interface (A2UI)**: Rich interactive cards, tables, and workout routines rendered natively in the frontend interface.
- 🎨 **Motivational Media Generation**: Post-workout meal concepts and milestone badges with Gemini multimodal imaging.
- 🧪 **Code Sandbox**: Calculates physiological formulas (1RM, training heart rate zones, pacing) safely in an isolated sandbox.
- 🌐 **FastAPI Web Frontend**: Lightweight proxy talking to the deployed agent over the **A2A Protocol** with a responsive chat UI and built-in A2UI card renderer.

---

## 📁 Repository Structure

```
├── fitcoach-ai/                  # ADK Agent backend
│   ├── app/
│   │   ├── agent.py              # Agent definition, system instructions, and tool bindings
│   │   ├── tools/                # Function tools (exercises, logging, metrics)
│   │   ├── a2ui_utils.py         # A2UI callback and surface generation
│   │   └── fast_api_app.py       # A2A / FastAPI endpoint
│   ├── tests/                    # Unit and integration test suite
│   ├── pyproject.toml            # Backend dependencies
│   └── agents-cli-manifest.yaml  # Agent deployment manifest
├── frontend/                     # FastAPI proxy + Web Chat UI
│   ├── main.py                   # A2A protocol proxy (authenticates to Agent Runtime)
│   ├── requirements.txt          # Frontend dependencies
│   └── static/
│       └── index.html            # Chat interface & A2UI component renderer
├── project_brief.md              # Project specifications & design brief
└── README.md                     # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) or standard `pip`
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`)
- [agents-cli](https://google.github.io/agents-cli/) (`uv tool install google-agents-cli`)

---

### 1. Running the Agent Backend

Navigate to `fitcoach-ai`:

```bash
cd fitcoach-ai
uv sync
uv run adk web
```

Or run the test suite:

```bash
uv run pytest
```

---

### 2. Running the Frontend Chat UI

Navigate to `frontend`:

```bash
cd frontend
pip install -r requirements.txt

# Configure your deployed agent resource name (or use defaults in .env)
export AGENT_ENGINE_RESOURCE_NAME="<your-reasoning-engine-resource-name>"
export AGENT_DIRECTORY="app"

python main.py
```

Open **http://localhost:8080** in your browser to chat with FitCoach AI.

---

## 🛠️ Deployment & Technologies

- **Agent Engine / Agent Runtime**: Serverless ADK agent execution on Google Cloud Vertex AI.
- **A2A Protocol**: Inter-agent and proxy communication standard.
- **A2UI**: Declarative, streaming UI component standard.
- **Firestore & Cloud Storage**: Persistence for workout logs and assets.

---

## 📄 License

Apache-2.0
