import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, JSON, DateTime, Boolean, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.db.base_class import Base


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, server_default=func.gen_random_uuid(), comment="Canonical problem identifier")
    title: Mapped[str] = mapped_column(String, unique=True, nullable=False, comment="Short internal name, e.g. 'Two Sum'")
    statement: Mapped[str] = mapped_column(Text, nullable=False, comment="Original, undisguised problem statement shown only internally")
    signature: Mapped[dict] = mapped_column(JSON, nullable=False, server_default='{}', comment="Strict I/O typing (function name, args, returns) to enforce LLM boundaries")
    constraints: Mapped[dict] = mapped_column(JSON, nullable=False, comment="Input bounds and edge-case rules the translation must preserve exactly")
    reference_solution: Mapped[str] = mapped_column(Text, nullable=False, comment="Known-correct solution, used to validate translated variants")
    test_cases: Mapped[dict] = mapped_column(JSON, nullable=False, comment="Hidden test suite; never shown to the candidate")
    difficulty: Mapped[str] = mapped_column(String, nullable=False, comment="e.g. easy / medium / hard")
    tags: Mapped[dict] = mapped_column(JSON, nullable=False, comment="Topic tags for randomization, e.g. ['arrays', 'hash-map']")
    
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    variants: Mapped[list["ProblemVariant"]] = relationship(back_populates="problem")


class ProblemVariant(Base):
    __tablename__ = "problem_variants"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    problem_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, comment="Source canonical problem this variant was translated from")
    translated_statement: Mapped[str] = mapped_column(Text, nullable=False, comment="LLM-generated disguised version shown to the candidate")
    
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    scenario_context: Mapped[str] = mapped_column(Text, nullable=False, comment="The overarching theme (e.g., 'Logistics coordinator for space cargo')")
    stage_1_mvp: Mapped[str] = mapped_column(Text, nullable=False, comment="The initial coding task (Disguised LeetCode)")
    stage_2_curveball: Mapped[str] = mapped_column(Text, nullable=False, comment="The sudden requirement change to test adaptability")
    stage_3_system: Mapped[str] = mapped_column(Text, nullable=False, comment="The architecture/scaling discussion prompt")
    technical_rubric: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"), comment="Time/space tradeoffs, expected data structures, edge cases to catch")
    system_rubric: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"), comment="Expected system design concepts (e.g., Redis, Sharding, CAP theorem)")
    communication_rubric: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"), comment="Questions they should have asked, testing strategies they should suggest")
    embedding = mapped_column(Vector(768), nullable=True, comment="Embedding of the scenario_context for dedup checks")
    validated: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"), comment="True once the reference solution has passed")

    problem: Mapped["Problem"] = relationship(back_populates="variants")
    sessions: Mapped[list["Session"]] = relationship(back_populates="variant")