#!/usr/bin/env python3
"""Week 46 calendar analysis script."""

import sys
from datetime import date, datetime, timedelta
from src.calendar_mcp.models import (
    CalendarEvent,
    Attendee,
    ClassificationConfig,
    Category,
    EnergyLevel,
    ClassifiedEvent
)
from src.calendar_mcp.classifier import EventClassifier
from src.calendar_mcp.energy_tracker import EnergyTracker
from src.calendar_mcp.report_generator import ReportGenerator
from src.calendar_mcp.config import ConfigManager


def get_week46_dates():
    """Get the date range for Week 46 of 2025."""
    # Week 46 of 2025 is November 10-16, 2025
    # Monday, November 10 to Sunday, November 16
    start_date = date(2025, 11, 10)
    end_date = date(2025, 11, 16)
    return start_date, end_date


def create_week46_sample_events():
    """Create realistic sample events for Week 46 analysis."""
    base_date = date(2025, 11, 10)  # Monday of Week 46

    events = [
        # Monday, November 10
        # Information Processing - Email catch-up
        CalendarEvent(
            title="Information processing",
            start=datetime(2025, 11, 10, 8, 30),
            end=datetime(2025, 11, 10, 9, 30),
            attendees=[],
            location=None,
            notes=None
        ),
        # Team meeting
        CalendarEvent(
            title="Weekly Team Sync",
            start=datetime(2025, 11, 10, 10, 0),
            end=datetime(2025, 11, 10, 11, 0),
            attendees=[Attendee(email="team@tensormedical.ai"), Attendee(email="colleague@tensormedical.ai")],
            location=None,
            notes=None
        ),
        # Strategy work
        CalendarEvent(
            title="Strategy review + planning",
            start=datetime(2025, 11, 10, 14, 0),
            end=datetime(2025, 11, 10, 16, 0),
            attendees=[],
            location="https://github.com/tensormedical/brain",
            notes=None
        ),
        # Energy marker for strategy work
        CalendarEvent(
            title="E4 - Deep strategic thinking session",
            start=datetime(2025, 11, 10, 14, 0),
            end=datetime(2025, 11, 10, 16, 0),
            attendees=[],
            location=None,
            notes=None
        ),

        # Tuesday, November 11
        # Information processing
        CalendarEvent(
            title="Email processing + task prioritization",
            start=datetime(2025, 11, 11, 9, 0),
            end=datetime(2025, 11, 11, 10, 0),
            attendees=[],
            location=None,
            notes=None
        ),
        # Engineering work
        CalendarEvent(
            title="Review study for Milan",
            start=datetime(2025, 11, 11, 11, 0),
            end=datetime(2025, 11, 11, 13, 0),
            attendees=[],
            location="https://github.com/tensormedical/research",
            notes=None
        ),
        # Sales meeting
        CalendarEvent(
            title="Call with Philips - Tensor Medical Platform Demo",
            start=datetime(2025, 11, 11, 15, 0),
            end=datetime(2025, 11, 11, 16, 30),
            attendees=[Attendee(email="external@philips.com")],
            location=None,
            notes=None
        ),
        # Energy marker
        CalendarEvent(
            title="E3",
            start=datetime(2025, 11, 11, 15, 0),
            end=datetime(2025, 11, 11, 16, 30),
            attendees=[],
            location=None,
            notes=None
        ),

        # Wednesday, November 12
        # Team 1:1
        CalendarEvent(
            title="1:1 with Julia",
            start=datetime(2025, 11, 12, 10, 30),
            end=datetime(2025, 11, 12, 11, 30),
            attendees=[Attendee(email="julia@tensormedical.ai")],
            location=None,
            notes=None
        ),
        # Strategy work
        CalendarEvent(
            title="Customer acquisition strategy docs",
            start=datetime(2025, 11, 12, 14, 0),
            end=datetime(2025, 11, 12, 16, 0),
            attendees=[],
            location=None,
            notes=None
        ),
        # Exercise
        CalendarEvent(
            title="🏋️ Workout",
            start=datetime(2025, 11, 12, 18, 0),
            end=datetime(2025, 11, 12, 19, 0),
            attendees=[],
            location=None,
            notes=None
        ),

        # Thursday, November 13
        # Information processing
        CalendarEvent(
            title="Information processing",
            start=datetime(2025, 11, 13, 8, 30),
            end=datetime(2025, 11, 13, 9, 30),
            attendees=[],
            location=None,
            notes=None
        ),
        # Investor relations
        CalendarEvent(
            title="Update investment deck for Series A",
            start=datetime(2025, 11, 13, 11, 0),
            end=datetime(2025, 11, 13, 12, 30),
            attendees=[],
            location=None,
            notes=None
        ),
        # Engineering work
        CalendarEvent(
            title="Hospital integrations review",
            start=datetime(2025, 11, 13, 14, 0),
            end=datetime(2025, 11, 13, 16, 0),
            attendees=[],
            location="https://github.com/tensormedical/research",
            notes=None
        ),
        # Energy marker
        CalendarEvent(
            title="E4 - Flow state coding",
            start=datetime(2025, 11, 13, 14, 0),
            end=datetime(2025, 11, 13, 16, 0),
            attendees=[],
            location=None,
            notes=None
        ),

        # Friday, November 14
        # Team standup
        CalendarEvent(
            title="Daily Standup",
            start=datetime(2025, 11, 14, 9, 30),
            end=datetime(2025, 11, 14, 10, 0),
            attendees=[Attendee(email="team@tensormedical.ai")],
            location=None,
            notes=None
        ),
        # Sales follow-up
        CalendarEvent(
            title="Follow-up with BMS on proposal",
            start=datetime(2025, 11, 14, 11, 0),
            end=datetime(2025, 11, 14, 12, 0),
            attendees=[Attendee(email="external@bms.com")],
            location=None,
            notes=None
        ),
        # Strategy planning
        CalendarEvent(
            title="Week 47 planning",
            start=datetime(2025, 11, 14, 15, 0),
            end=datetime(2025, 11, 14, 16, 30),
            attendees=[],
            location=None,
            notes=None
        ),

        # Saturday, November 15 - Personal/family time (excluded)
        CalendarEvent(
            title="Lunch - Helena",
            start=datetime(2025, 11, 15, 13, 0),
            end=datetime(2025, 11, 15, 14, 0),
            attendees=[],
            location=None,
            notes=None
        ),

        # Sunday, November 16 - Rest/meditation
        CalendarEvent(
            title="🧘‍♀️ Meditation",
            start=datetime(2025, 11, 16, 8, 0),
            end=datetime(2025, 11, 16, 9, 0),
            attendees=[],
            location=None,
            notes=None
        )
    ]

    return events


