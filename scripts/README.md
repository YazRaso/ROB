# Scripts

This directory contains example and testing scripts for the McHacks Onboarding Assistant.

## Available Scripts

### `test_complete_integration.py`

Complete end-to-end integration test that demonstrates:

- Client creation with Backboard
- Google Drive authentication
- Document registration and processing
- Querying the assistant

**Usage:**

```bash
python scripts/test_complete_integration.py
```

**Prerequisites:**

- Server running on port 8000
- Google Drive credentials configured
- Backboard API key set in .env

### `test_drive_auth.py`

Simple script to test Google Drive OAuth authentication.

**Usage:**

```bash
python scripts/test_drive_auth.py
```

Opens a browser window for OAuth flow and verifies authentication works.

### `test_simple_auth.py`

Shows the exact redirect URI being used for OAuth and helps debug authentication issues.

**Usage:**

```bash
python scripts/test_simple_auth.py
```

### `test_local.py`

Tests API endpoints without requiring actual Google Drive connection. Good for quick validation.

**Usage:**

```bash
# Start server first
cd src/backend && uvicorn server:app --reload --port 8080

# Then run test
python scripts/test_local.py
```

### `drive_example.py`

Comprehensive example showing the complete workflow:

1. Setting up a client
2. Authenticating with Drive
3. Registering documents
4. Starting polling

**Usage:**

```bash
python scripts/drive_example.py
```

## Testing Workflow

1. **First time setup:**

   ```bash
   # Authenticate with Google Drive
   python scripts/test_drive_auth.py
   ```

2. **Run integration test:**

   ```bash
   # Make sure server is running
   cd src/backend && uvicorn server:app --reload --port 8000

   # In another terminal
   python scripts/test_complete_integration.py
   ```

3. **Debug issues:**

   ```bash
   # Check OAuth redirect URI
   python scripts/test_simple_auth.py

   # Test endpoints without Drive
   python scripts/test_local.py
   ```

## Notes

- All scripts assume the server is running unless otherwise noted
- Make sure to set up `.env` with your Backboard API key
- Google Drive credentials should be in `src/backend/credentials.json`
- Token file will be created at `src/backend/token.json` after first auth
