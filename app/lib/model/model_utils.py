"""
model_utils.py

Provides utilities for interacting with LLM models via Ollama CLI or HTTP.
Includes:
- Streaming output (CLI and HTTP)
- Prompt execution with retry logic
- Prompt variable verification using Jinja2
- Unified logging and error handling

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import subprocess
from typing import Generator

from jinja2 import Environment, meta
from ollama import chat

from app.config import main_model
from app.constants.values import OLLAMA_CLI, OLLAMA_CMD, USE_HTTP_API
from app.enums.prompts import RoleKey
from app.lib.utils.decorators.errors import catch_and_log_errors
from app.lib.utils.logger import setup_logger

logger = setup_logger()


@catch_and_log_errors(default_return="")
def run_model_output(prompt: str) -> str:
    """
    Executes a blocking Ollama CLI call with the given prompt.

    Args:
        prompt (str): Prompt to send to the model.
        model (str): Model name (e.g., "llama3").

    Returns:
        str: Model output or empty string on failure.
    """
    result = subprocess.run(
        [OLLAMA_CLI, OLLAMA_CMD, main_model],
        input=prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    if result.returncode == 0:
        return result.stdout.decode()

    logger.warn(
        "Ollama CLI failed", code=result.returncode, stderr=result.stderr.decode()
    )
    return ""


def stream_model_output(prompt: str) -> Generator[str, None, None]:
    """
    Streams model output token-by-token from either CLI or HTTP interface,
    depending on the configured runtime flag (`USE_HTTP_API`).

    Args:
        prompt (str): The full prompt to send to the model.
        model (str): The model identifier or name (default: ModelType.LLAMA3).

    Returns:
        Generator[str, None, None]: A generator that yields model output tokens/segments.
    """
    return stream_with_http(prompt) if USE_HTTP_API else stream_with_cli(prompt)


@catch_and_log_errors()
def stream_with_http(prompt: str) -> Generator[str, None, None]:
    """
    Streams model output using the Ollama HTTP client (`ollama.chat`).

    Args:
        prompt (str): The prompt to send.
        model (str): The model to use.

    Yields:
        str: Chunks of model output as they stream in.
    """
    messages = [{"role": RoleKey.USER, "content": prompt}]
    response = chat(model=main_model, messages=messages, stream=True)
    for chunk in response:
        yield chunk.message.content or ""


@catch_and_log_errors()
def stream_with_cli(prompt: str) -> Generator[str, None, None]:
    """
    Streams model output using the Ollama CLI in real-time.

    Args:
        prompt (str): The prompt to send.
        model (str): The model to invoke via CLI.

    Yields:
        str: Lines of model output as they're printed by the subprocess.
    """
    process = subprocess.Popen(
        [OLLAMA_CLI, OLLAMA_CMD, main_model],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if process.stdin:
        process.stdin.write(prompt)
        process.stdin.close()

    if process.stdout:
        for line in iter(process.stdout.readline, ""):
            yield line
        process.stdout.close()

    process.wait()
    if process.returncode != 0:
        stderr = process.stderr.read() if process.stderr else ""
        logger.error("Ollama CLI stream failed", stderr=stderr)
        yield "[LLM CLI error]"


@catch_and_log_errors(default_return=["__template_error__"])
def verify_prompt_variables(template_str: str, provided_vars: dict) -> list[str]:
    """
    Verifies that all required Jinja2 template variables are provided.

    Args:
        template_str (str): The Jinja2 template string to analyze.
        provided_vars (dict): Dictionary of variables to inject into the template.

    Returns:
        list[str]: List of missing template variables.
    """
    env = Environment()
    parsed_content = env.parse(template_str)
    required_vars = meta.find_undeclared_variables(parsed_content)
    missing = [var for var in required_vars if var not in provided_vars]
    return missing
