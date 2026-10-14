from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai import (
    SYSTEM_PROMPT,
    OllamaUnavailableError,
    ask_ollama,
    build_user_prompt,
    select_records,
)
from app.database import get_db
from app.schemas import StudentOut

router = APIRouter(prefix="/ai", tags=["AI (Ollama)"])


class AskRequest(BaseModel):
    question: str = Field(
        ..., min_length=3, max_length=300, examples=["How many students are there?"]
    )


class AskResponse(BaseModel):
    question: str
    answer: str
    facts: list[str]
    records_used: list[StudentOut]


@router.post("/ask", response_model=AskResponse)
def ask_question(body: AskRequest, db: Session = Depends(get_db)):
    records, facts = select_records(db, body.question)
    prompt = build_user_prompt(body.question, records, facts)
    try:
        answer = ask_ollama(SYSTEM_PROMPT, prompt)
    except OllamaUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The local AI model is not available. Make sure Ollama is running "
                "and the model is installed: ollama pull llama3.2:1b"
            ),
        )
    return AskResponse(
        question=body.question, answer=answer, facts=facts, records_used=records
    )