"""Event classification engine for calendar analysis."""

import re
from datetime import time
from typing import List, Optional

from .models import (
    CalendarEvent,
    ClassifiedEvent,
    Category,
    EnergyLevel,
    ClassificationConfig
)


class EventClassifier:
    """Classifies calendar events into categories."""

    def __init__(self, config: ClassificationConfig):
        """Initialize classifier with configuration."""
        self.config = config

    def classify_events(self, events: List[CalendarEvent]) -> List[ClassifiedEvent]:
        """Classify a list of calendar events.

        Args:
            events: Raw calendar events to classify

        Returns:
            List of classified events (non-excluded only)
        """
        classified_events = []

        for i, event in enumerate(events, 1):
            if self._should_exclude_event(event):
                continue

            category = self._classify_event(event)
            duration_hours = (event.end - event.start).total_seconds() / 3600

            classified_event = ClassifiedEvent(
                event=event,
                category=category,
                energy_level=EnergyLevel.NOT_AVAILABLE,  # Will be set by energy tracker
                entry_number=i,
                duration_hours=duration_hours
            )

            classified_events.append(classified_event)

        return classified_events

    def _should_exclude_event(self, event: CalendarEvent) -> bool:
        """Check if an event should be excluded from analysis."""
        # Check all-day events
        if self.config.all_day_exclusion:
            start_time = event.start.time()
            end_time = event.end.time()
            if (start_time == time(0, 0) and
                (end_time == time(23, 59) or end_time == time(23, 59, 59))):
                return True

        # Check excluded titles
        for pattern in self.config.excluded_titles:
            if pattern.lower() in event.title.lower():
                return True

        # Check personal patterns
        for pattern in self.config.personal_patterns:
            if pattern.lower() in event.title.lower():
                return True

        # Check energy events (E1-E4, L1-L4)
        if re.match(r'^(E|L)\d(\s*-\s*.+)?$', event.title.strip(), re.IGNORECASE):
            return True

        return False

    def _classify_event(self, event: CalendarEvent) -> Category:
        """Classify a single event using priority-based logic."""
        title_lower = event.title.lower()
        location_lower = (event.location or "").lower()

        # Priority 1: Explicit category name match
        for category in Category:
            if category.value.lower() in title_lower:
                return category

        # Priority 2: External potential clients/partners → Sales/Network
        attendees = self._get_attendee_emails(event)
        external_domains = self._get_external_domains(attendees)

        if external_domains:
            # Check if these look like potential clients
            if self._looks_like_sales_opportunity(event, external_domains):
                return Category.SALES_AND_MARKETING
            else:
                return Category.NETWORK

        # Priority 3: Investors/fundraising → Investor Relations
        if self._contains_keywords(title_lower, self.config.investor_relations_keywords):
            return Category.INVESTOR_RELATIONS

        # Priority 4: Recruiting/hiring → Recruiting
        if self._contains_keywords(title_lower, self.config.recruiting_keywords):
            return Category.RECRUITING

        # Priority 5: @tensormedical.ai team members → Team
        team_attendees = self._get_team_attendees(attendees)
        if team_attendees:
            return Category.TEAM

        # Priority 6: Technical/code/product work → Engineering
        if self._contains_keywords(title_lower, self.config.engineering_keywords):
            return Category.ENGINEERING

        # Priority 7: Check location for GitHub links
        if self._is_github_location(location_lower):
            repo_type = self._get_github_repo_type(location_lower)
            if repo_type == "engineering":
                return Category.ENGINEERING
            elif repo_type == "strategy":
                return Category.STRATEGY

        # Priority 8: Planning/reflection/roadmap → Strategy
        if self._contains_keywords(title_lower, self.config.strategy_keywords):
            return Category.STRATEGY

        # Priority 9: Check other categories
        if self._contains_keywords(title_lower, self.config.information_processing_keywords):
            return Category.INFORMATION_PROCESSING
        elif self._contains_keywords(title_lower, self.config.reading_keywords):
            return Category.READING
        elif self._contains_keywords(title_lower, self.config.sales_marketing_keywords):
            return Category.SALES_AND_MARKETING
        elif self._contains_keywords(title_lower, self.config.operations_keywords):
            return Category.OPERATIONS
        elif self._contains_keywords(title_lower, self.config.exercise_keywords):
            return Category.EXERCISE
        elif self._contains_keywords(title_lower, self.config.meditation_keywords):
            return Category.MEDITATION

        # Default to Other
        return Category.OTHER

    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the keywords."""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)

    def _get_attendee_emails(self, event: CalendarEvent) -> List[str]:
        """Extract email addresses from event attendees."""
        emails = []
        for attendee in event.attendees:
            if attendee.email:
                emails.append(attendee.email.lower())
        return emails

    def _get_external_domains(self, emails: List[str]) -> List[str]:
        """Get domains that are not team domains."""
        external_domains = []
        for email in emails:
            if "@" in email:
                domain = email.split("@")[1]
                if not any(team_domain in domain for team_domain in self.config.team_domains):
                    external_domains.append(domain)
        return list(set(external_domains))  # Remove duplicates

    def _get_team_attendees(self, emails: List[str]) -> List[str]:
        """Get emails from team domains."""
        team_emails = []
        for email in emails:
            if any(team_domain in email for team_domain in self.config.team_domains):
                team_emails.append(email)
        return team_emails

    def _looks_like_sales_opportunity(self, event: CalendarEvent, external_domains: List[str]) -> bool:
        """Check if external meeting looks like a sales opportunity."""
        title_lower = event.title.lower()

        # Check for sales keywords
        sales_indicators = [
            "demo", "presentation", "proposal", "pitch", "call with",
            "meeting with", "discussion with"
        ]

        if any(indicator in title_lower for indicator in sales_indicators):
            return True

        # Check if domains look like companies (not personal)
        for domain in external_domains:
            # Skip obvious personal domains
            if domain in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]:
                continue
            # If we have any business-looking domains, consider it sales
            if "." in domain and len(domain.split(".")[0]) > 2:
                return True

        return False

    def _is_github_location(self, location: str) -> bool:
        """Check if location contains GitHub links."""
        return "github.com" in location

    def _get_github_repo_type(self, location: str) -> Optional[str]:
        """Determine if GitHub repo is engineering or strategy."""
        # Look for repo names in the URL
        for repo in self.config.github_repos_engineering:
            if f"/{repo}" in location:
                return "engineering"

        for repo in self.config.github_repos_strategy:
            if f"/{repo}" in location:
                return "strategy"

        return None
