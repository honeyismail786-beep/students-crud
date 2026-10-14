import re

import httpx
from sqlalchemy.orm import Session

from app import crud
from app.models import Student

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2:1b"
OLLAMA_TIMEOUT = 120  # seconds; small models on CPU can be slow
MAX_RECORDS_IN_PROMPT = 50

SYSTEM_PROMPT = (
    "You are an assistant for a student database. "
    "Answer ONLY using the FACTS and RECORDS provided. "
    "The numbers in FACTS are exact; use them as they are. "
    "If the answer is not in the FACTS or RECORDS, say you do not have that information. "
    "Never invent students, dates or numbers. Keep the answer short and clear."
)


class OllamaUnavailableError(Exception):
    """Raised when Ollama is not running or the model call fails."""


def select_records(db: Session, question: str) -> tuple[list[Student], list[str]]:
    """Pick the relevant records and compute facts. Pure backend logic, no AI."""
    q = question.lower()
    everyone = crud.get_students(db, limit=500)
    facts = [f"Total students in database: {len(everyone)}"]
    selected = everyone

    # "born after 2005", "born before 2004", "born in 2003"
    match = re.search(r"born\s+(after|before|in)\s+(\d{4})", q)
    if match:
        word, year = match.group(1), int(match.group(2))
        if word == "after":
            selected = [s for s in selected if s.date_of_birth.year > year]
        elif word == "before":
            selected = [s for s in selected if s.date_of_birth.year < year]
        else:
            selected = [s for s in selected if s.date_of_birth.year == year]
        facts.append(f"Students born {word} {year}: {len(selected)}")

    # a course name mentioned in the question, e.g. "BCA" or "B.Tech CSE"
    courses = {s.course for s in everyone if s.course}
    mentioned = [c for c in courses if c.lower() in q]
    if mentioned:
        selected = [s for s in selected if s.course in mentioned]
        facts.append(f"Students in {', '.join(sorted(mentioned))}: {len(selected)}")

    # a student's full or first name mentioned in the question
    by_name = [
        s
        for s in selected
        if re.search(rf"\b{re.escape(s.name.lower())}\b", q)
        or re.search(rf"\b{re.escape(s.name.split()[0].lower())}\b", q)
    ]
    if by_name:
        selected = by_name

    facts.append(f"Matching students: {len(selected)}")
    return selected[:MAX_RECORDS_IN_PROMPT], facts


def _format_record(s: Student) -> str:
    # Email and phone are deliberately NOT sent to the model.
    return (
        f"id={s.id}; name={s.name}; date_of_birth={s.date_of_birth}; "
        f"course={s.course or 'N/A'}; address={s.address or 'N/A'}; "
        f"enrollment_date={s.enrollment_date or 'N/A'}"
    )


def build_user_prompt(question: str, records: list[Student], facts: list[str]) -> str:
    facts_text = "\n".join(f"- {f}" for f in facts)
    records_text = "\n".join(_format_record(s) for s in records) or "(no matching records)"
    return f"FACTS:\n{facts_text}\n\nRECORDS:\n{records_text}\n\nQUESTION: {question}"


def ask_ollama(system_prompt: str, user_prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "options": {"temperature": 0},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    try:
        response = httpx.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise OllamaUnavailableError(str(exc)) from exc
    return response.json()["message"]["content"].strip()