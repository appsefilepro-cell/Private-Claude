#!/usr/bin/env python3
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes for all APIs
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/calendar'
]

def authenticate_google_apis():
    creds = None
    token_file = 'data/google_credentials/token.json'
    credentials_file = 'config/google/oauth_credentials.json'

    # Check if token already exists
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                print("ERROR: OAuth credentials file not found!")
                print(f"Please download from Google Cloud Console and save to:")
                print(f"  {credentials_file}")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save credentials for next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

        print("✅ Google APIs authenticated successfully!")
        print(f"   Token saved to: {token_file}")

    return creds

if __name__ == '__main__':
    print("=" * 80)
    print("GOOGLE APIs AUTHENTICATION")
    print("=" * 80)
    creds = authenticate_google_apis()
    if creds:
        print("\n✅ Authentication complete!")
        print("   All Google APIs are now accessible")
    else:
        print("\n⚠️ Authentication failed")
        print("   Follow setup instructions to configure OAuth 2.0")
