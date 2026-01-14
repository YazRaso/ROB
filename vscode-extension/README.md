# Backboard Onboarding Assistant - VS Code Extension

An intelligent VS Code extension that connects to your Backboard onboarding assistant, providing instant access to your team's knowledge from Google Drive docs, Git history, and Telegram conversations.

## Features

### 💬 Interactive Chat Interface

- Beautiful chat UI directly in VS Code sidebar
- Real-time responses from your onboarding assistant
- Markdown formatting support
- Message history

### ⌨️ Keyboard Shortcuts

- **Cmd+Shift+B** (Mac) / **Ctrl+Shift+B** (Windows/Linux): Open Backboard Chat
- **Cmd+Shift+A** (Mac) / **Ctrl+Shift+A** (Windows/Linux): Quick Ask - popup input for fast questions

### 🔍 @source Command

Type `@source` in your question to get exact source files with line numbers. The extension will show you:

- File paths
- Line number ranges
- Code snippets
- Click to open files directly in the editor

### 🎯 Smart Responses

The assistant understands questions about:

- **Meeting Notes**: "What was discussed in last week's meeting?"
- **Git History**: "What changed in the drive integration?"
- **Team Conversations**: "What did the team say about deployment?"

## Installation

1. Open VS Code
2. Open the Extensions view (Cmd+Shift+X)
3. Search for "Backboard Onboarding Assistant"
4. Click Install

Or install from VSIX:

```bash
code --install-extension backboard-assistant-0.1.0.vsix
```

## Setup

### 1. Configure API URL

Open VS Code settings and set your Backboard API URL:

```json
{
  "backboard.apiUrl": "http://localhost:8000",
  "backboard.clientId": "your_client_id"
}
```

### 2. Start Using

- Click the Backboard icon in the Activity Bar
- Or press **Cmd+Shift+B** to open the chat
- Start asking questions!

## Usage Examples

### Basic Questions

```
What meetings have you seen?
```

### Git Queries

```
Show me recent commits on the backend
```

### Source Files

```
@source How does the Drive authentication work?
```

The extension will show you the exact files and code!

## Commands

Access these via Command Palette (Cmd+Shift+P):

- **Backboard: Open Chat** - Open the chat sidebar
- **Backboard: Ask Question** - Quick input popup
- **Backboard: Clear Chat History** - Start fresh

## Configuration

| Setting                       | Description              | Default                 |
| ----------------------------- | ------------------------ | ----------------------- |
| `backboard.apiUrl`            | Backboard API server URL | `http://localhost:8000` |
| `backboard.clientId`          | Your unique client ID    | `vscode_user`           |
| `backboard.enableSourceLinks` | Enable @source command   | `true`                  |

## Development

### Building from Source

```bash
cd vscode-extension
npm install
npm run compile
```

### Running in Debug Mode

1. Open the vscode-extension folder in VS Code
2. Press F5 to launch Extension Development Host
3. Test the extension in the new window

### Packaging

```bash
npm install -g vsce
vsce package
```

## Features in Detail

### Chat View

- Persistent sidebar view
- Auto-scrolling messages
- Typing indicators
- Beautiful VS Code theme integration

### Source File Integration

When you use `@source`:

- See file paths with syntax highlighting
- View line number ranges
- Click to open files
- Navigate directly to relevant code

### Mock Mode

The extension includes mock responses for testing without a backend connection. Perfect for:

- Development
- Demos
- Offline testing

## Troubleshooting

### Extension not activating

Check the Output panel → Backboard Assistant for logs

### API connection issues

Verify your `backboard.apiUrl` setting points to a running server

### Chat not showing

Try: Command Palette → "Backboard: Open Chat"

## Roadmap

- [ ] Connect to real Backboard API
- [ ] Support for multiple workspaces
- [ ] Inline code suggestions
- [ ] Custom themes for chat
- [ ] Export chat history
- [ ] Voice input support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:

- GitHub Issues: [github.com/your-repo/issues](https://github.com)
- Documentation: [your-docs-url](https://docs.example.com)

---

Built with ❤️ for McHacks 2026
