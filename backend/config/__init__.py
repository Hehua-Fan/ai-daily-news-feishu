"""
Core modules for AI News Bot

This package contains core functionality including configuration management and database operations.
"""

from .config_manager import ConfigManager
from .database import NewsDatabase

__all__ = ["ConfigManager", "NewsDatabase"]
