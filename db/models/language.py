from sqlalchemy import Column, Integer, String, Boolean

from db.base import Base


class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    compile_cmd = Column(String, nullable=True)
    run_cmd = Column(String, nullable=False)
    source_file = Column(String, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
