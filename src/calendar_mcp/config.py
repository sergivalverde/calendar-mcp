"""Configuration management for calendar analysis."""

import json
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from .models import ClassificationConfig, CalendarConfig


class CalendarAnalysisConfig(BaseModel):
    """Combined configuration for calendar analysis."""

    calendar: CalendarConfig = Field(default_factory=CalendarConfig)
    classification: ClassificationConfig = Field(default_factory=ClassificationConfig)


class ConfigManager:
    """Manages configuration for the calendar analysis system."""

    DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.json"

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager.

        Args:
            config_path: Path to config file. If None, uses default location.
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config = None

    def get_config(self) -> CalendarAnalysisConfig:
        """Get the current configuration."""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def reload_config(self) -> CalendarAnalysisConfig:
        """Reload configuration from file."""
        self._config = self._load_config()
        return self._config

    def _load_config(self) -> CalendarAnalysisConfig:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            # Create default config if it doesn't exist
            self._create_default_config()
            return self._get_default_config()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return CalendarAnalysisConfig(**data)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Failed to load config from {self.config_path}: {e}")
            print("Using default configuration.")
            return self._get_default_config()

    def _get_default_config(self) -> CalendarAnalysisConfig:
        """Get the default configuration."""
        return CalendarAnalysisConfig()

    def _create_default_config(self):
        """Create the default configuration file."""
        default_config = self._get_default_config()
        config_dict = default_config.model_dump()

        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)

    def save_config(self, config: CalendarAnalysisConfig):
        """Save configuration to file."""
        config_dict = config.model_dump()
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)

        self._config = config

    def get_config_path(self) -> Path:
        """Get the path to the configuration file."""
        return self.config_path
