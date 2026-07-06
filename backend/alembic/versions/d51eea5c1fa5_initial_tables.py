"""initial tables

Revision ID: d51eea5c1fa5
Revises: 
Create Date: 2026-07-06 10:49:46.343406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'd51eea5c1fa5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from pgvector.sqlalchemy import Vector


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "problems",
        sa.Column(
            "id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()"),
            comment="Canonical problem identifier",
        ),
        sa.Column(
            "title", sa.String, nullable=False,
            comment="Short internal name, e.g. 'Two Sum'",
        ),
        sa.Column(
            "statement", sa.Text, nullable=False,
            comment="Original, undisguised problem statement shown only internally",
        ),
        sa.Column(
            "constraints", sa.JSON, nullable=False,
            comment="Input bounds and edge-case rules the translation must preserve exactly",
        ),
        sa.Column(
            "reference_solution", sa.Text, nullable=False,
            comment="Known-correct solution, used to validate translated variants",
        ),
        sa.Column(
            "test_cases", sa.JSON, nullable=False,
            comment="Hidden test suite; never shown to the candidate",
        ),
        sa.Column(
            "difficulty", sa.String, nullable=False,
            comment="e.g. easy / medium / hard",
        ),
        sa.Column(
            "tags", sa.JSON, nullable=False,
            comment="Topic tags for randomization, e.g. ['arrays', 'hash-map']",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "problem_variants",
        sa.Column(
            "id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "problem_id",
            sa.UUID,
            sa.ForeignKey("problems.id", ondelete="RESTRICT"),
            nullable=False,
            comment="Source canonical problem this variant was translated from",
        ),
        sa.Column(
            "translated_statement", sa.Text, nullable=False,
            comment="LLM-generated disguised version shown to the candidate",
        ),
        sa.Column(
            "embedding", Vector(1536),
            comment="Embedding of translated_statement, used for scenario grounding + dedup checks",
        ),
        sa.Column(
            "validated", sa.Boolean, nullable=False, server_default=sa.text("false"),
            comment="True once the reference solution has passed against this variant's re-derived test cases",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "sessions",
        sa.Column(
            "id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "problem_variant_id",
            sa.UUID,
            sa.ForeignKey("problem_variants.id", ondelete="RESTRICT"),
            nullable=False,
            comment="Which disguised variant this interview session used",
        ),
        sa.Column(
            "status", sa.String, nullable=False, server_default="pending",
            comment="pending / active / completed / abandoned",
        ),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("sessions")
    op.drop_table("problem_variants")
    op.drop_table("problems")

    op.execute("DROP EXTENSION IF EXISTS vector")
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")