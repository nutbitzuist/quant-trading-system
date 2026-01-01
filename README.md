# Quant Trading System

Renaissance-style Quantitative Trading System for Thai SET100 stocks.

## Features

- **5-Layer Architecture**: Regime → Orchestrator → 20 Models → Ensemble → Risk
- **20 Core Models**: Momentum, Trend, Fundamental, Quantitative
- **Sector Rotation**: RRG, Business Cycle, Momentum analysis
- **Real-time Data**: SET Smart API integration
- **Full-Stack**: FastAPI backend + Next.js frontend

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

Visit http://localhost:8000/docs for Swagger UI.

## Environment Variables

Create `.env` files from `.env.example` templates:

**Backend:**
- `SETSMART_API_KEY` - SET Smart API key for real market data
- `AUTH_SECRET_KEY` - JWT secret key

**Frontend:**
- `NEXT_PUBLIC_API_URL` - Backend API URL

## Deployment

- **Backend**: Railway (`railway up`)
- **Frontend**: Vercel (`vercel deploy`)

## License

MIT
