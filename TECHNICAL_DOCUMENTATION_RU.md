# Forecast AI — Полная Техническая Документация
### Для Защиты Дипломной Работы

---

## Общий Обзор Проекта

**Forecast AI** — система прогнозирования спроса на основе AI, разработанная для казахстанского рынка. Проект состоит из трёх частей:

1. **Backend** — Python FastAPI, ML модели, REST API
2. **Frontend** — React 19 + Vite, веб-панель администратора
3. **Mobile** — Flutter, приложение для iOS/Android

**Проблема**: Малый и средний бизнес не может точно прогнозировать спрос на товары — либо закупают лишнее (убытки), либо не хватает (упущенная прибыль). Наша система даёт прогноз на 7–30 дней через ML модели и отвечает на вопросы через AI чат.

---

# ЧАСТЬ ПЕРВАЯ: BACKEND (Python / FastAPI)

## 1.1 Технологии и Пакеты

**Основной стек:**

| Пакет | Версия | Применение |
|-------|--------|-----------|
| `fastapi` | 0.126.0 | Web framework — автогенерация API docs, type hints |
| `uvicorn[standard]` | 0.34.0 | ASGI сервер — обработка async HTTP |
| `sqlalchemy` | 2.0.46 | ORM — преобразование Python объектов в SQL |
| `python-jose[cryptography]` | 3.5.0 | Создание и проверка JWT токенов |
| `passlib[bcrypt]` | 1.7.4 | Хеширование паролей (алгоритм bcrypt) |
| `pandas` | 2.3.3 | Обработка данных (DataFrame, merge, groupby) |
| `numpy` | 2.0.2 | Математические операции |
| `scikit-learn` | 1.6.1 | Random Forest, Pipeline, preprocessing |
| `lightgbm` | ≥4.0.0 | LightGBM gradient boosting модель |
| `xgboost` | ≥2.0.0 | XGBoost gradient boosting модель |
| `openai` | 2.14.0 | Клиент OpenAI GPT-4o API |
| `psycopg2-binary` | 2.9.9 | Драйвер PostgreSQL |
| `slowapi` | 0.1.9 | Rate limiting (лимит: 5 логинов/мин, 20 чатов/мин) |
| `pydantic-settings` | 2.2.1 | Валидация переменных окружения с типами |
| `python-telegram-bot` | 20.7 | API Telegram бота |
| `google-auth` | 2.29.0 | Проверка токенов Google OAuth |
| `resend` | 2.0.0 | Сервис отправки email |
| `httpx` | 0.25.2 | Async HTTP клиент |
| `openpyxl` | 3.1.2 | Генерация Excel файлов |
| `jinja2` | 3.1.3 | HTML шаблоны (генерация отчётов) |
| `google-genai` | latest | Google Gemini AI (резервный LLM) |

**Почему FastAPI?** Быстрее Flask и Django. Автогенерация Swagger UI, поддержка async, Pydantic валидация — оптимальный выбор для Production API.

---

## 1.2 Структура Проекта

```
back/
├── backend.py                   # Точка входа: uvicorn backend:app
├── app/
│   ├── models.py               # SQLAlchemy ORM классы
│   ├── schemas.py              # Pydantic схемы request/response
│   ├── security.py             # Логика создания и проверки JWT
│   ├── auth_routes.py          # Эндпоинты /auth/*
│   ├── config.py               # Настройки (валидация env vars)
│   ├── database.py             # Engine, Session, Base, get_db()
│   ├── deps.py                 # FastAPI зависимости (get_current_user)
│   ├── rate_limiter.py         # Конфигурация rate limiting (SlowAPI)
│   ├── email_service.py        # Отправка email/кода верификации
│   ├── report_routes.py        # Эндпоинты отчётов Excel/CSV
│   ├── telegram_routes.py      # Webhook Telegram бота
│   ├── user_routes.py          # Админ: CRUD пользователей
│   ├── settings_routes.py      # Настройки пользователя
│   ├── demo_billing.py         # Mock подписка (демо)
│   └── routers/
│       └── dashboard.py        # Эндпоинты панели директора
├── services/                    # 23 модуля бизнес-логики
│   ├── ai_chat_service.py      # AI чат: стриминг, история, аналитика
│   ├── model_service.py        # ML модель: train, cache, predict
│   ├── forecast_service.py     # Логика прогнозирования
│   ├── insight_service.py      # Бизнес инсайты
│   ├── intent_classifier.py    # NLU: определение намерения сообщения
│   ├── alert_service.py        # Предупреждения об угрозах
│   ├── kz_market_service.py    # Аналитика казахстанского рынка
│   ├── scenario_service.py     # Анализ сценариев "что если"
│   └── ... (ещё 15 сервисов)
├── models/                      # Сохранённые ML модели (.pkl файлы)
│   ├── P0001_S001_lightgbm.pkl
│   ├── P0001_S001_xgboost.pkl
│   └── P0001_S001_random_forest.pkl
├── data/
│   ├── amazon/                 # Датасет товаров Amazon
│   └── ecommerce/              # Данные e-commerce
├── prompts/                     # Шаблоны промптов для LLM
├── Dockerfile                   # Конфигурация деплоя Railway
└── requirements.txt
```

**Зачем отдельная папка `services/`?** Routes — только HTTP; services — бизнес-логика. Это принцип SOLID (Single Responsibility). Упрощает написание тестов и повторное использование логики.

---

## 1.3 Модели Базы Данных (SQLAlchemy ORM)

### Таблица User (Пользователи)
```python
class User(Base):
    __tablename__ = "users"

    id: int                              # Primary Key
    email: str                           # Unique, indexed
    hashed_password: Optional[str]       # None = вошёл через Google OAuth
    is_active: bool = True               # Возможность деактивации
    is_admin: bool = False               # Права администратора
    is_verified: bool = False            # Прошла ли верификация email

    # Google OAuth
    google_id: Optional[str]             # Уникальный Google ID
    avatar_url: Optional[str]            # Фото профиля Google
    full_name: Optional[str]             # Полное имя

    # Подписка
    subscription_plan: str = "free"      # "free" | "paid" | "pro"

    is_onboarding_completed: bool = False
    created_at: datetime = utcnow
```

