#!/usr/bin/env python3
"""
PRISM Weekly Content Generator
Run via cron or on-demand: python generate-weekly.py

Generates a week's worth of content drafts, saves to drafts folder.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add engine to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "engine"))

from platform_writers.x_writer import write_x_thread, format_for_review
from content_brain import generate_brief, save_draft_to_db

DRAFTS_DIR = BASE_DIR / "drafts"


def create_draft_folder():
    """Create today's draft folder."""
    today = datetime.now().strftime("%Y-%m-%d")
    folder = DRAFTS_DIR / today
    folder.mkdir(parents=True, exist_ok=True)
    return folder, today


def generate_week_content(num_threads=3):
    """
    Generate content for the week.

    Args:
        num_threads: How many X threads to generate

    Returns:
        List of generated thread drafts
    """
    drafts = []

    for i in range(num_threads):
        try:
            # Generate brief
            brief = generate_brief()

            # Write thread
            thread = write_x_thread(brief)

            # Save to database
            draft_id = save_draft_to_db(brief, thread, status="pending")

            # Format for review
            review_text = format_for_review(thread)

            # Save to drafts folder
            today = datetime.now().strftime("%Y-%m-%d")
            draft_file = DRAFTS_DIR / today / f"thread-{i+1:02d}.md"
            meta_file = DRAFTS_DIR / today / f"thread-{i+1:02d}-meta.json"

            with open(draft_file, 'w') as f:
                f.write(review_text)

            with open(meta_file, 'w') as f:
                json.dump({
                    "draft_id": draft_id,
                    "topic": brief["topic"],
                    "hook_type": brief["hook_type"],
                    "hook_formula": brief["hook_formula"],
                    "platform": brief["platform"],
                    "format": brief["format"]
                }, f, indent=2)

            drafts.append({
                "draft_id": draft_id,
                "topic": brief["topic"],
                "hook_type": brief["hook_type"],
                "file": str(draft_file),
                "review": review_text
            })

            print(f"✅ Draft {i+1}: {brief['topic']} ({brief['hook_type']})")

        except Exception as e:
            print(f"❌ Error generating draft {i+1}: {e}")
            continue

    return drafts


def get_review_summary(drafts):
    """Build a Telegram-friendly summary of all drafts."""
    lines = []
    lines.append("📝 WEEKLY CONTENT READY")
    lines.append("=" * 40)

    for i, draft in enumerate(drafts, 1):
        lines.append(f"\nDraft {i}:")
        lines.append(f"  Topic: {draft['topic']}")
        lines.append(f"  Hook: {draft['hook_type']}")
        lines.append(f"  File: {draft['file']}")

    lines.append(f"\n{'='*40}")
    lines.append(f"Total drafts: {len(drafts)}")
    lines.append("\nReview each thread in the drafts folder.")
    lines.append("Copy → Buffer → Schedule.")
    lines.append("\nAfter posting, come back and tell me the results")
    lines.append("so I can update PRISM's content bank.")

    return "\n".join(lines)


def main():
    print(f"🚀 PRISM Weekly Generator — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    # Create draft folder
    folder, today = create_draft_folder()
    print(f"📁 Draft folder: {folder}")

    # Generate content
    # Default: 3 threads per week (you can adjust)
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    drafts = generate_week_content(num_threads=num)

    if drafts:
        summary = get_review_summary(drafts)
        print("\n" + summary)

        # Save summary
        summary_file = folder / "WEEKLY-SUMMARY.txt"
        with open(summary_file, 'w') as f:
            f.write(summary)
        print(f"\n📋 Summary saved: {summary_file}")
    else:
        print("❌ No drafts generated. Check errors above.")

    print("\n✅ Done.")


if __name__ == "__main__":
    main()
