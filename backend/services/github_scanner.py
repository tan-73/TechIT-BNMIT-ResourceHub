# backend/services/github_scanner.py

import os
import requests
from config import Config
from db.database import SessionLocal
from db.models import Resource

GITHUB_API = "https://api.github.com"
GITHUB_REPO = "TechIT-Community/TechIT-BNMIT-ResourceHub"

def run_github_sync(start_path="CSE", branch="streamlit-local-backup"):
    token = Config.GITHUB_TOKEN
    if not token:
        print("[ERROR] GitHub token not configured")
        raise Exception("GitHub token not configured")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    session = SessionLocal()

    def recurse_contents(path, branch=branch):
        url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}?ref={branch}"
        print(f"[INFO] Fetching: {url}")
        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            print(f"[WARNING] GitHub API failed: {res.status_code} - {res.text}")
            return

        for item in res.json():
            if item["type"] == "file":
                print(f"[INFO] Found file: {item['path']}")
                parts = item["path"].split("/")

                # Handle standard path or fallback to "misc"
                if len(parts) >= 4:
                    department, semester, subject, file_type = parts[:4]
                elif len(parts) == 3:
                    department, semester, subject = parts
                    file_type = "misc"
                else:
                    print(f"[SKIP] Skipping due to short path: {item['path']}")
                    continue

                title = parts[-1]
                link = item["html_url"]

                # Check if already in DB
                existing = session.query(Resource).filter_by(link=link).first()
                if existing:
                    print(f"[SKIP] Already in DB: {title}")
                    continue

                resource = Resource(
                    title=title,
                    subject=subject,
                    semester=semester,
                    department=department,
                    type=file_type,
                    source="github",
                    link=link
                )
                print(f"[ADD] Adding: {title}")
                session.add(resource)

            elif item["type"] == "dir":
                recurse_contents(item["path"], branch)

    try:
        print("[START] GitHub sync started")
        recurse_contents(start_path)
        session.commit()
        print("[SUCCESS] All changes committed to DB.")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Commit failed: {e}")
    finally:
        session.close()
