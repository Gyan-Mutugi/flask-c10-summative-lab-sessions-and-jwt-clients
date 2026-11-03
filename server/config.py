import os

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///workouts.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY",
        "workout-tracker-secret-key-2026-secure"
    )