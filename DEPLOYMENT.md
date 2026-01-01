# Deployment Configuration

This document contains all deployment information for the Quant Trading System.

---

## 🌐 Live URLs

| Service | URL |
|---------|-----|
| **Frontend** | https://nutquantsystem.vercel.app |
| **Backend API** | https://quant-trading-api-production.up.railway.app |
| **API Documentation** | https://quant-trading-api-production.up.railway.app/docs |

---

## 📦 Project IDs & Configuration

### Vercel (Frontend)

| Property | Value |
|----------|-------|
| **Project Name** | `quantv2` |
| **Project ID** | `prj_uLBoItgO0ssNRIM2XP21vl5Idxrw` |
| **Framework** | Next.js 14 |
| **Build Command** | `npm run build` |
| **Output Directory** | `.next` |
| **Root Directory** | `frontend` |

### Railway (Backend)

| Property | Value |
|----------|-------|
| **Project Name** | `nut-quant-system` |
| **Project ID** | `ded93c40-1ef1-4763-a213-440faf5e16c5` |
| **Service Name** | `quant-trading-api` |
| **Framework** | Python/FastAPI |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Root Directory** | `backend` |

### GitHub Repository

| Property | Value |
|----------|-------|
| **Repository** | https://github.com/nutbitzuist/quant-trading-system |
| **Branch** | `main` |

---

## 🔑 Environment Variables

### Backend (Railway)

```env
SETSMART_API_KEY=93001366-5f83-4b52-b96b-3550980d1b38
CORS_ORIGINS=https://nutquantsystem.vercel.app,http://localhost:3000
AUTH_SECRET_KEY=<your-secret-key>
```

### Frontend (Vercel)

```env
NEXT_PUBLIC_API_URL=https://quant-trading-api-production.up.railway.app/api
```

---

## 🚀 Deployment Commands

### Deploy Backend to Railway

```bash
cd backend
railway link ded93c40-1ef1-4763-a213-440faf5e16c5
railway up
```

### Deploy Frontend to Vercel

```bash
cd frontend
vercel --prod
```

Or link to specific project:

```bash
vercel link --project prj_uLBoItgO0ssNRIM2XP21vl5Idxrw
vercel --prod
```

### Push to GitHub (triggers auto-deploy if connected)

```bash
git add -A
git commit -m "Your commit message"
git push origin main
```

---

## 🔄 CI/CD Setup (Optional)

To enable automatic deployments on push:

### Vercel
1. Go to Vercel Dashboard → Project Settings → Git
2. Connect to GitHub repository
3. Set Root Directory to `frontend`

### Railway
1. Go to Railway Dashboard → Project → Settings → Source
2. Connect to GitHub repository
3. Set Root Directory to `backend`

---

## 📋 Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│                    QUANT TRADING SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Vercel)                                          │
│  ├─ URL: nutquantsystem.vercel.app                         │
│  ├─ Project: quantv2                                        │
│  └─ ID: prj_uLBoItgO0ssNRIM2XP21vl5Idxrw                   │
├─────────────────────────────────────────────────────────────┤
│  Backend (Railway)                                          │
│  ├─ URL: quant-trading-api-production.up.railway.app       │
│  ├─ Project: nut-quant-system                              │
│  └─ ID: ded93c40-1ef1-4763-a213-440faf5e16c5               │
├─────────────────────────────────────────────────────────────┤
│  GitHub                                                     │
│  └─ https://github.com/nutbitzuist/quant-trading-system    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠 Local Development

```bash
# Backend (Terminal 1)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

*Last updated: January 1, 2026*
