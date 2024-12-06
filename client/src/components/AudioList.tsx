'use client'

import { useState, useEffect } from 'react'
import styles from './AudioList.module.css'
import { useApi } from '@/lib/api'

type AudioFile = {
    key: string;
    url: string;
    createdAt: string;
}

export function AudioList() {
    const [audioFiles, setAudioFiles] = useState<AudioFile[]>([])
    const [loading, setLoading] = useState(true)
    const api = useApi()

    useEffect(() => {
        fetchAudioFiles()
    }, [])

    const fetchAudioFiles = async () => {
        try {
            const data = await api.listAudioFiles()
            setAudioFiles(data.files || [])
        } catch (error) {
            console.error('Error fetching audio files:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className={styles.container}>
                <h2 className={styles.title}>Your Audio Files</h2>
                <div className={styles.loading}>Loading audio files...</div>
            </div>
        )
    }

    return (
        <div className={styles.container}>
            <h2 className={styles.title}>Your Audio Files</h2>
            {audioFiles.length === 0 ? (
                <p className={styles.empty}>No audio files yet. Try converting an article!</p>
            ) : (
                <div className={styles.grid}>
                    {audioFiles.map((file) => (
                        <div key={file.key} className={styles.card}>
                            <h3>{file.key}</h3>
                            <audio controls src={file.url} className={styles.audio} />
                            <time className={styles.date}>
                                {new Date(file.createdAt).toLocaleDateString()}
                            </time>
                            <a href={file.url} download className={styles.downloadButton}>
                                Download
                            </a>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}