### Таблица UserSettings (Настройки пользователя)
```python
class UserSettings(Base):
    __tablename__ = "user_settings"

    id: int
    user_id: int          # FK → users.id (UNIQUE — один пользователь = одна запись)
    settings_json: str    # Сохраняется как JSON текст
    updated_at: datetime  # Автообновление при изменениях
```

**Почему JSON as text?** Схема настроек часто меняется. Если хранить как JSON — можно добавлять новые поля без миграций.

### Таблица ChatHistory (История чата)
```python
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: int
    user_id: int            # FK → users.id
    role: str               # "user" | "assistant"
    content: str            # Текст сообщения
    intent: Optional[str]   # Определённое намерение (forecast, analytics, и др.)
    data_json: Optional[str] # Данные диаграммы/таблицы
    created_at: datetime

    # Составной индекс: (user_id, created_at) — для быстрого поиска
```

### Таблица VerificationCode (Коды верификации)
```python
class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id: int
    email: str
    code: str          # 6-значный код
    created_at: datetime
    expires_at: datetime  # created_at + 10 минут
    is_used: bool = False # Нельзя использовать повторно
```

---

## 1.4 Аутентификация (JWT — полный поток)

### Регистрация (3 шага)

```
ШАГ 1: POST /auth/send-code
  → Вход: { "email": "user@example.com" }
  → Логика:
     1. Проверить — email ещё не зарегистрирован?
     2. Сгенерировать 6-значный код
     3. Создать запись VerificationCode(email, code, expires_at=сейчас+10мин)
     4. Отправить email через resend.com
  ← Выход: { "message": "Code sent", "success": true }

ШАГ 2: POST /auth/verify-code
  → Вход: { "email": "user@example.com", "code": "123456" }
  → Логика:
     1. Код существует?
     2. Срок не истёк? (expires_at > сейчас)
     3. Уже использован? (is_used = false)
  ← Выход: { "message": "Code verified", "success": true }

ШАГ 3: POST /auth/complete-registration
  → Вход: { "email": ..., "code": ..., "password": "securepass" }
  → Логика:
     1. Повторно проверить код
     2. Установить is_used = True
     3. bcrypt.hash(password) → hashed_password
     4. Создать или обновить запись User
     5. Сгенерировать пару JWT
  ← Выход: {
       "access_token": "eyJ...",   // действителен 24 часа
       "refresh_token": "eyJ...",  // действителен 7 дней
       "is_admin": false,
       "email": "user@example.com"
     }
```

### Вход (Логин)

```
POST /auth/login
  → Вход: { "email": ..., "password": ... }
  → Логика:
     1. Пользователь существует? → 401
     2. is_verified = true? → 403
     3. is_active = true? → 403
     4. bcrypt.verify(password, hashed_password)? → 401
     5. Сгенерировать пару JWT
  ← Выход: { access_token, refresh_token }
```

### Обновление Токена

```
POST /auth/refresh
  → Вход: { "refresh_token": "eyJ..." }
  → Логика:
     1. JWT decode (проверить type = "refresh")
     2. Извлечь email из sub
     3. Сгенерировать новый access_token
  ← Выход: { access_token, refresh_token }
```

### Структура JWT

```json
// Access Token (HS256)
{
  "sub": "user@example.com",
  "type": "access",
  "iat": 1717913600,
  "exp": 1717999999   // +24 часа
}

// Refresh Token (HS256)
{
  "sub": "user@example.com",
  "type": "refresh",
  "iat": 1717913600,
  "exp": 1718518000   // +7 дней
}
```

**Почему JWT?** Stateless — сервер не хранит сессии. Мобайл + веб работают одновременно. Паттерн refresh token — access token краткосрочный (безопасно), refresh token долгосрочный (удобно).

### Google OAuth

```
POST /auth/google
  → Вход: { "credential": "<Google ID Token>" }
  → Логика:
     1. google.oauth2.id_token.verify_oauth2_token()
     2. Получить email, google_id, full_name, avatar_url
     3. User UPSERT (создать или обновить)
     4. Сгенерировать пару JWT
  ← Выход: { access_token, refresh_token }
```

### Защищённые Эндпоинты

```python
# deps.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = decode_token(token)    # JWT decode
        email = payload["sub"]           # Получить email
    except JWTError:
        raise HTTPException(401)

    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(401)
    return user

# Использование в endpoint:
@router.get("/forecast")
async def get_forecast(user: User = Depends(get_current_user)):
    # user передан автоматически, токен уже проверен
    ...
```

---

## 1.5 Все API Эндпоинты

### Аутентификация (`/auth`)
```
POST  /auth/send-code               Отправка кода на email
POST  /auth/verify-code             Проверка 6-значного кода
POST  /auth/complete-registration   Завершение регистрации
POST  /auth/google                  Вход через Google OAuth
POST  /auth/login                   Вход email/пароль
POST  /auth/refresh                 Обновление access token
GET   /auth/me                      Текущий пользователь
PATCH /auth/me                      Обновление профиля (full_name)
POST  /auth/mock-subscribe          Демо подписка (тест)
POST  /auth/me/onboarding-complete  Отметить onboarding завершённым
```

### Прогнозирование (`/forecast`)
```
GET   /forecast                    Прогноз спроса
      params: product_id, horizon_days, store_id
GET   /forecast/v2                 Прогноз + бизнес инсайты
GET   /history/{product_id}        Исторические данные
      params: store_id, limit=100, offset=0
GET   /products                    Список всех товаров
GET   /forecast/chart/{product_id} Данные диаграммы
GET   /forecast/compare            Сравнение моделей
```

