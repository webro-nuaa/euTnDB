from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class ReviewAction(BaseModel):
    action: str
    comment: Optional[str] = None


class ReviewHistoryResponse(BaseModel):
    id: int
    tn_entry_id: int
    reviewer_id: int
    action: str
    comment: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MineTnImportRequest(BaseModel):
    element_ids: List[str] = []


class MineTnTaskCreate(BaseModel):
    genome_file: str
    min_tir_length: int = 10
    max_tir_length: int = 50
    min_element_length: int = 50
    max_element_length: int = 15000
    min_tir_similarity: float = 0.8


class MineTnTaskResponse(BaseModel):
    id: int
    task_id: str
    status: str
    progress: int
    genome_file: str
    parameters: dict
    detected_count: Optional[int]
    result_file: Optional[str]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BlastTaskCreate(BaseModel):
    sequence: str
    program: str = "blastn"
    evalue: float = 1e-5
    max_target_seqs: int = 10


class BlastHitResponse(BaseModel):
    accession: str
    definition: str
    score: float
    evalue: float
    identity: float
    alignment_length: int
    query_start: int
    query_end: int
    subject_start: int
    subject_end: int


class BlastTaskResponse(BaseModel):
    id: int
    task_id: str
    status: str
    program: str
    hits: Optional[List[BlastHitResponse]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
