from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, utcnow


class TnEntry(Base):
    __tablename__ = "tn_entry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    family: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tn_group: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    synonyms: Mapped[str | None] = mapped_column(Text)
    isoform: Mapped[str | None] = mapped_column(String(100))
    accession_number: Mapped[str | None] = mapped_column(String(100), index=True)

    origin: Mapped[str | None] = mapped_column(String(200), index=True)
    mge_type: Mapped[str | None] = mapped_column(String(50))
    related_elements: Mapped[str | None] = mapped_column(Text)

    length: Mapped[int | None] = mapped_column(Integer)
    ir: Mapped[str | None] = mapped_column(String(50))
    dr: Mapped[int | None] = mapped_column(Integer)
    orf: Mapped[str | None] = mapped_column(String(50))
    irl: Mapped[str | None] = mapped_column(Text)
    irr: Mapped[str | None] = mapped_column(Text)
    left_flank: Mapped[str | None] = mapped_column(Text)
    right_flank: Mapped[str | None] = mapped_column(Text)

    transposition: Mapped[str | None] = mapped_column(String(100))
    direct_repeat: Mapped[str | None] = mapped_column(Text)

    dna_sequence: Mapped[str | None] = mapped_column(Text)

    orf1_name: Mapped[str | None] = mapped_column(String(100))
    orf1_length: Mapped[int | None] = mapped_column(Integer)
    orf1_begin: Mapped[int | None] = mapped_column(Integer)
    orf1_end: Mapped[int | None] = mapped_column(Integer)
    orf1_strand: Mapped[str | None] = mapped_column(String(1))
    orf1_fusion_orf: Mapped[str | None] = mapped_column(String(10))
    orf1_function: Mapped[str | None] = mapped_column(String(100))
    orf1_chemistry: Mapped[str | None] = mapped_column(String(50))
    orf1_sequence: Mapped[str | None] = mapped_column(Text)

    orf2_name: Mapped[str | None] = mapped_column(String(100))
    orf2_length: Mapped[int | None] = mapped_column(Integer)
    orf2_begin: Mapped[int | None] = mapped_column(Integer)
    orf2_end: Mapped[int | None] = mapped_column(Integer)
    orf2_strand: Mapped[str | None] = mapped_column(String(1))
    orf2_fusion_orf: Mapped[str | None] = mapped_column(String(10))
    orf2_function: Mapped[str | None] = mapped_column(String(100))
    orf2_chemistry: Mapped[str | None] = mapped_column(String(50))
    orf2_sequence: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    submitted_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    reviewed_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    submitter = relationship("User", foreign_keys=[submitted_by], back_populates="tn_entries")
    reviewer = relationship("User", foreign_keys=[reviewed_by], back_populates="reviewed_entries")
    review_histories = relationship("ReviewHistory", back_populates="tn_entry", cascade="all, delete-orphan")