### AI Чат (`/chat`)
```
POST  /chat                        Отправить сообщение AI
      body: { message, language, model_type }
POST  /chat/stream                 Streaming ответ (SSE)
GET   /chat/history                История чата
      params: limit (опционально)
DELETE /chat/history               Очистить историю чата
POST  /chat/scenario               Анализ сценария
GET   /chat/scenario/features      Доступные сценарии
```

### Аналитика (`/analytics`)
```
GET   /analytics/summary           Общая статистика
GET   /analytics/trends            Рыночные тренды
```

### Управление Моделями (`/models`)
```
GET   /models/cache                Информация о кэше
DELETE /models/cache               Очистить кэш
POST  /models/retrain/{product_id} Переобучить модель
GET   /models/structure            Архитектура модели
GET   /models/features/{product_id} Feature importance
```

### Панель Директора (`/dashboard`)
```
GET   /dashboard/executive         Панель директоров (только админ)
POST  /dashboard/forecast-explorer Прогноз с фильтрами
GET   /dashboard/alerts            Активные предупреждения
```

### Отчёты (`/reports`)
```
GET   /reports/daily               Ежедневный отчёт (Excel/CSV)
GET   /reports/forecast/{product_id} Отчёт прогноза по товару
GET   /reports/analytics           Аналитический отчёт
GET   /reports/kz-market           Отчёт казахстанского рынка
```

### Казахстанский Рынок (`/kz`)
```
GET   /kz/cities                   16+ городов Казахстана
GET   /kz/categories               Категории товаров
POST  /kz/analyze                  Региональный анализ рынка
      body: { product_name, markup_percent }
GET   /kz/competitors              Цены конкурентов
GET   /kz/trends/{category}        Тренды по категории
POST  /kz/logistics                Калькулятор логистических затрат
```

### Управление Пользователями (`/admin/users`) — только Админ
```
GET   /admin/users                 Все пользователи (с пагинацией)
GET   /admin/users/{id}            Данные пользователя
PATCH /admin/users/{id}            Обновить пользователя
DELETE /admin/users/{id}           Удалить пользователя
```

### Настройки (`/settings`)
```
GET   /settings                    Получить настройки пользователя
PUT   /settings                    Обновить все настройки
PATCH /settings/{section}          Обновить один раздел
DELETE /settings                   Очистить настройки
```

---

## 1.6 ML Модели и Pipeline

### Три Модели

| Модель | Тариф | Горизонт | Особенность |
|--------|-------|----------|-------------|
| Random Forest | Бесплатно (Free) | 7 дней | Быстрый, легко интерпретировать |
| LightGBM | Pro | 30 дней | От Microsoft, leaf-wise рост |
| XGBoost | Pro | 30 дней | От Amazon, сильная регуляризация |

**Почему три модели?** Random Forest — базовый, работает быстро. LightGBM/XGBoost — точнее, но требуют ресурсов. Выдаём в зависимости от уровня подписки.

### Feature Engineering

```python
# Признаки даты
day, month, day_of_week
month_sin = sin(2π * month / 12)   # Циклическое кодирование — чтобы модель не считала декабрь=1
month_cos = cos(2π * month / 12)

# Лаговые признаки (временной ряд)
demand_lag_1    = спрос вчера
demand_lag_7    = 7 дней назад
demand_lag_14   = 14 дней назад
demand_lag_30   = 30 дней назад
demand_rolling_mean_7   = скользящее среднее за 7 дней
demand_rolling_std_7    = стандартное отклонение за 7 дней
demand_rolling_mean_30  = скользящее среднее за 30 дней
demand_diff             = изменение за день

# Категориальные (One-Hot Encoded)
Category, Region, Weather, Seasonality, Store ID

# Числовые
Inventory Level, Units Ordered, Price,
Discount, Competitor Pricing, Holiday/Promotion
```

### Pipeline Обучения

```python
def train_model(df, model_type="random_forest"):
    # 1. Feature Engineering
    df = add_date_features(df)
    df = add_lag_features(df)

    # 2. Train/Test Split (80/20)
    train, test = temporal_split(df, test_size=0.2)

    # 3. Preprocessing (внутри Pipeline)
    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features),
        ("num", StandardScaler(), num_features)
    ])

    # 4. Модель
    models = {
        "random_forest": RandomForestRegressor(n_estimators=300, n_jobs=-1),
        "lightgbm": LGBMRegressor(n_estimators=500, learning_rate=0.05, num_leaves=63),
        "xgboost": XGBRegressor(n_estimators=500, learning_rate=0.05)
    }

    # 5. Pipeline (preprocessor + model)
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", models[model_type])
    ])
    pipeline.fit(X_train, y_train)

    # 6. Метрики
    y_pred = pipeline.predict(X_test)
    metrics = {
        "mae":  mean_absolute_error(y_test, y_pred),
        "rmse": sqrt(mean_squared_error(y_test, y_pred)),
        "r2":   r2_score(y_test, y_pred)
    }

    # 7. Кэш (память + диск)
    _model_cache[f"{product_id}_{store_id}_{model_type}"] = {
        "model": pipeline, "metrics": metrics
    }
    joblib.dump(pipeline, f"models/{cache_key}.pkl")

    return pipeline, metrics
```

### Предсказание

```python
def predict(model, df, horizon_days=7):
    # Генерируем будущие даты
    future_dates = date_range(df["Date"].max()+1, periods=horizon_days)

    # Feature engineering (лаги из исторических данных)
    future_df = build_future_features(future_dates, df)

    # Прогноз
    predictions = model.predict(future_df[features])

    # Доверительный интервал ±15%
    return {
        "dates": future_dates,
        "predictions": predictions,
        "lower_bound": predictions * 0.85,
        "upper_bound": predictions * 1.15
    }
```

### Стратегия Кэширования

```
cache_key = "{product_id}_{store_id}_{model_type}"

1. cache_key есть? → вернуть из кэша (быстро)
2. Есть .pkl файл? → загрузить с диска
3. Ни того ни другого → обучить, сохранить в кэш и на диск
```

---

## 1.7 Rate Limiting

