import axios, { AxiosInstance } from "axios";
import * as vscode from "vscode";

export interface ChatMessage {

  role: "user" | "assistant";
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
  lineStart?: number;
  lineEnd?: number;
}

export class BackboardService {
  private apiClient: AxiosInstance;
  private clientId: string;

  constructor() {
    const config = vscode.workspace.getConfiguration("backboard");
    const apiUrl = config.get<string>(
      "apiUrl",
      "https://rob-production.up.railway.app/"
    );
    this.clientId = config.get<string>("clientId", "vscode_user");

    this.apiClient = axios.create({
      baseURL: apiUrl,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }

  async sendMessage(
    message: string,
    context?: FileContext
  ): Promise<ChatMessage> {
    if (message.includes("@source")) {
      return this.handleSourceRequest(message);
    }

    return this.queryBackend(message, context);
  }

  private async queryBackend(
    message: string,
    context?: FileContext
  ): Promise<ChatMessage> {
    try {
      // Build the query with optional context
      let fullMessage = message;
      if (context) {
        const contextInfo =
          context.lineStart && context.lineEnd
            ? `[Context from ${context.fileName} lines ${context.lineStart}-${context.lineEnd}]:\n${context.content}\n\n`
            : `[Context from ${context.fileName}]:\n${context.content}\n\n`;
        fullMessage = contextInfo + message;
      }

      // Call the backend /messages/query endpoint which returns (response, sources)
      const response = await this.apiClient.post("/messages/query", null, {
        params: {
          client_id: this.clientId,
          content: fullMessage,
        },
      });

      // Backend returns a tuple [response, sources]
      const [content, sources] = response.data;

      // Convert sources to SourceFile format if available
      const sourceFiles: SourceFile[] =
        sources?.map((source: string) => ({
          path: "memory",
          content: source,
        })) || [];

      return {
        role: "assistant",
        content: content,
        timestamp: Date.now(),
        sources: sourceFiles.length > 0 ? sourceFiles : undefined,
      };
    } catch (error: any) {
      console.error("Backend query failed:", error);

      // Return a helpful error message
      const errorMessage =
        error.response?.status === 404
          ? "Client not found. Please check your configuration in VS Code settings."
          : `Failed to connect to the backend. Make sure the server is running.\n\nError: ${error.message}`;

      return {
        role: "assistant",
        content: errorMessage,
        timestamp: Date.now(),
      };
    }
  }

  private async handleSourceRequest(message: string): Promise<ChatMessage> {
    await new Promise((resolve) => setTimeout(resolve, 800));

    const mockSources: SourceFile[] = [
      {
        path: "src/backend/server.py",
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
    
    return "".join(output)`,
      },
      {
        path: "src/backend/drive_service.py",
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
        )`,
      },
      {
        path: "README.md",
        lineStart: 1,
        lineEnd: 15,
        content: `# McHacks Onboarding Assistant

An intelligent onboarding assistant that integrates with:
- Google Drive (meeting notes, documentation)
- Git repositories (code history, changes)
- Telegram (team conversations)

All data is fed into the Backboard API for intelligent query answering.

## Features

- Real-time document monitoring with change detection
- OAuth2 authentication for Google Drive
- Automated polling for document updates
- AI-powered question answering`,
      },
    ];

    const cleanedMessage = message.replace("@source", "").trim();
    const response = `Here are the source files related to "${cleanedMessage}":

I found ${mockSources.length} relevant source files. Click on any file below to view the code.`;

    return {
      role: "assistant",
      content: response,
      timestamp: Date.now(),
      sources: mockSources,
    };
  }

  async checkConnection(): Promise<boolean> {
    try {
      const response = await this.apiClient.get("/");
      return response.data.status === "ok";
    } catch (error) {
      console.error("Connection check failed:", error);
      return false;
    }
  }
}
