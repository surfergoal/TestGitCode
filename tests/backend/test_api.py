from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    """Return a TestClient with a clean in-memory activity store for each test."""
    original_activities = deepcopy(activities)

    try:
        activities.clear()
        activities.update(deepcopy(original_activities))
        with TestClient(app) as test_client:
            yield test_client
    finally:
        activities.clear()
        activities.update(deepcopy(original_activities))


def test_get_activities_returns_activity_catalog(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity in payload
    assert payload[expected_activity]["description"]
    assert payload[expected_activity]["participants"]


def test_signup_for_activity_success(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicate_email(client):
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_unknown_activity_returns_404(client):
    # Arrange
    email = "student@mergington.edu"
    activity_name = "Unknown Activity"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_from_activity_success(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    activities[activity_name]["participants"].append(email)
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in response.json()["participants"]
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_from_activity_rejects_missing_email(client):
    # Arrange
    email = "ghost@mergington.edu"
    activity_name = "Chess Club"
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