```python
SEND_CODE    = "3/minute"   # Отправка кода на email
VERIFY_CODE  = "5/minute"   # Проверка кода
LOGIN        = "5/minute"   # Попытки входа
CHAT         = "20/minute"  # Сообщения AI чата
DEFAULT      = "100/minute" # Остальные эндпоинты

# Ключ:
# Зарегистрированный пользователь: "user:{user_id}"
# Незарегистрированный: IP адрес
```

При превышении → возвращается **429 Too Many Requests**.

---

## 1.8 Деплой

**Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["sh", "-c", "uvicorn backend:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

**Переменные Окружения:**
```bash
JWT_SECRET_KEY=<минимум 32 символа>
OPENAI_API_KEY=<ключ OpenAI>
DATABASE_URL=postgresql://user:pass@host/db
GOOGLE_CLIENT_ID=<Google OAuth>
TELEGRAM_BOT_TOKEN=<Telegram>
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
FRONTEND_URL=https://demand-forecasting-orcin.vercel.app
```

**CORS разрешения:**
- `http://localhost:5173` (dev frontend)
- `https://demand-forecasting-orcin.vercel.app` (prod)
- Railway автоматически HTTPS

---

# ЧАСТЬ ВТОРАЯ: FRONTEND (React / Vite)

## 2.1 Технологии и Пакеты

**Основной стек:**

| Пакет | Версия | Применение |
|-------|--------|-----------|
| `react` | 19.2.0 | UI framework, компонентно-ориентированный |
| `react-dom` | 19.2.0 | DOM rendering |
| `react-router-dom` | 7.13.0 | SPA routing, protected routes |
| `vite` | 7.2.4 | Build tool, HMR (Hot Module Replacement) |
| `recharts` | 3.8.0 | Линейные/столбчатые диаграммы |
| `chart.js` + `react-chartjs-2` | 4.5.1 | Круговые диаграммы |
| `three` | 0.183.2 | 3D визуализация (Landing page) |
| `@react-three/fiber` | 9.5.0 | React обёртка для Three.js |
| `framer-motion` | 12.38.0 | Анимации |
| `gsap` | 3.14.2 | Scroll анимации |
| `i18next` | 26.0.3 | Интернационализация (KK/RU/EN) |
| `react-i18next` | 17.0.2 | React хуки для i18n |
| `lucide-react` | 0.468.0 | Иконки |
| `sonner` | 2.0.7 | Toast уведомления |
| `driver.js` | 1.3.1 | Онбординг тур (UI подсказки) |

**Почему Vite?** В 10–50 раз быстрее Create React App. Использует ES modules, HMR работает мгновенно.

---

## 2.2 Структура Проекта

```
frontend-admin/
├── src/
│   ├── App.jsx                    # Маршрутизация + провайдеры
│   ├── main.jsx                   # Точка входа React DOM
│   ├── config.js                  # Конфигурация API URL
│   │
│   ├── pages/                     # Страницы маршрутов
│   │   ├── LandingPage.jsx       # Публичная страница (3D анимация)
│   │   ├── LoginPage.jsx         # Email верификация + вход
│   │   ├── ChatPage.jsx          # Интерфейс AI чата (47KB!)
│   │   ├── AdminDashboard.jsx    # Панель администратора
│   │   ├── ExecutiveDashboardPage.jsx  # Панель директора
│   │   ├── TablePage.jsx         # Таблица данных
│   │   ├── UploadPage.jsx        # Загрузка CSV
│   │   ├── ModelVisualizationPage.jsx  # Визуализация ML модели
│   │   ├── ReportsPage.jsx       # Генерация отчётов
│   │   ├── UserManagementPage.jsx     # CRUD пользователей (Admin)
│   │   ├── ProfilePage.jsx       # Профиль пользователя
│   │   ├── SubscriptionPage.jsx  # Страница тарифов
│   │   ├── SubscriptionPaymentPage.jsx  # Mock checkout
│   │   └── ForecastWorkspacePage.jsx   # Рабочее пространство прогноза
│   │
│   ├── components/               # Переиспользуемые компоненты (18 файлов)
│   │   └── OnboardingGate.jsx   # Управление потоком онбординга
│   │
│   ├── context/                  # Управление состоянием
│   │   ├── AuthContext.jsx       # Состояние аутентификации
│   │   ├── SettingsContext.jsx   # Настройки пользователя
│   │   └── ThemeContext.jsx      # Тёмная/светлая тема
│   │
│   ├── api/                      # Слой API клиента
│   │   ├── authApi.js           # Auth эндпоинты
│   │   ├── chatApi.js           # Чат эндпоинты
│   │   ├── forecastApi.js       # Эндпоинты прогноза
│   │   ├── settingsApi.js       # CRUD настроек
│   │   └── userApi.js           # Эндпоинты пользователя
│   │
│   ├── utils/                    # Утилиты
│   │   ├── authStorage.js       # Кэш Token/user (localStorage)
│   │   └── postAuthRedirect.js  # Route guards
│   │
│   └── i18n/locales/
│       ├── kk.json              # Казахский перевод
│       ├── ru.json              # Русский перевод
│       └── en.json              # Английский перевод
│
├── vercel.json                   # Конфигурация деплоя Vercel
└── package.json
```

---

## 2.3 Аутентификация (AuthContext)

**Файл**: `src/context/AuthContext.jsx`

```javascript
// Типы состояния
const AuthStatus = {
  LOADING: 'loading',               // Токен проверяется
  AUTHENTICATED: 'authenticated',   // Вошёл
  UNAUTHENTICATED: 'unauthenticated' // Вышел
};

// Содержимое контекста
{
  user: {
    id, email, is_admin,
    subscription_plan,     // "free" | "paid" | "pro"
    full_name, avatar_url,
    created_at
  },
  isAuthenticated: boolean,
  isLoading: boolean,
  error: string | null
}
```

**Логика инициализации:**

```javascript
async function checkAuth() {
  const token = getToken();    // Получить из localStorage
  if (!token) {
    setStatus(UNAUTHENTICATED);
    return;
  }

  // Сразу установить кэшированного пользователя, чтобы не было flash
  const cachedUser = getCachedUser();
  if (cachedUser) {
    setUser(cachedUser);
    setStatus(AUTHENTICATED);
  }

  // Проверить на сервере
  try {
    const response = await fetch(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const userData = await response.json();
    setUser(userData);
    setCachedUser(userData);  // Обновить кэш
    setStatus(AUTHENTICATED);
  } catch {
    clearAllAuthData();
    setStatus(UNAUTHENTICATED);
  }
}
```

**Зачем кэш?** При загрузке страницы запрос `/auth/me` занимает 200–500мс. В это время если быть в состоянии `LOADING` — пользователь видит пустой экран. Если сразу установить из кэша — UI мгновенный.

---

## 2.4 API Клиент

**chatApi.js — SSE Streaming:**

```javascript
export async function sendChatMessageStream(
  message,
  language,
  modelType,
  onChunk,  // Функция: вызывается для каждого токена
  onMeta    // Функция: для метаданных
) {
  const response = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${getToken()}`
    },
    body: JSON.stringify({ message, language, model_type: modelType })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const text = decoder.decode(value);
    // SSE формат: "data: {json}\n\n"
    const lines = text.split('\n').filter(l => l.startsWith('data: '));

    for (const line of lines) {
      const data = JSON.parse(line.slice(6));
      if (data.type === 'chunk') onChunk(data.content);
      if (data.type === 'meta') onMeta(data);
    }
  }
}
```

**Почему SSE (Server-Sent Events)?** Проще чем WebSocket — однонаправленный (сервер→клиент). Даёт живой print effect как ChatGPT. Пользователь начинает читать ответ сразу.

---

## 2.5 Маршрутизация

```javascript
// App.jsx
<AuthGuard>        // Ждать пока аутентификация проверится
  <AuthProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={
          <PublicRoute>  // Если вошёл → редирект на /chat
            <LoginPage />
          </PublicRoute>
        } />

        {/* Маршруты пользователя */}
        <Route path="/chat" element={
          <UserRoute>    // Если не вошёл → редирект на /login
            <ChatPage />
          </UserRoute>
        } />

        {/* Только Админ маршруты */}
        <Route path="/admin/*" element={
          <AdminRoute>   // Если is_admin=false → редирект на /chat
            <AdminDashboard />
          </AdminRoute>
        } />
      </Routes>
    </BrowserRouter>
  </AuthProvider>
