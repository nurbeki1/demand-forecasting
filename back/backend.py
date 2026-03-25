from __future__ import annotations

import os
from typing import Optional, Dict, Any, List

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ===== DB + AUTH =====
from app.database import engine, Base
from app.auth_routes import router as auth_router
from app.deps import get_current_user

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
    CAT_COLS,
    DATE_COL,
    TARGET_COL,
)

APP_TITLE = "Demand Forecasting System"

app = FastAPI(title=APP_TITLE)

# создаём таблицы при старте
Base.metadata.create_all(bind=engine)

# подключаем auth роуты
app.include_router(auth_router)

# CORS (для Flutter/веб)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# DATASET CONFIG
# =========================================================

DEFAULT_CSV_PATH = os.environ.get(
    "DATASET_PATH",
    os.path.join(os.path.dirname(__file__), "retail_store_inventory.csv"),
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
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

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
def get_products(user=Depends(get_current_user)):
    """Получить список всех продуктов"""
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
    user=Depends(get_current_user),
):
    """Получить исторические данные по продукту"""
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
    user=Depends(get_current_user),
):
    """Получить прогноз спроса на продукт"""
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
def analytics_summary(user=Depends(get_current_user)):
    """Сводная аналитика по датасету"""
    return get_analytics_summary()


@app.get("/analytics/trends")
def analytics_trends(user=Depends(get_current_user)):
    """Тренды: растущие и падающие продукты"""
    return get_analytics_trends()


# =========================================================
# CHART (для Flutter)
# =========================================================

@app.get("/forecast/chart/{product_id}")
def forecast_chart(product_id: str, horizon: int = 7, user=Depends(get_current_user)):
    """Получить данные для графика (история + прогноз)"""
    return get_forecast_chart(product_id, horizon)


# =========================================================
# UPLOAD
# =========================================================

@app.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    """Загрузить новый CSV датасет"""
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
def get_model_cache_info(user=Depends(get_current_user)):
    """Получить информацию о кэше моделей"""
    return get_cache_info()


@app.delete("/models/cache")
def clear_model_cache(user=Depends(get_current_user)):
    """Очистить кэш моделей"""
    cleared = clear_cache()
    return {"message": "Cache cleared", "models_cleared": cleared}


@app.post("/models/retrain/{product_id}")
def retrain_model(
    product_id: str,
    store_id: Optional[str] = Query(None),
    user=Depends(get_current_user),
):
    """Принудительно переобучить модель для продукта"""
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
