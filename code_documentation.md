# Дипломдық жұмыс — Маңызды код үзінділері
## Demand Forecasting System (ProdBot AI)

> **Стек:** Python, FastAPI, scikit-learn, LightGBM, XGBoost, SQLAlchemy, Claude AI (LLM)

---

## 1. Инициализация приложения и подключение модулей

**Файл:** `back/backend.py`
**Описание:** Точка входа всего бэкенда. FastAPI приложение подключает роутеры, CORS-политику, rate limiter и инициализирует базу данных с автоматическими миграциями при старте.

```python
app = FastAPI(title="Demand Forecasting System")

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Подключение роутеров
app.include_router(auth_router)        # /auth/*
app.include_router(dashboard_router)   # /dashboard/*
app.include_router(report_router)      # /reports/*
app.include_router(telegram_router)    # /telegram/*

# CORS настройка
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

@app.on_event("startup")
async def startup_event():
    """Инициализация Telegram бота при старте сервера"""
    from services.telegram_bot_service import init_telegram_bot
    await init_telegram_bot()
```

---

## 2. Автоматические миграции базы данных

**Файл:** `back/backend.py`
**Описание:** При каждом запуске сервер проверяет структуру базы данных и автоматически добавляет недостающие колонки. Это позволяет обновлять схему без ручных SQL-скриптов.

```python
def run_migrations():
    """Автоматическое добавление новых колонок в таблицу users"""
    with engine.connect() as conn:
        Base.metadata.create_all(bind=engine)

        existing_columns = [
            col['name'] for col in inspector.get_columns('users')
        ]

        migrations = [
            ("is_active",   "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"),
            ("is_admin",    "ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"),
            ("is_verified", "ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE"),
            ("google_id",   "ALTER TABLE users ADD COLUMN google_id VARCHAR UNIQUE"),
            ("avatar_url",  "ALTER TABLE users ADD COLUMN avatar_url VARCHAR"),
            ("full_name",   "ALTER TABLE users ADD COLUMN full_name VARCHAR"),
            ("created_at",  "ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ]

        for col_name, sql in migrations:
            if col_name not in existing_columns:
                conn.execute(text(sql))
                conn.commit()

run_migrations()
```

---

## 3. Feature Engineering — Временные и лаговые признаки

**Файл:** `back/services/model_service.py`
**Описание:** Критический этап подготовки данных. Из исторического спроса создаются лаговые признаки (спрос за 1, 7, 14, 30 дней назад), скользящие средние и циклические признаки для месяца и дня недели. Эти признаки позволяют модели улавливать сезонность и краткосрочные тренды.

```python
def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """Лаговые признаки — критично для временных рядов"""
    df = df.copy().sort_values("Date")

    # Исторический спрос со сдвигом
    df["demand_lag_1"]  = df["Demand Forecast"].shift(1)   # вчера
    df["demand_lag_7"]  = df["Demand Forecast"].shift(7)   # неделю назад
    df["demand_lag_14"] = df["Demand Forecast"].shift(14)  # 2 недели назад
    df["demand_lag_30"] = df["Demand Forecast"].shift(30)  # месяц назад

    # Скользящие статистики
    df["demand_rolling_mean_7"]  = df["Demand Forecast"].rolling(7,  min_periods=1).mean()
    df["demand_rolling_std_7"]   = df["Demand Forecast"].rolling(7,  min_periods=1).std().fillna(0)
    df["demand_rolling_mean_30"] = df["Demand Forecast"].rolling(30, min_periods=1).mean()

    # Тренд (изменение за день)
    df["demand_diff"] = df["Demand Forecast"].diff().fillna(0)

    # Заполняем NaN средними значениями
    for col in ["demand_lag_1", "demand_lag_7", "demand_lag_14", "demand_lag_30"]:
        df[col] = df[col].fillna(df["Demand Forecast"].mean())

    return df


def add_date_features(df: pd.DataFrame) -> pd.DataFrame:
    """Циклические признаки даты для ML модели"""
    df = df.copy()
    df["day"]         = df["Date"].dt.day
    df["month"]       = df["Date"].dt.month
    df["day_of_week"] = df["Date"].dt.dayofweek

    # Синусно-косинусное кодирование (лучше для ML чем числа 1–12)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["dow_sin"]   = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"]   = np.cos(2 * np.pi * df["day_of_week"] / 7)

    return df
```

---

## 4. Обучение ML модели с хронологическим split