def main():
    """Run Week 46 analysis."""
    print("Week 46 Calendar Analysis")
    print("=" * 50)

    # Get Week 46 date range
    start_date, end_date = get_week46_dates()
    print(f"Analyzing calendar for Week 46: {start_date} to {end_date}")
    print()

    try:
        # Initialize components
        config_manager = ConfigManager()
        config = config_manager.get_config()

        classifier = EventClassifier(config)
        energy_tracker = EnergyTracker()
        report_generator = ReportGenerator()

        # Create sample events for Week 46
        print("Creating Week 46 sample events...")
        events = create_week46_sample_events()

        print(f"Created {len(events)} sample calendar events for Week 46.")

        # Classify events
        print("Classifying events...")
        classified_events = classifier.classify_events(events)

        # Track energy levels
        print("Tracking energy levels...")
        events_with_energy = energy_tracker.track_energy_levels(classified_events, events)

        # Generate report
        print("Generating report...")
        report = report_generator.generate_report(events_with_energy, start_date, end_date)

        # Print report
        print("\n" + "=" * 50)
        print("WEEK 46 ANALYSIS REPORT")
        print("=" * 50)
        print(report)

        # Summary stats
        total_events = len(events_with_energy)
        total_hours = sum(e.duration_hours for e in events_with_energy)
        categories = set(e.category.value for e in events_with_energy)
        energy_levels = set(e.energy_level.value for e in events_with_energy)

        print("\n" + "=" * 50)
        print("📊 WEEK 46 SUMMARY:")
        print(f"   Events analyzed: {total_events}")
        print(".2f")
        print(f"   Categories: {sorted(categories)}")
        print(f"   Energy levels: {sorted(energy_levels)}")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
