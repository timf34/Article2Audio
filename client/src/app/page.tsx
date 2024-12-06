'use client'

import { useState } from 'react'
import styles from './page.module.css'
import { AudioList } from '@/components/AudioList'
import { AuthButton } from '@/components/AuthButton'
import { useApi } from '@/lib/api'

export default function Home() {
  const [url, setUrl] = useState('')
  const [processing, setProcessing] = useState(false)
  const [estimatedTime, setEstimatedTime] = useState<number | null>(null)
  const api = useApi()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setProcessing(true)

    try {
      const response = await api.convertArticle(url)
      setEstimatedTime(response.estimatedTime)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setProcessing(false)
    }
  }

  return (
      <div className={styles.container}>
        <div className="flex justify-between items-center w-full mb-8">
          <h1 className={styles.title}>Convert Articles to Audio</h1>
          <AuthButton />
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.inputGroup}>
            <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Paste article URL here..."
                required
                className={styles.input}
            />
            <button
                type="submit"
                className={styles.button}
                disabled={processing}
            >
              {processing ? 'Processing...' : 'Go'}
            </button>
          </div>
        </form>

        {estimatedTime && (
            <div className={styles.notice}>
              Processing your article... Estimated time: {estimatedTime} seconds
            </div>
        )}

        <AudioList />
      </div>
  )
}