**Файл:** `back/services/model_service.py`
**Описание:** Функция обучения поддерживает три алгоритма: Random Forest, LightGBM, XGBoost. Ключевая особенность — хронологический split данных (не случайный), что критично для задач прогнозирования временных рядов. Pipeline объединяет OneHotEncoder для категориальных признаков и сам регрессор.

```python
def build_model(model_type: str = "random_forest"):
    """Создаёт ML модель по типу"""
    if model_type == "lightgbm":
        from lightgbm import LGBMRegressor
        return LGBMRegressor(n_estimators=500, learning_rate=0.05, num_leaves=63, n_jobs=-1)
    elif model_type == "xgboost":
        from xgboost import XGBRegressor
        return XGBRegressor(n_estimators=500, learning_rate=0.05, n_jobs=-1)
    else:
        return RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)


def train_model(df: pd.DataFrame, test_size: float = 0.2,
                model_type: str = "random_forest") -> Dict[str, Any]:
    """Обучает модель с временным split и возвращает pipeline + метрики"""

    df = df.sort_values("Date").reset_index(drop=True)
    df = add_lag_features(df)
    df = add_date_features(df)

    # Признаки: категориальные + числовые + лаговые + циклические
    CAT_COLS = ["Category", "Region", "Weather Condition", "Seasonality", "Store ID"]
    NUM_COLS = ["Inventory Level", "Units Ordered", "Price", "Discount",
                "Competitor Pricing", "Holiday/Promotion"]
    num_cols_ext = NUM_COLS + ["day", "month", "day_of_week"] + LAG_COLS + CYCLIC_COLS

    y = df["Demand Forecast"]
    X = df[CAT_COLS + num_cols_ext]

    # Хронологический split (не случайный!) — важно для временных рядов
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # Pipeline: предобработка + модель
    preprocessor = ColumnTransformer(transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
        ("num", "passthrough", num_cols_ext),
    ])

    pipeline = Pipeline(steps=[
        ("pre", preprocessor),
        ("model", build_model(model_type)),
    ])

    pipeline.fit(X_train, y_train)

    # Метрики на тестовой выборке
    y_pred = pipeline.predict(X_test)
    metrics = {
        "mae":  round(float(mean_absolute_error(y_test, y_pred)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4),
        "r2":   round(float(r2_score(y_test, y_pred)), 4),
    }

    return {
        "pipeline": pipeline,
        "metrics":  metrics,
        "last_row": df.sort_values("Date").iloc[-1].to_dict(),
        "last_date": df.sort_values("Date").iloc[-1]["Date"],
        "model_type": model_type,
        "trained_at": datetime.now(),
    }
```

---

## 5. Двухуровневый кэш моделей (память + диск)

**Файл:** `back/services/model_service.py`
**Описание:** Система кэширования предотвращает повторное обучение. Модели сначала ищутся в оперативной памяти (быстро), затем на диске (joblib). Если нигде нет — обучается новая и сохраняется в оба хранилища.

```python
_model_cache: Dict[str, Dict[str, Any]] = {}  # Кэш в оперативной памяти

def get_or_train_model(df, product_id, store_id=None,
                       force_retrain=False, model_type="random_forest"):
    """
    Стратегия: память → диск → обучение новой модели

    Ключ кэша: "{product_id}_{store_id}_{model_type}"
    """
    cache_key = f"{product_id}_{store_id or 'all'}_{model_type}"

    # 1. Поиск в оперативной памяти (мгновенно)
    if not force_retrain and cache_key in _model_cache:
        return _update_last_row(_model_cache[cache_key], df)

    # 2. Поиск на диске (быстро, сохраняется между перезапусками)
    if not force_retrain:
        disk = load_model_from_disk(cache_key)
        if disk:
            disk = _update_last_row(disk, df)
            _model_cache[cache_key] = disk
            return disk

    # 3. Обучаем новую модель и сохраняем
    trained = train_model(df, model_type=model_type)
    _model_cache[cache_key] = trained
    save_model_to_disk(cache_key, trained)  # joblib.dump(pipeline, "*.pkl")

    return trained
```

---

## 6. Прогноз на будущие даты

**Файл:** `back/services/model_service.py`
**Описание:** Для прогноза создаются строки будущих дат с теми же признаками что при обучении. Лаговые признаки берутся из последней известной записи. Циклические признаки пересчитываются для каждой будущей даты.

