from app import crud, models  # noqa: F401
from app.database import Base, SessionLocal, engine
from app.schemas import StudentCreate

# All data below is fake. Do not add real students' details.
DUMMY_STUDENTS = [
    {"name": "Asha Rao", "date_of_birth": "2005-04-12", "email": "asha.rao@example.com",
     "phone": "9876543210", "course": "B.Tech CSE", "address": "Hyderabad",
     "enrollment_date": "2023-08-01"},
    {"name": "Ravi Kumar", "date_of_birth": "2003-01-20", "email": "ravi.kumar@example.com",
     "course": "BCA", "address": "Warangal", "enrollment_date": "2021-07-15"},
    {"name": "Sneha Reddy", "date_of_birth": "2006-09-30", "email": "sneha.reddy@example.com",
     "phone": "9123456780", "course": "B.Tech CSE", "enrollment_date": "2024-08-01"},
    {"name": "Arjun Verma", "date_of_birth": "2004-11-05", "email": "arjun.verma@example.com",
     "course": "B.Sc Data Science", "address": "Karimnagar", "enrollment_date": "2022-08-10"},
    {"name": "Meera Nair", "date_of_birth": "2007-02-14", "email": "meera.nair@example.com",
     "phone": "9988776655", "course": "B.Tech ECE", "enrollment_date": "2025-08-01"},
    {"name": "Kiran Patel", "date_of_birth": "2002-06-18", "email": "kiran.patel@example.com",
     "course": "MBA", "address": "Secunderabad", "enrollment_date": "2022-06-20"},
    {"name": "Divya Sharma", "date_of_birth": "2005-12-25", "phone": "9090909090",
     "course": "BCA", "enrollment_date": "2023-07-20"},
    {"name": "Imran Khan", "date_of_birth": "2006-03-08", "email": "imran.khan@example.com",
     "course": "B.Tech CSE", "address": "Nizamabad", "enrollment_date": "2024-08-01"},
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    added = skipped = 0
    try:
        for row in DUMMY_STUDENTS:
            email = row.get("email")
            if email and crud.get_student_by_email(db, email):
                skipped += 1
                continue
            crud.create_student(db, StudentCreate(**row))
            added += 1
    finally:
        db.close()
    print(f"Seed complete: {added} added, {skipped} already existed.")


if __name__ == "__main__":
    seed()