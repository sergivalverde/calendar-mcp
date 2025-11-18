#!/usr/bin/env python3
"""Final test to verify Calendar MCP is working."""

from src.calendar_mcp.simple_cache import SimpleCalendarCache
from datetime import date

def main():
    print("🎯 FINAL CALENDAR MCP TEST")
    print("=" * 50)

    # Test 1: Cache update
    print("\n1. Testing cache update...")
    try:
        cache = SimpleCalendarCache()
        cache._update_cache()
        print("✅ Cache update completed")
    except Exception as e:
        print(f"❌ Cache update failed: {e}")
        return False

    # Test 2: Today's events
    print("\n2. Checking today's events...")
    try:
        today = date.today()
        events = cache.get_events(today, today)

        print(f"📅 Found {len(events)} events for today ({today})")

        if events:
            print("✅ SUCCESS: Calendar events found!")
            print("\nToday's events:")
            for i, event in enumerate(events[:10], 1):
                time_str = event.start.strftime("%H:%M") if hasattr(event.start, 'strftime') else str(event.start)
                print(f"   {i}. {event.title} at {time_str}")
            if len(events) > 10:
                print(f"   ... and {len(events) - 10} more")
        else:
            print("⚠️  No events found for today (this is normal if you have no events scheduled)")

    except Exception as e:
        print(f"❌ Error checking events: {e}")
        return False

    # Test 3: MCP server
    print("\n3. Testing MCP server startup...")
    try:
        from src.calendar_mcp.server import CalendarAnalysisServer
        server = CalendarAnalysisServer()
        print("✅ MCP server can be initialized")
    except Exception as e:
        print(f"❌ MCP server failed: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 SUCCESS: Calendar MCP is ready!")
    print("\n📋 Next steps:")
    print("1. Configure Raycast with Calendar MCP")
    print("2. Ask: 'Analyze my calendar for this week'")
    print("3. Try: 'Block two mornings next week to work on X'")
    print("\n💡 If you see no events, it might be that you genuinely have no events scheduled for today.")

    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed. Check the output above.")
        exit(1)






