import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    
    problem_variant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("problem_variants.id", ondelete="RESTRICT"), nullable=False, comment="Which disguised variant this interview session used")
    
    status: Mapped[str] = mapped_column(String, nullable=False, server_default="pending", comment="pending / active / completed / abandoned")
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    variant: Mapped["ProblemVariant"] = relationship(back_populates="sessions")