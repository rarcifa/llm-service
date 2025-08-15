"""Module documentation for `app/domain/eval/utils/eval_utils.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

import re
import subprocess
from typing import Any, Dict, List

from jinja2 import Template
from opentelemetry.trace import get_current_span
from sentence_transformers import util

from app.common.decorators.errors import catch_and_log_errors
from app.config import config
from app.constants.errors import (
    COMPUTE_RATING,
    HALLUCINATION_DETECTION,
    SCORE_GROUNDEDNESS,
    SCORE_HELPFULNESS,
)
from app.constants.values import OLLAMA_CLI, OLLAMA_CMD
from app.domain.retrieval.utils.embeddings_utils import get_embedding_model
from app.enums.eval import HallucinationKey, RatingKey, RetrievalSource
from app.enums.prompts import ModelType, ScoreKey


@catch_and_log_errors(default_return={"error": SCORE_GROUNDEDNESS})
def score_groundedness_with_embeddings(
    response: str, retrieved_docs: list[str]
) -> float:
    """Summary of `score_groundedness_with_embeddings`.

    Args:
        response (str): Description of response.
        retrieved_docs (list[str]): Description of retrieved_docs.

    Returns:
        float: Description of return value.

    """
    if not retrieved_docs:
        return 0.0
    model = get_embedding_model()
    doc_text = "\n".join(retrieved_docs)
    response_emb = model.encode(response, convert_to_tensor=True)
    doc_emb = model.encode(doc_text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(response_emb, doc_emb).item()
    return round(similarity, 3)


@catch_and_log_errors(default_return={"error": SCORE_HELPFULNESS})
def score_helpfulness_with_llm(
    *,
    prompt: str,
    response: str,
    helpfulness_template: str,
    conversation_history: list[str] | None = None,
    model_name: Any = ModelType.LLAMA3,
) -> str:
    """Summary of `score_helpfulness_with_llm`.

    Args:
        prompt (str): Description of prompt.
        response (str): Description of response.
        helpfulness_template (str): Description of helpfulness_template.
        conversation_history (list[str] | None): Description of conversation_history, default=None.
        model_name (Any): Description of model_name, default=ModelType.LLAMA3.

    Returns:
        str: Description of return value.

    """
    history_block = (
        "\n\nConversation History:\n"
        + "\n".join(
            (f"{msg.role.capitalize()}: {msg.content}" for msg in conversation_history)
        )
        if conversation_history
        else ""
    )
    judge_prompt = Template(helpfulness_template).render(
        prompt=prompt, response=response, history_block=history_block
    )
    result = subprocess.run(
        [OLLAMA_CLI, OLLAMA_CMD, model_name],
        input=judge_prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.decode().strip()


@catch_and_log_errors(default_return={"error": COMPUTE_RATING})
def compute_rating(grounding_score: float, judgment: str) -> str:
    """Summary of `compute_rating`.

    Args:
        grounding_score (float): Description of grounding_score.
        judgment (str): Description of judgment.

    Returns:
        str: Description of return value.

    """
    "Map grounding + helpfulness to PASS/FAIL/NEUTRAL using manifest thresholds."
    "Map grounding + helpfulness to PASS or FAIL using manifest minimums."
    score = extract_score_from_judgment(judgment)
    gp = float(config.eval.grounding_min)
    hp = int(config.eval.helpfulness_min)
    if grounding_score >= gp and score >= hp:
        return RatingKey.PASS
    return RatingKey.FAIL


@catch_and_log_errors(default_return={"error": HALLUCINATION_DETECTION})
def detect_hallucination(response: str, retrieved_docs: list[str]) -> str:
    """Summary of `detect_hallucination`.

    Args:
        response (str): Description of response.
        retrieved_docs (list[str]): Description of retrieved_docs.

    Returns:
        str: Description of return value.

    """
    if not retrieved_docs:
        return HallucinationKey.HIGH
    response_tokens = set(response.lower().split())
    context_tokens = set(" ".join(retrieved_docs).lower().split())
    overlap = response_tokens & context_tokens
    ratio = len(overlap) / (len(response_tokens) or 1)
    if ratio > 0.4:
        return HallucinationKey.LOW
    if ratio > 0.2:
        return HallucinationKey.MEDIUM
    return HallucinationKey.HIGH


def extract_score_from_judgment(judgment: str) -> int:
    """Summary of `extract_score_from_judgment`.

    Args:
        judgment (str): Description of judgment.

    Returns:
        int: Description of return value.

    """
    match = re.search("\\b([1-5])\\b", judgment)
    return int(match.group(1)) if match else 0


def compute_scores(
    *,
    filtered_input: str,
    response: str,
    retrieved_docs: list[str],
    conversation_history: list[str] | None,
    helpfulness_template: str,
) -> dict:
    """Summary of `compute_scores`.

    Args:
        filtered_input (str): Description of filtered_input.
        response (str): Description of response.
        retrieved_docs (list[str]): Description of retrieved_docs.
        conversation_history (list[str] | None): Description of conversation_history.
        helpfulness_template (str): Description of helpfulness_template.

    Returns:
        dict: Description of return value.

    """
    grounding_score = score_groundedness_with_embeddings(response, retrieved_docs)
    helpfulness_output = score_helpfulness_with_llm(
        prompt=filtered_input,
        response=response,
        conversation_history=conversation_history,
        helpfulness_template=helpfulness_template,
    )
    hallucination_risk = detect_hallucination(response, retrieved_docs)
    rating = compute_rating(grounding_score, helpfulness_output)
    return {
        ScoreKey.GROUNDING: grounding_score,
        ScoreKey.HELPFULNESS: helpfulness_output,
        ScoreKey.HALLUCINATION: hallucination_risk,
        ScoreKey.RATING: rating,
        "retrieval": {"docs": build_doc_metadata(filtered_input, retrieved_docs)},
    }


def trace_eval_span(meta: dict, scores: dict) -> None:
    """Summary of `trace_eval_span`.

    Args:
        meta (dict): Description of meta.
        scores (dict): Description of scores.

    """
    span = get_current_span()
    for k, v in {**meta, **scores}.items():
        if isinstance(v, str) and len(v) > 200:
            span.set_attribute(k, v[:200])
        elif isinstance(v, (str, bool, int, float)):
            span.set_attribute(k, v)


def build_doc_metadata(query: str, docs: List[str]) -> List[Dict]:
    """Summary of `build_doc_metadata`.

    Args:
        query (str): Description of query.
        docs (List[str]): Description of docs.

    Returns:
        List[Dict]: Description of return value.

    """
    model = get_embedding_model()
    query_embedding = model.encode(query, convert_to_tensor=True)
    out: List[Dict] = []
    for doc in docs:
        doc_embedding = model.encode(doc, convert_to_tensor=True)
        score = util.pytorch_cos_sim(query_embedding, doc_embedding).item()
        source = RetrievalSource.MEMORY if "Agent:" in doc else RetrievalSource.VECTOR
        out.append({"chunk": doc[:100], "source": source, "score": round(score, 3)})
    return out
