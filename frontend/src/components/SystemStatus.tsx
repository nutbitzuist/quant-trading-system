'use client'

import { useState, useEffect } from 'react';

interface ModelStatus {
    name: string;
    category: string;
    status: 'active' | 'error' | 'not_implemented';
    error_count: number;
    error_message?: string;
}

interface DataSourceStatus {
    name: string;
    status: 'connected' | 'fallback' | 'error' | 'unknown';
    using_mock_data: boolean;
    error_message?: string;
}

interface PipelineStatus {
    status: string;
    last_run?: string;
    stocks_attempted: number;
    stocks_successful: number;
    stocks_failed: number;
    current_regime?: string;
    errors: string[];
    duration_seconds?: number;
}

interface SystemHealth {
    overall_status: 'healthy' | 'degraded' | 'error';
    timestamp: string;
    data_source: DataSourceStatus;
    pipeline: PipelineStatus;
    models: Record<string, ModelStatus>;
    recommendations: string[];
}

interface LogEntry {
    timestamp: string;
    type: 'error' | 'warning' | 'info';
    message: string;
    details?: Record<string, unknown>;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export default function SystemStatus() {
    const [health, setHealth] = useState<SystemHealth | null>(null);
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<'overview' | 'models' | 'logs'>('overview');

    const fetchHealth = async () => {
        try {
            const res = await fetch(`${API_URL}/diagnostics/status`);
            if (!res.ok) throw new Error('Failed to fetch health status');
            const data = await res.json();
            setHealth(data);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        }
    };

    const fetchLogs = async () => {
        try {
            const res = await fetch(`${API_URL}/diagnostics/logs`);
            if (!res.ok) throw new Error('Failed to fetch logs');
            const data = await res.json();
            setLogs(data.logs || []);
        } catch (err) {
            console.error('Failed to fetch logs:', err);
        }
    };

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            await Promise.all([fetchHealth(), fetchLogs()]);
            setLoading(false);
        };
        loadData();

        // Auto-refresh every 10 seconds
        const interval = setInterval(() => {
            fetchHealth();
            fetchLogs();
        }, 10000);

