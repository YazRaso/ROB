#!/usr/bin/env python3
"""
Simple auth test that shows the exact redirect URI being used.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "backend"))

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

print("=" * 60)
print("Testing Google OAuth Flow")
print("=" * 60)

try:
    flow = InstalledAppFlow.from_client_secrets_file(
        "src/backend/credentials.json", SCOPES
    )

    print("\n📍 This will use redirect URI: http://localhost:8080/")
    print("\nMake sure this EXACT URI is in your Google Cloud Console:")
    print("  → https://console.cloud.google.com/apis/credentials")
    print("  → Click your OAuth 2.0 Client ID")
    print("  → Under 'Authorized redirect URIs', add:")
    print("     http://localhost:8080/")
    print("  → Save")

    print("\n🌐 Opening browser for authentication...")
    input("\nPress ENTER to continue...")

    creds = flow.run_local_server(port=8080)

    print("\n✅ Authentication successful!")
    print(f"✅ Token obtained!")

    # Save token
    with open("src/backend/token.json", "w") as token:
        token.write(creds.to_json())

    print("✅ Token saved to src/backend/token.json")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
