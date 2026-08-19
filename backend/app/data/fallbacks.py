"""Fallback event extraction without LLM"""
import re
import logging

logger = logging.getLogger(__name__)


def extract_event_heuristic(text: str) -> dict:
    """
    Fallback event extraction using keywords and regex.
    Used when Ollama is unavailable.
    """
    if not text:
        return _default_event()
    
    # Determine event type
    event_type = _classify_event_type(text)
    
    # Extract location
    location = _extract_location(text)
    
    # Calculate severity
    severity = _calculate_severity(text)
    
    # Assess India relevance
    india_relevance = _assess_india_relevance(text)
    
    return {
        "event_type": event_type,
        "location": location,
        "severity": severity,
        "disruption_probability": severity * 0.8,
        "affected_corridor": location,
        "india_relevance": india_relevance,
        "confidence": 0.4,  # Low confidence for heuristic
    }


def _default_event() -> dict:
    """Return default event structure"""
    return {
        "event_type": "unknown",
        "location": "Unknown",
        "severity": 0.5,
        "disruption_probability": 0.4,
        "affected_corridor": "Unknown",
        "india_relevance": 0.5,
        "confidence": 0.3,
    }


def _classify_event_type(text: str) -> str:
    """Classify event type from text"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["port", "shipping", "cargo", "vessel", "tanker"]):
        return "port_disruption"
    elif any(word in text_lower for word in ["sanction", "embargo", "restriction"]):
        return "sanctions"
    elif any(word in text_lower for word in ["conflict", "war", "attack", "strikes", "tensions"]):
        return "geopolitical_conflict"
    elif any(word in text_lower for word in ["price", "barrel", "crude"]):
        return "price_movement"
    else:
        return "geopolitical_event"


def _extract_location(text: str) -> str:
    """Extract location/corridor from text"""
    text_lower = text.lower()
    
    locations = [
        ("Strait of Hormuz", "Hormuz"),
        ("Hormuz", "Hormuz"),
        ("Suez Canal", "Suez"),
        ("Suez", "Suez"),
        ("Red Sea", "Red Sea"),
        ("Persian Gulf", "Persian Gulf"),
        ("Cape of Good Hope", "Cape of Good Hope"),
        ("Bab el-Mandeb", "Red Sea"),
    ]
    
    for loc_pattern, loc_name in locations:
        if loc_pattern.lower() in text_lower:
            return loc_name
    
    return "Unknown"


def _calculate_severity(text: str) -> float:
    """Calculate severity score 0-1"""
    text_lower = text.lower()
    
    base_severity = 0.5
    
    # Increase for high-impact keywords
    if any(word in text_lower for word in ["escalat", "crisis", "critical", "severe", "emergency"]):
        return min(0.9, base_severity + 0.3)
    
    # Decrease for low-impact keywords
    if any(word in text_lower for word in ["minor", "report", "technical", "brief"]):
        return max(0.2, base_severity - 0.2)
    
    return base_severity


def _assess_india_relevance(text: str) -> float:
    """Assess relevance to India's crude supply (0-1)"""
    text_lower = text.lower()
    
    base_relevance = 0.0
    
    # Direct India mention
    if any(word in text_lower for word in ["india", "indian", "delhi"]):
        base_relevance += 0.5
    
    # Indian ports
    if any(port in text_lower for port in ["mundra", "jawaharlal nehru", "cochin", "paradip"]):
        base_relevance += 0.4
    
    # Crude/oil related
    if any(word in text_lower for word in ["crude", "oil", "barrel", "petroleum"]):
        base_relevance += 0.2
    
    # Major supplier regions
    if any(country in text_lower for country in ["saudi", "russia", "iran", "uae", "middle east"]):
        base_relevance += 0.3
    
    # Critical chokepoints
    if any(loc in text_lower for loc in ["hormuz", "suez", "red sea"]):
        base_relevance += 0.3
    
    return min(1.0, base_relevance)


logger.info("Heuristic fallback extractor initialized")
