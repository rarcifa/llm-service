"""
file_utils.py

Provides a utility function to recursively search for files in a given directory
that match a list of file extensions. Useful for document ingestion, media scanning,
or project cleanup tools.

Includes error handling and structured logging.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import os
from pathlib import Path
from typing import List

from app.lib.utils.decorators.errors import catch_and_log_errors
from app.lib.utils.logger import setup_logger

logger = setup_logger()


@catch_and_log_errors(default_return=[])
def find_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
    """
    Recursively finds files in a directory that match given file extensions.

    Args:
        directory (str): The root directory to search within.
        extensions (List[str]): A list of file patterns (e.g., ["*.txt", "*.md"]).

    Returns:
        List[str]: A list of matching file paths as strings.
                   Returns an empty list on failure.
    """
    files = []
    for ext in extensions:
        # rglob supports recursive glob pattern matching like "*.txt"
        files.extend(Path(directory).rglob(ext))

    logger.info(
        "Found files", directory=directory, count=len(files), extensions=extensions
    )
    return [str(f) for f in files]
