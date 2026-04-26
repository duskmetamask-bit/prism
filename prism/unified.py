"""
PRISM Unified Class
Chains: content_brain → writers → scheduler

Usage:
    from prism.unified import PRISM
    prism = PRISM()
    result = prism.generate_week()
    calendar = prism.get_calendar()
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Bridge paths
BASE_DIR = Path(__file__).parent.parent
ENGINE_DIR = BASE_DIR / "engine"
PRISM_DIR = Path(__file__).parent

# Add engine to path for imports
sys.path.insert(0, str(ENGINE_DIR))
sys.path.insert(0, str(PRISM_DIR))

from prism.scheduler import ContentScheduler


class PRISM:
    """
    PRISM unified content intelligence orchestrator.

    Workflow:
        1. content_brain generates content briefs (what to post)
        2. platform writers generate actual copy (how to post)
        3. scheduler builds the calendar (when to post)
        4. results are saved to drafts/ and tracked in SQLite
    """

    def __init__(self):
        self.scheduler = ContentScheduler()
        self.drafts_dir = BASE_DIR / "drafts"
        self.drafts_dir.mkdir(parents=True, exist_ok=True)

    def generate_week(self, num_threads_x=5, num_posts_linkedin=2, num_videos=0):
        """
        Generate a full week's content:
        1. Build the calendar schedule
        2. Generate content briefs via content_brain
        3. Write actual copy via platform writers
        4. Save drafts for review

        Returns dict with calendar and draft summaries.
        """
        # Step 1: Build schedule
        schedule = self.scheduler.build_week_schedule(
            num_threads_x=num_threads_x,
            num_posts_linkedin=num_posts_linkedin,
            num_videos=num_videos
        )

        # Step 2: Import content_brain and writers
        try:
            from content_brain import generate_brief, save_draft_to_db
            from platform_writers.x_writer import write_x_thread, format_for_review
        except ImportError as e:
            return {
                "error": f"Could not import engine modules: {e}",
                "schedule": schedule
            }

        # Step 3: Generate drafts for X content
        drafts = []
        x_items = [s for s in schedule if s["platform"] == "X"]

        for slot in x_items:
            try:
                brief = generate_brief(platform="X")
                thread = write_x_thread(brief)
                draft_id = save_draft_to_db(brief, thread, status="pending")

                # Save to drafts folder
                today = datetime.now().strftime("%Y-%m-%d")
                draft_file = self.drafts_dir / today / f"x-{slot['scheduled_date']}-{slot['scheduled_time'].replace(':', '')}.md"

                draft_file.parent.mkdir(parents=True, exist_ok=True)
                review_text = format_for_review(thread)

                with open(draft_file, 'w') as f:
                    f.write(review_text)

                drafts.append({
                    "draft_id": draft_id,
                    "platform": "X",
                    "slot": slot,
                    "brief": brief,
                    "file": str(draft_file)
                })

                # Update schedule slot with topic
                slot["topic"] = brief["topic"]
                slot["hook_type"] = brief["hook_type"]
                slot["draft_file"] = str(draft_file)

            except Exception as e:
                drafts.append({
                    "platform": "X",
                    "slot": slot,
                    "error": str(e)
                })

        # Step 4: Generate LinkedIn posts
        linkedin_items = [s for s in schedule if s["platform"] == "LinkedIn"]
        # LinkedIn writer not yet implemented — flag for build
        for slot in linkedin_items:
            slot["status"] = "linkedin_writer_pending"
            slot["topic"] = "[LinkedIn writer not yet built]"

        return {
            "generated_at": datetime.now().isoformat(),
            "schedule": schedule,
            "drafts": drafts,
            "calendar_formatted": self.scheduler.format_calendar(schedule)
        }

    def get_calendar(self, start_date=None):
        """Get this week's content calendar."""
        schedule = self.scheduler.build_week_schedule(start_date=start_date)
        return {
            "schedule": schedule,
            "formatted": self.scheduler.format_calendar(schedule)
        }

    def get_upcoming(self, days=3):
        """Get next N days of scheduled content."""
        return self.scheduler.get_upcoming(days=days)

    def export_calendar_ics(self):
        """Export calendar as .ics file for Google Calendar import."""
        filename = self.scheduler.export_ics()
        return str(filename)


# Convenience function
def run():
    """CLI entry point."""
    from prism.scheduler import build_and_format_schedule

    print("📅 PRISM Content Calendar")
    print("=" * 40)

    result, schedule = build_and_format_schedule(
        num_threads_x=5,
        num_posts_linkedin=2,
        num_videos=0
    )

    print(result)
    print(f"\n✅ {len(schedule)} slots scheduled")


if __name__ == "__main__":
    run()
