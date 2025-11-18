"""Calendar data extraction using direct .ics file reading."""

from datetime import date
from typing import List, Optional

from .models import CalendarEvent
from .ics_reader import CalendarICSReader, list_available_calendars
from .simple_cache import SimpleCalendarCache


class CalendarExtractor:
    """Extract calendar events by reading .ics files directly."""

    def __init__(self, calendars: Optional[List[str]] = None,
                 calendar_directories: Optional[List[str]] = None):
        """Initialize the calendar extractor.

        Args:
            calendars: List of calendar names to query. If None, queries all calendars.
            calendar_directories: Custom calendar directory paths.
                                 If None, uses default macOS locations.
        """
        self.calendars = calendars
        self.calendar_directories = calendar_directories
        self.reader = CalendarICSReader(calendar_directories)
        self.cache = SimpleCalendarCache()  # Fallback cache system

    def get_events(self, start_date: date, end_date: date) -> List[CalendarEvent]:
        """Get calendar events for the specified date range.

        Args:
            start_date: Start date for events
            end_date: End date for events

        Returns:
            List of CalendarEvent objects
        """
        # Try direct ICS reading first
        try:
            events = self.reader.get_events_in_range(start_date, end_date, self.calendars)
            if events:  # If we got events, return them
                return events
        except (PermissionError, OSError) as e:
            # If direct access fails (permission denied), fall back to cache
            print(f"Direct calendar access failed ({e}), using cache system")
        except Exception as e:
            # For any other error, also try cache
            print(f"ICS reading error ({e}), falling back to cache")

        # Fall back to cache system
        return self.cache.get_events(start_date, end_date)

    def list_calendars(self) -> List[str]:
        """List all available calendars.

        Returns:
            List of calendar names
        """
        return list_available_calendars()

    def test_connection(self) -> bool:
        """Test if calendar files can be accessed."""
        try:
            ics_files = self.reader.discover_calendar_files()
            return len(ics_files) > 0
        except Exception:
            return False
