
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from app import app
from models import db, User, Workout


@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        JWT_SECRET_KEY="test-secret-key-that-is-at-least-32-characters"
    )

    with app.app_context():
        original_engine = db.engines[None]

        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )

        db.session.remove()
        db.engines[None] = engine
        db.create_all()

        try:
            user1 = User(username="john")
            user1.set_password("password123")

            user2 = User(username="mary")
            user2.set_password("password123")

            db.session.add_all([user1, user2])
            db.session.commit()

            workout1 = Workout(
                exercise_name="Running",
                duration=30,
                calories_burned=250,
                workout_date="2026-11-03",
                user_id=user1.id
            )

            workout2 = Workout(
                exercise_name="Swimming",
                duration=60,
                calories_burned=400,
                workout_date="2026-11-03",
                user_id=user2.id
            )

            db.session.add_all([workout1, workout2])
            db.session.commit()

            with app.test_client() as test_client:
                yield test_client

        finally:
            db.session.remove()
            db.drop_all()
            db.engines[None] = original_engine
            engine.dispose()


def get_token(client, username="john"):
    response = client.post("/login", json={
        "username": username,
        "password": "password123"
    })
    return response.get_json()["token"]


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_signup(client):
    response = client.post("/signup", json={
        "username": "newuser",
        "password": "password123",
        "password_confirmation": "password123"
    })

    assert response.status_code == 201
    assert "token" in response.get_json()


def test_login(client):
    response = client.post("/login", json={
        "username": "john",
        "password": "password123"
    })

    assert response.status_code == 200
    assert "token" in response.get_json()


def test_login_invalid_password(client):
    response = client.post("/login", json={
        "username": "john",
        "password": "wrongpassword"
    })

    assert response.status_code == 401


def test_me(client):
    token = get_token(client)

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.get_json()["username"] == "john"


def test_workouts_require_authentication(client):
    response = client.get("/workouts")
    assert response.status_code == 401


def test_get_workouts(client):
    token = get_token(client)

    response = client.get(
        "/workouts",
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["pagination"]["total"] == 1
    assert data["workouts"][0]["exercise_name"] == "Running"


def test_create_workout(client):
    token = get_token(client)

    response = client.post(
        "/workouts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "exercise_name": "Cycling",
            "duration": 45,
            "calories_burned": 350,
            "workout_date": "2026-11-03"
        }
    )

    assert response.status_code == 201
    assert response.get_json()["exercise_name"] == "Cycling"


def test_update_workout(client):
    token = get_token(client)

    response = client.patch(
        "/workouts/1",
        headers={"Authorization": f"Bearer {token}"},
        json={"exercise_name": "Jogging"}
    )

    assert response.status_code == 200
    assert response.get_json()["exercise_name"] == "Jogging"


def test_delete_workout(client):
    token = get_token(client)

    response = client.delete(
        "/workouts/1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_user_cannot_access_another_users_workout(client):
    token = get_token(client)

    response = client.delete(
        "/workouts/2",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404


def test_workout_pagination(client):
    token = get_token(client)

    response = client.get(
        "/workouts?page=1&per_page=1",
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["pagination"]["per_page"] == 1
    assert len(data["workouts"]) == 1
