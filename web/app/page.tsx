export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold text-center">
          🚀 EtsyNova Dashboard
        </h1>
      </div>

      <div className="mb-32 grid text-center lg:max-w-5xl lg:w-full lg:mb-0 lg:grid-cols-4 lg:text-left">
        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100">
          <h2 className="mb-3 text-2xl font-semibold">
            Analytics{' '}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              📊
            </span>
          </h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Real-time metrics and insights for your Etsy store.
          </p>
        </div>

        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100">
          <h2 className="mb-3 text-2xl font-semibold">
            Products{' '}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              🏷️
            </span>
          </h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Track your best-performing products and listings.
          </p>
        </div>

        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100">
          <h2 className="mb-3 text-2xl font-semibold">
            Orders{' '}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              📦
            </span>
          </h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Monitor orders and revenue in real-time.
          </p>
        </div>

        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100">
          <h2 className="mb-3 text-2xl font-semibold">
            AI Insights{' '}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              🤖
            </span>
          </h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Get AI-powered suggestions to grow your business.
          </p>
        </div>
      </div>
    </main>
  )
}
