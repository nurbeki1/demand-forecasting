"""
Action Service - Execute actions from chat suggestions

Supports:
- create_alert: Create demand alert for product
- generate_report: Generate structured report
- compare_products: Run product comparison
- add_to_watchlist: Add product to user's watchlist
"""

from __future__ import annotations
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    """Supported action types"""
    CREATE_ALERT = "create_alert"
    GENERATE_REPORT = "generate_report"
    COMPARE_PRODUCTS = "compare_products"
    ADD_TO_WATCHLIST = "add_to_watchlist"
    RUN_SCENARIO = "run_scenario"


class ActionStatus(str, Enum):
    """Action execution status"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class ActionResult(BaseModel):
    """Result of action execution"""
    status: ActionStatus
    action_type: str
    message: str
    data: Optional[Dict[str, Any]] = None
    created_at: datetime = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ActionService:
    """
    Service for executing chat-suggested actions.

    Actions are triggered from the chat UI and perform real operations
    like creating alerts, generating reports, etc.
    """

    def __init__(self):
        # In-memory storage for MVP (replace with DB in production)
        self._alerts: Dict[int, List[Dict]] = {}  # user_id -> alerts
        self._watchlist: Dict[int, List[Dict]] = {}  # user_id -> watchlist items

    def execute_action(
        self,
        action_type: str,
        params: Dict[str, Any],
        user_id: int,
    ) -> ActionResult:
        """
        Execute an action based on type.

        Args:
            action_type: Type of action to execute
            params: Parameters for the action
            user_id: ID of the user executing the action

        Returns:
            ActionResult with status and data
        """
        try:
            action_type_enum = ActionType(action_type)
        except ValueError:
            return ActionResult(
                status=ActionStatus.FAILED,
                action_type=action_type,
                message=f"Unknown action type: {action_type}",
                created_at=datetime.utcnow(),
            )

        handlers = {
            ActionType.CREATE_ALERT: self._create_alert,
            ActionType.GENERATE_REPORT: self._generate_report,
            ActionType.COMPARE_PRODUCTS: self._compare_products,
            ActionType.ADD_TO_WATCHLIST: self._add_to_watchlist,
            ActionType.RUN_SCENARIO: self._run_scenario,
        }

        handler = handlers.get(action_type_enum)
        if not handler:
            return ActionResult(
                status=ActionStatus.FAILED,
                action_type=action_type,
                message=f"No handler for action: {action_type}",
                created_at=datetime.utcnow(),
            )

        try:
            return handler(params, user_id)
        except Exception as e:
            logger.error(f"Action execution failed: {action_type}, error: {e}")
            return ActionResult(
                status=ActionStatus.FAILED,
                action_type=action_type,
                message=f"Action failed: {str(e)}",
                created_at=datetime.utcnow(),
            )

    def _create_alert(self, params: Dict[str, Any], user_id: int) -> ActionResult:
        """
        Create a demand alert for a product.

        Expected params:
            - product_id: str
            - alert_type: str (stockout, demand_spike, demand_drop)
            - threshold: float (optional)
        """
        product_id = params.get("product_id")
        if not product_id:
            return ActionResult(
                status=ActionStatus.FAILED,
                action_type=ActionType.CREATE_ALERT,
                message="product_id is required",
                created_at=datetime.utcnow(),
            )

        alert = {
            "id": f"alert_{user_id}_{len(self._alerts.get(user_id, []))+1}",
            "product_id": product_id,
            "alert_type": params.get("alert_type", "demand_change"),
            "threshold": params.get("threshold", 20),
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True,
        }

        if user_id not in self._alerts:
            self._alerts[user_id] = []
        self._alerts[user_id].append(alert)

        logger.info(f"Alert created: {alert['id']} for user {user_id}")

        return ActionResult(
            status=ActionStatus.SUCCESS,
            action_type=ActionType.CREATE_ALERT,
            message=f"Alert created for {product_id}",
            data=alert,
            created_at=datetime.utcnow(),
        )

    def _generate_report(self, params: Dict[str, Any], user_id: int) -> ActionResult:
        """
        Generate a structured report.

        Expected params:
            - product_id: str (optional)
            - report_type: str (forecast, inventory, performance)
            - period: str (daily, weekly, monthly)
        """
        report_type = params.get("report_type", "forecast")
        product_id = params.get("product_id")
        period = params.get("period", "weekly")

        # Generate report data (simplified for MVP)
        report = {
            "id": f"report_{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "type": report_type,
            "product_id": product_id,
            "period": period,
            "generated_at": datetime.utcnow().isoformat(),
            "sections": [
                {
                    "title": "Summary",
                    "content": f"This is a {report_type} report for {product_id or 'all products'}",
                },
                {
                    "title": "Key Metrics",
                    "metrics": {
                        "total_forecast": 1250,
                        "trend": "increasing",
                        "confidence": "high",
                    },
                },
                {
                    "title": "Recommendations",
                    "items": [
                        "Monitor inventory levels",
                        "Review pricing strategy",
                    ],
                },
            ],
        }

        logger.info(f"Report generated: {report['id']} for user {user_id}")

        return ActionResult(
            status=ActionStatus.SUCCESS,
            action_type=ActionType.GENERATE_REPORT,
            message=f"Report generated: {report_type}",
            data=report,
            created_at=datetime.utcnow(),
        )

    def _compare_products(self, params: Dict[str, Any], user_id: int) -> ActionResult:
        """
        Compare multiple products.

        Expected params:
            - product_ids: List[str]
            - metrics: List[str] (optional)
        """
        product_ids = params.get("product_ids", [])
        if len(product_ids) < 2:
            return ActionResult(
                status=ActionStatus.FAILED,
                action_type=ActionType.COMPARE_PRODUCTS,
                message="At least 2 product_ids required for comparison",
                created_at=datetime.utcnow(),
            )

        # Generate comparison data (simplified for MVP)
        comparison = {
            "products": product_ids,
            "compared_at": datetime.utcnow().isoformat(),
            "results": [
                {
                    "product_id": pid,
                    "metrics": {
                        "avg_demand": 100 + i * 20,
                        "trend": "increasing" if i % 2 == 0 else "stable",
                        "risk_level": "low" if i < 2 else "medium",
                    },
                }
                for i, pid in enumerate(product_ids)
            ],
            "winner": {
                "highest_demand": product_ids[0],
                "best_trend": product_ids[0],
            },
        }

        logger.info(f"Comparison generated for products: {product_ids}")

        return ActionResult(
            status=ActionStatus.SUCCESS,
            action_type=ActionType.COMPARE_PRODUCTS,
            message=f"Compared {len(product_ids)} products",
            data=comparison,
            created_at=datetime.utcnow(),
        )

    def _add_to_watchlist(self, params: Dict[str, Any], user_id: int) -> ActionResult:
        """
        Add product to user's watchlist.

        Expected params:
            - product_id: str
            - notes: str (optional)
        """
        product_id = params.get("product_id")
        if not product_id:
            return ActionResult(
                status=ActionStatus.FAILED,
                action_type=ActionType.ADD_TO_WATCHLIST,
                message="product_id is required",
                created_at=datetime.utcnow(),
            )

        # Check if already in watchlist
        if user_id in self._watchlist:
            existing = [w for w in self._watchlist[user_id] if w["product_id"] == product_id]
            if existing:
                return ActionResult(
                    status=ActionStatus.SUCCESS,
                    action_type=ActionType.ADD_TO_WATCHLIST,
                    message=f"{product_id} is already in your watchlist",
                    data=existing[0],
                    created_at=datetime.utcnow(),
                )

        watchlist_item = {
            "id": f"watch_{user_id}_{len(self._watchlist.get(user_id, []))+1}",
            "product_id": product_id,
            "notes": params.get("notes", ""),
            "added_at": datetime.utcnow().isoformat(),
        }

        if user_id not in self._watchlist:
            self._watchlist[user_id] = []
        self._watchlist[user_id].append(watchlist_item)

        logger.info(f"Watchlist item added: {product_id} for user {user_id}")

        return ActionResult(
            status=ActionStatus.SUCCESS,
            action_type=ActionType.ADD_TO_WATCHLIST,
            message=f"Added {product_id} to watchlist",
            data=watchlist_item,
            created_at=datetime.utcnow(),
        )

    def _run_scenario(self, params: Dict[str, Any], user_id: int) -> ActionResult:
        """
        Run what-if scenario simulation.

        Expected params:
            - product_id: str
            - changes: List[Dict] with feature, change_type, value
        """
        product_id = params.get("product_id")
        changes = params.get("changes", [])

        if not product_id:
            return ActionResult(
                status=ActionStatus.FAILED,
                action_type=ActionType.RUN_SCENARIO,
                message="product_id is required",
                created_at=datetime.utcnow(),
            )

        # Simplified scenario result for MVP
        scenario_result = {
            "product_id": product_id,
            "changes_applied": changes,
            "simulated_at": datetime.utcnow().isoformat(),
            "baseline_forecast": 1000,
            "scenario_forecast": 1000 + sum(c.get("value", 0) * 10 for c in changes),
            "impact_percent": sum(c.get("value", 0) for c in changes),
        }

        return ActionResult(
            status=ActionStatus.SUCCESS,
            action_type=ActionType.RUN_SCENARIO,
            message=f"Scenario simulated for {product_id}",
            data=scenario_result,
            created_at=datetime.utcnow(),
        )

    # Query methods

    def get_user_alerts(self, user_id: int) -> List[Dict]:
        """Get all alerts for a user"""
        return self._alerts.get(user_id, [])

    def get_user_watchlist(self, user_id: int) -> List[Dict]:
        """Get user's watchlist"""
        return self._watchlist.get(user_id, [])

    def delete_alert(self, user_id: int, alert_id: str) -> bool:
        """Delete an alert"""
        if user_id in self._alerts:
            self._alerts[user_id] = [
                a for a in self._alerts[user_id] if a["id"] != alert_id
            ]
            return True
        return False

    def remove_from_watchlist(self, user_id: int, product_id: str) -> bool:
        """Remove product from watchlist"""
        if user_id in self._watchlist:
            self._watchlist[user_id] = [
                w for w in self._watchlist[user_id] if w["product_id"] != product_id
            ]
            return True
        return False


# Global singleton instance
action_service = ActionService()
