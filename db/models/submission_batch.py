import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, Uuid
from sqlalchemy.orm import relationship

from db.base import Base


class SubmissionBatch(Base):
    __tablename__ = "submission_batches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(Uuid, unique=True, nullable=False, default=uuid.uuid4, index=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    submissions = relationship("Submission", back_populates="batch", lazy="selectin")
