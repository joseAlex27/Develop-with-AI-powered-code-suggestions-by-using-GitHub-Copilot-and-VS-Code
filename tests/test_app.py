import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def test_activities(monkeypatch):
    activities = {
        "Robotics": {
            "description": "Build and program robots",
            "schedule": "Mondays, 3:30 PM",
            "max_participants": 4,
            "participants": ["existing@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(test_activities):
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client, test_activities):
    # Arrange
    expected_activities = {
        "Robotics": {
            "description": "Build and program robots",
            "schedule": "Mondays, 3:30 PM",
            "max_participants": 4,
            "participants": ["existing@example.com"],
        }
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, test_activities):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post("/activities/Robotics/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@example.com for Robotics"}
    assert test_activities["Robotics"]["participants"] == [
        "existing@example.com",
        email,
    ]


def test_signup_rejects_duplicate_participant(client, test_activities):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.post("/activities/Robotics/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert test_activities["Robotics"]["participants"].count(email) == 1


def test_signup_returns_404_for_unknown_activity(client, test_activities):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client, test_activities):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete("/activities/Robotics/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Unregistered existing@example.com from Robotics"}
    assert test_activities["Robotics"]["participants"] == []


def test_unregister_returns_404_for_nonparticipant(client, test_activities):
    # Arrange
    email = "missing@example.com"

    # Act
    response = client.delete("/activities/Robotics/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }


def test_unregister_returns_404_for_unknown_activity(client, test_activities):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}