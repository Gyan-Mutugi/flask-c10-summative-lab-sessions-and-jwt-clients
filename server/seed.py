
from app import app
from models import db, User, Workout


with app.app_context():
    Workout.query.delete()
    User.query.delete()

    user1 = User(username="john")
    user1.set_password("password123")

    user2 = User(username="mary")
    user2.set_password("password123")

    db.session.add_all([user1, user2])
    db.session.commit()

    workouts = [
        Workout(
            exercise_name="Running",
            duration=30,
            calories_burned=250,
            workout_date="2026-11-01",
            user_id=user1.id
        ),
        Workout(
            exercise_name="Cycling",
            duration=45,
            calories_burned=350,
            workout_date="2026-11-02",
            user_id=user1.id
        ),
        Workout(
            exercise_name="Swimming",
            duration=60,
            calories_burned=400,
            workout_date="2026-11-03",
            user_id=user2.id
        ),
        Workout(
            exercise_name="Walking",
            duration=25,
            calories_burned=120,
            workout_date="2026-11-03",
            user_id=user2.id
        )
    ]

    db.session.add_all(workouts)
    db.session.commit()

    print("Database seeded successfully!")
