from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.common import ApiResponse

router = APIRouter(prefix="/analyze", tags=["Analysis"])


class AnalyzeRequest(BaseModel):
    dna_sequence: str
    family: Optional[str] = None


class AnalyzeResult(BaseModel):
    length: int
    gc_content: float
    irl: Optional[str] = None
    irr: Optional[str] = None
    ir: Optional[str] = None
    dr: Optional[int] = None
    direct_repeat: Optional[str] = None
    orf1_begin: Optional[int] = None
    orf1_end: Optional[int] = None
    orf1_length: Optional[int] = None
    orf1_strand: Optional[str] = None
    orf2_begin: Optional[int] = None
    orf2_end: Optional[int] = None
    orf2_length: Optional[int] = None
    orf2_strand: Optional[str] = None
    orf: Optional[str] = None
    orf1_function: Optional[str] = None
    orf1_chemistry: Optional[str] = None
    orf2_function: Optional[str] = None
    orf2_chemistry: Optional[str] = None
    transposition: Optional[str] = None
    mge_type: Optional[str] = None


@router.post("/sequence", response_model=ApiResponse[AnalyzeResult])
async def analyze_sequence(data: AnalyzeRequest):
    seq = data.dna_sequence.upper().strip()
    if not seq:
        return ApiResponse(data=AnalyzeResult(length=0, gc_content=0.0))

    result = AnalyzeResult(
        length=len(seq),
        gc_content=round((seq.count('G') + seq.count('C')) / len(seq) * 100, 2),
    )

    irl, irr, ir_match, ir_total = detect_tir(seq)
    if irl:
        result.irl = irl
        result.irr = irr
        result.ir = f"{ir_match}/{ir_total}"

    tsd_len, tsd_seq = detect_tsd(seq)
    if tsd_len and tsd_len > 0:
        result.dr = tsd_len
        result.direct_repeat = tsd_seq

    orfs = predict_orfs(seq)
    if len(orfs) >= 1:
        o = orfs[0]
        result.orf1_begin = o["begin"]
        result.orf1_end = o["end"]
        result.orf1_length = o["length"]
        result.orf1_strand = o["strand"]
    if len(orfs) >= 2:
        o = orfs[1]
        result.orf2_begin = o["begin"]
        result.orf2_end = o["end"]
        result.orf2_length = o["length"]
        result.orf2_strand = o["strand"]

    if result.orf1_length or result.orf2_length:
        parts = []
        if result.orf1_length:
            parts.append(str(result.orf1_length))
        if result.orf2_length:
            parts.append(str(result.orf2_length))
        result.orf = "/".join(parts)

    if data.family:
        family_lower = data.family.lower()
        if "pif" in family_lower or "harbinger" in family_lower:
            result.orf1_function = "Transposase"
            result.orf1_chemistry = "DDE"
            result.orf2_function = "Yqaj"
            result.transposition = "Cut-and-paste"
        elif "tc1" in family_lower or "mariner" in family_lower:
            result.orf1_function = "Transposase"
            result.orf1_chemistry = "DDE"
            result.transposition = "Cut-and-paste"
        elif "hat" in family_lower:
            result.orf1_function = "Transposase"
            result.orf1_chemistry = "DDE"
            result.transposition = "Cut-and-paste"
        elif "mudr" in family_lower:
            result.orf1_function = "Transposase"
            result.orf1_chemistry = "DDE"
            result.transposition = "Cut-and-paste"
        elif "enspm" in family_lower or "cacta" in family_lower:
            result.orf1_function = "Transposase"
            result.orf1_chemistry = "DDE"
            result.transposition = "Cut-and-paste"
        elif "piggybac" in family_lower:
            result.orf1_function = "Transposase"
            result.orf1_chemistry = "DDD"
            result.transposition = "Cut-and-paste"
        elif "merlin" in family_lower:
            result.orf1_function = "Transposase"
            result.orf1_chemistry = "DDE"
            result.transposition = "Cut-and-paste"
        elif "helitron" in family_lower:
            result.orf1_function = "RepHel"
            result.orf1_chemistry = "Y1"
            result.transposition = "Rolling-circle"

        if result.length and result.length < 1500 and result.orf1_length is None:
            result.mge_type = "MITE"
        else:
            result.mge_type = "TE"

    return ApiResponse(data=result)


def detect_tir(seq: str, min_len: int = 10, max_len: int = 50) -> tuple:
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}

    def rev_comp(s: str) -> str:
        return ''.join(complement.get(c, 'N') for c in reversed(s))

    for length in range(min_len, min(max_len + 1, len(seq) // 4)):
        left = seq[:length]
        right = seq[-length:]
        rc_right = rev_comp(right)

        matches = sum(1 for a, b in zip(left, rc_right) if a == b)
        similarity = matches / length

        if similarity >= 0.7:
            return left, right, matches, length

    return None, None, None, None


def detect_tsd(seq: str, max_len: int = 20) -> tuple:
    for length in range(2, max_len + 1):
        flank_len = min(200, len(seq) // 4)
        left_flank = seq[:flank_len]
        right_flank = seq[-flank_len:]

        for offset in range(flank_len - length):
            candidate = left_flank[offset:offset + length]
            if 'N' in candidate:
                continue
            for r_offset in range(flank_len - length):
                right_candidate = right_flank[r_offset:r_offset + length]
                if candidate == right_candidate:
                    return length, candidate

    return 0, None


def predict_orfs(seq: str, min_length: int = 300) -> list:
    start_codons = {'ATG'}
    stop_codons = {'TAA', 'TAG', 'TGA'}
    orfs = []

    for strand, sequence in [('+', seq), ('-', _reverse_complement(seq))]:
        for frame in range(3):
            i = frame
            while i < len(sequence) - 2:
                codon = sequence[i:i + 3]
                if codon in start_codons:
                    orf_start = i
                    j = i + 3
                    found_stop = False
                    while j < len(sequence) - 2:
                        next_codon = sequence[j:j + 3]
                        if next_codon in stop_codons:
                            orf_end = j + 3
                            orf_length = orf_end - orf_start
                            if orf_length >= min_length:
                                if strand == '+':
                                    orfs.append({
                                        "begin": orf_start + 1,
                                        "end": orf_end,
                                        "length": orf_length,
                                        "strand": "+"
                                    })
                                else:
                                    orfs.append({
                                        "begin": len(seq) - orf_start,
                                        "end": len(seq) - orf_end + 1,
                                        "length": orf_length,
                                        "strand": "-"
                                    })
                            found_stop = True
                            i = j + 3
                            break
                        j += 3
                    if not found_stop:
                        i += 3
                else:
                    i += 3

    orfs.sort(key=lambda x: x["length"], reverse=True)

    filtered = []
    for orf in orfs:
        overlap = False
        for existing in filtered:
            if (orf["strand"] == existing["strand"] and
                orf["begin"] < existing["end"] and orf["end"] > existing["begin"]):
                overlap = True
                break
        if not overlap:
            filtered.append(orf)
        if len(filtered) >= 2:
            break

    return filtered


def _reverse_complement(seq: str) -> str:
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
    return ''.join(complement.get(c, 'N') for c in reversed(seq))
