# Project API Overview

_Auto-generated on 2025-08-15 19:30:51Z_

This documentation reflects the latest codebase after standardizing all docstrings to **Google style**.

## Modules

- `api/controllers/chat_controller.py` — Classes: **1**, Functions: **2**
- `api/routes/chat_router.py` — Classes: **0**, Functions: **2**
- `app/__init__.py` — Classes: **0**, Functions: **0**
- `app/common/__init__.py` — Classes: **0**, Functions: **0**
- `app/common/decorators/__init__.py` — Classes: **0**, Functions: **0**
- `app/common/decorators/errors.py` — Classes: **0**, Functions: **1**
- `app/common/decorators/retry.py` — Classes: **0**, Functions: **1**
- `app/common/decorators/tracing.py` — Classes: **0**, Functions: **3**
- `app/common/error_handling.py` — Classes: **1**, Functions: **1**
- `app/common/http_errors.py` — Classes: **0**, Functions: **1**
- `app/common/utils/__init__.py` — Classes: **0**, Functions: **0**
- `app/common/utils/files.py` — Classes: **0**, Functions: **1**
- `app/common/utils/logger.py` — Classes: **0**, Functions: **1**
- `app/common/utils/strings.py` — Classes: **0**, Functions: **1**
- `app/config.py` — Classes: **13**, Functions: **2**
- `app/constants/__init__.py` — Classes: **0**, Functions: **0**
- `app/constants/values.py` — Classes: **0**, Functions: **0**
- `app/db/__init__.py` — Classes: **0**, Functions: **0**
- `app/db/models/__init__.py` — Classes: **0**, Functions: **0**
- `app/db/models/message.py` — Classes: **1**, Functions: **0**
- `app/db/models/session.py` — Classes: **1**, Functions: **0**
- `app/db/models/vector_record.py` — Classes: **1**, Functions: **0**
- `app/db/postgres.py` — Classes: **0**, Functions: **2**
- `app/db/repositories/__init__.py` — Classes: **0**, Functions: **0**
- `app/db/repositories/pgvector_repository.py` — Classes: **1**, Functions: **4**
- `app/db/repositories/session_repository.py` — Classes: **1**, Functions: **7**
- `app/db/schemas/__init__.py` — Classes: **0**, Functions: **0**
- `app/db/schemas/chat.py` — Classes: **1**, Functions: **0**
- `app/db/schemas/message.py` — Classes: **3**, Functions: **0**
- `app/db/schemas/session.py` — Classes: **4**, Functions: **0**
- `app/domain/agent/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/agent/base/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/agent/base/agent_base.py` — Classes: **1**, Functions: **1**
- `app/domain/agent/impl/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/agent/impl/agent_impl.py` — Classes: **1**, Functions: **3**
- `app/domain/agent/impl/persistence.py` — Classes: **0**, Functions: **2**
- `app/domain/agent/impl/pipeline.py` — Classes: **1**, Functions: **2**
- `app/domain/agent/utils/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/agent/utils/agent_utils.py` — Classes: **0**, Functions: **3**
- `app/domain/eval/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/eval/base/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/eval/base/eval_base.py` — Classes: **1**, Functions: **1**
- `app/domain/eval/impl/eval_impl.py` — Classes: **1**, Functions: **1**
- `app/domain/eval/utils/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/eval/utils/eval_utils.py` — Classes: **0**, Functions: **8**
- `app/domain/ingestion/base/ingester_base.py` — Classes: **1**, Functions: **2**
- `app/domain/ingestion/impl/chroma_ingester.py` — Classes: **1**, Functions: **7**
- `app/domain/ingestion/utils/text.py` — Classes: **0**, Functions: **1**
- `app/domain/memory/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/memory/base/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/memory/base/memory_base.py` — Classes: **1**, Functions: **2**
- `app/domain/memory/impl/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/memory/impl/pgvector_memory.py` — Classes: **1**, Functions: **4**
- `app/domain/provider/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/provider/base/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/provider/base/provider_base.py` — Classes: **1**, Functions: **1**
- `app/domain/provider/impl/ollama_client.py` — Classes: **1**, Functions: **9**
- `app/domain/provider/impl/ollama_provider.py` — Classes: **1**, Functions: **6**
- `app/domain/provider/utils/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/provider/utils/provider_utils.py` — Classes: **0**, Functions: **1**
- `app/domain/retrieval/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/retrieval/base/retriever_base.py` — Classes: **1**, Functions: **2**
- `app/domain/retrieval/impl/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/retrieval/impl/rag_retriever_impl.py` — Classes: **1**, Functions: **2**
- `app/domain/retrieval/utils/embeddings_utils.py` — Classes: **0**, Functions: **2**
- `app/domain/safety/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/safety/base/safety_base.py` — Classes: **1**, Functions: **2**
- `app/domain/safety/impl/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/safety/impl/injection_detector_impl.py` — Classes: **1**, Functions: **1**
- `app/domain/safety/utils/hallucination_filter.py` — Classes: **0**, Functions: **1**
- `app/domain/safety/utils/injection_detector.py` — Classes: **0**, Functions: **2**
- `app/domain/safety/utils/pii_filter.py` — Classes: **0**, Functions: **1**
- `app/domain/safety/utils/profanity_filter.py` — Classes: **0**, Functions: **3**
- `app/domain/tools/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/tools/base/step_executor_base.py` — Classes: **1**, Functions: **1**
- `app/domain/tools/base/tool_planner_base.py` — Classes: **1**, Functions: **1**
- `app/domain/tools/impl/__init__.py` — Classes: **0**, Functions: **0**
- `app/domain/tools/impl/step_executor.py` — Classes: **1**, Functions: **3**
- `app/domain/tools/impl/tool_planner.py` — Classes: **1**, Functions: **3**
- `app/domain/tools/utils/calculator.py` — Classes: **0**, Functions: **2**
- `app/enums/__init__.py` — Classes: **0**, Functions: **0**
- `app/enums/api.py` — Classes: **3**, Functions: **0**
- `app/enums/errors/__init__.py` — Classes: **0**, Functions: **0**
- `app/enums/errors/agent.py` — Classes: **1**, Functions: **0**
- `app/enums/errors/eval.py` — Classes: **1**, Functions: **0**
- `app/enums/errors/model.py` — Classes: **1**, Functions: **0**
- `app/enums/errors/postgres.py` — Classes: **1**, Functions: **0**
- `app/enums/errors/session_repository.py` — Classes: **1**, Functions: **0**
- `app/enums/eval.py` — Classes: **11**, Functions: **0**
- `app/enums/manifest.py` — Classes: **1**, Functions: **0**
- `app/enums/model.py` — Classes: **1**, Functions: **0**
- `app/enums/prompts.py` — Classes: **5**, Functions: **0**
- `app/enums/tools.py` — Classes: **2**, Functions: **0**
- `app/registry/__init__.py` — Classes: **0**, Functions: **0**
- `app/registry/base_registry.py` — Classes: **3**, Functions: **8**
- `app/registry/prompt_registry.py` — Classes: **2**, Functions: **4**
- `app/registry/tool_registry.py` — Classes: **2**, Functions: **4**
- `app/services/__init__.py` — Classes: **0**, Functions: **0**
- `app/services/chat_service.py` — Classes: **1**, Functions: **2**
- `cli.py` — Classes: **0**, Functions: **1**
- `main.py` — Classes: **0**, Functions: **1**
- `migrations/env.py` — Classes: **0**, Functions: **2**
- `migrations/versions/09494a513e2f_merge_heads.py` — Classes: **0**, Functions: **2**
- `migrations/versions/20250814_add_pgvector_vector_records.py` — Classes: **0**, Functions: **2**
- `migrations/versions/2344c21b49f6_initial_schema.py` — Classes: **0**, Functions: **2**
- `tests/test_runner.py` — Classes: **0**, Functions: **4**

## Conventions

- Docstrings follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings).
- Each module, class, and function now has a concise summary line, followed by structured sections (`Args`, `Returns`, and `Raises` where applicable).
- Existing outdated/placeholder docstrings were replaced to ensure consistency.

## How to Use

Read the docstrings directly in the code for the most accurate and up-to-date documentation. Tooling like IDEs, Sphinx (with napoleon), or pdoc will render these docstrings cleanly.

## Build Docs Locally (Optional)

You can render HTML docs using Sphinx and napoleon:
```bash
pip install sphinx sphinxcontrib-napoleon
sphinx-quickstart  # if you don't already have a docs folder
```
Then set `extensions = ['sphinx.ext.napoleon']` in `conf.py`.

## Summary

- Files processed: **106**
- Classes documented: **84**
- Functions documented: **141**

---
_This README was updated automatically to reflect the standardized docstrings across the project._