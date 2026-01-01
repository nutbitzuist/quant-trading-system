'use client'

import { useModels } from '@/hooks/useData'

// Mock data
const mockModels = [
    // Momentum
    { name: 'hqm', class_name: 'HQMModel', category: 'momentum', description: 'High-Quality Momentum', implemented: true },
    { name: 'clenow', class_name: 'ClenowMomentumModel', category: 'momentum', description: 'Clenow Momentum', implemented: true },
    { name: 'dual_momentum', class_name: 'DualMomentumModel', category: 'momentum', description: 'Dual Momentum', implemented: true },
    { name: 'roc_multi', class_name: 'ROCMultiTimeframeModel', category: 'momentum', description: 'ROC Multi-Timeframe', implemented: true },
    { name: '52w_high', class_name: 'FiftyTwoWeekHighModel', category: 'momentum', description: '52-Week High', implemented: true },
    // Trend
    { name: 'adx', class_name: 'ADXTrendModel', category: 'trend', description: 'ADX Trend Strength', implemented: true },
    { name: 'multi_ema', class_name: 'MultiEMAModel', category: 'trend', description: 'Multi-EMA Matrix', implemented: true },
    { name: 'supertrend', class_name: 'SupertrendModel', category: 'trend', description: 'Supertrend', implemented: true },
    { name: 'ichimoku', class_name: 'IchimokuModel', category: 'trend', description: 'Ichimoku Cloud', implemented: true },
    { name: 'psar', class_name: 'ParabolicSARModel', category: 'trend', description: 'Parabolic SAR', implemented: true },
    // Fundamental
    { name: 'quality', class_name: 'QualityModel', category: 'fundamental', description: 'Quality Factor', implemented: true },
    { name: 'magic_formula', class_name: 'MagicFormulaModel', category: 'fundamental', description: 'Magic Formula', implemented: true },
    { name: 'garp', class_name: 'GARPModel', category: 'fundamental', description: 'GARP', implemented: true },
    { name: 'altman_z', class_name: 'AltmanZScoreModel', category: 'fundamental', description: 'Altman Z-Score', implemented: true },
    { name: 'dividend', class_name: 'DividendModel', category: 'fundamental', description: 'Dividend Quality', implemented: true },
    // Quant
    { name: 'hmm_regime', class_name: 'HMMRegimeModel', category: 'quant', description: 'HMM Regime', implemented: true },
    { name: 'vol_regime', class_name: 'VolatilityRegimeModel', category: 'quant', description: 'Volatility Regime', implemented: true },
    { name: 'mean_reversion', class_name: 'MeanReversionModel', category: 'quant', description: 'Mean Reversion', implemented: true },
    { name: 'correlation', class_name: 'CorrelationRegimeModel', category: 'quant', description: 'Correlation Regime', implemented: true },
    { name: 'rsi_divergence', class_name: 'RSIDivergenceModel', category: 'quant', description: 'RSI Divergence', implemented: true },
]

const categoryColors = {
    momentum: 'bg-purple-500/20 text-purple-400 border-purple-500/50',
    trend: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
    fundamental: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50',
    quant: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
}

const categoryDescriptions = {
    momentum: 'Price momentum and relative strength',
    trend: 'Trend direction and strength indicators',
    fundamental: 'Value, quality, and financial health',
    quant: 'Statistical and regime-based models',
}

export default function ModelsPage() {
    const categories = ['momentum', 'trend', 'fundamental', 'quant']

    const modelsByCategory = categories.reduce((acc, cat) => {
        acc[cat] = mockModels.filter(m => m.category === cat)
        return acc
    }, {} as Record<string, typeof mockModels>)

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white">Model Registry</h1>
                <div className="flex items-center gap-2">
                    <span className="text-bull font-medium">20</span>
                    <span className="text-zinc-500">/</span>
                    <span className="text-zinc-400">20 Implemented</span>
                </div>
            </div>

            {/* Progress */}
            <div className="card">
                <div className="flex items-center gap-4">
                    <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                        <div className="h-full bg-bull rounded-full" style={{ width: '100%' }} />
                    </div>
                    <div className="text-sm font-medium text-bull">100%</div>
                </div>
            </div>

            {/* Models by Category */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {categories.map((category) => (
                    <div key={category} className="card">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-white capitalize">{category}</h2>
                            <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${categoryColors[category as keyof typeof categoryColors]
                                }`}>
                                {modelsByCategory[category].length} models
                            </span>
                        </div>
                        <p className="text-sm text-zinc-500 mb-4">
                            {categoryDescriptions[category as keyof typeof categoryDescriptions]}
                        </p>

                        <div className="space-y-2">
                            {modelsByCategory[category].map((model) => (
                                <div
                                    key={model.name}
                                    className="flex items-center justify-between py-2 px-3 bg-zinc-800/50 rounded-lg"
                                >
                                    <div>
                                        <div className="font-medium text-zinc-200">{model.description}</div>
                                        <div className="text-xs text-zinc-500 font-mono">{model.name}</div>
                                    </div>
                                    <div className={`w-2 h-2 rounded-full ${model.implemented ? 'bg-bull' : 'bg-zinc-600'
                                        }`} />
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            {/* Weight Matrix */}
            <div className="card">
                <h2 className="card-header">Weight Matrix by Regime</h2>
                <p className="text-sm text-zinc-500 mb-4">
                    Model weights are dynamically adjusted based on current market regime
                </p>

                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="text-zinc-500 border-b border-zinc-800">
                                <th className="pb-2 text-left">Model</th>
                                <th className="pb-2 text-center text-bull">BULL</th>
                                <th className="pb-2 text-center text-bear">BEAR</th>
                                <th className="pb-2 text-center text-sideways">SIDEWAYS</th>
                            </tr>
                        </thead>
                        <tbody>
                            {[
                                { model: 'HQM', bull: 1.2, bear: 0.5, sideways: 0.8 },
                                { model: 'Clenow', bull: 1.0, bear: 0.6, sideways: 0.9 },
                                { model: 'ADX', bull: 1.0, bear: 1.0, sideways: 0.5 },
                                { model: 'Quality', bull: 0.8, bear: 1.5, sideways: 1.2 },
                                { model: 'Altman Z', bull: 0.5, bear: 2.0, sideways: 1.0 },
                                { model: 'Mean Rev', bull: 0.3, bear: 0.5, sideways: 1.5 },
                            ].map((row) => (
                                <tr key={row.model} className="border-b border-zinc-800/50">
                                    <td className="py-2 text-zinc-300">{row.model}</td>
                                    <td className="py-2 text-center font-mono">{row.bull.toFixed(1)}</td>
                                    <td className="py-2 text-center font-mono">{row.bear.toFixed(1)}</td>
                                    <td className="py-2 text-center font-mono">{row.sideways.toFixed(1)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}
