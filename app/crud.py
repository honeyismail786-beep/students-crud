from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Student
from app.schemas import StudentCreate, StudentUpdate


class DuplicateEmailError(Exception):
    """Raised when an email is already used by another student."""


def get_student(db: Session, student_id: int) -> Optional[Student]:
    return db.get(Student, student_id)


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    return db.scalar(select(Student).where(Student.email == email))


def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    course: Optional[str] = None,
    name: Optional[str] = None,
    born_after: Optional[date] = None,
) -> list[Student]:
    query = select(Student)
    if course:
        query = query.where(Student.course.ilike(course))
    if name:
        query = query.where(Student.name.ilike(f"%{name}%"))
    if born_after:
        query = query.where(Student.date_of_birth > born_after)
    query = query.order_by(Student.id).offset(skip).limit(limit)
    return list(db.scalars(query).all())


def create_student(db: Session, data: StudentCreate) -> Student:
    if data.email and get_student_by_email(db, data.email):
        raise DuplicateEmailError(data.email)
    student = Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def update_student(db: Session, student: Student, data: StudentUpdate) -> Student:
    changes = data.model_dump(exclude_unset=True)

    new_email = changes.get("email", student.email)
    new_phone = changes.get("phone", student.phone)
    if not new_email and not new_phone:
        raise ValueError("a student must keep at least one contact: email or phone")

    if new_email and new_email != student.email:
        if get_student_by_email(db, new_email):
            raise DuplicateEmailError(new_email)

    for field, value in changes.items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student: Student) -> None:
    db.delete(student)
    db.commit()