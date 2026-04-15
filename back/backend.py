from __future__ import annotations

import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Depends, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import validate_settings_on_startup, get_settings
from app.rate_limiter import limiter, RateLimits

# ===== DB + AUTH =====
from sqlalchemy import text, inspect
from app.database import engine, Base
from app.auth_routes import router as auth_router
from app.deps import get_current_user, get_admin_user

# ===== ROUTERS =====
from app.routers.dashboard import router as dashboard_router
from app.telegram_routes import router as telegram_router
from app.report_routes import router as report_router
from app.user_routes import router as user_router
from app.settings_routes import router as settings_router

# ===== SERVICES =====
from services.ai_chat_service import (
    handle_ai_chat,
    get_chat_history,
    clear_chat_history,
    get_analytics_summary,
    get_analytics_trends,
)
from services.forecast_service import get_forecast_chart
from services.model_service import (
    get_or_train_model,
    train_model_preview,
    predict,
    clear_cache,
    get_cache_info,
    get_cache_key,
    get_feature_importance,
    get_model_structure,
    _model_cache,
    CAT_COLS,
    DATE_COL,
    TARGET_COL,
)
from services.trust_service import TrustCalculator
from services.insight_service import InsightGenerator
from services.alert_service import AlertService, BusinessAlert
from services.suggestion_service import SuggestionService, FollowUpSuggestion
from app.insight_schemas import (
    DecisionAssistantResponse,
    PredictionPoint,
    RiskLevel,
)

APP_TITLE = "Demand Forecasting System"

# Validate settings at startup (exits if invalid)
settings = validate_settings_on_startup()

app = FastAPI(title=APP_TITLE)

