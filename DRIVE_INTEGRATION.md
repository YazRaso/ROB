# Google Drive Integration for Onboarding Assistant

This module provides Google Drive integration for the McHacks Onboarding Assistant, allowing automatic extraction and processing of meeting notes from Google Drive documents.

## Features

- 🔐 **OAuth2 Authentication** - Secure authentication with Google Drive API
- 🔄 **Polling Mechanism** - Automatically detects changes in Drive documents
- 📝 **Content Extraction** - Extracts text from Google Docs
- 🧠 **Memory Integration** - Feeds content to Backboard API for AI memory
- 💾 **Change Detection** - Uses content hashing to avoid redundant processing
- 📊 **Multi-Document Support** - Monitor multiple documents simultaneously

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements_drive.txt
```

### 2. Set Up Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google Drive API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

### 3. Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Configure the OAuth consent screen if prompted:
   - User Type: External (for testing) or Internal (for organization)
   - Add required information
   - Add scope: `https://www.googleapis.com/auth/drive.readonly`
4. Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: "McHacks Onboarding Assistant"
5. Download the credentials JSON file
6. Rename it to `credentials.json` and place it in the `src/backend/` directory

### 4. First-Time Authentication

When you first use the Drive service, it will:

1. Open a browser window for authentication
2. Ask you to sign in with your Google account
3. Request permission to read your Drive files
4. Save a token file (`token.json`) for future use

## API Endpoints

### Authenticate with Google Drive

```bash
POST /drive/authenticate
```

Opens OAuth2 flow for authentication. Must be done before using other Drive endpoints.

**Response:**

```json
{
  "status": "authenticated",
  "message": "Successfully authenticated with Google Drive"
}
```

### Register a Document for Monitoring

```bash
POST /drive/register?client_id=YOUR_CLIENT_ID&drive_url=DRIVE_URL_OR_FILE_ID
```

**Parameters:**

- `client_id`: Your client ID (must be created first via `/client` endpoint)
- `drive_url`: Google Drive document URL or file ID

**Example:**

```bash
curl -X POST "http://localhost:8000/drive/register?client_id=mycompany&drive_url=https://docs.google.com/document/d/1ABC123xyz/edit"
```

**Response:**

```json
{
  "status": "registered",
  "file_id": "1ABC123xyz",
  "message": "Document registered for monitoring"
}
```

### Process a Document Manually

```bash
POST /drive/process?client_id=YOUR_CLIENT_ID&file_id=FILE_ID
```

Immediately process a document and send its content to Backboard.

**Response:**

```json
{
  "status": "processed",
  "file_id": "1ABC123xyz",
  "message": "Document processed successfully"
}
```

### Start Polling

```bash
POST /drive/start-polling?client_id=YOUR_CLIENT_ID&interval=300
```

**Parameters:**

- `client_id`: Your client ID
- `interval`: Polling interval in seconds (default: 300 = 5 minutes)

**Response:**

```json
{
  "status": "polling_started",
  "client_id": "mycompany",
  "document_count": 3,
  "interval": 300,
  "message": "Started polling 3 documents every 300 seconds"
}
```

### Get Registered Documents

```bash
GET /drive/documents?client_id=YOUR_CLIENT_ID
```

Returns all registered documents for a client.

**Response:**

```json
{
  "client_id": "mycompany",
  "document_count": 2,
  "documents": [
    {
      "file_id": "1ABC123xyz",
      "file_name": "Team Meeting Notes",
      "content_hash": "a1b2c3d4e5f6...",
      "last_modified": "2026-01-12T10:30:00Z",
      "created_at": "2026-01-12T09:00:00Z",
      "updated_at": "2026-01-12T10:30:00Z"
    }
  ]
}
```

## Usage Example

### Complete Workflow

```python
import httpx
import asyncio

async def setup_drive_monitoring():
    base_url = "http://localhost:8000"
    client_id = "mycompany"
    api_key = "your_backboard_api_key"

    async with httpx.AsyncClient() as client:
        # 1. Create a client (if not exists)
        await client.post(
            f"{base_url}/client",
            params={"client_id": client_id, "api_key": api_key}
        )

        # 2. Authenticate with Google Drive
        await client.post(f"{base_url}/drive/authenticate")

        # 3. Register documents for monitoring
        drive_urls = [
            "https://docs.google.com/document/d/1ABC123xyz/edit",
            "https://docs.google.com/document/d/2DEF456abc/edit"
        ]

        for url in drive_urls:
            await client.post(
                f"{base_url}/drive/register",
                params={"client_id": client_id, "drive_url": url}
            )

        # 4. Start polling (checks every 5 minutes)
        await client.post(
            f"{base_url}/drive/start-polling",
            params={"client_id": client_id, "interval": 300}
        )

# Run the setup
asyncio.run(setup_drive_monitoring())
```

## How It Works

### 1. Content Detection

- Each document's content is hashed using MD5
- Hash is stored in the database
- On each poll, new hash is compared with stored hash
- Only changed documents are processed

### 2. Content Processing

When a document changes:

1. Content is extracted from Google Docs
2. Formatted with metadata (title, last modified, link)
3. Sent to Backboard with memory enabled
4. Database is updated with new hash and content

### 3. Backboard Integration

Content is sent to Backboard in this format:

```
Meeting Notes from: [Document Title]
Last Modified: [Timestamp]
Link: [Drive URL]

Content:
[Actual document content]

Please remember this information for future queries about onboarding, meetings, and project context.
```

## Database Schema

The Drive integration adds a new table:

```sql
CREATE TABLE drive_documents (
    file_id TEXT PRIMARY KEY,
    client_id TEXT,
    file_name TEXT,
    content_hash TEXT,
    last_modified TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Security Considerations

- ✅ OAuth2 tokens are stored locally in `token.json`
- ✅ API keys are encrypted before storage
- ✅ Read-only access to Drive (cannot modify or delete files)
- ⚠️ Keep `credentials.json` and `token.json` secure
- ⚠️ Add both files to `.gitignore`

## Troubleshooting

### Authentication Issues

**Problem:** "Credentials file not found"

- **Solution:** Download OAuth2 credentials from Google Cloud Console and save as `credentials.json`

**Problem:** "The project has been deleted"

- **Solution:** Create a new project in Google Cloud Console and enable Drive API

### Permission Errors

**Problem:** "Cannot access file"

- **Solution:** Ensure the Google account used for authentication has access to the Drive document

### Polling Not Working

**Problem:** Documents not being processed

- **Solution:**
  1. Check server logs for errors
  2. Verify documents are registered using `/drive/documents` endpoint
  3. Ensure polling was started with `/drive/start-polling`

## Future Enhancements

- [ ] Support for multiple file types (Sheets, PDFs, etc.)
- [ ] Webhook-based updates instead of polling
- [ ] Document folder monitoring
- [ ] Incremental content updates
- [ ] Rate limiting and quota management
- [ ] Document permissions verification
- [ ] Automatic re-authentication on token expiry

## Contributing

When adding new features:

1. Update the database schema in `db.py`
2. Add new endpoints in `server.py`
3. Update this README with usage examples
4. Add tests in `tests/test_drive_service.py`
