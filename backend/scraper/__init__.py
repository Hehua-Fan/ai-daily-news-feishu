"""
News scrapers package

This package contains scrapers for different news sources and trending repositories.
"""

from .techcrunch_scraper import TechCrunchScraper
from .verge_scraper import VergeScraper
from .github_trending_scraper import GitHubTrendingScraper

__all__ = ["TechCrunchScraper", "VergeScraper", "GitHubTrendingScraper"]
