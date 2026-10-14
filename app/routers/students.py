from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import StudentCreate, StudentOut, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])


def get_student_or_404(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )
    return student


@router.post("", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_student(db, data)
    except crud.DuplicateEmailError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists",
        )


@router.get("", response_model=list[StudentOut])
def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    course: Optional[str] = Query(None, description="Exact course name (case-insensitive)"),
    name: Optional[str] = Query(None, description="Part of the student's name"),
    born_after: Optional[date] = Query(None, description="Date of birth after YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    return crud.get_students(
        db, skip=skip, limit=limit, course=course, name=name, born_after=born_after
    )


@router.get("/{student_id}", response_model=StudentOut)
def read_student(student=Depends(get_student_or_404)):
    return student


@router.api_route("/{student_id}", methods=["PUT", "PATCH"], response_model=StudentOut)
def update_student(
    data: StudentUpdate,
    student=Depends(get_student_or_404),
    db: Session = Depends(get_db),
):
    try:
        return crud.update_student(db, student, data)
    except crud.DuplicateEmailError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail=str(exc)
        )


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student=Depends(get_student_or_404), db: Session = Depends(get_db)):
    crud.delete_student(db, student)
    return Response(status_code=status.HTTP_204_NO_CONTENT)