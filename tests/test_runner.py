"""
test_runner.py

Executes a set of predefined "golden" test cases that validate whether the agent
produces the expected evaluation ratings (e.g., PASS/FAIL) on known prompts.

Features:
- Runs all test cases from `golden_tests.yaml`
- Automatically compares actual vs. expected rating
- Optionally collects human feedback interactively
- Logs results and writes them to timestamped CSV files

Usage:
    python test_runner.py

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import csv
import os
from datetime import datetime
from typing import Any

import yaml

from app.agent.agent_runner import run_agent
from app.constants.values import ENCODING
from app.enums.prompts import JsonKey, ScoreKey
from app.utils.logger import setup_logger

logger = setup_logger()

# === Load golden test cases ===
with open("tests/golden_tests.yaml") as f:
    golden_tests = yaml.safe_load(f)


def prompt_for_feedback(response: str, interactive: bool = True) -> str:
    """
    Optionally prompt the user for feedback after seeing a model response.

    Args:
        response (str): Model-generated response to display.
        interactive (bool): Whether to prompt the user for feedback.

    Returns:
        str: One of 'thumbs_up', 'thumbs_down', or 'skipped'.
    """
    if not interactive:
        return "skipped"

    print("\nResponse preview:")
    print(response[:300] + "...\n")
    fb = input("Helpful (y) / Unhelpful (n) / Skip (enter)? ").strip().lower()
    return {"y": "thumbs_up", "n": "thumbs_down"}.get(fb, "skipped")


def evaluate_test_case(test: dict, index: int, interactive: bool = True) -> dict:
    """
    Runs a single golden test case and compares actual vs. expected result.

    Args:
        test (dict): The test case with prompt and expected rating.
        index (int): Test case index (for display/logging).
        interactive (bool): Whether to allow human feedback.

    Returns:
        dict: A result dictionary with evaluation metadata.
    """
    prompt = test["prompt"]
    expected = test.get("expected_rating")

    result = run_agent(prompt)
    actual = result["eval"].get("rating")
    response = result[JsonKey.RESPONSE]
    status = "PASS" if actual == expected else "FAIL"
    feedback = prompt_for_feedback(response, interactive=interactive)

    logger.info(
        f"#{index}: {prompt}\n→ Rating: {actual} | Expected: {expected} → {status}"
    )

    return {
        "id": test.get("id", f"test_{index}"),
        "prompt": prompt,
        "expected_rating": expected,
        "actual_rating": actual,
        "status": status,
        "feedback": feedback,
        JsonKey.RESPONSE: response[:250],
        ScoreKey.GROUNDING: result["eval"].get(ScoreKey.GROUNDING),
        ScoreKey.HELPFULNESS: result["eval"].get(ScoreKey.HELPFULNESS)[:100],
    }


def write_results_to_csv(results: list[dict], path: str) -> None:
    """
    Writes evaluation results to a CSV file.

    Args:
        results (list[dict]): List of test results.
        path (str): File path to write the CSV.
    """
    with open(path, "w", newline="", encoding=ENCODING) as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)


def run_golden_tests(interactive: bool = True) -> Any:
    """
    Orchestrates execution of all golden test cases.

    Args:
        interactive (bool): Whether to prompt for human feedback after each case.

    Returns:
        Any: None (side-effecting function that writes results to CSV and logs outcome).
    """
    results = []
    passed = 0
    logger.info("Running Golden Set Tests...\n")

    for i, test in enumerate(golden_tests, 1):
        result = evaluate_test_case(test, i, interactive=interactive)
        results.append(result)
        if result["status"] == "PASS":
            passed += 1

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = f"tests/results/golden_results_{timestamp}.csv"
    os.makedirs("tests/results", exist_ok=True)
    write_results_to_csv(results, output_path)

    logger.info(
        f"Done. {passed}/{len(golden_tests)} passed. Results saved to {output_path}"
    )


if __name__ == "__main__":
    run_golden_tests(interactive=True)
