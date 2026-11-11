# antigravity-context-engine

Local context indexer, Argon anti-reread lock, and cross-chat continuity engine for Antigravity.

Solves three major headaches in Antigravity:
1. **Model Switches (Especially to Argon):** When you switch models mid-chat, the new model normally re-reads every file from scratch because older tool outputs were truncated. This plugin caches file digests after every turn and locks the new model against redundant `read_file` calls.
2. **Post-Restart & Post-Compaction Refusals:** Built-in `/compact` sends your chat to a cloud summarizer that can refuse on dark/creative writing or strip out your established tone, causing the model to suddenly refuse requests it accepted earlier. This plugin indexes `transcript_full.jsonl` **100% locally in Python** (zero API calls, never refuses) and restores the last accepted turns verbatim.
3. **Cross-Chat & Same-Chat Continuity (`/save`, `/carry`, `/chats`):** Move your cached files and accepted session state from Chat A into Chat B or resume your current chat after restarting Antigravity by number (`/carry 1`), tag (`/carry story`), or short ID (`/carry fd4cfb71`), with an inline UI banner confirming the exact source and destination chat.

---

## Slash Commands & Skills Autocomplete

The plugin ships native Antigravity Skills (`skills/`) so typing `/` in the chat bar displays the commands and their descriptions in the autocomplete menu:

| Slash Command | Dot Alias | Arguments | What It Does |
| :--- | :--- | :--- | :--- |
| **`/save`** | `.save` | `[tag] [instruction]` | Snapshots and pins the current chat. Auto-restores in the same chat on restart, or allows carrying into new chats. |
| **`/carry`** | `.carry` | `[target] [instruction]` | Pulls saved context into the current chat (by `#1`, tag, or chat ID) with DO NOT RE-READ lock. |
| **`/chats`** | `.chats` | *none* | Displays a table of all saved snapshots, tags, cached file counts, and carry shortcuts. |
| **`/compact`** | `.compact` | `[instruction]` | Manually syncs and locks working memory without cloud summarization or refusals. |
| **`/context`** | `.context` | *none* | Displays the interactive command guide and status overview. |

> [!TIP]
> **Both `/` and `.` prefixes are 100% supported.** You can type `/save` or `.save`, `/carry` or `.carry`, `/chats` or `.chats`.

---

## Compatibility

- **Antigravity:** 2.0+ (uses `PreInvocation` `metadata.user_markdown` and `Stop` lifecycle hooks + Skills autocomplete).
- **Python:** 3.8+ (standard library only, zero external dependencies).
- **Platform:** Windows, macOS, Linux.
- **Safety Invariant:** 100% read-only on `transcript.jsonl` / `transcript_full.jsonl`. Stores snapshots in `~/.gemini/context_store/`.

---

## Install

Paste this into any Antigravity chat:

```
Clone https://github.com/revolverocelot1/antigravity-context-engine into:
- Windows: %USERPROFILE%\.gemini\config\plugins\antigravity-context-engine
- Mac/Linux: ~/.gemini/config/plugins\antigravity-context-engine

Then run python test_context_engine.py and confirm all 16 tests pass.
```

Or manually:

```bash
# Windows (PowerShell)
git clone https://github.com/revolverocelot1/antigravity-context-engine "$env:USERPROFILE\.gemini\config\plugins\antigravity-context-engine"

# Mac/Linux
git clone https://github.com/revolverocelot1/antigravity-context-engine ~/.gemini/config/plugins/antigravity-context-engine
```

---

## Workflow & Examples

### 1. Same-Chat Resume (Zero Context Loss After Restart)
1. Type `/save` (or `/save story`) before closing Antigravity or switching models.
2. Close and reopen Antigravity.
3. Type your next prompt in the exact same chat.
4. **Context Engine automatically detects the new host PID** and injects the snapshot with the `[DO NOT RE-READ LOCK]` and `[PRIOR ACCEPTED STATE]`.

### 2. Carrying Context Across Chats
Every time context is carried, Antigravity displays an inline Markdown card right in the chat UI:

| Command | Where to Type It | What It Does |
| :--- | :--- | :--- |
| **`/chats`** | Any Chat | Displays a numbered table showing your saved chats (`#1`, `#2`...), Short IDs, Tags, Workspaces, File Counts, and previews. |
| **`/carry 1`** | New Chat B | Carries context from row `#1` of the `/chats` table into the current chat (e.g. `/carry 1 now write chapter 2`). |
| **`/save story`** | Old Chat A | Pins the chat under tag `story`. |
| **`/carry story`** | New Chat B | Carries context from the chat tagged `story`. |
| **`/carry fd4cfb71`** | New Chat B | Carries context by 8-character conversation ID. |
| **`/carry`** *(no args)* | New Chat B | Automatically pulls from the last pinned chat or the most recent chat in the active workspace. |

---

## Verify

```bash
python test_context_engine.py
```

Runs 16 automated test cases verifying read-only transcript parsing, refusal stripping, Argon model-switch detection, host-PID app restart detection, `/save` auto-arming, `/chats`, `/carry`, `/compact`, and `/context`.

---

## Files

```
antigravity-context-engine/
├── plugin.json             # Manifest (v1.0.0)
├── hooks.json              # PreInvocation & Stop hook definitions
├── context_engine.py       # Local transcript indexer, store manager, & payload builder
├── context_pre.py          # PreInvocation handler (auto-sync + /save, /carry, /chats, etc.)
├── context_stop.py         # Stop handler (updates snapshot after every turn)
├── test_context_engine.py  # 16 automated test cases
├── skills/                 # Native Antigravity Skills for slash command autocomplete
│   ├── save/SKILL.md       # /save skill definition
│   ├── carry/SKILL.md      # /carry skill definition
│   ├── chats/SKILL.md      # /chats skill definition
│   ├── compact/SKILL.md    # /compact skill definition
│   └── context/SKILL.md    # /context command guide
└── README.md
```
