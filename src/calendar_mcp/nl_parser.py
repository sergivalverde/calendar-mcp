"""Natural language parsing for calendar event creation."""

import re
from datetime import date, datetime, time, timedelta
from typing import List, Optional, Tuple, Dict, Any

from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

from .models import EventRequest


class NaturalLanguageEventParser:
    """Parse natural language requests into structured event data."""

    def __init__(self):
        """Initialize the parser."""
        self.time_patterns = {
            'morning': time(9, 0),
            'afternoon': time(14, 0),
            'evening': time(18, 0),
            'noon': time(12, 0),
            'midnight': time(0, 0)
        }

    def parse_event_request(self, query: str) -> Optional[EventRequest]:
        """Parse a natural language event request.

        Args:
            query: Natural language query

        Returns:
            EventRequest object or None if parsing fails
        """
        query_lower = query.lower().strip()

        # Check for blocking time requests
        if self._is_blocking_request(query_lower):
            return self._parse_blocking_request(query)

        # Check for meeting requests
        if self._is_meeting_request(query_lower):
            return self._parse_meeting_request(query)

        # Parse general event creation
        return self._parse_general_event(query)

    def _is_blocking_request(self, query: str) -> bool:
        """Check if query is for blocking time."""
        blocking_keywords = ['block', 'blocking', 'focus', 'deep work', 'work on', 'concentrate']
        return any(keyword in query for keyword in blocking_keywords)

    def _is_meeting_request(self, query: str) -> bool:
        """Check if query is for scheduling a meeting."""
        meeting_keywords = ['meeting', 'meet with', 'schedule', 'propose', 'call with']
        return any(keyword in query for keyword in meeting_keywords)

    def _parse_blocking_request(self, query: str) -> Optional[EventRequest]:
        """Parse blocking time requests like 'block two mornings next week to work on X'."""
        try:
            # Extract count (e.g., "two", "three")
            count_match = re.search(r'\b(\w+)\s+(morning|afternoon|evening)s?\b', query)
            count = 1  # Default
            if count_match:
                count_word = count_match.group(1)
                count_map = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
                count = count_map.get(count_word, 1)

            # Extract time of day
            time_slot = 'morning'  # Default
            if 'afternoon' in query:
                time_slot = 'afternoon'
            elif 'evening' in query:
                time_slot = 'evening'

            # Extract purpose
            purpose = "Focused Work"  # Default
            if 'work on' in query:
                work_part = query.split('work on', 1)[1].strip()
                purpose = work_part.split('.')[0].strip()

            # Extract dates
            dates = self._extract_dates(query, count)
            if not dates:
                dates = [date.today() + timedelta(days=1)]  # Tomorrow default

            # Create events for each date
            start_time = self.time_patterns.get(time_slot, time(9, 0))
            start_datetime = datetime.combine(dates[0], start_time)
            end_datetime = start_datetime + timedelta(hours=3)  # 3 hours default

            return EventRequest(
                title=f"Blocked: {purpose}",
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                notes=f"Blocking time for {purpose}"
            )

        except Exception as e:
            print(f"Error parsing blocking request: {e}")
            return None

    def _parse_meeting_request(self, query: str) -> Optional[EventRequest]:
        """Parse meeting requests like 'meeting with Joe in two weeks, afternoon'."""
        try:
            # Extract attendees
            attendees = []
            attendee_pattern = r'\b(?:meet|meeting|call)\s+with\s+([A-Za-z\s]+?)(?:\s+in|\s+next|\s+tomorrow|\s+at|$)'
            attendee_match = re.search(attendee_pattern, query, re.IGNORECASE)
            if attendee_match:
                attendee_names = attendee_match.group(1).strip().split()
                attendees.extend(attendee_names)

            # Extract date
            event_date = self._extract_single_date(query)
            if not event_date:
                event_date = date.today() + timedelta(days=14)  # Two weeks default

            # Extract time preference
            time_preference = 'afternoon'  # Default
            if 'morning' in query:
                time_preference = 'morning'
            elif 'evening' in query:
                time_preference = 'evening'

            start_time = self.time_patterns.get(time_preference, time(14, 0))
            start_datetime = datetime.combine(event_date, start_time)
            end_datetime = start_datetime + timedelta(hours=1)  # 1 hour default

            attendee_str = ", ".join(attendees) if attendees else ""
            title = f"Meeting with {attendee_str}" if attendee_str else "Meeting"

            return EventRequest(
                title=title,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                notes=f"Meeting scheduled via natural language request"
            )

        except Exception as e:
            print(f"Error parsing meeting request: {e}")
            return None

    def _parse_general_event(self, query: str) -> Optional[EventRequest]:
        """Parse general event creation like 'Add dentist appointment tomorrow at 2pm'."""
        try:
            # Extract title
            title = self._extract_title(query)

            # Extract date and time
            event_datetime = self._extract_datetime(query)
            if not event_datetime:
                return None

            # Assume 1 hour duration if not specified
            duration = self._extract_duration(query)
            end_datetime = event_datetime + duration

            return EventRequest(
                title=title,
                start_datetime=event_datetime,
                end_datetime=end_datetime
            )

        except Exception as e:
            print(f"Error parsing general event: {e}")
            return None

    def _extract_title(self, query: str) -> str:
        """Extract event title from query."""
        # Remove common prefixes
        title = query
        prefixes = ['add ', 'create ', 'schedule ', 'make ', 'set up ']
        for prefix in prefixes:
            if title.lower().startswith(prefix):
                title = title[len(prefix):].strip()
                break

        # Remove time/date information
        time_patterns = [
            r'\s+tomorrow\s+at\s+.*',
            r'\s+at\s+\d+(?::\d+)?(?:\s*[ap]m)?',
            r'\s+in\s+\d+\s+days?',
            r'\s+next\s+\w+',
            r'\s+on\s+\w+',
            r'\s+for\s+\d+\s*(?:hour|minute|min|hr)s?'
        ]

        for pattern in time_patterns:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)

        return title.strip() or "New Event"

    def _extract_datetime(self, query: str) -> Optional[datetime]:
        """Extract date and time from query."""
        try:
            # Use dateutil parser with some preprocessing
            query_clean = query.lower()

            # Handle relative dates
            if 'tomorrow' in query_clean:
                base_date = date.today() + timedelta(days=1)
            elif 'today' in query_clean:
                base_date = date.today()
            else:
                base_date = date.today()

            # Try to parse with dateutil
            try:
                parsed = date_parser.parse(query, fuzzy=True, default=base_date)
                return parsed
            except:
                # Fallback: look for time patterns
                time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', query, re.IGNORECASE)
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2) or 0)
                    ampm = time_match.group(3)

                    if ampm and ampm.lower() == 'pm' and hour != 12:
                        hour += 12
                    elif ampm and ampm.lower() == 'am' and hour == 12:
                        hour = 0

                    return datetime.combine(base_date, time(hour, minute))

                return datetime.combine(base_date, time(9, 0))  # 9 AM default

        except Exception as e:
            print(f"Error extracting datetime: {e}")
            return None

    def _extract_duration(self, query: str) -> timedelta:
        """Extract duration from query."""
        # Default 1 hour
        duration_match = re.search(r'for\s+(\d+)\s*(hour|hr|minute|min)s?', query, re.IGNORECASE)
        if duration_match:
            amount = int(duration_match.group(1))
            unit = duration_match.group(2).lower()

            if 'hour' in unit or 'hr' in unit:
                return timedelta(hours=amount)
            elif 'minute' in unit or 'min' in unit:
                return timedelta(minutes=amount)

        return timedelta(hours=1)

    def _extract_dates(self, query: str, count: int) -> List[date]:
        """Extract multiple dates from query."""
        # For now, just return the next N weekdays
        dates = []
        current_date = date.today()

        while len(dates) < count:
            current_date += timedelta(days=1)
            if current_date.weekday() < 5:  # Monday-Friday
                dates.append(current_date)

        return dates

    def _extract_single_date(self, query: str) -> Optional[date]:
        """Extract a single date from query."""
        query_lower = query.lower()

        if 'tomorrow' in query_lower:
            return date.today() + timedelta(days=1)
        elif 'today' in query_lower:
            return date.today()
        elif 'two weeks' in query_lower:
            return date.today() + timedelta(weeks=2)
        elif 'next week' in query_lower:
            return date.today() + timedelta(weeks=1)
        else:
            # Try to parse other relative dates
            try:
                parsed = date_parser.parse(query, fuzzy=True)
                return parsed.date()
            except:
                return date.today() + timedelta(days=1)  # Tomorrow default


def parse_event_request(query: str) -> Optional[EventRequest]:
    """Convenience function to parse event requests.

    Args:
        query: Natural language query

    Returns:
        EventRequest object or None
    """
    parser = NaturalLanguageEventParser()
    return parser.parse_event_request(query)






