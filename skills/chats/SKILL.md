---
name: chats
description: Display a table of all indexed chat snapshots, showing row numbers, short IDs, tags, workspace names, cached file counts, and carry shortcuts. Triggered by /chats or .chats.
---

# /chats — Saved Chat Snapshot Index

Lists all indexed conversation snapshots in an interactive Markdown table directly in your chat.

## Syntax
- `/chats` — Shows all available snapshots, row numbers (#1, #2...), tags, file counts, and carry shortcuts.

## Example Output
```markdown
| # | Short ID | Tag | Workspace | Cached Files | Last Model | Preview |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- |
| **1** | `fd4cfb71` 📌 | **`story`** | `story-workspace` | 2 files | `gemini-4-argon` | Write chapter 1 in chapter1.md |
| **2** | `8e3a104c` | — | `project-refactor` | 5 files | `gemini-3-flash` | Refactor auth middleware |
```

To carry any row into your current chat, simply type `/carry 1` or `/carry story`.

> [!TIP]
> Both slash command syntax (`/chats`) and dot command syntax (`.chats`) work identically.
