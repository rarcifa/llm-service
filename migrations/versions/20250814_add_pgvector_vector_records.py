import sqlalchemy as sa
from alembic import op

# revision identifiers
revision = "pgvec_20250814"
down_revision = None  # or your latest
branch_labels = None
depends_on = None

EMBED_DIM = 384  # keep in sync with manifest
DISTANCE = "cosine"  # "l2" | "ip" | "cosine"
INDEX = "hnsw"  # "hnsw" | "ivfflat"

OPS = {
    "l2": "vector_l2_ops",
    "ip": "vector_ip_ops",
    "cosine": "vector_cosine_ops",
}[DISTANCE]


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "vector_records",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "session_id",
            sa.Uuid(),
            sa.ForeignKey("sessions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("collection", sa.String(), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False, index=True),
        sa.Column(
            "embedding", sa.dialects.postgresql.ARRAY(sa.Float()), nullable=False
        ),  # fallback if pgvector pkg not in env at migration time
        sa.Column("document", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.UniqueConstraint(
            "content_sha256", "collection", name="uq_vec_content_collection"
        ),
    )

    # Convert to pgvector column type (keeps migration tool simple)
    op.execute(
        f"ALTER TABLE vector_records ALTER COLUMN embedding TYPE vector({EMBED_DIM}) USING embedding::vector"
    )

    if INDEX == "hnsw":
        op.execute(
            f"CREATE INDEX IF NOT EXISTS ix_vec_embedding_hnsw "
            f"ON vector_records USING hnsw (embedding {OPS}) WITH (m = 16, ef_construction = 64)"
        )
    else:
        op.execute(
            f"CREATE INDEX IF NOT EXISTS ix_vec_embedding_ivf "
            f"ON vector_records USING ivfflat (embedding {OPS}) WITH (lists = 100)"
        )
    op.execute("ANALYZE vector_records")


def downgrade():
    op.drop_table("vector_records")
    # leave extension installed
