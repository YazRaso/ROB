import axios, { AxiosInstance } from 'axios';
import * as vscode from 'vscode';

export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
    sources?: SourceFile[];
    context?: FileContext;
}

export interface SourceFile {
    path: string;
    lineStart?: number;
    lineEnd?: number;
    content?: string;
}

export interface FileContext {
    fileName: string;
    filePath: string;
    content: string;
}

export class BackboardService {
    private apiClient: AxiosInstance;
    private clientId: string;

    constructor() {
        const config = vscode.workspace.getConfiguration('backboard');
        const apiUrl = config.get<string>('apiUrl', 'http://localhost:8000');
        this.clientId = config.get<string>('clientId', 'vscode_user');

        this.apiClient = axios.create({
            baseURL: apiUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    async sendMessage(message: string, context?: FileContext): Promise<ChatMessage> {
        if (message.includes('@source')) {
            return this.handleSourceRequest(message);
        }

        return this.getMockResponse(message, context);
    }

    private async getMockResponse(message: string, context?: FileContext): Promise<ChatMessage> {
        await new Promise(resolve => setTimeout(resolve, 1000));

        let response = '';
        
        if (context) {
            response = `I can see you've attached **${context.fileName}** (${Math.round(context.content.length / 1024)}KB).\n\n`;
        }
        
        if (message.toLowerCase().includes('meeting') || message.toLowerCase().includes('notes')) {
            response = `Based on the meeting notes from Google Drive, I found several important discussions:

• June 2024 meetings with Jerry and Henri covering project architecture
• Weekly standups with the team (Tina, Karan, Dexuan, Veronika)
• Latest sync from January 2026 discussing the McHacks integration

Would you like me to dive deeper into any specific meeting?`;
        } else if (message.toLowerCase().includes('git') || message.toLowerCase().includes('commit')) {
            response = `Looking at the Git history, I can see:

• Recent commits focused on Drive integration and Backboard API setup
• Feature branch: drive-content-extraction merged to main
• Major refactoring for code cleanup and emoji removal
• Test coverage improvements across backend components

Need details on a specific commit or file changes?`;
        } else if (message.toLowerCase().includes('telegram') || message.toLowerCase().includes('chat')) {
            response = `From Telegram conversations, the team has been discussing:

• Real-time integration patterns for the onboarding assistant
• OAuth flow improvements for Google Drive
• VS Code extension ideas (that's what we're building now!)
• Deployment strategies for the demo

Want me to pull specific messages or topics?`;
        } else if (message.toLowerCase().includes('help') || message.toLowerCase().includes('what can you')) {
            response = `I'm your Backboard Onboarding Assistant! I can help you with:

📄 **Meeting Notes**: Query information from Google Drive documents
🔀 **Git History**: Explore commits, file changes, and code evolution  
💬 **Team Chats**: Search Telegram conversations and discussions
🔍 **@source**: Type @source to see exact source files and line numbers

Try asking:
• "What were the main topics in last week's meeting?"
• "Show me recent commits on the drive integration"
• "What did the team discuss about deployment?"`;
        } else {
            response = `I understand you're asking about: "${message}"

Based on the connected data sources (Drive docs, Git history, Telegram), here's what I found:

This is a mock response for testing. The actual Backboard API will provide intelligent answers based on your team's documentation, code changes, and conversations.

**Tip**: Use @source in your question to see the exact source files I'm referencing!`;
        }

        return {
            role: 'assistant',
            content: response,
            timestamp: Date.now()
        };
    }

    private async handleSourceRequest(message: string): Promise<ChatMessage> {
        await new Promise(resolve => setTimeout(resolve, 800));

        const mockSources: SourceFile[] = [
            {
                path: 'src/backend/server.py',
                lineStart: 67,
                lineEnd: 92,
                content: `@app.post("/messages/send")
async def add_thread(client_id: str, content: str, status_code=201):
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")
    
    decrypted_api_key = encryption.decrypt_api_key(client["api_key"])
    backboard_client = BackboardClient(api_key=decrypted_api_key)
    
    assistant = db.lookup_assistant(client_id)
    if not assistant:
        raise HTTPException(status_code=404, detail="No assistant found!")
    
    assistant_id = assistant["assistant_id"]
    thread = await backboard_client.create_thread(assistant_id)
    
    output = []
    async for chunk in await backboard_client.add_message(
        thread_id=thread.thread_id,
        content=content,
        memory="Auto",
        stream=True,
    ):
        if chunk["type"] == "content_streaming":
            output.append(chunk["content"])
    
    return "".join(output)`
            },
            {
                path: 'src/backend/drive_service.py',
                lineStart: 145,
                lineEnd: 167,
                content: `async def process_document(self, file_id: str, client_id: str):
    try:
        content = self.get_document_content(file_id)
        
        client = db.lookup_client(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        decrypted_api_key = encryption.decrypt_api_key(client["api_key"])
        backboard_client = BackboardClient(api_key=decrypted_api_key)
        
        assistant = db.lookup_assistant(client_id)
        if not assistant:
            raise ValueError(f"No assistant found for client {client_id}")
        
        assistant_id = assistant["assistant_id"]
        
        await backboard_client.upload_document_to_assistant(
            assistant_id=assistant_id,
            file_path=temp_file_path,
            file_name=filename
        )`
            },
            {
                path: 'README.md',
                lineStart: 1,
                lineEnd: 15,
                content: `# McHacks Onboarding Assistant

An intelligent onboarding assistant that integrates with:
- 📄 Google Drive (meeting notes, documentation)
- 🔀 Git repositories (code history, changes)
- 💬 Telegram (team conversations)

All data is fed into the Backboard API for intelligent query answering.

## Features

- Real-time document monitoring with change detection
- OAuth2 authentication for Google Drive
- Automated polling for document updates
- AI-powered question answering`
            }
        ];

        const cleanedMessage = message.replace('@source', '').trim();
        const response = `Here are the source files related to "${cleanedMessage}":

I found ${mockSources.length} relevant source files. Click on any file below to view the code.`;

        return {
            role: 'assistant',
            content: response,
            timestamp: Date.now(),
            sources: mockSources
        };
    }

    async checkConnection(): Promise<boolean> {
        try {
            const response = await this.apiClient.get('/');
            return response.data.status === 'ok';
        } catch (error) {
            console.error('Connection check failed:', error);
            return false;
        }
    }
}
