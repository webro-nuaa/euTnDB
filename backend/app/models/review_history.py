from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, utcnow


class ReviewHistory(Base):
    __tablename__ = "review_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tn_entry_id: Mapped[int] = mapped_column(Integer, ForeignKey("tn_entry.id"), nullable=False)
    reviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    old_data: Mapped[dict | None] = mapped_column(JSON)
    new_data: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    tn_entry = relationship("TnEntry", back_populates="review_histories")
    reviewer = relationship("User", back_populates="review_histories")
