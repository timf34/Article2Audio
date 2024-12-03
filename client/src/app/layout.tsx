import './globals.css'

export default function RootLayout({
                                     children,
                                   }: {
  children: React.ReactNode
}) {
  return (
      <html lang="en">
      <body>
      <nav className="navbar">
        <div className="logo">article2audio</div>
      </nav>
      <main>{children}</main>
      </body>
      </html>
  )
}