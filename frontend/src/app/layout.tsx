import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
    title: 'Quant Trading Dashboard',
    description: 'Renaissance-style Quantitative Trading System for Thai SET100',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className="min-h-screen bg-zinc-950">
                <nav className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur">
                    <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <span className="text-xl font-bold text-white">📊 Quant</span>
                            <span className="text-zinc-500">SET100</span>
                        </div>
                        <div className="flex gap-4 text-sm">
                            <a href="/" className="text-zinc-300 hover:text-white">Dashboard</a>
                            <a href="/models" className="text-zinc-500 hover:text-white">Models</a>
                            <a href="/sectors" className="text-zinc-500 hover:text-white">Sectors</a>
                        </div>
                    </div>
                </nav>
                <main className="max-w-7xl mx-auto px-4 py-6">
                    {children}
                </main>
            </body>
        </html>
    )
}
