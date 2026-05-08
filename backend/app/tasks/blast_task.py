import json
import os
import re
import subprocess
import tempfile

from celery import shared_task
from sqlalchemy import select

from app.core.config import settings
from app.core.database import utcnow
from app.tasks.celery_app import get_sync_session

VALID_DNA = set("ATGCN")
VALID_PROTEIN = set("ACDEFGHIKLMNPQRSTVWYX*")

NUCL_PROGRAMS = {"blastn", "blastx", "tblastn"}
PROT_PROGRAMS = {"blastp", "tblastx"}
PROT_DB_PROGRAMS = {"blastp", "blastx"}


def _clean_sequence(seq: str, is_nucleotide: bool = True) -> str:
    seq = seq.upper()
    seq = re.sub(r'\s+', '', seq)
    seq = re.sub(r'\d+', '', seq)
    if seq.startswith(">"):
        first_newline = seq.find('\n')
        if first_newline != -1:
            seq = seq[first_newline + 1:]
        seq = re.sub(r'\s+', '', seq)
    if is_nucleotide:
        seq = ''.join(c for c in seq if c in VALID_DNA)
    else:
        seq = ''.join(c for c in seq if c in VALID_PROTEIN)
    return seq


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def run_blast_task(self, task_id: str, sequence: str, program: str, evalue: float, max_target_seqs: int):
    from app.models import BlastTask, TnEntry  # noqa: F811

    session = get_sync_session()

    try:
        task = session.query(BlastTask).filter_by(task_id=task_id).first()
        if not task:
            return {"error": "Task not found"}

        task.status = "running"
        session.commit()

        is_protein_query = program in PROT_PROGRAMS
        is_protein_db = program in PROT_DB_PROGRAMS
        is_nucleotide_query = program in NUCL_PROGRAMS

        cleaned_seq = _clean_sequence(sequence, is_nucleotide=is_nucleotide_query)

        db_dir = settings.BLAST_DB_DIR
        db_path = _ensure_blast_db(db_dir, is_protein_db)

        if db_path is None:
            entries = session.query(TnEntry).all()
            fasta_entries = _build_fasta_entries(entries, is_protein_db)
            if fasta_entries:
                db_path = _build_blast_db(db_dir, fasta_entries, is_protein_db)
            else:
                task.status = "completed"
                task.result = []
                task.completed_at = utcnow()
                session.commit()
                return {"status": "completed", "hits": []}

        hits = _run_blast(cleaned_seq, db_path, program, evalue, max_target_seqs)

        entries = session.query(TnEntry).all()
        name_map = {e.name: e for e in entries}

        enriched = []
        for hit in hits:
            name = hit["name"]
            base_name = name.rsplit("_orf", 1)[0] if "_orf" in name else name
            entry = name_map.get(base_name) or name_map.get(name)
            enriched.append({
                **hit,
                "family": entry.family if entry else "",
                "origin": entry.origin if entry else "",
            })

        enriched.sort(key=lambda x: x.get("identity", 0), reverse=True)
        enriched = enriched[:max_target_seqs]

        task.status = "completed"
        task.result = enriched
        task.completed_at = utcnow()
        session.commit()

        return {"status": "completed", "hits": enriched}

    except Exception as exc:
        task = session.query(BlastTask).filter_by(task_id=task_id).first()
        if task:
            task.status = "failed"
            task.error_message = str(exc)
            task.completed_at = utcnow()
            session.commit()
        raise self.retry(exc=exc)

    finally:
        session.close()


def _ensure_blast_db(db_dir: str, is_protein: bool) -> str | None:
    prefix = "tndb_prot" if is_protein else "tndb"
    ext = ".phr" if is_protein else ".nhr"
    path = os.path.join(db_dir, prefix)
    return path if os.path.exists(path + ext) else None


def _build_fasta_entries(entries, is_protein: bool) -> list[tuple[str, str]]:
    result = []
    if is_protein:
        for e in entries:
            for field in ("orf1_sequence", "orf2_sequence"):
                seq = (getattr(e, field, None) or "").upper()
                seq = re.sub(r'[^ACDEFGHIKLMNPQRSTVWYX*]', '', seq)
                if seq and len(seq) >= 5:
                    result.append((f"{e.name}_{field.replace('_sequence', '')}", seq))
    else:
        for e in entries:
            seq = (e.dna_sequence or "").upper()
            seq = re.sub(r'[^ATGCN]', '', seq)
            if seq and len(seq) >= 10:
                result.append((e.name, seq))
    return result


def _build_blast_db(db_dir: str, fasta_entries: list[tuple[str, str]], is_protein: bool) -> str:
    os.makedirs(db_dir, exist_ok=True)
    prefix = "tndb_prot" if is_protein else "tndb"
    dbtype = "prot" if is_protein else "nucl"
    fasta_path = os.path.join(db_dir, f"{prefix}.fasta")
    db_path = os.path.join(db_dir, prefix)

    with open(fasta_path, 'w') as f:
        for name, seq in fasta_entries:
            f.write(f">{name}\n{seq}\n")

    subprocess.run(
        ["makeblastdb", "-in", fasta_path, "-dbtype", dbtype, "-out", db_path, "-parse_seqids"],
        capture_output=True, text=True, timeout=120, check=True,
    )
    return db_path


def _run_blast(query_seq: str, db_path: str, program: str, evalue: float, max_target_seqs: int) -> list[dict]:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as qf:
        qf.write(f">query\n{query_seq}\n")
        query_file = qf.name

    out_file = query_file + ".out"
    try:
        subprocess.run(
            [program, "-query", query_file, "-db", db_path, "-evalue", str(evalue),
             "-max_target_seqs", str(max_target_seqs), "-outfmt", "15", "-out", out_file],
            capture_output=True, text=True, timeout=300, check=True,
        )
        if not os.path.exists(out_file):
            return []

        with open(out_file, 'r') as f:
            data = json.load(f)

        hits = []
        for report in data.get("BlastOutput2", []):
            for search in report.get("report", {}).get("results", {}).get("search", {}).get("hits", []):
                desc = search.get("description", [{}])[0]
                name = desc.get("accession", "") or desc.get("id", "")
                for hsp in search.get("hsps", []):
                    hits.append({
                        "name": name,
                        "identity": hsp.get("identity", 0) / hsp.get("align_len", 1) if hsp.get("align_len") else 0,
                        "score": hsp.get("bit_score", 0),
                        "evalue": hsp.get("evalue", 1),
                        "alignment_length": hsp.get("align_len", 0),
                        "query_start": hsp.get("query_from", 1),
                        "query_end": hsp.get("query_to", 1),
                        "subject_start": hsp.get("hit_from", 1),
                        "subject_end": hsp.get("hit_to", 1),
                    })
        return hits
    finally:
        for f in [query_file, out_file]:
            if os.path.exists(f):
                os.unlink(f)
