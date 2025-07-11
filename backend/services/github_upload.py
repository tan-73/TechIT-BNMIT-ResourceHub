# backend/services/github_upload.py

import os
import base64
import requests
from io import BytesIO
from config import Config

GITHUB_TOKEN = Config.GITHUB_TOKEN
GITHUB_REPO = "TechIT-Community/TechIT-BNMIT-ResourceHub"
GITHUB_API = "https://api.github.com"

def create_github_pr(file_bytes: BytesIO, filename: str, department: str, semester: str, subject: str, type_label: str):
    if not GITHUB_TOKEN:
        raise Exception("GitHub token not set in environment")

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    # Step 1: Get default branch (usually 'main')
    repo_url = f"{GITHUB_API}/repos/{GITHUB_REPO}"
    repo_data = requests.get(repo_url, headers=headers).json()
    default_branch = repo_data.get("default_branch", "main")

    # Step 2: Create a new branch from default
    ref_url = f"{GITHUB_API}/repos/{GITHUB_REPO}/git/ref/heads/{default_branch}"
    base_sha = requests.get(ref_url, headers=headers).json()["object"]["sha"]
    branch_name = f"upload-{filename.replace('.', '-')}-{os.urandom(4).hex()}"
    create_ref_url = f"{GITHUB_API}/repos/{GITHUB_REPO}/git/refs"
    ref_response = requests.post(create_ref_url, headers=headers, json={
        "ref": f"refs/heads/{branch_name}",
        "sha": base_sha
    })
    if ref_response.status_code not in (200, 201):
        raise Exception(f"Failed to create branch: {ref_response.text}")

    # Step 3: Commit the file to the new branch
    file_bytes.seek(0)
    content = base64.b64encode(file_bytes.read()).decode("utf-8")
    github_path = f"{department}/{semester}/{subject}/{type_label}/{filename}"
    commit_url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{github_path}"
    commit_response = requests.put(commit_url, headers=headers, json={
        "message": f"Add {filename} via contribution upload",
        "content": content,
        "branch": branch_name
    })
    if commit_response.status_code not in (200, 201):
        raise Exception(f"GitHub commit failed: {commit_response.text}")

    # Step 4: Create a pull request
    pr_url = f"{GITHUB_API}/repos/{GITHUB_REPO}/pulls"
    pr_response = requests.post(pr_url, headers=headers, json={
        "title": f"Add {filename} to {subject}",
        "head": branch_name,
        "base": default_branch,
        "body": f"Uploaded via backend API to {department}/{semester}/{subject}"
    })
    if pr_response.status_code not in (200, 201):
        raise Exception(f"GitHub PR failed: {pr_response.text}")

    return pr_response.json()["html_url"]
