import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, JSON, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, server_default=func.gen_random_uuid(), comment="Canonical problem identifier")
    title: Mapped[str] = mapped_column(String, nullable=False, comment="Short internal name, e.g. 'Two Sum'")
    statement: Mapped[str] = mapped_column(Text, nullable=False, comment="Original, undisguised problem statement shown only internally")
    constraints: Mapped[dict] = mapped_column(JSON, nullable=False, comment="Input bounds and edge-case rules the translation must preserve exactly")
    reference_solution: Mapped[str] = mapped_column(Text, nullable=False, comment="Known-correct solution, used to validate translated variants")
    test_cases: Mapped[dict] = mapped_column(JSON, nullable=False, comment="Hidden test suite; never shown to the candidate")
    difficulty: Mapped[str] = mapped_column(String, nullable=False, comment="e.g. easy / medium / hard")
    tags: Mapped[dict] = mapped_column(JSON, nullable=False, comment="Topic tags for randomization, e.g. ['arrays', 'hash-map']")
    
    # Note: See the 'Bonus Tip' below regarding this column!
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    variants: Mapped[list["ProblemVariant"]] = relationship(back_populates="problem")


class ProblemVariant(Base):
    __tablename__ = "problem_variants"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    problem_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("problems.id", ondelete="RESTRICT"), nullable=False, comment="Source canonical problem this variant was translated from")
    translated_statement: Mapped[str] = mapped_column(Text, nullable=False, comment="LLM-generated disguised version shown to the candidate")
    embedding = mapped_column(Vector(768), nullable=True, comment="Embedding of translated_statement, used for scenario grounding + dedup checks")
    validated: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false", comment="True once the reference solution has passed against this variant's re-derived test cases")
    
    # Note: See the 'Bonus Tip' below regarding this column!
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    problem: Mapped["Problem"] = relationship(back_populates="variants")
    sessions: Mapped[list["Session"]] = relationship(back_populates="variant")