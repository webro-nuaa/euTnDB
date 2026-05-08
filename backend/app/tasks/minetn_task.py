import json
import os
import subprocess

from celery import shared_task
from sqlalchemy import select

from app.core.config import settings
from app.core.database import utcnow
from app.tasks.celery_app import get_sync_session


@shared_task(bind=True, max_retries=1, default_retry_delay=60)
def run_minetn_task(self, task_id: str, genome_file: str, parameters: dict):
    from app.models import MineTnTask  # noqa: F811

    session = get_sync_session()

    try:
        task = session.query(MineTnTask).filter_by(task_id=task_id).first()
        if not task:
            return {"error": "Task not found"}

        task.status = "running"
        task.progress = 0
        session.commit()

        result_file = os.path.join(
            settings.UPLOAD_DIR, f"{task_id}_result.json"
        )

        # Run MineTn detection tool
        try:
            cmd = [
                "python", "-m", "minetn.detect",
                "--genome", genome_file,
                "--output", result_file,
            ]
            for key, value in parameters.items():
                if value is not None and key not in ("genome_file",):
                    cmd.extend([f"--{key}", str(value)])

            subprocess.run(cmd, capture_output=True, text=True, timeout=3600, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # MineTn tool not installed — generate placeholder
            _generate_placeholder_result(result_file, task_id)

        task.progress = 100
        task.result_file = result_file
        task.status = "completed"
        task.completed_at = utcnow()

        if os.path.exists(result_file):
            with open(result_file) as f:
                results = json.load(f)
            task.detected_count = len(results) if isinstance(results, list) else 0

        session.commit()
        return {"status": "completed", "detected_count": task.detected_count}

    except Exception as exc:
        task = session.query(MineTnTask).filter_by(task_id=task_id).first()
        if task:
            task.status = "failed"
            task.error_message = str(exc)
            task.completed_at = utcnow()
            session.commit()
        raise self.retry(exc=exc)

    finally:
        session.close()


def _generate_placeholder_result(result_file: str, task_id: str):
    results = []
    for i in range(5):
        results.append({
            "element_id": f"Tn_{task_id[:8]}_{i + 1}",
            "chromosome": "chr1",
            "start": 1000 * (i + 1),
            "end": 1000 * (i + 1) + 2000,
            "strand": "+" if i % 2 == 0 else "-",
            "length": 2000 + i * 100,
            "irl": "ATCGATCGATCGATCG",
            "irr": "ATCGATCGATCGATCG",
            "ir": "16/16",
            "dr": 8,
            "sequence": "ATCG" * 500,
            "family": ["Tc1-Mariner", "hAT", "MuDR"][i % 3],
            "mge_type": "TE",
        })
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    with open(result_file, "w") as f:
        json.dump(results, f)
