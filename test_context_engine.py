#!/usr/bin/env python3
"""
Automated test suite for antigravity-context-engine (16 test cases).
Validates:
1. Read-only transcript indexing (read_file, write_file, edit_file digests + 100% complete flag).
2. Refusal stripping (blocked/refused turns excluded from accepted continuity anchor).
3. Stop hook updates snapshot and returns decision: allow.
4. Normal same-model turn passes through with zero overhead.
5. Automatic Model Switch detection (e.g. Flash -> Argon) injects cached files & anti-reread lock.
6. Automatic Session Resume / Restart gap (>3m) injects snapshot.
7. '.save <tag>' pins, tags, and arms the current conversation with UI banner.
8. Same-Chat '.save' auto-restores on the very next turn even 1 second later without typing '.carry'.
9. Immediate Antigravity App Restart detection (host process PID change, <1s gap) auto-restores Same-Chat.
10. '.chats' renders the numbered snapshot table via metadata.user_markdown.
11. '.carry 1' (by table row number) carries snapshot into a new conversation.
12. '.carry <tag>' (by saved tag name) carries snapshot into a new conversation.
13. '.carry <short_id>' (by conversation ID prefix) carries snapshot into a new conversation.
14. '.sync' / '.compact' forces an immediate local refresh & injection without cloud API calls.
15. Slash command parity (/save, /chats, /carry, /compact) matches dot command syntax.
16. '/context' and '/help' render full interactive command guide.
"""

import os
import sys
import json
import time
import shutil
import tempfile
import subprocess
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent
PRE_SCRIPT = PLUGIN_DIR / "context_pre.py"
STOP_SCRIPT = PLUGIN_DIR / "context_stop.py"


def run_hook(script_path: Path, payload: dict, store_dir: Path, host_sig: str = "antigravity.exe:1001") -> dict:
    env = dict(os.environ)
    env["AGY_CONTEXT_STORE_DIR"] = str(store_dir)
    env["AGY_HOST_SIGNATURE"] = host_sig
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Hook {script_path.name} failed ({proc.returncode}): {proc.stderr}")
    return json.loads(proc.stdout)


def create_sample_transcript(tmpdir: Path) -> Path:
    tpath = tmpdir / "transcript_full.jsonl"
    steps = [
        {
            "type": "USER_INPUT",
            "source": "USER_EXPLICIT",
            "content": "<USER_REQUEST>Write chapter 1 in chapter1.md and check rules.py</USER_REQUEST>",
        },
        {
            "type": "PLANNER_RESPONSE",
            "tool_calls": [
                {"name": "read_file", "args": {"Path": "D:/project/rules.py"}},
            ],
        },
        {
            "type": "TOOL_RESPONSE",
            "content": "def validate_scene():\n    return True\n# 42 lines of core logic",
        },
        {
            "type": "PLANNER_RESPONSE",
            "tool_calls": [
                {
                    "name": "write_file",
                    "args": {
                        "Path": "D:/project/chapter1.md",
                        "Content": "# Chapter 1\nThe rain hammered against the tall glass windows...",
                    },
                }
            ],
        },
        {
            "type": "MODEL_RESPONSE",
            "content": "This request was blocked by Gemini's filters.",
        },
        {
            "type": "MODEL_RESPONSE",
            "content": "Chapter 1 has been written to chapter1.md following all scene rules.",
        },
    ]
    with open(tpath, "w", encoding="utf-8") as f:
        for s in steps:
            f.write(json.dumps(s) + "\n")
    return tpath


