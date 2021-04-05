from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate


class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    def get(self, db: Session, id: int) -> Optional[Student]:
        return db.query(Student).filter(Student.user_id == id).first()

    def create(self, db: Session, *, obj_in: StudentCreate) -> Student:
        db_obj = Student(user_id=obj_in.user_id, term_id=obj_in.term_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Student, obj_in: Union[StudentUpdate, Dict[str, Any]]) -> Student:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def remove(self, db: Session, *, id: int) -> Student:
        obj = db.query(Student).filter(Student.user_id == id).first()
        db.delete(obj)
        db.commit()
        return obj


student = CRUDStudent(Student)
