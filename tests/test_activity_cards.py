from pathlib import Path

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_activity_cards_render_participants_list():
    script = Path("src/static/app.js").read_text()

    assert "Participants" in script
    assert "participants-list" in script
    assert "delete-participant" in script
    assert "<ul" in script


def test_unregister_participant_from_activity():
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    client.post(f"/activities/{activity}/signup?email={email}")

    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    assert response.status_code == 200
    assert email not in response.json()["participants"]
