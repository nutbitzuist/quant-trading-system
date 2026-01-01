/**
 * API client for backend communication
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export interface RegimeData {
    trend_regime: string
    volatility_regime: string
    active_models: string[]
    model_weights: Record<string, number>
    position_size_multiplier: number
    timestamp: string
}

export interface StockRanking {
    ticker: string
    composite_score: number
    signal: string
    confidence: number
    model_agreement: number
    rank: number
    position_size_pct: number
    model_scores: Record<string, number>
    model_signals: Record<string, string>
}

export interface ScreeningResult {
    regime: string
    volatility_regime: string
    top_buy: StockRanking[]
    top_avoid: StockRanking[]
    total_screened: number
    active_models: string[]
}

export interface ModelInfo {
    name: string
    class_name: string
    category: string
    description: string
    implemented: boolean
}

export interface SectorRRG {
    sector: string
    rs_ratio: number
    rs_momentum: number
    quadrant: string
    rotation_direction: string
}

export interface SectorRotation {
    timestamp: string
    rrg_data: SectorRRG[]
    sector_recommendations: Record<string, string>
    top_sectors: string[]
    bottom_sectors: string[]
    cycle_phase: string
}

// API Functions
export async function fetchRegime(): Promise<RegimeData> {
    const res = await fetch(`${API_BASE}/regime/current`)
    if (!res.ok) throw new Error('Failed to fetch regime')
    return res.json()
}

export async function fetchRankings(): Promise<ScreeningResult> {
    const res = await fetch(`${API_BASE}/screen/rankings`)
    if (!res.ok) throw new Error('Failed to fetch rankings')
    return res.json()
}

export async function runScreening(): Promise<ScreeningResult> {
    const res = await fetch(`${API_BASE}/screen/run`, { method: 'POST' })
    if (!res.ok) throw new Error('Failed to run screening')
    return res.json()
}

export async function fetchModels(): Promise<ModelInfo[]> {
    const res = await fetch(`${API_BASE}/models/`)
    if (!res.ok) throw new Error('Failed to fetch models')
    return res.json()
}

export async function fetchSectorRotation(): Promise<SectorRotation> {
    const res = await fetch(`${API_BASE}/sector/rrg`)
    if (!res.ok) throw new Error('Failed to fetch sector rotation')
    return res.json()
}

export async function fetchModelStatus(): Promise<{
    total: number
    implemented: number
    tested: number
    remaining: number
}> {
    const res = await fetch(`${API_BASE}/models/status`)
    if (!res.ok) throw new Error('Failed to fetch model status')
    return res.json()
}
