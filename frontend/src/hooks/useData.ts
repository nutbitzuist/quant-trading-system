'use client'

import { useState, useEffect } from 'react'
import {
    fetchRegime,
    fetchRankings,
    fetchModels,
    fetchSectorRotation,
    type RegimeData,
    type ScreeningResult,
    type ModelInfo,
    type SectorRotation,
} from '@/lib/api'

export function useRegime() {
    const [data, setData] = useState<RegimeData | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchRegime()
            .then(setData)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false))
    }, [])

    return { data, loading, error }
}

export function useRankings() {
    const [data, setData] = useState<ScreeningResult | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchRankings()
            .then(setData)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false))
    }, [])

    return {
        data, loading, error, refetch: () => {
            setLoading(true)
            fetchRankings()
                .then(setData)
                .catch((e) => setError(e.message))
                .finally(() => setLoading(false))
        }
    }
}

export function useModels() {
    const [data, setData] = useState<ModelInfo[] | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchModels()
            .then(setData)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false))
    }, [])

    return { data, loading, error }
}

export function useSectorRotation() {
    const [data, setData] = useState<SectorRotation | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchSectorRotation()
            .then(setData)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false))
    }, [])

    return { data, loading, error }
}
