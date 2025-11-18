"""
Simplified calendar data manager using unified cache.

This module provides a clean interface to calendar data,
using UnifiedCache as the single source of truth.
"""

from datetime import date
from typing import List, Optional
import logging

from .models import CalendarEvent
from .unified_cache import UnifiedCache
from .classifier import EventClassifier
from .energy_tracker import EnergyTracker

logger = logging.getLogger(__name__)


class CalendarManager:
    """
    Simplified calendar data manager.
    Uses UnifiedCache as single source of truth for all calendar data.
    """

    def __init__(
        self,
        cache: Optional[UnifiedCache] = None,
        classifier: Optional[EventClassifier] = None,
        energy_tracker: Optional[EnergyTracker] = None,
    ):
        """
        Initialize calendar manager.

        Args:
            cache: UnifiedCache instance (created if None)
            classifier: EventClassifier instance (optional)
            energy_tracker: EnergyTracker instance (created if None)
        """
        self.cache = cache or UnifiedCache()
        self.classifier = classifier  # Can be None
        self.energy_tracker = energy_tracker or EnergyTracker()

        logger.info("CalendarManager initialized")

    def initialize(self) -> bool:
        """
        Initialize calendar manager.

        This will initialize the cache, which may trigger an initial
        calendar data fetch if the cache is empty or expired.

        Returns:
            True if initialization successful, False otherwise
        """
        logger.info("Initializing CalendarManager...")
        return self.cache.initialize()

    def get_events(
        self, start_date: date, end_date: date, auto_refresh: bool = True
    ) -> List[CalendarEvent]:
        """
        Get calendar events for the specified date range.

        Events are retrieved from the unified cache, which automatically
        refreshes if expired (when auto_refresh=True).

        Args:
            start_date: Start date for events
            end_date: End date for events
            auto_refresh: Auto-refresh cache if expired (default: True)

        Returns:
            List of CalendarEvent objects
        """
        logger.debug(f"Getting events from {start_date} to {end_date}")
        return self.cache.get_events(start_date, end_date, auto_refresh=auto_refresh)

    def refresh_cache(self, force: bool = False) -> dict:
        """
        Manually refresh the calendar cache.

        Args:
            force: Force refresh even if cache is fresh

        Returns:
            Cache status dictionary with refresh statistics
        """
        logger.info(f"Refreshing cache (force={force})")
        return self.cache.refresh(force=force)

    def get_cache_status(self) -> dict:
        """
        Get calendar cache health status.

        Returns:
            Dictionary with cache status information including:
            - cache_file: Path to cache file
            - exists: Whether cache file exists
            - age_seconds: Age of cache in seconds
            - is_expired: Whether cache is expired
            - ttl: Time-to-live in seconds
            - event_count: Number of cached events
            - date_range: Cached date range (start/end)
            - last_refresh: Last refresh timestamp
            - next_refresh: Next scheduled refresh timestamp
            - background_refresh: Background refresh status
            - error: Error message if any
        """
        return self.cache.get_status()

    def list_calendars(self) -> List[str]:
        """
        List all available calendars.

        This is a convenience method that delegates to AppleScript.
        Consider moving to a separate utility module if needed.

        Returns:
            List of calendar names
        """
        from .applescript_writer import list_available_calendars

        try:
            return list_available_calendars()
        except Exception as e:
            logger.error(f"Failed to list calendars: {e}")
            return []

    def start_background_refresh(self):
        """Start background cache refresh daemon."""
        logger.info("Starting background refresh")
        self.cache.start_background_refresh()

    def stop_background_refresh(self):
        """Stop background cache refresh daemon."""
        logger.info("Stopping background refresh")
        self.cache.stop_background_refresh()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        self.stop_background_refresh()
        return False