</AuthGuard>
```

**Типы Route Guard:**
- **PublicRoute** — только для незарегистрированных
- **UserRoute** — для любого авторизованного пользователя
- **AdminRoute** — только если `is_admin=true`
- **AuthGuard** — ожидает проверки, чтобы не было flash контента

---

## 2.6 Деплой (Vercel)

```json
// vercel.json
{
  "framework": "vite",
  "buildCommand": "vite build",
  "outputDirectory": "dist",
  "env": {
    "VITE_API_URL": "https://demand-forecasting-production-c886.up.railway.app"
  }
}
```

**CI/CD:** Git push → Vercel автоматически собирает → Deploy. Для каждого pull request создаётся Preview URL.

---

# ЧАСТЬ ТРЕТЬЯ: MOBILE (Flutter / Dart)

## 3.1 Технологии и Пакеты

**Основной стек:**

| Пакет | Версия | Применение |
|-------|--------|-----------|
| `flutter` SDK | ≥3.3.0 | Кросс-платформенный UI framework |
| `dart` | ≥3.3.0 | Язык (строгая типизация, null-safe) |
| `provider` | 6.1.1 | Управление состоянием (ChangeNotifier) |
| `dio` | 5.4.0 | HTTP клиент (interceptors, retry) |
| `flutter_secure_storage` | 10.0.0 | Безопасное хранение JWT токена (Keychain/Keystore) |
| `shared_preferences` | 2.2.2 | Кэш, настройки (key-value) |
| `fl_chart` | 0.69.0 | Интерактивные диаграммы |
| `cached_network_image` | 3.3.1 | Кэширование сетевых изображений |
| `shimmer` | 3.0.0 | Skeleton анимация загрузки |
| `lottie` | 3.1.0 | JSON анимации |
| `share_plus` | 13.1.0 | Шэринг отчётов |
| `intl` | 0.20.2 | Форматирование даты/времени |
| `equatable` | 2.0.5 | Сравнение объектов (оператор ==) |
| `google_fonts` | 6.1.0 | Кастомные шрифты |
| `flutter_localizations` | SDK | Локализация (KK/RU/EN) |

**Почему Flutter?** Один код → iOS + Android. Dart — статически типизированный, null-safe. Hot reload — быстрая разработка.

---

## 3.2 Структура Проекта

```
prodbot_ai/lib/
├── main.dart                       # Точка входа приложения
├── core/
│   ├── config/
│   │   └── app_config.dart        # Конфигурация (Railway URL, версия)
│   ├── theme/
│   │   └── theme.dart             # AppColors, AppTextStyles, AppDimensions
│   └── locale/                    # Конфигурация языка
│
├── data/
│   ├── models/
│   │   ├── current_user.dart      # Модель пользователя
│   │   ├── chat_models.dart       # Модели сообщений и ответов
│   │   ├── conversation.dart      # Модель диалога
│   │   └── user_settings.dart     # Модель настроек
│   ├── providers/                 # Провайдеры для получения данных
│   └── repositories/              # Repository pattern
│
├── presentation/
│   ├── screens/
│   │   ├── splash/                # Экран загрузки
│   │   ├── onboarding/            # Welcome, SubscriptionPlans
│   │   ├── auth/                  # Login, Register
│   │   ├── chat/                  # ChatHomeScreen, виджеты
│   │   │   └── widgets/
│   │   │       ├── chat_drawer.dart      # Боковая панель
│   │   │       ├── message_bubble.dart   # UI сообщения
│   │   │       ├── model_selector.dart   # Выбор ML модели
│   │   │       ├── mini_chart.dart       # Мини диаграмма
│   │   │       └── product_carousel.dart # Carousel товаров
│   │   ├── home/                  # Главный экран
│   │   ├── profile/               # ProfileScreen, SettingsScreen, SubscriptionScreen
│   │   ├── analytics/             # Экран аналитики
│   │   ├── forecast/              # Экран прогноза
│   │   └── reports/               # Экран отчётов
│   └── widgets/                   # Общие виджеты
│       └── common/
│           └── brand_logo.dart    # Компонент BrandLogo
│
├── services/
│   ├── api/
│   │   ├── api_client.dart        # Dio HTTP клиент (singleton)
│   │   ├── api_exception.dart     # Кастомные классы ошибок
│   │   └── api_interceptor.dart   # Auth, Logging, Retry interceptors
│   ├── auth_service.dart          # Логика аутентификации
│   ├── chat_service.dart          # Логика чат API
│   ├── storage_service.dart       # LocalStorage + SecureStorage
│   ├── chat_provider.dart         # Состояние чата (ChangeNotifier)
│   └── settings_provider.dart     # Состояние настроек (ChangeNotifier)
│
├── routes/
│   └── app_router.dart            # Named routes + анимации
│
└── l10n/
    ├── app_en.arb                 # Английские строки
    ├── app_ru.arb                 # Русские строки
    └── app_kk.arb                 # Казахские строки
