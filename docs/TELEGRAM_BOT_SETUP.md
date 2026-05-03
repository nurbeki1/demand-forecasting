# Telegram қолдау боты — толық баптау нұсқаулығы

Құжат мақсаты: **ForecastDemandAiBot** (немесе өз ботыңыз) және вебтегі Enterprise «хабарласу» дұрыс жұмыс істеуі үшін не қосу керек — айнымалылар, Telegram әрекеттері, прод орта.

---

## 1. Архитектура (қысқа)

| Компонент | Рөлі |
|-----------|------|
| **Backend** (`back`) | `TELEGRAM_BOT_TOKEN` арқылы polling; хабарламаларды өңдейді; қолданушыдан келген **Отзыв / Запрос** тикеттерін ішкі топқа жібереді; топтағы оператордың **reply** жауабын қолданушыға қайта жібереді. |
| **Frontend** (`frontend-admin`) | Жазылым бетінде Enterprise батырмасы `VITE_TELEGRAM_SUPPORT_URL` бойынша Telegramды ашады. |
| **Ішкі топ** (supergroup) | Операторлар тикетті көріп, бот хабарламасына reply жасайды. |

Маңызды: токенді **Git-ке, чатқа, скриншотқа салмаңыз** — тек `.env` / Railway / Vercel Variables.

---

## 2. Telegramта не істеу керек

### 2.1. Бот жасау (@BotFather)

1. Telegramда **@BotFather** → `/newbot` немесе бар ботты пайдалану.
2. **HTTP API token** алыңыз — ол backend үшін `TELEGRAM_BOT_TOKEN`.
3. Токен әлеуметтік желіде тұрса → BotFather **жаңа токен** шығарыңыз (`/revoke` немесе Token бөлімі).

### 2.2. Қолдау тобы (міндетті — адам оператор арқылы жауап үшін)

1. Telegramда **топ** немесе **супергруппа** құрыңыз (ішкі қолдау үшін).
2. Оған **ботты админ емес, қарапайым мүше ретінде** қосыңыз жеткілікті (хабарламаларды оқу үшін топ параметрлерінде боттың құқығын тексеріңіз).
3. Топтың **chat id** алыңыз — форматы әдетте `-100…`:
   - топқа `@RawDataBot` немесе `@getidsbot` сияқты бот қосып хабарламадағы id қараңыз;
   - немесе өз сервер логынан бір реттік хабарламамен алу.
4. Бұл мәнді орнатыңыз: **`TELEGRAM_SUPPORT_GROUP_ID=-100xxxxxxxxxx`**

Егер топ ID қойылмаса: қолданушы Отзыв/Запрос жіберседі, бот хабарлайды — «қолдау топы бапталмаған».

### 2.3. Операторлар (міндетті емес)

- **`TELEGRAM_SUPPORT_OPERATOR_IDS`** — тек көрсетілген Telegram **user id** жауаптары қолданушыға жіберіледі.
- Бос қалдырсаңыз: топтағы кез келген мүшенің бот тикетіне **reply** жасауы қолданушыға келеді.

Оператор жауабы: топтағы **бот жіберген тикет хабарламасына reply** (жаңа үшінші хабарлама емес).

---

## 3. Backend айнымалылары (`back/.env` немесе Railway Variables)

Бот пен API үшін кем дегенде мына жолдар маңызды.

### Міндетті (өнім жұмысы үшін жалпы)

| Айнымалы | Сипаттама | Мысал форматы |
|----------|-----------|----------------|
| `JWT_SECRET_KEY` | JWT үшін криптокіл. **Кемінде 32 таңба**, кездейсоқ. | `openssl rand -base64 48` |
| `OPENAI_API_KEY` | `/forecast`, `/chat`, AI командалары үшін. | `sk-…` |

### Telegram бот үшін

| Айнымалы | Міндетті? | Сипаттама |
|----------|-----------|-----------|
| `TELEGRAM_BOT_TOKEN` | Иә (бот іске қосылуы үшін) | @BotFather token |
| `TELEGRAM_SUPPORT_GROUP_ID` | Жоғары ұсынылады | Supergroup id, мысалы `-1001234567890` |
| `TELEGRAM_SUPPORT_OPERATOR_IDS` | Жоқ | `111111111,222222222` (үнді белгімен) |

### Қолдау мәтіндері / CORS үшін ұсынылады

| Айнымалы | Сипаттама |
|----------|-----------|
| `FRONTEND_URL` | Admin frontend URL (соңында `/` жоқ). Бот `/start`, `/help` мәтіндерінде сілтеме үшін. |
| `SUPPORT_EMAIL` | Пошта көрсеткісі (міндетті емес). |

