from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint

from app.db.base_class import Base
from app.models import School


class Year(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    school_id = Column(
        Integer, ForeignKey(f'{School.__table__.name}.id', ondelete='CASCADE'), index=True, nullable=False
    )
    start_year = Column(Integer, index=True, nullable=False)
    end_year = Column(Integer, index=True, nullable=False)
    is_active = Column(Boolean, default=True)

    __table_args__ = (UniqueConstraint("name", "school_id", "start_year", "end_year"),)
