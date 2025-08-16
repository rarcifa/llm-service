"""Module documentation for `app/constants/values.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

import os
from pathlib import Path

USE_HTTP_API = True
OLLAMA_CLI = "ollama"
OLLAMA_CMD = "run"
ENCODING = "utf-8"
EVAL_SERVICE_URL = os.getenv("EVAL_SERVICE_URL", "http://localhost:8001")
CONFIG_SERVICE_URL = os.getenv("CONFIG_SERVICE_URL", "http://localhost:8888")
APP_CONFIG_NAME = os.getenv("APP_CONFIG_NAME", "document_qa_assistant")
APP_CONFIG_PROFILE = os.getenv("APP_CONFIG_PROFILE", "default")
CONFIG_TIMEOUT_SEC = float(os.getenv("CONFIG_TIMEOUT_SEC", "5.0"))