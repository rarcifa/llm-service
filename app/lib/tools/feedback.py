"""
feedback.py

Handles storage and retrieval of user or evaluator feedback for LLM responses.
Each feedback entry is stored as a JSON line in an append-only local file.

Supports:
- Storing structured feedback records
- Fetching feedback by ID
- Listing all feedback or filtering by session

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import json
import os
import uuid
from typing import Any

from app.constants.values import ENCODING, FEEDBACK_PATH
from app.enums.prompts import JsonKey
from app.lib.utils.decorators.errors import catch_and_log_errors


@catch_and_log_errors(default_return=None)
def store_feedback(
    trace_id: Any,
    response_id: Any,
    message_id: Any,
    session_id: Any,
    feedback: Any,
    notes: Any,
) -> str:
    """
    Stores a feedback record in a local JSONL file.

    Args:
        trace_id (Any): Unique trace identifier for observability.
        response_id (Any): ID of the evaluated model response.
        message_id (Any): ID of the message associated with the response.
        session_id (Any): User session identifier.
        feedback (Any): Feedback score, flag, or rating.
        notes (Any): Optional notes or explanation.

    Returns:
        str: Generated feedback ID.
    """
    feedback_id = str(uuid.uuid4())
    os.makedirs("feedback", exist_ok=True)

    record = {
        JsonKey.FEEDBACK_ID: feedback_id,
        JsonKey.TRACE_ID: trace_id,
        JsonKey.RESPONSE_ID: response_id,
        JsonKey.MESSAGE_ID: message_id,
        JsonKey.SESSION_ID: session_id,
        "feedback": feedback,
        "notes": notes,
    }

    with open(FEEDBACK_PATH, "a", encoding=ENCODING) as f:
        f.write(json.dumps(record) + "\n")

    return feedback_id


@catch_and_log_errors(default_return=[])
def read_all_feedback() -> list[dict[str, Any]]:
    """
    Reads all feedback entries from the local feedback file.

    Returns:
        list[dict[str, Any]]: A list of feedback records.
    """
    if not os.path.exists(FEEDBACK_PATH):
        return []

    with open(FEEDBACK_PATH, "r", encoding=ENCODING) as f:
        return [json.loads(line) for line in f]


@catch_and_log_errors(default_return=None)
def get_feedback_by_id(feedback_id: str) -> dict[str, Any] | None:
    """
    Retrieves a single feedback record by its unique feedback ID.

    Args:
        feedback_id (str): The UUID of the feedback record.

    Returns:
        dict[str, Any] | None: The matching record or None if not found.
    """
    for record in read_all_feedback():
        if record.get(JsonKey.FEEDBACK_ID) == feedback_id:
            return record
    return None


@catch_and_log_errors(default_return=[])
def list_feedback(session_id: str | None = None) -> list[dict[str, Any]]:
    """
    Lists all feedback records, optionally filtered by session ID.

    Args:
        session_id (str | None, optional): If provided, filters by session.

    Returns:
        list[dict[str, Any]]: Filtered feedback records.
    """
    return [
        record
        for record in read_all_feedback()
        if session_id is None or record.get(JsonKey.SESSION_ID) == session_id
    ]
