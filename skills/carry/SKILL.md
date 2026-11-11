---
name: carry
description: Carry forward saved context from a previous chat or snapshot into this session without re-reading files or cold-start refusals. Triggered by /carry or .carry.
---

# /carry — Cross-Chat Continuity & Anti-Reread Lock

Carries forward full cached context from a previous chat or pinned snapshot into your current session.

## Syntax
- `/carry` — Carries forward the last pinned snapshot or the most recent chat from the current workspace
- `/carry 1` (or `#1`) — Carries forward snapshot #1 from the `/chats` table
- `/carry <tag>` — Carries forward snapshot by tag name (e.g., `/carry story`)
- `/carry <shortId>` — Carries forward snapshot by 8-character chat ID (e.g., `/carry fd4cfb71`)
- `/carry <target> <instruction>` — Carries forward context and immediately executes your prompt in one turn

## What Happens When You Run /carry
1. **DO NOT RE-READ Lock**: Injects cached file contents directly into working memory so the model never spends API calls or time re-reading files with `read_file`.
2. **Accepted Continuity Anchor**: Injects accepted turns to anchor the model's persona, writing style, and project parameters without re-litigating or refusing the work.
3. **Session Linking**: Links the current conversation to the source conversation so future saves maintain the lineage.

> [!TIP]
> Both slash command syntax (`/carry`) and dot command syntax (`.carry`) work identically.
