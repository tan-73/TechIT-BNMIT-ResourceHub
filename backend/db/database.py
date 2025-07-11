# backend/db/database.py

from sqlalchemy import create_engine, distinct
from sqlalchemy.orm import sessionmaker
from config import Config
from db.base import Base  # ✅ Import from separate base module
from db.models import Resource  # ✅ Now safe to import

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_all_metadata():
    session = SessionLocal()
    try:
        departments = [row[0] for row in session.query(distinct(Resource.department)).all() if row[0]]
        semesters = [row[0] for row in session.query(distinct(Resource.semester)).all() if row[0]]
        subjects = [row[0] for row in session.query(distinct(Resource.subject)).all() if row[0]]
        return departments, semesters, subjects
    finally:
        session.close()