```

---

## 3.3 Конфигурация

**Файл**: `lib/core/config/app_config.dart`

```dart
class AppConfig {
  // Логика выбора API URL
  static String get apiBaseUrl {
    const customUrl = String.fromEnvironment('API_URL');
    if (customUrl.isNotEmpty) return customUrl;

    if (kIsWeb) return "http://127.0.0.1:8000";

    // Prod: Railway URL
    return "https://demand-forecasting-production-c886.up.railway.app";
  }

  static const int apiTimeoutSeconds = 30;

  static const String appName = 'Forecast AI';
  static const String appVersion = '1.0.0';
}
```

**Зачем централизованная конфигурация?** Меняем одно место — применяется везде. Interceptor, ChatService, ForecastService — все используют `AppConfig.apiBaseUrl`.

---

## 3.4 Модели Данных

```dart
// CurrentUser — Flutter версия объекта User из backend
class CurrentUser {
  final int id;
  final String email;
  final bool isAdmin;
  final String subscriptionPlan;  // "free" | "paid" | "pro"
  final String? fullName;
  final String? avatarUrl;
  final DateTime? createdAt;

  // Доступ к Premium функциям
  bool get canUsePremiumMlModels {
    final p = subscriptionPlan.toLowerCase();
    return p == 'paid' || p == 'pro' || p == 'subscriber';
  }

  factory CurrentUser.fromJson(Map<String, dynamic> json) {
    return CurrentUser(
      id: json['id'],
      email: json['email'],
      isAdmin: json['is_admin'] ?? false,
      subscriptionPlan: json['subscription_plan'] ?? 'free',
      fullName: json['full_name'],
      avatarUrl: json['avatar_url'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
    );
  }
}
```

---

## 3.5 Аутентификация (AuthService)

**Файл**: `lib/services/auth_service.dart`

```dart
class AuthService extends ChangeNotifier {
  bool _isLoading = false;
  bool _isAuthenticated = false;
  CurrentUser? _profile;
  String? _error;

  // Геттеры
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  CurrentUser? get profile => _profile;
  bool get canUsePremiumMlModels => _profile?.canUsePremiumMlModels ?? false;

  // Инициализация (вызывается в main.dart)
  Future<void> init() async {
    _isLoading = true;
    notifyListeners();

    final token = await StorageService.getAccessToken();
    if (token != null && token.isNotEmpty) {
      _isAuthenticated = true;

      // Кэшированный пользователь (быстрый UI без сети)
      final cached = StorageService.getUserData();
      if (cached != null) {
        _profile = CurrentUser.fromStored(cached);
      }

      // Проверка с сервером
      await refreshProfile();
    }

    _isLoading = false;
    notifyListeners();
  }

  // Вход
  Future<AuthResult> login(String email, String password) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await ApiClient().post<Map<String, dynamic>>(
        '/auth/login',
        data: {'email': email, 'password': password},
      );

      final accessToken = response['access_token'];
      final refreshToken = response['refresh_token'];

      // Безопасно сохранить токены
      await StorageService.saveTokens(
        accessToken: accessToken,
        refreshToken: refreshToken,
      );

      _isAuthenticated = true;
      await refreshProfile();  // Загрузить профиль

      return AuthResult.success(accessToken: accessToken);
    } catch (e) {
      return AuthResult.failure(e.toString());
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Обновление профиля
  Future<void> refreshProfile() async {
    try {
      final data = await ApiClient().get<Map<String, dynamic>>('/auth/me');
      _profile = CurrentUser.fromJson(data);
      await StorageService.saveUserData(_profile!.toStorageMap());
      notifyListeners();
    } catch (e) {
      debugPrint('Profile refresh error: $e');
    }
  }

  // Выход
  Future<void> logout() async {
    await StorageService.clearAll();
    _isAuthenticated = false;
    _profile = null;
    notifyListeners();
  }
}
```

---

## 3.6 API Клиент (Dio)

**Файл**: `lib/services/api/api_client.dart`

```dart
// Singleton pattern
class ApiClient {
  static ApiClient? _instance;
  late final Dio _dio;

  factory ApiClient() {
    _instance ??= ApiClient._internal();
    return _instance!;
  }

