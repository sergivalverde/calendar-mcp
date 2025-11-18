"""Calendar Analysis MCP Server.

An executive assistant that analyzes calendar data to provide insights
into time allocation, work patterns, and productivity.

Uses unified cache architecture with icalBuddy for reliable calendar access.
"""

__version__ = "0.2.0"

# Export main components
from .unified_cache import UnifiedCache
from .calendar_manager import CalendarManager
from .config import ConfigManager, CalendarAnalysisConfig
from .server import CalendarAnalysisServer

__all__ = [
    "UnifiedCache",
    "CalendarManager",
    "ConfigManager",
    "CalendarAnalysisConfig",
    "CalendarAnalysisServer",
]