```python
def make_future_rows(last_row, last_date, horizon: int) -> pd.DataFrame:
    """Создаёт строки будущих дат для предсказания"""
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon)

    rows = []
    for d in future_dates:
        r = dict(last_row)
        r["Date"] = d

        # Временные признаки для новой даты
        r["day"]         = d.day
        r["month"]       = d.month
        r["day_of_week"] = d.dayofweek

        # Циклические признаки
        r["month_sin"] = np.sin(2 * np.pi * d.month / 12)
        r["month_cos"] = np.cos(2 * np.pi * d.month / 12)
        r["dow_sin"]   = np.sin(2 * np.pi * d.dayofweek / 7)
        r["dow_cos"]   = np.cos(2 * np.pi * d.dayofweek / 7)

        r.pop("Demand Forecast", None)  # Убираем целевую переменную
        rows.append(r)

    return pd.DataFrame(rows)


def predict(trained, horizon_days: int):
    """Генерирует предсказания на horizon_days дней вперёд"""
    future_df = make_future_rows(
        trained["last_row"], trained["last_date"], horizon_days
    )
    X_future = future_df[CAT_COLS + trained["num_cols_ext"]]
    predictions = trained["pipeline"].predict(X_future)

    return future_df, predictions
```

---

## 7. Forecast API endpoint (v1 и v2)

**Файл:** `back/backend.py`
**Описание:** Два варианта API прогноза. V1 — базовый, возвращает только предсказания. V2 (Decision Assistant) — расширенный: добавляет слой доверия (trust layer), бизнес-инсайты, алерты и предложения следующих действий.

```python
# ===== V1: Базовый прогноз =====
@app.get("/forecast", response_model=ForecastResponse)
def forecast(
    product_id: str  = Query(...),
    store_id: Optional[str] = Query(None),
    horizon_days: int = Query(7, ge=1, le=30),
    model_type: str  = Query("random_forest",
                             enum=["random_forest", "lightgbm", "xgboost"]),
    user = Depends(get_admin_user),  # Только для администраторов
):
    df = get_df()
    sub = df[df["Product ID"] == product_id]

    trained = get_or_train_model(sub, product_id, store_id, model_type=model_type)
    future_df, preds = predict(trained, horizon_days)

    predictions = [
        {"date": str(d.date()), "predicted_units_sold": round(float(p), 2)}
        for d, p in zip(future_df["Date"], preds)
    ]
    return ForecastResponse(
        product_id=product_id,
        predictions=predictions,
        model_metrics=ModelMetrics(**trained["metrics"]),
    )


# ===== V2: Decision Assistant с Trust Layer =====
@app.get("/forecast/v2", response_model=DecisionAssistantResponse)
def forecast_v2(
    product_id: str  = Query(...),
    horizon_days: int = Query(7, ge=1, le=30),
    model_type: str  = Query("random_forest"),
    user = Depends(get_admin_user),
):
    """Расширенный прогноз: инсайты + доверие + алерты + предложения"""
    trained = get_or_train_model(sub, product_id, store_id, model_type=model_type)
    future_df, preds = predict(trained, horizon_days)

    # Trust Layer — оценка надёжности прогноза
    trust_layer = TrustCalculator().calculate_trust_layer(
        model_metrics=trained["metrics"],
        trained_at=trained["trained_at"],
        historical_demand=sub["Demand Forecast"],
        sample_size=len(sub),
    )

    # Генерация бизнес-инсайтов
    insights = InsightGenerator().generate_insights(
        product_id=product_id,
        predictions=predictions_dict,
        historical_data=sub,
        model_metrics=trained["metrics"],
        inventory_level=inventory_level,
    )

    # Бизнес-алерты (критические предупреждения)
    alerts = AlertService().generate_alerts(
        product_id=product_id,
        predictions=predictions_dict,
        historical_data=sub,
        inventory_level=inventory_level,
    )

    # Предложения следующих действий
    suggestions = SuggestionService().generate_suggestions(
        product_id=product_id,
        forecast_context={"risk_level": insights.risk.level.value},
        alerts=[a.model_dump() for a in alerts],
    )

    return {
        "predictions": predictions,
        "trust":        trust_layer,
        "insights":     insights,
        "alerts":       alerts,
        "suggestions":  suggestions,
        "has_critical_alert": any(a.severity.value == "critical" for a in alerts),
    }
```

---

## 8. AI Chat — RAG Pipeline и маршрутизация интентов

**Файл:** `back/services/ai_chat_service.py`
**Описание:** Ядро AI чата. Входящее сообщение сначала классифицируется по интенту (намерению). Структурированные интенты (прогноз, анализ продукта) получают детерминированный ответ без LLM. Текстовые интенты строят RAG-контекст из данных и передают его LLM (Claude AI) для генерации ответа.

