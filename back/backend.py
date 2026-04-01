from __future__ import annotations

import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ===== DB + AUTH =====
from sqlalchemy import text, inspect
from app.database import engine, Base
from app.auth_routes import router as auth_router
from app.deps import get_current_user, get_admin_user

# ===== ROUTERS =====
from app.routers.dashboard import router as dashboard_router

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
    predict,
    clear_cache,
    get_cache_info,
    get_feature_importance,
    get_model_structure,
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

app = FastAPI(title=APP_TITLE)

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
                    ("is_verified", "ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE"),
                    ("google_id", "ALTER TABLE users ADD COLUMN google_id VARCHAR UNIQUE"),
                    ("avatar_url", "ALTER TABLE users ADD COLUMN avatar_url VARCHAR"),
                    ("full_name", "ALTER TABLE users ADD COLUMN full_name VARCHAR"),
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

# CORS (для Flutter/веб)
# CORS - allow frontend domains
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "https://demand-forecasting-orcin.vercel.app",
    "https://demand-forecasting.vercel.app",
    "https://demand-forecasting-chat.vercel.app",  # AI Chat frontend
]

# Add FRONTEND_URL from environment if set
FRONTEND_URL = os.environ.get("FRONTEND_URL")
if FRONTEND_URL and FRONTEND_URL not in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def chat(payload: ChatRequest, user=Depends(get_current_user)):
    """AI чат с RAG для анализа спроса"""
    return handle_ai_chat(payload.message, user.id)


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

    trained = get_or_train_model(sub, product_id, store_id, force_retrain=True)

    return {
        "message": "Model retrained successfully",
        "product_id": product_id,
        "store_id": store_id,
        "metrics": trained["metrics"],
        "trained_at": str(trained["trained_at"]),
    }


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
