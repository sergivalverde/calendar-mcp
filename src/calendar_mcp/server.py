"""MCP server for calendar analysis."""

import asyncio
import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, List

from mcp import Tool
from mcp.server import Server
from mcp.types import TextContent, PromptMessage

from .calendar_extractor import CalendarExtractor
from .classifier import EventClassifier
from .energy_tracker import EnergyTracker
from .report_generator import ReportGenerator
from .config import ConfigManager
from .models import QueryRequest, CalendarAnalysisConfig


class CalendarAnalysisServer:
    """MCP server for calendar analysis."""

    def __init__(self):
        """Initialize the calendar analysis server."""
        self.server = Server("calendar-analysis")
        self.config_manager = ConfigManager()
        self.calendar_extractor = None
        self.classifier = None
        self.energy_tracker = EnergyTracker()
        self.report_generator = ReportGenerator()

    async def initialize(self):
        """Initialize the server and register tools."""
        # Reload configuration
        config: CalendarAnalysisConfig = self.config_manager.get_config()
        self.calendar_extractor = CalendarExtractor(calendars=config.calendar.calendars)
        self.classifier = EventClassifier(config.classification)

        # Register the query_calendar tool
        @self.server.tool()
        async def query_calendar(query: str) -> str:
            """Analyze calendar data based on natural language queries.

            Args:
                query: Natural language query (e.g., "Analyze my calendar for last week",
                       "Show time distribution for November", "What were my energy levels yesterday?")

            Returns:
                Comprehensive markdown report with tables and charts
            """
            try:
                # Parse date range from query
                start_date, end_date = self._parse_date_range(query)

                # Extract calendar events
                events = self.calendar_extractor.get_events(start_date, end_date)

                if not events:
                    return f"No calendar events found for the date range {start_date} to {end_date}."

                # Classify events
                classified_events = self.classifier.classify_events(events)

                # Track energy levels
                events_with_energy = self.energy_tracker.track_energy_levels(classified_events)

                # Generate report
                report = self.report_generator.generate_report(events_with_energy)

                return report

            except Exception as e:
                return f"Error analyzing calendar: {str(e)}"

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