```python
# Интенты с детерминированным структурированным ответом (без LLM)
STRUCTURED_INTENTS = {
    Intent.FORECAST,
    Intent.SMART_FORECAST,
    Intent.PRODUCT_INFO,
    Intent.PRODUCT_ANALYSIS,
    Intent.SEASONALITY,
    Intent.WEATHER_IMPACT,
}

# Интенты с текстовым LLM-ответом
TEXT_INTENTS = {
    Intent.GENERAL,
    Intent.RECOMMENDATIONS,
    Intent.TRENDS,
    Intent.TOP_PRODUCTS,
    Intent.CATEGORY_STATS,
    Intent.REGION_STATS,
}

# Интенты для Казахстанского рынка
KZ_INTENTS = {
    Intent.KZ_ANALYSIS,
    Intent.KZ_CITY_PROFIT,
    Intent.KZ_COMPETITOR,
    Intent.KZ_WHOLESALE,
}


def build_rag_context(intent: Intent, entities: Dict[str, Any]) -> str:
    """
    RAG (Retrieval-Augmented Generation) — строит контекст для LLM
    на основе реальных данных из базы/датасета
    """
    context_parts = []
    product_ids = entities.get("product_ids", [])
    category    = entities.get("category")
    days        = entities.get("days", 7)

    if intent == Intent.FORECAST:
        for pid in product_ids[:2]:
            summary = get_product_summary(pid)
            if summary:
                context_parts.append(build_forecast_context(summary, days))

    elif intent == Intent.COMPARISON:
        comparison_queries = entities.get("comparison_queries", [])
        if comparison_queries:
            # Поиск продуктов для сравнения
            for query in comparison_queries[:4]:
                results = search_amazon_products(query, top_k=1)
                if results:
                    analysis = get_amazon_product_analysis(results[0]['product_id'])
                    context_parts.append(build_amazon_comparison_context([analysis]))

    elif intent == Intent.TOP_PRODUCTS:
        performers = get_top_performers(top_n=entities.get("top_n", 5))
        context_parts.append(build_top_products_context(performers))

    elif intent == Intent.CATEGORY_STATS:
        stats = get_category_stats(category)
        context_parts.append(build_category_context(stats))

    return "\n\n".join(context_parts)
```

---

## 9. Аутентификация — Email верификация и Google OAuth

**Файл:** `back/app/auth_routes.py`
**Описание:** Трёхшаговая регистрация через email: отправка кода → проверка кода → создание аккаунта с паролем. Google OAuth верифицирует токен через Google API и автоматически создаёт аккаунт. Все эндпоинты защищены rate limiter от брутфорса.

```python
# ===== ШАГ 1: Отправка кода подтверждения =====
@router.post("/auth/send-code")
@limiter.limit(RateLimits.SEND_CODE)  # Защита от спама
def send_verification_code(request: Request, data: SendCodeRequest, db: Session = Depends(get_db)):
    # Удаляем старые коды и создаём новый
    db.query(VerificationCode).filter(VerificationCode.email == data.email).delete()
    code = generate_verification_code()  # 6-значный код
    db.add(VerificationCode(
        email=data.email, code=code, expires_at=get_code_expiry()
    ))
    db.commit()
    send_verification_email(data.email, code)


# ===== ШАГ 2+3: Верификация и регистрация =====
@router.post("/auth/complete-registration", response_model=TokenPairResponse)
def complete_registration(request: Request, data: CompleteRegistrationRequest, db: Session = Depends(get_db)):
    # Проверяем код
    verification = db.query(VerificationCode).filter(
        VerificationCode.email == data.email,
        VerificationCode.code == data.code,
        VerificationCode.is_used == False
    ).first()

    if verification.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Код истёк")

    verification.is_used = True
    db.commit()

    # Создаём пользователя с хэшированным паролем
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),  # bcrypt
        is_verified=True,
    )
    db.add(user)
    db.commit()

    access_token, refresh_token = create_token_pair(user.email)
    return TokenPairResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        is_admin=user.is_admin,
    )


# ===== GOOGLE OAUTH =====
@router.post("/auth/google", response_model=TokenPairResponse)
def google_auth(request: Request, data: GoogleAuthRequest, db: Session = Depends(get_db)):
    # Верифицируем токен через Google API
    idinfo = id_token.verify_oauth2_token(
        data.credential,
        google_requests.Request(),
        GOOGLE_CLIENT_ID
    )

    email      = idinfo.get("email")
    google_id  = idinfo.get("sub")
    full_name  = idinfo.get("name")
    avatar_url = idinfo.get("picture")

    # Находим или создаём пользователя
    user = db.query(User).filter(
        (User.email == email) | (User.google_id == google_id)
    ).first()

    if not user:
        user = User(email=email, google_id=google_id,
                    full_name=full_name, avatar_url=avatar_url, is_verified=True)
        db.add(user)
        db.commit()

    access_token, refresh_token = create_token_pair(user.email)
    return TokenPairResponse(access_token=access_token, refresh_token=refresh_token)


# ===== СТАНДАРТНЫЙ ЛОГИН =====
@router.post("/auth/login", response_model=TokenPairResponse)
@limiter.limit(RateLimits.LOGIN)
def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверные данные")

    if not user.is_verified:
        raise HTTPException(status_code=401, detail="Email не подтверждён")

    access_token, refresh_token = create_token_pair(user.email)
    return TokenPairResponse(
        access_token=access_token, refresh_token=refresh_token,
        is_admin=user.is_admin, email=user.email
    )
```

