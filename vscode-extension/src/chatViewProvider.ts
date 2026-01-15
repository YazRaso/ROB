import * as vscode from "vscode";
import * as path from "path";
import { BackboardService, ChatMessage, FileContext } from "./backboardService";

export class ChatViewProvider implements vscode.WebviewViewProvider {
  private _view?: vscode.WebviewView;
  private messages: ChatMessage[] = [];
  private currentContext: FileContext | null = null;

  constructor(
    private readonly _extensionUri: vscode.Uri,
    private readonly backboardService: BackboardService
  ) {}

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri],
    };

    webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

    webviewView.webview.onDidReceiveMessage(async (data: any) => {
      switch (data.type) {
        case "sendMessage":
          await this.handleUserMessage(data.message);
          break;
        case "openFile":
          this.openFileAtLine(data.path, data.line);
          break;
        case "webviewReady":
          this.sendWelcomeMessage();
          break;
        case "attachFile":
          this.attachCurrentFile();
          break;
        case "removeContext":
          this.removeContext();
          break;
      }
    });

    webviewView.onDidChangeVisibility(() => {
      if (webviewView.visible && this.messages.length === 0) {
        this.sendWelcomeMessage();
      }
    });
  }

  private async handleUserMessage(message: string) {
    const userMessage: ChatMessage = {
      role: "user",
      content: message,
      timestamp: Date.now(),
      context: this.currentContext || undefined,
    };

    this.messages.push(userMessage);
    this._view?.webview.postMessage({
      type: "addMessage",
      message: userMessage,
    });

    if (this.currentContext) {
      this.currentContext = null;
      this._view?.webview.postMessage({ type: "contextRemoved" });
    }

    this._view?.webview.postMessage({ type: "showTyping" });

    try {
      const response = await this.backboardService.sendMessage(
        message,
        userMessage.context
      );
      this.messages.push(response);
      this._view?.webview.postMessage({ type: "hideTyping" });
      this._view?.webview.postMessage({
        type: "addMessage",
        message: response,
      });

      // Handle tool results (e.g., create_file)
      if ((response as any).toolResult?.type === 'create_file') {
        await this.handleCreateFile((response as any).toolResult);
      }
    } catch (error) {
      this._view?.webview.postMessage({ type: "hideTyping" });
      const errorMessage: ChatMessage = {
        role: "assistant",
        content:
          "Sorry, I encountered an error. Please check your connection and try again.",
        timestamp: Date.now(),
      };
      this.messages.push(errorMessage);
      this._view?.webview.postMessage({
        type: "addMessage",
        message: errorMessage,
      });
    }
  }

  private sendWelcomeMessage() {
    const welcomeMessage: ChatMessage = {
      role: "assistant",
      content: `Welcome to Backboard Assistant!

I can help you explore your team's knowledge from:
• Google Drive documents
• Git history and commits
• Telegram conversations

**Quick tips:**
• Type @source to see exact source files
• Type @create_file to create onboarding docs
• Type @get_recent_context to catch up on recent activity
• Type @generate_mermaid_graph to visualize feature lineage
• Use Cmd+Shift+A for quick questions
• Ask about meetings, code changes, or team discussions

How can I help you today?`,
      timestamp: Date.now(),
    };

    this.messages.push(welcomeMessage);
    this._view?.webview.postMessage({
      type: "addMessage",
      message: welcomeMessage,
    });
  }

  public sendMessageFromCommand(message: string) {
    if (this._view) {
      this._view.show?.(true);
      setTimeout(() => {
        this._view?.webview.postMessage({
          type: "setInput",
          message: message,
        });
      }, 100);
    }
  }

  public clearChat() {
    this.messages = [];
    this._view?.webview.postMessage({ type: "clearChat" });
    this.sendWelcomeMessage();
    vscode.window.showInformationMessage("Chat history cleared!");
  }

  private attachCurrentFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showInformationMessage("No file is currently open");
      return;
    }

    const document = editor.document;
    const selection = editor.selection;
    const fileName = vscode.workspace.asRelativePath(document.uri);
    
    if (!selection.isEmpty) {
      const selectedText = document.getText(selection);
      this.currentContext = {
        fileName: fileName,
        filePath: document.uri.fsPath,
        content: selectedText,
        lineStart: selection.start.line + 1,
        lineEnd: selection.end.line + 1,
      };
    } else {
      this.currentContext = {
        fileName: fileName,
        filePath: document.uri.fsPath,
        content: document.getText(),
      };
    }

    this._view?.webview.postMessage({
      type: "fileAttached",
      context: this.currentContext,
    });
  }

  private removeContext() {
    this.currentContext = null;
    this._view?.webview.postMessage({ type: "contextRemoved" });
  }

  private async handleCreateFile(toolResult: any) {
    try {
      const filename = toolResult.filename;
      const content = toolResult.content;

      if (!filename || !content) {
        vscode.window.showErrorMessage('File creation failed: missing filename or content');
        return;
      }

      // Validate and sanitize filename to prevent path traversal
      if (!filename.trim()) {
        vscode.window.showErrorMessage('File creation failed: filename cannot be empty');
        return;
      }

      // Get workspace folder
      const workspaceFolders = vscode.workspace.workspaceFolders;
      if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('No workspace folder found');
        return;
      }

      const workspaceRoot = workspaceFolders[0].uri;
      
      // Normalize and validate path segments
      const normalizedPath = path.normalize(filename).replace(/\\/g, '/');
      const segments = normalizedPath.split('/').filter(seg => seg.length > 0);
      
      // Reject absolute paths
      if (path.isAbsolute(normalizedPath)) {
        vscode.window.showErrorMessage('File creation failed: absolute paths are not allowed');
        return;
      }
      
      // Reject paths containing '..' (path traversal)
      if (segments.includes('..')) {
        vscode.window.showErrorMessage('File creation failed: path traversal (..) is not allowed');
        return;
      }
      
      // Build target URI using sanitized segments
      const fileUri = vscode.Uri.joinPath(workspaceRoot, ...segments);
      
      // Verify the resolved path is inside workspace root
      const workspaceRootPath = workspaceRoot.fsPath;
      const filePath = fileUri.fsPath;
      const relativePath = path.relative(workspaceRootPath, filePath);
      
      if (relativePath.startsWith('..') || path.isAbsolute(relativePath)) {
        vscode.window.showErrorMessage('File creation failed: path is outside workspace');
        return;
      }

      // Create directory if needed using sanitized segments
      if (segments.length > 1) {
        const dirSegments = segments.slice(0, -1);
        const dirUri = vscode.Uri.joinPath(workspaceRoot, ...dirSegments);
        
        try {
          await vscode.workspace.fs.createDirectory(dirUri);
        } catch (error: any) {
          // Only ignore "already exists" errors, rethrow others
          if (error instanceof vscode.FileSystemError) {
            // Check if it's a FileExists error
            if (error.code === 'EntryExists' || error.code === 'FileExists') {
              // Directory already exists, this is fine
            } else {
              // Other filesystem errors (permission, IO, etc.) should be surfaced
              throw error;
            }
          } else {
            // Non-FileSystemError should be rethrown
            throw error;
          }
        }
      }

      // Write file
      const encoder = new TextEncoder();
      const fileData = encoder.encode(content);
      await vscode.workspace.fs.writeFile(fileUri, fileData);

      // Open the file
      const document = await vscode.workspace.openTextDocument(fileUri);
      await vscode.window.showTextDocument(document);

      vscode.window.showInformationMessage(`File created: ${filename}`);
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to create file: ${error}`);
    }
  }

  private openFileAtLine(filePath: string, line?: number) {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders) {
      vscode.window.showErrorMessage("No workspace folder open");
      return;
    }

    const uri = vscode.Uri.joinPath(workspaceFolders[0].uri, filePath);
    vscode.window.showTextDocument(uri, {
      selection: line ? new vscode.Range(line - 1, 0, line - 1, 0) : undefined,
    });
  }

  private getNonce() {
    let text = "";
    const possible =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (let i = 0; i < 32; i++) {
      text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
  }

  private _getHtmlForWebview(webview: vscode.Webview) {
    const nonce = this.getNonce();

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <title>Backboard Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            background: linear-gradient(180deg, var(--vscode-editor-background) 0%, var(--vscode-sideBar-background) 100%);
            color: var(--vscode-editor-foreground);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        #chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .message {
            display: flex;
            flex-direction: column;
            gap: 6px;
            animation: slideIn 0.2s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            align-items: flex-end;
        }

        .message.assistant {
            align-items: flex-start;
        }

        .message-header {
            font-size: 11px;
            opacity: 0.7;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .message-content {
            max-width: 85%;
            padding: 10px 14px;
            border-radius: 12px;
            line-height: 1.5;
            word-wrap: break-word;
        }

        .message.user .message-content {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border-bottom-right-radius: 4px;
        }

        .message.assistant .message-content {
            background-color: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-bottom-left-radius: 4px;
        }

        .source-files {
            margin-top: 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .source-file {
            background-color: var(--vscode-editor-inactiveSelectionBackground);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            padding: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .source-file:hover {
            background-color: var(--vscode-list-hoverBackground);
            border-color: var(--vscode-focusBorder);
            transform: translateX(4px);
        }

        .source-file-header {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
            font-size: 13px;
            margin-bottom: 6px;
        }

        .source-file-icon {
            opacity: 0.7;
        }

        .source-file-lines {
            font-size: 11px;
            opacity: 0.6;
            margin-top: 2px;
        }

        .source-file-code {
            margin-top: 8px;
            padding: 8px;
            background-color: var(--vscode-textCodeBlock-background);
            border-radius: 4px;
            font-family: var(--vscode-editor-font-family);
            font-size: 12px;
            overflow-x: auto;
            white-space: pre;
            line-height: 1.4;
        }

        #typing-indicator {
            display: none;
            align-items: center;
            gap: 6px;
            padding: 10px 14px;
            background-color: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 12px;
            width: fit-content;
        }

        #typing-indicator.show {
            display: flex;
        }

        .typing-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: var(--vscode-editor-foreground);
            opacity: 0.4;
            animation: typing 1.4s infinite;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing {
            0%, 60%, 100% {
                opacity: 0.4;
                transform: scale(1);
            }
            30% {
                opacity: 1;
                transform: scale(1.2);
            }
        }

        #input-container {
            padding: 12px 16px;
            background-color: var(--vscode-editor-background);
            border-top: 1px solid var(--vscode-panel-border);
            display: flex;
            align-items: flex-end;
            gap: 8px;
        }

        .input-wrapper {
            flex: 1;
            display: flex;
            align-items: center;
            background-color: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 6px;
            padding: 8px 12px;
            transition: all 0.2s ease;
        }

        .input-wrapper:focus-within {
            border-color: var(--vscode-focusBorder);
            box-shadow: 0 0 0 1px var(--vscode-focusBorder);
        }

        #message-input {
            flex: 1;
            background: transparent;
            color: var(--vscode-input-foreground);
            border: none;
            padding: 0;
            font-family: var(--vscode-font-family);
            font-size: 13px;
            line-height: 20px;
            resize: none;
            outline: none;
            max-height: 200px;
            overflow-y: auto;
        }

        #message-input::placeholder {
            color: var(--vscode-input-placeholderForeground);
        }

        #message-input::-webkit-scrollbar {
            width: 6px;
        }

        #message-input::-webkit-scrollbar-thumb {
            background: var(--vscode-scrollbarSlider-background);
            border-radius: 3px;
        }

        #message-input:focus {
            border-color: var(--vscode-focusBorder);
        }

        #send-button {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s ease;
            flex-shrink: 0;
        }

        #send-button:hover:not(:disabled) {
            background-color: var(--vscode-button-hoverBackground);
            transform: scale(1.05);
        }

        #send-button:active {
            transform: scale(0.95);
        }

        #send-button:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }

        #send-button svg {
            width: 16px;
            height: 16px;
        }

        #attach-file-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            background: transparent;
            color: var(--vscode-icon-foreground);
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s ease;
            flex-shrink: 0;
        }

        #attach-file-btn:hover {
            background-color: var(--vscode-toolbar-hoverBackground);
        }

        #attach-file-btn svg {
            width: 16px;
            height: 16px;
        }

        #attached-file {
            padding: 8px 16px;
            border-top: 1px solid var(--vscode-panel-border);
        }

        .attached-file-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 8px;
            background-color: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            border-radius: 4px;
            font-size: 12px;
        }

        .file-icon {
            font-size: 14px;
        }

        #remove-file-btn {
            width: 18px;
            height: 18px;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            background: transparent;
            color: inherit;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 700;
            transition: all 0.15s ease;
        }

        #remove-file-btn:hover {
            background-color: var(--vscode-errorForeground);
            color: white;
        }

        .shortcut-hint {
            font-size: 10px;
            opacity: 0.5;
            text-align: center;
            padding: 8px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        code {
            background-color: var(--vscode-textCodeBlock-background);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: var(--vscode-editor-font-family);
            font-size: 0.9em;
        }

        pre {
            background-color: var(--vscode-textCodeBlock-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 6px;
            padding: 12px;
            margin: 8px 0;
            overflow-x: auto;
        }

        pre code {
            background: none;
            padding: 0;
            font-size: 0.85em;
            line-height: 1.5;
        }

        strong {
            font-weight: 700;
        }
    </style>
</head>
<body>
    <div class="shortcut-hint">
        Cmd+Shift+B to open • Cmd+Shift+A for quick questions
    </div>
    <div id="chat-container"></div>
    <div id="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    </div>
    <div id="attached-file" style="display: none;">
        <div class="attached-file-badge">
            <span class="file-icon">[file]</span>
            <span id="attached-file-name"></span>
            <button id="remove-file-btn" title="Remove file">×</button>
        </div>
    </div>
    <div id="input-container">
        <button id="attach-file-btn" title="Attach current file" aria-label="Attach file">
            <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M11.5 1a3.5 3.5 0 0 0-3.5 3.5V11a2 2 0 1 0 4 0V4.5a.5.5 0 0 1 1 0V11a3 3 0 1 1-6 0V4.5a4.5 4.5 0 1 1 9 0V11a.5.5 0 0 1-1 0V4.5A3.5 3.5 0 0 0 11.5 1z"/>
            </svg>
        </button>
        <div class="input-wrapper">
            <textarea 
                id="message-input" 
                placeholder="Ask Backboard..."
                rows="1"
                aria-label="Chat message"
            ></textarea>
        </div>
        <button id="send-button" title="Send message" aria-label="Send message">
            <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M15.854 7.354l-7-7a.5.5 0 0 0-.708.708L14.293 7H.5a.5.5 0 0 0 0 1h13.793l-6.147 6.146a.5.5 0 0 0 .708.708l7-7a.5.5 0 0 0 0-.708z"/>
            </svg>
        </button>
    </div>

    <script nonce="${nonce}">
        (function() {
            const vscode = acquireVsCodeApi();
            const chatContainer = document.getElementById('chat-container');
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');
            const attachFileBtn = document.getElementById('attach-file-btn');
            const attachedFileDiv = document.getElementById('attached-file');
            const attachedFileName = document.getElementById('attached-file-name');
            const removeFileBtn = document.getElementById('remove-file-btn');
            const typingIndicator = document.getElementById('typing-indicator');

            sendButton.disabled = true;

            messageInput.addEventListener('input', function() {
                this.style.height = 'auto';
                const newHeight = Math.min(this.scrollHeight, 200);
                this.style.height = newHeight + 'px';
                
                // Enable/disable send button based on content
                sendButton.disabled = !this.value.trim();
            });

            messageInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            sendButton.addEventListener('click', sendMessage);

            attachFileBtn.addEventListener('click', function() {
                vscode.postMessage({ type: 'attachFile' });
            });

            removeFileBtn.addEventListener('click', function() {
                vscode.postMessage({ type: 'removeContext' });
            });

            function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) {
                    return;
                }

                vscode.postMessage({
                    type: 'sendMessage',
                    message: message
                });

                messageInput.value = '';
                messageInput.style.height = 'auto';
                sendButton.disabled = true;
            }

            function addMessage(message) {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + message.role;

                const header = document.createElement('div');
                header.className = 'message-header';
                header.textContent = message.role === 'user' ? 'You' : 'Backboard';
                messageDiv.appendChild(header);

                const content = document.createElement('div');
                content.className = 'message-content';
                content.innerHTML = formatMessage(message.content);
                messageDiv.appendChild(content);

                if (message.sources && message.sources.length > 0) {
                    const sourcesContainer = document.createElement('div');
                    sourcesContainer.className = 'source-files';
                    
                    message.sources.forEach(function(source) {
                        const sourceDiv = document.createElement('div');
                        sourceDiv.className = 'source-file';
                        sourceDiv.onclick = function() {
                            vscode.postMessage({
                                type: 'openFile',
                                path: source.path,
                                line: source.lineStart
                            });
                        };

                        const sourceHeader = document.createElement('div');
                        sourceHeader.className = 'source-file-header';
                        
                        const icon = document.createElement('span');
                        icon.className = 'source-file-icon';
                        icon.textContent = '[file]';
                        sourceHeader.appendChild(icon);
                        
                        const pathSpan = document.createElement('span');
                        pathSpan.textContent = source.path;
                        sourceHeader.appendChild(pathSpan);
                        
                        sourceDiv.appendChild(sourceHeader);

                        if (source.lineStart) {
                            const lines = document.createElement('div');
                            lines.className = 'source-file-lines';
                            lines.textContent = 'Lines ' + source.lineStart + '-' + (source.lineEnd || source.lineStart);
                            sourceDiv.appendChild(lines);
                        }

                        if (source.content) {
                            const code = document.createElement('div');
                            code.className = 'source-file-code';
                            code.textContent = source.content;
                            sourceDiv.appendChild(code);
                        }

                        sourcesContainer.appendChild(sourceDiv);
                    });

                    content.appendChild(sourcesContainer);
                }

                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            function formatMessage(text) {
                text = text.replace(/\\\`\\\`\\\`([\\s\\S]*?)\\\`\\\`\\\`/g, function(match, code) {
                    return '<pre><code>' + code + '</code></pre>';
                });
                text = text.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
                text = text.replace(/\`(.+?)\`/g, '<code>$1</code>');
                text = text.replace(/\\n/g, '<br>');
                return text;
            }

            window.addEventListener('message', function(event) {
                const message = event.data;
                switch (message.type) {
                    case 'addMessage':
                        addMessage(message.message);
                        break;
                    case 'showTyping':
                        typingIndicator.classList.add('show');
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                        break;
                    case 'hideTyping':
                        typingIndicator.classList.remove('show');
                        break;
                    case 'setInput':
                        messageInput.value = message.message;
                        messageInput.focus();
                        break;
                    case 'clearChat':
                        chatContainer.innerHTML = '';
                        break;
                    case 'fileAttached':
                        var displayName = message.context.fileName;
                        if (message.context.lineStart && message.context.lineEnd) {
                            displayName += ':L' + message.context.lineStart;
                            if (message.context.lineStart !== message.context.lineEnd) {
                                displayName += '-L' + message.context.lineEnd;
                            }
                        }
                        attachedFileName.textContent = displayName;
                        attachedFileDiv.style.display = 'block';
                        break;
                    case 'contextRemoved':
                        attachedFileDiv.style.display = 'none';
                        attachedFileName.textContent = '';
                        break;
                }
            });

            vscode.postMessage({ type: 'webviewReady' });
        })();
    </script>
</body>
</html>`;
  }
}
