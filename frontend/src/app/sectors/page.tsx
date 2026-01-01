'use client'

import { useSectorRotation } from '@/hooks/useData'

// RRG Quadrant colors
const quadrantColors = {
    LEADING: 'bg-bull text-white',
    IMPROVING: 'bg-blue-500 text-white',
    WEAKENING: 'bg-sideways text-black',
    LAGGING: 'bg-bear text-white',
}

const recommendationColors = {
    OVERWEIGHT: 'text-bull',
    NEUTRAL: 'text-zinc-400',
    UNDERWEIGHT: 'text-bear',
}

// Mock data for demo
const mockRRGData = [
    { sector: 'FINCIAL', rs_ratio: 103.5, rs_momentum: 102.1, quadrant: 'LEADING', rotation_direction: 'CLOCKWISE' },
    { sector: 'TECH', rs_ratio: 98.2, rs_momentum: 104.5, quadrant: 'IMPROVING', rotation_direction: 'COUNTER_CLOCKWISE' },
    { sector: 'INDUS', rs_ratio: 101.8, rs_momentum: 99.2, quadrant: 'WEAKENING', rotation_direction: 'CLOCKWISE' },
    { sector: 'RESOURC', rs_ratio: 97.5, rs_momentum: 97.8, quadrant: 'LAGGING', rotation_direction: 'CLOCKWISE' },
    { sector: 'PROPCON', rs_ratio: 96.5, rs_momentum: 96.2, quadrant: 'LAGGING', rotation_direction: 'CLOCKWISE' },
    { sector: 'SERVICE', rs_ratio: 99.8, rs_momentum: 101.2, quadrant: 'IMPROVING', rotation_direction: 'STABLE' },
    { sector: 'CONSUMP', rs_ratio: 102.1, rs_momentum: 99.5, quadrant: 'WEAKENING', rotation_direction: 'CLOCKWISE' },
    { sector: 'AGRO', rs_ratio: 97.2, rs_momentum: 101.8, quadrant: 'IMPROVING', rotation_direction: 'COUNTER_CLOCKWISE' },
]

const mockRecommendations = {
    FINCIAL: 'OVERWEIGHT',
    TECH: 'OVERWEIGHT',
    INDUS: 'NEUTRAL',
    RESOURC: 'UNDERWEIGHT',
    PROPCON: 'UNDERWEIGHT',
    SERVICE: 'NEUTRAL',
    CONSUMP: 'NEUTRAL',
    AGRO: 'NEUTRAL',
}

export default function SectorsPage() {
    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Sector Rotation</h1>

            {/* RRG Visualization */}
            <div className="card">
                <h2 className="card-header">Relative Rotation Graph</h2>
                <div className="relative h-96 bg-zinc-800/50 rounded-lg">
                    {/* Grid lines */}
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-px h-full bg-zinc-700" />
                    </div>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-full h-px bg-zinc-700" />
                    </div>

                    {/* Quadrant labels */}
                    <div className="absolute top-4 left-4 text-xs text-zinc-500">IMPROVING</div>
                    <div className="absolute top-4 right-4 text-xs text-zinc-500">LEADING</div>
                    <div className="absolute bottom-4 left-4 text-xs text-zinc-500">LAGGING</div>
                    <div className="absolute bottom-4 right-4 text-xs text-zinc-500">WEAKENING</div>

                    {/* Sector points */}
                    {mockRRGData.map((sector) => {
                        // Map to position (center = 100, scale by 5)
                        const x = 50 + (sector.rs_ratio - 100) * 5
                        const y = 50 - (sector.rs_momentum - 100) * 5

                        return (
                            <div
                                key={sector.sector}
                                className="absolute transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center"
                                style={{ left: `${x}%`, top: `${y}%` }}
                            >
                                <div
                                    className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${quadrantColors[sector.quadrant as keyof typeof quadrantColors]
                                        }`}
                                >
                                    {sector.sector.slice(0, 2)}
                                </div>
                                <span className="text-xs text-zinc-400 mt-1">{sector.sector}</span>
                            </div>
                        )
                    })}

                    {/* Axis labels */}
                    <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 text-xs text-zinc-500">
                        RS-Ratio →
                    </div>
                    <div className="absolute left-2 top-1/2 transform -translate-y-1/2 -rotate-90 text-xs text-zinc-500">
                        RS-Momentum →
                    </div>
                </div>
            </div>

            {/* Sector Table */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card">
                    <h2 className="card-header">Sector Positions</h2>
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="text-zinc-500 border-b border-zinc-800">
                                <th className="pb-2 text-left">Sector</th>
                                <th className="pb-2 text-right">RS-Ratio</th>
                                <th className="pb-2 text-right">RS-Mom</th>
                                <th className="pb-2 text-left">Quadrant</th>
                            </tr>
                        </thead>
                        <tbody>
                            {mockRRGData.map((sector) => (
                                <tr key={sector.sector} className="border-b border-zinc-800/50">
                                    <td className="py-2 font-medium text-white">{sector.sector}</td>
                                    <td className="py-2 text-right font-mono text-zinc-300">{sector.rs_ratio.toFixed(1)}</td>
                                    <td className="py-2 text-right font-mono text-zinc-300">{sector.rs_momentum.toFixed(1)}</td>
                                    <td className="py-2">
                                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${quadrantColors[sector.quadrant as keyof typeof quadrantColors]
                                            }`}>
                                            {sector.quadrant}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div className="card">
                    <h2 className="card-header">Recommendations</h2>
                    <div className="space-y-3">
                        {Object.entries(mockRecommendations).map(([sector, rec]) => (
                            <div key={sector} className="flex items-center justify-between">
                                <span className="text-zinc-300">{sector}</span>
                                <span className={`font-medium ${recommendationColors[rec as keyof typeof recommendationColors]
                                    }`}>
                                    {rec}
                                </span>
                            </div>
                        ))}
                    </div>

                    <div className="mt-6 pt-4 border-t border-zinc-800">
                        <h3 className="text-sm font-medium text-zinc-400 mb-2">Business Cycle</h3>
                        <div className="flex items-center gap-2">
                            <span className="px-3 py-1 bg-bull/20 text-bull rounded-full text-sm font-medium">
                                MID-EXPANSION
                            </span>
                            <span className="text-xs text-zinc-500">Confidence: 72%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