  ApiClient._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: Duration(seconds: AppConfig.apiTimeoutSeconds),
      receiveTimeout: Duration(seconds: AppConfig.apiTimeoutSeconds),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    _dio.interceptors.addAll([
      AuthInterceptor(),    // Добавление токена
      LoggingInterceptor(), // Debug логирование
      RetryInterceptor(),   // Повтор при ошибке сети
    ]);
  }
}
```

**Файл**: `lib/services/api/api_interceptor.dart`

```dart
// 1. AuthInterceptor — добавляет токен ко всем запросам
class AuthInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, handler) async {
    final token = await StorageService.getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, handler) async {
    if (err.response?.statusCode == 401) {
      // Обновить токен
      final refreshed = await _refreshToken();
      if (refreshed) {
        // Повторить запрос
        final token = await StorageService.getAccessToken();
        err.requestOptions.headers['Authorization'] = 'Bearer $token';
        final response = await Dio().fetch(err.requestOptions);
        return handler.resolve(response);
      }
      // Если не удалось — выйти
      await StorageService.clearTokens();
    }
    handler.next(err);
  }

  Future<bool> _refreshToken() async {
    final refreshToken = await StorageService.getRefreshToken();
    if (refreshToken == null) return false;

    try {
      final response = await Dio().post(
        '${AppConfig.apiBaseUrl}/auth/refresh',
        data: {'refresh_token': refreshToken},
      );
      if (response.statusCode == 200) {
        await StorageService.saveTokens(
          accessToken: response.data['access_token'],
          refreshToken: response.data['refresh_token'],
        );
        return true;
      }
    } catch (_) {}
    return false;
  }
}

// 2. RetryInterceptor — повтор при ошибке сети
class RetryInterceptor extends Interceptor {
  final int maxRetries = 3;

  @override
  void onError(DioException err, handler) async {
    final retryCount = err.requestOptions.extra['retryCount'] ?? 0;

    if (_shouldRetry(err) && retryCount < maxRetries) {
      await Future.delayed(Duration(seconds: retryCount + 1));
      err.requestOptions.extra['retryCount'] = retryCount + 1;

      try {
        final response = await Dio().fetch(err.requestOptions);
        return handler.resolve(response);
      } catch (_) {}
    }
    handler.next(err);
  }

  bool _shouldRetry(DioException err) =>
    err.type == DioExceptionType.connectionTimeout ||
    err.type == DioExceptionType.connectionError;
}
```

---

## 3.7 Управление Состоянием (Provider Pattern)

```dart
// main.dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final authService = AuthService();
  await authService.init();  // Проверить токен, загрузить профиль

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: authService),
        ChangeNotifierProvider(create: (_) => ChatProvider()),
        ChangeNotifierProvider(create: (_) => SettingsProvider()),
      ],
      child: const MyApp(),
    ),
  );
}

// Использование в Widget
class ProfileScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // context.watch — rebuild при изменении состояния
    final auth = context.watch<AuthService>();
    final user = auth.profile;

    return Text(user?.fullName ?? 'Имя не указано');
  }
}

class LoginButton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // context.read — без rebuild, только одноразовое чтение
    final auth = context.read<AuthService>();

    return ElevatedButton(
      onPressed: () => auth.login(email, password),
      child: Text('Войти'),
    );
  }
}
```

**Почему Provider, а не BLoC?** BLoC — сложный, использует Streams. Provider — на основе ChangeNotifier, официальная рекомендация Flutter. Достаточно для масштаба проекта.

---

## 3.8 Маршрутизация

**Файл**: `lib/routes/app_router.dart`

```dart
class AppRoutes {
  static const splash       = '/';
  static const welcome      = '/welcome';
  static const login        = '/login';
  static const main         = '/main';    // → ChatHomeScreen (без вкладок)
  static const profile      = '/profile';
  static const subscription = '/subscription';
  static const settings     = '/settings';
}

class AppRouter {
  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case AppRoutes.splash:
        return _fade(const SplashScreen());
      case AppRoutes.welcome:
        return _fade(const WelcomeScreen());
      case AppRoutes.login:
        return _slide(const LoginScreen());
      case AppRoutes.main:
        return _fade(const ChatHomeScreen());  // Главный экран
      case AppRoutes.profile:
        return _slide(const ProfileScreen());
      case AppRoutes.subscription:
        return _slide(const SubscriptionScreen());
      default:
        return _fade(const WelcomeScreen());
    }
  }

  // Fade анимация
  static Route _fade(Widget page) => PageRouteBuilder(
    pageBuilder: (_, __, ___) => page,
    transitionsBuilder: (_, anim, __, child) =>
        FadeTransition(opacity: anim, child: child),
  );

  // Slide анимация (справа налево)
  static Route _slide(Widget page) => PageRouteBuilder(
    pageBuilder: (_, __, ___) => page,
    transitionsBuilder: (_, anim, __, child) => SlideTransition(
      position: Tween(begin: Offset(1, 0), end: Offset.zero).animate(anim),
      child: child,
    ),
  );
}
```

---

## 3.9 Локализация

```dart
// Все строки в .arb файлах
// lib/l10n/app_ru.arb
{
  "appTitle": "Forecast AI",
  "chatNewChat": "Новый чат",
  "chatSearchHint": "Поиск чата...",
  "settingsSubscriptionButton": "Подписка",
  "@appTitle": { "description": "App title" }
}

// Использование
final l10n = AppLocalizations.of(context)
    ?? lookupAppLocalizations(const Locale('en'));  // null-safe fallback

Text(l10n.appTitle)   // → "Forecast AI"
```

**Почему `?? lookupAppLocalizations`?** При смене языка `MaterialApp` перестраивается. В этот момент `AppLocalizations.of(context)` может вернуть `null`. Без fallback — app крашится.

---

# ОБЩАЯ АРХИТЕКТУРА

## Full Stack Диаграмма

```
┌─────────────────────────────────────────────────────────────────────┐
│                     КЛИЕНТСКИЙ УРОВЕНЬ                              │
│                                                                      │
│  ┌──────────────────┐          ┌──────────────────────────────────┐  │
│  │  Flutter Mobile  │          │     React Frontend (Vercel)      │  │
│  │                  │          │                                  │  │
│  │  • Provider      │          │  • Context API (AuthContext)     │  │
│  │  • Dio + JWT     │          │  • Axios + JWT                   │  │
│  │  • fl_chart      │          │  • Recharts + Three.js           │  │
│  │  • SecureStorage │          │  • i18next (KK/RU/EN)            │  │
│  └────────┬─────────┘          └──────────────┬───────────────────┘  │
└───────────┼────────────────────────────────────┼─────────────────────┘
            │ HTTPS + JWT Bearer                  │ HTTPS + JWT Bearer
            ▼                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Railway)                          │
