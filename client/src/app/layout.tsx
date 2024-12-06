'use client'

import './globals.css'
import { AuthProvider } from '@/providers/AuthProvider'
import { NavBar } from '@/components/NavBar'

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en">
        <body>
        <AuthProvider>
            <NavBar />
            <main>{children}</main>
        </AuthProvider>
        </body>
        </html>
    )
}