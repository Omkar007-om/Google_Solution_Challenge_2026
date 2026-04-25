# 🛡️ SAR Multi-Agent Backend

> **Production-ready FastAPI backend** for Situation Analysis Report (SAR) generation,
> powered by a modular multi-agent pipeline architecture.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FastAPI Application                           │
│  ┌──────────┐  ┌─────────────┐  ┌────────────┐  ┌──────────────────┐  │
│  │  Routes   │→ │  Services   │→ │Orchestrator│→ │  Agent Pipeline  │  │
│  │ /analyze  │  │  (caching)  │  │ (tracing)  │  │                  │  │
│  │ /pipeline │  └─────────────┘  └────────────┘  │ ┌──────────────┐ │  │
│  │ /health   │                                   │ │ InputHandler │ │  │
│  └──────────┘                                    │ │     ↓        │ │  │
│                                                  │ │Preprocessing │ │  │
│  ┌──────────────────────────────────────────┐    │ │     ↓        │ │  │
│  │            Cross-Cutting Concerns        │    │ │FeatureProc.  │ │  │
│  │  • Request ID middleware (X-Request-ID)  │    │ │     ↓        │ │  │
│  │  • CORS middleware                       │    │ │AnalysisEngine│ │  │
│  │  • Structured JSON logging               │    │ │     ↓        │ │  │
│  │  • TTL cache with LRU eviction           │    │ │OutputFormat. │ │  │
│  │  • Exception hierarchy                   │    │ └──────────────┘ │  │
│  └──────────────────────────────────────────┘    └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📂 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app factory & lifecycle
│   ├── config.py               # pydantic-settings configuration
│   │
│   ├── agents/                 # 🤖 Pipeline agents (one per file)
│   │   ├── __init__.py         # Re-exports all agent classes
│   │   ├── base.py             # BaseAgent ABC (timeout, retry, logging)
│   │   ├── agent_input_handler.py
│   │   ├── agent_preprocessing.py
│   │   ├── agent_feature_processing.py
│   │   ├── agent_analysis_engine.py
│   │   └── agent_output_formatter.py
│   │
│   ├── core/                   # ⚙️ Framework internals
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # Sequential pipeline runner
│   │   ├── exceptions.py       # Domain exception hierarchy
│   │   ├── logger.py           # Structured JSON/text logger
│   │   ├── cache.py            # In-memory TTL + LRU cache
│   │   └── middleware.py       # Request ID & timing middleware
│   │
│   ├── models/                 # 📐 Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py          # Request, Response, Error models
│   │
│   ├── routes/                 # 🌐 API endpoints
│   │   ├── __init__.py
│   │   ├── analyze.py          # POST /api/v1/analyze
│   │   └── pipeline.py         # GET  /api/v1/pipeline/info
│   │
│   ├── services/               # 💼 Business logic layer
│   │   ├── __init__.py
│   │   └── pipeline_service.py # Cache-aware pipeline execution
│   │
│   └── utils/                  # 🔧 Shared utilities
│       ├── __init__.py
│       └── helpers.py          # timed(), safe_serialize(), etc.
│
├── .env                        # Environment variables
├── .env.example                # Documented env template
├── requirements.txt            # Python dependencies
├── run.py                      # CLI server launcher
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env as needed
```

### 3. Run the Server

```bash
# Option A: CLI runner (recommended)
python run.py

# Option B: Direct uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Explore

| URL | Description |
|-----|-------------|
| `http://localhost:8000/` | API index |
| `http://localhost:8000/docs` | Swagger UI (interactive) |
| `http://localhost:8000/redoc` | ReDoc (readable) |
| `http://localhost:8000/health` | Health check + cache stats |

---

## 📡 API Reference

### `POST /api/v1/analyze`

Run the full SAR analysis pipeline.

