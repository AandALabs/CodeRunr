import uuid

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Uuid,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.base import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(Uuid, unique=True, nullable=False, default=uuid.uuid4, index=True)

    # Code
    source_code = Column(Text, nullable=False)
    language_id = Column(Integer, nullable=False)

    # I/O
    stdin = Column(Text, nullable=True)
    expected_output = Column(Text, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    compile_output = Column(Text, nullable=True)
    message = Column(Text, nullable=True)

    # Verdict
    status = Column(String(64), nullable=False, default="Queued")
    time = Column(Float, nullable=True)
    wall_time = Column(Float, nullable=True)
    memory = Column(Integer, nullable=True)
    exit_code = Column(Integer, nullable=True)
    exit_signal = Column(Integer, nullable=True)

    # Limits
    cpu_time_limit = Column(Float, nullable=False, default=5)
    cpu_extra_time = Column(Float, nullable=False, default=1)
    wall_time_limit = Column(Float, nullable=False, default=10)
    memory_limit = Column(Integer, nullable=False, default=128000)
    stack_limit = Column(Integer, nullable=False, default=65536)
    max_file_size = Column(Integer, nullable=False, default=1024)
    max_processes_and_or_threads = Column(Integer, nullable=False, default=60)
    enable_per_process_and_thread_time_limit = Column(Boolean, default=True)
    enable_per_process_and_thread_memory_limit = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())
    finished_at = Column(DateTime, nullable=True)

    # Batch relationship (nullable — standalone submissions have no batch)
    batch_token = Column(Uuid, ForeignKey("submission_batches.token"), nullable=True)
    batch = relationship("SubmissionBatch", back_populates="submissions")
