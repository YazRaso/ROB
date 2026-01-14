import * as vscode from "vscode";
import { ChatViewProvider } from "./chatViewProvider";
import { BackboardService } from "./backboardService";

export function activate(context: vscode.ExtensionContext) {
  const backboardService = new BackboardService();
  const chatProvider = new ChatViewProvider(
    context.extensionUri,
    backboardService
  );

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(
      "backboard.chatView",
      chatProvider
    )
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("backboard.openChat", () => {
      vscode.commands.executeCommand(
        "workbench.view.extension.backboard-sidebar"
      );
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("backboard.askQuestion", async () => {
      const question = await vscode.window.showInputBox({
        placeHolder: "Ask your onboarding assistant anything...",
        prompt: "Type your question or use @source to see source files",
      });

      if (question) {
        chatProvider.sendMessageFromCommand(question);
        vscode.commands.executeCommand(
          "workbench.view.extension.backboard-sidebar"
        );
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("backboard.clearChat", () => {
      chatProvider.clearChat();
    })
  );
}

export function deactivate() {}
