import './globals.css'
import {AuthProvider} from '@/providers/AuthProvider';

export default function RootLayout({
                                       children,
                                   }: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body>
                <AuthProvider>
                    <nav className="navbar">
                        <div className="logo">article2audio</div>
                    </nav>
                    <main>{children}</main>
                </AuthProvider>
            </body>
        </html>
    )
}