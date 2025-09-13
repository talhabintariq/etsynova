'use client'

import { useState, useEffect } from 'react'

interface ShopMetrics {
  orders: number
  gmv: number
  visits: number
  views: number
  conversion_rate: number
  favorites: number
  cart_adds: number
  refunds: number
}

interface AuthStatus {
  connected: boolean
  pending: boolean
  shop_id: string | null
}

export default function Home() {
  const [activeTab, setActiveTab] = useState('analytics')
  const [metrics, setMetrics] = useState<ShopMetrics | null>(null)
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)

      // Fetch auth status
      const authResponse = await fetch(`${apiBase}/auth/status`)
      const authData = await authResponse.json()
      setAuthStatus(authData)

      // Fetch metrics if connected or in demo mode
      if (authData.connected || authData.pending) {
        const metricsResponse = await fetch(`${apiBase}/metrics/shop?shop_id=demo_shop`)
        const metricsData = await metricsResponse.json()
        setMetrics(metricsData)
      }
    } catch (err) {
      setError('Failed to fetch data')
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  const connectToEtsy = async () => {
    try {
      const response = await fetch(`${apiBase}/auth/etsy/connect`, { method: 'POST' })
      const data = await response.json()
      if (data.auth_url) {
        window.location.href = data.auth_url
      }
    } catch (err) {
      setError('Failed to connect to Etsy')
    }
  }

  const renderTabContent = () => {
    if (loading) {
      return <div className="text-center py-8">Loading...</div>
    }

    if (error) {
      return <div className="text-center py-8 text-red-600">Error: {error}</div>
    }

    if (!authStatus?.connected && !authStatus?.pending) {
      return (
        <div className="text-center py-12">
          <h3 className="text-xl mb-4">Connect Your Etsy Store</h3>
          <p className="mb-6 text-gray-600">Connect your Etsy store to view analytics and insights</p>
          <button
            onClick={connectToEtsy}
            className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg"
          >
            Connect to Etsy
          </button>
        </div>
      )
    }

    switch (activeTab) {
      case 'analytics':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-800">Orders</h4>
                <p className="text-2xl font-bold text-blue-900">{metrics?.orders || 0}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-semibold text-green-800">Revenue</h4>
                <p className="text-2xl font-bold text-green-900">${metrics?.gmv || 0}</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <h4 className="font-semibold text-purple-800">Views</h4>
                <p className="text-2xl font-bold text-purple-900">{metrics?.views || 0}</p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <h4 className="font-semibold text-orange-800">Conversion</h4>
                <p className="text-2xl font-bold text-orange-900">{metrics?.conversion_rate || 0}%</p>
              </div>
            </div>
          </div>
        )

      case 'products':
        return (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Top Products</h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p>Product analytics will appear here when you have listings data.</p>
            </div>
          </div>
        )

      case 'orders':
        return (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Recent Orders</h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p>Order details and trends will appear here.</p>
            </div>
          </div>
        )

      case 'insights':
        return (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">AI Insights</h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p>AI-powered recommendations will appear here.</p>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <main className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🚀 EtsyNova Dashboard
          </h1>
          {authStatus && (
            <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium">
              <span className={`w-2 h-2 rounded-full mr-2 ${
                authStatus.connected ? 'bg-green-500' :
                authStatus.pending ? 'bg-yellow-500' : 'bg-gray-500'
              }`}></span>
              {authStatus.connected ? 'Live Data' :
               authStatus.pending ? 'Demo Mode' : 'Not Connected'}
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <div className="flex justify-center mb-8">
          <div className="flex space-x-1 bg-gray-200 p-1 rounded-lg">
            {[
              { key: 'analytics', label: 'Analytics', emoji: '📊' },
              { key: 'products', label: 'Products', emoji: '🏷️' },
              { key: 'orders', label: 'Orders', emoji: '📦' },
              { key: 'insights', label: 'AI Insights', emoji: '🤖' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === tab.key
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.emoji} {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          {renderTabContent()}
        </div>
      </div>
    </main>
  )
}
