from __future__ import annotations

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException, Query, Depends, File, UploadFile, Request
from fastapi.responses import StreamingResponse
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
from app.deps import get_current_user, get_admin_user, get_db
from app.subscription_utils import enforce_chat_model_type
from app.models import User
from app.schemas import MockSubscribeRequest, UserResponse
from app.demo_billing import apply_mock_subscription

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
from services.model_service import (
    clear_cache,
    get_cache_info,
    get_model_structure,
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
                    ("subscription_plan", "ALTER TABLE users ADD COLUMN subscription_plan VARCHAR(32) DEFAULT 'free'"),
                    ("created_at", "ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                    ("is_onboarding_completed", "ALTER TABLE users ADD COLUMN is_onboarding_completed BOOLEAN DEFAULT FALSE"),
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


@app.post("/subscription/mock-checkout", response_model=UserResponse, tags=["subscription"])
def subscription_mock_checkout(
    data: MockSubscribeRequest,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Demo checkout (same as POST /auth/mock-subscribe). Registered here so it ships with the main app."""
    return apply_mock_subscription(db, user, data)


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
# SCHEMAS
# =========================================================

class ChatRequest(BaseModel):
    message: str
    language: str = "kk"  # Default to Kazakh, supports kk, ru, en
    model_type: str = "random_forest"  # ML model: random_forest, lightgbm, xgboost


# =========================================================
# API ENDPOINTS
# =========================================================

@app.get("/")
def root():
    return {"status": "ok", "message": "Backend is running"}


# =========================================================
# PRODUCTS & HISTORY
# =========================================================

@app.get("/products")
def get_products(
    q: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    user=Depends(get_admin_user),
):
    """Return top Amazon products (Admin only)"""
    import pandas as pd
    from pathlib import Path

    csv_path = Path(__file__).parent / "data" / "amazon" / "Amazon-Products-sample.csv"
    if not csv_path.exists():
        return []

    df = pd.read_csv(csv_path, nrows=100_000)
    df.columns = df.columns.str.strip()
    df["no_of_ratings"] = (
        df["no_of_ratings"].astype(str).str.replace(",", "").str.strip()
    )
    df["no_of_ratings"] = pd.to_numeric(df["no_of_ratings"], errors="coerce").fillna(0)
    df["ratings"] = pd.to_numeric(df["ratings"], errors="coerce")
    df = df.dropna(subset=["name", "ratings"])
    df = df[df["ratings"] >= 3.5]

    if q:
        mask = df["name"].str.contains(q, case=False, na=False) | df["main_category"].str.contains(q, case=False, na=False)
        df = df[mask]

    # Pick top products per category for variety
    per_cat = max(1, limit // df["main_category"].nunique()) if df["main_category"].nunique() > 0 else limit
    sampled = (
        df.groupby("main_category", group_keys=False)
        .apply(lambda g: g.nlargest(per_cat, "no_of_ratings"))
        .reset_index(drop=True)
    )
    sampled = sampled.nlargest(limit, "no_of_ratings")

    results = []
    for i, (_, row) in enumerate(sampled.iterrows()):
        cat = str(row["main_category"]).replace(" ", "_").replace("&", "and")[:12].upper()
        results.append({
            "product_id": f"{cat}_{i+1:03d}",
            "name": str(row["name"])[:80],
            "category": str(row["main_category"]).title(),
            "sub_category": str(row.get("sub_category", "")).title(),
            "rating": float(row["ratings"]),
            "review_count": int(row["no_of_ratings"]),
            "total_records": int(row["no_of_ratings"]),
        })

    return results


@app.get("/history/{product_id}")
def get_history(product_id: str, user=Depends(get_admin_user)):
    """Historical sales data endpoint (deprecated — use /chat for analysis)"""
    raise HTTPException(
        status_code=410,
        detail="Historical data endpoint removed. Use /chat for product analysis.",
    )


# =========================================================
# FORECAST
# =========================================================

@app.get("/forecast")
def forecast(product_id: str = Query(...), user=Depends(get_admin_user)):
    """Forecast endpoint (deprecated — use /chat for AI-powered demand analysis)"""
    raise HTTPException(
        status_code=410,
        detail="Forecast endpoint removed. Use /chat for AI-powered demand analysis with web search.",
    )


@app.get("/forecast/v2")
def forecast_v2(product_id: str = Query(...), user=Depends(get_admin_user)):
    """Forecast v2 endpoint (deprecated — use /chat)"""
    raise HTTPException(
        status_code=410,
        detail="Forecast endpoint removed. Use /chat for AI-powered demand analysis.",
    )


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
    """Get active business alerts"""
    return {"alerts": [], "total": 0, "critical_count": 0, "high_count": 0}


# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
@limiter.limit(RateLimits.CHAT)
def chat(request: Request, payload: ChatRequest, user=Depends(get_current_user)):
    """AI чат с RAG для анализа спроса"""
    try:
        mt = enforce_chat_model_type(user, payload.model_type)
        return handle_ai_chat(payload.message, user.id, language=payload.language, model_type=mt, subscription_plan=getattr(user, "subscription_plan", "free") or "free")
    except Exception as e:
        import logging, traceback
        tb = traceback.format_exc()
        logging.error(f"[CHAT ERROR] user={user.id} msg={payload.message[:50]!r}: {e}\n{tb}")
        raise HTTPException(status_code=500, detail=f"Chat error: {type(e).__name__}: {str(e)}")


@app.post("/chat/stream")
@limiter.limit(RateLimits.CHAT)
async def chat_stream(request: Request, payload: ChatRequest, user=Depends(get_current_user)):
    """Streaming AI chat via Server-Sent Events"""
    from services.ai_chat_service import handle_ai_chat_stream
    mt = enforce_chat_model_type(user, payload.model_type)
    return StreamingResponse(
        handle_ai_chat_stream(payload.message, user.id, language=payload.language, model_type=mt, subscription_plan=getattr(user, "subscription_plan", "free") or "free"),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


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


@app.post("/chat/scenario")
def run_chat_scenario(user=Depends(get_current_user)):
    """Scenario simulation (deprecated — use /chat for analysis)"""
    raise HTTPException(
        status_code=410,
        detail="Scenario simulation removed. Use /chat for AI-powered analysis.",
    )


@app.get("/chat/scenario/features")
def get_scenario_features(user=Depends(get_current_user)):
    """Get available features for scenario simulation"""
    return {"features": []}


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
    """Forecast chart (deprecated)"""
    raise HTTPException(status_code=410, detail="Forecast chart removed. Use /chat for analysis.")


# =========================================================
# UPLOAD
# =========================================================

@app.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    user=Depends(get_admin_user),
):
    """Upload CSV dataset (Admin only)"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        contents = await file.read()
        upload_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploaded_dataset.csv")
        with open(upload_path, "wb") as f:
            f.write(contents)

        cleared = clear_cache()
        return {
            "message": "Dataset uploaded successfully",
            "filename": file.filename,
            "size_bytes": len(contents),
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
def retrain_model(product_id: str, user=Depends(get_admin_user)):
    """Retrain model (deprecated — models now trained from Amazon dataset automatically)"""
    raise HTTPException(status_code=410, detail="Manual retrain removed. Models train automatically from Amazon data.")


# =========================================================
# FORECAST COMPARISON
# =========================================================

@app.get("/forecast/compare")
async def forecast_compare(product_id: str = Query(...), user=Depends(get_admin_user)):
    """Forecast compare (deprecated)"""
    raise HTTPException(status_code=410, detail="Forecast compare removed. Use /chat for analysis.")


@app.post("/forecast/compare/accept")
def forecast_compare_accept(product_id: str = Query(...), user=Depends(get_admin_user)):
    """Accept retrained model (deprecated)"""
    raise HTTPException(status_code=410, detail="Forecast compare removed. Use /chat for analysis.")


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
def model_features(product_id: str, user=Depends(get_admin_user)):
    """Model feature importance (Amazon-based model)"""
    structure = get_model_structure()
    return {"product_id": product_id, "features": [], "structure": structure}


@app.get("/models/visualize/{product_id}")
def model_visualize(product_id: str, user=Depends(get_admin_user)):
    """Model visualization (Amazon-based model)"""
    structure = get_model_structure()
    return {"structure": structure, "feature_importance": [], "metrics": {}, "product_id": product_id}


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
