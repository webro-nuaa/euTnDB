from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class TnEntryBase(BaseModel):
    name: str
    family: str
    tn_group: str
    synonyms: Optional[str] = None
    isoform: Optional[str] = None
    accession_number: Optional[str] = None

    origin: Optional[str] = None
    mge_type: Optional[str] = None
    related_elements: Optional[str] = None

    length: Optional[int] = None
    ir: Optional[str] = None
    dr: Optional[int] = None
    orf: Optional[str] = None
    irl: Optional[str] = None
    irr: Optional[str] = None
    left_flank: Optional[str] = None
    right_flank: Optional[str] = None

    transposition: Optional[str] = None
    direct_repeat: Optional[str] = None

    dna_sequence: Optional[str] = None

    orf1_name: Optional[str] = None
    orf1_length: Optional[int] = None
    orf1_begin: Optional[int] = None
    orf1_end: Optional[int] = None
    orf1_strand: Optional[str] = None
    orf1_fusion_orf: Optional[str] = None
    orf1_function: Optional[str] = None
    orf1_chemistry: Optional[str] = None
    orf1_sequence: Optional[str] = None

    orf2_name: Optional[str] = None
    orf2_length: Optional[int] = None
    orf2_begin: Optional[int] = None
    orf2_end: Optional[int] = None
    orf2_strand: Optional[str] = None
    orf2_fusion_orf: Optional[str] = None
    orf2_function: Optional[str] = None
    orf2_chemistry: Optional[str] = None
    orf2_sequence: Optional[str] = None


class TnEntryCreate(TnEntryBase):
    pass


class TnEntryUpdate(BaseModel):
    name: Optional[str] = None
    family: Optional[str] = None
    tn_group: Optional[str] = None
    synonyms: Optional[str] = None
    isoform: Optional[str] = None
    accession_number: Optional[str] = None
    origin: Optional[str] = None
    mge_type: Optional[str] = None
    related_elements: Optional[str] = None
    length: Optional[int] = None
    ir: Optional[str] = None
    dr: Optional[int] = None
    orf: Optional[str] = None
    irl: Optional[str] = None
    irr: Optional[str] = None
    left_flank: Optional[str] = None
    right_flank: Optional[str] = None
    transposition: Optional[str] = None
    direct_repeat: Optional[str] = None
    dna_sequence: Optional[str] = None
    orf1_name: Optional[str] = None
    orf1_length: Optional[int] = None
    orf1_begin: Optional[int] = None
    orf1_end: Optional[int] = None
    orf1_strand: Optional[str] = None
    orf1_fusion_orf: Optional[str] = None
    orf1_function: Optional[str] = None
    orf1_chemistry: Optional[str] = None
    orf1_sequence: Optional[str] = None
    orf2_name: Optional[str] = None
    orf2_length: Optional[int] = None
    orf2_begin: Optional[int] = None
    orf2_end: Optional[int] = None
    orf2_strand: Optional[str] = None
    orf2_fusion_orf: Optional[str] = None
    orf2_function: Optional[str] = None
    orf2_chemistry: Optional[str] = None
    orf2_sequence: Optional[str] = None


class TnEntryResponse(TnEntryBase):
    id: int
    status: str
    submitted_by: Optional[int] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TnFilter(BaseModel):
    keyword: Optional[str] = None
    family: Optional[str] = None
    tn_group: Optional[str] = None
    origin: Optional[str] = None
    mge_type: Optional[str] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20


class TnListResponse(BaseModel):
    items: List[TnEntryResponse]
    total: int
    page: int
    page_size: int
