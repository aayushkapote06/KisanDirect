"""
database.py - Database Configuration

This file sets up the connection between our Python code and the SQLite database.

SQLite is a simple database that stores everything in a single file on your computer.
No need to install a separate database server - perfect for development!

Key concepts:
- "Engine": The connection to the database file
- "Session": A conversation with the database (open it, do work, close it)
- "Base": A parent class that all our database tables will inherit from
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# This is the path to our database file. It will be created automatically.
# "sqlite:///./marketplace.db" means: use SQLite, store the file as "marketplace.db"
# in the same folder where we run the server.
DATABASE_URL = "sqlite:///./marketplace.db"

# Create the engine (the connection to our database)
# check_same_thread=False is needed for SQLite to work with FastAPI
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a session factory - we'll use this to create database sessions
# autocommit=False means we control when changes are saved
# autoflush=False means we control when data is sent to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our database models (tables)
Base = declarative_base()


def get_db():
    """
    This function creates a database session for each API request.
    
    How it works:
    1. Creates a new session (opens a conversation with the database)
    2. Gives it to the API endpoint to use
    3. Closes the session when the endpoint is done (even if an error occurs)
    
    The "yield" keyword makes this a "generator" - it pauses the function,
    gives the session to the caller, and resumes to close it when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
