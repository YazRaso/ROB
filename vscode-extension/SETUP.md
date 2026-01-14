# Backboard VS Code Extension Setup

## Quick Start

1. **Install dependencies:**

   ```bash
   cd vscode-extension
   npm install
   ```

2. **Compile the extension:**

   ```bash
   npm run compile
   ```

3. **Run in development mode:**

   - Open this folder in VS Code
   - Press `F5` to launch Extension Development Host
   - A new VS Code window will open with the extension loaded

4. **Test the extension:**
   - In the new window, press `Cmd+Shift+B` (Mac) or `Ctrl+Shift+B` (Windows/Linux)
   - The Backboard chat sidebar will open
   - Start chatting!

## Keyboard Shortcuts

- **Cmd+Shift+B** / **Ctrl+Shift+B**: Open Backboard Chat
- **Cmd+Shift+A** / **Ctrl+Shift+A**: Quick Ask (popup input)

## Features to Test

### 1. Basic Chat

Type: `help`

Expected: Welcome message with features

### 2. Meeting Notes Query

Type: `What meetings have you seen?`

Expected: Mock response about meetings from June 2024 - January 2026

### 3. Git History Query

Type: `Show me recent commits`

Expected: Mock response about Drive integration and refactoring

### 4. @source Command

Type: `@source How does authentication work?`

Expected: Response with clickable source files showing:

- server.py (lines 67-92)
- drive_service.py (lines 145-167)
- README.md (lines 1-15)

Click on any source file to open it in the editor!

## Configuration

Go to VS Code Settings and search for "backboard" to configure:

- **API URL**: Set to your backend URL (default: http://localhost:8000)
- **Client ID**: Your unique identifier (default: vscode_user)
- **Enable Source Links**: Show source files with @source command

## Package Extension

To create a `.vsix` file for distribution:

```bash
npm install -g vsce
vsce package
```

This creates `backboard-assistant-0.1.0.vsix` that can be installed with:

```bash
code --install-extension backboard-assistant-0.1.0.vsix
```

## Development

### Watch mode

For active development with auto-recompile:

```bash
npm run watch
```

Then press `Cmd+R` in the Extension Development Host to reload.

### File Structure

```
vscode-extension/
├── src/
│   ├── extension.ts          # Main entry point
│   ├── chatViewProvider.ts   # Chat UI webview
│   └── backboardService.ts   # API communication
├── resources/
│   └── icon.svg              # Extension icon
├── dist/                     # Compiled JavaScript (generated)
├── package.json              # Extension manifest
└── tsconfig.json             # TypeScript config
```

## Troubleshooting

### Extension doesn't activate

- Check the Debug Console in Extension Development Host
- Look for error messages in Output → Backboard Assistant

### Chat not showing

- Press `Cmd+Shift+P` → type "Backboard: Open Chat"
- Check if the Backboard icon appears in the Activity Bar

### TypeScript errors

- Run `npm install` to ensure all dependencies are installed
- Run `npm run compile` to check for compilation errors

## Next Steps

1. **Connect to Real API**: Update `backboardService.ts` to call actual backend
2. **Custom Styling**: Modify the HTML/CSS in `chatViewProvider.ts`
3. **Add Features**: Implement file upload, voice input, etc.

Happy coding! 🚀
