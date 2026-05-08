from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, utcnow


class BlastTask(Base):
    __tablename__ = "blast_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    sequence: Mapped[str] = mapped_column(Text, nullable=False)
    program: Mapped[str] = mapped_column(String(20), default="blastn")
    evalue: Mapped[float] = mapped_column(Float, default=1e-5)
    max_target_seqs: Mapped[int] = mapped_column(Integer, default=10)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    result: Mapped[dict | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    user = relationship("User")
