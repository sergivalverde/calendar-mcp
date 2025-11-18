#!/usr/bin/env python3
"""Test calendar access and MCP functionality."""

import subprocess
import sys
from datetime import date

def test_calendar_access():
    """Test if we can access calendar data."""
    print("🔍 Testing Calendar MCP Access")
    print("=" * 50)

    # Test 1: icalBuddy access
    print("\n1. Testing icalBuddy access...")
    try:
        result = subprocess.run(['icalBuddy', 'calendars'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            print("   ✅ icalBuddy can access calendars")
            calendars = [line.strip() for line in result.stdout.split('\n') if line.strip().startswith('• ')]
            print(f"   📅 Found {len(calendars)} calendars")
        else:
            print("   ❌ icalBuddy cannot access calendars")
            print("   📝 SOLUTION: Grant Terminal calendar permissions")
            print("      System Settings → Privacy & Security → Calendars → Enable Terminal")
            return False
    except Exception as e:
        print(f"   ❌ icalBuddy error: {e}")
        return False

    # Test 2: Get some events
    print("\n2. Testing event retrieval...")
    try:
        from src.calendar_mcp.simple_cache import SimpleCalendarCache
        cache = SimpleCalendarCache()

        # Get events for this week
        today = date.today()
        start_of_week = today
        end_of_week = today

        events = cache.get_events(start_of_week, end_of_week)
        print(f"   📅 Found {len(events)} events for today")

        if events:
            print("   ✅ Calendar data accessible!")
            for event in events[:3]:  # Show first 3 events
                print(f"      • {event.title} ({event.start.strftime('%H:%M')})")
        else:
            print("   ℹ️  No events found for today (this is normal if you have no events)")

    except Exception as e:
        print(f"   ❌ Error accessing calendar data: {e}")
        return False

    # Test 3: MCP server
    print("\n3. Testing MCP server startup...")
    try:
        # Test if server can start (timeout after 3 seconds)
        result = subprocess.run([
            sys.executable, '-m', 'calendar_mcp.server'
        ], capture_output=True, timeout=3)

        # Server should start without immediate errors
        if "Error importing MCP" not in result.stderr.decode():
            print("   ✅ MCP server can start")
        else:
            print("   ❌ MCP server has import errors")
            return False

    except subprocess.TimeoutExpired:
        print("   ✅ MCP server started successfully (timeout expected)")
    except Exception as e:
        print(f"   ❌ MCP server error: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 SUCCESS: Calendar MCP is ready!")
    print("\n📋 Next steps:")
    print("1. Configure Raycast with the Calendar MCP")
    print("2. Ask: 'Analyze my calendar for this week'")
    print("3. Try creating events: 'Block two mornings next week to work on X'")

    return True

if __name__ == "__main__":
    success = test_calendar_access()
    sys.exit(0 if success else 1)






