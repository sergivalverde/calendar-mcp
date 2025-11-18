"""
Unified calendar cache system.

This module provides a single source of truth for all calendar data,
using icalBuddy exclusively for reliable calendar access.
"""

import subprocess
import json
import re
import threading
import time
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

from .models import CalendarEvent, Attendee

logger = logging.getLogger(__name__)


class CacheStatus(dict):
    """Cache status information with dict compatibility."""

    def __init__(
        self,
        cache_file: str,
        exists: bool,
        age_seconds: Optional[int] = None,
        is_expired: bool = False,
        ttl: int = 300,
        event_count: int = 0,
        date_range: Optional[Dict[str, str]] = None,
        last_refresh: Optional[str] = None,
        next_refresh: Optional[str] = None,
        background_refresh: bool = False,
        error: Optional[str] = None,
    ):
        super().__init__(
            cache_file=cache_file,
            exists=exists,
            age_seconds=age_seconds,
            is_expired=is_expired,
            ttl=ttl,
            event_count=event_count,
            date_range=date_range or {},
            last_refresh=last_refresh,
            next_refresh=next_refresh,
            background_refresh=background_refresh,
            error=error,
        )


class UnifiedCache:
    """
    Single source of truth for all calendar data.
    Uses icalBuddy exclusively for reliable calendar access.
    """

    # Default configuration
    DEFAULT_CACHE_DIR = Path.home() / ".cache" / "calendar-mcp"
    DEFAULT_CACHE_FILE = "unified_cache.json"
    DEFAULT_TTL = 300  # 5 minutes
    DEFAULT_DAYS_PAST = 60  # 2 months back
    DEFAULT_DAYS_FUTURE = 60  # 2 months forward

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        ttl: int = DEFAULT_TTL,
        days_past: int = DEFAULT_DAYS_PAST,
        days_future: int = DEFAULT_DAYS_FUTURE,
        background_refresh: bool = False,
        calendars: Optional[List[str]] = None,
    ):
        """
        Initialize unified cache.

        Args:
            cache_dir: Directory for cache files (default: ~/.cache/calendar-mcp)
            ttl: Time-to-live in seconds (default: 300)
            days_past: Days in the past to cache (default: 60)
            days_future: Days in the future to cache (default: 60)
            background_refresh: Enable background auto-refresh (default: False)
            calendars: List of calendar names to include (None = all)
        """
        self.cache_dir = cache_dir or self.DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / self.DEFAULT_CACHE_FILE

        self.ttl = ttl
        self.days_past = days_past
        self.days_future = days_future
        self.calendars = calendars

        self._background_refresh = background_refresh
        self._background_thread: Optional[threading.Thread] = None
        self._stop_refresh = threading.Event()
        self._lock = threading.Lock()

        logger.info(
            f"UnifiedCache initialized: ttl={ttl}s, "
            f"range={days_past}d past to {days_future}d future"
        )

    def initialize(self) -> bool:
        """
        Initialize cache on startup.

        Creates cache directory if needed and performs initial fetch
        if cache is missing or expired.

        Returns:
            True if successful, False if failed
        """
        try:
            logger.info("Initializing calendar cache...")

            # Create cache directory
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            # Check if cache needs refresh
            if not self.cache_file.exists() or self._is_expired():
                logger.info("Cache missing or expired, fetching fresh data...")
                result = self.refresh(force=True)
                if result.get("error"):
                    logger.error(f"Failed to initialize cache: {result['error']}")
                    return False
            else:
                logger.info("Cache exists and is fresh")

            # Start background refresh if enabled
            if self._background_refresh:
                self.start_background_refresh()

            logger.info("Cache initialization complete")
            return True

        except Exception as e:
            logger.error(f"Cache initialization failed: {e}", exc_info=True)
            return False

    def refresh(self, force: bool = False) -> CacheStatus:
        """
        Manually refresh cache.

        Args:
            force: Force refresh even if cache is fresh

        Returns:
            Cache status dictionary with statistics
        """
        with self._lock:
            try:
                # Check if refresh needed
                if not force and not self._is_expired():
                    logger.debug("Cache is fresh, skipping refresh")
                    return self.get_status()

                logger.info("Refreshing calendar cache...")

                # Calculate date range
                start_date = date.today() - timedelta(days=self.days_past)
                end_date = date.today() + timedelta(days=self.days_future)

                # Fetch events from icalBuddy
                output = self._run_icalbuddy(start_date, end_date)
                events = self._parse_icalbuddy_output(output)

                # Save cache data
                cache_data = {
                    "updated_at": datetime.now().isoformat(),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "event_count": len(events),
                    "events": [self._event_to_dict(event) for event in events],
                }

                with open(self.cache_file, "w") as f:
                    json.dump(cache_data, f, indent=2)

                logger.info(f"Cache refreshed: {len(events)} events")
                return self.get_status()

            except subprocess.CalledProcessError as e:
                error_msg = f"icalBuddy command failed: {e.stderr if hasattr(e, 'stderr') else str(e)}"
                logger.error(error_msg)
                return CacheStatus(
                    cache_file=str(self.cache_file),
                    exists=self.cache_file.exists(),
                    ttl=self.ttl,
                    error=error_msg,
                )
            except Exception as e:
                error_msg = f"Cache refresh failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return CacheStatus(
                    cache_file=str(self.cache_file),
                    exists=self.cache_file.exists(),
                    ttl=self.ttl,
                    error=error_msg,
                )

    def get_events(
        self, start_date: date, end_date: date, auto_refresh: bool = True
    ) -> List[CalendarEvent]:
        """
        Retrieve events from cache.

        Args:
            start_date: Start date for events
            end_date: End date for events
            auto_refresh: Auto-refresh if cache expired (default: True)

        Returns:
            List of CalendarEvent objects
        """
        try:
            # Auto-refresh if expired and enabled
            if auto_refresh and self._is_expired():
                logger.info("Cache expired, auto-refreshing...")
                self.refresh(force=True)

            # Load from cache
            return self._load_cached_events(start_date, end_date)

        except Exception as e:
            logger.error(f"Failed to get events: {e}", exc_info=True)
            return []

    def get_status(self) -> CacheStatus:
        """
        Get cache health status.

        Returns:
            Dictionary with cache status information
        """
        try:
            exists = self.cache_file.exists()
            age_seconds = None
            last_refresh = None
            event_count = 0
            date_range = {}

            if exists:
                # Get file age
                stat = self.cache_file.stat()
                age_seconds = int(datetime.now().timestamp() - stat.st_mtime)
                last_refresh = datetime.fromtimestamp(stat.st_mtime).isoformat()

                # Load cache data
                try:
                    with open(self.cache_file, "r") as f:
                        cache_data = json.load(f)
                    event_count = cache_data.get("event_count", 0)
                    date_range = {
                        "start": cache_data.get("start_date"),
                        "end": cache_data.get("end_date"),
                    }
                except json.JSONDecodeError:
                    logger.warning("Cache file is corrupted")

            is_expired = self._is_expired()
            next_refresh = None
            if last_refresh and not is_expired:
                next_refresh_time = datetime.fromisoformat(last_refresh) + timedelta(
                    seconds=self.ttl
                )
                next_refresh = next_refresh_time.isoformat()

            return CacheStatus(
                cache_file=str(self.cache_file),
                exists=exists,
                age_seconds=age_seconds,
                is_expired=is_expired,
                ttl=self.ttl,
                event_count=event_count,
                date_range=date_range,
                last_refresh=last_refresh,
                next_refresh=next_refresh,
                background_refresh=self._background_refresh
                and self._background_thread is not None
                and self._background_thread.is_alive(),
            )

        except Exception as e:
            logger.error(f"Failed to get cache status: {e}", exc_info=True)
            return CacheStatus(
                cache_file=str(self.cache_file),
                exists=False,
                ttl=self.ttl,
                error=str(e),
            )

    def start_background_refresh(self):
        """
        Start background thread that refreshes cache periodically.

        The thread runs as a daemon and refreshes cache every TTL seconds.
        Silent failures are logged but not raised.
        """
        if self._background_thread and self._background_thread.is_alive():
            logger.warning("Background refresh already running")
            return

        self._stop_refresh.clear()
        self._background_thread = threading.Thread(
            target=self._background_refresh_loop, daemon=True
        )
        self._background_thread.start()
        logger.info("Background refresh started")

    def stop_background_refresh(self):
        """Stop background refresh thread gracefully."""
        if not self._background_thread or not self._background_thread.is_alive():
            logger.debug("Background refresh not running")
            return

        logger.info("Stopping background refresh...")
        self._stop_refresh.set()
        self._background_thread.join(timeout=5.0)
        logger.info("Background refresh stopped")

    def _background_refresh_loop(self):
        """Background refresh loop (runs in separate thread)."""
        logger.info(f"Background refresh loop started (interval: {self.ttl}s)")

        while not self._stop_refresh.is_set():
            try:
                # Wait for TTL seconds or until stop signal
                if self._stop_refresh.wait(timeout=self.ttl):
                    break

                # Refresh cache
                logger.debug("Background refresh triggered")
                self.refresh(force=False)

            except Exception as e:
                logger.error(f"Background refresh error: {e}", exc_info=True)
                # Continue running despite errors

        logger.info("Background refresh loop exited")

    def _is_expired(self) -> bool:
        """Check if cache is expired based on TTL."""
        if not self.cache_file.exists():
            return True

        try:
            stat = self.cache_file.stat()
            age_seconds = datetime.now().timestamp() - stat.st_mtime
            return age_seconds >= self.ttl
        except Exception:
            return True

    def _run_icalbuddy(self, start_date: date, end_date: date) -> str:
        """
        Execute icalBuddy command.

        Args:
            start_date: Start date for events
            end_date: End date for events

        Returns:
            Raw icalBuddy output

        Raises:
            subprocess.CalledProcessError: If icalBuddy command fails
            FileNotFoundError: If icalBuddy is not installed
        """
        # Build command
        cmd = [
            "icalBuddy",
            "-nc",  # No color
            "-iep",
            "title,datetime,location,notes,attendees",
            "-df",
            "%Y-%m-%d",  # Date format: YYYY-MM-DD
            "-tf",
            "%H:%M",  # Time format: HH:MM
        ]

        # Add calendar filter if specified
        if self.calendars:
            cmd.extend(["-includeCals", ",".join(self.calendars)])
        
        # Command must come last
        cmd.append(f"eventsFrom:{start_date.strftime('%Y-%m-%d')}")
        cmd.append(f"to:{end_date.strftime('%Y-%m-%d')}")

        logger.debug(f"Running icalBuddy: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30, check=True
            )
            return result.stdout

        except FileNotFoundError:
            raise FileNotFoundError(
                "icalBuddy not found. Install it with: brew install ical-buddy"
            )
        except subprocess.TimeoutExpired:
            raise subprocess.CalledProcessError(
                1, cmd, stderr="icalBuddy command timed out after 30 seconds"
            )

    def _parse_icalbuddy_output(self, output: str) -> List[CalendarEvent]:
        """
        Parse icalBuddy output into CalendarEvent objects.

        Args:
            output: Raw icalBuddy output

        Returns:
            List of CalendarEvent objects
        """
        if not output or output.strip() == "No events found.":
            return []

        events = []
        lines = output.strip().split("\n")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Events start with bullet point  
            if line.startswith("• "):
                event_title = line[2:].strip()
                datetime_str = None
                location = None
                notes = None
                attendees = []

                # Look for datetime on next line
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if re.match(r"\d{4}-\d{2}-\d{2}", next_line):
                        datetime_str = next_line
                        i += 1

                        # Look for additional details
                        while i + 1 < len(lines):
                            detail_line = lines[i + 1].strip()

                            # Stop at next event
                            if detail_line.startswith("• "):
                                break
                            
                            # Stop if we hit another datetime (unlikely but safe)
                            if re.match(r"\d{4}-\d{2}-\d{2}", detail_line):
                                break

                            # Parse details
                            if detail_line.startswith("location:"):
                                location = detail_line[9:].strip()
                                if location == "(null)":
                                    location = None
                            elif detail_line.startswith("notes:"):
                                notes = detail_line[6:].strip()
                                if notes == "(null)":
                                    notes = None
                            elif detail_line.startswith("attendees:"):
                                attendees_str = detail_line[10:].strip()
                                if attendees_str and attendees_str != "(null)":
                                    # Parse "Name <email>" format
                                    attendee_matches = re.findall(
                                        r"([^<]+)<([^>]+)>", attendees_str
                                    )
                                    for name, email in attendee_matches:
                                        attendees.append(
                                            Attendee(
                                                name=name.strip(), email=email.strip()
                                            )
                                        )

                            i += 1
                            if not detail_line:
                                break

                # Create event if we have both datetime and title
                if datetime_str and event_title:
                    try:
                        event = self._parse_event_datetime(
                            event_title, datetime_str, location, notes, attendees
                        )
                        if event:
                            events.append(event)
                    except Exception as e:
                        logger.warning(f"Failed to parse event '{event_title}': {e}")

            i += 1

        return events

    def _parse_event_datetime(
        self,
        title: str,
        datetime_str: str,
        location: Optional[str] = None,
        notes: Optional[str] = None,
        attendees: Optional[List[Attendee]] = None,
    ) -> Optional[CalendarEvent]:
        """
        Parse event datetime string into CalendarEvent.

        Handles formats like:
        - "2024-11-17 at 10:00 - 11:00" (timed event)
        - "2024-11-17 at 10:00" (event with no end time - default 1 hour)
        - "2024-11-17" (all-day)
        """
        try:
            # Format: "2024-11-17 at 10:00 - 11:00" or "2024-11-17 at 10:00"
            datetime_match = re.match(
                r"(\d{4}-\d{2}-\d{2})\s+at\s+(\d{1,2}:\d{2})\s*(?:-\s*(\d{1,2}:\d{2}))?",
                datetime_str,
            )

            if datetime_match:
                date_str = datetime_match.group(1)
                start_time = datetime_match.group(2)
                end_time = datetime_match.group(3)

                start_datetime = datetime.strptime(
                    f"{date_str} {start_time}", "%Y-%m-%d %H:%M"
                )
                
                # If no end time provided, default to 1 hour duration
                if end_time is None:
                    end_datetime = start_datetime + timedelta(hours=1)
                else:
                    end_datetime = datetime.strptime(
                        f"{date_str} {end_time}", "%Y-%m-%d %H:%M"
                    )
                    # If end time is earlier than start time, assume next day
                    if end_datetime < start_datetime:
                        end_datetime += timedelta(days=1)

                return CalendarEvent(
                    title=title,
                    start=start_datetime,
                    end=end_datetime,
                    location=location,
                    notes=notes,
                    attendees=attendees or [],
                )

            # Format: "2024-11-17" (all-day event)
            date_match = re.match(r"(\d{4}-\d{2}-\d{2})$", datetime_str)
            if date_match:
                date_str = date_match.group(1)
                event_date = datetime.strptime(date_str, "%Y-%m-%d")

                return CalendarEvent(
                    title=title,
                    start=event_date,
                    end=event_date + timedelta(days=1),
                    location=location,
                    notes=notes,
                    attendees=attendees or [],
                )

        except Exception as e:
            logger.warning(f"Failed to parse datetime '{datetime_str}': {e}")

        return None

    def _load_cached_events(
        self, start_date: date, end_date: date
    ) -> List[CalendarEvent]:
        """
        Load events from cache for the given date range.

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            List of CalendarEvent objects
        """
        try:
            if not self.cache_file.exists():
                logger.warning("Cache file does not exist")
                return []

            with open(self.cache_file, "r") as f:
                cache_data = json.load(f)

            events = []
            for event_dict in cache_data.get("events", []):
                event = self._dict_to_event(event_dict)
                if event:
                    # Filter by date range
                    event_date = event.start.date()
                    if start_date <= event_date <= end_date:
                        events.append(event)

            return events

        except json.JSONDecodeError as e:
            logger.error(f"Cache file is corrupted: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to load cached events: {e}", exc_info=True)
            return []

    def _event_to_dict(self, event: CalendarEvent) -> Dict[str, Any]:
        """Convert CalendarEvent to dictionary for JSON storage."""
        return {
            "title": event.title,
            "start": event.start.isoformat(),
            "end": event.end.isoformat(),
            "location": event.location,
            "notes": event.notes,
            "attendees": [
                {"name": a.name, "email": a.email} for a in event.attendees
            ],
        }

    def _dict_to_event(self, data: Dict[str, Any]) -> Optional[CalendarEvent]:
        """Convert dictionary back to CalendarEvent."""
        try:
            return CalendarEvent(
                title=data["title"],
                start=datetime.fromisoformat(data["start"]),
                end=datetime.fromisoformat(data["end"]),
                location=data.get("location"),
                notes=data.get("notes"),
                attendees=[
                    Attendee(name=a["name"], email=a["email"])
                    for a in data.get("attendees", [])
                ],
            )
        except Exception as e:
            logger.warning(f"Failed to convert cached event: {e}")
            return None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop background refresh."""
        self.stop_background_refresh()
        return False
