# Testing Guide

## Steps to Test the Extension

### 1. **Restart the Extension Development Host**

- If it's running, stop it (close the Extension Development Host window)
- In the main VS Code window (with vscode-extension folder open), press **F5**
- A new "Extension Development Host" window will open

### 2. **Open Debug Console**

- In the **Extension Development Host** window:
- **Help** → **Toggle Developer Tools**
- Click the **Console** tab
- Keep this open to see logs

### 3. **Test Chat Sidebar**

- Press **Cmd+Shift+B** (Mac) or **Ctrl+Shift+B** (Win/Linux)
- The Backboard chat sidebar should open

**Expected in Console:**

```
Backboard Assistant is now active!
Webview is ready, sending welcome message
```

### 4. **Test Sending a Message**

- Type in the chat input: `hello`
- Click the **Send** button

**Expected in Console:**

```
Send button clicked, message: hello
Posting message to extension
Received message from webview: {type: 'sendMessage', message: 'hello'}
Handling user message: hello
Sending user message to webview
Showing typing indicator
Getting response from backboard service
Got response: [object Object]
```

**Expected in Chat:**

- Your message "hello" appears
- Typing indicator shows (3 dots)
- Response appears

### 5. **Test Quick Question (Cmd+Shift+A)**

- Press **Cmd+Shift+A** (Mac) or **Ctrl+Shift+A** (Win/Linux)
- A popup input should appear at top of window
- Type: `test question`
- Press Enter

**Expected:**

- Chat sidebar opens automatically
- Your question appears in the input box
- You can click Send or press Enter

### 6. **Test @source Command**

- In chat, type: `@source authentication`
- Click Send

**Expected:**

- Response with 3 source file cards
- Each card shows file name, line numbers, code snippet
- Cards are clickable (though files may not exist in this workspace)

## What to Check

### ✅ Working Correctly If:

- [x] Console shows "Webview is ready"
- [x] Console shows "Send button clicked" when you click Send
- [x] Messages appear in chat
- [x] Typing indicator shows
- [x] Responses come back
- [x] Cmd+Shift+A opens popup
- [x] @source shows file cards

### ❌ Still Broken If:

- [ ] No "Webview is ready" message
- [ ] Click Send but nothing happens
- [ ] No console logs when clicking Send
- [ ] Cmd+Shift+A doesn't work

## Common Issues

### If Send Button Still Doesn't Work:

1. Check console for JavaScript errors (red text)
2. Try typing and pressing **Enter** instead of clicking
3. Check if the button is visible (scroll down in sidebar)

### If Quick Question Doesn't Work:

1. Make sure you're pressing the shortcut in the Extension Development Host, not the main window
2. Check **Preferences** → **Keyboard Shortcuts**, search for "backboard.askQuestion"

### If Nothing Shows in Console:

1. Make sure you opened Developer Tools in the **Extension Development Host** window
2. Try clicking the Console tab (not Sources or Network)
3. Filter by "backboard" or "webview"

## Test Messages

Try these messages to see different responses:

```
help
What meetings have you seen?
Show me recent commits
@source How does authentication work?
```

## Success Criteria

The extension is working if you can:

1. ✅ Open chat with Cmd+Shift+B
2. ✅ Type a message and click Send
3. ✅ See your message and a response
4. ✅ See typing indicator
5. ✅ Use Cmd+Shift+A to quickly ask
6. ✅ Use @source to see file cards
