"""AppleScript-based calendar event creation for macOS."""

import subprocess
import re
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any

from .models import CalendarEvent, Attendee


class AppleScriptCalendarWriter:
    """Creates and manages calendar events using AppleScript."""

    def __init__(self, default_calendar: str = "Calendar"):
        """Initialize the AppleScript writer.

        Args:
            default_calendar: Default calendar name to use for events
        """
        self.default_calendar = default_calendar

    def create_event(self, title: str, start_datetime: datetime, end_datetime: datetime,
                    calendar_name: Optional[str] = None, location: Optional[str] = None,
                    notes: Optional[str] = None) -> str:
        """Create a single calendar event.

        Args:
            title: Event title
            start_datetime: Start date and time
            end_datetime: End date and time
            calendar_name: Calendar name (uses default if None)
            location: Event location
            notes: Event notes/description

        Returns:
            Success message or error
        """
        calendar_clause = f'calendar "{calendar_name}"' if calendar_name else f'calendar "{self.default_calendar}"'

        applescript = f'''
        tell application "Calendar"
            tell {calendar_clause}
                set newEvent to make new event with properties {{
                    summary:"{title}",
                    start date:date "{start_datetime.strftime('%m/%d/%Y %I:%M:%S %p')}",
                    end date:date "{end_datetime.strftime('%m/%d/%Y %I:%M:%S %p')}"
                }}
                {f'set location of newEvent to "{location}"' if location else ''}
                {f'set description of newEvent to "{notes}"' if notes else ''}
            end tell
        end tell
        '''

        try:
            result = subprocess.run(['osascript', '-e', applescript],
                                  capture_output=True, text=True, check=True)
            return f"✅ Created event: '{title}' on {start_datetime.strftime('%Y-%m-%d at %I:%M %p')}"
        except subprocess.CalledProcessError as e:
            return f"❌ Failed to create event: {e.stderr}"

    def create_blocking_events(self, purpose: str, dates: List[date],
                              time_slots: str = "mornings", duration_hours: int = 3,
                              calendar_name: Optional[str] = None) -> List[str]:
        """Create multiple blocking events for focused work.

        Args:
            purpose: Purpose/description for the blocking time
            dates: List of dates to create events for
            time_slots: Time of day ("mornings", "afternoons", "evenings")
            duration_hours: How many hours to block
            calendar_name: Calendar to use

        Returns:
            List of success/error messages
        """
        results = []

        for event_date in dates:
            start_time = self._get_time_for_slot(time_slots, event_date)
            if not start_time:
                results.append(f"❌ Invalid time slot: {time_slots}")
                continue

            start_datetime = datetime.combine(event_date, start_time)
            end_datetime = start_datetime + timedelta(hours=duration_hours)

            title = f"Blocked: {purpose}"
            result = self.create_event(title, start_datetime, end_datetime, calendar_name)
            results.append(result)

        return results

    def list_available_calendars(self) -> List[str]:
        """Get list of available calendar names.

        Returns:
            List of calendar names
        """
        applescript = '''
        tell application "Calendar"
            set calendarList to {}
            repeat with cal in calendars
                set end of calendarList to name of cal
            end repeat
            return calendarList
        end tell
        '''

        try:
            result = subprocess.run(['osascript', '-e', applescript],
                                  capture_output=True, text=True, check=True)
            # Parse the AppleScript list format
            output = result.stdout.strip()
            if output:
                # Remove leading/trailing braces and split by comma
                calendars = [cal.strip().strip('"') for cal in output.strip('{}').split(',')]
                return [cal for cal in calendars if cal]  # Filter out empty strings
            return []
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not list calendars: {e.stderr}")
            return []

    def find_free_slots(self, start_date: date, end_date: date,
                       duration_minutes: int = 60, preferred_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find available time slots in the given date range.

        Args:
            start_date: Start date to search
            end_date: End date to search
            duration_minutes: Required duration in minutes
            preferred_time: Preferred time of day ("morning", "afternoon", "evening")

        Returns:
            List of available time slots with start/end times
        """
        # For now, return some sample slots based on preferred time
        # In a full implementation, this would query existing events and find gaps
        slots = []

        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday-Friday
                day_slots = self._get_slots_for_day(current_date, duration_minutes, preferred_time)
                slots.extend(day_slots)
            current_date += timedelta(days=1)

        return slots[:10]  # Limit to 10 suggestions

    def _get_time_for_slot(self, time_slot: str, event_date: date) -> Optional[time]:
        """Convert time slot string to actual time.

        Args:
            time_slot: Time slot name ("mornings", "afternoons", "evenings")
            event_date: Date for the event

        Returns:
            time object or None if invalid
        """
        slot_lower = time_slot.lower()

        if 'morning' in slot_lower:
            return time(9, 0)  # 9:00 AM
        elif 'afternoon' in slot_lower:
            return time(14, 0)  # 2:00 PM
        elif 'evening' in slot_lower:
            return time(18, 0)  # 6:00 PM
        else:
            return time(9, 0)  # Default to morning

    def _get_slots_for_day(self, day: date, duration_minutes: int, preferred_time: Optional[str]) -> List[Dict[str, Any]]:
        """Get available slots for a specific day.

        Args:
            day: Date to check
            duration_minutes: Required duration
            preferred_time: Preferred time of day

        Returns:
            List of available time slots
        """
        slots = []

        # Define work hours
        work_start = time(9, 0)  # 9:00 AM
        work_end = time(17, 0)   # 5:00 PM

        # Focus on preferred time if specified
        if preferred_time:
            if preferred_time.lower() == 'morning':
                start_time = time(9, 0)
                end_time = time(12, 0)
            elif preferred_time.lower() == 'afternoon':
                start_time = time(14, 0)
                end_time = time(17, 0)
            elif preferred_time.lower() == 'evening':
                start_time = time(18, 0)
                end_time = time(21, 0)
            else:
                start_time = work_start
                end_time = work_end
        else:
            start_time = work_start
            end_time = work_end

        # Create a few sample slots (in real implementation, check against existing events)
        slot_duration = timedelta(minutes=duration_minutes)
        current_time = datetime.combine(day, start_time)

        while current_time + slot_duration <= datetime.combine(day, end_time):
            end_slot_time = current_time + slot_duration
            slots.append({
                'start': current_time,
                'end': end_slot_time,
                'duration_minutes': duration_minutes
            })
            # Skip ahead by the slot duration + 30 minutes
            current_time += timedelta(minutes=duration_minutes + 30)

        return slots


def create_blocking_events(purpose: str, dates: List[date], time_slots: str = "mornings",
                          duration_hours: int = 3, calendar_name: Optional[str] = None) -> List[str]:
    """Convenience function to create blocking events.

    Args:
        purpose: Purpose for blocking time
        dates: Dates to block
        time_slots: Time of day
        duration_hours: Hours to block
        calendar_name: Calendar to use

    Returns:
        List of results
    """
    writer = AppleScriptCalendarWriter(calendar_name or "Calendar")
    return writer.create_blocking_events(purpose, dates, time_slots, duration_hours, calendar_name)


def list_available_calendars() -> List[str]:
    """Convenience function to list calendars.

    Returns:
        List of calendar names
    """
    writer = AppleScriptCalendarWriter()
    return writer.list_available_calendars()


def find_free_slots(start_date: date, end_date: date, duration_minutes: int = 60,
                   preferred_time: Optional[str] = None) -> List[Dict[str, Any]]:
    """Convenience function to find free time slots.

    Args:
        start_date: Start date
        end_date: End date
        duration_minutes: Required duration
        preferred_time: Preferred time of day

    Returns:
        List of available slots
    """
    writer = AppleScriptCalendarWriter()
    return writer.find_free_slots(start_date, end_date, duration_minutes, preferred_time)






