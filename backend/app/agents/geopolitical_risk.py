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


def score_risk_for_event(
    event: Dict,
    ml_prediction: Optional[float] = None
) -> Dict:
    """
    Convert geopolitical event into a risk score for India's supply chain.
    
    Combines:
    - Event severity
    - India-specific relevance
    - ML disruption prediction
    - Affected suppliers/corridors
    
    Returns:
    {
        "risk_score": 0-100,
        "confidence": 0-1,
        "evidence": {
            "news_signal": 0-1,
            "sanctions_signal": 0-1,
            "historical_signal": 0-1
        }
    }
    """
    logger.debug(f"Scoring risk for event: {event.get('location')}")
    
    # TODO: Implement in Phase 5
    
    return {
        "risk_score": 50,
        "confidence": 0.5,
        "evidence": {
            "news_signal": 0.6,
            "sanctions_signal": 0.4,
            "historical_signal": 0.5
        }
    }


logger.info("Geopolitical risk agent initialized")
