#!/usr/bin/env python3
"""Force update the calendar cache."""

from src.calendar_mcp.simple_cache import SimpleCalendarCache
from datetime import date

def main():
    print("🔄 Updating calendar cache...")

    cache = SimpleCalendarCache()
    cache._update_cache()  # Force update

    # Check what we got
    today = date.today()
    events = cache.get_events(today, today)

    print(f"✅ Cache updated!")
    print(f"📅 Found {len(events)} events for today")

    if events:
        print("\nToday's events:")
        for event in events[:10]:  # Show first 10
            time_str = event.start.strftime("%H:%M") if hasattr(event.start, 'strftime') else str(event.start)
            print(f"  • {event.title} at {time_str}")
        if len(events) > 10:
            print(f"  ... and {len(events) - 10} more")
    else:
        print("No events found for today")

    print("\n💡 If you still see no events, check that:")
    print("   1. Terminal has calendar permissions")
    print("   2. You actually have events scheduled for today")
    print("   3. Calendar.app shows the events")

if __name__ == "__main__":
    main()