### Толық үлгі блок (мәндерді өзіңізбен ауыстырыңыз)

```env
# --- жалпы backend ---
JWT_SECRET_KEY=өзіңіздің_узын_кездейсоқ_жол
OPENAI_API_KEY=sk-...

FRONTEND_URL=https://sizdin-admin.vercel.app
# SUPPORT_EMAIL=support@example.com

# --- Telegram ---
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_SUPPORT_GROUP_ID=-1001234567890
# TELEGRAM_SUPPORT_OPERATOR_IDS=111111111,222222222
```

Бот **backend процесімен бірге** іске қосылады (`startup` ішінде polling). Railwayда бір сервисте орналасқан `back` үшін осы айнымалыларды **Railway → Variables** жазып, redeploy жасаңыз.

---

## 4. Frontend айнымалылары (`frontend-admin/.env` немесе Vercel Build Env)

`VITE_*` тек **build** кезінде енеді — өзгерткен соң жаңа деплой керек.

| Айнымалы | Сипаттама |
|----------|-----------|
| `VITE_API_URL` | Backend түбірі: `https://xxx.up.railway.app` (соңында `/` жоқ, `/api` жоқ). |
| `VITE_TELEGRAM_SUPPORT_URL` | Enterprise батырмасы ашатын сілтеме. Толық URL немесе `@бот`. |

### Мысалдар

```env
VITE_API_URL=https://demand-forecasting-production-c886.up.railway.app
VITE_TELEGRAM_SUPPORT_URL=https://t.me/ForecastDemandAiBot
```

Қолдау экранын бірден `/start` үшін арнайы жеткізгіңіз келсе:

```env
VITE_TELEGRAM_SUPPORT_URL=https://t.me/ForecastDemandAiBot?start=support
```

Егер `VITE_TELEGRAM_SUPPORT_URL` бос болса: жазылым бетінде Enterprise басқанда **toast** шығады — «сілтеме бапталмаған».

---

## 5. Қолданушы және оператор ағымы

1. Вебтен Enterprise → Telegram ашылады (`VITE_TELEGRAM_SUPPORT_URL`).
2. `/start` → **Отзыв** немесе **Запрос** түймесі → қолданушы мәселесін жібереді.
3. Бот қолданушыға қысқа растау береді; AI автожауап бермейді (осы ағын үшін).
4. Топта оператор тикетке **reply** → жауап сол қолданушының чатына көшіріліп жіберіледі.

Қосымша бот командалары (AI қолданылады): `/forecast`, `/price`, `/report`, `/alerts`, `/cities`, `/help`.

---

## 6. Тексеру чек-листі

- [ ] Backend `.env` немесе Railway: `TELEGRAM_BOT_TOKEN` орнатылған.
- [ ] Бот топқа қосылған; `TELEGRAM_SUPPORT_GROUP_ID` дұрыс.
- [ ] Railway логында Telegram polling қатесі жоқ (не болмаса `[Telegram Bot]` хабарламасы).
- [ ] Frontend build: `VITE_TELEGRAM_SUPPORT_URL` және `VITE_API_URL` орнатылған.
- [ ] Топта тест тикетіне reply → жауап жеке чатқа келеді.

---

## 7. Белгілі шектеулер

- **Тикет ↔ қолданушы** байланысы қазір процесс жадында — сервер қайта іске қосылғаннан кейін ескі хабарламаға reply картасы тазаланады (ұзақ мерзімде Redis/DB қосуға болады).
- Railwayда **бірнеше реплика** болса, бірнеше процесс бір TOKEN бойынша polling жасауыма түсіруі мүмкін — Telegram үшін әдетте **бір инстанс** ұстаңыз немесе webhook архитектурасына өтіңіз.

---

## 8. Қатысты файлдар (репозиторийде)

| Файл | Мазмұны |
|------|---------|
| `back/services/telegram_bot_service.py` | Бот логикасы, relay, reply |
| `back/backend.py` | `startup` / `shutdown` ішінде бот іске қосу |
| `frontend-admin/src/config.js` | `TELEGRAM_SUPPORT_URL` құрастыру |
| `frontend-admin/src/pages/SubscriptionPage.jsx` | Enterprise → Telegram |
| `back/.env.example`, `frontend-admin/.env.example` | Қысқа түсініктемелер |

---

*Соңғы жаңарту: құжат репозиторийдегі ағымдағы кодқа сәйкес келтіру үшін қолданушы сұрауы бойынша қосылды.*
