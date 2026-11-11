---
name: save
description: Snapshot and pin the current chat context (working memory, cached files, accepted turns) so you can resume after restarting Antigravity or carry into another chat. Triggered by /save or .save.
---

# /save — Context Snapshot & Memory Pin

Snapshot the current conversation's working state to local cache so you never lose context across app restarts, model switches (such as Argon), or when starting new chats.

## Syntax
- `/save` — Auto-saves and pins this chat with default tag `chat-<shortId>`
- `/save <tag>` — Saves and pins this chat with a custom memorable tag (e.g., `/save story`, `/save refactor`)
- `/save <tag> <instruction>` — Saves the snapshot and immediately executes your instruction

## What Happens When You Run /save
1. **Zero-API Overhead**: Reads only local transcript history — makes zero external API calls.
2. **File Working Memory Cache**: All files read or edited during this session are cached (up to 4,000 characters each).
3. **Accepted Persona & Momentum Anchor**: The last 6 accepted User and Assistant turns are anchored verbatim (all refusals and error stops are stripped).
4. **Auto-Restore on Resume**: If you restart Antigravity, switch models, or continue chatting in this same chat, the context is automatically reinjected with the DO NOT RE-READ lock.
5. **Cross-Chat Ready**: You can instantly pull this state into any new chat using `/carry <tag>` or `/carry 1`.

> [!TIP]
> Both slash command syntax (`/save`) and dot command syntax (`.save`) work identically.
