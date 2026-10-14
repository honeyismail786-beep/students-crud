from app.ai import OllamaUnavailableError
from app.routers import ai as ai_router


def add(client, name, dob, email, course="BCA"):
    response = client.post(
        "/students",
        json={"name": name, "date_of_birth": dob, "email": email, "course": course},
    )
    assert response.status_code == 201, response.text


def test_ask_passes_computed_facts_and_records(client, monkeypatch):
    add(client, "Asha Rao", "2005-04-12", "asha@example.com")
    add(client, "Meera Nair", "2007-02-14", "meera@example.com")
    captured = {}

    def fake_ollama(system_prompt, user_prompt):
        captured["prompt"] = user_prompt
        return "stub answer"

    monkeypatch.setattr(ai_router, "ask_ollama", fake_ollama)

    response = client.post("/ai/ask", json={"question": "List students born after 2005"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "stub answer"
    assert [s["name"] for s in body["records_used"]] == ["Meera Nair"]
    assert "Total students in database: 2" in captured["prompt"]
    assert "Students born after 2005: 1" in captured["prompt"]
    # contact details must never reach the model
    assert "meera@example.com" not in captured["prompt"]


def test_ask_returns_503_when_ollama_is_down(client, monkeypatch):
    def broken(system_prompt, user_prompt):
        raise OllamaUnavailableError("connection refused")

    monkeypatch.setattr(ai_router, "ask_ollama", broken)
    response = client.post("/ai/ask", json={"question": "How many students are there?"})
    assert response.status_code == 503


def test_ask_rejects_too_short_question(client):
    response = client.post("/ai/ask", json={"question": "hi"})
    assert response.status_code == 422