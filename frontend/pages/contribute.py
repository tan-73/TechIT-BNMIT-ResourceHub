# frontend/contribute.py

import streamlit as st
import requests
import os

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:5000")
BACKEND_URL = f"{BASE_URL}/contribute"
METADATA_API = f"{BASE_URL}/resources/metadata"


st.set_page_config(page_title="📤 Contribute to ResourceHub", layout="wide")

st.title("📤 Contribute to TechIT ResourceHub")
st.markdown("""
Welcome! Upload your academic resources here.

- **Code files** will be automatically sent to GitHub.
- **PDFs, DOCXs, JPGs** and other binaries will go to Google Drive.
- Please make sure to select correct metadata for each file.
---
""")

# 🔽 Set your backend endpoint here
# BACKEND_URL = "http://localhost:5000/contribute"
# METADATA_API = "http://localhost:5000/resources/metadata"

# 🔍 Fetch metadata from backend
try:
    response = requests.get(METADATA_API)
    metadata = response.json()
    departments = metadata.get("departments", [])
    semesters = metadata.get("semesters", [])
    subjects = metadata.get("subjects", [])
except Exception as e:
    st.error(f"Failed to fetch metadata: {str(e)}")
    departments = ["CSE", "ISE", "ECE"]
    semesters = ["1", "2", "3", "4", "5", "6", "7", "8"]
    subjects = []

# 📦 Upload Form
with st.form("upload_form"):
    uploaded_files = st.file_uploader(
        "Upload your files", accept_multiple_files=True,
        type=["pdf", "docx", "jpg", "jpeg", "png", "py", "c", "cpp", "java", "js", "ts", "html", "css"]
    )

    department = st.selectbox("Department", departments)
    semester = st.selectbox("Semester", semesters)

    subject_choice = st.selectbox("Subject", subjects + ["Other (Add new subject)"])
    if subject_choice == "Other (Add new subject)":
        subject = st.text_input("Enter new subject name")
    else:
        subject = subject_choice

    submitted = st.form_submit_button("🚀 Submit")

# 📤 Submission Logic
if submitted:
    if not uploaded_files:
        st.error("Please upload at least one file.")
        st.stop()
    if not subject:
        st.error("Please enter or select a subject.")
        st.stop()

    with st.spinner("Uploading your files..."):
        files_payload = []
        for file in uploaded_files:
            files_payload.append(("files", (file.name, file, file.type)))

        data = {
            "department": department,
            "semester": semester,
            "subject": subject,
            "type": "contributions"
        }

        try:
            res = requests.post(BACKEND_URL, files=files_payload, data=data)
            if res.status_code == 200:
                responses = res.json()
                for r in responses:
                    if r["status"] == "success":
                        st.success(f"✅ {r['filename']} uploaded to {r['source'].capitalize()}: [View]({r['link']})")
                    elif r["status"] == "skipped":
                        st.warning(f"⚠️ {r['filename']} skipped: {r['reason']}")
                    else:
                        st.error(f"❌ {r['filename']} failed: {r.get('error', 'Unknown error')}")
            else:
                st.error(f"❌ Upload failed: {res.text}")
        except Exception as e:
            st.error(f"❌ Upload failed: {str(e)}")
