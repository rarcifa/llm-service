"""Module documentation for `app/common/utils/files.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

import os
from pathlib import Path
from typing import List

from app.common.decorators.errors import catch_and_log_errors
from app.common.utils.logger import setup_logger

logger = setup_logger()


@catch_and_log_errors(default_return=[])
def find_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
    """Summary of `find_files_by_extension`.

    Args:
        directory (str): Description of directory.
        extensions (List[str]): Description of extensions.

    Returns:
        List[str]: Description of return value.

    """
    files = []
    for ext in extensions:
        files.extend(Path(directory).rglob(ext))
    logger.info(
        "Found files", directory=directory, count=len(files), extensions=extensions
    )
    return [str(f) for f in files]
