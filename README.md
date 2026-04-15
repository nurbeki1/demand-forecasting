# Demand Forecasting System

Платформа для прогнозирования спроса с AI-ассистентом, аналитикой казахстанского рынка и мультиплатформенным доступом.

---

## Содержание

- [Обзор проекта](#обзор-проекта)
- [Архитектура](#архитектура)
- [Технологический стек](#технологический-стек)
- [Структура проекта](#структура-проекта)
- [Функциональность](#функциональность)
- [API Reference](#api-reference)
- [База данных](#база-данных)
- [Аутентификация](#аутентификация)
- [Переменные окружения](#переменные-окружения)
- [Локальная разработка](#локальная-разработка)
- [Деплой](#деплой)
- [Известные проблемы](#известные-проблемы)

---

## Обзор проекта

Demand Forecasting System — full-stack SaaS приложение для предсказания спроса на товары. Система использует ML-модели на основе scikit-learn, интегрирует OpenAI GPT для AI-чата, и предоставляет специализированную аналитику для казахстанского рынка.

**Целевая аудитория:** Предприниматели, e-commerce компании, аналитики рынка Казахстана.

---

## Архитектура

```
┌─────────────────────────────────────────────────────┐
│                   Клиентский слой                   │
├──────────────────────┬──────────────────────────────┤
│  React Admin (Vite)  │    Flutter Mobile App        │
│  Vercel Deploy       │    iOS / Android / Web       │
└──────────┬───────────┴──────────────────────────────┘
           │ HTTPS REST API
           ▼
┌──────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                   │
├──────────────────────────────────────────────────────┤
│  Auth · Forecasting · AI Chat · Analytics · KZ Market│
├──────────────────────────────────────────────────────┤
│  ML Models (scikit-learn) · OpenAI · Telegram Bot    │
├──────────────────────────────────────────────────────┤
│          PostgreSQL (Neon) / SQLite (dev)            │
└──────────────────────────────────────────────────────┘
           │ Docker Container
           │ Railway Deployment
```

---

## Технологический стек

### Backend
| Технология | Версия | Назначение |
|---|---|---|
| Python | 3.11 | Основной язык |
| FastAPI | 0.126.0 | Web фреймворк |
| Uvicorn | 0.34.0 | ASGI сервер |
| SQLAlchemy | 2.0.46 | ORM |
| scikit-learn | 1.6.1 | ML модели |
| pandas | 2.3.3 | Обработка данных |
| numpy | 2.0.2 | Числовые вычисления |
| OpenAI SDK | 2.14.0 | AI чат |
| python-jose | 3.5.0 | JWT токены |
| passlib + bcrypt | 1.7.4 / 4.0.1 | Хэширование паролей |
| slowapi | 0.1.9 | Rate limiting |
| psycopg2-binary | 2.9.9 | PostgreSQL драйвер |
| resend | 2.0.0 | Email сервис |
| google-auth | 2.29.0 | Google OAuth |
| python-telegram-bot | 20.7 | Telegram Bot |
| openpyxl | 3.1.2 | Excel экспорт |

### Frontend (Web Admin)
| Технология | Версия | Назначение |
|---|---|---|
| React | 19.2.0 | UI фреймворк |
| Vite | 7.2.4 | Build инструмент |
| React Router | 7.13.0 | Маршрутизация |
| Chart.js | 4.5.1 | Графики |
| Recharts | 3.8.0 | Дополнительные графики |
| Three.js | 0.183.2 | 3D графика |
| Framer Motion | 12.38.0 | Анимации |
| GSAP | 3.14.2 | Анимации |
| i18next | 26.0.3 | Интернационализация |
| Sonner | 2.0.7 | Toast уведомления |

### Mobile
| Технология | Назначение |
|---|---|
| Flutter (Dart) | Мультиплатформенное приложение |
| fl_chart | Графики |
| provider | State management |
| dio | HTTP клиент |

### Инфраструктура
| Сервис | Назначение |
|---|---|
| Railway | Хостинг backend (Docker) |
| Vercel | Хостинг frontend |
| Neon | PostgreSQL база данных |
| GitHub Actions | CI/CD |

---

## Структура проекта

```
demand-forecasting-project/
├── back/                          # Backend (Python/FastAPI)
│   ├── app/
│   │   ├── auth_routes.py         # Маршруты аутентификации
│   │   ├── config.py              # Настройки и валидация
│   │   ├── database.py            # Подключение к БД
│   │   ├── deps.py                # Dependency injection
│   │   ├── email_service.py       # Email верификация
│   │   ├── models.py              # SQLAlchemy модели
│   │   ├── rate_limiter.py        # Rate limiting
│   │   ├── report_routes.py       # Маршруты отчётов
│   │   ├── schemas.py             # Pydantic схемы
│   │   ├── security.py            # JWT, хэширование
│   │   ├── settings_routes.py     # Маршруты настроек
│   │   ├── telegram_routes.py     # Telegram маршруты
│   │   ├── user_routes.py         # Маршруты пользователей
│   │   └── routers/dashboard.py   # Dashboard маршруты
│   ├── services/
│   │   ├── ai_chat_service.py     # AI чат (OpenAI)
│   │   ├── alert_service.py       # Бизнес алерты
│   │   ├── amazon_data_service.py # Amazon данные
│   │   ├── forecast_service.py    # Прогнозирование
│   │   ├── insight_service.py     # Инсайты
│   │   ├── kz_market_service.py   # Казахстанский рынок
│   │   ├── model_service.py       # ML модели
│   │   ├── profit_calculator_service.py
│   │   ├── report_service.py      # Генерация отчётов
│   │   ├── telegram_bot_service.py
│   │   ├── trust_service.py       # Trust score
│   │   └── web_search_service.py  # Веб-поиск (Tavily)
│   ├── data/
│   │   ├── amazon/                # Amazon товары (184MB)
│   │   └── ecommerce/             # E-commerce данные (43MB)
│   ├── backend.py                 # Точка входа
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── railway.json
│   └── create_admin.py
│
├── frontend-admin/                # Web Admin (React)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── UserDashboard.jsx
│   │   │   ├── ChatPage.jsx
│   │   │   ├── TablePage.jsx
│   │   │   ├── UploadPage.jsx
│   │   │   ├── ChartsPage.jsx
│   │   │   ├── ReportsPage.jsx
│   │   │   ├── ForecastComparisonPage.jsx
│   │   │   ├── ModelVisualizationPage.jsx
│   │   │   ├── ExecutiveDashboardPage.jsx
│   │   │   └── UserManagementPage.jsx
│   │   ├── components/
│   │   │   ├── chat/ · charts/ · dashboard/
│   │   │   ├── insights/ · kz/ · landing/
│   │   │   └── layout/ · settings/
│   │   ├── api/
│   │   │   ├── authApi.js · chatApi.js
│   │   │   ├── forecastApi.js · userApi.js
│   │   │   └── settingsApi.js
│   │   ├── i18n/                  # Переводы KZ/RU/EN
│   │   └── config.js              # API URL
│   ├── vercel.json
│   └── vite.config.js
│
├── prodbot_ai/                    # Flutter Mobile App
└── .github/workflows/ci.yml       # CI/CD
```

---

## Функциональность

### 1. Прогнозирование спроса
- ML модели (scikit-learn) обучаются на загружаемых CSV данных
- Визуализация прогноза на интерактивных графиках
- Сравнение нескольких моделей между собой
- Feature importance анализ
- Сценарный анализ ("что если?")

### 2. AI Чат-ассистент
- Интеграция с OpenAI GPT
- Сохранение истории разговоров
- Анализ бизнес-данных через чат
- Веб-поиск через Tavily API для актуальных данных

### 3. Аналитика казахстанского рынка
- Данные по городам и регионам Казахстана
- Анализ конкурентов и ценовых трендов
- Логистические расчёты
- Региональные прогнозы спроса

### 4. Аутентификация и авторизация
- Email + пароль с двухэтапной верификацией кода
- Google OAuth (Sign in with Google)
- JWT access + refresh токены
- Роли пользователей: admin / user
- Rate limiting на все эндпоинты

### 5. Отчёты
- Генерация Excel отчётов
- Executive дашборд со сводкой
- Экспорт данных

### 6. Telegram Бот
- Уведомления через Telegram

### 7. Управление пользователями (Admin)
- Просмотр всех пользователей
- Активация / деактивация аккаунтов
- Назначение ролей

---

## API Reference

### Аутентификация (`/auth`)

| Метод | Путь | Описание | Auth |
|---|---|---|---|
| POST | `/auth/send-code` | Отправить код на email | — |
| POST | `/auth/verify-code` | Проверить код | — |
| POST | `/auth/complete-registration` | Завершить регистрацию | — |
| POST | `/auth/login` | Войти, получить токены | — |
| POST | `/auth/register` | Регистрация (legacy) | — |
| POST | `/auth/refresh` | Обновить access token | — |
| POST | `/auth/google` | Google OAuth | — |
| GET | `/auth/me` | Текущий пользователь | Bearer |

### Прогнозирование

| Метод | Путь | Описание | Auth |
|---|---|---|---|
| GET | `/forecast` | Получить прогноз | Bearer |
| GET | `/products` | Список товаров | Bearer |
| GET | `/history/{product_id}` | История продаж | Bearer |
| POST | `/upload` | Загрузить CSV | Bearer |
| GET | `/models` | Список ML моделей | Bearer |
| POST | `/models/train` | Обучить модель | Bearer |

### Аналитика

| Метод | Путь | Описание | Auth |
|---|---|---|---|
| GET | `/analytics/summary` | Сводная аналитика | Bearer |
| GET | `/analytics/trends` | Тренды | Bearer |
| POST | `/chat` | AI чат | Bearer |

### Казахстанский рынок (`/kz`)

| Метод | Путь | Описание | Auth |
|---|---|---|---|
| GET | `/kz/cities` | Список городов | Bearer |
| GET | `/kz/competitors` | Конкуренты | Bearer |
| GET | `/kz/trends` | Рыночные тренды | Bearer |
| GET | `/kz/logistics` | Логистика | Bearer |

### Управление

| Метод | Путь | Описание | Auth |
|---|---|---|---|
| GET | `/reports` | Список отчётов | Bearer |
| POST | `/reports/generate` | Генерировать отчёт | Bearer |
| GET | `/user/list` | Все пользователи | Admin |
| PUT | `/user/{id}` | Обновить пользователя | Admin |
| GET | `/settings` | Настройки | Bearer |
| PUT | `/settings` | Обновить настройки | Bearer |

> Полная Swagger документация доступна по адресу: `https://your-railway-url/docs`

---

## База данных

### Таблица `users`
| Колонка | Тип | Описание |
|---|---|---|
| id | INTEGER PK | ID |
| email | VARCHAR UNIQUE | Email |
| hashed_password | VARCHAR | Хэш пароля |
| is_active | BOOLEAN | Активен |
| is_admin | BOOLEAN | Администратор |
| is_verified | BOOLEAN | Email подтверждён |
| google_id | VARCHAR UNIQUE | Google OAuth ID |
| full_name | VARCHAR | Полное имя |
| avatar_url | VARCHAR | URL аватара |
| created_at | TIMESTAMP | Дата создания |

### Таблица `user_settings`
| Колонка | Тип | Описание |
|---|---|---|
| id | INTEGER PK | ID |
| user_id | INTEGER FK → users | Пользователь |
| settings_json | TEXT | JSON настройки |
| updated_at | TIMESTAMP | Дата обновления |

### Таблица `verification_codes`
| Колонка | Тип | Описание |
|---|---|---|
| id | INTEGER PK | ID |
| email | VARCHAR | Email |
| code | VARCHAR | 6-значный код |
| created_at | TIMESTAMP | Дата создания |
| expires_at | TIMESTAMP | Срок истечения |
| is_used | BOOLEAN | Использован |

- **Development:** SQLite (`back/app.db`)
- **Production:** PostgreSQL via Neon (`DATABASE_URL`)
- Миграции применяются **автоматически** при каждом старте приложения

---

## Аутентификация

### Флоу регистрации
```
1. POST /auth/send-code              → Email с 6-значным кодом
2. POST /auth/verify-code            → Проверка кода
3. POST /auth/complete-registration  → Создание аккаунта + JWT пара
```

### Флоу входа
```
1. POST /auth/login                  → { access_token, refresh_token, is_admin }
2. Защищённые запросы:               Authorization: Bearer <access_token>
3. POST /auth/refresh                → новая пара токенов
```

### Параметры JWT
| Параметр | Значение по умолчанию | Env var |
|---|---|---|
| Access token | 60 минут | `ACCESS_TOKEN_EXPIRE_MINUTES` |
| Refresh token | 7 дней | `REFRESH_TOKEN_EXPIRE_DAYS` |
| Алгоритм | HS256 | — |

---

## Переменные окружения

### Backend (`back/.env`)

```env
# ОБЯЗАТЕЛЬНО
JWT_SECRET_KEY=your-secret-key-minimum-32-characters-long

# База данных (production)
DATABASE_URL=postgresql://user:password@host/dbname

# AI сервисы
OPENAI_API_KEY=sk-proj-...
TAVILY_API_KEY=tvly-dev-...

# Email
RESEND_API_KEY=re_...

# Google OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com

# Telegram
TELEGRAM_BOT_TOKEN=xxx:xxx

# CORS (дополнительные origins)
FRONTEND_URL=https://your-app.vercel.app
CORS_ORIGINS=https://other-domain.com

# Токены (опционально)
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate limiting (опционально)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_AUTH_PER_MINUTE=5
RATE_LIMIT_CHAT_PER_MINUTE=20
RATE_LIMIT_DEFAULT_PER_MINUTE=100
```

### Frontend (`frontend-admin/.env`)

```env
VITE_API_URL=https://your-railway-app.up.railway.app
VITE_GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
```

---

## Локальная разработка

### Backend

```bash
cd back

# Виртуальное окружение
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# Зависимости
pip install -r requirements.txt

# Создай .env (заполни значения из раздела выше)
cp .env.example .env

# Запуск
uvicorn backend:app --reload --port 8000
```

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend-admin
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

- Frontend: `http://localhost:5173`

### Создание admin пользователя

```bash
cd back
python create_admin.py
```

---

## Деплой

### Backend → Railway

1. Подключи GitHub репозиторий в [Railway](https://railway.app)
2. Укажи root directory: `back/`
3. Добавь все переменные из раздела [Переменные окружения](#переменные-окружения) в Railway → Variables
4. Деплой происходит автоматически при пуше в `main`

**`back/railway.json`:**
```json
{
  "build": { "builder": "DOCKERFILE" },
  "deploy": {
    "startCommand": "sh -c 'uvicorn backend:app --host 0.0.0.0 --port ${PORT:-8000}'",
    "healthcheckPath": "/",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Frontend → Vercel

1. Подключи GitHub репозиторий в [Vercel](https://vercel.com)
2. Root Directory: `frontend-admin`
3. Добавь Environment Variables:
   - `VITE_API_URL` = твой Railway URL (с `https://`)
   - `VITE_GOOGLE_CLIENT_ID` = Google Client ID
4. Деплой при пуше в `main`

### База данных → Neon

1. Создай проект на [neon.tech](https://neon.tech)
2. Скопируй `DATABASE_URL` в Railway Variables
3. Миграции применяются автоматически при старте

---

## Известные проблемы

| Проблема | Файл | Решение |
|---|---|---|
| CI/CD ссылается на `frontend-chat/` (не существует) | `.github/workflows/ci.yml` | Исправить путь на `frontend-admin/` |
| E2E тесты отключены (`if: false`) | `.github/workflows/ci.yml` | Настроить Playwright |
| Мёртвый код в `refresh_token` endpoint | `back/app/auth_routes.py:336` | Удалить unreachable `raise` |
| Минимальное тестовое покрытие (50%) | `ci.yml` | Поднять до 70%+ |
