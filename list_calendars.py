#!/usr/bin/env python3
"""Utility script to list available calendars for configuration."""

from src.calendar_mcp.calendar_extractor import CalendarExtractor

def main():
    """List available calendars."""
    print("Checking available calendars...")
    print("=" * 50)

    extractor = CalendarExtractor()

    # Test connection
    if not extractor.test_connection():
        print("❌ icalBuddy not found or not working.")
        print("Please install icalBuddy: brew install ical-buddy")
        return 1

    # List calendars
    calendars = extractor.list_calendars()

    if not calendars:
        print("❌ No calendars found or unable to access calendars.")
        print("Make sure Calendar.app has permissions and calendars are set up.")
        return 1

    print("✅ Available calendars:")
    print()
    for i, calendar in enumerate(calendars, 1):
        print(f"  {i}. {calendar}")

    print()
    print("To use specific calendars, edit src/calendar_mcp/config.json:")
    print('''
{
  "calendar": {
    "calendars": ["''' + '", "'.join(calendars[:2]) + '''"]
  },
  ...
}
''')

    return 0

if __name__ == "__main__":
    exit(main())
