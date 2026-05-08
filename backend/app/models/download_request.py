from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, utcnow


class DownloadRequest(Base):
    __tablename__ = "download_request"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    requester_email: Mapped[str] = mapped_column(String(200), nullable=False)
    requester_name: Mapped[str | None] = mapped_column(String(100))
    requester_institution: Mapped[str | None] = mapped_column(String(200))

    requested_data: Mapped[str] = mapped_column(Text, nullable=False)
    data_format: Mapped[str] = mapped_column(String(20), default="fasta")
    purpose: Mapped[str | None] = mapped_column(Text)

    reviewer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    review_comment: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)

    reviewer = relationship("User", foreign_keys=[reviewer_id])
