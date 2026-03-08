"""
RQ Worker — processes submissions asynchronously.

Run with:  rq worker submissions --url redis://localhost:6379/0
Or:        python worker.py
"""

import logging
import asyncio
from uuid import UUID
from datetime import datetime, timezone

from core.config import settings
from db.session import AsyncSessionLocal
from db.repository.languages import get_language
from db.repository.submissions import get_submission_by_token
from schema import Submission, SubmissionLanguage, Status
from job.isolate_job import IsolateJob

logger = logging.getLogger(__name__)


async def async_process_submission(submission_token: str) -> None:
    """
    Main task function invoked by the RQ worker.

    1. Loads the submission from PostgreSQL.
    2. Builds the internal Submission schema and IsolateJob.
    3. Runs the job inside the sandbox.
    4. Writes results back to the database.
    """
    token = UUID(submission_token)

    try:
        async with AsyncSessionLocal() as db:
            row = await get_submission_by_token(db, token)

            if row is None:
                logger.error("Submission %s not found", token)
                return

            language = await get_language(db, row.language_id)
            if language is None:
                row.status = Status.boxerr.value["value"]
                row.message = f"Unsupported language_id: {row.language_id}"
                await db.commit()
                return

            # Mark as processing
            row.status = Status.process.value["value"]
            await db.commit()

            # Build internal schema
            submission = Submission(
                id=row.id,
                language=SubmissionLanguage.model_validate(language),
                source_code=row.source_code,
                stdin=row.stdin or "",
                expected_output=row.expected_output,
                cpu_time_limit=int(row.cpu_time_limit),
                cpu_extra_time=int(row.cpu_extra_time),
                wall_time_limit=int(row.wall_time_limit),
                memory_limit=row.memory_limit,
                stack_limit=row.stack_limit,
                max_file_size=row.max_file_size,
                max_processes_and_or_threads=row.max_processes_and_or_threads,
                enable_per_process_and_thread_time_limit=row.enable_per_process_and_thread_time_limit,
                enable_per_process_and_thread_memory_limit=row.enable_per_process_and_thread_memory_limit,
            )

            # Run in sandbox
            job = IsolateJob(submission)
            job.run_job()

            # Write results back
            row.status = submission.status.value["value"]
            row.stdout = submission.stdout
            row.stderr = submission.stderr
            row.compile_output = submission.compile_output
            row.time = submission.time
            row.wall_time = submission.wall_time
            row.memory = submission.memory
            row.exit_code = submission.exit_code
            row.exit_signal = submission.exit_signal
            row.message = submission.message
            row.finished_at = datetime.now(timezone.utc)

            await db.commit()
            logger.info("Submission %s processed → %s", token, row.status)

    except Exception:
        logger.exception("Failed to process submission %s", token)
        # Mark as internal error
        if row:
            row.status = Status.boxerr.value["value"]
            row.message = "Internal worker error"
            await db.commit()


def process_submission(submission_token: str) -> None:
    asyncio.run(async_process_submission(submission_token))


# ---------------------------------------------------------------------------
# Entry point — run as standalone worker
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from redis import Redis
    from rq import Worker

    logging.basicConfig(level=logging.INFO)

    conn = Redis.from_url(settings.REDIS_URL)
    worker = Worker([settings.REDIS_QUEUE_NAME], connection=conn)
    worker.work()
