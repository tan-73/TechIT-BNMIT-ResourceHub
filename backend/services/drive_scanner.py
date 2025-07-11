# backend/services/drive_scanner.py

import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from db.database import SessionLocal
from db.models import Resource
from config import Config

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
ROOT_FOLDER_ID = Config.GOOGLE_DRIVE_ROOT_FOLDER_ID

def authenticate_drive():
    creds = None
    try:
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(Config.GOOGLE_CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    except Exception as e:
        print("[!] Google Auth Error:", str(e))
        raise Exception("Google Drive authentication failed")
    
    return build('drive', 'v3', credentials=creds)

def run_drive_sync():
    try:
        service = authenticate_drive()
    except Exception as e:
        print("[!] Drive Sync Auth Failure:", str(e))
        raise

    session = SessionLocal()
    try:
        def recurse_folder(folder_id, path_parts):
            query = f"'{folder_id}' in parents and trashed = false"
            results = service.files().list(q=query, fields="files(id, name, mimeType, webViewLink)").execute()
            files = results.get('files', [])
            for file in files:
                if file['mimeType'] == 'application/vnd.google-apps.folder':
                    recurse_folder(file['id'], path_parts + [file['name']])
                else:
                    if len(path_parts) < 4:
                        continue
                    department, semester, subject, file_type = path_parts[:4]
                    title = file['name']
                    link = file['webViewLink']

                    existing = session.query(Resource).filter_by(link=link).first()
                    if existing:
                        continue

                    resource = Resource(
                        title=title,
                        subject=subject,
                        semester=semester,
                        department=department,
                        type=file_type,
                        source="drive",
                        link=link
                    )
                    session.add(resource)

        recurse_folder(ROOT_FOLDER_ID, [])
        session.commit()
        print("[✓] Google Drive sync completed successfully.")
    except Exception as e:
        session.rollback()
        print("[!] Drive Sync Error:", str(e))
        raise Exception("Drive sync failed")
    finally:
        session.close()
