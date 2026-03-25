# Deployment Guide

## Quick Deploy

### Backend → Railway

1. **Создайте GitHub репозиторий:**
```bash
cd /Users/nur52k/Desktop/demand-forecasting-project
git init
git add .
git commit -m "Initial commit"
gh repo create demand-forecasting --public --source=. --push
```

2. **Деплой на Railway:**
   - Зайдите на [railway.app](https://railway.app)
   - "New Project" → "Deploy from GitHub repo"
   - Выберите репозиторий
   - Выберите папку `back` как root directory
   - Добавьте Environment Variables:
     - `OPENAI_API_KEY` = ваш ключ
     - `JWT_SECRET` = случайная строка
     - `FRONTEND_URL` = URL вашего Vercel (добавите позже)

3. **Скопируйте URL бэкенда** (например: `https://demand-forecasting-back.up.railway.app`)

### Frontend → Vercel

1. **Деплой на Vercel:**
   - Зайдите на [vercel.com](https://vercel.com)
   - "New Project" → Import from GitHub
   - Выберите репозиторий
   - Root Directory: `frontend-admin`
   - Environment Variables:
     - `VITE_API_URL` = URL вашего Railway бэкенда

2. **Обновите CORS на Railway:**
   - Добавьте `FRONTEND_URL` = URL вашего Vercel

---

## Alternative: Render (Free)

### Backend
```bash
# На render.com создайте Web Service
# Build Command: pip install -r requirements.txt
# Start Command: uvicorn backend:app --host 0.0.0.0 --port $PORT
```

### Frontend
```bash
# Static Site на Render
# Build Command: npm run build
# Publish Directory: dist
```

---

## Local Testing

```bash
# Backend
cd back
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend:app --reload

# Frontend
cd frontend-admin
npm install
npm run dev
```

---

## Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=sk-...
JWT_SECRET=random-secret-key
FRONTEND_URL=https://your-app.vercel.app
```

### Frontend (.env)
```
VITE_API_URL=https://your-api.railway.app
```