#!/usr/bin/env python3
"""
PreInvocation Hook Handler for Antigravity Context Engine (context_pre.py).
Handles:
- Automatic context & file-digest injection when switching models (e.g. to Argon) or after app restart.
- User commands: .chats, .save [tag], .sync / .compact, and .carry [# | tag | id].
"""

import sys
import json
from context_engine import handle_pre_invocation, log


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception as e:
        log(f"[PreInvocation] JSON parse error: {e}")
        json.dump({"injectSteps": [], "terminationBehavior": ""}, sys.stdout)
        return

    try:
        result = handle_pre_invocation(data)
    except Exception as e:
        log(f"[PreInvocation] Execution error: {e}")
        result = {"injectSteps": [], "terminationBehavior": ""}

    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
