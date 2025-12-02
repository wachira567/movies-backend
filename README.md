# Movies Backend API

A FastAPI-based backend application for managing movie genres and catalogues using SQLAlchemy ORM and Alembic for database migrations.

## Overview

This project demonstrates how to build a REST API with:

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **Alembic**: Database migration tool
- **SQLite**: Database (easily switchable to PostgreSQL for production)

## Project Structure

```
movies-backend/
├── .gitignore          # Ignores virtual environment
├── Pipfile            # Dependency management
├── Pipfile.lock       # Locked dependency versions
├── alembic.ini        # Alembic migration configuration
├── app.py             # Main FastAPI application
├── models.py          # Database models and session management
├── movies.db          # SQLite database (created automatically)
├── README.md          # This file
└── migrations/        # Database migration files
    ├── env.py
    ├── README
    ├── script.py.mako
    └── versions/      # Individual migration files
```

## Step-by-Step Setup Guide

### 1. Initialize Project and Dependencies

Create a new directory for your project and navigate to it:

```bash
mkdir my-backend-project
cd my-backend-project
```

Initialize Pipenv and install dependencies:

```bash
pipenv install sqlalchemy alembic "fastapi[standard]"
```

Activate the virtual environment:

```bash
pipenv shell
```

### 2. Set Up Database Migrations

Initialize Alembic (run this only once):

```bash
alembic init migrations
```

Update `alembic.ini` file - find line 66 and change it to:

```ini
sqlalchemy.url = sqlite:///your_database.db
```

Replace `your_database.db` with your desired database name.

### 3. Create Core Files

Create the main application files:

```bash
touch models.py app.py
```

### 4. Configure Migrations Environment

Edit `migrations/env.py` and add these lines after the existing imports (around line 21):

```python
from models import Base
target_metadata = Base.metadata
```

This tells Alembic where to find your database models.

### 5. Define Database Models

Create `models.py` with the following content:

```python
# Import required packages
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Create database engine - this handles SQL conversion
# echo=True shows SQL queries in console (useful for debugging)
engine = create_engine("sqlite:///your_database.db", echo=True)

# Create session factory - manages database connections
Session = sessionmaker(bind=engine)

# Dependency function for FastAPI - provides database sessions
def get_db():
    session = Session()
    try:
        # Yield session to FastAPI endpoint
        yield session
    finally:
        # Always close connection after use
        session.close()

# Base class for all database models
Base = declarative_base()

# Genre model - represents movie categories
class Genre(Base):
    __tablename__ = "genre"  # Database table name

    # Table columns
    id = Column(Integer(), primary_key=True)  # Auto-incrementing ID
    name = Column(Text(), nullable=False, unique=True)  # Genre name, required and unique
    created_at = Column(DateTime, default=datetime.now())  # Auto-set timestamp

# Catalogue model - represents movies
class Catalogue(Base):
    __tablename__ = "catalogues"

    id = Column(Integer(), primary_key=True)
    name = Column(Text(), nullable=False)  # Movie title
    year = Column(Integer(), nullable=False)  # Release year
    description = Column(Text(), nullable=False)  # Movie description
    genre_id = Column(Integer())  # References genre.id (foreign key)
    like_count = Column(Integer(), nullable=False, default=0)  # Number of likes
    duration = Column(Integer(), nullable=False)  # Duration in minutes
    created_at = Column(DateTime, default=datetime.now())
```

**Key Concepts Explained:**

- **Engine**: The SQLAlchemy engine converts Python code to SQL and executes it
- **Session**: A temporary connection to the database for performing operations
- **Base**: Parent class that all models inherit from - provides ORM functionality
- **Column**: Defines database table columns with types and constraints
- **nullable=False**: Field must have a value (cannot be NULL)
- **unique=True**: Values must be unique in the table
- **primary_key=True**: Unique identifier for each record
- **default=...**: Auto-set value if none provided

### 6. Create FastAPI Application

Create `app.py` with the following content:

