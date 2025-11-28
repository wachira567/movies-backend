# Movies App

## Description
- This is the backend that powers our movies app, we use fastapi as the framework and sqlalchemy for db management
- At the beginning, we will use sqlite and if we host the application, we will switch to postgres

## Project setup

1. Install the required packages with `pipenv install sqlalchemy alembic "fastapi[standard]"`
2. Active the virtual environment with `pipenv shell`
3. Initialize migrations with the command `alembic init migrations`
