# Enterprise Agent: Modular LLM Service

> An enterprise-grade framework for building LLM-powered agents with memory, tools, safety filters, evaluation, observability, and streaming interfaces.

---

## Architecture Overview

This system follows a **modular, layered architecture** inspired by:

- **Clean Architecture** (separation of concerns)
- **LLM Agent Design Patterns** (LangServe, Haystack, OpenAgents)
- **Microservice + Plugin Model** (modular evaluation, tools, memory, etc)

### Layers

```mermaid
graph TD
    subgraph Client
        Z[Frontend / CLI / External App]
    end

    subgraph API_Layer
        A[FastAPI Controller]
    end

    subgraph Guardrails
        GA[Input Filters - PII, Injection, Profanity]
    end

    subgraph Agent_Layer
        B[AgentRunner / Streamer]
        B --> D[Async Eval Thread]
    end

    subgraph LLM_Pipeline
        E[Prompt + Tools + Memory]
        F[LLM Call via Ollama]
    end

    subgraph Persistence
        G[PostgreSQL - Sessions]
        H[Phoenix Tracing - OTLP]
    end

    Z -->|POST /chat| A --> GA --> B
    B --> E --> F
    B --> G
    D --> H
    B -->|Response| Z

```

---

## Agent Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant AgentRunner
    participant LLM
    participant EvalThread
    participant DB
    participant Phoenix

    User->>API: POST /chat
    API->>AgentRunner: invoke run()
    AgentRunner->>LLM: prompt + context
    LLM-->>AgentRunner: response
    AgentRunner->>DB: store messages
    AgentRunner-->>User: return response
    Note right of AgentRunner: spawn background thread
    AgentRunner->>EvalThread: evaluate in parallel
    EvalThread->>Phoenix: trace eval results
```

---

## Folder Structure

### `app/` – Core Application Logic

| Path          | Purpose                                                                             |
| ------------- | ----------------------------------------------------------------------------------- |
| `lib/agent/`  | Agent pipeline: prompt prep, LLM calls, streaming, background eval                  |
| `lib/tools/`  | Tool functions, `tool_registry.py`, `tool_planner.py`, and custom tool logic        |
| `lib/memory/` | Short-term memory (in-memory store or placeholder for vector memory)                |
| `lib/model/`  | LLM wrappers like `model_runner.py`, with retry + streaming support                 |
| `lib/eval/`   | `eval_runner.py` and scorers used in async eval phase                               |
| `lib/safety/` | Guardrails: `guardrail_registry.py`, prompt injection, profanity, and PII detection |
| `lib/utils/`  | Logger, UUIDs, decorators, etc                                                      |
| `app/db/`     | SQLAlchemy models and repositories                                                  |
| `services/`   | Business logic, like `chat_service.py`                                              |
| `api/`        | FastAPI routes and controllers                                                      |

### `migrations/`

- Alembic-managed DB migrations
- Migration commands:

```bash
# Create new migration from model changes
./scripts/generate-migration.sh "message here"

# Apply pending migrations
./scripts/run-migrations.sh

# Initialize DB (create if not exists and run migrations)
./scripts/init-db.sh
```

### `prompts/`

- YAML/Jinja2 system + user prompts (`agent_prompt.yaml`)

### `config/`

- Manifest (`manifest.yaml`) and `.env`-driven settings

### `feedback/`

- JSONL log of feedback (e.g., thumbs up/down)

### `tests/`

- Golden tests + CLI-based regression suite

---

## Agent Flow

1. PII & prompt injection filter
2. Memory + document retrieval
3. ToolPlanner selects & calls matching tool (optional)
4. Tool result injected into prompt context
5. Prompt rendering (Jinja2)
6. LLM call (sync or streaming)
7. Store conversation in DB & memory
8. Respond to user immediately
9. Trigger evaluation in a background thread
10. Emit OpenTelemetry span to Phoenix
11. Feedback trace support

---

## Observability

- **Phoenix** via OTLP gRPC
- Traced spans for agent call, prompt, eval, tool use
- Includes scores: `grounding`, `confidence`, `hallucination`, etc

---

## Guardrails

The agent applies input and output filters based on the manifest:

```yaml
guardrails:
  prompt_injection_detection: rebuff
  pii_filter: presidio
  output_filters:
    - profanity_check
    - hallucination_blocker
```

These are mapped to callable tools via guardrail_registry.py.

- **Input**: Prompt injection + PII + profanity filters
- **Output**: Hallucination blocking, custom regex filters

## Safety Tooling

| Name                    | Purpose                                 |
| ----------------------- | --------------------------------------- |
| `rebuff`                | Prompt injection detection              |
| `presidio`              | PII redaction                           |
| `profanity_check`       | Replaces/flags offensive content        |
| `hallucination_blocker` | (Custom) filters misleading completions |

## Design Philosophy

- **Modular**: Add/remove tools, models, filters
- **Traceable**: All responses are traced with UUIDs
- **Extensible**: Plugin system for tools & evaluation
- **Testable**: CI-ready golden test runner
- **Eval-first**: Built-in LLM-as-a-Judge & grounding evals

---

## Built With

- LLM: Ollama (supports streaming)
- Vector DB: ChromaDB (in-memory or persisted)
- Eval: Phoenix + LLM-as-a-Judge
- Prompting: Jinja2 + YAML
- Backend: FastAPI + Pydantic
- Storage: PostgreSQL (via SQLAlchemy + Alembic)
- Tracing: OTLP / OpenTelemetry

---

## Quickstart

```bash
git clone https://github.com/your-org/enterprise-agent
cd enterprise-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with:

```
DATABASE_URL=postgresql+psycopg2://postgres:yourpass@localhost:5432/enterprise_agent
```

### Start DB + Phoenix (Observability)

```bash
docker-compose up -d postgres phoenix
```

### Initialize Database

```bash
./scripts/init-db.sh
```

### Run App (API mode)

```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

### Run CLI prompt

```bash
python cli.py "What is CLM?"
```

---

## Migration Management

### Create a new migration from model changes

```bash
./scripts/generate-migration.sh "added new table"
```

### Apply pending migrations

```bash
./scripts/run-migrations.sh
```

---

## API Endpoints

| Method | Endpoint                 | Description              |
| ------ | ------------------------ | ------------------------ |
| POST   | `/chat`                  | Agent response           |
| POST   | `/chat/stream`           | Streaming agent response |
| POST   | `/feedback`              | Save feedback            |
| GET    | `/feedback/{id}`         | Get feedback by ID       |
| GET    | `/feedback`              | List + filter feedback   |
| POST   | `/admin/load_documents`  | Upload documents to RAG  |
| GET    | `/sessions/{session_id}` | Full session transcript  |

---

## Evaluation Outputs

- `eval.rating`: pass/fail/neutral
- `grounding_score`: 0.0–1.0
- `helpfulness_score`: 0.0–1.0
- `confidence_score`: avg(grounding + helpfulness)
- `hallucination_risk`: low / medium / high

All metrics are sent to Phoenix and can be traced per `trace_id`.

---

## Dev Notes

- Use `scripts/generate-migration.sh` to generate schema changes
- Use `scripts/run-migrations.sh` to apply them
- Use `scripts/init-db.sh` to create the DB if missing
- DB schema lives in `db/models/`
- API + service schema lives in `api/controllers/` and `services/chat_service.py`

---

## Coming Soon

- Streaming frontend (Streamlit or React)
- Tool orchestration via planner
- Agent-to-agent messaging
- External API integrations
