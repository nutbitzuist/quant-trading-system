# Quant Project v2

Renaissance-style quantitative trading system for Thai SET100 stocks.

## Structure

```
backend/           Python FastAPI backend
  app/
    core/          Regime engine, orchestrator, ensemble, risk manager
    models/        20 quantitative models
    data/          Data fetching and caching
    api/           API routes
    reports/       PDF generation
    sector/        Sector rotation module
  tests/           Unit and integration tests

frontend/          Next.js dashboard
  src/
    components/    React components
    pages/         Page routes
    hooks/         Custom hooks

docs/              Documentation
scripts/           Utility scripts
```

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```
