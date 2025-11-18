#!/usr/bin/env python3
"""Test script for calendar analysis MCP server."""

from datetime import datetime, date
from src.calendar_mcp.models import (
    CalendarEvent,
    Attendee,
    ClassificationConfig,
    Category,
    EnergyLevel
)
from src.calendar_mcp.classifier import EventClassifier
from src.calendar_mcp.energy_tracker import EnergyTracker
from src.calendar_mcp.report_generator import ReportGenerator
from src.calendar_mcp.ics_reader import CalendarICSReader


def create_sample_events():
    """Create sample calendar events for testing."""
    base_date = date(2024, 11, 15)

    events = [
        # Team meeting with Tensor Medical attendee
        CalendarEvent(
            title="Tensor Team Meeting",
            start=datetime(2024, 11, 15, 11, 0),
            end=datetime(2024, 11, 15, 12, 0),
            attendees=[Attendee(email="mguirao@tensormedical.ai")],
            location=None,
            notes=None
        ),

        # Investor relations event
        CalendarEvent(
            title="Update investment deck",
            start=datetime(2024, 11, 15, 8, 0),
            end=datetime(2024, 11, 15, 8, 45),
            attendees=[],
            location=None,
            notes=None
        ),

        # Energy marker
        CalendarEvent(
            title="E3",
            start=datetime(2024, 11, 15, 8, 0),
            end=datetime(2024, 11, 15, 8, 45),
            attendees=[],
            location=None,
            notes=None
        ),

        # Sales meeting
        CalendarEvent(
            title="Call with Celia Oreja-Guevara - Tensor Medical Platform Demo",
            start=datetime(2024, 11, 15, 14, 0),
            end=datetime(2024, 11, 15, 15, 30),
            attendees=[Attendee(email="external@client.com")],
            location=None,
            notes=None
        ),

        # Strategy meeting
        CalendarEvent(
            title="Strategy review",
            start=datetime(2024, 11, 15, 16, 0),
            end=datetime(2024, 11, 15, 17, 0),
            attendees=[],
            location=None,
            notes=None
        ),

        # Information processing
        CalendarEvent(
            title="Information processing",
            start=datetime(2024, 11, 15, 9, 0),
            end=datetime(2024, 11, 15, 10, 30),
            attendees=[],
            location=None,
            notes=None
        ),

        # Exercise
        CalendarEvent(
            title="🏋️ Keetlebell",
            start=datetime(2024, 11, 15, 18, 0),
            end=datetime(2024, 11, 15, 19, 0),
            attendees=[],
            location=None,
            notes=None
        ),

        # All-day event (should be excluded)
        CalendarEvent(
            title="All Day Event",
            start=datetime(2024, 11, 15, 0, 0),
            end=datetime(2024, 11, 15, 23, 59, 59),
            attendees=[],
            location=None,
            notes=None
        ),

        # Personal event (should be excluded)
        CalendarEvent(
            title="Lunch - Helena",
            start=datetime(2024, 11, 15, 12, 30),
            end=datetime(2024, 11, 15, 13, 30),
            attendees=[],
            location=None,
            notes=None
        ),

        # Blocked event (should be excluded)
        CalendarEvent(
            title="Blocked ✋",
            start=datetime(2024, 11, 15, 10, 0),
            end=datetime(2024, 11, 15, 10, 30),
            attendees=[],
            location=None,
            notes=None
        )
    ]

    return events


