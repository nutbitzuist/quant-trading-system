import { useState } from 'react';
import { runScreening } from '@/lib/api';

export default function RunScreeningButton() {
    const [isLoading, setIsLoading] = useState(false);
    const [status, setStatus] = useState<'idle' | 'running' | 'success' | 'error'>('idle');

    const handleRun = async () => {
        setIsLoading(true);
        setStatus('running');
        try {
            await runScreening();
            setStatus('success');
            // Ideally trigger a refresh of the rankings data here
            // For now, we rely on the user refreshing or auto-refresh interval
            setTimeout(() => window.location.reload(), 2000);
        } catch (error) {
            console.error('Failed to run screening:', error);
            setStatus('error');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center gap-4">
            {status === 'running' && (
                <span className="text-sm text-yellow-600 animate-pulse">
                    Running pipeline (this may take a minute)...
                </span>
            )}
            {status === 'success' && (
                <span className="text-sm text-green-600">
                    Screening started successfully!
                </span>
            )}
            {status === 'error' && (
                <span className="text-sm text-red-600">
                    Failed to start screening.
                </span>
            )}
            <button
                onClick={handleRun}
                disabled={isLoading}
                className={`px-4 py-2 text-sm font-medium text-white transition-colors rounded-md shadow-sm 
          ${isLoading
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-indigo-600 hover:bg-indigo-700'
                    }`}
            >
                {isLoading ? 'Processing...' : 'Run Global Screening'}
            </button>
        </div>
    );
}
