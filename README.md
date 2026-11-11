# antigravity-context-engine

Local context indexer, Argon anti-reread lock, and cross-chat continuity engine for Antigravity.

Solves three major headaches in Antigravity:
1. **Model Switches (Especially to Argon):** When you switch models mid-chat, the new model normally re-reads every file from scratch because older tool outputs were truncated. This plugin caches file digests after every turn and locks the new model against redundant `read_file` calls.
2. **Post-Restart & Post-Compaction Refusals:** Built-in `/compact` sends your chat to a cloud summarizer that can refuse on dark/creative writing or strip out your established tone, causing the model to suddenly refuse requests it accepted earlier. This plugin indexes `transcript_full.jsonl` **100% locally in Python** (zero API calls, never refuses) and restores the last accepted turns verbatim.
3. **Cross-Chat Handoff (`.chats`, `.save`, `.carry`):** Move your cached files and accepted session state from Old Chat A into a fresh Chat B by number (`.carry 1`), tag (`.carry story`), or short ID (`.carry fd4cfb71`), with an inline UI banner confirming the exact source and destination chat.

---

## Compatibility

- **Antigravity:** 2.0+ (uses `PreInvocation` `metadata.user_markdown` and `Stop` lifecycle hooks).
- **Python:** 3.8+ (standard library only, zero external dependencies).
- **Platform:** Windows, macOS, Linux.
- **Safety Invariant:** 100% read-only on `transcript.jsonl` / `transcript_full.jsonl`. Stores snapshots in `~/.gemini/context_store/`.

---

## Install

Paste this into any Antigravity chat:

```
Clone https://github.com/revolverocelot1/antigravity-context-engine into:
- Windows: %USERPROFILE%\.gemini\config\plugins\antigravity-context-engine
- Mac/Linux: ~/.gemini/config/plugins/antigravity-context-engine

Then run python test_context_engine.py and confirm all 12 tests pass.
```

Or manually:

```bash
# Windows (PowerShell)
git clone https://github.com/revolverocelot1/antigravity-context-engine "$env:USERPROFILE\.gemini\config\plugins\antigravity-context-engine"

# Mac/Linux
git clone https://github.com/revolverocelot1/antigravity-context-engine ~/.gemini/config/plugins/antigravity-context-engine
```

---

## Workflow & Commands

### 1. Inside the Same Chat (Automatic)
You don't need to type any command when staying in the same chat:
- **Switch model dropdown (e.g., to Argon):** Automatically detects `modelName` changed and injects this chat's cached file digests + accepted continuity state on your next message.
- **Reopen Antigravity (>10m gap):** Automatically restores this chat's snapshot on resume.
- **Force local refresh anytime:** Type `.sync` (or `.compact`) at the start of your message.

### 2. Carrying Context From Chat A ➔ New Chat B
Every time context is carried or synced, Antigravity displays a visual banner right in the chat UI showing **Source Chat (`short_id` / `tag`) ➔ Current Chat** and how many cached files were loaded.

| Command | Where to Type It | What It Does |
| :--- | :--- | :--- |
| **`.chats`** *(or `.carry ?`)* | Any Chat | Prints a numbered table in the chat UI showing your recent saved chats (`#1`, `#2`...), their Short ID, Tag, Workspace, File Count, and a 1-line preview. |
| **`.carry 1`** | New Chat B | Carries context from row `#1` of the `.chats` table into the current chat. (Can include instructions: `.carry 1 now write chapter 3`). |
| **`.save <tag>`** | Old Chat A | Pins the current chat under a friendly name (e.g. `.save story` or `.save upscaler`). |
| **`.carry <tag>`** | New Chat B | Carries context from the chat saved as `<tag>` (e.g. `.carry story`). |
| **`.carry <id>`** | New Chat B | Carries context by conversation ID prefix (e.g. `.carry fd4cfb71`). |
| **`.carry`** *(no args)* | New Chat B | Automatically pulls from the last `.save`-pinned chat, or the most recent chat from the **same workspace folder**. |

---

## Verify

```bash
python test_context_engine.py
```

Runs 12 automated test cases verifying read-only transcript parsing, refusal stripping, Argon model-switch detection, restart gap detection, `.chats`, `.save`, `.carry`, and `.sync`.

---

## Files

```
antigravity-context-engine/
├── plugin.json             # Manifest (v1.0.0)
├── hooks.json              # PreInvocation & Stop hook definitions
├── context_engine.py       # Local transcript indexer, store manager, & payload builder
├── context_pre.py          # PreInvocation handler (auto-sync + .chats/.save/.carry/.sync)
├── context_stop.py         # Stop handler (updates snapshot after every turn)
├── test_context_engine.py  # 12 automated tests
└── README.md
```
