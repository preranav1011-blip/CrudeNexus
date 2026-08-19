"""Routes for procurement optimization endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import ProcurementStrategy, SupplierAllocation, RiskAssessment
from app.models.optimization import (
    OptimizationRequest, 
    OptimizationResultsResponse,
    StrategyResponse,
    StrategyComparisonResponse
)
from app.agents.procurement_optimizer import optimize_procurement
from app.data.csv_loaders import SupplierLoader, RouteLoader
from app.data.mock_sources import get_mock_india_crude_demand
import json
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/strategies", response_model=OptimizationResultsResponse)
async def generate_strategies(
    request: OptimizationRequest,
    db: Session = Depends(get_db)
):
    """Generate three procurement strategies (cheapest, balanced, safest)"""
    try:
        # Load master data
        suppliers = SupplierLoader.load_suppliers()
        routes = RouteLoader.load_routes()
        
        if not suppliers or not routes:
            raise HTTPException(status_code=400, detail="Missing supplier or route data")
        
        # Get India demand
        india_demand = request.india_demand_mbd or get_mock_india_crude_demand()
        
        # Handle blocked corridors
        blocked_corridors = request.blocked_corridors or []
        
        # Get risk context from assessment if provided
        risk_context = None
        if request.risk_assessment_id:
            risk_context = db.query(RiskAssessment).filter(
                RiskAssessment.assessment_id == request.risk_assessment_id
            ).first()
        
        # Generate strategies using optimizer
        cheapest, balanced, safest = optimize_procurement(
            suppliers=suppliers,
            routes=routes,
            india_demand_mbd=india_demand,
            risk_tolerance=request.risk_tolerance or 0.5,
            blocked_corridors=blocked_corridors,
            risk_context=risk_context
        )
        
        # Save strategies to database
        saved_strategies = []
        
        for strategy_dict in [cheapest, balanced, safest]:
            strategy_id = f"STR_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            db_strategy = ProcurementStrategy(
                strategy_id=strategy_id,
                strategy_type=strategy_dict.get("strategy_type", "balanced"),
                risk_assessment_id=request.risk_assessment_id,
                total_cost=strategy_dict.get("total_cost", 0),
                total_crude_supply=strategy_dict.get("total_crude_supply", india_demand),
                avg_risk_score=strategy_dict.get("avg_risk_score", 50),
                avg_transit_time=strategy_dict.get("avg_transit_time", 20),
                supplier_concentration_ratio=strategy_dict.get("supplier_concentration_ratio", 0.5),
                allocation_json=json.dumps(strategy_dict.get("allocations", [])),
                explanation=strategy_dict.get("explanation", "")
            )
            
            db.add(db_strategy)
            db.flush()
            
            # Save allocations
            for alloc in strategy_dict.get("allocations", []):
                db_alloc = SupplierAllocation(
                    strategy_id=strategy_id,
                    supplier_id=alloc.get("supplier_id", ""),
                    allocation_percentage=alloc.get("allocation_percentage", 0),
                    allocated_volume_mbd=alloc.get("allocation_mbd", 0),
                    allocated_cost=alloc.get("allocated_cost", 0),
                )
                db.add(db_alloc)
            
            saved_strategies.append(StrategyResponse.model_validate(db_strategy))
        
        db.commit()
        
        logger.info(f"Generated 3 procurement strategies for demand {india_demand} MBD")
        
        by_type = {strategy.strategy_type: strategy for strategy in saved_strategies}
        recommended = by_type["balanced"]
        return OptimizationResultsResponse(
            cheapest=by_type["cheapest"],
            balanced=recommended,
            safest=by_type["safest"],
            india_demand_mbd=india_demand,
            recommended=recommended.strategy_id,
            recommendation_reason="Balanced strategy minimizes concentration while maintaining a moderate cost-risk tradeoff.",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating strategies: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: str,
    db: Session = Depends(get_db)
):
    """Get strategy details"""
    try:
        strategy = db.query(ProcurementStrategy).filter(
            ProcurementStrategy.strategy_id == strategy_id
        ).first()
        
        if not strategy:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy_id} not found")
        
        # Get allocations
        allocations = db.query(SupplierAllocation).filter(
            SupplierAllocation.strategy_id == strategy_id
        ).all()
        
        response = StrategyResponse.model_validate(strategy)
        response.allocations = [
            {
                "supplier_id": a.supplier_id,
                "allocation_percentage": a.allocation_percentage,
                "allocated_volume_mbd": a.allocated_volume_mbd or 0,
                "allocated_cost": a.allocated_cost or 0,
            }
            for a in allocations
        ]
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving strategy {strategy_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving strategy")


@router.post("/compare", response_model=StrategyComparisonResponse)
async def compare_strategies(
    strategy_ids: list[str],
    db: Session = Depends(get_db)
):
    """Compare multiple strategies"""
    try:
        strategies = db.query(ProcurementStrategy).filter(
            ProcurementStrategy.strategy_id.in_(strategy_ids)
        ).all()
        
        if not strategies:
            raise HTTPException(status_code=404, detail="No strategies found")
        
        # Build comparison
        comparison = {
            "strategies": [],
            "best_by_cost": None,
            "best_by_safety": None,
            "best_balanced": None,
        }
        
        for strategy in strategies:
            allocations = db.query(SupplierAllocation).filter(
                SupplierAllocation.strategy_id == strategy.strategy_id
            ).all()
            
            strategy_info = {
                "strategy_id": strategy.strategy_id,
                "strategy_type": strategy.strategy_type,
                "total_cost": strategy.total_cost,
                "avg_risk_score": strategy.avg_risk_score,
                "avg_transit_time": strategy.avg_transit_time,
                "supplier_concentration_ratio": strategy.supplier_concentration_ratio,
                "total_crude_supply": strategy.total_crude_supply,
                "explanation": strategy.explanation,
                "created_at": strategy.created_at,
                "allocations": [
                    {
                        "supplier_id": a.supplier_id,
                        "allocation_percentage": a.allocation_percentage,
                        "allocated_volume_mbd": a.allocated_volume_mbd or 0,
                        "allocated_cost": a.allocated_cost or 0,
                    }
                    for a in allocations
                ]
            }
            comparison["strategies"].append(strategy_info)
            
            # Track bests
            if not comparison["best_by_cost"] or strategy.total_cost < comparison["best_by_cost"]["total_cost"]:
                comparison["best_by_cost"] = strategy_info
            if not comparison["best_by_safety"] or strategy.avg_risk_score < comparison["best_by_safety"]["avg_risk_score"]:
                comparison["best_by_safety"] = strategy_info
            if strategy.strategy_type == "balanced":
                comparison["best_balanced"] = strategy_info
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing strategies: {e}")
        raise HTTPException(status_code=400, detail="Error comparing strategies")


@router.get("")
async def list_strategies(
    strategy_type: str = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List procurement strategies"""
    try:
        query = db.query(ProcurementStrategy).order_by(ProcurementStrategy.created_at.desc())
        
        if strategy_type:
            query = query.filter(ProcurementStrategy.strategy_type == strategy_type)
        
        total = query.count()
        strategies = query.offset(offset).limit(limit).all()
        
        return {
            "strategies": [StrategyResponse.model_validate(s) for s in strategies],
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error listing strategies: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving strategies")
