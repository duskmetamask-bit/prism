"""
PRISM Content Scheduler
Builds a platform-native content calendar based on algorithm windows.

Usage:
    from prism.scheduler import ContentScheduler
    scheduler = ContentScheduler()
    calendar = scheduler.build_week_schedule()
    print(scheduler.format_calendar(calendar))
"""

import json
import random
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config" / "user-profile.yaml"


def load_user_profile():
    """Load user profile from YAML."""
    import yaml
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)


class ContentScheduler:
    """
    Generates a weekly content calendar optimised for each platform's algorithm.

    Algorithm windows used:
    - X: 9am / 12pm / 6pm AWST (highest engagement)
    - LinkedIn: 8am AWST Tue–Thu (algorithm favours early-week professional content)
    - YouTube: 3–6pm AWST Thu–Sun (viewing peaks evenings/weekends)
    """

    # Platform algorithm windows (AWST)
    PLATFORM_WINDOWS = {
        "X": {
            "best_days": [1, 2, 3, 4, 5],  # Mon–Fri
            "windows": ["09:00", "12:00", "18:00"],
            "posts_per_week": 7,
            "reason": "X engagement peaks mid-morning, lunch, and evening. Weekdays outperform weekends."
        },
        "LinkedIn": {
            "best_days": [2, 3, 4],  # Tue, Wed, Thu
            "windows": ["08:00"],
            "posts_per_week": 2,
            "reason": "LinkedIn algorithm rewards early-week professional content. Tue 8am is consistently strongest."
        },
        "YouTube": {
            "best_days": [4, 5, 6, 7],  # Thu–Sun
            "windows": ["15:00", "17:00", "18:00"],
            "posts_per_week": 1,
            "reason": "YouTube viewership peaks Thu–Sun evenings. Afternoon uploads allow subscriber notifications to hit inboxes before prime time."
        }
    }

    # Content type mix targets (% of weekly posts)
    CONTENT_MIX = {
        "personal_story": 0.30,   # "I almost gave up..."
        "tips_lessons": 0.25,     # "The N things I learned..."
        "hot_take": 0.20,         # "[X] is wrong because..."
        "tool_resource": 0.15,     # "I tested [tool] for 30 days..."
        "engagement": 0.10        # questions, callouts
    }

    def __init__(self, user_profile=None):
        self.user = user_profile or load_user_profile()
        self.schedule = []

    def build_week_schedule(self, start_date=None, num_threads_x=5, num_posts_linkedin=2, num_videos=0):
        """
        Build a full week's content schedule.

        Args:
            start_date: Date to start scheduling from (default: next Monday)
            num_threads_x: How many X posts/threads to schedule
            num_posts_linkedin: How many LinkedIn posts
            num_videos: How many YouTube videos

        Returns:
            List of scheduled content items
        """
        if start_date is None:
            # Next Monday
            today = datetime.now()
            days_ahead = 7 - today.weekday()  # Days until Monday
            if days_ahead <= 0:
                days_ahead = 7
            start_date = today + timedelta(days=days_ahead)

        schedule = []
        content_plan = self._build_content_plan(
            num_threads_x=num_threads_x,
            num_posts_linkedin=num_posts_linkedin,
            num_videos=num_videos
        )

        # Assign content to X slots
        x_items = [c for c in content_plan if c["platform"] == "X"]
        x_slots = self._generate_platform_slots("X", start_date, len(x_items))

        # Assign content to LinkedIn slots
        linkedin_items = [c for c in content_plan if c["platform"] == "LinkedIn"]
        linkedin_slots = self._generate_platform_slots("LinkedIn", start_date, len(linkedin_items))

        # Assign content to YouTube slots
        youtube_items = [c for c in content_plan if c["platform"] == "YouTube"]
        youtube_slots = self._generate_platform_slots("YouTube", start_date, len(youtube_items))

        all_slots = x_slots + linkedin_slots + youtube_slots
        all_slots.sort(key=lambda x: x["scheduled_datetime"])

        # Merge slots with content
        for i, slot in enumerate(all_slots):
            if slot["platform"] == "X" and i < len(x_items):
                slot.update(x_items[i])
            elif slot["platform"] == "LinkedIn" and (i - len(x_slots)) < len(linkedin_items):
                idx = i - len(x_slots)
                if idx >= 0:
                    slot.update(linkedin_items[idx])
            elif slot["platform"] == "YouTube" and (i - len(x_slots) - len(linkedin_slots)) < len(youtube_items):
                idx = i - len(x_slots) - len(linkedin_slots)
                if idx >= 0:
                    slot.update(youtube_items[idx])

        self.schedule = all_slots
        return all_slots

    def _generate_platform_slots(self, platform, start_date, num_items):
        """Generate datetime slots for a platform's algorithm windows."""
        config = self.PLATFORM_WINDOWS[platform]
        slots = []

        # Build list of all valid day/window combinations for the week
        valid_datetimes = []
        for day_offset in range(7):  # Mon–Sun
            date = start_date + timedelta(days=day_offset)
            if date.weekday() + 1 not in config["best_days"]:
                continue
            for window in config["windows"]:
                hour, minute = map(int, window.split(":"))
                dt = date.replace(hour=hour, minute=minute, second=0)
                valid_datetimes.append(dt)

        # Pick the first N slots (sorted by datetime)
        valid_datetimes.sort()
        chosen = valid_datetimes[:num_items]

        for dt in chosen:
            slots.append({
                "platform": platform,
                "scheduled_datetime": dt,
                "scheduled_date": dt.strftime("%Y-%m-%d"),
                "scheduled_time": dt.strftime("%H:%M"),
                "awst_time": dt.strftime("%-I:%M %p AWST"),
                "day_name": dt.strftime("%A"),
                "window_reason": config["reason"],
                "status": "draft"  # draft | queued | posted
            })

        return slots

    def _build_content_plan(self, num_threads_x, num_posts_linkedin, num_videos):
        """Build a planned content mix across platforms."""
        plan = []

        # X content — 5-7 posts/week
        for i in range(num_threads_x):
            content_type = self._pick_content_type()
            plan.append({
                "platform": "X",
                "content_type": content_type,
                "slot_index": i + 1,
                "format": "thread" if random.random() > 0.3 else "single",
            })

        # LinkedIn content — 2-3 posts/week
        for i in range(num_posts_linkedin):
            plan.append({
                "platform": "LinkedIn",
                "content_type": random.choice(["tips_lessons", "personal_story", "tool_resource"]),
                "slot_index": i + 1,
                "format": "post"
            })

        # YouTube — 1-2 videos/week
        for i in range(num_videos):
            plan.append({
                "platform": "YouTube",
                "content_type": "tutorial",  # YouTube rewards educational/long-form
                "slot_index": i + 1,
                "format": "video"
            })

        return plan

    def _pick_content_type(self):
        """Pick a content type based on the target mix."""
        r = random.random()
        cumulative = 0
        for ct, pct in self.CONTENT_MIX.items():
            cumulative += pct
            if r <= cumulative:
                return ct
        return "tips_lessons"

    def format_calendar(self, schedule=None):
        """Format the schedule as a readable calendar for Telegram."""
        if schedule is None:
            schedule = self.schedule

        if not schedule:
            return "No schedule generated yet."

        lines = []
        lines.append("📅 PRISM CONTENT CALENDAR")
        lines.append("=" * 44)

        current_date = None
        for item in schedule:
            dt = item["scheduled_datetime"]
            date_str = dt.strftime("%A %-d %b")

            if date_str != current_date:
                lines.append("")
                lines.append(f"── {date_str} ──")
                current_date = date_str

            time_str = item["awst_time"]
            platform = item["platform"]
            platform_icon = {"X": "𝕏", "LinkedIn": "💼", "YouTube": "▶️"}.get(platform, platform)
            content_type = item.get("content_type", "content")
            fmt = item.get("format", "post")
            topic = item.get("topic", f"[topic TBD via content_brain]")

            lines.append(f"  {platform_icon} {time_str} | {fmt} | {content_type}")
            lines.append(f"     → {topic}")

        lines.append("")
        lines.append("=" * 44)
        lines.append("Platform windows optimised for algorithm peaks.")
        lines.append("Topics assigned via content_brain when generating drafts.")
        lines.append("")
        lines.append("To generate drafts for this week:")
        lines.append("  python prism/scripts/generate_weekly.py")
        lines.append("  python prism/scripts/generate_weekly.py --platforms X --count 5")

        return "\n".join(lines)

    def get_upcoming(self, days=3):
        """Get the next N days of scheduled content."""
        now = datetime.now()
        upcoming = []

        for item in self.schedule:
            dt = item["scheduled_datetime"]
            if dt >= now and (dt - now).days <= days:
                upcoming.append(item)

        return upcoming

    def export_ics(self, schedule=None, filename=None):
        """Export schedule as .ics calendar file for Google Calendar import."""
        if schedule is None:
            schedule = self.schedule

        if filename is None:
            filename = BASE_DIR / "drafts" / f"prism-calendar-{datetime.now().strftime('%Y-%m-%d')}.ics"

        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//PRISM//Content Scheduler//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "X-WR-CALNAME:PRISM Content Calendar"
        ]

        for item in schedule:
            dt = item["scheduled_datetime"]
            content_type = item.get("content_type", "content")
            topic = item.get("topic", "Content draft")
            platform = item["platform"]

            lines.append("BEGIN:VEVENT")
            lines.append(f"DTSTART:{dt.strftime('%Y%m%dT%H%M%S')}")
            # Default 30 min duration
            end_dt = dt + timedelta(minutes=30)
            lines.append(f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}")
            lines.append(f"SUMMARY:{platform} — {content_type}")
            lines.append(f"DESCRIPTION:{topic}")
            lines.append(f"UID:prism-{item['scheduled_date']}-{item['scheduled_time'].replace(':', '')}@prism")
            lines.append("END:VEVENT")

        lines.append("END:VCALENDAR")

        with open(filename, 'w') as f:
            f.write("\n".join(lines))

        return filename


def build_and_format_schedule(**kwargs):
    """One-shot: build schedule and return formatted string."""
    scheduler = ContentScheduler()
    schedule = scheduler.build_week_schedule(**kwargs)
    return scheduler.format_calendar(schedule), schedule


if __name__ == "__main__":
    result, schedule = build_and_format_schedule(num_threads_x=5, num_posts_linkedin=2)
    print(result)
    print(f"\n📁 {len(schedule)} items scheduled")
