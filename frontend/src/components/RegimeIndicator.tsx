'use client'

import { useState, useEffect } from 'react'

interface RegimeData {
    trend_regime: string
    volatility_regime: string
    active_models: number
    position_multiplier: number
}

export function RegimeIndicator() {
    const [regime, setRegime] = useState<RegimeData | null>(null)

    useEffect(() => {
        // Mock data - replace with API call
        setRegime({
            trend_regime: 'BULL',
            volatility_regime: 'NORMAL',
            active_models: 12,
            position_multiplier: 1.0,
        })
    }, [])

    if (!regime) return <div className="card animate-pulse h-32" />

    const trendColors = {
        BULL: 'regime-bull',
        BEAR: 'regime-bear',
        SIDEWAYS: 'regime-sideways',
    }

    const volColors = {
        LOW: 'text-bull',
        NORMAL: 'text-zinc-400',
        HIGH: 'text-sideways',
        SPIKE: 'text-bear',
    }

    return (
        <div className="card">
            <h2 className="card-header">Market Regime</h2>
            <div className="space-y-3">
                {/* Trend Badge */}
                <div className="flex items-center gap-3">
                    <span
                        className={`px-3 py-1.5 rounded-full border text-sm font-semibold ${trendColors[regime.trend_regime as keyof typeof trendColors] || 'bg-zinc-800'
                            }`}
                    >
                        {regime.trend_regime}
                    </span>
                    <span className="text-zinc-500">Trend</span>
                </div>

                {/* Volatility */}
                <div className="flex items-center gap-3">
                    <span
                        className={`text-lg font-medium ${volColors[regime.volatility_regime as keyof typeof volColors] || 'text-zinc-400'
                            }`}
                    >
                        {regime.volatility_regime}
                    </span>
                    <span className="text-zinc-500">Volatility</span>
                </div>

                {/* Position Multiplier */}
                <div className="pt-2 border-t border-zinc-800">
                    <div className="flex justify-between text-sm">
                        <span className="text-zinc-500">Position Size</span>
                        <span className="font-medium text-white">
                            {(regime.position_multiplier * 100).toFixed(0)}%
                        </span>
                    </div>
                </div>
            </div>
        </div>
    )
}
