"""Data models for calendar analysis MCP server."""

from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


class Category(str, Enum):
    """Event categories for classification."""

    INFORMATION_PROCESSING = "Information Processing"
    RECRUITING = "Recruiting"
    READING = "Reading"
    TEAM = "Team"
    INVESTOR_RELATIONS = "Investor Relations"
    STRATEGY = "Strategy"
    SALES_AND_MARKETING = "Sales and Marketing"
    NETWORK = "Network"
    ENGINEERING = "Engineering"
    OPERATIONS = "Operations"
    EXERCISE = "Exercise"
    MEDITATION = "Meditation"
    OTHER = "Other"


class EnergyLevel(str, Enum):
    """Energy levels for events."""

    VERY_LOW = "Very low energy"
    LOW = "Low energy"
    HIGH = "High energy"
    ZONE_OF_GENIUS = "Zone of Genius"
    NOT_AVAILABLE = "N/A"


class Attendee(BaseModel):
    """Calendar event attendee."""

    name: Optional[str] = None
    email: Optional[str] = None


class CalendarEvent(BaseModel):
    """Raw calendar event data."""

    title: str
    start: datetime
    end: datetime
    attendees: List[Attendee] = Field(default_factory=list)
    location: Optional[str] = None
    notes: Optional[str] = None
    calendar: Optional[str] = None


class ClassifiedEvent(BaseModel):
    """Event with classification and energy level."""

    event: CalendarEvent
    category: Category
    energy_level: EnergyLevel
    entry_number: int
    duration_hours: float

    @property
    def is_excluded(self) -> bool:
        """Check if this event should be excluded from analysis."""
        return False  # This will be determined by the classifier


class DailyCategory(BaseModel):
    """Category information for daily summary."""

    category: Category
    hours: float
    event_names: List[str]


class DailySummary(BaseModel):
    """Summary for a single day."""

    date: date
    categories: List[DailyCategory]
    energy_breakdown: dict[EnergyLevel, float]  # Energy level -> percentage


class CategoryDistribution(BaseModel):
    """Time distribution across categories."""

    category: Category
    total_hours: float
    percentage: float


class EnergyDistribution(BaseModel):
    """Time distribution across energy levels."""

    energy_level: EnergyLevel
    total_hours: float
    percentage: float


class DateRange(BaseModel):
    """Date range for analysis."""

    start: date
    end: date


class AnalysisReport(BaseModel):
    """Complete analysis report."""

    raw_events: List[ClassifiedEvent]
    daily_summaries: List[DailySummary]
    category_distribution: List[CategoryDistribution]
    energy_distribution: List[EnergyDistribution]
    total_hours: float
    date_range: DateRange


class CalendarConfig(BaseModel):
    """Configuration for calendar access."""

    # Calendar selection
    calendars: Optional[List[str]] = None  # If None, uses all calendars
    default_calendar: str = "Calendar"  # Default calendar for event creation

    # Event creation settings
    event_creation: Dict[str, Any] = Field(default_factory=lambda: {
        "default_duration_minutes": 60,
        "default_morning_start": "09:00",
        "default_afternoon_start": "14:00",
        "default_evening_start": "18:00",
        "work_hours_start": "09:00",
        "work_hours_end": "17:00"
    })


class ClassificationConfig(BaseModel):
    """Configuration for event classification."""

    # Exclusion patterns
    excluded_titles: List[str] = Field(default_factory=lambda: [
        "Blocked ✋", "Blocked", "Busy", "Tentative"
    ])
    personal_patterns: List[str] = Field(default_factory=lambda: [
        "Helena", "Furgo Sergi - Mireia ❤️", "Teatre mireia i amigues", "Lunch - Helena"
    ])
    all_day_exclusion: bool = True

    # Team domains
    team_domains: List[str] = Field(default_factory=lambda: ["tensormedical.ai"])

    # Category keywords
    information_processing_keywords: List[str] = Field(default_factory=lambda: [
        "email", "processing", "information", "communication"
    ])

    recruiting_keywords: List[str] = Field(default_factory=lambda: [
        "interview", "recruiting", "hiring", "candidate"
    ])

    reading_keywords: List[str] = Field(default_factory=lambda: [
        "reading", "anki", "study", "paper", "book"
    ])

    team_keywords: List[str] = Field(default_factory=lambda: [
        "1:1", "sync", "weekly", "bi-weekly", "standup"
    ])

    investor_relations_keywords: List[str] = Field(default_factory=lambda: [
        "investment", "investor", "shareholder", "fundraising", "deck", "pitch"
    ])

    strategy_keywords: List[str] = Field(default_factory=lambda: [
        "strategy", "planning", "recap", "roadmap", "reflection", "vision", "objective"
    ])

    sales_marketing_keywords: List[str] = Field(default_factory=lambda: [
        "demo", "proposal", "call with", "presentation", "pitch"
    ])

    network_keywords: List[str] = Field(default_factory=lambda: [
        "network", "connection", "event", "conference"
    ])

    engineering_keywords: List[str] = Field(default_factory=lambda: [
        "review", "integration", "product", "technical", "code", "implementation"
    ])

    operations_keywords: List[str] = Field(default_factory=lambda: [
        "audit", "tax", "legal", "HR", "compliance", "accounting", "operations"
    ])

    exercise_keywords: List[str] = Field(default_factory=lambda: [
        "exercise", "workout", "run", "swim", "gym", "🏋️", "🏃‍♀️", "🏊‍♂️"
    ])

    meditation_keywords: List[str] = Field(default_factory=lambda: [
        "meditation", "mindfulness", "🧘‍♀️"
    ])

    # Location patterns
    github_repos_engineering: List[str] = Field(default_factory=lambda: ["research", "brain"])
    github_repos_strategy: List[str] = Field(default_factory=lambda: ["brain"])


class EventRequest(BaseModel):
    """Request to create a calendar event."""

    title: str
    start_datetime: datetime
    end_datetime: datetime
    calendar_name: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    attendees: List[str] = []


class TimePreference(BaseModel):
    """Time preference for scheduling."""

    preference: str  # "morning", "afternoon", "evening"
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class FreeSlot(BaseModel):
    """Available time slot."""

    start: datetime
    end: datetime
    duration_minutes: int


class QueryRequest(BaseModel):
    """Request for calendar analysis."""

    query: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
