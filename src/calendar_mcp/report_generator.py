"""Report generator for calendar analysis."""

from collections import defaultdict
from datetime import date
from typing import Dict, List, Tuple

from .models import (
    ClassifiedEvent,
    Category,
    EnergyLevel,
    DailySummary,
    DailyCategory,
    CategoryDistribution,
    EnergyDistribution,
    AnalysisReport,
    DateRange
)


class ReportGenerator:
    """Generates comprehensive analysis reports in markdown format."""

    def generate_report(self, events: List[ClassifiedEvent]) -> str:
        """Generate a complete analysis report.

        Args:
            events: Classified events to analyze

        Returns:
            Complete markdown report
        """
        if not events:
            return "No events found for the specified date range."

        # Sort events chronologically
        sorted_events = sorted(events, key=lambda e: (e.event.start.date(), e.event.start))

        # Calculate date range
        start_date = min(e.event.start.date() for e in events)
        end_date = max(e.event.end.date() for e in events)

        # Generate report components
        raw_events_table = self._generate_raw_events_table(sorted_events)
        daily_summaries = self._calculate_daily_summaries(sorted_events)
        daily_summary_table = self._generate_daily_summary_table(daily_summaries)
        category_dist = self._calculate_category_distribution(sorted_events)
        category_table, category_chart = self._generate_category_distribution(category_dist)
        energy_dist = self._calculate_energy_distribution(sorted_events)
        energy_table, energy_chart = self._generate_energy_distribution(energy_dist)

        total_hours = sum(event.duration_hours for event in events)

        # Combine all sections
        report = f"""# Calendar Analysis Report

**Date Range:** {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}
**Total Hours:** {self._format_hours(total_hours)}
**Total Events:** {len(events)}

## 1. Raw Events Table

{raw_events_table}

## 2. Daily Summary Table

{daily_summary_table}

## 3. Category Distribution

{category_table}

{category_chart}

## 4. Energy Distribution

{energy_table}

{energy_chart}
"""

        return report

    def _generate_raw_events_table(self, events: List[ClassifiedEvent]) -> str:
        """Generate the raw events table."""
        if not events:
            return "No events to display."

        lines = [
            "| Entry Num | Name | Day | Event Init | Event End | Total time | Category | Energy |",
            "|-----------|------|-----|------------|-----------|------------|----------|--------|"
        ]

        for event in events:
            day = event.event.start.strftime('%d/%m/%Y')
            start_time = event.event.start.strftime('%H:%M')
            end_time = event.event.end.strftime('%H:%M')
            total_time = self._format_hours(event.duration_hours)

            lines.append(
                f"| {event.entry_number} | {event.event.title} | {day} | {start_time} | {end_time} | {total_time} | {event.category.value} | {event.energy_level.value} |"
            )

        return "\n".join(lines)

    def _calculate_daily_summaries(self, events: List[ClassifiedEvent]) -> List[DailySummary]:
        """Calculate daily summaries with top 3 categories and energy breakdowns."""
        daily_data = defaultdict(lambda: {
            'events': [],
            'categories': defaultdict(float),
            'energies': defaultdict(float)
        })

        # Group events by day
        for event in events:
            day = event.event.start.date()
            daily_data[day]['events'].append(event)
            daily_data[day]['categories'][event.category] += event.duration_hours
            daily_data[day]['energies'][event.energy_level] += event.duration_hours

        summaries = []
        for day, data in daily_data.items():
            # Get top 3 categories by time spent
            categories_sorted = sorted(
                data['categories'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]

            # Calculate energy percentages
            total_day_hours = sum(data['energies'].values())
            energy_percentages = {}
            if total_day_hours > 0:
                for energy_level, hours in data['energies'].items():
                    if energy_level != EnergyLevel.NOT_AVAILABLE:
                        percentage = (hours / total_day_hours) * 100
                        energy_percentages[energy_level] = percentage

            # Format categories string
            category_parts = []
            for category, hours in categories_sorted:
                event_names = [
                    e.event.title for e in data['events']
                    if e.category == category
                ][:2]  # Show max 2 event names
                events_str = ", ".join(event_names)
                category_parts.append(f"{category.value} ({self._format_hours(hours)}h): {events_str}")

            categories_str = "; ".join(category_parts)

            # Format energy string
            energy_parts = []
            for energy_level in [EnergyLevel.ZONE_OF_GENIUS, EnergyLevel.HIGH, EnergyLevel.LOW, EnergyLevel.VERY_LOW]:
                if energy_level in energy_percentages:
                    energy_parts.append(f"{energy_level.value}: {energy_percentages[energy_level]:.0f}%")

            energy_str = ", ".join(energy_parts)

            # Create DailyCategory objects
            daily_categories = []
            for category, hours in categories_sorted:
                event_names = [
                    e.event.title for e in data['events']
                    if e.category == category
                ][:2]  # Show max 2 event names
                daily_categories.append(DailyCategory(
                    category=category,
                    hours=hours,
                    event_names=event_names
                ))

            summaries.append(DailySummary(
                date=day,
                categories=daily_categories,
                energy_breakdown=energy_percentages
            ))

        # Sort by date
        return sorted(summaries, key=lambda s: s.date)

    def _generate_daily_summary_table(self, summaries: List[DailySummary]) -> str:
        """Generate the daily summary table."""
        if not summaries:
            return "No daily summaries to display."

        lines = [
            "| Day | Categories | Energy levels |",
            "|-----|------------|---------------|"
        ]

        for summary in summaries:
            day_str = summary.date.strftime('%d/%m/%Y')

            # Format categories
            category_parts = []
            for cat_info in summary.categories:
                events_str = ", ".join(cat_info.event_names[:2])
                category_parts.append(f"{cat_info.category.value} ({self._format_hours(cat_info.hours)}h): {events_str}")
            categories_str = "; ".join(category_parts)

            # Format energy levels
            energy_parts = []
            for energy_level in [EnergyLevel.ZONE_OF_GENIUS, EnergyLevel.HIGH, EnergyLevel.LOW, EnergyLevel.VERY_LOW]:
                if energy_level in summary.energy_breakdown:
                    pct = summary.energy_breakdown[energy_level]
                    energy_parts.append(f"E{4 - list(EnergyLevel).index(energy_level)}: {pct:.0f}%")

            energy_str = ", ".join(energy_parts)

            lines.append(f"| {day_str} | {categories_str} | {energy_str} |")

        return "\n".join(lines)

    def _calculate_category_distribution(self, events: List[ClassifiedEvent]) -> List[CategoryDistribution]:
        """Calculate time distribution across categories."""
        category_hours = defaultdict(float)
        total_hours = 0

        for event in events:
            category_hours[event.category] += event.duration_hours
            total_hours += event.duration_hours

        distributions = []
        for category, hours in category_hours.items():
            percentage = (hours / total_hours * 100) if total_hours > 0 else 0
            distributions.append(CategoryDistribution(
                category=category,
                total_hours=hours,
                percentage=percentage
            ))

        # Sort by hours descending
        return sorted(distributions, key=lambda d: d.total_hours, reverse=True)

    def _generate_category_distribution(self, distributions: List[CategoryDistribution]) -> Tuple[str, str]:
        """Generate category distribution table and chart."""
        if not distributions:
            return "No category data to display.", ""

        # Table
        lines = [
            "| Category | Total Hours | % of time |",
            "|----------|-------------|-----------|"
        ]

        for dist in distributions:
            lines.append(
                f"| {dist.category.value} | {self._format_hours(dist.total_hours)} | {dist.percentage:.1f}% |"
            )

        table = "\n".join(lines)

        # Pie chart
        chart_lines = ["```mermaid", "pie title Time Distribution by Category"]
        for dist in distributions:
            chart_lines.append(f'"{dist.category.value}" : {dist.total_hours:.2f}')

        chart_lines.append("```")
        chart = "\n".join(chart_lines)

        return table, chart

    def _calculate_energy_distribution(self, events: List[ClassifiedEvent]) -> List[EnergyDistribution]:
        """Calculate time distribution across energy levels."""
        energy_hours = defaultdict(float)
        total_hours = 0

        for event in events:
            energy_hours[event.energy_level] += event.duration_hours
            total_hours += event.duration_hours

        distributions = []
        for energy_level, hours in energy_hours.items():
            percentage = (hours / total_hours * 100) if total_hours > 0 else 0
            distributions.append(EnergyDistribution(
                energy_level=energy_level,
                total_hours=hours,
                percentage=percentage
            ))

        # Sort by hours descending
        return sorted(distributions, key=lambda d: d.total_hours, reverse=True)

    def _generate_energy_distribution(self, distributions: List[EnergyDistribution]) -> Tuple[str, str]:
        """Generate energy distribution table and chart."""
        if not distributions:
            return "No energy data to display.", ""

        # Table
        lines = [
            "| Energy Level | Total Hours | % of time |",
            "|--------------|-------------|-----------|"
        ]

        for dist in distributions:
            lines.append(
                f"| {dist.energy_level.value} | {self._format_hours(dist.total_hours)} | {dist.percentage:.1f}% |"
            )

        table = "\n".join(lines)

        # Pie chart
        chart_lines = ["```mermaid", "pie title Energy Distribution"]
        for dist in distributions:
            chart_lines.append(f'"{dist.energy_level.value}" : {dist.total_hours:.2f}')

        chart_lines.append("```")
        chart = "\n".join(chart_lines)

        return table, chart

    def _format_hours(self, hours: float) -> str:
        """Format hours with comma decimal separator."""
        return f"{hours:.2f}".replace(".", ",")
