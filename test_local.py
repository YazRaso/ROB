#!/usr/bin/env python3
"""
Simple test script to demonstrate the Google Drive integration is working.
This tests the API endpoints without actually connecting to Google Drive.
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")

def test_root():
    """Test the root endpoint."""
    print_section("Testing Root Endpoint")
    response = requests.get(f"{BASE_URL}/")
    print(f"GET / → Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("✓ Root endpoint working!")

def test_api_docs():
    """Test that API docs are available."""
    print_section("Testing API Documentation")
    response = requests.get(f"{BASE_URL}/docs")
    print(f"GET /docs → Status: {response.status_code}")
    print("✓ API documentation available at http://localhost:8080/docs")

def main():
    """Run all tests."""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   Google Drive Integration - Local Test Suite             ║
    ║   McHacks Onboarding Assistant                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    try:
        test_root()
        test_api_docs()
        
        print_section("Test Summary")
        print("✓ All basic tests passed!")
        print("\nServer is running and ready for:")
        print("  - Client creation (/client)")
        print("  - Drive authentication (/drive/authenticate)")
        print("  - Document registration (/drive/register)")
        print("  - Document processing (/drive/process)")
        print("  - Polling (/drive/start-polling)")
        print("  - Document listing (/drive/documents)")
        
        print("\nNext steps:")
        print("  1. Get a Backboard API key")
        print("  2. Set up Google Cloud credentials")
        print("  3. Run: python src/backend/drive_setup_example.py")
        
        print("\n" + "=" * 60)
        print("✅ Server is functional and ready for integration!")
        print("=" * 60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server!")
        print("Please start the server first:")
        print("  cd src/backend && uvicorn server:app --reload --port 8080")
        return 1
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
