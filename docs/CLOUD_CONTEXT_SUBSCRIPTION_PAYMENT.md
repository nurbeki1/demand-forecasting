# Контекст для Claude / Cloud: жазылым, демо төлем, конфиг

Бұл құжат репозиторийдегі **жазылым (pricing)**, **демо төлем беті**, **mock API**, **фронт маршруттары** және **API конфигі** туралы бір жерден түсініктеме береді. Басқа сессияда немесе Cloud Agentта контекст ретінде осы файлды қосса болғаны.

---

## 1. Негізгі мақсат

- Тарифтер бетінде үш карточка (Starter / Pro / Enterprise): кеңейтілген bulletтар, tagline, footnote, салыстыру дәптерінің жолы.
- **Көрме үшін төлем**: нақты банк / Stripe жоқ; форма толтырылады → JWT-пен API шақыру → PostgreSQL/SQLite-та `users.subscription_plan = paid`.
- Сәтті жауаптан кейін UI **10 секунд** кернелі редирект: қарапайым user → `/user`, admin → `/admin`.
- Жазылымнан **Pro** немесе **Enterprise** басқанда: кірген пайдаланушы төлем бетіне; қонақ → `/login` + қайтару (`state.from`).
- Premium тарифтегі пайдаланушылар үшін чатта RF-тен бөлек **LightGBM / XGBoost** қолжетімділігі бекендте бұрыннан түйме бойынша шектеледі (`paid`, `pro`, `subscriber`).

---

## 2. Backend (Python / FastAPI, қалта `back/`)

### 2.1 Дерекқор моделі

- **`app/models.py`**, кесте **`users`**, өріс **`subscription_plan`** (`VARCHAR`, әдепкі `'free'`).
- Mock төлем соңында мәні **`paid`** болып жазады.

### 2.2 Ортақ демо логика

- Файл: **`app/demo_billing.py`**
- Функция: **`apply_mock_subscription(db, user, data: MockSubscribeRequest) -> UserResponse`**
  - `data.plan` қазіргі күйде тек аудит үшін (`pro` | `enterprise`).
  - `user.subscription_plan = "paid"`, commit, `UserResponse` қайтару.

### 2.3 Схема сұранысы

- Файл: **`app/schemas.py`**
- **`MockSubscribeRequest`**: өріс **`plan`** (pattern/string шегі — pydantic моделі бойынша).

### 2.4 Эндпоинтерлер (екі жол да бірдей семантика)

| Әдіс | Path | Auth | Денесі |
|------|------|------|--------|
| POST | `/subscription/mock-checkout` | `Authorization: Bearer <JWT>` | `{"plan":"pro"\|"enterprise"}` |
| POST | `/auth/mock-subscribe` | дәл сол | дәл сол |

- **`/subscription/mock-checkout`** тікелей **`backend.py`** ішінде `@app.post` арқылы тіркелген (негізгі қолданба файлынан көрінеді).
- **`/auth/mock-subscribe`** — **`app/auth_routes.py`** роутері (`prefix=/auth`), ішінде `apply_mock_subscription` шақырады.

### 2.5 Басқа файлдар

- **`backend.py`**: миграциялар (`subscription_plan` бағанасын қосу т.б.), `include_router(auth_router)`, содан кейін **`subscription_mock_checkout`** анықтамасы.
- **`app/subscription_utils.py`**: `allowed_ml_models_for_user`, `enforce_chat_model_type` — жазылымға қарап модель жинағын шектеу.

---

## 3. Frontend (React / Vite, қалта `frontend-admin/`)

### 3.1 Конфиг API

- Файл: **`src/config.js`**
- Экспорт: **`API_URL`**
- Логика:
  - Қысқа қайту: соңғы `/` алынады.
  - Егер жол **`…/api`** менен аяқталса, `/api` кесіп тасталады (қате `…/api/auth/…` болдырмау үшін).
  - **`import.meta.env.DEV`** және **`VITE_API_URL` бос** болса → әдепкі **`http://127.0.0.1:8000`**.
  - Production build, **`VITE_API_URL` жоқ** → кодтағы Railway әдепкі домені.

### 3.2 Маршруттар

- Файл: **`src/App.jsx`**
  - **`/subscriptions`** — `SubscriptionPage` (қонақ + кірген).
  - **`/subscriptions/payment`** — `SubscriptionPaymentPage`, **`AuthenticatedRoute`** арқылы: тек authenticated; әйтпесе **`Navigate`** → `/login`, **`state.from`** = ағымдағы path + query.
  - **`AuthenticatedRoute`**: admin дерлік төлем бетіне кіре алады; редирект төлемнен кейін рөлге байланысты.

