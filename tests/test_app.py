import copy
import sys
from pathlib import Path
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from app import activities, app  # noqa: E402

client = TestClient(app)


def activity_path(name: str) -> str:
    return quote(name, safe="")


@pytest.fixture(autouse=True)
def reset_activities_state():
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


def test_get_activities_returns_data():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_adds_participant():
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{activity_path(activity)}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_rejects_duplicate():
    activity = "Chess Club"
    email = activities[activity]["participants"][0]

    response = client.post(
        f"/activities/{activity_path(activity)}/signup",
        params={"email": email},
    )

    assert response.status_code == 400


def test_remove_participant():
    activity = "Chess Club"
    email = activities[activity]["participants"][0]

    response = client.delete(
        f"/activities/{activity_path(activity)}/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_unknown_participant_returns_404():
    activity = "Chess Club"
    email = "missing@mergington.edu"

    response = client.delete(
        f"/activities/{activity_path(activity)}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