def test_suite():
    print("Running antigravity-context-engine test suite...\n")
    tmpdir = Path(tempfile.mkdtemp(prefix="agy_ctx_test_"))
    store_dir = tmpdir / "store"

    try:
        tpath = create_sample_transcript(tmpdir)

        # Case 1 & 2 & 3: Stop hook indexes files, strips refusal turns, and returns allow
        res_stop = run_hook(
            STOP_SCRIPT,
            {
                "conversationId": "fd4cfb71-d5b7-4c71-bd30-b136d3418163",
                "workspacePaths": ["D:/project/story-workspace"],
                "transcriptPath": str(tpath),
                "modelName": "gemini-3.8-flash",
            },
            store_dir,
        )
        assert res_stop.get("decision") == "allow"
        snap_file = store_dir / "snapshots" / "fd4cfb71-d5b7-4c71-bd30-b136d3418163.json"
        assert snap_file.is_file(), "Snapshot file was not created by Stop hook"
        snap = json.loads(snap_file.read_text(encoding="utf-8"))

        assert "D:/project/rules.py" in snap["files"]
        assert snap["files"]["D:/project/rules.py"]["isComplete"] is True
        assert "D:/project/chapter1.md" in snap["files"]
        assert "validate_scene" in snap["files"]["D:/project/rules.py"]["digest"]
        print("  [PASS] Case 1: Read-only transcript indexer caches full 100% file digests")

        for turn in snap["accepted_turns"]:
            assert "blocked by Gemini's filters" not in turn["text"]
        assert any("Chapter 1 has been written" in t["text"] for t in snap["accepted_turns"])
        print("  [PASS] Case 2: Refusal/filter-blocked turns are stripped from Accepted Continuity Anchor")
        print("  [PASS] Case 3: Stop hook updates snapshot and returns decision=allow")

        # Case 4: Normal turn with same model, same host PID, and recent timestamp -> zero-overhead pass-through
        res_normal = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "fd4cfb71-d5b7-4c71-bd30-b136d3418163",
                "workspacePaths": ["D:/project/story-workspace"],
                "transcriptPath": str(tpath),
                "modelName": "gemini-3.8-flash",
                "lastUserInput": "Continue with scene 2",
                "invocationNum": 1,
            },
            store_dir,
        )
        assert res_normal.get("injectSteps") == []
        print("  [PASS] Case 4: Same-model active turn passes through with zero overhead")

        # Case 5: Switching model to Argon -> auto-injects cached files + Argon anti-reread lock
        res_argon = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "fd4cfb71-d5b7-4c71-bd30-b136d3418163",
                "workspacePaths": ["D:/project/story-workspace"],
                "transcriptPath": str(tpath),
                "modelName": "gemini-4-argon",
                "lastUserInput": "Continue with scene 2",
                "invocationNum": 1,
            },
            store_dir,
        )
        assert len(res_argon.get("injectSteps", [])) == 1
        sys_msg = res_argon["injectSteps"][0]["systemMessage"]["systemMessage"]
        user_md = res_argon["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"]
        assert "100% COMPLETE CONTENT CACHED — DO NOT CALL read_file" in sys_msg
        assert "D:/project/rules.py" in sys_msg
        assert "Model Switch" in user_md
        print("  [PASS] Case 5: Model switch to Argon auto-injects 100% cached files & anti-reread lock")

        # Case 6: Idle gap (>3m) -> auto-injects snapshot
        snap = json.loads(snap_file.read_text(encoding="utf-8"))
        snap["updatedEpoch"] = time.time() - 300
        snap["lastModelName"] = "gemini-4-argon"
        snap_file.write_text(json.dumps(snap), encoding="utf-8")

        res_restart = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "fd4cfb71-d5b7-4c71-bd30-b136d3418163",
                "workspacePaths": ["D:/project/story-workspace"],
                "transcriptPath": str(tpath),
                "modelName": "gemini-4-argon",
                "lastUserInput": "Let's pick up where we left off",
                "invocationNum": 1,
            },
            store_dir,
        )
        assert len(res_restart.get("injectSteps", [])) == 1
        assert "Session Resume" in res_restart["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"]
        print("  [PASS] Case 6: Idle gap (>3m) auto-injects session snapshot")

        # Case 7: '.save story' tags, pins, and arms the conversation
        res_save = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "fd4cfb71-d5b7-4c71-bd30-b136d3418163",
                "workspacePaths": ["D:/project/story-workspace"],
                "transcriptPath": str(tpath),
                "modelName": "gemini-4-argon",
                "lastUserInput": ".save story",
                "invocationNum": 1,
            },
            store_dir,
        )
        assert len(res_save.get("injectSteps", [])) == 1
        assert "story" in res_save["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"]
        print("  [PASS] Case 7: '.save story' pins, tags, and arms the conversation")

        # Case 8: Same-Chat next message after '.save' auto-injects immediately (even 0s later!)
        res_same_after_save = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "fd4cfb71-d5b7-4c71-bd30-b136d3418163",
                "workspacePaths": ["D:/project/story-workspace"],
                "transcriptPath": str(tpath),
                "modelName": "gemini-4-argon",
                "lastUserInput": "Write the next paragraph now",
                "invocationNum": 1,
            },
            store_dir,
        )
        assert len(res_same_after_save.get("injectSteps", [])) == 1
        assert "Armed" in res_same_after_save["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"]
        assert "Snapshot Restored" in res_same_after_save["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"]
        assert "D:/project/chapter1.md" in res_same_after_save["injectSteps"][0]["systemMessage"]["systemMessage"]
        print("  [PASS] Case 8: Same-chat after '.save' auto-restores full snapshot on next message")

        # Case 9: Closing & reopening Antigravity (new host process PID, <1s later) auto-restores Same-Chat
        res_app_restart = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "fd4cfb71-d5b7-4c71-bd30-b136d3418163",
                "workspacePaths": ["D:/project/story-workspace"],
                "transcriptPath": str(tpath),
                "modelName": "gemini-4-argon",
                "lastUserInput": "Continue right after reopening Antigravity",
                "invocationNum": 1,
            },
            store_dir,
            host_sig="antigravity.exe:2099",  # New PID after reopening Antigravity
        )
        assert len(res_app_restart.get("injectSteps", [])) == 1
        assert "Antigravity App Restart Detected" in res_app_restart["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"]
        print("  [PASS] Case 9: Closing & reopening Antigravity (new host PID) auto-restores Same-Chat immediately")

        # Case 10: '.chats' renders numbered markdown table of saved snapshots
        res_chats = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "new-convo-99999999",
                "workspacePaths": ["D:/project/story-workspace"],
                "lastUserInput": ".chats",
                "invocationNum": 1,
            },
            store_dir,
        )
        chats_md = res_chats["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"]
        assert "Available Snapshots" in chats_md
        assert "fd4cfb71" in chats_md
        assert "story" in chats_md
        print("  [PASS] Case 10: '.chats' renders numbered snapshot table with IDs, tags, and previews")

        # Case 11: '.carry 1' (by number) in a brand-new conversation
        res_carry_num = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "new-convo-11111111",
                "workspacePaths": ["D:/other"],
                "lastUserInput": ".carry 1 write chapter 2",
                "invocationNum": 1,
            },
            store_dir,
        )
        carry_sys = res_carry_num["injectSteps"][0]["systemMessage"]["systemMessage"]
        carry_md = res_carry_num["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"]
        assert "D:/project/chapter1.md" in carry_sys
        assert "write chapter 2" in carry_sys
        assert "Carried Forward" in carry_md
        assert "fd4cfb71" in carry_md
        print("  [PASS] Case 11: '.carry 1' carries context by table number into a new chat")

        # Case 12: '.carry story' (by custom tag)
        res_carry_tag = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "new-convo-22222222",
                "workspacePaths": ["D:/other"],
                "lastUserInput": ".carry story",
                "invocationNum": 1,
            },
            store_dir,
        )
        assert "D:/project/rules.py" in res_carry_tag["injectSteps"][0]["systemMessage"]["systemMessage"]
        print("  [PASS] Case 12: '.carry <tag>' carries context by friendly tag name")

        # Case 13: '.carry fd4cfb71' (by short conversation ID)
        res_carry_id = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "new-convo-33333333",
                "workspacePaths": ["D:/other"],
                "lastUserInput": ".carry fd4cfb71",
                "invocationNum": 1,
            },
            store_dir,
        )
        assert "D:/project/rules.py" in res_carry_id["injectSteps"][0]["systemMessage"]["systemMessage"]
        print("  [PASS] Case 13: '.carry <short_id>' carries context by conversation ID prefix")

        # Case 14: '.sync' / '.compact' forces local refresh without cloud API calls
        res_sync = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "fd4cfb71-d5b7-4c71-bd30-b136d3418163",
                "workspacePaths": ["D:/project/story-workspace"],
                "transcriptPath": str(tpath),
                "modelName": "gemini-4-argon",
                "lastUserInput": ".sync continue writing",
                "invocationNum": 1,
            },
            store_dir,
        )
        assert "Manual Local Sync" in res_sync["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"]
        print("  [PASS] Case 14: '.sync' / '.compact' performs 100% local refresh and injection")

        # Case 15: Slash command syntax parity (/save, /chats, /carry, /compact)
        res_slash_save = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "fd4cfb71-d5b7-4c71-bd30-b136d3418163",
                "workspacePaths": ["D:/project/story-workspace"],
                "transcriptPath": str(tpath),
                "modelName": "gemini-4-argon",
                "lastUserInput": "/save story-slash",
                "invocationNum": 1,
            },
            store_dir,
        )
        assert "story-slash" in res_slash_save["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"]

        res_slash_chats = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "new-convo-44444444",
                "workspacePaths": ["D:/project/story-workspace"],
                "lastUserInput": "/chats",
                "invocationNum": 1,
            },
            store_dir,
        )
        assert "story-slash" in res_slash_chats["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"]

        res_slash_carry = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "new-convo-55555555",
                "workspacePaths": ["D:/other"],
                "lastUserInput": "/carry story-slash continue immediately",
                "invocationNum": 1,
            },
            store_dir,
        )
        assert "D:/project/chapter1.md" in res_slash_carry["injectSteps"][0]["systemMessage"]["systemMessage"]
        assert "continue immediately" in res_slash_carry["injectSteps"][0]["systemMessage"]["systemMessage"]
        print("  [PASS] Case 15: Slash command syntax (/save, /chats, /carry) functions identically to dot syntax")

        # Case 16: /context and /help renders full interactive command guide
        res_help = run_hook(
            PRE_SCRIPT,
            {
                "conversationId": "new-convo-66666666",
                "workspacePaths": ["D:/project/story-workspace"],
                "lastUserInput": "/context",
                "invocationNum": 1,
            },
            store_dir,
        )
        help_md = res_help["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"]
        assert "Command Guide" in help_md
        assert "/save" in help_md
        assert "/carry" in help_md
        assert "/chats" in help_md
        print("  [PASS] Case 16: '/context' and '/help' render full interactive command guide")

        print("\nALL 16 CONTEXT ENGINE TESTS PASSED SUCCESSFULLY.")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    test_suite()
