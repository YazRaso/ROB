#!/usr/bin/env python3
"""
Example script demonstrating Google Drive integration for the Onboarding Assistant.

This script shows how to:
1. Set up a client
2. Authenticate with Google Drive
3. Register documents for monitoring
4. Start polling for changes
"""

import asyncio
import httpx
import sys


async def main():
    """Main demonstration workflow."""

    # Configuration
    base_url = "https://rob-production.up.railway.app/"
    client_id = "demo_company"
    backboard_api_key = input("Enter your Backboard API key: ").strip()

    if not backboard_api_key:
        print("Error: Backboard API key is required")
        sys.exit(1)

    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n=== Setting up Onboarding Assistant with Drive Integration ===\n")

        # Step 1: Create a client
        print("Step 1: Creating client...")
        try:
            response = await client.post(
                f"{base_url}/client",
                params={"client_id": client_id, "api_key": backboard_api_key},
            )
            if response.status_code == 201:
                print(f"OK Client '{client_id}' created successfully")
            elif response.status_code == 409:
                print(f"OK Client '{client_id}' already exists")
            else:
                print(f"✗ Error creating client: {response.text}")
                return
        except Exception as e:
            print(f"✗ Error: {e}")
            return

        # Step 2: Authenticate with Google Drive
        print("\nStep 2: Authenticating with Google Drive...")
        print("(This will open a browser window for OAuth authentication)")
        try:
            response = await client.post(f"{base_url}/drive/authenticate")
            if response.status_code == 201:
                print("OK Google Drive authentication successful")
            else:
                print(f"✗ Error authenticating: {response.text}")
                return
        except Exception as e:
            print(f"✗ Error: {e}")
            return

        # Step 3: Register documents
        print("\nStep 3: Registering Google Drive documents...")
        print("Enter Google Drive document URLs (one per line).")
        print("Press Enter on an empty line when done.\n")

        drive_urls = []
        while True:
            url = input("Drive URL: ").strip()
            if not url:
                break
            drive_urls.append(url)

        if not drive_urls:
            print("No documents to register. Exiting.")
            return

        registered_count = 0
        for url in drive_urls:
            try:
                response = await client.post(
                    f"{base_url}/drive/register",
                    params={"client_id": client_id, "drive_url": url},
                )
                if response.status_code == 201:
                    data = response.json()
                    print(f"OK Registered: {data.get('file_id')}")
                    registered_count += 1
                else:
                    print(f"✗ Failed to register {url}: {response.text}")
            except Exception as e:
                print(f"✗ Error registering {url}: {e}")

        print(f"\nRegistered {registered_count} document(s)")

        # Step 4: Start polling
        print("\nStep 4: Starting document polling...")
        interval = input("Enter polling interval in seconds (default: 300): ").strip()
        interval = int(interval) if interval.isdigit() else 300

        try:
            response = await client.post(
                f"{base_url}/drive/start-polling",
                params={"client_id": client_id, "interval": interval},
            )
            if response.status_code == 201:
                data = response.json()
                print(f"OK Polling started!")
                print(f"  - Monitoring {data['document_count']} document(s)")
                print(f"  - Check interval: {data['interval']} seconds")
                print("\nThe server is now monitoring your documents for changes.")
                print(
                    "Content will automatically be sent to Backboard when changes are detected."
                )
            else:
                print(f"✗ Error starting polling: {response.text}")
        except Exception as e:
            print(f"✗ Error: {e}")

        # Show registered documents
        print("\n=== Registered Documents ===")
        try:
            response = await client.get(
                f"{base_url}/drive/documents", params={"client_id": client_id}
            )
            if response.status_code == 200:
                data = response.json()
                for doc in data["documents"]:
                    print(f"\n {doc['file_name']}")
                    print(f"   ID: {doc['file_id']}")
                    print(f"   Last Modified: {doc['last_modified']}")
                    print(
                        f"   Status: {'Processed' if doc['content_hash'] else 'Pending'}"
                    )
            else:
                print(f"Could not retrieve documents: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n[OK] Setup complete! Your Drive integration is active.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
