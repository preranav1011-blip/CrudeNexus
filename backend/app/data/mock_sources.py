"""Mocked data sources for MVP (to be replaced with real APIs)"""
import logging

logger = logging.getLogger(__name__)


def get_mock_sanctions_exposure(supplier_id: str) -> dict:
    """Return mocked sanctions exposure score for supplier"""
    mock_data = {
        "S001": {"country": "Saudi Arabia", "sanctions_risk_score": 15},
        "S002": {"country": "Russia", "sanctions_risk_score": 85},
        "S003": {"country": "Iran", "sanctions_risk_score": 95},
        "S004": {"country": "UAE", "sanctions_risk_score": 20},
        "S005": {"country": "Kuwait", "sanctions_risk_score": 18},
        "S006": {"country": "Qatar", "sanctions_risk_score": 22},
        "S007": {"country": "USA", "sanctions_risk_score": 10},
        "S008": {"country": "Azerbaijan", "sanctions_risk_score": 25},
    }
    return mock_data.get(supplier_id, {"country": "Unknown", "sanctions_risk_score": 50})


def get_mock_india_crude_demand() -> float:
    """Return India's daily crude oil demand in million barrels"""
    return 4.5  # Million barrels per day


def get_mock_supplier_shares() -> dict:
    """Return historical India import share by supplier"""
    return {
        "S001": 0.35,  # 35% from Saudi Arabia
        "S002": 0.28,  # 28% from Russia
        "S003": 0.08,  # 8% from Iran
        "S004": 0.18,  # 18% from UAE
        "S005": 0.06,  # 6% from Kuwait
        "S006": 0.03,  # 3% from Qatar
        "S007": 0.01,  # 1% from USA
        "S008": 0.01,  # 1% from Azerbaijan
    }


def get_mock_trade_data() -> dict:
    """Return mocked trade data"""
    return {
        "india_crude_demand_mbd": get_mock_india_crude_demand(),
        "supplier_shares": get_mock_supplier_shares(),
        "average_oil_price": 85.0,  # USD per barrel
    }


logger.info("Mock data sources initialized")