        return () => clearInterval(interval);
    }, []);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'healthy':
            case 'connected':
            case 'active':
                return 'bg-green-500';
            case 'degraded':
            case 'fallback':
                return 'bg-yellow-500';
            case 'error':
            case 'failed':
                return 'bg-red-500';
            default:
                return 'bg-gray-500';
        }
    };

    const getStatusBadge = (status: string) => {
        const color = getStatusColor(status);
        return (
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white ${color}`}>
                {status.toUpperCase()}
            </span>
        );
    };

    if (loading) {
        return (
            <div className="p-6 bg-slate-800 rounded-lg">
                <div className="animate-pulse flex items-center gap-3">
                    <div className="h-4 w-4 bg-slate-600 rounded-full"></div>
                    <div className="h-4 w-48 bg-slate-600 rounded"></div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6 bg-red-900/20 border border-red-500 rounded-lg">
                <h3 className="text-red-400 font-semibold mb-2">System Status Unavailable</h3>
                <p className="text-red-300 text-sm">{error}</p>
                <button
                    onClick={() => { fetchHealth(); fetchLogs(); }}
                    className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-white text-sm"
                >
                    Retry
                </button>
            </div>
        );
    }

    const implementedModels = health ? Object.values(health.models).filter(m => m.status === 'active').length : 0;
    const totalModels = health ? Object.keys(health.models).length : 20;

    return (
        <div className="bg-slate-800 rounded-lg overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-slate-700 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(health?.overall_status || 'unknown')} animate-pulse`}></div>
                    <h2 className="text-lg font-semibold text-white">System Status</h2>
                    {health && getStatusBadge(health.overall_status)}
                </div>
                <span className="text-xs text-slate-400">
                    Last updated: {new Date().toLocaleTimeString()}
                </span>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-slate-700">
                {(['overview', 'models', 'logs'] as const).map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`px-4 py-2 text-sm font-medium transition-colors ${activeTab === tab
                                ? 'text-blue-400 border-b-2 border-blue-400 bg-slate-700/50'
                                : 'text-slate-400 hover:text-white'
                            }`}
                    >
                        {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                ))}
            </div>

            {/* Content */}
            <div className="p-4">
                {activeTab === 'overview' && health && (
                    <div className="space-y-4">
                        {/* Data Source */}
                        <div className="bg-slate-700/50 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-sm font-medium text-white">Data Source</h3>
                                {getStatusBadge(health.data_source.status)}
                            </div>
                            <p className="text-slate-300 text-sm">{health.data_source.name}</p>
                            {health.data_source.using_mock_data && (
                                <p className="text-yellow-400 text-xs mt-1">⚠️ Using mock data (API unavailable)</p>
                            )}
                        </div>

                        {/* Pipeline Status */}
                        <div className="bg-slate-700/50 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-sm font-medium text-white">Pipeline</h3>
                                {getStatusBadge(health.pipeline.status)}
                            </div>
                            <div className="grid grid-cols-3 gap-4 mt-3">
                                <div className="text-center">
                                    <p className="text-2xl font-bold text-white">{health.pipeline.stocks_successful}</p>
                                    <p className="text-xs text-slate-400">Successful</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-2xl font-bold text-red-400">{health.pipeline.stocks_failed}</p>
                                    <p className="text-xs text-slate-400">Failed</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-2xl font-bold text-blue-400">{health.pipeline.current_regime || 'N/A'}</p>
                                    <p className="text-xs text-slate-400">Regime</p>
                                </div>
                            </div>
                        </div>

                        {/* Models Summary */}
                        <div className="bg-slate-700/50 rounded-lg p-4">
                            <h3 className="text-sm font-medium text-white mb-2">Models</h3>
                            <div className="flex items-center gap-4">
                                <div className="flex-1 bg-slate-600 rounded-full h-2">
                                    <div
                                        className="bg-green-500 h-2 rounded-full transition-all"
                                        style={{ width: `${(implementedModels / totalModels) * 100}%` }}
                                    />
                                </div>
                                <span className="text-sm text-slate-300">{implementedModels}/{totalModels} active</span>
                            </div>
                        </div>

                        {/* Recommendations */}
                        {health.recommendations.length > 0 && (
                            <div className="bg-yellow-900/20 border border-yellow-600/50 rounded-lg p-4">
                                <h3 className="text-sm font-medium text-yellow-400 mb-2">Recommendations</h3>
                                <ul className="space-y-1">
                                    {health.recommendations.map((rec, i) => (
                                        <li key={i} className="text-yellow-200 text-sm flex items-start gap-2">
                                            <span>→</span>
                                            <span>{rec}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'models' && health && (
                    <div className="space-y-2">
                        {Object.entries(health.models).map(([id, model]) => (
                            <div
                                key={id}
                                className={`flex items-center justify-between p-3 rounded-lg ${model.status === 'active' ? 'bg-green-900/20' : 'bg-slate-700/50'
                                    }`}
                            >
                                <div>
                                    <p className="text-white text-sm font-medium">{model.name}</p>
                                    <p className="text-slate-400 text-xs">{model.category}</p>
                                </div>
                                <div className="flex items-center gap-2">
                                    {model.error_count > 0 && (
                                        <span className="text-red-400 text-xs">{model.error_count} errors</span>
                                    )}
                                    {getStatusBadge(model.status === 'not_implemented' ? 'pending' : model.status)}
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {activeTab === 'logs' && (
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                        {logs.length === 0 ? (
                            <p className="text-slate-400 text-sm text-center py-8">No logs available</p>
                        ) : (
                            logs.map((log, i) => (
                                <div
                                    key={i}
                                    className={`p-3 rounded-lg text-sm ${log.type === 'error' ? 'bg-red-900/20 border border-red-500/30' :
                                            log.type === 'warning' ? 'bg-yellow-900/20 border border-yellow-500/30' :
                                                'bg-slate-700/50'
                                        }`}
                                >
                                    <div className="flex items-center justify-between mb-1">
                                        <span className={`font-medium ${log.type === 'error' ? 'text-red-400' :
                                                log.type === 'warning' ? 'text-yellow-400' :
                                                    'text-blue-400'
                                            }`}>
                                            {log.type.toUpperCase()}
                                        </span>
                                        <span className="text-slate-500 text-xs">
                                            {new Date(log.timestamp).toLocaleTimeString()}
                                        </span>
                                    </div>
                                    <p className="text-slate-300">{log.message}</p>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
