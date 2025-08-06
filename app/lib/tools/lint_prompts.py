"""
lint_prompts.py

Lints all YAML prompt templates in the PROMPT_DIR by checking for:
1. Required metadata keys (id, name, template, placeholders)
2. Correct use of declared placeholders within Jinja2 template syntax
3. Missing or unused placeholder variables

This script helps enforce prompt structure consistency and prevents runtime errors.

Usage:
    python lint_prompts.py

Returns:
    0 if all prompt files are valid
    1 if any linting issues are detected

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from pathlib import Path

import yaml
from jinja2 import Environment, meta

from app.constants.values import ENCODING, PROMPT_DIR
from app.lib.utils.decorators.errors import catch_and_log_errors
from app.lib.utils.logger import setup_logger

logger = setup_logger()


def load_prompt_file(file_path: Path) -> dict:
    """
    Loads a YAML prompt file and parses it into a dictionary.

    Args:
        file_path (Path): Path to the YAML file.

    Returns:
        dict: Parsed contents of the prompt file.
    """
    with open(file_path, "r", encoding=ENCODING) as f:
        return yaml.safe_load(f)


@catch_and_log_errors(default_return=["invalid_yaml"])
def lint_prompt_file(file: Path) -> list[str]:
    """
    Validates structure and variable consistency of a single prompt file.

    Checks for:
    - Required keys: id, name, template, placeholders
    - Declared placeholders match Jinja2 variables in template

    Args:
        file (Path): The prompt file to validate.

    Returns:
        list[str]: Lint messages, or ["invalid_yaml"] on failure.
    """
    logger.info("Checking prompt file", file=str(file))
    config = load_prompt_file(file)
    messages = []

    # Step 1: Check required metadata keys
    required_keys = {"id", "name", "template", "placeholders"}
    if not required_keys.issubset(config):
        missing = required_keys - config.keys()
        messages.append(f"{file.name}: missing keys: {missing}")
        return messages

    # Step 2: Parse Jinja2 template and extract variables
    template = config["template"]
    placeholders = set(config.get("placeholders", []))

    env = Environment()
    parsed = env.parse(template)
    undeclared_vars = meta.find_undeclared_variables(parsed)

    # Step 3: Compare declared placeholders and actual variables
    missing_in_template = placeholders - undeclared_vars
    missing_in_placeholders = undeclared_vars - placeholders

    if missing_in_template:
        messages.append(
            f"{file.name}: placeholders not used in template: {sorted(missing_in_template)}"
        )
    if missing_in_placeholders:
        messages.append(
            f"{file.name}: undeclared placeholders in template: {sorted(missing_in_placeholders)}"
        )

    if not missing_in_template and not missing_in_placeholders:
        messages.append(f"{file.name}: OK")

    return messages


def main() -> int:
    """
    Lints all YAML files in the configured PROMPT_DIR.

    Returns:
        int: 0 if all prompts pass, 1 if any file has issues.
    """
    files = list(PROMPT_DIR.glob("*.yaml"))
    total = len(files)
    issues = 0

    for file in files:
        results = lint_prompt_file(file)
        for message in results:
            logger.info("lint_result", file=file.name, message=message)
            if "OK" not in message:
                issues += 1

    logger.info("Linting complete", total_files=total, files_with_issues=issues)
    return 1 if issues > 0 else 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
