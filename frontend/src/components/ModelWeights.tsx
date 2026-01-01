'use client'

import { useState, useEffect } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

interface ModelWeight {
    name: string
    bull: number
    bear: number
    sideways: number
}

const defaultWeights: ModelWeight[] = [
    { name: 'HQM', bull: 1.2, bear: 0.5, sideways: 0.8 },
    { name: 'Clenow', bull: 1.0, bear: 0.6, sideways: 0.9 },
    { name: 'ADX', bull: 1.0, bear: 1.0, sideways: 0.5 },
    { name: 'Quality', bull: 0.8, bear: 1.5, sideways: 1.2 },
    { name: 'Altman Z', bull: 0.5, bear: 2.0, sideways: 1.0 },
    { name: 'Mean Rev', bull: 0.3, bear: 0.5, sideways: 1.5 },
]

export function ModelWeights() {
    const [weights, setWeights] = useState<ModelWeight[]>(defaultWeights)
    const [currentRegime, setCurrentRegime] = useState<string>('BULL')
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        Promise.all([
            fetch(`${API_URL}/regime/weights`).then(r => r.json()).catch(() => null),
            fetch(`${API_URL}/regime/current`).then(r => r.json()).catch(() => null),
        ])
            .then(([weightsData, regimeData]) => {
                if (regimeData?.trend_regime || regimeData?.regime) {
                    setCurrentRegime(regimeData.trend_regime || regimeData.regime)
                }

                if (weightsData?.weights || weightsData?.matrix) {
                    const matrix = weightsData.weights || weightsData.matrix
                    // Transform API weights to component format if needed
                    if (Array.isArray(matrix)) {
                        setWeights(matrix)
                    }
                }
            })
            .finally(() => setLoading(false))
    }, [])

    const getBarWidth = (weight: number) => {
        const maxWeight = 2.0
        return `${(weight / maxWeight) * 100}%`
    }

    const getBarColor = (weight: number) => {
        if (weight >= 1.2) return 'bg-bull'
        if (weight >= 0.8) return 'bg-zinc-500'
        return 'bg-zinc-700'
    }

    if (loading) {
        return <div className="animate-pulse h-48 bg-zinc-800/50 rounded" />
    }

    return (
        <div className="space-y-3">
            {weights.map((model) => {
                const weight = model[currentRegime.toLowerCase() as keyof typeof model] as number || 1.0
                return (
                    <div key={model.name} className="flex items-center gap-3">
                        <div className="w-20 text-sm text-zinc-400">{model.name}</div>
                        <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                            <div
                                className={`h-full rounded-full ${getBarColor(weight)}`}
                                style={{ width: getBarWidth(weight) }}
                            />
                        </div>
                        <div className="w-12 text-right text-sm font-mono text-zinc-300">
                            {weight.toFixed(1)}x
                        </div>
                    </div>
                )
            })}
            <div className="pt-2 text-xs text-zinc-500 text-center">
                Weights shown for <span className={`font-semibold ${currentRegime === 'BULL' ? 'text-bull' :
                        currentRegime === 'BEAR' ? 'text-bear' : 'text-sideways'
                    }`}>{currentRegime}</span> regime
            </div>
        </div>
    )
}
