'use client'

import { useState, useEffect } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

interface StockRanking {
    ticker: string
    score: number
    signal: string
    agreement: number
    position: number
}

interface StockRankingsProps {
    type: 'buy' | 'avoid'
}

// Fallback mock data
const mockBuyData: StockRanking[] = [
    { ticker: 'DELTA', score: 92, signal: 'STRONG_BUY', agreement: 0.85, position: 8.5 },
    { ticker: 'GPSC', score: 88, signal: 'STRONG_BUY', agreement: 0.82, position: 7.2 },
    { ticker: 'BDMS', score: 85, signal: 'BUY', agreement: 0.78, position: 6.8 },
    { ticker: 'SCB', score: 82, signal: 'BUY', agreement: 0.75, position: 6.5 },
    { ticker: 'AOT', score: 80, signal: 'BUY', agreement: 0.72, position: 6.0 },
]

const mockAvoidData: StockRanking[] = [
    { ticker: 'THAI', score: 15, signal: 'STRONG_AVOID', agreement: 0.88, position: 0 },
    { ticker: 'BA', score: 18, signal: 'STRONG_AVOID', agreement: 0.85, position: 0 },
    { ticker: 'MINT', score: 22, signal: 'AVOID', agreement: 0.72, position: 0 },
    { ticker: 'ERW', score: 28, signal: 'AVOID', agreement: 0.68, position: 0 },
    { ticker: 'CENTEL', score: 32, signal: 'AVOID', agreement: 0.65, position: 0 },
]

const signalColors = {
    STRONG_BUY: 'signal-strong-buy',
    BUY: 'signal-buy',
    HOLD: 'signal-hold',
    AVOID: 'signal-avoid',
    STRONG_AVOID: 'signal-strong-avoid',
}

export function StockRankings({ type }: StockRankingsProps) {
    const [data, setData] = useState<StockRanking[]>([])
    const [loading, setLoading] = useState(true)
    const [fromApi, setFromApi] = useState(false)

    useEffect(() => {
        fetch(`${API_URL}/screen/rankings`)
            .then(res => res.json())
            .then(result => {
                // Extract buy or avoid list from API response
                const list = type === 'buy'
                    ? (result.top_buy || result.rankings?.slice(0, 10) || [])
                    : (result.top_avoid || result.rankings?.slice(-10).reverse() || [])

                const formatted = list.map((item: any) => ({
                    ticker: item.ticker,
                    score: item.composite_score || item.score || 0,
                    signal: item.signal || (item.composite_score > 60 ? 'BUY' : 'AVOID'),
                    agreement: item.model_agreement || item.agreement || 0.5,
                    position: item.position_size_pct || item.position || 0,
                }))

                if (formatted.length > 0) {
                    setData(formatted)
                    setFromApi(true)
                } else {
                    setData(type === 'buy' ? mockBuyData : mockAvoidData)
                }
            })
            .catch(() => {
                setData(type === 'buy' ? mockBuyData : mockAvoidData)
            })
            .finally(() => setLoading(false))
    }, [type])

    if (loading) {
        return <div className="animate-pulse h-48 bg-zinc-800/50 rounded" />
    }

    return (
        <div className="overflow-x-auto">
            {!fromApi && <div className="text-xs text-zinc-500 mb-2">Demo data</div>}
            <table className="w-full text-sm">
                <thead>
                    <tr className="text-left text-zinc-500 border-b border-zinc-800">
                        <th className="pb-2 font-medium">#</th>
                        <th className="pb-2 font-medium">Ticker</th>
                        <th className="pb-2 font-medium">Score</th>
                        <th className="pb-2 font-medium">Signal</th>
                        <th className="pb-2 font-medium">Agreement</th>
                        {type === 'buy' && <th className="pb-2 font-medium">Size %</th>}
                    </tr>
                </thead>
                <tbody>
                    {data.map((stock, i) => (
                        <tr key={stock.ticker} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
                            <td className="py-2 text-zinc-500">{i + 1}</td>
                            <td className="py-2 font-medium text-white">{stock.ticker}</td>
                            <td className="py-2">
                                <span
                                    className={`font-mono ${stock.score >= 80 ? 'text-bull' : stock.score <= 30 ? 'text-bear' : 'text-zinc-400'
                                        }`}
                                >
                                    {stock.score.toFixed(0)}
                                </span>
                            </td>
                            <td className="py-2">
                                <span
                                    className={`px-2 py-0.5 rounded text-xs font-medium ${signalColors[stock.signal as keyof typeof signalColors] || 'bg-zinc-700'
                                        }`}
                                >
                                    {stock.signal.replace('_', ' ')}
                                </span>
                            </td>
                            <td className="py-2 text-zinc-400">
                                {(stock.agreement * 100).toFixed(0)}%
                            </td>
                            {type === 'buy' && (
                                <td className="py-2 font-medium text-thai-gold">
                                    {stock.position.toFixed(1)}%
                                </td>
                            )}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