# Setup rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# создаём таблицы при старте + миграции
def run_migrations():
    """Run database migrations to add missing columns"""
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)

            # First create all tables that don't exist
            Base.metadata.create_all(bind=engine)

            # Check and add missing columns to users table
            if 'users' in inspector.get_table_names():
                existing_columns = [col['name'] for col in inspector.get_columns('users')]

                migrations = [
                    ("is_active", "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"),
                    ("is_admin", "ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"),
                    ("is_verified", "ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE"),
                    ("google_id", "ALTER TABLE users ADD COLUMN google_id VARCHAR UNIQUE"),
                    ("avatar_url", "ALTER TABLE users ADD COLUMN avatar_url VARCHAR"),
                    ("full_name", "ALTER TABLE users ADD COLUMN full_name VARCHAR"),
                    ("created_at", "ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                ]

                for col_name, sql in migrations:
                    if col_name not in existing_columns:
                        print(f"[Migration] Adding column: {col_name}")
                        try:
                            conn.execute(text(sql))
                            conn.commit()
                        except Exception as e:
                            print(f"[Migration] Column {col_name} might already exist: {e}")
                            conn.rollback()

            print("[Migration] Database migrations complete")
    except Exception as e:
        print(f"[Migration] Error: {e}")

run_migrations()

# подключаем auth роуты
app.include_router(auth_router)

# подключаем dashboard роуты
app.include_router(dashboard_router)

# подключаем telegram роуты
app.include_router(telegram_router)

# подключаем report роуты
app.include_router(report_router)
app.include_router(user_router)
app.include_router(settings_router)

# CORS - allow frontend domains
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://localhost:5177",
    "http://localhost:5178",
    "http://localhost:3000",
    "https://demand-forecasting-orcin.vercel.app",
    "https://demand-forecasting.vercel.app",
    "https://demand-forecasting-chat.vercel.app",  # AI Chat frontend
    "https://demand-forecasting-2y5v5n25-nurbekhs-projects.vercel.app",
]

# Add FRONTEND_URL from environment if set
FRONTEND_URL = os.environ.get("FRONTEND_URL")
if FRONTEND_URL and FRONTEND_URL not in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

# Add additional CORS origins from settings
if settings.cors_origins:
    for origin in settings.cors_origins.split(","):
        origin = origin.strip()
        if origin and origin not in ALLOWED_ORIGINS:
            ALLOWED_ORIGINS.append(origin)

# Explicit CORS methods and headers (security best practice)
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
ALLOWED_HEADERS = [
    "Content-Type",
    "Authorization",
    "Accept",
    "Origin",
    "X-Requested-With",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)

# =========================================================
# TELEGRAM BOT STARTUP
# =========================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        from services.telegram_bot_service import init_telegram_bot
        await init_telegram_bot()
    except Exception as e:
        print(f"[Telegram Bot] Failed to start: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        from services.telegram_bot_service import stop_telegram_bot
        await stop_telegram_bot()
    except Exception as e:
        print(f"[Telegram Bot] Failed to stop: {e}")


# =========================================================
# DATASET CONFIG
# =========================================================

DEFAULT_CSV_PATH = os.environ.get(
    "DATASET_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "retail_store_inventory.csv"),
)


# =========================================================
# SCHEMAS
# =========================================================

class ModelMetrics(BaseModel):
    mae: float
    rmse: float
    r2: float


class ForecastResponse(BaseModel):
    product_id: str
    store_id: Optional[str] = None
    horizon_days: int
    last_date_in_history: str
    predictions: List[Dict[str, Any]]
    model_metrics: Optional[ModelMetrics] = None


class ChatRequest(BaseModel):
    message: str
    language: str = "kk"  # Default to Kazakh, supports kk, ru, en


class ProductInfo(BaseModel):
    product_id: str
    category: Optional[str] = None
    total_records: int


class HistoryResponse(BaseModel):
    product_id: str
    records: List[Dict[str, Any]]
    total: int


# =========================================================
# DATASET HELPERS
# =========================================================

_df_cache: Optional[pd.DataFrame] = None


def load_dataset(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        raise HTTPException(
            status_code=503,
            detail=f"Dataset unavailable. Expected at: {csv_path}"
        )

    df = pd.read_csv(csv_path)

    required = {DATE_COL, "Product ID", TARGET_COL}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    df = df.dropna(subset=[DATE_COL, TARGET_COL])

    df["Product ID"] = df["Product ID"].astype(str)
    if "Store ID" in df.columns:
        df["Store ID"] = df["Store ID"].astype(str)

    return df


def get_df() -> pd.DataFrame:
    global _df_cache
    if _df_cache is None:
        _df_cache = load_dataset(DEFAULT_CSV_PATH)
    return _df_cache


def reload_dataset() -> int:
    """Перезагружает датасет. Возвращает количество записей."""
    global _df_cache
    _df_cache = load_dataset(DEFAULT_CSV_PATH)
    return len(_df_cache)


# =========================================================
# API ENDPOINTS
# =========================================================

@app.get("/")
def root():
    return {"status": "ok", "message": "Backend is running"}


# =========================================================
# PRODUCTS & HISTORY
# =========================================================

@app.get("/products", response_model=List[ProductInfo])
def get_products(user=Depends(get_admin_user)):
    """Получить список всех продуктов (Admin only)"""
    df = get_df()

    products = []
    for pid in df["Product ID"].unique():
        sub = df[df["Product ID"] == pid]
        category = sub["Category"].iloc[0] if "Category" in sub.columns else None
        products.append(
            ProductInfo(
                product_id=pid,
                category=category,
                total_records=len(sub),
            )
        )

    return sorted(products, key=lambda x: x.product_id)


@app.get("/history/{product_id}", response_model=HistoryResponse)
def get_history(
    product_id: str,
    store_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    user=Depends(get_admin_user),
):
    """Получить исторические данные по продукту (Admin only)"""
    df = get_df()

    sub = df[df["Product ID"] == product_id]
    if store_id and "Store ID" in sub.columns:
        sub = sub[sub["Store ID"] == store_id]

    if len(sub) == 0:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

    # Сортируем по дате
    sub = sub.sort_values(DATE_COL)
    total = len(sub)

    # Пагинация
    sub = sub.iloc[offset : offset + limit]

    records = []
    for _, row in sub.iterrows():
        records.append({
            "date": str(row[DATE_COL].date()),
            "units_sold": float(row[TARGET_COL]),
            "category": row.get("Category"),
            "region": row.get("Region"),
            "price": float(row.get("Price", 0)),
            "inventory_level": float(row.get("Inventory Level", 0)),
        })

    return HistoryResponse(
        product_id=product_id,
        records=records,
        total=total,
    )


# =========================================================
# FORECAST
# =========================================================

@app.get("/forecast", response_model=ForecastResponse)
def forecast(
    product_id: str = Query(...),
    store_id: Optional[str] = Query(None),
    horizon_days: int = Query(7, ge=1, le=30),
    user=Depends(get_admin_user),
):
    """Получить прогноз спроса на продукт (Admin only)"""
    df = get_df()

    sub = df[df["Product ID"] == product_id]
    if store_id and "Store ID" in sub.columns:
        sub = sub[sub["Store ID"] == store_id]

    if len(sub) < 30:
        raise HTTPException(status_code=400, detail="Not enough data for this product")

    # Используем кэшированную модель или обучаем новую
    trained = get_or_train_model(sub, product_id, store_id)

    # Получаем предсказания
    future_df, preds = predict(trained, horizon_days)

    predictions = [
        {"date": str(d.date()), "predicted_units_sold": round(float(p), 2)}
        for d, p in zip(future_df[DATE_COL], preds)
    ]

    return ForecastResponse(
        product_id=product_id,
        store_id=store_id,
        horizon_days=horizon_days,
        last_date_in_history=str(trained["last_date"].date()),
        predictions=predictions,
        model_metrics=ModelMetrics(**trained["metrics"]),
    )


# =========================================================
# FORECAST V2 - Decision Assistant with Trust Layer
# =========================================================

@app.get("/forecast/v2", response_model=DecisionAssistantResponse)
def forecast_v2(
    product_id: str = Query(...),
    store_id: Optional[str] = Query(None),
    horizon_days: int = Query(7, ge=1, le=30),
    user=Depends(get_admin_user),
):
    """
    Decision Assistant endpoint with insights and trust layer.
    Returns enhanced forecast with actionable insights and confidence metrics.
    """
    df = get_df()

    sub = df[df["Product ID"] == product_id]
    if store_id and "Store ID" in sub.columns:
        sub = sub[sub["Store ID"] == store_id]

    if len(sub) < 30:
        raise HTTPException(status_code=400, detail="Not enough data for this product")

    # Get model and predictions
    trained = get_or_train_model(sub, product_id, store_id)
    future_df, preds = predict(trained, horizon_days)

    # Build predictions list
    predictions = [
        PredictionPoint(
            date=str(d.date()),
            predicted_units_sold=round(float(p), 2)
        )
        for d, p in zip(future_df[DATE_COL], preds)
    ]

    # Get feature importance for insights
    feature_importance_data = get_feature_importance(product_id, store_id)
    feature_importances = feature_importance_data.get("features", [])

    # Get category and inventory from latest record
    latest_record = sub.sort_values(DATE_COL).iloc[-1]
    category = latest_record.get("Category") if "Category" in sub.columns else None
    inventory_level = int(latest_record.get("Inventory Level", 0)) if "Inventory Level" in sub.columns else None

    # Calculate trust layer
    trust_calculator = TrustCalculator()
    historical_demand = sub[TARGET_COL]
    trust_layer = trust_calculator.calculate_trust_layer(
        model_metrics=trained["metrics"],
        trained_at=trained["trained_at"],
        last_data_date=trained["last_date"],
        historical_demand=historical_demand,
        sample_size=len(sub),
    )

    # Generate insights
    insight_generator = InsightGenerator()
    predictions_dict = [{"date": p.date, "predicted_units_sold": p.predicted_units_sold} for p in predictions]
    insights = insight_generator.generate_insights(
        product_id=product_id,
        predictions=predictions_dict,
        historical_data=sub,
        model_metrics=trained["metrics"],
        feature_importances=feature_importances,
        inventory_level=inventory_level,
        category=category,
    )

    # Calculate totals
    total_predicted = sum(p.predicted_units_sold for p in predictions)
    avg_daily = total_predicted / len(predictions) if predictions else 0

    # Generate business alerts
    alert_service = AlertService()
    alerts = alert_service.generate_alerts(
        product_id=product_id,
        predictions=predictions_dict,
        historical_data=sub,
        model_metrics=trained["metrics"],
        inventory_level=inventory_level,
        category=category,
    )

    # Generate follow-up suggestions
    suggestion_service = SuggestionService()
    forecast_context = {
        "risk_level": insights.risk.level.value,
        "confidence": trust_layer.confidence.value,
        "trend_direction": "increasing" if avg_daily > sub[TARGET_COL].tail(7).mean() else "decreasing" if avg_daily < sub[TARGET_COL].tail(7).mean() * 0.9 else "stable",
        "category": category,
    }
    suggestions = suggestion_service.generate_suggestions(
        product_id=product_id,
        forecast_context=forecast_context,
        alerts=[a.model_dump() for a in alerts],
        user_role="admin",
    )

    # Determine alert level
    alert_level = insights.risk.level if insights.risk.level != RiskLevel.LOW else None

    # Build response with alerts and suggestions
    response_data = {
        "product_id": product_id,
        "store_id": store_id,
        "horizon_days": horizon_days,
        "last_date_in_history": str(trained["last_date"].date()),
        "predictions": predictions,
        "model_metrics": trained["metrics"],
        "insights": insights,
        "trust": trust_layer,
        "alert_level": alert_level,
        "category": category,
        "current_inventory": inventory_level,
        "total_predicted_demand": round(total_predicted, 2),
        "avg_daily_demand": round(avg_daily, 2),
        # New fields
        "alerts": [a.model_dump() for a in alerts],
        "suggestions": [s.model_dump() for s in suggestions],
        "has_critical_alert": any(a.severity.value == "critical" for a in alerts),
    }

    return response_data


# =========================================================
# ALERTS ENDPOINT
# =========================================================

@app.get("/alerts/active")
def get_active_alerts(
    product_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    user=Depends(get_admin_user),
):
    """
    Get active business alerts.
    Can filter by product_id and severity.
    """
    df = get_df()
    all_alerts = []

    # If product_id specified, get alerts for that product
    if product_id:
        product_ids = [product_id]
    else:
        # Get top products by recent activity
        product_ids = df["Product ID"].value_counts().head(10).index.tolist()

    alert_service = AlertService()

    for pid in product_ids:
        sub = df[df["Product ID"] == pid]
        if len(sub) < 30:
            continue

        try:
            trained = get_or_train_model(sub, pid, None)
            _, preds = predict(trained, 7)

            predictions = [
                {"date": str(d.date()), "predicted_units_sold": round(float(p), 2)}
                for d, p in zip(
                    pd.date_range(trained["last_date"] + pd.Timedelta(days=1), periods=7),
                    preds
                )
            ]

            latest = sub.sort_values(DATE_COL).iloc[-1]
            inventory = int(latest.get("Inventory Level", 0)) if "Inventory Level" in sub.columns else None
            category = latest.get("Category") if "Category" in sub.columns else None

            alerts = alert_service.generate_alerts(
                product_id=pid,
                predictions=predictions,
                historical_data=sub,
                model_metrics=trained["metrics"],
                inventory_level=inventory,
                category=category,
            )

            all_alerts.extend(alerts)
        except Exception:
            continue

    # Filter by severity if specified
    if severity:
        all_alerts = [a for a in all_alerts if a.severity.value == severity]

    # Sort by severity and limit
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_alerts.sort(key=lambda x: severity_order.get(x.severity.value, 4))

    return {
        "alerts": [a.model_dump() for a in all_alerts[:limit]],
        "total": len(all_alerts),
        "critical_count": sum(1 for a in all_alerts if a.severity.value == "critical"),
        "high_count": sum(1 for a in all_alerts if a.severity.value == "high"),
    }


# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
@limiter.limit(RateLimits.CHAT)
def chat(request: Request, payload: ChatRequest, user=Depends(get_current_user)):
    """AI чат с RAG для анализа спроса"""
    return handle_ai_chat(payload.message, user.id, language=payload.language)


@app.get("/chat/history")
def chat_history(
    limit: Optional[int] = Query(None, ge=1, le=100),
    user=Depends(get_current_user),
):
    """Получить историю чата"""
    return get_chat_history(user.id, limit=limit)


@app.delete("/chat/history")
def delete_chat_history(user=Depends(get_current_user)):
    """Очистить историю чата"""
    return clear_chat_history(user.id)


class ScenarioChangeRequest(BaseModel):
    """Request model for scenario change"""
    feature: str
    change_type: str = "percent"  # "absolute" | "percent" | "set"
    value: float


@app.post("/chat/scenario")
def run_chat_scenario(
    product_id: str = Query(..., description="Product ID to simulate"),
    horizon_days: int = Query(7, ge=1, le=30, description="Forecast horizon"),
    changes: List[ScenarioChangeRequest] = [],
    user=Depends(get_current_user),
):
    """
    Run what-if scenario simulation.

    Simulates changes to price, discount, promotion, etc. and shows
    impact on demand forecast.

    Example:
        POST /chat/scenario?product_id=SKU001&horizon_days=7
        Body: [{"feature": "Price", "change_type": "percent", "value": -10}]
    """
    from services.scenario_service import scenario_service, ScenarioChange

    df = get_df()
    sub = df[df["Product ID"] == product_id]

    if len(sub) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough data for product {product_id}. Need at least 30 records."
        )

    # Convert request models to ScenarioChange dataclasses
    scenario_changes = [
        ScenarioChange(
            feature=c.feature,
            change_type=c.change_type,
            value=c.value
        )
        for c in changes
    ]

    try:
        result = scenario_service.simulate_scenario(
            product_id=product_id,
            df=sub,
            horizon_days=horizon_days,
            changes=scenario_changes,
        )

        return {
            "product_id": product_id,
            "horizon_days": horizon_days,
            "baseline_predictions": result.baseline_predictions,
            "scenario_predictions": result.scenario_predictions,
            "total_baseline": result.total_baseline,
            "total_scenario": result.total_scenario,
            "change_percent": result.change_percent,
            "change_absolute": result.change_absolute,
            "impact_explanation": result.impact_explanation,
            "feature_impacts": result.feature_impacts,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/scenario/features")
def get_scenario_features(user=Depends(get_current_user)):
    """Get available features for scenario simulation"""
    from services.scenario_service import scenario_service
    return scenario_service.get_available_features()


# =========================================================
# ANALYTICS
# =========================================================

@app.get("/analytics/summary")
def analytics_summary(user=Depends(get_admin_user)):
    """Сводная аналитика по датасету (Admin only)"""
    return get_analytics_summary()


@app.get("/analytics/trends")
def analytics_trends(user=Depends(get_admin_user)):
    """Тренды: растущие и падающие продукты (Admin only)"""
    return get_analytics_trends()


# =========================================================
# CHART (для Flutter)
# =========================================================

@app.get("/forecast/chart/{product_id}")
def forecast_chart(product_id: str, horizon: int = 7, user=Depends(get_admin_user)):
    """Получить данные для графика (Admin only)"""
    return get_forecast_chart(product_id, horizon)


# =========================================================
# UPLOAD
# =========================================================

@app.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    user=Depends(get_admin_user),
):
    """Загрузить новый CSV датасет (Admin only)"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        contents = await file.read()
        # Сохраняем файл
        with open(DEFAULT_CSV_PATH, "wb") as f:
            f.write(contents)

        # Перезагружаем датасет
        records = reload_dataset()
        # Очищаем кэш моделей
        cleared = clear_cache()

        return {
            "message": "Dataset uploaded successfully",
            "records": records,
            "models_cleared": cleared,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# =========================================================
# MODEL CACHE MANAGEMENT
# =========================================================

@app.get("/models/cache")
def get_model_cache_info(user=Depends(get_admin_user)):
    """Получить информацию о кэше моделей (Admin only)"""
    return get_cache_info()


@app.delete("/models/cache")
def clear_model_cache(user=Depends(get_admin_user)):
    """Очистить кэш моделей (Admin only)"""
    cleared = clear_cache()
    return {"message": "Cache cleared", "models_cleared": cleared}


@app.post("/models/retrain/{product_id}")
def retrain_model(
    product_id: str,
    store_id: Optional[str] = Query(None),
    user=Depends(get_admin_user),
):
    """Принудительно переобучить модель для продукта (Admin only)"""
    df = get_df()

    sub = df[df["Product ID"] == product_id]
    if store_id and "Store ID" in sub.columns:
        sub = sub[sub["Store ID"] == store_id]

    if len(sub) < 30:
        raise HTTPException(status_code=400, detail="Not enough data for this product")

    # Capture old metrics before retrain
    cache_key = get_cache_key(product_id, store_id)
    old_metrics = _model_cache[cache_key]["metrics"] if cache_key in _model_cache else None
    old_trained_at = str(_model_cache[cache_key]["trained_at"]) if cache_key in _model_cache else None

    trained = get_or_train_model(sub, product_id, store_id, force_retrain=True)

    improvement = None
    if old_metrics:
        improvement = {
            "mae_change": round(trained["metrics"]["mae"] - old_metrics["mae"], 4),
            "rmse_change": round(trained["metrics"]["rmse"] - old_metrics["rmse"], 4),
            "r2_change": round(trained["metrics"]["r2"] - old_metrics["r2"], 4),
        }

    return {
        "message": "Model retrained successfully",
        "product_id": product_id,
        "store_id": store_id,
        "metrics": trained["metrics"],
        "old_metrics": old_metrics,
        "trained_at": str(trained["trained_at"]),
        "old_trained_at": old_trained_at,
        "improvement": improvement,
    }


# =========================================================
# FORECAST COMPARISON
# =========================================================

@app.get("/forecast/compare")
async def forecast_compare(
    product_id: str = Query(...),
    store_id: Optional[str] = Query(None),
    horizon_days: int = Query(7, ge=1, le=30),
    user=Depends(get_admin_user),
):
    """Compare current cached model vs freshly retrained model"""
    import asyncio

    df = get_df()
    sub = df[df["Product ID"] == product_id]
    if store_id and "Store ID" in sub.columns:
        sub = sub[sub["Store ID"] == store_id]

    if len(sub) < 30:
        raise HTTPException(status_code=400, detail="Not enough data for this product")

    cache_key = get_cache_key(product_id, store_id)

    # Get current model predictions (if cached)
    current_data = None
    if cache_key in _model_cache:
        current_trained = _model_cache[cache_key]
        _, current_preds = predict(current_trained, horizon_days)
        current_data = {
            "predictions": [round(float(p), 2) for p in current_preds],
            "metrics": current_trained["metrics"],
            "trained_at": str(current_trained["trained_at"]),
        }

    # Train new model without caching (CPU-intensive, run in thread)
    new_trained = await asyncio.to_thread(train_model_preview, sub, product_id, store_id)
    future_df, new_preds = predict(new_trained, horizon_days)

    dates = [str(d.date()) for d in future_df[DATE_COL]]

    new_data = {
        "predictions": [round(float(p), 2) for p in new_preds],
        "metrics": new_trained["metrics"],
        "trained_at": str(new_trained["trained_at"]),
    }

    # Calculate comparison
    comparison = None
    if current_data:
        comparison = {
            "mae_diff": round(new_trained["metrics"]["mae"] - current_data["metrics"]["mae"], 4),
            "rmse_diff": round(new_trained["metrics"]["rmse"] - current_data["metrics"]["rmse"], 4),
            "r2_diff": round(new_trained["metrics"]["r2"] - current_data["metrics"]["r2"], 4),
        }

    return {
        "product_id": product_id,
        "dates": dates,
        "current": current_data,
        "retrained": new_data,
        "comparison": comparison,
    }


@app.post("/forecast/compare/accept")
def forecast_compare_accept(
    product_id: str = Query(...),
    store_id: Optional[str] = Query(None),
    user=Depends(get_admin_user),
):
    """Accept retrained model — force retrain and save to cache"""
    df = get_df()
    sub = df[df["Product ID"] == product_id]
    if store_id and "Store ID" in sub.columns:
        sub = sub[sub["Store ID"] == store_id]

    if len(sub) < 30:
        raise HTTPException(status_code=400, detail="Not enough data")

    trained = get_or_train_model(sub, product_id, store_id, force_retrain=True)

    return {
        "message": "New model accepted and saved",
        "product_id": product_id,
        "metrics": trained["metrics"],
        "trained_at": str(trained["trained_at"]),
    }


# =========================================================
# SEARCH
# =========================================================

@app.get("/search")
def global_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    user=Depends(get_current_user),
):
    """Global product search using fuzzy matching"""
    from services.product_search_service import search_product
    results = search_product(q, top_k=limit)
    return {"results": results, "query": q, "total": len(results)}


# =========================================================
# MODEL VISUALIZATION
# =========================================================

@app.get("/models/structure")
def model_structure():
    """Получить структуру модели для визуализации (публичный)"""
    return get_model_structure()


@app.get("/models/features/{product_id}")
def model_features(
    product_id: str,
    store_id: Optional[str] = Query(None),
    user=Depends(get_admin_user),
):
    """Получить важность признаков для продукта (Admin only)"""
    return get_feature_importance(product_id, store_id)


@app.get("/models/visualize/{product_id}")
def model_visualize(
    product_id: str,
    store_id: Optional[str] = Query(None),
    user=Depends(get_admin_user),
):
    """Полная визуализация модели (Admin only)"""
    structure = get_model_structure()
    features = get_feature_importance(product_id, store_id)

    return {
        "structure": structure,
        "feature_importance": features.get("features", []),
        "metrics": features.get("metrics", {}),
        "product_id": product_id,
    }


# =========================================================
# KAZAKHSTAN MARKET ANALYSIS
# =========================================================

from services.kz_market_service import kz_market_service
from services.profit_calculator_service import profit_calculator
from services.web_search_service import web_search_service
from app.kz_schemas import (
    CityResponse,
    CityListResponse,
    CategoryInfo,
    CategoryListResponse,
    CurrencyRates,
    AnalyzeProductRequest,
    AnalyzeCityRequest,
    RegionalAnalysisResponse,
    CityProfitAnalysisResponse,
    CompetitorAnalysisResponse,
    CompetitorPriceResponse,
    LogisticsCostRequest,
    LogisticsCostResponse,
    MarketTrendResponse,
    WholesalePriceInfo,
)


@app.get("/kz/cities", response_model=CityListResponse)
def get_kz_cities(user=Depends(get_current_user)):
    """Get all Kazakhstan cities with economic indicators"""
    cities = kz_market_service.get_cities_dict()
    return CityListResponse(cities=cities, total=len(cities))


@app.get("/kz/cities/{city_id}", response_model=CityResponse)
def get_kz_city(city_id: str, user=Depends(get_current_user)):
    """Get specific city by ID"""
    city = kz_market_service.get_city_by_id(city_id)
    if city is None:
        raise HTTPException(status_code=404, detail=f"City {city_id} not found")
    return city.to_dict()


@app.get("/kz/categories", response_model=CategoryListResponse)
def get_kz_categories(user=Depends(get_current_user)):
    """Get all product categories with market characteristics"""
    categories = kz_market_service.get_categories()
    return CategoryListResponse(
        categories=[
            CategoryInfo(
                id=c.id,
                name_ru=c.name_ru,
                demand_multiplier=c.demand_multiplier,
                typical_margin_percent=c.typical_margin_percent,
                price_sensitivity=c.price_sensitivity,
            )
            for c in categories
        ]
    )


@app.get("/kz/currency", response_model=CurrencyRates)
def get_kz_currency(user=Depends(get_current_user)):
    """Get current currency exchange rates"""
    rates = kz_market_service.get_all_currency_rates()
    return CurrencyRates(
        usd_to_kzt=rates["USD"],
        rub_to_kzt=rates["RUB"],
        cny_to_kzt=rates["CNY"],
    )


@app.post("/kz/analyze", response_model=RegionalAnalysisResponse)
async def analyze_product_for_kz(
    request: AnalyzeProductRequest,
    user=Depends(get_current_user),
):
    """
    Analyze product profitability across all Kazakhstan cities.

    If product_cost_usd is not provided, will search for wholesale price online.
    """
    # Get product cost
    wholesale_info = None
    if request.product_cost_usd is not None:
        product_cost_usd = request.product_cost_usd
    else:
        # Search for price online
        price_info = await web_search_service.search_product_price(request.product_name)
        product_cost_usd = price_info.price_usd
        wholesale_info = WholesalePriceInfo(
            price_usd=price_info.price_usd,
            price_kzt=price_info.price_usd * kz_market_service.get_currency_rate("USD"),
            source=price_info.source,
            url=price_info.url,
            found=price_info.found,
        )

    # Run analysis
    result = profit_calculator.analyze_all_cities(
        product_cost_usd=product_cost_usd,
        category=request.category,
        markup_percent=request.markup_percent,
        product_name=request.product_name,
        shipping_cost_usd=request.shipping_cost_usd,
    )

    # Convert to response
    response_data = result.to_dict()
    response_data["wholesale_info"] = wholesale_info
    return response_data


@app.get("/kz/analyze/{city_id}", response_model=CityProfitAnalysisResponse)
def analyze_city_profit(
    city_id: str,
    product_cost_usd: float = Query(..., ge=0),
    category: str = Query("electronics"),
    markup_percent: float = Query(25.0, ge=0, le=200),
    shipping_cost_usd: float = Query(0.0, ge=0),
    user=Depends(get_current_user),
):
    """Analyze profitability for a specific city"""
    analysis = profit_calculator.calculate_city_profit(
        product_cost_usd=product_cost_usd,
        category=category,
        city_id=city_id,
        markup_percent=markup_percent,
        shipping_cost_usd=shipping_cost_usd,
    )

    if analysis is None:
        raise HTTPException(status_code=404, detail=f"City {city_id} not found")

    return analysis.to_dict()


@app.get("/kz/competitors")
async def get_competitor_prices(
    product_name: str = Query(..., min_length=1),
    market: str = Query("kaspi"),
    user=Depends(get_current_user),
):
    """Get competitor prices on Kazakhstan marketplaces"""
    competitors = await web_search_service.get_competitor_prices(product_name, market)

    prices = [c.price_kzt for c in competitors if c.price_kzt > 0]

    return CompetitorAnalysisResponse(
        product_name=product_name,
        competitors=[
            CompetitorPriceResponse(
                product_name=c.product_name,
                price_kzt=c.price_kzt,
                seller=c.seller,
                platform=c.platform,
                url=c.url,
                rating=c.rating,
                reviews_count=c.reviews_count,
            )
            for c in competitors
        ],
        avg_price_kzt=sum(prices) / len(prices) if prices else 0,
        min_price_kzt=min(prices) if prices else 0,
        max_price_kzt=max(prices) if prices else 0,
    )


@app.get("/kz/trends/{category}", response_model=MarketTrendResponse)
async def get_market_trends(
    category: str,
    user=Depends(get_current_user),
):
    """Get market trends for a category"""
    trend = await web_search_service.get_market_trends(category)
    return MarketTrendResponse(
        category=trend.category,
        trend_direction=trend.trend_direction,
        trend_description=trend.trend_description,
        key_products=trend.key_products,
        source=trend.source,
    )


@app.post("/kz/logistics", response_model=LogisticsCostResponse)
def calculate_logistics_cost(
    request: LogisticsCostRequest,
    user=Depends(get_current_user),
):
    """Calculate logistics cost between cities"""
    base_cost = kz_market_service.get_logistics_cost(
        from_city=request.from_city,
        to_city=request.to_city,
    )

    total_cost = kz_market_service.get_logistics_cost(
        from_city=request.from_city,
        to_city=request.to_city,
        weight_kg=request.weight_kg,
        is_express=request.is_express,
        is_bulky=request.is_bulky,
    )

    weight_cost = total_cost - base_cost
    if request.is_express:
        weight_cost = 0  # Already included in multiplier

    return LogisticsCostResponse(
        from_city=request.from_city,
        to_city=request.to_city,
        base_cost_kzt=base_cost,
        weight_cost_kzt=weight_cost,
        total_cost_kzt=total_cost,
        is_express=request.is_express,
        is_bulky=request.is_bulky,
    )
