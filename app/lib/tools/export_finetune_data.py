"""
export_finetune_data.py

Processes evaluation logs and extracts high-quality examples to prepare
fine-tuning datasets for language models. This includes:
- Reading structured JSONL data line-by-line
- Filtering examples marked as "pass" or "thumbs_up"
- Extracting prompt and completion pairs
- Writing the cleaned data to a newline-delimited JSON file

Typical use case:
    python export_finetune_data.py

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import json
from pathlib import Path
from typing import Dict, List

from app.constants.values import ENCODING, INPUT_FILE, OUTPUT_FILE
from app.enums.prompts import JsonKey
from app.lib.utils.decorators.errors import catch_and_log_errors
from app.lib.utils.logger import setup_logger

logger = setup_logger()


@catch_and_log_errors(default_return=[])
def load_raw_lines(path: Path) -> List[dict]:
    """
    Loads newline-delimited JSON entries from the specified file.

    Args:
        path (Path): Path to the input JSONL file.

    Returns:
        List[dict]: Parsed list of JSON entries, skipping malformed lines.
    """
    lines = []
    with path.open("r", encoding=ENCODING) as f:
        for line in f:
            try:
                lines.append(json.loads(line))
            except Exception as e:
                logger.warning("Skipping malformed line", error=str(e))
    return lines


def filter_valid_examples(lines: List[dict]) -> List[Dict[str, str]]:
    """
    Filters out examples that don't meet quality criteria (e.g., not rated "pass" or "thumbs_up").

    Args:
        lines (List[dict]): List of raw JSONL log lines.

    Returns:
        List[Dict[str, str]]: Cleaned examples with 'prompt' and 'completion' keys.
    """
    examples = []
    for item in lines:
        rating = item.get(JsonKey.RATING)
        if rating not in ("pass", "thumbs_up"):
            continue

        # Try multiple fallback keys for prompt
        prompt = item.get(JsonKey.INPUT, {}).get("raw") or item.get(
            JsonKey.INPUT, {}
        ).get("prompt")
        completion = item.get("output", {}).get(JsonKey.RESPONSE)

        if prompt and completion:
            examples.append(
                {"prompt": prompt.strip(), "completion": completion.strip()}
            )

    return examples


@catch_and_log_errors()
def write_examples_to_file(examples: List[dict], path: Path) -> None:
    """
    Writes prompt-completion examples to a JSONL file.

    Args:
        examples (List[dict]): Clean prompt-completion pairs.
        path (Path): Path to write the output file.
    """
    with path.open("w", encoding=ENCODING) as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    logger.info("Saved fine-tune examples", count=len(examples), path=str(path))


def export_finetune_data():
    """
    Orchestrates the data export process from raw eval logs to fine-tuning file format.
    """
    raw_lines = load_raw_lines(INPUT_FILE)
    examples = filter_valid_examples(raw_lines)
    write_examples_to_file(examples, OUTPUT_FILE)


if __name__ == "__main__":
    export_finetune_data()
