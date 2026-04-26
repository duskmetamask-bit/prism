"""
PRISM — Entry Point
Content intelligence agent. Generates X posts from research + story brain.
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """PRISM main loop."""
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        print("Usage:")
        print("  python3 run.py generate    — generate X posts from story brain")
        print("  python3 run.py status      — show story count, drafts, queue")
        print("  python3 run.py fetch       — fetch fresh stories")
        return

    cmd = args[0].lower()

    if cmd == "generate":
        from writers.x_writer import generate_pending_stories
        count = int(args[1]) if len(args) > 1 else 3
        generate_pending_stories(limit=count)

    elif cmd == "status":
        from database.prism_db import get_db
        db = get_db()
        hooks = db.execute("SELECT COUNT(*) FROM stories").fetchone()[0]
        drafts = db.execute("SELECT COUNT(*) FROM drafts WHERE status = 'pending'").fetchone()[0]
        print(f"PRISM Status — Stories: {hooks}, Pending Drafts: {drafts}")

    elif cmd == "fetch":
        print("[*] Fetching stories...")
        from scripts.fetch_stories import main as fetch_main
        fetch_main()

    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python3 run.py [generate|status|fetch]")


if __name__ == "__main__":
    main()
