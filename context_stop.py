#!/usr/bin/env python3
"""
Stop Hook Handler for Antigravity Context Engine (context_stop.py).
Updates the conversation's local snapshot in ~/.gemini/context_store/ whenever a turn completes,
then returns {"decision": "allow"} so it never interferes with normal stop behavior.
"""

import sys
import json
from context_engine import update_context_snapshot, log


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception as e:
        log(f"[StopHook] JSON parse error: {e}")
        json.dump({"decision": "allow"}, sys.stdout)
        return

    try:
        if data.get("conversationId") or data.get("transcriptPath"):
            update_context_snapshot(data)
    except Exception as e:
        log(f"[StopHook] Snapshot update error: {e}")

    json.dump({"decision": "allow"}, sys.stdout)


if __name__ == "__main__":
    main()