def test_classification():
    """Test event classification."""
    print("Testing event classification...")

    config = ClassificationConfig()
    classifier = EventClassifier(config)
    events = create_sample_events()

    classified_events = classifier.classify_events(events)

    # Verify classifications
    expected_classifications = {
        "Tensor Team Meeting": Category.TEAM,
        "Update investment deck": Category.INVESTOR_RELATIONS,
        "Call with Celia Oreja-Guevara - Tensor Medical Platform Demo": Category.SALES_AND_MARKETING,
        "Strategy review": Category.STRATEGY,
        "Information processing": Category.INFORMATION_PROCESSING,
        "🏋️ Keetlebell": Category.EXERCISE,
    }

    for event in classified_events:
        expected = expected_classifications.get(event.event.title)
        if expected:
            assert event.category == expected, f"Expected {expected}, got {event.category} for '{event.event.title}'"
            print(f"✓ '{event.event.title}' → {event.category.value}")

    # Verify exclusions (should not appear in classified events)
    classified_titles = {e.event.title for e in classified_events}
    excluded_events = ["All Day Event", "Lunch - Helena", "Blocked ✋", "E3"]
    for excluded in excluded_events:
        assert excluded not in classified_titles, f"'{excluded}' should be excluded but was classified"

    print(f"✓ Classified {len(classified_events)} events, excluded {len(excluded_events)} events")
    return classified_events


def test_energy_tracking():
    """Test energy level tracking."""
    print("\nTesting energy level tracking...")

    config = ClassificationConfig()
    classifier = EventClassifier(config)
    energy_tracker = EnergyTracker()

    events = create_sample_events()
    # First classify events (this will exclude energy events)
    classified_events = classifier.classify_events(events)
    # Then track energy levels on the classified events, passing raw events for energy markers
    events_with_energy = energy_tracker.track_energy_levels(classified_events, events)

    # Find the investment deck event
    investment_event = None
    for event in events_with_energy:
        if event.event.title == "Update investment deck":
            investment_event = event
            break

    assert investment_event is not None, "Investment deck event not found"
    assert investment_event.energy_level == EnergyLevel.HIGH, f"Expected High energy, got {investment_event.energy_level}"

    print("✓ Energy tracking working correctly")
    return events_with_energy


def test_report_generation():
    """Test report generation."""
    print("\nTesting report generation...")

    config = ClassificationConfig()
    classifier = EventClassifier(config)
    energy_tracker = EnergyTracker()
    report_generator = ReportGenerator()

    events = create_sample_events()
    classified_events = classifier.classify_events(events)
    events_with_energy = energy_tracker.track_energy_levels(classified_events, events)

    report = report_generator.generate_report(events_with_energy)

    # Verify report contains expected sections
    assert "# Calendar Analysis Report" in report
    assert "## 1. Raw Events Table" in report
    assert "## 2. Daily Summary Table" in report
    assert "## 3. Category Distribution" in report
    assert "## 4. Energy Distribution" in report

    # Verify tables have proper format
    assert "| Entry Num | Name | Day |" in report
    assert "| Category | Total Hours | % of time |" in report

    # Verify mermaid charts
    assert "pie title Time Distribution by Category" in report
    assert "pie title Energy Distribution" in report

    # Verify proper formatting (comma decimals, dd/mm/yyyy)
    assert "0,75" in report  # 0.75 hours formatted as 0,75
    assert "15/11/2024" in report  # dd/mm/yyyy format

    print("✓ Report generation working correctly")
    print(f"✓ Report length: {len(report)} characters")

    return report


def main():
    """Run all tests."""
    print("Running Calendar Analysis MCP Tests")
    print("=" * 50)

    try:
        # Run tests
        classified_events = test_classification()
        events_with_energy = test_energy_tracking()
        report = test_report_generation()

        print("\n" + "=" * 50)
        print("✅ All tests passed!")

        # Show summary
        total_events = len(events_with_energy)
        total_hours = sum(e.duration_hours for e in events_with_energy)
        categories = set(e.category.value for e in events_with_energy)
        energy_levels = set(e.energy_level.value for e in events_with_energy)

        print("\n📊 Test Results Summary:")
        print(f"   Events processed: {total_events}")
        print(f"   Total hours: {total_hours:.2f}")
        print(f"   Categories found: {sorted(categories)}")
        print(f"   Energy levels found: {sorted(energy_levels)}")

        print(f"\n📄 Sample report output (first 500 chars):\n{report[:500]}...")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
