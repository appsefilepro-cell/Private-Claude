#!/usr/bin/env python3
import os
import json
from msal import ConfidentialClientApplication

def authenticate_microsoft_graph():
    # Load credentials
    creds_file = 'config/microsoft/app_credentials.json'

    if not os.path.exists(creds_file):
        print("ERROR: Credentials file not found!")
        print(f"Please create: {creds_file}")
        print("Follow setup instructions to get credentials from Azure Portal")
        return None

    with open(creds_file, 'r') as f:
        config = json.load(f)

    # Create MSAL application
    app = ConfidentialClientApplication(
        config['clientId'],
        authority=config['authority'],
        client_credential=config['clientSecret']
    )

    # Get access token
    result = app.acquire_token_for_client(scopes=config['scopes'])

    if 'access_token' in result:
        print("✅ Microsoft Graph API authenticated successfully!")

        # Save token
        token_file = 'data/microsoft_credentials/token.json'
        os.makedirs('data/microsoft_credentials', exist_ok=True)

        with open(token_file, 'w') as f:
            json.dump({
                'access_token': result['access_token'],
                'expires_in': result['expires_in'],
                'token_type': result['token_type']
            }, f, indent=2)

        print(f"   Token saved to: {token_file}")
        return result['access_token']
    else:
        print("⚠️ Authentication failed:")
        print(f"   {result.get('error')}")
        print(f"   {result.get('error_description')}")
        return None

if __name__ == '__main__':
    print("=" * 80)
    print("MICROSOFT GRAPH API AUTHENTICATION")
    print("=" * 80)
    token = authenticate_microsoft_graph()
    if token:
        print("\n✅ Authentication complete!")
        print("   Microsoft Graph API is now accessible")
    else:
        print("\n⚠️ Authentication failed")
        print("   Follow setup instructions to configure Azure AD app")
