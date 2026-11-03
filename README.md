# Workout Tracker API

## About the Project

This is a simple Workout Tracker API built with Flask. Users can create accounts, log in, and keep track of their workouts. Each user has their own workouts and can only manage their own records.

## Technologies Used

- Python and Flask
- Flask-SQLAlchemy
- Flask-Bcrypt
- Flask-JWT-Extended
- SQLite
- React

## Getting Started

### 1. Go to the server folder

```bash
cd server
```

### 2. Activate the virtual environment

```bash
pipenv shell
```

### 3. Set up the database

```bash
flask --app app db upgrade
python seed.py
```

### 4. Start the server

```bash
python app.py
```

The API runs at `http://127.0.0.1:5555`.

## Test