**Request:**
```json
{
  "input_data": {
    "user_id": "USR-001",
    "transactions": [
      {"amount": 15000, "type": "wire", "timestamp": "2026-04-25T10:00:00Z"},
      {"amount": 3200,  "type": "deposit", "timestamp": "2026-04-25T11:30:00Z"},
      {"amount": 52000, "type": "wire", "timestamp": "2026-04-25T14:00:00Z"},
      {"amount": 8700,  "type": "ach", "timestamp": "2026-04-25T15:45:00Z"}
    ]
  }
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "report_id": "SAR-USR-001",
    "generated_at": "2026-04-25T18:00:00.123456+00:00",
    "user_id": "USR-001",
    "summary": {
      "total_transactions": 4,
      "total_amount": 78900.0,
      "avg_amount": 19725.0,
      "max_amount": 52000.0,
      "min_amount": 3200.0,
      "high_value_count": 2
    },
    "risk_assessment": {
      "score": 65,
      "level": "HIGH",
      "contributing_factors": [
        "High cumulative transaction volume",
        "Elevated average transaction size",
        "Single very-high-value transaction"
      ]
    },
    "status": "SAR Generated"
  },
  "metadata": {
    "total_duration_s": 0.0023,
    "agents_executed": 5,
    "trace": [
      {"step": 1, "agent": "InputHandler",      "status": "success", "duration_s": 0.0001},
      {"step": 2, "agent": "Preprocessing",      "status": "success", "duration_s": 0.0003},
      {"step": 3, "agent": "FeatureProcessing",  "status": "success", "duration_s": 0.0002},
      {"step": 4, "agent": "AnalysisEngine",     "status": "success", "duration_s": 0.0001},
      {"step": 5, "agent": "OutputFormatter",    "status": "success", "duration_s": 0.0001}
    ],
    "cached": false
  }
}
```

### `GET /api/v1/pipeline/info`

Inspect the current agent pipeline configuration.

```json
{
  "total_agents": 5,
  "agents": [
    {"step": 1, "name": "InputHandler",      "class": "InputHandlerAgent",      "retries": 0, "retry_delay": 0.5},
    {"step": 2, "name": "Preprocessing",      "class": "PreprocessingAgent",      "retries": 0, "retry_delay": 0.5},
    {"step": 3, "name": "FeatureProcessing",  "class": "FeatureProcessingAgent",  "retries": 0, "retry_delay": 0.5},
    {"step": 4, "name": "AnalysisEngine",     "class": "AnalysisEngineAgent",     "retries": 0, "retry_delay": 0.5},
    {"step": 5, "name": "OutputFormatter",    "class": "OutputFormatterAgent",    "retries": 0, "retry_delay": 0.5}
  ]
}
```

### `GET /health`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2026-04-25T18:00:00.000000+00:00",
  "cache": {
    "size": 3,
    "hits": 12,
    "misses": 5,
    "evictions": 0,
    "hit_rate": 70.6
  }
}
```

---

## 🤖 Adding a New Agent

1. Create `app/agents/agent_my_new_agent.py`:

```python
from app.agents.base import BaseAgent

class MyNewAgent(BaseAgent):
    name = "MyNewAgent"
    retries = 2               # Optional: retry on failure
    retry_delay = 1.0         # Optional: base delay between retries

    async def process(self, data: dict) -> dict:
        # Your logic here — data comes from the previous agent
        data["my_field"] = "computed_value"
        return data
```

2. Register it in `app/core/orchestrator.py`:

```python
from app.agents.agent_my_new_agent import MyNewAgent

AGENT_REGISTRY: list[BaseAgent] = [
    InputHandlerAgent(),
    PreprocessingAgent(),
    MyNewAgent(),            # ← Insert at desired position
    FeatureProcessingAgent(),
    AnalysisEngineAgent(),
    OutputFormatterAgent(),
]
```

That's it. The orchestrator, logging, timing, error handling, and retry logic
are all inherited from `BaseAgent`.

---

## ⚡ Key Features

| Feature | Implementation |
|---------|---------------|
| **Async pipeline** | All agents are `async`; orchestrator uses `await` |
| **Per-agent timeout** | `asyncio.wait_for` enforced via `AGENT_TIMEOUT_SECONDS` |
| **Retry w/ backoff** | Set `retries` and `retry_delay` on any agent class |
| **LRU + TTL cache** | SHA-256 keyed, configurable max size and expiry |
| **Request tracing** | `X-Request-ID` header injected by middleware |
| **Structured logging** | JSON or text format, switchable via env var |
| **Exception hierarchy** | `SARBaseException → AgentError → AgentTimeoutError` |
| **Pipeline introspection** | `GET /pipeline/info` shows agents, order, config |
| **OpenAPI docs** | Auto-generated Swagger + ReDoc |

---

## 🔧 Configuration

All settings are loaded from environment variables via **pydantic-settings**.
See [`.env.example`](.env.example) for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Environment name |
| `DEBUG` | `true` | Enable hot-reload |
| `LOG_FORMAT` | `json` | `json` or `text` |
| `CACHE_ENABLED` | `true` | Toggle result caching |
| `CACHE_TTL_SECONDS` | `300` | Cache entry lifetime |
| `AGENT_TIMEOUT_SECONDS` | `30` | Per-agent max execution time |
| `RATE_LIMIT_RPM` | `60` | Requests per minute limit |

---

## 📜 License

MIT
