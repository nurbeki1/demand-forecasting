"""
Alert Service - Business-critical alerts with prioritization

Generates actionable alerts based on:
- Stockout risk (revenue protection)
- Demand anomalies (operational planning)
- Model degradation (forecast reliability)
- Inventory optimization opportunities (cost savings)
"""

from __future__ import annotations
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np


class AlertSeverity(str, Enum):
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"          # Action within 24h
    MEDIUM = "medium"      # Action within 48h
    LOW = "low"            # Informational


class AlertCategory(str, Enum):
    STOCKOUT = "stockout"
    OVERSTOCK = "overstock"
    DEMAND_SPIKE = "demand_spike"
    DEMAND_DROP = "demand_drop"
    MODEL_DRIFT = "model_drift"
    DATA_QUALITY = "data_quality"
    OPPORTUNITY = "opportunity"


class BusinessAlert(BaseModel):
    """Business-critical alert with actionable context"""
    id: str
    severity: AlertSeverity
    category: AlertCategory
    title: str
    message: str
    impact: str  # Business impact in plain language
    action: str  # Specific action to take
    metric_value: Optional[float] = None
    metric_unit: Optional[str] = None
    product_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    # For UI
    icon: str = "alert"
    color: str = "red"


class AlertService:
    """
    Generates business-critical alerts based on forecast analysis.

    Focus areas:
    1. Revenue protection (stockouts)
    2. Cost optimization (overstock)
    3. Operational efficiency (demand changes)
    4. Forecast reliability (model health)
    """

    # Business thresholds (configurable per client)
    STOCKOUT_DAYS_CRITICAL = 2
    STOCKOUT_DAYS_HIGH = 5
    OVERSTOCK_DAYS_THRESHOLD = 60
    DEMAND_CHANGE_THRESHOLD = 0.25  # 25%
    MODEL_R2_WARNING = 0.6
    MODEL_R2_CRITICAL = 0.4

    def generate_alerts(
        self,
        product_id: str,
        predictions: List[Dict],
        historical_data: pd.DataFrame,
        model_metrics: Dict[str, float],
        inventory_level: Optional[int],
        category: Optional[str] = None,
        avg_daily_sales: Optional[float] = None,
    ) -> List[BusinessAlert]:
        """
        Generate all relevant alerts for a product forecast.

        Returns prioritized list of alerts (critical first).
        """
        alerts = []

        # Calculate key metrics
        total_predicted = sum(p.get("predicted_units_sold", 0) for p in predictions)
        horizon_days = len(predictions)
        predicted_daily_avg = total_predicted / horizon_days if horizon_days > 0 else 0

        # Historical average
        demand_col = "Demand Forecast" if "Demand Forecast" in historical_data.columns else "units_sold"
        if demand_col in historical_data.columns:
            hist_avg = historical_data[demand_col].tail(30).mean()
        else:
            hist_avg = avg_daily_sales or predicted_daily_avg

        # 1. Stockout Risk Alerts
        if inventory_level is not None and predicted_daily_avg > 0:
            coverage_days = inventory_level / predicted_daily_avg
            stockout_alert = self._check_stockout_risk(
                product_id, coverage_days, inventory_level,
                predicted_daily_avg, total_predicted, category
            )
            if stockout_alert:
                alerts.append(stockout_alert)

        # 2. Overstock Alert
        if inventory_level is not None and predicted_daily_avg > 0:
            coverage_days = inventory_level / predicted_daily_avg
            overstock_alert = self._check_overstock(
                product_id, coverage_days, inventory_level, category
            )
            if overstock_alert:
                alerts.append(overstock_alert)

        # 3. Demand Change Alerts
        if hist_avg > 0:
            change_pct = (predicted_daily_avg - hist_avg) / hist_avg
            demand_alert = self._check_demand_change(
                product_id, change_pct, hist_avg, predicted_daily_avg, category
            )
            if demand_alert:
                alerts.append(demand_alert)

        # 4. Model Health Alerts
        r2 = model_metrics.get("r2", 0)
        model_alert = self._check_model_health(product_id, r2, model_metrics)
        if model_alert:
            alerts.append(model_alert)

        # 5. Opportunity Alerts
        opportunity = self._check_opportunities(
            product_id, predictions, historical_data, category
        )
        if opportunity:
            alerts.append(opportunity)

        # Sort by severity (critical first)
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.HIGH: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.LOW: 3,
        }
        alerts.sort(key=lambda x: severity_order[x.severity])

        return alerts

    def _check_stockout_risk(
        self,
        product_id: str,
        coverage_days: float,
        inventory: int,
        daily_demand: float,
        total_demand: float,
        category: Optional[str],
    ) -> Optional[BusinessAlert]:
        """Check for stockout risk and generate alert"""

        if coverage_days <= self.STOCKOUT_DAYS_CRITICAL:
            reorder_qty = int(total_demand * 1.3 - inventory)
            return BusinessAlert(
                id=f"stockout_{product_id}_{datetime.now().strftime('%Y%m%d')}",
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.STOCKOUT,
                title=f"Критический риск дефицита: {product_id}",
                message=f"Текущий запас ({inventory} шт.) покрывает только {coverage_days:.1f} дней. "
                        f"При текущем спросе ({daily_demand:.0f} шт./день) дефицит наступит через {int(coverage_days)} дня.",
                impact=f"Потенциальная потеря выручки: {int(daily_demand * (7 - coverage_days))} единиц продаж",
                action=f"Срочно заказать минимум {reorder_qty} единиц для покрытия 7-дневного спроса",
                metric_value=coverage_days,
                metric_unit="дней запаса",
                product_id=product_id,
                expires_at=datetime.now() + timedelta(days=int(coverage_days)),
                icon="alert-triangle",
                color="#ef4444",
            )

        elif coverage_days <= self.STOCKOUT_DAYS_HIGH:
            reorder_qty = int(total_demand * 1.2 - inventory)
            return BusinessAlert(
                id=f"stockout_{product_id}_{datetime.now().strftime('%Y%m%d')}",
                severity=AlertSeverity.HIGH,
                category=AlertCategory.STOCKOUT,
                title=f"Низкий запас: {product_id}",
                message=f"Запас покрывает {coverage_days:.1f} дней при спросе {daily_demand:.0f} шт./день",
                impact="Риск упущенных продаж в ближайшую неделю",
                action=f"Запланировать заказ {reorder_qty} единиц в течение 24 часов",
                metric_value=coverage_days,
                metric_unit="дней запаса",
                product_id=product_id,
                icon="alert-circle",
                color="#f59e0b",
            )

        return None

    def _check_overstock(
        self,
        product_id: str,
        coverage_days: float,
        inventory: int,
        category: Optional[str],
    ) -> Optional[BusinessAlert]:
        """Check for overstock situation"""

        if coverage_days > self.OVERSTOCK_DAYS_THRESHOLD:
            excess_units = int(inventory - (coverage_days - 30) * (inventory / coverage_days))
            return BusinessAlert(
                id=f"overstock_{product_id}_{datetime.now().strftime('%Y%m%d')}",
                severity=AlertSeverity.MEDIUM,
                category=AlertCategory.OVERSTOCK,
                title=f"Избыточный запас: {product_id}",
                message=f"Текущий запас ({inventory} шт.) покрывает {coverage_days:.0f} дней - "
                        f"это превышает оптимальный уровень в 2 раза",
                impact=f"Замороженный капитал в {excess_units} единицах товара",
                action="Рассмотреть промо-акцию или перераспределение между складами",
                metric_value=coverage_days,
                metric_unit="дней запаса",
                product_id=product_id,
                icon="package",
                color="#3b82f6",
            )

        return None

    def _check_demand_change(
        self,
        product_id: str,
        change_pct: float,
        hist_avg: float,
        predicted_avg: float,
        category: Optional[str],
    ) -> Optional[BusinessAlert]:
        """Check for significant demand changes"""

        if change_pct > self.DEMAND_CHANGE_THRESHOLD:
            return BusinessAlert(
                id=f"demand_spike_{product_id}_{datetime.now().strftime('%Y%m%d')}",
                severity=AlertSeverity.HIGH,
                category=AlertCategory.DEMAND_SPIKE,
                title=f"Рост спроса +{change_pct*100:.0f}%: {product_id}",
                message=f"Прогнозируемый спрос ({predicted_avg:.0f} шт./день) значительно выше "
                        f"исторического ({hist_avg:.0f} шт./день)",
                impact="Возможность увеличить выручку при достаточном запасе",
                action="Проверить запасы и увеличить заказ; рассмотреть корректировку цены",
                metric_value=change_pct * 100,
                metric_unit="% роста",
                product_id=product_id,
                icon="trending-up",
                color="#22c55e",
            )

        elif change_pct < -self.DEMAND_CHANGE_THRESHOLD:
            return BusinessAlert(
                id=f"demand_drop_{product_id}_{datetime.now().strftime('%Y%m%d')}",
                severity=AlertSeverity.MEDIUM,
                category=AlertCategory.DEMAND_DROP,
                title=f"Падение спроса {change_pct*100:.0f}%: {product_id}",
                message=f"Прогнозируемый спрос ({predicted_avg:.0f} шт./день) ниже "
                        f"исторического ({hist_avg:.0f} шт./день)",
                impact="Риск затоваривания при текущем уровне закупок",
                action="Скорректировать заказы; проанализировать причины падения",
                metric_value=abs(change_pct) * 100,
                metric_unit="% падения",
                product_id=product_id,
                icon="trending-down",
                color="#f59e0b",
            )

        return None

    def _check_model_health(
        self,
        product_id: str,
        r2: float,
        metrics: Dict[str, float],
    ) -> Optional[BusinessAlert]:
        """Check model quality and reliability"""

        if r2 < self.MODEL_R2_CRITICAL:
            return BusinessAlert(
                id=f"model_drift_{product_id}_{datetime.now().strftime('%Y%m%d')}",
                severity=AlertSeverity.HIGH,
                category=AlertCategory.MODEL_DRIFT,
                title=f"Низкая точность прогноза: {product_id}",
                message=f"R² модели = {r2:.1%} - прогноз может быть ненадежным. "
                        f"MAE = {metrics.get('mae', 0):.1f} единиц",
                impact="Высокий риск ошибок в планировании запасов",
                action="Переобучить модель с актуальными данными; проверить качество входных данных",
                metric_value=r2 * 100,
                metric_unit="% R²",
                product_id=product_id,
                icon="activity",
                color="#ef4444",
            )

        elif r2 < self.MODEL_R2_WARNING:
            return BusinessAlert(
                id=f"model_warning_{product_id}_{datetime.now().strftime('%Y%m%d')}",
                severity=AlertSeverity.LOW,
                category=AlertCategory.MODEL_DRIFT,
                title=f"Точность прогноза снижена: {product_id}",
                message=f"R² модели = {r2:.1%} - рекомендуется мониторинг",
                impact="Возможны отклонения от прогноза",
                action="Запланировать переобучение модели",
                metric_value=r2 * 100,
                metric_unit="% R²",
                product_id=product_id,
                icon="info",
                color="#6b7280",
            )

        return None

    def _check_opportunities(
        self,
        product_id: str,
        predictions: List[Dict],
        historical_data: pd.DataFrame,
        category: Optional[str],
    ) -> Optional[BusinessAlert]:
        """Identify business opportunities"""

        # Check for weekend spike opportunity
        if len(predictions) >= 7:
            weekend_demand = sum(
                p.get("predicted_units_sold", 0)
                for i, p in enumerate(predictions)
                if i % 7 in [5, 6]  # Sat, Sun
            )
            weekday_demand = sum(
                p.get("predicted_units_sold", 0)
                for i, p in enumerate(predictions)
                if i % 7 not in [5, 6]
            )

            if weekend_demand > 0 and weekday_demand > 0:
                weekend_avg = weekend_demand / 2
                weekday_avg = weekday_demand / 5

                if weekend_avg > weekday_avg * 1.3:
                    return BusinessAlert(
                        id=f"opportunity_{product_id}_{datetime.now().strftime('%Y%m%d')}",
                        severity=AlertSeverity.LOW,
                        category=AlertCategory.OPPORTUNITY,
                        title=f"Возможность: пиковый спрос в выходные",
                        message=f"Спрос в выходные на {((weekend_avg/weekday_avg)-1)*100:.0f}% выше будней",
                        impact="Возможность увеличить выручку через целевой маркетинг",
                        action="Рассмотреть weekend-промо или усиленный сток к выходным",
                        metric_value=(weekend_avg/weekday_avg - 1) * 100,
                        metric_unit="% разницы",
                        product_id=product_id,
                        icon="lightbulb",
                        color="#8b5cf6",
                    )

        return None


# Singleton instance
alert_service = AlertService()
