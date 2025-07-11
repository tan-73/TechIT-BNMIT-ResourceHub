# backend/services/github_scanner.py

import os
import requests
from config import Config
from db.database import SessionLocal
from db.models import Resource

GITHUB_API = "https://api.github.com"
GITHUB_REPO = "TechIT-Community/TechIT-BNMIT-ResourceHub"

def run_github_sync():
    token = Config.GITHUB_TOKEN
    if not token:
        raise Exception("GitHub token not configured")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    session = SessionLocal()

    def recurse_contents(path, branch="main"):
        url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}?ref={branch}"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return

        for item in res.json():
            if item["type"] == "file":
                parts = item["path"].split("/")
                if len(parts) < 4:
                    continue
                department, semester, subject, file_type = parts[:4]
                title = parts[-1]
                link = item["html_url"]

                # Check for duplicates
                existing = session.query(Resource).filter_by(link=link).first()
                if existing:
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
                session.add(resource)
            elif item["type"] == "dir":
                recurse_contents(item["path"], branch)

    recurse_contents("")
    session.commit()
    session.close()
