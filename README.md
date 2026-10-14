# Students Database CRUD API

A Python backend for managing student records with Create, Read, Update and Delete
operations. Built with **FastAPI**, **SQLAlchemy** and **SQLite**, with an optional
**Ollama** endpoint that answers natural-language questions about the stored data.

Built for the EWB Edu Tech Pvt. Ltd. internship project assignment.

## Features

- Full CRUD for students, with data persisted in SQLite
- Input validation with Pydantic (email format, phone format, date of birth in the
  past, at least one contact: email or phone)
- Proper error handling: `404` for missing records, `409` for duplicate emails,
  `422` for invalid input
- Filtering by course, name and date of birth
- Automated tests with Pytest, each run on a separate temporary SQLite database
- Optional local AI (`POST /ai/ask`) grounded in records fetched by backend code

## Tech stack

Python 3.12, FastAPI, SQLAlchemy, SQLite, Pydantic, Uvicorn, Pytest, Ollama (optional)

## Project structure

```
students-crud/
├── app/
│   ├── main.py          # FastAPI app and router registration
│   ├── database.py      # SQLite engine, session, get_db dependency
│   ├── models.py        # SQLAlchemy Student model
│   ├── schemas.py       # Pydantic schemas and validation rules
│   ├── crud.py          # Database operations
│   ├── ai.py            # Record selection and Ollama client
│   ├── seed.py          # Loads dummy data
│   └── routers/
│       ├── students.py  # CRUD endpoints
│       └── ai.py        # AI question endpoint
├── tests/               # Pytest tests (temporary DB per test)
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.10 or newer
- Git
- (Optional, for the AI feature) [Ollama](https://ollama.com)

## Installation (Windows PowerShell)

```powershell
git clone https://github.com/<your-username>/students-crud.git
cd students-crud
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If activation is blocked, run once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Run the application

```powershell
python -m app.seed                       # optional: load 8 dummy students
python -m uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Interactive docs (Swagger): http://127.0.0.1:8000/docs

The SQLite file `students.db` is created automatically in the project folder.

## API endpoints

| Method    | Endpoint                 | Purpose                          |
|-----------|--------------------------|----------------------------------|
| POST      | `/students`              | Create a student (201)           |
| GET       | `/students`              | List / filter students           |
| GET       | `/students/{student_id}` | View a student (404 if missing)  |
| PUT/PATCH | `/students/{student_id}` | Update details (partial update)  |
| DELETE    | `/students/{student_id}` | Delete a student (204)           |
| POST      | `/ai/ask`                | Optional: ask about the data     |

List filters: `course`, `name`, `born_after` (YYYY-MM-DD), `skip`, `limit`.

### Student fields

Required: `name`, `date_of_birth`, and at least one of `email` / `phone`.
Optional: `course`, `address`, `enrollment_date`. `id` is generated automatically.

## Testing the API

### Option 1: Swagger UI

Open http://127.0.0.1:8000/docs, choose an endpoint, click **Try it out**, then **Execute**.

### Option 2: PowerShell

```powershell
# Create
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/students `
  -ContentType "application/json" `
  -Body '{"name":"Test Student","date_of_birth":"2005-01-15","email":"test@example.com","course":"BCA"}'

# List, filtered by course
Invoke-RestMethod "http://127.0.0.1:8000/students?course=BCA"

# Get one
Invoke-RestMethod http://127.0.0.1:8000/students/1

# Partial update
Invoke-RestMethod -Method Patch -Uri http://127.0.0.1:8000/students/1 `
  -ContentType "application/json" -Body '{"course":"B.Tech CSE"}'

# Delete
Invoke-RestMethod -Method Delete -Uri http://127.0.0.1:8000/students/1
```

### Run the automated tests

```powershell
python -m pytest -v
```

Tests use a separate temporary SQLite database, so `students.db` is never modified.

## Optional: AI questions with Ollama

1. Install Ollama and pull a small model:
```powershell
   ollama pull llama3.2:1b
```
2. Make sure Ollama is running, load the dummy data (`python -m app.seed`) and start the API.
3. Send a question to `POST /ai/ask`:
```powershell
   Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/ai/ask `
     -ContentType "application/json" `
     -Body '{"question":"List students born after 2005"}'
```

Example questions: "How many students are there?", "List students born after 2005",
"Who is enrolled in BCA?", "Tell me about Asha".

### How it stays grounded and safe

- The model **never runs SQL**. Backend code reads the question, selects records
  through the existing CRUD functions, and computes counts itself.
- Those records and facts are passed to the model as context; it only phrases the answer.
- The prompt tells the model to say so when the information is not in the context.
- Email and phone are **not** sent to the model.
- The response includes `facts` and `records_used` so every answer can be verified.
- If Ollama is not running, the endpoint returns `503` with a helpful message.

## Data and security notes

- All seed data is fake. Do not store real student information in this project.
- `students.db`, `.env` and the virtual environment are excluded by `.gitignore`.
- No passwords or secrets are used or committed.