```python
# Import FastAPI and related tools
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models import get_db, Genre, Catalogue

# Create FastAPI application instance
app = FastAPI()

# Add CORS middleware to allow requests from different domains
# This is needed when your frontend runs on a different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change for production)
    allow_methods=["*"]   # Allow all HTTP methods
)

# Root endpoint - test that API is working
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Pydantic schema for genre creation requests
# This validates incoming JSON data
class GenreSchema(BaseModel):
    name: str

# CREATE genre endpoint
@app.post("/genre")
def create_genre(genre: GenreSchema, session=Depends(get_db)):
    # Check if genre already exists
    existing = session.query(Genre).filter(Genre.name == genre.name).first()

    if existing is None:
        # Create new genre instance
        new_genre = Genre(name=genre.name)
        # Add to session (staging for database)
        session.add(new_genre)
        # Commit changes to database
        session.commit()
        return {"message": "Genre created successfully"}
    else:
        return {"message": "Genre already exists"}

# READ all genres endpoint
@app.get("/genre")
def get_genres(session=Depends(get_db)):
    # Query all genres from database
    genres = session.query(Genre).all()
    return genres

# Placeholder endpoints (not fully implemented)
@app.get("/genre/{genre_id}")
def get_genre(genre_id: int):
    return {"id": genre_id}

@app.patch("/genre/{genre_id}")
def update_genre(genre_id: int):
    return {"message": "Not implemented"}

@app.delete("/genre/{genre_id}")
def delete_genre(genre_id: int):
    return {"message": "Not implemented"}

# Pydantic schema for catalogue creation
class CatalogueSchema(BaseModel):
    name: str
    description: str
    year: int
    duration: int
    genre_id: int

# CREATE catalogue (movie) endpoint
@app.post("/catalogue")
def create_catalogue(catalogue: CatalogueSchema, session=Depends(get_db)):
    # Create new catalogue instance with request data
    new_catalogue = Catalogue(
        name=catalogue.name,
        description=catalogue.description,
        year=catalogue.year,
        duration=catalogue.duration,
        genre_id=catalogue.genre_id
    )
    # Stage and commit to database
    session.add(new_catalogue)
    session.commit()

    return {"message": "Movie added successfully"}

# READ all catalogues endpoint
@app.get("/catalogue")
def get_catalogues(session=Depends(get_db)):
    # Query all movies from database
    catalogues = session.query(Catalogue).all()
    return catalogues
```

**Key Concepts Explained:**

- **FastAPI()**: Creates the web application instance
- **@app.get/post/etc**: Decorators that define API endpoints
- **Depends(get_db)**: Dependency injection - automatically provides database session
- **Pydantic BaseModel**: Validates request/response data structure
- **session.add()**: Stages object for database insertion
- **session.commit()**: Saves staged changes to database
- **session.query()**: Creates database queries

### 7. Run Database Migrations

Generate and apply your first migration:

```bash
# Generate migration based on your models
alembic revision --autogenerate -m "init"

# Apply the migration to create database tables
alembic upgrade head
```

As you add more models or change existing ones, repeat this process:

```bash
alembic revision --autogenerate -m "describe your changes"
alembic upgrade head
```

### 8. Run the Application

Start the development server:

```bash
fastapi dev app.py
```

Visit:

- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Genres

- `POST /genre` - Create a new genre
- `GET /genre` - Get all genres

### Catalogues (Movies)

- `POST /catalogue` - Create a new movie
- `GET /catalogue` - Get all movies

## Database Schema

### genre table

- `id` (INTEGER, PRIMARY KEY) - Auto-incrementing ID
- `name` (TEXT, NOT NULL, UNIQUE) - Genre name
- `created_at` (DATETIME) - Creation timestamp

### catalogues table

- `id` (INTEGER, PRIMARY KEY) - Auto-incrementing ID
- `name` (TEXT, NOT NULL) - Movie title
- `year` (INTEGER, NOT NULL) - Release year
- `description` (TEXT, NOT NULL) - Movie description
- `genre_id` (INTEGER) - Foreign key to genre.id
- `like_count` (INTEGER, NOT NULL, DEFAULT 0) - Number of likes
- `duration` (INTEGER, NOT NULL) - Duration in minutes
- `created_at` (DATETIME) - Creation timestamp

## Key Concepts Summary

### SQLAlchemy ORM

- **Models**: Python classes that represent database tables
- **Engine**: Interface to the database
- **Session**: Temporary workspace for database operations
- **Query**: Object for building database queries

### FastAPI

- **Dependency Injection**: `Depends()` provides resources to endpoints
- **Pydantic**: Automatic request/response validation
- **CORS**: Cross-Origin Resource Sharing for web apps

### Alembic

- **Migration**: Version-controlled database schema changes
- **Revision**: Individual migration file
- **Upgrade**: Apply migrations forward
- **Downgrade**: Revert migrations backward

## Production Deployment

For production:

1. Change database URL in `alembic.ini` and `models.py`:

   ```python
   # For PostgreSQL
   engine = create_engine("postgresql://user:password@localhost/dbname")
   ```

2. Update CORS settings:

   ```python
   allow_origins=["https://yourfrontend.com"]
   ```

3. Use environment variables for sensitive data
4. Run with a production server like Gunicorn

## Troubleshooting

- **Migration errors**: Ensure `target_metadata = Base.metadata` is set in `env.py`
- **Connection errors**: Check database URL and permissions
- **Import errors**: Ensure all files are in the same directory
- **CORS errors**: Verify frontend is making requests to correct port

## Next Steps

To extend this project:

1. Implement full CRUD operations for genres and catalogues
2. Add relationships between models (foreign keys)
3. Add authentication and authorization
4. Implement search and filtering
5. Add pagination for large datasets
6. Write unit tests
7. Add input validation and error handling