---

## 10. Генерация отчётов и экспорт в Excel

**Файл:** `back/app/report_routes.py`
**Описание:** Система генерации отчётов создаёт Excel-файлы с анализом прогноза, историческими данными и бизнес-рекомендациями. Отчёт по казахстанскому рынку включает расчёт маржинальности по городам с учётом конкуренции.

```python
@router.get("/reports/forecast/{product_id}")
def get_forecast_report(product_id: str, horizon_days: int = 30,
                        user=Depends(get_admin_user)):
    """Отчёт с прогнозом + история + метрики модели"""
    df = load_df()
    sub = df[df["Product ID"] == product_id]

    trained = get_or_train_model(sub, product_id)
    future_df, preds = predict(trained, horizon_days)

    # История последних 30 дней
    history = sub.sort_values("Date").tail(30)[["Date", "Demand Forecast"]].to_dict("records")

    # Прогноз с доверительными интервалами ±15%
    forecast_data = [
        {
            "date":           str(d.date()),
            "predicted":      round(float(p), 2),
            "lower_bound":    round(float(p) * 0.85, 2),
            "upper_bound":    round(float(p) * 1.15, 2),
        }
        for d, p in zip(future_df["Date"], preds)
    ]

    # Формируем Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame(history).to_excel(writer, sheet_name="History", index=False)
        pd.DataFrame(forecast_data).to_excel(writer, sheet_name="Forecast", index=False)
        pd.DataFrame([trained["metrics"]]).to_excel(writer, sheet_name="Metrics", index=False)

    return StreamingResponse(
        BytesIO(output.getvalue()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=forecast_{product_id}.xlsx"}
    )
```

---

## Архитектурная схема системы

```
┌─────────────────────────────────────────────────────────────┐
│                      КЛИЕНТ                                  │
│         Web (React)          Mobile (Flutter)                │
└──────────────────┬───────────────────────────────────────────┘
                   │ HTTP/REST
┌──────────────────▼───────────────────────────────────────────┐
│                FastAPI Backend                                │
│                                                              │
│  /auth/*        /forecast     /forecast/v2    /chat          │
│  (JWT + OAuth)  (ML v1)       (Decision       (RAG +         │
│                               Assistant)       LLM)          │
│                                                              │
│  ┌─────────────────┐    ┌──────────────────────────────┐    │
│  │   ML Pipeline   │    │      AI Chat Pipeline        │    │
│  │                 │    │                              │    │
│  │ Feature Eng. → │    │ Intent → RAG Context →       │    │
│  │ RandomForest /  │    │ LLM (Claude) → Response     │    │
│  │ LightGBM /     │    │                              │    │
│  │ XGBoost        │    └──────────────────────────────┘    │
│  │                 │                                        │
│  │ Cache: RAM+Disk │    ┌──────────────────────────────┐    │
│  └─────────────────┘    │     Trust & Alert Layer      │    │
│                          │ Confidence + Insights +     │    │
│                          │ Alerts + Suggestions        │    │
│                          └──────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │   Database (SQLite/PostgreSQL via SQLAlchemy)       │    │
│  │   Users | VerificationCodes | ChatHistory           │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## Используемые технологии

| Компонент | Технология |
|-----------|-----------|
| Web Framework | FastAPI (Python) |
| ML Models | scikit-learn, LightGBM, XGBoost |
| LLM | Claude AI (Anthropic API) |
| Database | SQLAlchemy + SQLite/PostgreSQL |
| Auth | JWT tokens + Google OAuth 2.0 |
| Caching | In-memory dict + joblib (disk) |
| Rate Limiting | slowapi |
| Reports | openpyxl (Excel) |
| Deployment | Railway (backend) + Vercel (frontend) |
