
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from config import Config
from models import db, bcrypt, User, Workout

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)


@app.route("/")
def home():
    return jsonify({"message": "Workout Tracker API is running"}), 200


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")
    password_confirmation = data.get("password_confirmation", "")

    errors = []

    if not username:
        errors.append("Username is required.")

    if not password:
        errors.append("Password is required.")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters long.")

    if password != password_confirmation:
        errors.append("Passwords do not match.")

    if username and User.query.filter_by(username=username).first():
        errors.append("Username already exists.")

    if errors:
        return jsonify({"errors": errors}), 422

    user = User(username=username)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": token,
        "user": user.to_dict()
    }), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"errors": ["Invalid username or password."]}), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": token,
        "user": user.to_dict()
    }), 200


@app.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if not user:
        return jsonify({"errors": ["User not found."]}), 404

    return jsonify(user.to_dict()), 200


@app.route("/workouts", methods=["GET"])
@jwt_required()
def get_workouts():
    user_id = int(get_jwt_identity())

    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        return jsonify({"errors": ["Page and per_page must be numbers."]}), 400

    if page < 1 or per_page < 1:
        return jsonify({"errors": ["Page and per_page must be positive numbers."]}), 400

    per_page = min(per_page, 100)

    pagination = Workout.query.filter_by(user_id=user_id).order_by(
        Workout.id.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "workouts": [workout.to_dict() for workout in pagination.items],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }), 200


@app.route("/workouts", methods=["POST"])
@jwt_required()
def create_workout():
    data = request.get_json() or {}

    exercise_name = data.get("exercise_name")
    duration = data.get("duration")
    calories_burned = data.get("calories_burned")
    workout_date = data.get("workout_date")

    errors = []

    if not isinstance(exercise_name, str) or not exercise_name.strip():
        errors.append("Exercise name is required.")

    if isinstance(duration, bool) or not isinstance(duration, int) or duration <= 0:
        errors.append("Duration must be a positive integer.")

    if isinstance(calories_burned, bool) or not isinstance(calories_burned, int) or calories_burned < 0:
        errors.append("Calories burned must be a non-negative integer.")

    if not isinstance(workout_date, str) or not workout_date.strip():
        errors.append("Workout date is required.")

    if errors:
        return jsonify({"errors": errors}), 422

    workout = Workout(
        exercise_name=exercise_name.strip(),
        duration=duration,
        calories_burned=calories_burned,
        workout_date=workout_date.strip(),
        user_id=int(get_jwt_identity())
    )

    db.session.add(workout)
    db.session.commit()

    return jsonify(workout.to_dict()), 201


@app.route("/workouts/<int:workout_id>", methods=["PATCH"])
@jwt_required()
def update_workout(workout_id):
    user_id = int(get_jwt_identity())

    workout = Workout.query.filter_by(
        id=workout_id,
        user_id=user_id
    ).first()

    if not workout:
        return jsonify({"errors": ["Workout not found."]}), 404

    data = request.get_json() or {}
    errors = []

    if "exercise_name" in data:
        if not isinstance(data["exercise_name"], str) or not data["exercise_name"].strip():
            errors.append("Exercise name must not be empty.")
        else:
            workout.exercise_name = data["exercise_name"].strip()

    if "duration" in data:
        value = data["duration"]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            errors.append("Duration must be a positive integer.")
        else:
            workout.duration = value

    if "calories_burned" in data:
        value = data["calories_burned"]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errors.append("Calories burned must be a non-negative integer.")
        else:
            workout.calories_burned = value

    if "workout_date" in data:
        value = data["workout_date"]
        if not isinstance(value, str) or not value.strip():
            errors.append("Workout date must not be empty.")
        else:
            workout.workout_date = value.strip()

    if errors:
        db.session.rollback()
        return jsonify({"errors": errors}), 422

    db.session.commit()

    return jsonify(workout.to_dict()), 200


@app.route("/workouts/<int:workout_id>", methods=["DELETE"])
@jwt_required()
def delete_workout(workout_id):
    user_id = int(get_jwt_identity())

    workout = Workout.query.filter_by(
        id=workout_id,
        user_id=user_id
    ).first()

    if not workout:
        return jsonify({"errors": ["Workout not found."]}), 404

    db.session.delete(workout)
    db.session.commit()

    return jsonify({"message": "Workout deleted successfully."}), 200


if __name__ == "__main__":
    app.run(port=5555, debug=True)
