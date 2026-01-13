#!/usr/bin/env python3
"""
Quick test to verify Google Drive authentication works.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "backend"))

from drive_service import DriveService

print("Testing Google Drive Authentication...")
print("=" * 60)

try:
    # Initialize Drive service
    drive_service = DriveService(
        credentials_path="src/backend/credentials.json",
        token_path="src/backend/token.json",
    )

    print("✓ DriveService initialized")

    # Authenticate (will open browser)
    print("\n🌐 Opening browser for OAuth authentication...")
    print("Please sign in with your Google account and grant access.")
    drive_service.authenticate()

    print("\n✓ Authentication successful!")
    print("✓ Token saved to src/backend/token.json")

    # Test API access
    print("\n📂 Testing Drive API access...")

    # Try to list some files (just metadata, not content)
    if drive_service.service:
        results = (
            drive_service.service.files()
            .list(pageSize=5, fields="files(id, name, modifiedTime)")
            .execute()
        )

        files = results.get("files", [])

        if files:
            print(f"\n✓ Successfully connected to Drive!")
            print(f"✓ Found {len(files)} files (showing up to 5):")
            for file in files:
                print(f"  - {file['name']} (ID: {file['id']})")
        else:
            print("\n✓ Connected to Drive (no files found)")

    print("\n" + "=" * 60)
    print("✅ Google Drive integration is ready!")
    print("\nYou can now:")
    print("  1. Start the server: cd src/backend && uvicorn server:app --reload")
    print("  2. Register documents via API")
    print("  3. Start polling for changes")
    print("=" * 60)

except FileNotFoundError as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure credentials.json exists in src/backend/")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Authentication failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
