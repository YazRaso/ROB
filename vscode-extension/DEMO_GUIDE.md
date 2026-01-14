# VS Code Extension Demo Guide

## 🎯 Complete Feature Demonstration

This guide shows you how to test every feature of the Backboard VS Code Extension.

---

## Part 1: Installation & Setup

### Step 1: Open in VS Code

```bash
cd vscode-extension
code .
```

### Step 2: Run Setup Script

```bash
./setup.sh
```

Or manually:

```bash
npm install
npm run compile
```

### Step 3: Launch Extension

- Press **F5** in VS Code
- A new "Extension Development Host" window will open
- The extension is now running!

---

## Part 2: Testing Features

### Feature 1: Open Chat (Keyboard Shortcut)

**Action:** Press `Cmd+Shift+B` (Mac) or `Ctrl+Shift+B` (Windows/Linux)

**Expected Result:**

- Backboard icon appears in Activity Bar (left sidebar)
- Chat panel opens
- Welcome message displays with features

**Screenshot Opportunity:** Clean chat interface with welcome message

---

### Feature 2: Basic Question

**Action:** Type in chat:

```
help
```

**Expected Result:**

```
I'm your Backboard Onboarding Assistant! I can help you with:

📄 Meeting Notes: Query information from Google Drive documents
🔀 Git History: Explore commits, file changes, and code evolution
💬 Team Chats: Search Telegram conversations and discussions
🔍 @source: Type @source to see exact source files

Try asking:
• "What were the main topics in last week's meeting?"
• "Show me recent commits on the drive integration"
• "What did the team discuss about deployment?"
```

---

### Feature 3: Meeting Notes Query

**Action:** Type:

```
What meetings have you seen?
```

**Expected Result:**

```
Based on the meeting notes from Google Drive, I found several important discussions:

• June 2024 meetings with Jerry and Henri covering project architecture
• Weekly standups with the team (Tina, Karan, Dexuan, Veronika)
• Latest sync from January 2026 discussing the McHacks integration

Would you like me to dive deeper into any specific meeting?
```

**Screenshot Opportunity:** Intelligent response with bullet points

---

### Feature 4: Git History Query

**Action:** Type:

```
Show me recent commits
```

**Expected Result:**

```
Looking at the Git history, I can see:

• Recent commits focused on Drive integration and Backboard API setup
• Feature branch: drive-content-extraction merged to main
• Major refactoring for code cleanup and emoji removal
• Test coverage improvements across backend components

Need details on a specific commit or file changes?
```

---

### Feature 5: Telegram Chat Query

**Action:** Type:

```
What did the team discuss?
```

**Expected Result:**

```
From Telegram conversations, the team has been discussing:

• Real-time integration patterns for the onboarding assistant
• OAuth flow improvements for Google Drive
• VS Code extension ideas (that's what we're building now!)
• Deployment strategies for the demo

Want me to pull specific messages or topics?
```

---

### Feature 6: @source Command (STAR FEATURE!)

**Action:** Type:

```
@source How does authentication work?
```

**Expected Result:**

- Response explaining sources found
- **Three clickable source file cards:**
  1. `src/backend/server.py` (Lines 67-92)
  2. `src/backend/drive_service.py` (Lines 145-167)
  3. `README.md` (Lines 1-15)
- Each card shows:
  - File icon 📄
  - Full file path
  - Line number range
  - Code snippet preview
  - Hover effect

**Action:** Click on first source file

**Expected Result:**

- File opens in VS Code editor
- Cursor jumps to line 67
- Relevant code is visible

**Screenshot Opportunity:** Source files with code snippets displayed

---

### Feature 7: Quick Ask (Keyboard Shortcut #2)

**Action:** Press `Cmd+Shift+A` (Mac) or `Ctrl+Shift+A` (Windows/Linux)

**Expected Result:**

- Input popup appears at top of screen
- Placeholder: "Ask your onboarding assistant anything..."

**Action:** Type:

```
Tell me about the project
```

**Expected Result:**

- Chat sidebar auto-opens
- Question appears in chat
- Response is generated

**Screenshot Opportunity:** Quick Ask popup

---

### Feature 8: Clear Chat

**Action:**

- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
- Type: "Backboard: Clear Chat History"
- Press Enter

**Expected Result:**

- Chat clears
- Welcome message re-appears
- Notification: "Chat history cleared!"

---

### Feature 9: Typing Indicator

**Action:** Ask any question and watch carefully

