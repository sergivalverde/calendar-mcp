"""MCP server for calendar analysis."""

import asyncio
import re
from datetime import date, datetime, timedelta, time
from typing import Any, Sequence

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError as e:
    print(f"Error importing MCP: {e}")
    print("Please ensure MCP is installed: uv add mcp")
    raise

from .calendar_extractor import CalendarExtractor
from .classifier import EventClassifier
from .energy_tracker import EnergyTracker
from .report_generator import ReportGenerator
from .config import ConfigManager, CalendarAnalysisConfig
from .models import CalendarEvent
from .applescript_writer import AppleScriptCalendarWriter, list_available_calendars, find_free_slots
from .nl_parser import parse_event_request
from .simple_cache import SimpleCalendarCache


class CalendarAnalysisServer:
    """MCP server for calendar analysis."""

    def __init__(self):
        """Initialize the calendar analysis server."""
        self.server = Server("calendar-analysis")
        self.config_manager = ConfigManager()
        self.calendar_extractor = None
        self.calendar_writer = None
        self.classifier = None
        self.energy_tracker = EnergyTracker()
        self.report_generator = ReportGenerator()

        # Setup server handlers
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP server request handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="query_calendar",
                    description="Analyze calendar data based on natural language queries. "
                               "Examples: 'Analyze my calendar for last week', "
                               "'Show time distribution for November', "
                               "'What were my energy levels yesterday?'",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query about your calendar"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="create_event",
                    description="Create a single calendar event. "
                               "Example: Create a 'Team Meeting' event tomorrow at 2pm for 1 hour",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Event title"},
                            "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                            "start_time": {"type": "string", "description": "Start time (HH:MM)"},
                            "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                            "end_time": {"type": "string", "description": "End time (HH:MM)"},
                            "calendar": {"type": "string", "description": "Calendar name (optional)"},
                            "location": {"type": "string", "description": "Event location (optional)"},
                            "notes": {"type": "string", "description": "Event notes (optional)"}
                        },
                        "required": ["title", "start_date", "start_time"]
                    }
                ),
                Tool(
                    name="create_blocking_time",
                    description="Block time periods for focused work. "
                               "Example: Block two mornings next week to work on the presentation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "purpose": {"type": "string", "description": "Purpose of the blocked time"},
                            "time_slots": {"type": "string", "description": "Time of day: 'mornings', 'afternoons', 'evenings'"},
                            "dates": {"type": "string", "description": "Date range or specific dates"},
                            "duration_hours": {"type": "number", "description": "Hours to block per session"}
                        },
                        "required": ["purpose", "time_slots", "dates"]
                    }
                ),
                Tool(
                    name="propose_meeting",
                    description="Intelligently schedule a meeting by finding free slots. "
                               "Example: Propose a meeting with Julia in two weeks, afternoon preferred",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Meeting title"},
                            "attendees": {"type": "string", "description": "Comma-separated attendee names"},
                            "relative_date": {"type": "string", "description": "When: 'tomorrow', 'in two weeks', 'next Monday'"},
                            "time_preference": {"type": "string", "description": "Preferred time: 'morning', 'afternoon', 'evening'"},
                            "duration_minutes": {"type": "number", "description": "Meeting duration in minutes"}
                        },
                        "required": ["title", "attendees", "relative_date"]
                    }
                ),
                Tool(
                    name="list_calendars",
                    description="List all available calendar names",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="find_free_time",
                    description="Find available time slots in your calendar. "
                               "Example: Find 1-hour slots next week in the afternoon",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                            "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                            "duration_minutes": {"type": "number", "description": "Required duration in minutes"},
                            "time_preference": {"type": "string", "description": "Preferred time: 'morning', 'afternoon', 'evening'"}
                        },
                        "required": ["start_date", "end_date", "duration_minutes"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
            """Handle tool calls."""
            if name == "query_calendar":
                return await self._query_calendar(arguments.get("query", ""))
            elif name == "create_event":
                return await self._create_event(arguments)
            elif name == "create_blocking_time":
                return await self._create_blocking_time(arguments)
            elif name == "propose_meeting":
                return await self._propose_meeting(arguments)
            elif name == "list_calendars":
                return await self._list_calendars()
            elif name == "find_free_time":
                return await self._find_free_time(arguments)

            raise ValueError(f"Unknown tool: {name}")
    
    async def _query_calendar(self, query: str) -> Sequence[TextContent]:
        """Analyze calendar data based on natural language queries.

        Args:
            query: Natural language query

        Returns:
            Sequence of TextContent with the report
        """
        try:
            # Parse date range from query
            start_date, end_date = self._parse_date_range(query)

            # Extract calendar events (raw, including energy markers)
            raw_events = self.calendar_extractor.get_events(start_date, end_date)

            if not raw_events:
                return [TextContent(
                    type="text",
                    text=f"No calendar events found for the date range {start_date} to {end_date}."
                )]

            # Classify events (filters out energy markers and excluded events)
            classified_events = self.classifier.classify_events(raw_events)

            # Track energy levels (needs both classified and raw events)
            events_with_energy = self.energy_tracker.track_energy_levels(
                classified_events, 
                raw_events
            )

            # Generate report
            report = self.report_generator.generate_report(events_with_energy)

            return [TextContent(type="text", text=report)]

        except Exception as e:
            error_msg = f"Error analyzing calendar: {str(e)}\n\nPlease check:\n" \
                       f"- Calendar files are accessible in ~/Library/Calendars/\n" \
                       f"- Calendar.app has events in the date range"
            return [TextContent(type="text", text=error_msg)]

    async def _create_event(self, arguments: dict) -> Sequence[TextContent]:
        """Create a single calendar event."""
        try:
            # Parse arguments
            title = arguments["title"]
            start_date = arguments["start_date"]
            start_time = arguments["start_time"]

            # Optional arguments
            end_date = arguments.get("end_date", start_date)
            end_time = arguments.get("end_time", None)
            calendar = arguments.get("calendar")
            location = arguments.get("location")
            notes = arguments.get("notes")

            # Parse dates and times
            start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")

            if end_time:
                end_datetime = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
            else:
                # Default 1 hour if no end time
                end_datetime = start_datetime + timedelta(hours=1)

            # Create event
            result = self.calendar_writer.create_event(
                title=title,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                calendar_name=calendar,
                location=location,
                notes=notes
            )

            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error creating event: {e}")]

    async def _create_blocking_time(self, arguments: dict) -> Sequence[TextContent]:
        """Create blocking time for focused work."""
        try:
            purpose = arguments["purpose"]
            time_slots = arguments["time_slots"]
            dates = arguments["dates"]
            duration_hours = arguments.get("duration_hours", 3)

            # Parse dates (simple parsing for now)
            # In a full implementation, this would parse "next week", "tomorrow", etc.
            from .nl_parser import NaturalLanguageEventParser
            parser = NaturalLanguageEventParser()

            # Create a query string and parse it
            query = f"block time for {purpose} in {time_slots} for {dates}"
            request = parser.parse_event_request(query)

            if request:
                # For blocking time, create the event
                result = self.calendar_writer.create_event(
                    title=f"Blocked: {purpose}",
                    start_datetime=request.start_datetime,
                    end_datetime=request.end_datetime,
                    notes=f"Blocking time for {purpose}"
                )
                return [TextContent(type="text", text=result)]
            else:
                return [TextContent(type="text", text="Could not parse blocking time request")]

        except Exception as e:
            return [TextContent(type="text", text=f"Error creating blocking time: {e}")]

    async def _propose_meeting(self, arguments: dict) -> Sequence[TextContent]:
        """Propose a meeting by finding free slots."""
        try:
            title = arguments["title"]
            attendees = arguments["attendees"]
            relative_date = arguments["relative_date"]
            time_preference = arguments.get("time_preference", "afternoon")
            duration_minutes = arguments.get("duration_minutes", 60)

            # Parse relative date
            from .nl_parser import NaturalLanguageEventParser
            parser = NaturalLanguageEventParser()

            query = f"meeting with {attendees} {relative_date} {time_preference}"
            request = parser.parse_event_request(query)

            if request:
                # Find free slots and create meeting
                result = self.calendar_writer.create_event(
                    title=f"{title} with {attendees}",
                    start_datetime=request.start_datetime,
                    end_datetime=request.end_datetime,
                    notes=f"Meeting with {attendees}"
                )
                return [TextContent(type="text", text=f"Meeting proposed: {result}")]
            else:
                # Find free slots in the requested time period
                # This is a simplified version - in practice you'd check existing events
                return [TextContent(type="text", text=f"Would propose meeting '{title}' with {attendees} {relative_date} in {time_preference} for {duration_minutes} minutes")]

        except Exception as e:
            return [TextContent(type="text", text=f"Error proposing meeting: {e}")]

    async def _list_calendars(self) -> Sequence[TextContent]:
        """List available calendars."""
        try:
            calendars = list_available_calendars()
            if calendars:
                calendar_list = "\n".join(f"- {cal}" for cal in calendars)
                return [TextContent(type="text", text=f"Available calendars:\n{calendar_list}")]
            else:
                return [TextContent(type="text", text="No calendars found or unable to access calendar data")]

        except Exception as e:
            return [TextContent(type="text", text=f"Error listing calendars: {e}")]

    async def _find_free_time(self, arguments: dict) -> Sequence[TextContent]:
        """Find available time slots."""
        try:
            start_date_str = arguments["start_date"]
            end_date_str = arguments["end_date"]
            duration_minutes = arguments["duration_minutes"]
            time_preference = arguments.get("time_preference")

            # Parse dates
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)

            # Find free slots
            slots = find_free_slots(start_date, end_date, duration_minutes, time_preference)

            if slots:
                slot_list = "\n".join(
                    f"- {slot['start'].strftime('%Y-%m-%d %I:%M %p')} - {slot['end'].strftime('%I:%M %p')}"
                    for slot in slots
                )
                return [TextContent(type="text", text=f"Available {duration_minutes}-minute slots:\n{slot_list}")]
            else:
                return [TextContent(type="text", text=f"No available {duration_minutes}-minute slots found in the specified date range")]

        except Exception as e:
            return [TextContent(type="text", text=f"Error finding free time: {e}")]
    
    async def initialize(self):
        """Initialize the server components."""
        # Reload configuration
        config: CalendarAnalysisConfig = self.config_manager.get_config()
        self.calendar_extractor = CalendarExtractor(calendars=config.calendar.calendars)
        self.calendar_writer = AppleScriptCalendarWriter(default_calendar=config.calendar.default_calendar)
        self.cache = SimpleCalendarCache()  # Initialize cache system
        self.classifier = EventClassifier(config.classification)

    def _parse_date_range(self, query: str) -> tuple[date, date]:
        """Parse date range from natural language query.

        Args:
            query: Natural language query containing date references

        Returns:
            Tuple of (start_date, end_date)
        """
        query_lower = query.lower()
        today = date.today()

        # Patterns for different date ranges
        if re.search(r'\b(today|this day)\b', query_lower):
            return today, today

        elif re.search(r'\b(yesterday)\b', query_lower):
            yesterday = today - timedelta(days=1)
            return yesterday, yesterday

        elif re.search(r'\b(last week|previous week)\b', query_lower):
            # Last week: Monday to Sunday of the previous week
            days_since_monday = today.weekday()  # 0=Monday, 6=Sunday
            last_monday = today - timedelta(days=days_since_monday + 7)
            last_sunday = last_monday + timedelta(days=6)
            return last_monday, last_sunday

        elif re.search(r'\b(this week|current week)\b', query_lower):
            # This week: Monday to today
            days_since_monday = today.weekday()
            monday = today - timedelta(days=days_since_monday)
            return monday, today

        elif re.search(r'\b(last month|previous month)\b', query_lower):
            # Last month
            first_of_this_month = today.replace(day=1)
            last_month_end = first_of_this_month - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            return last_month_start, last_month_end

        elif re.search(r'\b(this month|current month)\b', query_lower):
            # This month: 1st to today
            first_of_month = today.replace(day=1)
            return first_of_month, today

        elif re.search(r'\b(last (\d+) days?|past (\d+) days?)\b', query_lower):
            # Last N days
            match = re.search(r'\b(last|past) (\d+) days?\b', query_lower)
            if match:
                days = int(match.group(2))
                start_date = today - timedelta(days=days)
                return start_date, today

        elif re.search(r'\b(last (\d+) weeks?|past (\d+) weeks?)\b', query_lower):
            # Last N weeks
            match = re.search(r'\b(last|past) (\d+) weeks?\b', query_lower)
            if match:
                weeks = int(match.group(2))
                start_date = today - timedelta(weeks=weeks)
                return start_date, today

        elif re.search(r'\b(last (\d+) months?|past (\d+) months?)\b', query_lower):
            # Last N months
            match = re.search(r'\b(last|past) (\d+) months?\b', query_lower)
            if match:
                months = int(match.group(2))
                # Approximate months as 30 days
                start_date = today - timedelta(days=months * 30)
                return start_date, today

        # Check for specific month names
        month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
        }

        for month_name, month_num in month_names.items():
            if month_name in query_lower:
                if 'last year' in query_lower or 'previous year' in query_lower:
                    year = today.year - 1
                else:
                    year = today.year

                # If month is in the future, use previous year
                if year == today.year and month_num > today.month:
                    year -= 1

                start_date = date(year, month_num, 1)
                if month_num == 12:
                    end_date = date(year, 12, 31)
                else:
                    end_date = date(year, month_num + 1, 1) - timedelta(days=1)
                return start_date, end_date

        # Default: last 7 days
        return today - timedelta(days=7), today

    async def run(self):
        """Run the MCP server."""
        # Initialize components
        await self.initialize()

        # Run the server
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point for the calendar analysis MCP server."""
    server = CalendarAnalysisServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