│                                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────────┐ │
│  │  Auth Layer │  │  API Routes  │  │       Services Layer         │ │
│  │             │  │              │  │                              │ │
│  │  JWT tokens │  │  /auth       │  │  ai_chat_service.py          │ │
│  │  bcrypt     │  │  /chat       │  │  model_service.py            │ │
│  │  rate limit │  │  /forecast   │  │  forecast_service.py         │ │
│  │  Google OAuth  │  /analytics  │  │  kz_market_service.py        │ │
│  └─────────────┘  │  /kz        │  │  intent_classifier.py        │ │
│                   │  /reports    │  │  + 18 других сервисов        │ │
│                   └──────────────┘  └─────────────────────────────┘ │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    ML Pipeline                                  │ │
│  │                                                                 │ │
│  │  Free:  Random Forest ──────→ прогноз 7 дней                    │ │
│  │  Pro:   LightGBM + XGBoost → прогноз 30 дней                    │ │
│  │                                                                 │ │
│  │  Features: date lags, rolling means, cyclical encoding,         │ │
│  │            one-hot categories, competitor pricing               │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                          │                                           │
│              ┌───────────┴────────────┐                              │
│              │                        │                              │
│         OpenAI GPT-4o           PostgreSQL (Neon)                    │
│         (ответы AI чата)        (пользователи, история)              │
└─────────────────────────────────────────────────────────────────────┘
```

## Поток Аутентификации (Все Платформы)

```
Регистрация (Email Verification):
  Client → POST /auth/send-code(email)
  Server → 6-значный код → Email
  Client → POST /auth/verify-code(email, code)
  Client → POST /auth/complete-registration(email, code, password)
  Server → bcrypt.hash(password) → Создать User → Пара JWT
  Client → Сохранить access_token (24ч) + refresh_token (7д)

Вход:
  Client → POST /auth/login(email, password)
  Server → bcrypt.verify → Пара JWT
  Client → Сохранить токены

Обновление токена (авто):
  Client → Получил 401 Unauthorized
  Client → POST /auth/refresh(refresh_token)
  Server → Новый access_token
  Client → Повторить запрос

Google OAuth:
  Client → Получить Google ID Token
  Client → POST /auth/google(credential)
  Server → google.verify → User UPSERT → Пара JWT
```

---

# ОЖИДАЕМЫЕ ВОПРОСЫ НА ЗАЩИТЕ

## Общие Вопросы

**"Какова цель проекта?"**
Система AI-чат + ML-прогноз для малого и среднего бизнеса на казахстанском рынке для прогнозирования спроса на товары. Пользователь задаёт вопрос на казахском/русском — AI отвечает и предлагает прогноз на основе данных.

**"Почему сделали и мобайл, и веб?"**
Веб — для широкого Dashboard, таблиц, отчётов. Мобайл — для быстрого AI чата в полевых условиях (магазин, склад). Один backend — используют оба.

## Backend

**"Почему выбрали FastAPI?"**
- В 2–3 раза быстрее Django или Flask (поддержка async)
- Pydantic validation — автоматическая проверка типов
- Автогенерация Swagger UI — удобно для команды frontend
- Нативная поддержка async/await

**"Как обучали ML модели?"**
Использовали датасет Amazon e-commerce (500K+ записей). Feature engineering: временные лаги, скользящие средние, циклическое кодирование. Pipeline: ColumnTransformer (OneHot + Standard Scale) + модель.

**"Какой R2 score?"**
Random Forest: ~0.75–0.82. LightGBM: ~0.83–0.89. XGBoost: ~0.82–0.88. Для рыночных товаров 0.75+ — хороший результат.

**"Зачем rate limiting?"**
Защита от brute-force атак. `/auth/login` — 5 раз/мин. При превышении возвращается 429.

## Frontend

**"Почему React 19?"**
Новейшая версия. Server Components, Concurrent Mode. Хорошая интеграция с Vercel.

**"Как работает i18next?"**
Файлы `i18n/locales/kk.json`, `ru.json`, `en.json`. Хук `useTranslation()`, функция `t('key')`. Автоопределение из URL параметра или языка браузера.

**"Зачем нужен AuthGuard?"**
Проверка токена занимает 200–500мс. В это время `isAuthenticated=false`. Без AuthGuard — пользователь попадёт на /login и тут же улетит на /chat (flash). Guard показывает loader пока проверка не завершится.

## Mobile (Flutter)

**"Почему Flutter, а не React Native?"**
Flutter — Dart компилируется в нативный код. React Native использует JS bridge (медленно). Flutter Skia/Impeller engine — рисует сам (не native widgets) → 60/120fps плавная анимация.

**"Разница между Provider и BLoC?"**
BLoC — на основе Stream, паттерн event-state. Provider — на основе ChangeNotifier, проще. Для данного проекта Provider — достаточный уровень сложности.

**"Как хранится JWT в мобайл?"**
`flutter_secure_storage` — iOS: Keychain, Android: Keystore. Зашифровано, другое приложение не может прочитать. Безопаснее чем SharedPreferences.

**"Как работает SSE streaming в мобайл?"**
Dio `ResponseType.stream` → `Stream<Uint8List>`. Декод → парсинг SSE формата → обновление UI через `setState()`.

---

*Forecast AI — Backend: FastAPI/Python + Railway | Frontend: React 19/Vite + Vercel | Mobile: Flutter + iOS/Android*