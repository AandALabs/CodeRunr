import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Uuid
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db.base import Base


class SubmissionBatch(Base):
    __tablename__ = "submission_batches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(Uuid, unique=True, nullable=False, default=uuid.uuid4, index=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(datetime.UTC)
    )

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

    submissions = relationship("Submission", back_populates="batch", lazy="selectin")
