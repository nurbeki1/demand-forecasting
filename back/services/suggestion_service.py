"""
Suggestion Service - Contextual follow-up suggestions

Generates intelligent next-step suggestions based on:
- Current forecast context
- User role and permissions
- Business priorities
- Data availability
"""

from __future__ import annotations
from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel


class SuggestionCategory(str, Enum):
    ANALYSIS = "analysis"
    ACTION = "action"
    EXPLORATION = "exploration"
    COMPARISON = "comparison"


class SuggestionPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FollowUpSuggestion(BaseModel):
    """Contextual follow-up suggestion for chat interface"""
    id: str
    text: str
    category: SuggestionCategory
    priority: SuggestionPriority
    icon: str
    # For chat integration
    prompt: str  # Full prompt to send to AI
    requires_data: bool = False
    data_params: Optional[Dict] = None


class SuggestionService:
    """
    Generates contextual follow-up suggestions.

    Key principles:
    1. Context-aware - based on current forecast state
    2. Action-oriented - each suggestion leads to a decision
    3. Prioritized - most valuable first
    4. Role-aware - admin vs regular user
    """

    def generate_suggestions(
        self,
        product_id: str,
        forecast_context: Dict,
        alerts: List[Dict],
        user_role: str = "admin",
    ) -> List[FollowUpSuggestion]:
        """
        Generate follow-up suggestions based on forecast context.

        Args:
            product_id: Current product
            forecast_context: Dict with predictions, metrics, insights
            alerts: Active alerts for this product
            user_role: User role for permission filtering

        Returns:
            Prioritized list of suggestions
        """
        suggestions = []

        # Extract context
        risk_level = forecast_context.get("risk_level", "low")
        confidence = forecast_context.get("confidence", "medium")
        trend = forecast_context.get("trend_direction", "stable")
        category = forecast_context.get("category")
        has_stockout_risk = any(a.get("category") == "stockout" for a in alerts)
        has_demand_change = any(
            a.get("category") in ["demand_spike", "demand_drop"] for a in alerts
        )

        # 1. High-priority suggestions based on alerts
        if has_stockout_risk:
            suggestions.append(FollowUpSuggestion(
                id="reorder_calc",
                text="Рассчитать оптимальный заказ",
                category=SuggestionCategory.ACTION,
                priority=SuggestionPriority.HIGH,
                icon="calculator",
                prompt=f"Рассчитай оптимальный объем заказа для {product_id} с учетом текущего прогноза, "
                       f"времени доставки 3 дня и целевого запаса на 14 дней",
                requires_data=True,
                data_params={"product_id": product_id, "action": "reorder_calculation"},
            ))

        if has_demand_change:
            suggestions.append(FollowUpSuggestion(
                id="demand_drivers",
                text="Почему изменился спрос?",
                category=SuggestionCategory.ANALYSIS,
                priority=SuggestionPriority.HIGH,
                icon="search",
                prompt=f"Проанализируй причины изменения спроса на {product_id}. "
                       f"Какие факторы (сезонность, цены, промо, конкуренты) могли повлиять?",
                requires_data=True,
                data_params={"product_id": product_id, "action": "demand_analysis"},
            ))

        # 2. Risk-based suggestions
        if risk_level == "high":
            suggestions.append(FollowUpSuggestion(
                id="risk_mitigation",
                text="Как снизить риски?",
                category=SuggestionCategory.ACTION,
                priority=SuggestionPriority.HIGH,
                icon="shield",
                prompt=f"Какие действия помогут снизить риски для {product_id}? "
                       f"Дай конкретные рекомендации с приоритетами",
            ))

        # 3. Confidence-based suggestions
        if confidence == "low":
            suggestions.append(FollowUpSuggestion(
                id="improve_accuracy",
                text="Как улучшить точность прогноза?",
                category=SuggestionCategory.ANALYSIS,
                priority=SuggestionPriority.MEDIUM,
                icon="target",
                prompt=f"Точность прогноза для {product_id} низкая. "
                       f"Какие данные нужно добавить или что изменить для улучшения?",
            ))

        # 4. Trend-based suggestions
        if trend == "increasing":
            suggestions.append(FollowUpSuggestion(
                id="growth_opportunity",
                text="Как максимизировать рост?",
                category=SuggestionCategory.ACTION,
                priority=SuggestionPriority.MEDIUM,
                icon="trending-up",
                prompt=f"Спрос на {product_id} растет. Какие действия помогут максимизировать выручку? "
                       f"Рассмотри ценообразование, запасы, маркетинг",
            ))
        elif trend == "decreasing":
            suggestions.append(FollowUpSuggestion(
                id="decline_response",
                text="Как реагировать на падение?",
                category=SuggestionCategory.ACTION,
                priority=SuggestionPriority.MEDIUM,
                icon="trending-down",
                prompt=f"Спрос на {product_id} падает. Какие действия предпринять? "
                       f"Снизить закупки? Запустить промо? Проверить конкурентов?",
            ))

        # 5. Comparison suggestions
        if category:
            suggestions.append(FollowUpSuggestion(
                id="category_comparison",
                text=f"Сравнить с категорией {category}",
                category=SuggestionCategory.COMPARISON,
                priority=SuggestionPriority.LOW,
                icon="bar-chart",
                prompt=f"Сравни показатели {product_id} с другими товарами категории {category}. "
                       f"Как этот товар выглядит на фоне конкурентов внутри категории?",
                requires_data=True,
                data_params={"category": category, "action": "category_comparison"},
            ))

        suggestions.append(FollowUpSuggestion(
            id="similar_products",
            text="Показать похожие товары",
            category=SuggestionCategory.EXPLORATION,
            priority=SuggestionPriority.LOW,
            icon="grid",
            prompt=f"Какие товары имеют похожий паттерн спроса с {product_id}? "
                   f"Можно ли их продавать вместе или заменять друг друга?",
            requires_data=True,
            data_params={"product_id": product_id, "action": "similar_products"},
        ))

        # 6. Exploration suggestions
        suggestions.append(FollowUpSuggestion(
            id="seasonality",
            text="Анализ сезонности",
            category=SuggestionCategory.ANALYSIS,
            priority=SuggestionPriority.LOW,
            icon="calendar",
            prompt=f"Проанализируй сезонные паттерны для {product_id}. "
                   f"Когда пики и спады? Как это использовать для планирования?",
            requires_data=True,
            data_params={"product_id": product_id, "action": "seasonality_analysis"},
        ))

        suggestions.append(FollowUpSuggestion(
            id="price_elasticity",
            text="Влияние цены на спрос",
            category=SuggestionCategory.ANALYSIS,
            priority=SuggestionPriority.LOW,
            icon="dollar-sign",
            prompt=f"Как цена влияет на спрос {product_id}? "
                   f"Есть ли возможность оптимизировать ценообразование?",
            requires_data=True,
            data_params={"product_id": product_id, "action": "price_analysis"},
        ))

        # 7. Admin-only suggestions
        if user_role == "admin":
            suggestions.append(FollowUpSuggestion(
                id="retrain_model",
                text="Переобучить модель",
                category=SuggestionCategory.ACTION,
                priority=SuggestionPriority.LOW,
                icon="refresh-cw",
                prompt=f"Запусти переобучение модели для {product_id} с последними данными",
                requires_data=True,
                data_params={"product_id": product_id, "action": "retrain"},
            ))

        # Sort by priority
        priority_order = {
            SuggestionPriority.HIGH: 0,
            SuggestionPriority.MEDIUM: 1,
            SuggestionPriority.LOW: 2,
        }
        suggestions.sort(key=lambda x: priority_order[x.priority])

        # Return top 5
        return suggestions[:5]

    def get_quick_actions(
        self,
        product_id: str,
        has_critical_alert: bool = False,
    ) -> List[FollowUpSuggestion]:
        """
        Get quick action buttons for UI.
        These are always-available shortcuts.
        """
        actions = []

        if has_critical_alert:
            actions.append(FollowUpSuggestion(
                id="quick_reorder",
                text="Быстрый заказ",
                category=SuggestionCategory.ACTION,
                priority=SuggestionPriority.HIGH,
                icon="shopping-cart",
                prompt=f"Создай заказ для {product_id} с оптимальным количеством",
            ))

        actions.append(FollowUpSuggestion(
            id="quick_summary",
            text="Краткий отчет",
            category=SuggestionCategory.ANALYSIS,
            priority=SuggestionPriority.MEDIUM,
            icon="file-text",
            prompt=f"Дай краткую сводку по {product_id}: текущий статус, прогноз, риски, рекомендации",
        ))

        actions.append(FollowUpSuggestion(
            id="quick_compare",
            text="Сравнить периоды",
            category=SuggestionCategory.COMPARISON,
            priority=SuggestionPriority.LOW,
            icon="git-compare",
            prompt=f"Сравни показатели {product_id} за последние 7 дней с предыдущей неделей",
        ))

        return actions


# Singleton instance
suggestion_service = SuggestionService()
