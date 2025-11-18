#!/usr/bin/env python3
"""
Test script for the new unified cache architecture.

This script tests:
1. UnifiedCache initialization
2. Calendar data fetching via icalBuddy
3. CalendarManager integration
4. Cache status reporting
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from calendar_mcp.unified_cache import UnifiedCache
from calendar_mcp.calendar_manager import CalendarManager
from calendar_mcp.config import ConfigManager


def test_unified_cache():
    """Test UnifiedCache directly."""
    print("=" * 60)
    print("TEST 1: UnifiedCache")
    print("=" * 60)
    
    try:
        # Create cache instance
        cache = UnifiedCache(
            ttl=300,
            days_past=60,
            days_future=60,
            background_refresh=False
        )
        
        print("\n✓ UnifiedCache created")
        
        # Initialize cache
        print("\n→ Initializing cache (this may take a few seconds)...")
        success = cache.initialize()
        
        if success:
            print("✓ Cache initialized successfully")
        else:
            print("✗ Cache initialization failed")
            return False
        
        # Get cache status
        print("\n→ Getting cache status...")
        status = cache.get_status()
        
        print(f"\nCache Status:")
        print(f"  - File: {status['cache_file']}")
        print(f"  - Exists: {status['exists']}")
        print(f"  - Events: {status['event_count']}")
        print(f"  - Expired: {status['is_expired']}")
        print(f"  - TTL: {status['ttl']}s")
        print(f"  - Date range: {status['date_range'].get('start')} to {status['date_range'].get('end')}")
        
        if status.get('error'):
            print(f"  ✗ Error: {status['error']}")
            return False
        
        # Get events
        print("\n→ Retrieving events for last 7 days...")
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        events = cache.get_events(start_date, end_date)
        print(f"✓ Retrieved {len(events)} events")
        
        if events:
            print(f"\nSample events:")
            for event in events[:3]:
                print(f"  - {event.start.strftime('%Y-%m-%d %H:%M')} | {event.title}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ UnifiedCache test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_calendar_manager():
    """Test CalendarManager integration."""
    print("\n" + "=" * 60)
    print("TEST 2: CalendarManager")
    print("=" * 60)
    
    try:
        # Create manager
        manager = CalendarManager()
        print("\n✓ CalendarManager created")
        
        # Initialize
        print("\n→ Initializing CalendarManager...")
        success = manager.initialize()
        
        if success:
            print("✓ CalendarManager initialized successfully")
        else:
            print("✗ CalendarManager initialization failed")
            return False
        
        # Get cache status
        print("\n→ Getting cache status via manager...")
        status = manager.get_cache_status()
        
        print(f"\nCache Status (via Manager):")
        print(f"  - Events: {status['event_count']}")
        print(f"  - Age: {status.get('age_seconds', 0)}s")
        print(f"  - Expired: {status['is_expired']}")
        
        # Get events
        print("\n→ Getting events via manager...")
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        events = manager.get_events(start_date, end_date)
        print(f"✓ Retrieved {len(events)} events via manager")
        
        # Test refresh
        print("\n→ Testing manual cache refresh...")
        refresh_status = manager.refresh_cache(force=True)
        
        if refresh_status.get('error'):
            print(f"✗ Refresh failed: {refresh_status['error']}")
            return False
        else:
            print(f"✓ Cache refreshed successfully ({refresh_status['event_count']} events)")
        
        return True
        
    except Exception as e:
        print(f"\n✗ CalendarManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_config():
    """Test with actual config.json."""
    print("\n" + "=" * 60)
    print("TEST 3: Configuration Integration")
    print("=" * 60)
    
    try:
        # Load config
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        print("\n✓ Configuration loaded")
        print(f"  - Calendars: {config.calendar.calendars}")
        print(f"  - Default calendar: {config.calendar.default_calendar}")
        print(f"  - Cache TTL: {config.calendar.event_creation.get('cache_ttl', 300)}s")
        print(f"  - Days past: {config.calendar.event_creation.get('cache_days_past', 60)}")
        print(f"  - Days future: {config.calendar.event_creation.get('cache_days_future', 60)}")
        print(f"  - Background refresh: {config.calendar.event_creation.get('background_refresh', False)}")
        
        # Create cache with config
        cache = UnifiedCache(
            ttl=config.calendar.event_creation.get("cache_ttl", 300),
            days_past=config.calendar.event_creation.get("cache_days_past", 60),
            days_future=config.calendar.event_creation.get("cache_days_future", 60),
            background_refresh=config.calendar.event_creation.get("background_refresh", False),
            calendars=config.calendar.calendars,
        )
        
        print("\n✓ UnifiedCache created with config")
        
        # Initialize
        print("\n→ Initializing with config settings...")
        success = cache.initialize()
        
        if success:
            print("✓ Cache initialized with config")
            status = cache.get_status()
            print(f"  - Events: {status['event_count']}")
            return True
        else:
            print("✗ Initialization failed")
            return False
        
    except Exception as e:
        print(f"\n✗ Config integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n🗓️  Calendar-MCP Unified Cache Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: UnifiedCache
    results.append(("UnifiedCache", test_unified_cache()))
    
    # Test 2: CalendarManager
    results.append(("CalendarManager", test_calendar_manager()))
    
    # Test 3: Configuration Integration
    results.append(("Configuration", test_with_config()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed. Check output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
