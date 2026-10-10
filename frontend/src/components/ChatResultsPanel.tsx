import { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useChatResults } from '../chatResults'
import ProductCard from './ProductCard'

// Shows the products from the latest chat reply as cards at the top of the page.
// On a product page it collapses to a slim bar so the PDP stays front and center.
export default function ChatResultsPanel() {
  const { results, clear } = useChatResults()
  const { pathname } = useLocation()
  const onPdp = pathname.startsWith('/products/')
  const [expandedOnPdp, setExpandedOnPdp] = useState<number | null>(null)
  const panelRef = useRef<HTMLElement>(null)
  const resultsId = results?.id

  // Bring new matches into view when they arrive.
  useEffect(() => {
    if (resultsId) panelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [resultsId])

  if (!results) return null
  const count = results.products.length
  const collapsed = onPdp && expandedOnPdp !== results.id

  return (
    <section ref={panelRef} className="chat-results" aria-label="Products from chat" aria-live="polite">
      <div className="chat-results-inner">
        <div className="chat-results-head">
          <div>
            <p className="chat-results-eyebrow">From your chat</p>
            <h2 className="chat-results-title">
              {results.heading} <span className="chat-results-count">({count})</span>
            </h2>
          </div>
          <div className="chat-results-actions">
            {results.category && !collapsed && (
              <Link to={`/products?category=${encodeURIComponent(results.category)}`} className="chat-results-link">
                View all {results.category} →
              </Link>
            )}
            {collapsed ? (
              <button type="button" className="btn btn-outline btn-small" onClick={() => setExpandedOnPdp(results.id)}>
                Show matches
              </button>
            ) : (
              onPdp && (
                <button type="button" className="btn btn-outline btn-small" onClick={() => setExpandedOnPdp(null)}>
                  Hide
                </button>
              )
            )}
            <button type="button" className="chat-results-close" onClick={clear} aria-label="Clear chat matches">
              ×
            </button>
          </div>
        </div>
        {!collapsed && (
          <div className="grid chat-results-grid">
            {results.products.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
