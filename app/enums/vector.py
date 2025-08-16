"""Vector/embedding related enums.

Generated on 2025-08-16.
"""

from enum import StrEnum


class DistanceMetric(StrEnum):
    COSINE = "cosine"
    L2 = "l2"
    INNER = "inner"
