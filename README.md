# ROB - Real-time onboarding w Backboard

An intelligent onboarding assistant that integrates with Google Drive, Telegram, and GitHub to help new team members get up to speed quickly using Backboard AI.

## Features

- **Google Drive Integration**: Automatically monitors Google Drive documents for changes and indexes them
- **Backboard AI**: Stores and retrieves context from meeting notes, documentation, and code
- **Telegram Bot**: (Coming soon) Chat interface for querying the assistant
- **Smart Caching**: Tracks document changes using MD5 hashing to avoid redundant processing
- **Secure**: API keys encrypted using Fernet symmetric encryption

## How does the app work?

The application workflow starts by connecting your database, where your team stores a collection of meeting notes, linking the chat platform your team uses, and connecting the repository where the code is hosted or deployed.

<img width="2438" height="1187" alt="Screenshot 2026-01-15 at 1 18 38 PM" src="https://github.com/user-attachments/assets/47b7f919-554c-4cfa-b919-8407e96a797d" />
<br>
In our application, we use Drive for documents, Telegram for team communication, and a GitHub repository for the codebase.

<img width="2439" height="1185" alt="Screenshot 2026-01-15 at 1 39 18 PM" src="https://github.com/user-attachments/assets/f66b457c-b724-4e41-807b-adbbd77bdad9" />

Once these connections are set up, you are all ready to go. The rest is handled by our application and the Backboard API.

At this point, all connections are in place. The system continuously polls for changes and keeps the shared memory up to date.

<br>
On the user side, users can chat through the window below and ask questions about the codebase or have general conversations.

<img width="951" height="1162" alt="Screenshot 2026-01-15 at 1 21 42 PM" src="https://github.com/user-attachments/assets/43ac4d5c-8a9d-45d0-bddf-c76c7a9d9b87" />

<br>

<img width="951" height="1162" alt="Screenshot 2026-01-15 at 1 21 42 PM" src="https://github.com/user-attachments/assets/b71ab6ae-d445-4b7b-b5a6-000a6330f6d2" />
<br>
<br>

You can also track for live updates on the website:

<img width="2439" height="1190" alt="Screenshot 2026-01-15 at 1 18 57 PM" src="https://github.com/user-attachments/assets/f1901371-1789-4ae8-9244-13bfc11457d1" />

## Quick Start

### Prerequisites

- Python 3.9+
- Google Cloud Project with Drive API enabled
- Backboard API key ([get one here](https://backboard.io))

### Installation

1. Clone the repository:

```bash
git clone https://github.com/YazRaso/McHacks_onboarding_assistant.git
cd McHacks_onboarding_assistant
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env and add your Backboard API key
```

4. Set up Google Drive OAuth:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing
   - Enable Google Drive API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials as `src/backend/credentials.json`
   - Add redirect URI: `http://localhost:8080/`

### Running the Server

```bash
cd src/backend
uvicorn server:app --reload --port 8000
```

The server will be available at `http://localhost:8000`

## Usage

### 1. Create a Client

```bash
curl -X POST "http://localhost:8000/client?client_id=my_company&api_key=YOUR_BACKBOARD_KEY"
```

### 2. Authenticate with Google Drive

```bash
curl -X POST "http://localhost:8000/drive/authenticate"
```

This will open a browser window for OAuth authentication.

### 3. Register a Document

```bash
curl -X POST "http://localhost:8000/drive/register?client_id=my_company&drive_url=https://docs.google.com/document/d/YOUR_DOC_ID/edit"
```

### 4. Process the Document

```bash
curl -X POST "http://localhost:8000/drive/process?client_id=my_company&file_id=YOUR_DOC_ID"
```

The document will be uploaded to Backboard and indexed for retrieval.

### 5. Query the Assistant

```bash
curl -X POST "http://localhost:8000/messages/send?client_id=my_company&content=What%20meetings%20have%20you%20seen?"
```

### 6. Start Polling (Optional)

To automatically monitor documents for changes:

```bash
curl -X POST "http://localhost:8000/drive/start-polling?client_id=my_company&interval=300"
```

This will check for changes every 5 minutes (300 seconds).

## Project Structure

```
McHacks_onboarding_assistant/
├── src/
│   ├── backend/
│   │   ├── server.py          # FastAPI server
│   │   ├── drive_service.py   # Google Drive integration
│   │   ├── db.py              # SQLite database operations
│   │   ├── encryption.py      # API key encryption
│   │   ├── bot.py             # Telegram bot (future)
│   │   └── get_key.py         # Encryption key management
│   └── services/
│       └── place_holder.txt
├── tests/                      # Unit tests
├── scripts/                    # Example/test scripts
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Pytest configuration
└── README.md
```

## API Endpoints

### Client Management

- `POST /client` - Create a new client with Backboard
- `GET /` - Health check

### Drive Operations

- `POST /drive/authenticate` - Authenticate with Google Drive
- `POST /drive/register` - Register a document for monitoring
- `POST /drive/process` - Process and upload a document to Backboard
- `POST /drive/start-polling` - Start automatic polling for changes
- `GET /drive/documents` - List registered documents

### Message Operations

- `POST /messages/send` - Send a message to the assistant
- `POST /messages/summarize` - Get a summary of stored memories

## Testing

Run unit tests:

```bash
pytest tests/ -v
```

Run integration test:

```bash
python scripts/test_complete_integration.py
```

## Development

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_drive_service.py -v

# With coverage
pytest --cov=src/backend tests/
```

### Code Style

The project follows PEP 8 style guidelines. Format code with:

```bash
black src/
```

## Security Notes

- **Never commit** `credentials.json`, `token.json`, or `.env` files
- API keys are encrypted in the database using Fernet
- The encryption key is stored in `src/backend/key.key`
- Use environment variables for sensitive configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- Built for [McHacks 2026](https://mchacks.io)
- Powered by [Backboard AI](https://backboard.io)
- Uses Google Drive API for document monitoring

## Support

For issues or questions:

- Open a [GitHub issue](https://github.com/YazRaso/McHacks_onboarding_assistant/issues)
- Check the [documentation](QUICKSTART.md)
