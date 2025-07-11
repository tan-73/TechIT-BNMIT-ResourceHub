# backend/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/demodb")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

    # ✅ Add these two:
    GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    GOOGLE_DRIVE_ROOT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID")
