"""Calendar data extraction using icalBuddy."""

import subprocess
import re
from datetime import datetime, date
from typing import List, Optional
from dateutil import parser as date_parser

from .models import CalendarEvent, Attendee


class CalendarExtractor:
    """Extract calendar events using icalBuddy."""

    def __init__(self, calendars: Optional[List[str]] = None):
        """Initialize the calendar extractor.

        Args:
            calendars: List of calendar names to query. If None, queries all calendars.
        """
        self.icalbuddy_cmd = ["icalBuddy"]
        self.calendars = calendars

    def _run_icalbuddy(self, args: List[str]) -> str:
        """Run icalBuddy command and return output."""
        cmd = self.icalbuddy_cmd + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"icalBuddy command failed: {e.stderr}") from e
        except FileNotFoundError:
            raise RuntimeError("icalBuddy not found. Please install icalBuddy: brew install ical-buddy")

    def get_events(self, start_date: date, end_date: date) -> List[CalendarEvent]:
        """Get calendar events for the specified date range.

        Args:
            start_date: Start date for events
            end_date: End date for events

        Returns:
            List of CalendarEvent objects
        """
        # Format dates for icalBuddy
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        # Build icalBuddy command
        # -iep: include event properties
        # eventsFrom:to: - date range
        args = [
            "-iep", "title,datetime,attendees,notes,location",
            f"eventsFrom:{start_str}",
            f"to:{end_str}"
        ]

        # Add calendar selection if specified
        if self.calendars:
            for calendar in self.calendars:
                args.extend(["-ic", calendar])

        output = self._run_icalbuddy(args)
        return self._parse_icalbuddy_output(output)

    def _parse_icalbuddy_output(self, output: str) -> List[CalendarEvent]:
        """Parse icalBuddy output into CalendarEvent objects.

        icalBuddy output format:
        • Event Title
            datetime: 2024-01-15 10:00:00 +0000 to 2024-01-15 11:00:00 +0000
            attendees: Name <email@example.com>, Another <email2@example.com>
            notes: Some notes here
            location: Conference Room A

        Returns:
            List of parsed CalendarEvent objects
        """
        events = []
        lines = output.strip().split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for event titles (start with bullet point)
            if line.startswith('• '):
                event_title = line[2:]  # Remove bullet point

                # Parse event details
                event_data = self._parse_event_details(lines, i + 1)
                if event_data:
                    try:
                        event = self._create_event_from_data(event_title, event_data)
                        if event:
                            events.append(event)
                    except Exception as e:
                        # Skip malformed events but continue parsing
                        print(f"Warning: Failed to parse event '{event_title}': {e}")
                        continue

                # Skip to next event (find next bullet point or end)
                while i < len(lines) and not lines[i].strip().startswith('• '):
                    i += 1
                continue

            i += 1

        return events

    def _parse_event_details(self, lines: List[str], start_idx: int) -> dict:
        """Parse event details from icalBuddy output lines."""
        details = {}
        i = start_idx

        while i < len(lines):
            line = lines[i].strip()

            # Stop if we hit another event or end of relevant content
            if line.startswith('• ') or not line:
                break

            # Parse different detail types
            if line.startswith('datetime:'):
                details['datetime'] = line[9:].strip()
            elif line.startswith('attendees:'):
                details['attendees'] = line[10:].strip()
            elif line.startswith('notes:'):
                details['notes'] = line[6:].strip()
            elif line.startswith('location:'):
                details['location'] = line[9:].strip()

            i += 1

        return details

    def _create_event_from_data(self, title: str, data: dict) -> Optional[CalendarEvent]:
        """Create a CalendarEvent from parsed data."""
        # Parse datetime
        datetime_str = data.get('datetime', '')
        if not datetime_str:
            return None

        # Parse datetime range: "2024-01-15 10:00:00 +0000 to 2024-01-15 11:00:00 +0000"
        datetime_match = re.match(
            r'(.+?) to (.+)',
            datetime_str
        )

        if not datetime_match:
            return None

        try:
            start_str = datetime_match.group(1).strip()
            end_str = datetime_match.group(2).strip()

            # Parse with dateutil (handles various formats and timezones)
            start_datetime = date_parser.parse(start_str)
            end_datetime = date_parser.parse(end_str)

        except Exception:
            return None

        # Parse attendees
        attendees = []
        attendees_str = data.get('attendees', '')
        if attendees_str and attendees_str != '(null)':
            # Parse: "Name <email@example.com>, Another <email2@example.com>"
            attendee_matches = re.findall(r'([^<]+)<([^>]+)>', attendees_str)
            for name, email in attendee_matches:
                attendees.append(Attendee(
                    name=name.strip(),
                    email=email.strip()
                ))

        # Get other fields
        location = data.get('location')
        if location == '(null)':
            location = None

        notes = data.get('notes')
        if notes == '(null)':
            notes = None

        return CalendarEvent(
            title=title,
            start=start_datetime,
            end=end_datetime,
            attendees=attendees,
            location=location,
            notes=notes
        )

    def list_calendars(self) -> List[str]:
        """List all available calendars.

        Returns:
            List of calendar names
        """
        try:
            output = self._run_icalbuddy(["calendars"])
            # Parse calendar names from output
            # icalBuddy outputs calendars in format:
            # • Calendar Name
            # • Another Calendar
            calendars = []
            for line in output.strip().split('\n'):
                line = line.strip()
                if line.startswith('• '):
                    calendar_name = line[2:].strip()
                    calendars.append(calendar_name)
            return calendars
        except RuntimeError:
            return []

    def test_connection(self) -> bool:
        """Test if icalBuddy is available and working."""
        try:
            self._run_icalbuddy(["-V"])  # Version check
            return True
        except RuntimeError:
            return False