**Expected Result:**

- Three animated dots appear while processing
- Dots pulse with smooth animation
- Disappear when response arrives

**Screenshot Opportunity:** Typing indicator in action

---

### Feature 10: Message Formatting

**Action:** The mock responses automatically use formatting. Notice:

**Bold text:** `**Meeting Notes**` renders as **Meeting Notes**
**Code:** Inline code uses monospace font
**Line breaks:** Multi-line responses format nicely

---

## Part 3: Visual Features

### Theme Integration

**Test:** Try different VS Code themes

**Action:**

- `Cmd+K Cmd+T` → Select "Dark+ (default dark)"
- `Cmd+K Cmd+T` → Select "Light+ (default light)"

**Expected Result:**

- Chat colors adapt to theme
- Always readable
- Beautiful gradients on buttons

---

### Animation & Polish

**Observe:**

- Messages slide in smoothly (0.2s animation)
- Typing dots pulse rhythmically
- Source files highlight on hover
- Send button changes on hover

---

## Part 4: Configuration

### Settings

**Action:** Open VS Code Settings (`Cmd+,`)

**Search:** "backboard"

**Available Settings:**

```json
{
  "backboard.apiUrl": "http://localhost:8000",
  "backboard.clientId": "vscode_user",
  "backboard.enableSourceLinks": true
}
```

**Test:** Change `clientId` to `"test_user"` and verify it's used

---

## Part 5: Advanced Testing

### Test Conversation Flow

**Action:** Have a multi-turn conversation:

1. `What meetings have you seen?`
2. `What about git commits?`
3. `@source Show me the code`

**Expected:** All messages persist, smooth scrolling

---

### Test Edge Cases

**Test 1:** Empty message

- **Action:** Try to send empty message
- **Expected:** Nothing happens

**Test 2:** Long message

- **Action:** Type a very long question (200+ words)
- **Expected:** Text area expands (max 120px), scrolls if needed

**Test 3:** Special characters

- **Action:** Type: `What about @#$%^&* characters?`
- **Expected:** Handled gracefully

---

## Part 6: Demo Script

### For Live Presentation:

**Opening (30 seconds):**

> "We've built a VS Code extension that brings your team's knowledge directly into your editor. Let me show you."

**Demo (2 minutes):**

1. **Press `Cmd+Shift+B`**

   > "Quick access with a keyboard shortcut opens our chat interface."

2. **Type: `help`**

   > "The assistant knows about Drive docs, Git history, and Telegram chats."

3. **Type: `What meetings have you seen?`**

   > "It can recall meetings from months ago with specific details."

4. **Type: `@source How does authentication work?`**
   > "Here's the magic: @source shows you the EXACT code files. Click any file..."
5. **Click source file**

   > "And we jump right to the implementation. No searching, instant context."

6. **Press `Cmd+Shift+A`**
   > "Quick questions without leaving your workflow."

**Closing (15 seconds):**

> "This is how we're making onboarding seamless - knowledge at your fingertips, right where you code."

---

## 🎬 Video Recording Checklist

For demo videos:

- [ ] Clean VS Code theme (Dark+ recommended)
- [ ] Hide personal info from titlebar
- [ ] Zoom in for readability (Cmd+= multiple times)
- [ ] Slow down mouse movements
- [ ] Pause after each action (2 seconds)
- [ ] Record terminal commands with clear output
- [ ] Show keyboard shortcuts on screen (KeyCastr for Mac)

---

## 📸 Screenshot List

Capture these for documentation:

1. Welcome screen with chat open
2. Basic question + response
3. @source response with 3 file cards
4. Clicked source file showing code
5. Quick Ask popup
6. Extension in Activity Bar
7. Settings page
8. Typing indicator
9. Multiple messages in conversation
10. Different VS Code theme integration

---

## 🚀 Next Steps After Demo

1. Connect to real Backboard API (replace mocks in `backboardService.ts`)
2. Add authentication
3. Implement real @source file fetching
4. Add more commands
5. Package for marketplace

---

## Troubleshooting

**Extension doesn't show:**

- Ensure you pressed F5
- Check for compilation errors
- Restart Extension Development Host

**Chat doesn't open:**

- Try Command Palette → "Backboard: Open Chat"
- Check console for errors (Help → Toggle Developer Tools)

**Source files don't open:**

- Ensure you have the workspace open
- Files must exist in workspace

---

Built for McHacks 2026 🏆
