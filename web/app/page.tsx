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

interface GmailAuthStatus {
  connected: boolean
  email: string | null
  provider: string
  last_sync: string | null
  messages_count: number
}

interface InboxMessage {
  id: string
  thread_id: string
  from_email: string
  from_name?: string
  subject: string
  snippet: string
  is_unread: boolean
  internal_date: string
  etsy_receipt_id?: string
  has_etsy_links: boolean
  needs_reply: boolean
  reply_priority: string
  is_refund_related: boolean
}

interface InboxStats {
  total_messages: number
  unread_count: number
  needs_reply_count: number
  refund_requests: number
  linked_to_orders: number
  sources: {
    gmail: number
    etsy: number
  }
}

export default function Home() {
  const [activeTab, setActiveTab] = useState('analytics')
  const [metrics, setMetrics] = useState<ShopMetrics | null>(null)
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null)
  const [gmailStatus, setGmailStatus] = useState<GmailAuthStatus | null>(null)
  const [inboxMessages, setInboxMessages] = useState<InboxMessage[]>([])
  const [inboxStats, setInboxStats] = useState<InboxStats | null>(null)
  const [inboxFilter, setInboxFilter] = useState('all')
  const [selectedMessage, setSelectedMessage] = useState<InboxMessage | null>(null)
  const [aiDraft, setAiDraft] = useState<any>(null)
  const [draftLoading, setDraftLoading] = useState(false)
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

      // Fetch Gmail auth status
      const gmailResponse = await fetch(`${apiBase}/auth/google/status`)
      const gmailData = await gmailResponse.json()
      setGmailStatus(gmailData)

      // Fetch metrics if connected or in demo mode
      if (authData.connected || authData.pending) {
        const metricsResponse = await fetch(`${apiBase}/metrics/shop?shop_id=demo_shop`)
        const metricsData = await metricsResponse.json()
        setMetrics(metricsData)
      }

      // Fetch inbox data if Gmail is connected or in demo mode
      if (gmailData.connected) {
        await fetchInboxData()
      }
    } catch (err) {
      setError('Failed to fetch data')
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchInboxData = async () => {
    try {
      // Fetch inbox messages
      const messagesResponse = await fetch(`${apiBase}/inbox/messages?filter_type=${inboxFilter}`)
      const messagesData = await messagesResponse.json()
      setInboxMessages(messagesData.messages || [])

      // Fetch inbox stats
      const statsResponse = await fetch(`${apiBase}/inbox/stats`)
      const statsData = await statsResponse.json()
      setInboxStats(statsData)
    } catch (err) {
      console.error('Error fetching inbox data:', err)
    }
  }

  const connectToGmail = async () => {
    try {
      const response = await fetch(`${apiBase}/auth/google/connect`, { method: 'POST' })
      const data = await response.json()
      if (data.auth_url && data.auth_url !== 'mock://google-oauth') {
        window.location.href = data.auth_url
      } else {
        // Mock mode - simulate connection
        setGmailStatus({
          connected: true,
          email: 'talha.b.tariq4etsy1@gmail.com',
          provider: 'google',
          last_sync: new Date().toISOString(),
          messages_count: 5
        })
        await fetchInboxData()
      }
    } catch (err) {
      setError('Failed to connect to Gmail')
    }
  }

  const generateAIDraft = async (messageId: string) => {
    try {
      setDraftLoading(true)
      setAiDraft(null)

      const response = await fetch(`${apiBase}/inbox/messages/${messageId}/draft`, {
        method: 'POST'
      })
      const data = await response.json()
      setAiDraft(data)
    } catch (err) {
      console.error('Failed to generate AI draft:', err)
      setError('Failed to generate AI draft')
    } finally {
      setDraftLoading(false)
    }
  }

  const copyDraftToClipboard = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content)
      alert('Draft copied to clipboard!')
    } catch (err) {
      console.error('Failed to copy to clipboard:', err)
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

      case 'inbox':
        return (
          <div className="space-y-6">
            {/* Gmail Connection Status */}
            <div className="bg-white border rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-semibold">Gmail Integration</h4>
                  <p className="text-sm text-gray-600">
                    {gmailStatus?.connected
                      ? `Connected as ${gmailStatus.email}`
                      : 'Connect Gmail to manage all your messages in one place'
                    }
                  </p>
                </div>
                {!gmailStatus?.connected && (
                  <button
                    onClick={connectToGmail}
                    className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
                  >
                    Connect Gmail
                  </button>
                )}
              </div>
            </div>

            {/* Inbox Stats */}
            {inboxStats && (
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <div className="bg-blue-50 p-3 rounded-lg">
                  <h5 className="font-medium text-blue-800">Total</h5>
                  <p className="text-lg font-bold text-blue-900">{inboxStats.total_messages}</p>
                </div>
                <div className="bg-orange-50 p-3 rounded-lg">
                  <h5 className="font-medium text-orange-800">Unread</h5>
                  <p className="text-lg font-bold text-orange-900">{inboxStats.unread_count}</p>
                </div>
                <div className="bg-red-50 p-3 rounded-lg">
                  <h5 className="font-medium text-red-800">Need Reply</h5>
                  <p className="text-lg font-bold text-red-900">{inboxStats.needs_reply_count}</p>
                </div>
                <div className="bg-yellow-50 p-3 rounded-lg">
                  <h5 className="font-medium text-yellow-800">Refunds</h5>
                  <p className="text-lg font-bold text-yellow-900">{inboxStats.refund_requests}</p>
                </div>
                <div className="bg-green-50 p-3 rounded-lg">
                  <h5 className="font-medium text-green-800">Linked</h5>
                  <p className="text-lg font-bold text-green-900">{inboxStats.linked_to_orders}</p>
                </div>
              </div>
            )}

            {/* Filter Tabs */}
            <div className="flex space-x-2">
              {['all', 'needs_reply', 'refunds'].map((filter) => (
                <button
                  key={filter}
                  onClick={() => {
                    setInboxFilter(filter)
                    fetchInboxData()
                  }}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    inboxFilter === filter
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {filter.replace('_', ' ').toUpperCase()}
                </button>
              ))}
            </div>

            {/* Messages List */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Message List Panel */}
              <div className="space-y-2">
                <h4 className="font-semibold">Messages ({inboxMessages.length})</h4>
                <div className="max-h-96 overflow-y-auto space-y-2">
                  {inboxMessages.map((message) => (
                    <div
                      key={message.id}
                      onClick={() => setSelectedMessage(message)}
                      className={`p-3 border rounded-lg cursor-pointer hover:bg-gray-50 ${
                        selectedMessage?.id === message.id ? 'border-blue-500 bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2">
                            <p className="font-medium text-sm truncate">
                              {message.from_name || message.from_email}
                            </p>
                            {message.is_unread && (
                              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                            )}
                            {message.etsy_receipt_id && (
                              <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded">
                                Order #{message.etsy_receipt_id}
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-800 font-medium">{message.subject}</p>
                          <p className="text-xs text-gray-600 mt-1 line-clamp-2">{message.snippet}</p>
                          <div className="flex items-center space-x-2 mt-2">
                            {message.needs_reply && (
                              <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                                Reply Needed
                              </span>
                            )}
                            {message.is_refund_related && (
                              <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                                Refund
                              </span>
                            )}
                            <span className="text-xs text-gray-500">
                              {new Date(message.internal_date).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  {inboxMessages.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      No messages found
                    </div>
                  )}
                </div>
              </div>

              {/* Message Detail & AI Draft Panel */}
              <div className="space-y-4">
                {selectedMessage ? (
                  <>
                    <div className="border rounded-lg p-4">
                      <h5 className="font-semibold mb-2">Message Details</h5>
                      <div className="space-y-2 text-sm">
                        <p><strong>From:</strong> {selectedMessage.from_name} &lt;{selectedMessage.from_email}&gt;</p>
                        <p><strong>Subject:</strong> {selectedMessage.subject}</p>
                        <div className="bg-gray-50 p-3 rounded">
                          <p className="whitespace-pre-wrap">{selectedMessage.snippet}</p>
                        </div>
                      </div>

                      {selectedMessage.needs_reply && (
                        <button
                          onClick={() => generateAIDraft(selectedMessage.id)}
                          disabled={draftLoading}
                          className="mt-4 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-4 py-2 rounded"
                        >
                          {draftLoading ? 'Generating...' : '🤖 Generate AI Draft'}
                        </button>
                      )}
                    </div>

                    {/* AI Draft Display */}
                    {aiDraft && (
                      <div className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h5 className="font-semibold">AI Draft Reply</h5>
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                            {Math.round(aiDraft.confidence_score * 100)}% confidence
                          </span>
                        </div>

                        <div className="bg-gray-50 p-3 rounded mb-3">
                          <pre className="whitespace-pre-wrap text-sm">{aiDraft.draft_content}</pre>
                        </div>

                        <div className="bg-blue-50 p-3 rounded mb-3">
                          <p className="text-sm"><strong>AI Rationale:</strong> {aiDraft.rationale}</p>
                        </div>

                        <div className="flex space-x-2">
                          <button
                            onClick={() => copyDraftToClipboard(aiDraft.draft_content)}
                            className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm"
                          >
                            📋 Copy Draft
                          </button>
                          <button
                            onClick={() => setAiDraft(null)}
                            className="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm"
                          >
                            Dismiss
                          </button>
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="border rounded-lg p-8 text-center text-gray-500">
                    Select a message to view details and generate AI drafts
                  </div>
                )}
              </div>
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
              { key: 'inbox', label: 'Inbox', emoji: '📧' },
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
