---
name: context
description: Context Engine command guide and status overview for working memory persistence, anti-reread caching, and cross-chat carry forward. Triggered by /context or /help.
---

# /context — Context Engine Quick Guide

Command reference and documentation for the Antigravity Context Engine.

## Commands Overview

| Slash Command | Dot Command | Arguments | Description |
| :--- | :--- | :--- | :--- |
| **`/save`** | `.save` | `[tag] [instruction]` | Snapshots and pins working state. Auto-restores in this chat on next message or restart. |
| **`/carry`** | `.carry` | `[target] [instruction]` | Pulls saved context into current chat (by `#1`, tag, or chat ID) with DO NOT RE-READ lock. |
| **`/chats`** | `.chats` | *none* | Displays a table of all saved snapshots, tags, and carry numbers. |
| **`/compact`** | `.compact` | `[instruction]` | Manually syncs and locks file cache and accepted turns. |
| **`/context`** | `.context` | *none* | Displays this command guide. |

## Key Capabilities
- **Survives App Restarts**: Detects host process PID changes instantly — reopening Antigravity auto-restores your saved state.
- **Argon Model Switch Defense**: Model changes automatically inject the DO NOT RE-READ lock, saving API calls.
- **Accepted Persona Lock**: Prior accepted turns are re-anchored verbatim, preventing cold-start refusals.
- **Zero Cloud API Usage**: 100% local JSON files in `~/.gemini/jetski/context_store/`.
