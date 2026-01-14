# Contributing to McHacks Onboarding Assistant

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/McHacks_onboarding_assistant.git
   cd McHacks_onboarding_assistant
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your credentials
   ```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_drive_service.py -v

# Run with coverage
pytest --cov=src/backend tests/

# Run integration tests
python scripts/test_complete_integration.py
```

## Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small
- Add type hints where appropriate

## Making Changes

1. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**

   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**

   ```bash
   pytest
   python scripts/test_complete_integration.py
   ```

4. **Commit your changes:**

   ```bash
   git add .
   git commit -m "feat: description of your changes"
   ```

   Use conventional commit messages:

   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `test:` for tests
   - `refactor:` for code refactoring
   - `chore:` for maintenance tasks

5. **Push and create a PR:**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then open a Pull Request on GitHub.

## Project Structure

```
McHacks_onboarding_assistant/
├── src/
│   ├── backend/           # Backend application code
│   │   ├── server.py      # FastAPI server
│   │   ├── drive_service.py  # Google Drive integration
│   │   ├── db.py          # Database operations
│   │   ├── encryption.py  # API key encryption
│   │   └── bot.py         # Telegram bot (future)
│   └── services/          # Future microservices
├── tests/                 # Unit tests
├── scripts/               # Example and testing scripts
├── requirements.txt       # Python dependencies
└── README.md
```

## Adding New Features

### Adding a New API Endpoint

1. Add the endpoint to `src/backend/server.py`
2. Add corresponding database operations to `src/backend/db.py` if needed
3. Write tests in `tests/test_server.py`
4. Update API documentation in README.md

### Adding New Drive Functionality

1. Add methods to `DriveService` class in `src/backend/drive_service.py`
2. Write tests in `tests/test_drive_service.py`
3. Update documentation

## Testing Guidelines

- Write tests for all new functionality
- Aim for >80% code coverage
- Use pytest fixtures for common setup
- Mock external API calls
- Test both success and failure cases

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all functions/classes
- Update QUICKSTART.md for setup changes
- Add examples to `scripts/` directory

## Pull Request Process

1. Ensure all tests pass
2. Update documentation
3. Add a clear PR description
4. Reference any related issues
5. Wait for code review
6. Address review feedback
7. Merge after approval

## Questions?

Open an issue on GitHub or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
