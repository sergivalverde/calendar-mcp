"""Simple automatic calendar cache system."""

import subprocess
import json
import re
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

from .models import CalendarEvent, Attendee


class SimpleCalendarCache:
    """Simple cache that automatically fetches calendar data."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the cache."""
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "calendar-mcp"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "events.json"

    def get_events(self, start_date: date, end_date: date) -> List[CalendarEvent]:
        """Get events for the date range, using cache or fetching if needed."""
        # Check if we have fresh cache
        if not self._is_cache_fresh():
            self._update_cache()

        # Load from cache
        return self._load_cached_events(start_date, end_date)

    def _is_cache_fresh(self) -> bool:
        """Check if cache is fresh (less than 5 minutes old)."""
        if not self.cache_file.exists():
            return False

        try:
            stat = self.cache_file.stat()
            age_seconds = datetime.now().timestamp() - stat.st_mtime
            return age_seconds < 300  # 5 minutes
        except:
            return False

    def _update_cache(self):
        """Update the cache with fresh calendar data."""
        try:
            # Fetch events for the next 90 days
            start_date = date.today() - timedelta(days=7)  # Include past week
            end_date = date.today() + timedelta(days=90)

            # Try multiple approaches to get calendar data

            # Approach 1: Direct icalBuddy call (works in some environments)
            events = self._try_direct_icalbuddy(start_date, end_date)

            # Approach 2: Shell script wrapper (more reliable)
            if not events:
                events = self._try_shell_script(start_date, end_date)

            # Save cache data
            cache_data = {
                "updated_at": datetime.now().isoformat(),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "event_count": len(events),
                "events": [self._event_to_dict(event) for event in events]
            }

            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

            print(f"Cache updated: {len(events)} events found")

        except Exception as e:
            print(f"Warning: Failed to update calendar cache: {e}")
            # Create empty cache to avoid repeated failures
            cache_data = {
                "updated_at": datetime.now().isoformat(),
                "start_date": start_date.isoformat() if 'start_date' in locals() else None,
                "end_date": end_date.isoformat() if 'end_date' in locals() else None,
                "event_count": 0,
                "events": []
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

    def _try_direct_icalbuddy(self, start_date, end_date):
        """Try direct icalBuddy call."""
        try:
            cmd = [
                "icalBuddy",
                "-nc",
                "-iep", "title,datetime,location,notes,attendees",
                "-df", "%Y-%m-%d %H:%M:%S",
                "-tf", "%H:%M",
                f"eventsFrom:{start_date.strftime('%Y-%m-%d')}",
                f"to:{end_date.strftime('%Y-%m-%d')}"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and result.stdout.strip():
                return self._parse_icalbuddy_output(result.stdout)
        except Exception as e:
            print(f"Direct icalBuddy failed: {e}")

        return []

    def _try_shell_script(self, start_date, end_date):
        """Try using shell script wrapper."""
        try:
            script_path = Path(__file__).parent.parent / "get_calendar_data.sh"
            if script_path.exists():
                cmd = [
                    str(script_path),
                    "events",
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                if result.returncode == 0 and result.stdout.strip():
                    return self._parse_icalbuddy_output(result.stdout)
                else:
                    print(f"Shell script failed: {result.stderr}")
        except Exception as e:
            print(f"Shell script approach failed: {e}")

        return []

    def _load_cached_events(self, start_date: date, end_date: date) -> List[CalendarEvent]:
        """Load events from cache for the given date range."""
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)

            events = []
            for event_dict in cache_data.get("events", []):
                event = self._dict_to_event(event_dict)
                if event:
                    # Filter by date range
                    event_date = event.start.date()
                    if start_date <= event_date <= end_date:
                        events.append(event)

            return events

        except Exception as e:
            print(f"Warning: Failed to load cached events: {e}")
            return []

    def _parse_icalbuddy_output(self, output: str) -> List[CalendarEvent]:
        """Parse icalBuddy output into CalendarEvent objects."""
        events = []
        lines = output.strip().split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if line.startswith('• '):
                event_title = line[2:].strip()

                # Parse datetime from next line if it exists
                datetime_str = None
                location = None
                notes = None
                attendees = []

                # Look for datetime on next line
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    # Check if it looks like a datetime
                    if re.match(r'\d{4}-\d{2}-\d{2}', next_line):
                        datetime_str = next_line
                        i += 1  # Skip this line

                        # Look for additional details
                        while i + 1 < len(lines):
                            detail_line = lines[i + 1].strip()
                            if detail_line.startswith('• '):
                                break  # Next event

                            if detail_line.startswith('location:'):
                                location = detail_line[9:].strip()
                            elif detail_line.startswith('notes:'):
                                notes = detail_line[6:].strip()
                            elif detail_line.startswith('attendees:'):
                                attendees_str = detail_line[10:].strip()
                                if attendees_str and attendees_str != '(null)':
                                    # Parse attendee format
                                    attendee_matches = re.findall(r'([^<]+)<([^>]+)>', attendees_str)
                                    for name, email in attendee_matches:
                                        attendees.append(Attendee(name=name.strip(), email=email.strip()))

                            i += 1
                            if not detail_line:
                                break

                # Create event if we have datetime
                if datetime_str and event_title:
                    try:
                        event = self._parse_event_datetime(event_title, datetime_str, location, notes, attendees)
                        if event:
                            events.append(event)
                    except Exception as e:
                        print(f"Warning: Failed to parse event '{event_title}': {e}")

            i += 1

        return events

    def _parse_event_datetime(self, title: str, datetime_str: str, location: str = None,
                            notes: str = None, attendees: List[Attendee] = None) -> Optional[CalendarEvent]:
        """Parse event datetime string."""
        try:
            # Handle formats like:
            # "2024-11-17 10:00 - 11:00"
            # "2024-11-17 at 10:00"
            datetime_match = re.match(r'(\d{4}-\d{2}-\d{2})\s+(?:at\s+)?(\d{1,2}:\d{2})\s*(?:-\s*(\d{1,2}:\d{2}))?', datetime_str)

            if datetime_match:
                date_str = datetime_match.group(1)
                start_time = datetime_match.group(2)
                end_time = datetime_match.group(3) or start_time  # Default to same time

                start_datetime = datetime.strptime(f"{date_str} {start_time}", "%Y-%m-%d %H:%M")
                end_datetime = datetime.strptime(f"{date_str} {end_time}", "%Y-%m-%d %H:%M")

                # If end time is earlier than start time, assume next day
                if end_datetime <= start_datetime:
                    end_datetime += timedelta(days=1)

                return CalendarEvent(
                    title=title,
                    start=start_datetime,
                    end=end_datetime,
                    location=location,
                    notes=notes,
                    attendees=attendees or []
                )

        except Exception as e:
            print(f"Warning: Failed to parse datetime '{datetime_str}': {e}")

        return None

    def _event_to_dict(self, event: CalendarEvent) -> Dict[str, Any]:
        """Convert CalendarEvent to dictionary for JSON storage."""
        return {
            "title": event.title,
            "start": event.start.isoformat(),
            "end": event.end.isoformat(),
            "location": event.location,
            "notes": event.notes,
            "attendees": [{"name": a.name, "email": a.email} for a in event.attendees]
        }

    def _dict_to_event(self, data: Dict[str, Any]) -> Optional[CalendarEvent]:
        """Convert dictionary back to CalendarEvent."""
        try:
            return CalendarEvent(
                title=data["title"],
                start=datetime.fromisoformat(data["start"]),
                end=datetime.fromisoformat(data["end"]),
                location=data.get("location"),
                notes=data.get("notes"),
                attendees=[Attendee(name=a["name"], email=a["email"]) for a in data.get("attendees", [])]
            )
        except Exception as e:
            print(f"Warning: Failed to convert cached event: {e}")
            return None
