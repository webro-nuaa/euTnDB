from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base, utcnow


class TnFamily(Base):
    __tablename__ = "tn_family"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    family_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    superfamily: Mapped[str] = mapped_column(String(50), nullable=False)
    consensus_seq: Mapped[str | None] = mapped_column(Text)
    member_count: Mapped[int] = mapped_column(Integer, default=0)
    alignment_file: Mapped[str | None] = mapped_column(String(255))
    tree_file: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
