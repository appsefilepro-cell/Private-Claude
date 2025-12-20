#!/usr/bin/env python3
"""
Google Drive Automated Upload Script
Requires: google-auth, google-auth-oauthlib, google-api-python-client
"""

import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import pickle

# If modifying these scopes, delete the file token.pickle
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveUploader:
    """Upload files to Google Drive programmatically"""

    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with Google Drive API"""

        # Token file stores user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('drive', 'v3', credentials=self.creds)

    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """Create folder in Google Drive"""

        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]

        folder = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()

        return folder.get('id')

    def upload_file(self, file_path: str, folder_id: str = None) -> str:
        """Upload file to Google Drive"""

        file_name = os.path.basename(file_path)

        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(file_path, resumable=True)

        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        print(f'✓ Uploaded: {file_name} (ID: {file.get("id")})')
        return file.get('id')

    def upload_directory(self, dir_path: str, parent_folder_id: str = None):
        """Upload entire directory to Google Drive"""

        folder_name = os.path.basename(dir_path)
        folder_id = self.create_folder(folder_name, parent_folder_id)

        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)

            if os.path.isfile(item_path):
                self.upload_file(item_path, folder_id)
            elif os.path.isdir(item_path):
                self.upload_directory(item_path, folder_id)


if __name__ == "__main__":
    # Example usage
    uploader = GoogleDriveUploader()

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     GOOGLE DRIVE AUTOMATED UPLOAD                            ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    # Upload deployment packages
    print("[1/3] Uploading trading bot package...")
    uploader.upload_file('./deploy/TradingBot.zip')

    print("[2/3] Uploading legal tools package...")
    uploader.upload_file('./deploy/LegalTools.zip')

    print("[3/3] Uploading complete system package...")
    uploader.upload_file('./deploy/Agent_5.0_Complete.zip')

    print()
    print("✓ All files uploaded successfully!")
    print("✓ Check Google Drive: https://drive.google.com")
