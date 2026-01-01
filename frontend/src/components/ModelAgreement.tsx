'use client'

// Simplified heatmap for model agreement
const agreementData = [
    { stock: 'DELTA', hqm: 'B', adx: 'B', quality: 'B', altman: 'B', clenow: 'B' },
    { stock: 'GPSC', hqm: 'B', adx: 'B', quality: 'B', altman: 'H', clenow: 'B' },
    { stock: 'BDMS', hqm: 'B', adx: 'H', quality: 'B', altman: 'B', clenow: 'B' },
    { stock: 'SCB', hqm: 'B', adx: 'B', quality: 'H', altman: 'B', clenow: 'H' },
    { stock: 'THAI', hqm: 'A', adx: 'A', quality: 'A', altman: 'A', clenow: 'A' },
]

const signalColors = {
    B: 'bg-bull/80',
    H: 'bg-zinc-600',
    A: 'bg-bear/80',
}

const signalLabels = {
    B: 'Buy',
    H: 'Hold',
    A: 'Avoid',
}

export function ModelAgreement() {
    const models = ['hqm', 'adx', 'quality', 'altman', 'clenow']

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-xs">
                <thead>
                    <tr className="text-zinc-500">
                        <th className="pb-2 text-left font-medium">Stock</th>
                        {models.map((m) => (
                            <th key={m} className="pb-2 font-medium uppercase">
                                {m}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {agreementData.map((row) => (
                        <tr key={row.stock} className="border-t border-zinc-800/50">
                            <td className="py-1.5 font-medium text-white">{row.stock}</td>
                            {models.map((model) => {
                                const signal = row[model as keyof typeof row] as string
                                if (model === 'stock') return null
                                return (
                                    <td key={model} className="py-1.5 text-center">
                                        <span
                                            className={`inline-block w-6 h-6 rounded ${signalColors[signal as keyof typeof signalColors]
                                                }`}
                                            title={signalLabels[signal as keyof typeof signalLabels]}
                                        />
                                    </td>
                                )
                            })}
                        </tr>
                    ))}
                </tbody>
            </table>
            <div className="flex gap-4 mt-3 justify-center text-xs">
                <span className="flex items-center gap-1">
                    <span className="w-3 h-3 rounded bg-bull/80" /> Buy
                </span>
                <span className="flex items-center gap-1">
                    <span className="w-3 h-3 rounded bg-zinc-600" /> Hold
                </span>
                <span className="flex items-center gap-1">
                    <span className="w-3 h-3 rounded bg-bear/80" /> Avoid
                </span>
            </div>
        </div>
    )
}