### 3.3 Негізгі беттер

- **`src/pages/SubscriptionPage.jsx`**: тарифтер торы; Pro/Enterprise **`goCheckout(plan)`**; Starter **`openAuth`**.
- **`src/pages/SubscriptionPaymentPage.jsx`**:
  - Query: **`plan=pro`** немесе **`enterprise`**.
  - Fetch реттігі: бірінші **`POST ${API_URL}/subscription/mock-checkout`**, статус **404** болса → **`POST ${API_URL}/auth/mock-subscribe`**.
  - Сәтті болса **`refreshUser()`** (`AuthContext`), содан кейін countdown және **`navigate`**.
  - **404** үшін арнайы i18n кілті **`payment.notFoundHint`**.

### 3.4 Форма тексерулері (төлем)

- **Карта иесі**: uppercase; `\p{L}`, пробел, `-`, `'`; max **26** символ.
- **Карта нөмірі**: тек сандар; **16** цифраға дейін; топтау `XXXX XXXX XXXX XXXX`.
- **Мерзім**: **`MM/YY`**; тек сандар; max **5** көрініс символы.
- **CVV**: тек сандар; max **4**.
- Карта деректері серверге **жіберілмейді** — тек клиенттік форма және mock жазылым API.

### 3.5 Логиннен кейін қайту

- **`src/utils/postAuthRedirect.js`**: **`postAuthPath(isAdmin, fromState)`** — `from` `/`-ден басталса сол жолға.
- **`AuthModal.jsx`** (Login / Register соңы), **`LoginPage.jsx`** (Google): **`postAuthPath`** қолданылады.

### 3.6 Контекст

- **`src/context/AuthContext.jsx`**: экспорт **`refreshUser`** (= **`checkAuth`**) — төлемнен кейін `/auth/me` қайта алу.

### 3.7 Стильдер

- **`src/styles/subscription.css`**: тариф карточкалары (`subscription-card__tagline`, `__footnote`), төлем UI (`subscription-pay-*`).

### 3.8 i18n

- **`src/i18n/en.json`**, **`kk.json`**, **`ru.json`**:
  - **`subscription.*`** — тариф мәтіндері, **`compareNote`**, т.б.
  - **`payment.*`** — төлем бетінің барлық жолдары, соның ішінде **`notFoundHint`**.

---

## 4. Flutter қолданба (`prodbot_ai/`)

Бұл құжаттағы негізгі өзгерістер **frontend-admin** пен **back** үшін сипатталған. Мобильді жазылым / төлем UI синхрондау үшін Flutter қай файлдарды қолданатынын кодқа қарап бөлек тексеру керек.

---

## 5. Әзірлеуші үшін қысқа checklist

1. Бекендті іске қосу (мысалы `uvicorn backend:app`, порт **8000**).
2. Әкімші веб: `frontend-admin` ішінде `npm run dev`; **`VITE_API_URL` қоймағанда** әдепкі жергілікті **`127.0.0.1:8000`**.
3. Production: соңғы **`back`** образын деплойлау; фронт build үшін **`VITE_API_URL`** дұрыс түбірге көрсетілген болсын (**`/api` қоспаған жөн**, жолдар `/auth/...`, `/subscription/...`, `/chat` түбірден басталады).

---

## 6. Файлдардың жылдам индексі

| Құрбы | Файл |
|------|------|
| DB логика + модель | `back/app/models.py`, миграциялар `back/backend.py` ішінде |
| Mock жазылым | `back/app/demo_billing.py` |
| Auth роут | `back/app/auth_routes.py` (`POST /auth/mock-subscribe`) |
| Негізгі app роут | `back/backend.py` (`POST /subscription/mock-checkout`) |
| Конфиг | `frontend-admin/src/config.js` |
| Төлем UX | `frontend-admin/src/pages/SubscriptionPaymentPage.jsx` |
| Тарифтер UX | `frontend-admin/src/pages/SubscriptionPage.jsx` |
| Маршруттар | `frontend-admin/src/App.jsx` |
| Стильдер | `frontend-admin/src/styles/subscription.css` |
| Аударма | `frontend-admin/src/i18n/*.json` |

---

*Соңғы жаңарту: келесі функционал қосылған кезде осы құжатты бір жолмен синхрондап тұру пайдалы.*
