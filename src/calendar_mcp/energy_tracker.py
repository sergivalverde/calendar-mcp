"""Energy level tracking for calendar events."""

import re
from typing import Dict, List, Tuple

from .models import CalendarEvent, ClassifiedEvent, EnergyLevel


class EnergyTracker:
    """Tracks energy levels for calendar events."""

    # Energy event patterns: E1-E4 or L1-L4, optionally with descriptive text
    ENERGY_PATTERN = re.compile(r'^(E|L)(\d)(?:\s*-\s*.+)?$', re.IGNORECASE)

    # Mapping from energy numbers to levels
    ENERGY_MAPPING = {
        1: EnergyLevel.VERY_LOW,
        2: EnergyLevel.LOW,
        3: EnergyLevel.HIGH,
        4: EnergyLevel.ZONE_OF_GENIUS,
    }

    def track_energy_levels(self, events: List[ClassifiedEvent], raw_events: List[CalendarEvent]) -> List[ClassifiedEvent]:
        """Track energy levels for classified events.

        Args:
            events: List of classified events (main events only, energy markers excluded)
            raw_events: List of all raw events (including energy markers)

        Returns:
            List of events with energy levels assigned
        """
        # Extract energy events from raw events
        energy_events = [e for e in raw_events if self._is_energy_event(e.title)]

        # Create energy mapping for time periods
        energy_map = self._create_energy_map_from_raw(energy_events)

        # Assign energy levels to main events
        for main_event in events:
            energy_level = self._get_energy_for_event(main_event, energy_map)
            main_event.energy_level = energy_level

        return events

    def _create_energy_map_from_raw(self, energy_events: List[CalendarEvent]) -> Dict[Tuple[int, int], int]:
        """Create a mapping of time periods to energy levels from raw events.

        Returns:
            Dict mapping (start_timestamp, end_timestamp) -> energy_level
        """
        energy_map = {}

        for energy_event in energy_events:
            level = self._parse_energy_level(energy_event.title)
            if level > 0:
                # Convert to timestamps for easy comparison
                start_ts = int(energy_event.start.timestamp())
                end_ts = int(energy_event.end.timestamp())

                energy_map[(start_ts, end_ts)] = level

        return energy_map

    def _is_energy_event(self, title: str) -> bool:
        """Check if an event is an energy marker event."""
        return bool(self.ENERGY_PATTERN.match(title.strip()))

    def _parse_energy_level(self, title: str) -> int:
        """Parse energy level number from event title."""
        match = self.ENERGY_PATTERN.match(title.strip())
        if match:
            return int(match.group(2))
        return 0

    def _create_energy_map(self, energy_events: List[ClassifiedEvent]) -> Dict[Tuple[int, int], int]:
        """Create a mapping of time periods to energy levels.

        Returns:
            Dict mapping (start_timestamp, end_timestamp) -> energy_level
        """
        energy_map = {}

        for energy_event in energy_events:
            level = self._parse_energy_level(energy_event.event.title)
            if level > 0:
                # Convert to timestamps for easy comparison
                start_ts = int(energy_event.event.start.timestamp())
                end_ts = int(energy_event.event.end.timestamp())

                energy_map[(start_ts, end_ts)] = level

        return energy_map

    def _get_energy_for_event(self, event: ClassifiedEvent, energy_map: Dict[Tuple[int, int], int]) -> EnergyLevel:
        """Get the energy level for a main event based on overlapping energy events."""
        event_start = int(event.event.start.timestamp())
        event_end = int(event.event.end.timestamp())

        overlapping_levels = []

        # Find all energy events that overlap with this main event
        for (energy_start, energy_end), level in energy_map.items():
            if self._events_overlap(event_start, event_end, energy_start, energy_end):
                overlapping_levels.append(level)

        if not overlapping_levels:
            return EnergyLevel.NOT_AVAILABLE

        # Use the highest energy level from overlapping events
        highest_level = max(overlapping_levels)
        return self.ENERGY_MAPPING.get(highest_level, EnergyLevel.NOT_AVAILABLE)

    def _events_overlap(self, start1: int, end1: int, start2: int, end2: int) -> bool:
        """Check if two time periods overlap (any overlap counts)."""
        return start1 < end2 and start2 < end1
