VALID = {
    "name": "Asha Rao",
    "date_of_birth": "2005-04-12",
    "email": "asha@example.com",
    "course": "B.Tech CSE",
}


def make_student(client, **overrides):
    response = client.post("/students", json={**VALID, **overrides})
    assert response.status_code == 201, response.text
    return response.json()


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Students API is running"}


# ---------- CREATE ----------
def test_create_student(client):
    data = make_student(client)
    assert data["id"] == 1
    assert data["name"] == "Asha Rao"
    assert data["email"] == "asha@example.com"


def test_create_duplicate_email_returns_409(client):
    make_student(client)
    response = client.post("/students", json=VALID)
    assert response.status_code == 409


def test_create_without_contact_returns_422(client):
    response = client.post(
        "/students", json={"name": "No Contact", "date_of_birth": "2004-01-01"}
    )
    assert response.status_code == 422


def test_create_with_bad_email_returns_422(client):
    response = client.post("/students", json={**VALID, "email": "not-an-email"})
    assert response.status_code == 422


def test_create_with_future_dob_returns_422(client):
    response = client.post("/students", json={**VALID, "date_of_birth": "2999-01-01"})
    assert response.status_code == 422


# ---------- READ ----------
def test_list_and_filters(client):
    make_student(client)
    make_student(
        client,
        name="Ravi Kumar",
        date_of_birth="2003-01-20",
        email=None,
        phone="9876543210",
        course="BCA",
    )

    assert len(client.get("/students").json()) == 2

    by_course = client.get("/students", params={"course": "bca"}).json()
    assert [s["name"] for s in by_course] == ["Ravi Kumar"]

    by_name = client.get("/students", params={"name": "asha"}).json()
    assert [s["name"] for s in by_name] == ["Asha Rao"]

    born_after = client.get("/students", params={"born_after": "2004-12-31"}).json()
    assert [s["name"] for s in born_after] == ["Asha Rao"]


def test_get_student(client):
    student = make_student(client)
    response = client.get(f"/students/{student['id']}")
    assert response.status_code == 200
    assert response.json()["email"] == "asha@example.com"


def test_get_missing_student_returns_404(client):
    response = client.get("/students/999")
    assert response.status_code == 404


# ---------- UPDATE ----------
def test_patch_student(client):
    student = make_student(client)
    response = client.patch(f"/students/{student['id']}", json={"course": "BCA"})
    assert response.status_code == 200
    assert response.json()["course"] == "BCA"
    assert response.json()["name"] == "Asha Rao"  # unchanged fields stay


def test_put_student(client):
    student = make_student(client)
    response = client.put(f"/students/{student['id']}", json={"address": "Hyderabad"})
    assert response.status_code == 200
    assert response.json()["address"] == "Hyderabad"


def test_update_missing_student_returns_404(client):
    response = client.patch("/students/999", json={"course": "BCA"})
    assert response.status_code == 404


def test_update_to_duplicate_email_returns_409(client):
    make_student(client)
    other = make_student(client, name="Ravi Kumar", email="ravi@example.com")
    response = client.patch(
        f"/students/{other['id']}", json={"email": "asha@example.com"}
    )
    assert response.status_code == 409


def test_cannot_remove_only_contact(client):
    student = make_student(client)  # has email only
    response = client.patch(f"/students/{student['id']}", json={"email": None})
    assert response.status_code == 422


# ---------- DELETE ----------
def test_delete_student(client):
    student = make_student(client)
    response = client.delete(f"/students/{student['id']}")
    assert response.status_code == 204
    assert client.get(f"/students/{student['id']}").status_code == 404


def test_delete_missing_student_returns_404(client):
    response = client.delete("/students/999")
    assert response.status_code == 404