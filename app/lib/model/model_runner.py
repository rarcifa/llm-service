"""
llm_service.py

Handles model inference and streaming using CLI or HTTP interfaces.
Applies retry logic and error handling, and abstracts away the specific
backend used to run the model.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from app.enums.errors.model import ModelErrorType
from app.lib.model.model_utils import run_model_output, stream_model_output
from app.lib.utils.decorators.errors import catch_and_log_errors
from app.lib.utils.decorators.retry import with_retry


class ModelRunner:
    """
    Service class for executing model queries with retry and error handling.

    Methods:
        run(prompt): Gets a full response from the model.
        stream(prompt): Streams the model response.
    """

    @with_retry(max_retries=3, backoff_factor=1.5)
    @catch_and_log_errors(default_return={"error": ModelErrorType.RUN_MODEL_OUTPUT})
    def run(self, prompt: str) -> str:
        """
        Executes a model query and returns the full response.

        Args:
            prompt (str): The prompt to send to the model.

        Returns:
            str: Model output or fallback error string on failure.
        """
        return run_model_output(prompt)

    @with_retry(max_retries=3, backoff_factor=1.5)
    @catch_and_log_errors(default_return={"error": ModelErrorType.STREAM_WITH_HTTP})
    def stream(self, prompt: str) -> str:
        """
        Executes a model query and returns the streamed response.

        Args:
            prompt (str): The prompt to send to the model.

        Returns:
            str: Model output or fallback error string on failure.
        """
        return stream_model_output(prompt)
