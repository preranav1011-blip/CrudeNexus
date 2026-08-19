"""Geopolitical risk intelligence agent"""
import logging
from typing import Optional, Dict
from app.config import LLM_CONFIG
from app.data.fallbacks import extract_event_heuristic

logger = logging.getLogger(__name__)


def extract_event_from_text(text: str) -> Dict:
    """
    Extract structured geopolitical event from unstructured text.
    
    Tries LLM extraction first (if Ollama available), falls back to heuristic.
    
    Returns:
    {
        "event_type": "...",
        "location": "...",
        "severity": 0.0-1.0,
        "disruption_probability": 0.0-1.0,
        "affected_corridor": "...",
        "india_relevance": 0.0-1.0,
        "confidence": 0.0-1.0,
    }
    """
    if not text:
        return extract_event_heuristic(text)
    
    # Try LLM extraction if enabled
    if LLM_CONFIG.get("enabled"):
        try:
            return _extract_event_llm(text)
        except ConnectionError:
            logger.warning("Ollama unavailable, falling back to heuristic extraction")
            return extract_event_heuristic(text)
        except Exception as e:
            logger.warning(f"LLM extraction failed: {e}, using fallback")
            return extract_event_heuristic(text)
    else:
        logger.debug("LLM disabled in config, using heuristic extraction")
        return extract_event_heuristic(text)


def _extract_event_llm(text: str) -> Dict:
    """
    LLM-based event extraction using Ollama + Qwen.
    
    Requires Ollama to be running on LLM_CONFIG["base_url"]
    """
    logger.debug("Attempting LLM-based event extraction")
    
    try:
        from langchain.llms import Ollama
        import json
        
        llm = Ollama(
            model=LLM_CONFIG["model"],
            base_url=LLM_CONFIG["base_url"],
        )
        
        prompt = f"""Extract structured geopolitical event from this text.

Text: {text}

Return ONLY valid JSON (no markdown, no explanations):
{{
  "event_type": "geopolitical_tension|port_disruption|sanctions|price_movement|other",
  "location": "location name",
  "severity": 0.0-1.0,
  "disruption_probability": 0.0-1.0,
  "affected_corridor": "corridor name or location",
  "india_relevance": 0.0-1.0,
  "confidence": 0.0-1.0
}}"""
        
        response = llm(prompt)
        
        # Parse JSON response
        # TODO: Add JSON validation and error handling
        logger.debug(f"LLM response: {response}")
        
        return extract_event_heuristic(text)  # Fallback to heuristic for now
        
    except ImportError:
        logger.warning("LangChain not installed, cannot use LLM extraction")
        raise ConnectionError("LLM provider not available")


def calculate_risk_score(event) -> Dict:
    """
    Convert geopolitical event into a risk score for India's supply chain.
    
    Combines:
    - Event severity
    - India-specific relevance
    - Event type risk multiplier
    - Affected corridor criticality
    
    Returns:
    {
        "risk_score_ml": 0-100,
        "confidence": 0-1,
        "disruption_probability": 0-1,
        "sanctions_signal": 0-1,
        "historical_signal": 0-1
    }
    """
    logger.debug(f"Calculating risk score for event: {event.location}")
    
    # Base risk from severity and india relevance
    base_risk = (event.severity_raw + event.india_relevance) / 2 * 100  # 0-100
    
    # Event type multiplier
    event_type_multiplier = {
        "geopolitical_tension": 1.2,
        "port_disruption": 1.5,
        "sanctions_action": 1.3,
        "price_movement": 0.8,
        "naval_exercise": 1.0,
        "blockade": 1.8,
    }.get(event.event_type, 1.0)
    
    # Apply multiplier
    adjusted_risk = min(100, base_risk * event_type_multiplier)
    
    # Confidence based on raw confidence and event freshness
    from datetime import datetime, timedelta
    time_since_event = datetime.utcnow() - event.timestamp
    recency_factor = max(0.3, 1.0 - (time_since_event.days / 30))  # Decay over 30 days
    
    confidence = event.raw_confidence * recency_factor
    
    # Set disruption probability based on risk level
    disruption_prob = min(0.95, adjusted_risk / 100 * 0.8 + 0.1)
    
    return {
        "risk_score_ml": adjusted_risk,
        "confidence": confidence,
        "disruption_probability": disruption_prob,
        "sanctions_signal": 0.7 if "sanction" in event.event_type.lower() else 0.2,
        "historical_signal": min(0.8, base_risk / 100),
    }


logger.info("Geopolitical risk agent initialized")
