import './globals.css'

export const metadata = {
  title: 'EtsyNova - Etsy Analytics Dashboard',
  description: 'Comprehensive analytics dashboard for Etsy store owners',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
