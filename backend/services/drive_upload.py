import os
import json
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.file']
ROOT_FOLDER_ID = '1Le_C3BJGhWXzOJO8XJcM4DmGzJwWZcqc'  # Replace with your actual folder ID

def authenticate_drive():
    """
    Authenticates and returns a Google Drive service object using credentials from env.
    """
    creds = None

    # Load token.json if it exists (OAuth2 refresh tokens)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        # Parse credentials JSON string from env
        credentials_json_str = os.getenv("GOOGLE_CREDENTIALS_PATH")
        if not credentials_json_str:
            raise Exception("GOOGLE_CREDENTIALS_PATH environment variable is missing")

        try:
            credentials_dict = json.loads(credentials_json_str)
        except json.JSONDecodeError:
            raise Exception("Invalid JSON in GOOGLE_CREDENTIALS_PATH")

        flow = InstalledAppFlow.from_client_config(credentials_dict, SCOPES)
        creds = flow.run_local_server(port=0)

        # Save the token for reuse
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


def ensure_folder(service, name, parent_id):
    """
    Ensures a folder exists in Drive. Returns its ID.
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
    Uploads a file to Google Drive in the correct folder hierarchy.
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
