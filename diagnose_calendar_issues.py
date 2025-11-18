#!/usr/bin/env python3
"""Comprehensive calendar access diagnostic."""

import subprocess
import os
import json
from pathlib import Path
from datetime import date

def check_calendar_app():
    """Check if Calendar.app has calendars configured."""
    print("📱 Checking Calendar.app status...")

    # Check if Calendar.app exists
    calendar_app = "/System/Applications/Calendar.app"
    if not os.path.exists(calendar_app):
        calendar_app = "/Applications/Calendar.app"
        if not os.path.exists(calendar_app):
            print("❌ Calendar.app not found")
            return False

    print("✅ Calendar.app found")

    # Try to check calendar data directory
    calendars_dir = Path.home() / "Library" / "Calendars"
    if calendars_dir.exists():
        print("✅ Calendar data directory exists")
        subdirs = list(calendars_dir.glob("*"))
        print(f"📁 Found {len(subdirs)} calendar data directories:")
        for subdir in subdirs[:5]:  # Show first 5
            print(f"   • {subdir.name}")
        if len(subdirs) > 5:
            print(f"   • ... and {len(subdirs) - 5} more")

        # Check for .ics files
        ics_files = list(calendars_dir.rglob("*.ics"))
        print(f"📄 Found {len(ics_files)} .ics files")
    else:
        print("❌ Calendar data directory does not exist")
        print("   This means no calendars are configured in Calendar.app")

    return True

def check_permissions():
    """Check calendar permissions for current process."""
    print("\n🔐 Checking permissions...")

    # Test icalBuddy calendars
    print("Testing icalBuddy calendars...")
    result = subprocess.run(['icalBuddy', 'calendars'],
                          capture_output=True, text=True, timeout=10)

    if result.returncode == 0 and result.stdout.strip():
        print("✅ icalBuddy can access calendars")
        calendars = [line.strip() for line in result.stdout.split('\n') if line.strip().startswith('•')]
        print(f"📅 Found {len(calendars)} calendars:")
        for cal in calendars[:5]:
            print(f"   • {cal[2:]}")  # Remove bullet
        return True
    else:
        print("❌ icalBuddy cannot access calendars")
        print(f"Error: {result.stderr.strip()}")
        return False

def check_events():
    """Check if we can retrieve events."""
    print("\n📅 Checking event retrieval...")

    # Test eventsToday
    result = subprocess.run(['icalBuddy', 'eventsToday'],
                          capture_output=True, text=True, timeout=10)

    if result.returncode == 0 and result.stdout.strip():
        lines = result.stdout.strip().split('\n')
        event_count = sum(1 for line in lines if line.strip().startswith('•'))
        print(f"✅ Found {event_count} events today")
        if event_count > 0:
            print("Sample events:")
            for line in lines[:5]:
                if line.strip():
                    print(f"   {line}")
        return event_count > 0
    else:
        print("❌ No events found today or error retrieving events")
        if result.stderr.strip():
            print(f"Error: {result.stderr.strip()}")
        return False

def check_cache():
    """Check cache status."""
    print("\n💾 Checking cache status...")

    cache_file = Path.home() / ".cache" / "calendar-mcp" / "events.json"
    if cache_file.exists():
        print("✅ Cache file exists")
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)

            fetched_at = cache_data.get('fetched_at', 'unknown')
            event_count = cache_data.get('event_count', 0)
            events = cache_data.get('events', [])

            print(f"📅 Cache fetched at: {fetched_at}")
            print(f"📊 Total cached events: {event_count}")

            # Check today's events
            today = date.today().isoformat()
            today_events = [e for e in events if 'datetime' in e and today in e['datetime']]
            print(f"📅 Today's cached events: {len(today_events)}")

            if today_events:
                print("Sample today's events:")
                for event in today_events[:3]:
                    print(f"   • {event.get('title', 'Unknown')} - {event.get('datetime', 'no time')}")

            return event_count > 0

        except Exception as e:
            print(f"❌ Error reading cache: {e}")
            return False
    else:
        print("❌ Cache file does not exist")
        return False

def main():
    """Run all diagnostics."""
    print("🔍 COMPREHENSIVE CALENDAR DIAGNOSTIC")
    print("=" * 50)

    results = {
        'calendar_app': check_calendar_app(),
        'permissions': check_permissions(),
        'events': check_events(),
        'cache': check_cache()
    }

    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC SUMMARY")

    issues = []
    recommendations = []

    if not results['calendar_app']:
        issues.append("Calendar.app not properly set up")
        recommendations.append("Open Calendar.app and check if calendars are configured")

    if not results['permissions']:
        issues.append("No calendar permissions")
        recommendations.append("Grant calendar access to Terminal in System Settings")

    if not results['events']:
        issues.append("Cannot retrieve events")
        if results['permissions']:
            recommendations.append("Check if Calendar.app actually has events scheduled")
        else:
            recommendations.append("Fix permissions first")

    if not results['cache']:
        issues.append("Cache not working")
        recommendations.append("Cache will work once permissions are fixed")

    if not issues:
        print("✅ ALL SYSTEMS GO!")
        print("Calendar MCP should work perfectly.")
        return 0

    print(f"❌ Found {len(issues)} issues:")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")

    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")

    print(f"\n🔄 After fixing, run: python test_calendar_access.py")
    return 1

if __name__ == "__main__":
    exit(main())






