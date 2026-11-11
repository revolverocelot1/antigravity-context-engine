---
name: compact
description: Compact and synchronize working memory with instant DO NOT RE-READ cache and accepted state lock without losing context. Triggered by /compact or /sync.
---

# /compact — Working Memory Sync & Lock

Forces an immediate local snapshot of all files and accepted turns, injecting the DO NOT RE-READ cache and accepted continuity anchor into working memory.

## Syntax
- `/compact` — Synchronizes and locks working memory immediately
- `/compact <instruction>` — Synchronizes context and executes your prompt in one turn

## Why Use /compact Instead of Built-in Compacting?
- Built-in compacting can sometimes summarize away critical details or trigger cold-start refusals.
- Context Engine's `/compact` operates 100% locally: it caches exact file digests and verbatim accepted turns, guaranteeing that the model doesn't re-read files or refuse ongoing creative/technical work.

> [!TIP]
> Both slash command syntax (`/compact`) and dot command syntax (`.compact` / `.sync`) work identically.
