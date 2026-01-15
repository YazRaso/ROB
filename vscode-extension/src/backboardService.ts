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
  sourceType: "telegram" | "drive" | "git" | "unknown";
  sourceLabel: string;
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
    const apiUrl = config.get<string>("apiUrl", "http://localhost:8000");
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
      // Handle both array format [response, sources] and potential object format
      let content: string;
      let sources: string[] = [];

      if (Array.isArray(response.data)) {
        [content, sources] = response.data;
      } else if (typeof response.data === "object" && response.data !== null) {
        content =
          response.data.response ||
          response.data.content ||
          JSON.stringify(response.data);
        sources = response.data.sources || [];
      } else {
        content = String(response.data || "No response received");
      }

      // Ensure content is not empty
      if (!content || content.trim() === "") {
        content =
          "I received your message but couldn't generate a response. Please try again.";
      }

      // Convert sources to SourceFile format with proper source identification
      const sourceFiles: SourceFile[] =
        sources?.map((source: string) => this.parseSource(source)) || [];

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
    // Strip @source from the message and query the backend
    const cleanedMessage = message.replace(/@source/gi, "").trim();

    // If there's no actual query after removing @source, ask for clarification
    if (!cleanedMessage) {
      return {
        role: "assistant",
        content:
          "Please specify what you'd like to find sources for. For example: `@source how does authentication work?`",
        timestamp: Date.now(),
      };
    }

    // Query the backend - sources will be included in the response
    return this.queryBackend(cleanedMessage);
  }

  /**
   * Parse a source string and identify its type (Telegram, Drive, or Git)
   */
  private parseSource(source: string): SourceFile {
    const lowerSource = source.toLowerCase();
    
    // Check for Telegram chat patterns
    if (
      lowerSource.includes("telegram") ||
      /\[\w+\s+\d+,\s*\d+:\d+\]/.test(source) || // [Jan 15, 21:05] pattern
      source.includes("@") && (source.includes("Jack") || source.includes("Karan") || source.includes("Eldiiar") || source.includes("Yazdan"))
    ) {
      // Extract date from Telegram message if present
      const dateMatch = source.match(/\[(\w+\s+\d+),\s*(\d+:\d+)\]/);
      const dateLabel = dateMatch ? `${dateMatch[1]} at ${dateMatch[2]}` : "";
      
      return {
        path: "telegram.txt",
        sourceType: "telegram",
        sourceLabel: dateLabel ? `💬 Telegram Chat - ${dateLabel}` : "💬 Telegram Chat History",
        content: source,
      };
    }
    
    // Check for Git commit patterns
    if (
      lowerSource.includes("git") ||
      lowerSource.includes("commit") ||
      /^[a-f0-9]{7,40}\s/.test(source) || // Commit hash pattern
      source.includes("GIT COMMIT HISTORY") ||
      /^\w+:\s*(add|fix|update|remove|implement|merge)/i.test(source) // Commit message pattern
    ) {
      // Try to extract commit hash and author
      const commitMatch = source.match(/^([a-f0-9]{7,40})\s+(\w+):/);
      const commitLabel = commitMatch 
        ? `${commitMatch[1].substring(0, 7)} by ${commitMatch[2]}`
        : "";
      
      return {
        path: "git.txt",
        sourceType: "git",
        sourceLabel: commitLabel ? `📝 Git Commit - ${commitLabel}` : "📝 Git Repository History",
        content: source,
      };
    }
    
    // Check for Google Drive document patterns
    if (
      lowerSource.includes("google drive") ||
      lowerSource.includes("drive") ||
      lowerSource.includes("adr") ||
      lowerSource.includes("rfc") ||
      lowerSource.includes("memo") ||
      lowerSource.includes("meeting notes") ||
      lowerSource.includes("post-mortem") ||
      lowerSource.includes("postmortem") ||
      lowerSource.includes("security audit") ||
      lowerSource.includes("legal compliance") ||
      lowerSource.includes("gdpr") ||
      source.includes("Document:") ||
      source.includes("Title:") ||
      source.includes("Author:") ||
      source.includes("Status: ACCEPTED")
    ) {
      // Try to extract document title
      let docTitle = "";
      const titleMatch = source.match(/(?:Title:|Document:)\s*(.+?)(?:\n|$)/i);
      if (titleMatch) {
        docTitle = titleMatch[1].trim();
      } else if (lowerSource.includes("adr")) {
        const adrMatch = source.match(/ADR[-\s]?\d+[:\s]+(.+?)(?:\n|$)/i);
        docTitle = adrMatch ? adrMatch[0].trim() : "ADR Document";
      } else if (lowerSource.includes("post-mortem") || lowerSource.includes("postmortem")) {
        const pmMatch = source.match(/PM-\d+-\d+/i);
        docTitle = pmMatch ? `Post-Mortem ${pmMatch[0]}` : "Post-Mortem";
      } else if (lowerSource.includes("meeting")) {
        docTitle = "Meeting Notes";
      } else if (lowerSource.includes("memo")) {
        docTitle = "Team Memo";
      }
      
      return {
        path: "drive.txt",
        sourceType: "drive",
        sourceLabel: docTitle ? `📄 Google Drive - ${docTitle}` : "📄 Google Drive Document",
        content: source,
      };
    }
    
    // Default: unknown source
    return {
      path: "memory",
      sourceType: "unknown",
      sourceLabel: "📎 Retrieved Context",
      content: source,
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
