from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original = deepcopy(app_module.activities)
    yield
    app_module.activities = deepcopy(original)


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities_returns_all_activities(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_for_activity_success(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_fails_for_missing_activity(client):
    # Arrange

    # Act
    response = client.post("/activities/Nonexistent/signup", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_fails_if_student_already_signed_up(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_fails_if_activity_is_full(client):
    # Arrange
    activity_name = "Drama Club"
    app_module.activities[activity_name]["participants"] = [
        f"student{i}@mergington.edu" for i in range(app_module.activities[activity_name]["max_participants"])
    ]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": "late.student@mergington.edu"})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_from_activity_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "daniel@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_fails_for_missing_activity(client):
    # Arrange

    # Act
    response = client.delete("/activities/Nonexistent/signup", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_fails_for_student_not_signed_up(client):
    # Arrange

    # Act
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "not.registered@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
