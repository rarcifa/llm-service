"""Merge heads

Revision ID: 09494a513e2f
Revises: pgvec_20250814, 2344c21b49f6
Create Date: 2025-08-14 20:16:44.273928

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "09494a513e2f"
down_revision: Union[str, Sequence[str], None] = ("pgvec_20250814", "2344c21b49f6")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
