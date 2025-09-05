# db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config import APP_DB_URL, DB_DIR

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR, exist_ok=True)

engine_app = create_engine(
    APP_DB_URL,
    connect_args={"check_same_thread": False},  # SQLite + multithreading
    pool_pre_ping=True,
    echo=False
)

SessionFactory = sessionmaker(bind=engine_app, autocommit=False, autoflush=False)
SessionApp = scoped_session(SessionFactory)

def get_session():
    """Safely get a database session for use within the Discord bot"""
    return SessionApp()

def init_db():
    """Create tables if they don't exist."""
    from .models import BaseApp  # import here to avoid circular imports
    BaseApp.metadata.create_all(bind=engine_app)
