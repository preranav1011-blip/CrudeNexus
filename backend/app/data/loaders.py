"""GDELT data fetcher for geopolitical events"""
import logging
import requests
from typing import List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

GDELT_API_URL = "https://gdeltproject.org/api/v2/search/tv"


def fetch_gdelt_events(
    keywords: Optional[List[str]] = None,
    hours_back: int = 24,
    limit: int = 100
) -> List[dict]:
    """
    Fetch geopolitical events from GDELT Project.
    
    Args:
        keywords: Search keywords (if None, uses defaults from config)
        hours_back: Historical window in hours
        limit: Max results to return
    
    Returns:
        List of event dictionaries with timestamp, description, etc.
    """
    if keywords is None:
        keywords = settings.gdelt_keywords
    
    events = []

    # Build query string
    query_str = " ".join(keywords)
    params = {
        "query": query_str,
        "maxrecords": limit,
    }

    try:
        resp = requests.get(GDELT_API_URL, params=params, timeout=10)
        if not resp.ok:
            logger.warning(f"GDELT request returned status {resp.status_code}")
            return events

        data = resp.json()
        # GDELT v2 responses vary by endpoint; try common keys
        if isinstance(data, dict):
            # Prefer 'articles' or 'results' if present
            if "articles" in data and isinstance(data["articles"], list):
                events = data["articles"]
            elif "results" in data and isinstance(data["results"], list):
                events = data["results"]
            else:
                # Fallback: try to find top-level list value
                for v in data.values():
                    if isinstance(v, list):
                        events = v
                        break
        elif isinstance(data, list):
            events = data

    except Exception as exc:
        logger.exception("Failed to fetch or parse GDELT data: %s", exc)
        # Return empty list on any failure to keep caller resilient
        return []

    logger.info(f"Fetched {len(events)} events from GDELT (keywords: {', '.join(keywords[:3])}...)")
    return events


def query_gdelt(query: str) -> List[dict]:
    """
    Query GDELT with a specific search term.

    Args:
        query: Search query string

    Returns:
        List of matching events
    """
    logger.debug(f"Querying GDELT for: {query}")
    # Reuse fetch_gdelt_events with the single query term
    return fetch_gdelt_events(keywords=[query], hours_back=24, limit=100)


logger.info("GDELT fetcher initialized")
