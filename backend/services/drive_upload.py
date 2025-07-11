# backend/services/drive_upload.py

import os
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from config import Config

SCOPES = ['https://www.googleapis.com/auth/drive.file']
ROOT_FOLDER_ID = '1Le_C3BJGhWXzOJO8XJcM4DmGzJwWZcqc'  # Replace with your actual folder ID


def authenticate_drive():
    """
    Authenticates and returns a Google Drive service object.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(Config.GOOGLE_CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)


def ensure_folder(service, name, parent_id):
    """
    Ensures that a folder with the given name exists under the specified parent.
    Returns the folder ID.
    """
    query = f"'{parent_id}' in parents and name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    result = service.files().list(q=query, fields="files(id)").execute()
    folders = result.get("files", [])
    if folders:
        return folders[0]["id"]

    metadata = {
        "name": name,
        "parents": [parent_id],
        "mimeType": "application/vnd.google-apps.folder"
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder.get("id")


def upload_to_drive(file_bytes: BytesIO, filename: str, department: str, semester: str, subject: str, type_label: str):
    """
    Uploads a file to the appropriate Google Drive folder structure.
    Returns the webViewLink of the uploaded file.
    """
    service = authenticate_drive()

    dep_id = ensure_folder(service, department, ROOT_FOLDER_ID)
    sem_id = ensure_folder(service, semester, dep_id)
    subj_id = ensure_folder(service, subject, sem_id)
    type_id = ensure_folder(service, type_label, subj_id)

    file_metadata = {
        "name": filename,
        "parents": [type_id]
    }
    media = MediaIoBaseUpload(file_bytes, mimetype="application/octet-stream")
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()

    return file.get("webViewLink")
