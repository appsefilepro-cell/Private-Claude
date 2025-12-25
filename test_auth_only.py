#!/usr/bin/env python3
"""
Quick test to verify authentication setup works
This will show the device code but won't wait for completion
"""

import os
import sys
from msal import PublicClientApplication

# Use Microsoft Graph Explorer client ID (public app)
client_id = "de8bc8b5-d9f9-48b1-a8ad-b748da725064"
tenant_id = "common"
authority = f"https://login.microsoftonline.com/{tenant_id}"

scopes = [
    "Files.Read.All",
    "Sites.Read.All",
    "User.Read"
]

print("\n" + "="*60)
print("TESTING MICROSOFT 365 AUTHENTICATION")
print("="*60)
print(f"\nClient ID: {client_id}")
print(f"Authority: {authority}")
print(f"Scopes: {', '.join(scopes)}")
print("\n" + "="*60)

try:
    # Create MSAL app
    app = PublicClientApplication(
        client_id,
        authority=authority
    )

    print("✅ MSAL app created successfully")

    # Initiate device flow
    print("\nInitiating device code flow...")
    flow = app.initiate_device_flow(scopes=scopes)

    if "user_code" not in flow:
        print("❌ Failed to create device flow")
        print(f"Error: {flow.get('error_description', 'Unknown error')}")
        sys.exit(1)

    print("\n" + "="*60)
    print("✅ AUTHENTICATION SETUP WORKS!")
    print("="*60)
    print("\nYou would see this message when running the actual extraction:")
    print("\n" + flow["message"])
    print("\n" + "="*60)
    print("\n✅ SUCCESS! Authentication is configured correctly.")
    print("\nThe actual extraction script will:")
    print("  1. Show you this device code")
    print("  2. Wait for you to authenticate")
    print("  3. Start downloading your documents")
    print("\nYou're ready to run:")
    print("  ./EXTRACT_SIMPLE.sh")
    print("\n" + "="*60)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("  1. Check internet connection")
    print("  2. Verify msal is installed: pip3 install msal")
    print("  3. Try again in a few moments")
    sys.exit(1)
