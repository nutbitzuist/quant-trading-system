import { RegimeIndicator } from '@/components/RegimeIndicator'
import { ModelWeights } from '@/components/ModelWeights'
import { StockRankings } from '@/components/StockRankings'
import { ModelAgreement } from '@/components/ModelAgreement'

export default function Dashboard() {
    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white">
                    Market Dashboard
                </h1>
                <div className="text-sm text-zinc-500">
                    SET Smart API Connected
                </div>
            </div>

            {/* Regime Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <RegimeIndicator />
                <div className="card md:col-span-2">
                    <h2 className="card-header">Quick Stats</h2>
                    <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                            <div className="text-3xl font-bold text-bull">20</div>
                            <div className="text-sm text-zinc-500">Active Models</div>
                        </div>
                        <div>
                            <div className="text-3xl font-bold text-white">100</div>
                            <div className="text-sm text-zinc-500">SET100 Stocks</div>
                        </div>
                        <div>
                            <div className="text-3xl font-bold text-thai-gold">Live</div>
                            <div className="text-sm text-zinc-500">Data Source</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Stock Rankings */}
                <div className="card">
                    <h2 className="card-header">Top Buy Recommendations</h2>
                    <StockRankings type="buy" />
                </div>

                <div className="card">
                    <h2 className="card-header">Top Avoid List</h2>
                    <StockRankings type="avoid" />
                </div>
            </div>

            {/* Model Weights & Agreement */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card">
                    <h2 className="card-header">Model Weights (by Regime)</h2>
                    <ModelWeights />
                </div>

                <div className="card">
                    <h2 className="card-header">Model Agreement Heatmap</h2>
                    <ModelAgreement />
                </div>
            </div>
        </div>
    )
}
