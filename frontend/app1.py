# frontend/app1.py

import streamlit as st
import requests
import os
from dotenv import load_dotenv
# BACKEND_URL = os.getenv("BACKEND_URL")

BACKEND_URL = "https://techit-bnmit-resourcehub.onrender.com"  # Update this for deployment
# BACKEND_URL = "https://techit-bnmit-resourcehub.onrender.com"

st.set_page_config(page_title="TechIT ResourceHub", layout="wide")

st.title("📚 TechIT ResourceHub")
st.markdown("Search, sort, and filter all files and folders across GitHub and Google Drive.")
st.markdown("Using backend:", BACKEND_URL)


# 🔁 Sync Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Sync GitHub"):
        res = requests.post(f"{BACKEND_URL}/sync/github")
        if res.status_code == 200:
            st.success(res.json().get("message", "✅ GitHub sync completed."))
        else:
            st.error(f"❌ GitHub sync failed: {res.json().get('error', 'Unknown error')}")

with col2:
    if st.button("🔄 Sync Google Drive"):
        res = requests.post(f"{BACKEND_URL}/sync/drive")
        if res.status_code == 200:
            st.success(res.json().get("message", "✅ Google Drive sync completed."))
        else:
            st.error(f"❌ Drive sync failed: {res.json().get('error', 'Unknown error')}")

st.markdown("---")

# 🔍 Search Bar
query = st.text_input("🔎 Search", placeholder="Enter keyword (e.g., Regression, Semester4)")

# 🔽 Filters
col1, col2, col3, col4 = st.columns(4)
with col1:
    dept_filter = st.selectbox("Department", ["All", "CSE", "ISE", "ECE", "ME", "CIV", "AI/ML"])
with col2:
    sem_filter = st.selectbox("Semester", ["All"] + [f"Semester{i}" for i in range(1, 9)])
with col3:
    type_filter = st.selectbox("Type", ["All", "notes", "lab", "question-paper", "assignment", "misc", "folder"])
with col4:
    show_filter = st.selectbox("Show", ["Everything", "Files only", "Folders only"])

# 🔃 Sorting
col1, col2 = st.columns([2, 1])
with col1:
    sort_field = st.selectbox("Sort By", ["Date Added", "Title"])
with col2:
    sort_order = st.radio("Order", ["Newest First", "Oldest First"], horizontal=True)

# 🧠 Query Backend
params = {
    "q": query,
    "department": dept_filter,
    "semester": sem_filter,
    "type": type_filter,
    "show": show_filter,
    "sort_by": "date" if sort_field == "Date Added" else "title",
    "order": "desc" if sort_order == "Newest First" else "asc"
}

response = requests.get(f"{BACKEND_URL}/resources/search", params=params)
results = response.json()

# 📋 Results
st.markdown("---")
if query:
    st.subheader(f"🔍 Results for: _{query}_ ({len(results)} found)")
elif results:
    st.subheader(f"📁 Showing {len(results)} items")

if results:
    for r in results:
        with st.container():
            st.markdown(f"### {'📁' if r['type'] == 'folder' else '📄'} [{r['title']}]({r['link']})")
            cols = st.columns(2)
            with cols[0]:
                st.markdown(f"- **Department:** {r['department']}")
                st.markdown(f"- **Semester:** {r['semester']}")
                st.markdown(f"- **Subject:** {r['subject']}")
            with cols[1]:
                st.markdown(f"- **Type:** `{r['type']}`")
                st.markdown(f"- **Source:** {r['source']}")
                st.markdown(f"- **Added:** {r['last_updated'].split('T')[0]}")
            st.markdown("---")
else:
    st.info("No resources found. Try changing the filters or search term.")
