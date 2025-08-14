"""Utilities for evaluating LLM responses (scores + tracing).

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from __future__ import annotations

import re
import subprocess
from typing import Any, Dict, List

from jinja2 import Template
from opentelemetry.trace import get_current_span
from sentence_transformers import util

from app.config import CFG
from app.constants.values import OLLAMA_CLI, OLLAMA_CMD
from app.domain.embeddings.utils.embeddings_utils import get_embedding_model
from app.enums.errors.eval import EvalErrorType
from app.enums.eval import (
    GroundingKey,
    HallucinationKey,
    HelpfulnessKey,
    RatingKey,
    RetrievalSource,
)
from app.enums.prompts import ModelType, ScoreKey
from app.common.decorators.errors import catch_and_log_errors


@catch_and_log_errors(default_return={"error": EvalErrorType.SCORE_GROUNDEDNESS})
def score_groundedness_with_embeddings(
    response: str, retrieved_docs: list[str]
) -> float:
    """Cosine similarity between response and retrieved context via sentence embeddings."""
    if not retrieved_docs:
        return 0.0

    model = get_embedding_model()
    doc_text = "\n".join(retrieved_docs)
    response_emb = model.encode(response, convert_to_tensor=True)
    doc_emb = model.encode(doc_text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(response_emb, doc_emb).item()
    return round(similarity, 3)


@catch_and_log_errors(default_return={"error": EvalErrorType.SCORE_HELPFULNESS})
def score_helpfulness_with_llm(
    *,
    prompt: str,
    response: str,
    helpfulness_template: str,
    conversation_history: list[str] | None = None,
    model_name: Any = ModelType.LLAMA3,
) -> str:
    """Use a local LLM (via `ollama`) to score helpfulness with a judge prompt."""
    history_block = (
        "\n\nConversation History:\n"
        + "\n".join(f"{msg.role.capitalize()}: {msg.content}" for msg in conversation_history)  # type: ignore[attr-defined]
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


@catch_and_log_errors(default_return={"error": EvalErrorType.COMPUTE_RATING})
def compute_rating(grounding_score: float, judgment: str) -> str:
    """Map grounding + helpfulness to PASS/FAIL/NEUTRAL using configured thresholds."""
    """Map grounding + helpfulness to PASS/FAIL/NEUTRAL using manifest thresholds."""
    """Map grounding + helpfulness to PASS or FAIL using manifest minimums."""
    score = extract_score_from_judgment(judgment)

    gp = float(CFG.eval.grounding_min)
    hp = int(CFG.eval.helpfulness_min)

    if grounding_score >= gp and score >= hp:
        return RatingKey.PASS
    return RatingKey.FAIL


@catch_and_log_errors(default_return={"error": EvalErrorType.HALLUCINATION_DETECTION})
def detect_hallucination(response: str, retrieved_docs: list[str]) -> str:
    """Heuristic token-overlap hallucination detector (LOW/MEDIUM/HIGH)."""
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
    """Extract a numeric score (1–5) from judge output; 0 if not found."""
    match = re.search(r"\b([1-5])\b", judgment)
    return int(match.group(1)) if match else 0


def compute_scores(
    *,
    filtered_input: str,
    response: str,
    retrieved_docs: list[str],
    conversation_history: list[str] | None,
    helpfulness_template: str,
) -> dict:
    """Run evaluation suite and return structured scores + retrieval metadata."""
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
    """Attach evaluation metadata and scores to the current OpenTelemetry span.

    Long strings (>200 chars) are truncated to reduce span payload size.
    """
    span = get_current_span()
    for k, v in {**meta, **scores}.items():
        if isinstance(v, str) and len(v) > 200:
            span.set_attribute(k, v[:200])
        elif isinstance(v, (str, bool, int, float)):
            span.set_attribute(k, v)


def build_doc_metadata(query: str, docs: List[str]) -> List[Dict]:
    """Build similarity metadata for retrieved documents."""
    model = get_embedding_model()
    query_embedding = model.encode(query, convert_to_tensor=True)
    out: List[Dict] = []
    for doc in docs:
        doc_embedding = model.encode(doc, convert_to_tensor=True)
        score = util.pytorch_cos_sim(query_embedding, doc_embedding).item()
        source = RetrievalSource.MEMORY if "Agent:" in doc else RetrievalSource.VECTOR
        out.append({"chunk": doc[:100], "source": source, "score": round(score, 3)})
    return out
