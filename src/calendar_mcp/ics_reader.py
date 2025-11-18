"""Direct .ics file reading for macOS Calendar."""

import os
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
from dateutil import rrule, tz
from icalendar import Calendar, Event

from .models import CalendarEvent, Attendee


class CalendarICSReader:
    """Reads calendar events directly from macOS .ics files."""

    def __init__(self, calendar_directories: Optional[List[str]] = None):
        """Initialize the ICS reader.

        Args:
            calendar_directories: Custom calendar directory paths.
                                 If None, uses default macOS locations.
        """
        if calendar_directories:
            self.calendar_dirs = [Path(d) for d in calendar_directories]
        else:
            # Default macOS Calendar locations
            home = Path.home()
            self.calendar_dirs = [
                home / "Library" / "Calendars",  # Local calendars
            ]

    def discover_calendar_files(self) -> List[Path]:
        """Discover all .ics files in calendar directories.

        Returns:
            List of .ics file paths
        """
        ics_files = []

        for calendar_dir in self.calendar_dirs:
            if calendar_dir.exists() and calendar_dir.is_dir():
                # Find all .ics files recursively
                for ics_file in calendar_dir.rglob("*.ics"):
                    # Skip hidden files and directories
                    if not any(part.startswith('.') for part in ics_file.parts):
                        ics_files.append(ics_file)

        return sorted(ics_files)

    def get_events_in_range(self, start_date: date, end_date: date,
                          calendar_names: Optional[List[str]] = None) -> List[CalendarEvent]:
        """Get all events within the specified date range.

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            calendar_names: Optional list of calendar names to include

        Returns:
            List of CalendarEvent objects within the date range
        """
        all_events = []

        # Discover and parse all .ics files
        ics_files = self.discover_calendar_files()

        for ics_file in ics_files:
            try:
                events = self.parse_ics_file(ics_file)
                all_events.extend(events)
            except Exception as e:
                # Skip files that can't be parsed
                print(f"Warning: Could not parse {ics_file}: {e}")
                continue

        # Filter events by date range
        filtered_events = []
        for event in all_events:
            # Convert datetime to date for comparison
            event_date = event.start.date() if isinstance(event.start, datetime) else event.start

            if start_date <= event_date <= end_date:
                filtered_events.append(event)

        # Filter by calendar names if specified
        if calendar_names:
            # For now, we don't have calendar name metadata in the events
            # This would require extracting calendar names from file paths
            # or parsing additional calendar metadata
            pass

        return sorted(filtered_events, key=lambda e: e.start)

    def parse_ics_file(self, file_path: Path) -> List[CalendarEvent]:
        """Parse a single .ics file and extract events.

        Args:
            file_path: Path to the .ics file

        Returns:
            List of CalendarEvent objects
        """
        events = []

        try:
            with open(file_path, 'rb') as f:
                cal_data = f.read()

            cal = Calendar.from_ical(cal_data)

            for component in cal.walk('VEVENT'):
                event = self._parse_vevent(component)
                if event:
                    events.append(event)

        except Exception as e:
            raise RuntimeError(f"Failed to parse {file_path}: {e}") from e

        return events

    def _parse_vevent(self, component: Event) -> Optional[CalendarEvent]:
        """Parse a single VEVENT component.

        Args:
            component: icalendar Event component

        Returns:
            CalendarEvent object or None if parsing fails
        """
        try:
            # Extract basic properties
            summary = component.get('summary', '')
            if not summary:
                return None  # Skip events without titles

            # Parse start and end times
            dtstart = component.get('dtstart')
            dtend = component.get('dtend')

            if not dtstart:
                return None  # Skip events without start time

            # Handle different datetime formats
            start_datetime = self._parse_datetime(dtstart)
            end_datetime = self._parse_datetime(dtend) if dtend else start_datetime + timedelta(hours=1)

            # Extract other properties
            location = str(component.get('location', '')).strip()
            description = str(component.get('description', '')).strip()

            # Parse attendees
            attendees = self._parse_attendees(component)

            return CalendarEvent(
                title=str(summary),
                start=start_datetime,
                end=end_datetime,
                attendees=attendees,
                location=location if location else None,
                notes=description if description else None
            )

        except Exception as e:
            # Skip malformed events
            print(f"Warning: Could not parse VEVENT: {e}")
            return None

    def _parse_datetime(self, dt_value) -> datetime:
        """Parse icalendar datetime object into Python datetime.

        Args:
            dt_value: icalendar datetime object

        Returns:
            Python datetime object
        """
        if hasattr(dt_value, 'dt'):
            # It's already a datetime object
            dt = dt_value.dt
        else:
            dt = dt_value

        # Ensure it's a datetime object (not just date)
        if isinstance(dt, date) and not isinstance(dt, datetime):
            # Convert date to datetime at midnight
            dt = datetime.combine(dt, datetime.min.time())

        # Add timezone if missing
        if dt.tzinfo is None:
            # Assume local timezone
            dt = dt.replace(tzinfo=tz.gettz())

        return dt

    def _parse_attendees(self, component: Event) -> List[Attendee]:
        """Parse attendee information from VEVENT component.

        Args:
            component: icalendar Event component

        Returns:
            List of Attendee objects
        """
        attendees = []
        attendee_list = component.get('attendee', [])

        # Handle both single attendee and list of attendees
        if not isinstance(attendee_list, list):
            attendee_list = [attendee_list]

        for attendee_data in attendee_list:
            if attendee_data:
                attendee = self._parse_single_attendee(attendee_data)
                if attendee:
                    attendees.append(attendee)

        return attendees

    def _parse_single_attendee(self, attendee_data) -> Optional[Attendee]:
        """Parse a single attendee entry.

        Args:
            attendee_data: Raw attendee data from icalendar

        Returns:
            Attendee object or None
        """
        try:
            # attendee_data might be a string like "mailto:name@example.com"
            # or a more complex object
            attendee_str = str(attendee_data)

            # Extract email and name
            if attendee_str.startswith('mailto:'):
                email = attendee_str[7:]
                name = email.split('@')[0]  # Use email prefix as name if no name provided
                return Attendee(name=name, email=email)
            else:
                # Try to parse "Name <email>" format
                import re
                match = re.match(r'([^<]+)<([^>]+)>', attendee_str)
                if match:
                    name = match.group(1).strip()
                    email = match.group(2).strip()
                    return Attendee(name=name, email=email)

                # Fallback: treat as email
                return Attendee(name=attendee_str, email=attendee_str)

        except Exception:
            return None

    def list_calendars(self) -> List[str]:
        """List available calendar names.

        Returns:
            List of calendar names found in .ics files
        """
        calendar_names = set()

        ics_files = self.discover_calendar_files()

        for ics_file in ics_files:
            try:
                # Extract calendar name from file path or content
                # For now, just extract from path structure
                parts = ics_file.parts

                # Look for calendar name in path (usually a directory name)
                for part in reversed(parts):
                    if part.endswith('.calendar') or part.endswith('.caldav'):
                        calendar_names.add(part.rsplit('.', 1)[0])
                        break

            except Exception:
                continue

        return sorted(list(calendar_names))


def get_events_in_range(start_date: date, end_date: date,
                      calendar_names: Optional[List[str]] = None) -> List[CalendarEvent]:
    """Convenience function to get events in date range.

    Args:
        start_date: Start date
        end_date: End date
        calendar_names: Optional calendar names to filter by

    Returns:
        List of CalendarEvent objects
    """
    reader = CalendarICSReader()
    return reader.get_events_in_range(start_date, end_date, calendar_names)


def list_available_calendars() -> List[str]:
    """Convenience function to list available calendars.

    Returns:
        List of calendar names
    """
    reader = CalendarICSReader()
    return reader.list_calendars()






