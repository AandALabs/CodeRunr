"""
Pydantic schemas for the Submission API.

Internal models (used by IsolateJob):
  - Status, StatusDict, SubmissionLanguage, Submission

API-facing models (request / response):
  - SubmissionCreate, SubmissionResponse
  - SubmissionBatchCreate, SubmissionBatchResponse
"""

from enum import Enum
from typing import TypedDict, Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class StatusDict(TypedDict):
    id: int
    value: str


class Status(Enum):
    queue = StatusDict(id=1, value="Queued")
    process = StatusDict(id=2, value="Processing")
    acc = StatusDict(id=3, value="Accepted")
    wans = StatusDict(id=4, value="Wrong Answer")
    tle = StatusDict(id=5, value="Time Limit Exceeded")
    mle = StatusDict(id=5, value="Memory Limit Exceeded")
    rf = StatusDict(id=6, value="Stack Overflow Error")
    comerr = StatusDict(id=7, value="Compilation Error")
    sigsegv = StatusDict(id=8, value="Runtime Error (SIGSEGV)")
    sigxfsz = StatusDict(id=9, value="Runtime Error (SIGXFSZ)")
    sigfpe = StatusDict(id=10, value="Runtime Error (SIGFPE)")
    sigabrt = StatusDict(id=11, value="Runtime Error (SIGABRT)")
    nzec = StatusDict(id=12, value="Runtime Error (NZEC)")
    other = StatusDict(id=13, value="Runtime Error (Other)")
    boxerr = StatusDict(id=14, value="Internal Error (boxerr)")
    exeerr = StatusDict(id=15, value="Exec Format Error (exeerr)")


class SubmissionLanguage(BaseModel):
    source_file: str
    compile_cmd: str
    run_cmd: str

    model_config = {"from_attributes": True}


class Submission(BaseModel):
    """Internal model consumed by IsolateJob."""

    id: int
    language: SubmissionLanguage
    source_code: str
    compile_output: Optional[str] = None
    stdin: Optional[str] = None
    expected_output: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    time: Optional[float] = None
    wall_time: Optional[float] = None
    memory: Optional[int] = None
    exit_code: Optional[int] = None
    exit_signal: Optional[int] = None
    message: Optional[str] = None
    status: Status = Status.queue
    cpu_time_limit: int
    cpu_extra_time: int
    wall_time_limit: int
    stack_limit: int
    memory_limit: int
    max_file_size: int
    max_processes_and_or_threads: int
    enable_per_process_and_thread_time_limit: bool
    enable_per_process_and_thread_memory_limit: bool
    created_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# API request schemas
# ---------------------------------------------------------------------------


class SubmissionCreate(BaseModel):
    """POST /submissions request body."""

    source_code: str
    language_id: int
    stdin: Optional[str] = None
    expected_output: Optional[str] = None
    cpu_time_limit: float = Field(default=5, ge=0.1, le=15)
    cpu_extra_time: float = Field(default=1, ge=0, le=5)
    wall_time_limit: float = Field(default=10, ge=0.5, le=30)
    memory_limit: int = Field(default=128000, ge=2048, le=512000, description="KB")
    stack_limit: int = Field(default=65536, ge=2048, le=131072, description="KB")
    max_file_size: int = Field(default=1024, ge=1, le=4096, description="KB")
    max_processes_and_or_threads: int = Field(default=60, ge=1, le=128)
    enable_per_process_and_thread_time_limit: bool = True
    enable_per_process_and_thread_memory_limit: bool = True


class SubmissionBatchCreate(BaseModel):
    """POST /submissions/batch request body."""

    submissions: list[SubmissionCreate] = Field(..., min_length=1, max_length=20)


# ---------------------------------------------------------------------------
# API response schemas
# ---------------------------------------------------------------------------


class SubmissionResponse(BaseModel):
    """GET /submissions/{token} response."""

    token: UUID
    source_code: str
    language_id: int
    stdin: Optional[str] = None
    expected_output: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    compile_output: Optional[str] = None
    message: Optional[str] = None
    status: str
    time: Optional[float] = None
    wall_time: Optional[float] = None
    memory: Optional[int] = None
    exit_code: Optional[int] = None
    exit_signal: Optional[int] = None
    cpu_time_limit: float
    cpu_extra_time: float
    wall_time_limit: float
    memory_limit: int
    stack_limit: int
    max_file_size: int
    max_processes_and_or_threads: int
    enable_per_process_and_thread_time_limit: bool
    enable_per_process_and_thread_memory_limit: bool
    created_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SubmissionBatchResponse(BaseModel):
    """GET /submissions/batch/{token} response."""

    token: UUID
    submissions: list[SubmissionResponse]

    model_config = {"from_attributes": True}
