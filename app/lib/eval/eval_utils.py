"""
eval_utils.py

Provides utility functions to evaluate an LLM-generated response using:
- Embedding-based groundedness scoring
- LLM-as-a-judge for helpfulness
- Simple heuristics for hallucination detection
- Final rating calculation using thresholds

Also supports OpenTelemetry span tracing with structured metadata.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import re
import subprocess
from typing import Any, Dict, List

from jinja2 import Template
from opentelemetry import trace
from opentelemetry.trace import get_current_span
from sentence_transformers import util

from app.config import helpfulness_template, thresholds
from app.constants.values import OLLAMA_CLI, OLLAMA_CMD
from app.enums.errors.eval import EvalErrorType
from app.enums.eval import (
    GroundingKey,
    HallucinationKey,
    HelpfulnessKey,
    RatingKey,
    RetrievalSource,
)
from app.enums.prompts import ModelType, ScoreKey
from app.lib.embeddings.embeddings_utils import get_embedding_model
from app.lib.utils.decorators.errors import catch_and_log_errors
from app.lib.utils.logger import setup_logger

logger = setup_logger()
tracer = trace.get_tracer(__name__)
embedding_model = get_embedding_model()


@catch_and_log_errors(default_return={"error": EvalErrorType.SCORE_GROUNDEDNESS})
def score_groundedness_with_embeddings(
    response: str, retrieved_docs: list[str]
) -> float:
    """
    Calculates cosine similarity between the response and retrieved context using sentence embeddings.

    Args:
        response (str): The agent's generated response.
        retrieved_docs (list[str]): Contextual documents retrieved during prompt construction.

    Returns:
        float: Cosine similarity score between response and context (0.0–1.0).
    """
    if not retrieved_docs:
        return 0.0

    doc_text = "\n".join(retrieved_docs)
    response_emb = embedding_model.encode(response, convert_to_tensor=True)
    doc_emb = embedding_model.encode(doc_text, convert_to_tensor=True)

    similarity = util.pytorch_cos_sim(response_emb, doc_emb).item()
    return round(similarity, 3)


@catch_and_log_errors(default_return={"error": EvalErrorType.SCORE_HELPFULNESS})
def score_helpfulness_with_llm(
    prompt: str,
    response: str,
    conversation_history: list[str] = None,
    model_name: Any = ModelType.LLAMA3,
) -> str:
    """
    Uses a local LLM to score helpfulness of a response based on a custom judge prompt.

    Args:
        prompt (str): The prompt used to generate the response.
        response (str): The response to be evaluated.
        conversation_history (list[str], optional): Prior conversation history, if available.
        model_name (Any, optional): The judge model to invoke (default: LLaMA3).

    Returns:
        str: The raw response from the judge model (typically a numeric score or explanation).
    """
    history_block = (
        "\n\nConversation History:\n"
        + "\n".join(
            f"{msg.role.capitalize()}: {msg.content}" for msg in conversation_history
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


@catch_and_log_errors(default_return={"error": EvalErrorType.COMPUTE_RATING})
def compute_rating(grounding_score: float, judgment: str, thresholds: dict) -> str:
    """
    Computes a final rating based on grounding and helpfulness scores and thresholds.

    Args:
        grounding_score (float): Grounding similarity score.
        judgment (str): Output from helpfulness judge model.
        thresholds (dict): Dictionary of rating thresholds.

    Returns:
        str: One of RatingKey.PASS, RatingKey.FAIL, or RatingKey.NEUTRAL.
    """
    score = extract_score_from_judgment(judgment)

    # Thresholds for grounding and helpfulness
    gp = thresholds.get(GroundingKey.PASS, 0.7)
    gf = thresholds.get(GroundingKey.FAIL, 0.4)
    hp = thresholds.get(HelpfulnessKey.PASS, 4)
    hf = thresholds.get(HelpfulnessKey.FAIL, 2)

    if grounding_score >= gp and score >= hp:
        return RatingKey.PASS
    elif grounding_score < gf or score <= hf:
        return RatingKey.FAIL
    else:
        return RatingKey.NEUTRAL


@catch_and_log_errors(default_return={"error": EvalErrorType.HALLUCINATION_DETECTION})
def detect_hallucination(response: str, retrieved_docs: list[str]) -> str:
    """
    Detects hallucination by calculating token overlap between response and context.

    Args:
        response (str): The agent-generated response.
        retrieved_docs (list[str]): List of retrieved supporting documents.

    Returns:
        str: HallucinationKey representing LOW, MEDIUM, HIGH, or UNKNOWN.
    """
    if not retrieved_docs:
        return HallucinationKey.HIGH

    response_tokens = set(response.lower().split())
    context_tokens = set(" ".join(retrieved_docs).lower().split())

    overlap = response_tokens & context_tokens
    ratio = len(overlap) / (len(response_tokens) or 1)

    if ratio > 0.4:
        return HallucinationKey.LOW
    elif ratio > 0.2:
        return HallucinationKey.MEDIUM
    else:
        return HallucinationKey.HIGH


def extract_score_from_judgment(judgment: str) -> int:
    """
    Extracts a numeric score (1–5) from the LLM's helpfulness judgment.

    Args:
        judgment (str): The LLM's raw output string.

    Returns:
        int: The extracted score or 0 if none found.
    """
    match = re.search(r"\b([1-5])\b", judgment)
    return int(match.group(1)) if match else 0


def compute_scores(
    filtered_input: str,
    response: str,
    retrieved_docs: list[str],
    conversation_history: list[str] = None,
) -> dict:
    """
    Runs the full evaluation suite on an agent response and returns structured scores.

    Args:
        filtered_input (str): Cleaned input used to prompt the model.
        response (str): The model's generated output.
        retrieved_docs (list[str]): Contextual documents used during prompting.
        conversation_history (list[str], optional): Past messages in the conversation.

    Returns:
        dict: Dictionary containing values for:
            - ScoreKey.GROUNDING
            - ScoreKey.HELPFULNESS
            - ScoreKey.HALLUCINATION
            - ScoreKey.RATING
    """
    grounding_score = score_groundedness_with_embeddings(response, retrieved_docs)
    helpfulness_output = score_helpfulness_with_llm(
        filtered_input, response, conversation_history
    )
    hallucination_risk = detect_hallucination(response, retrieved_docs)
    rating = compute_rating(grounding_score, helpfulness_output, thresholds)

    return {
        ScoreKey.GROUNDING: grounding_score,
        ScoreKey.HELPFULNESS: helpfulness_output,
        ScoreKey.HALLUCINATION: hallucination_risk,
        ScoreKey.RATING: rating,
        "retrieval": {"docs": build_doc_metadata(filtered_input, retrieved_docs)},
    }


def trace_eval_span(meta: dict, scores: dict) -> None:
    """
    Adds all evaluation metadata and score values to the current OpenTelemetry span.

    Args:
        meta (dict): Metadata about the prompt, input, output, etc.
        scores (dict): Evaluation scores to trace.

    Notes:
        Truncates very long string attributes (>200 chars) to reduce span overload.
    """
    span = get_current_span()
    for k, v in {**meta, **scores}.items():
        if isinstance(v, str) and len(v) > 200:
            span.set_attribute(k, v[:200])
        elif isinstance(v, (str, bool, int, float)):
            span.set_attribute(k, v)


def build_doc_metadata(query: str, docs: List[str]) -> List[Dict]:
    """
    Builds metadata for a list of retrieved documents based on their similarity to the input query.

    Each document is:
    - Scored via cosine similarity with the query embedding
    - Tagged as "memory" or "vector" based on its format
    - Truncated to 100 characters for preview purposes

    Args:
        query (str): The original query used to retrieve documents.
        docs (List[str]): The list of retrieved document strings.

    Returns:
        List[Dict]: A list of metadata dicts for each document, including:
            - 'chunk': Truncated document preview
            - 'source': Either RetrievalSource.MEMORY or VECTOR
            - 'score': Cosine similarity score rounded to 3 decimals
    """
    embedding_model = get_embedding_model()
    query_embedding = embedding_model.encode(query, convert_to_tensor=True)

    metadata = []
    for doc in docs:
        doc_embedding = embedding_model.encode(doc, convert_to_tensor=True)
        score = util.pytorch_cos_sim(query_embedding, doc_embedding).item()
        source = RetrievalSource.MEMORY if "Agent:" in doc else RetrievalSource.VECTOR
        metadata.append(
            {
                "chunk": doc[:100],
                "source": source,
                "score": round(score, 3),
            }
        )

    return metadata
