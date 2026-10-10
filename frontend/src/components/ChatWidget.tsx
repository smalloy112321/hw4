import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  clearChatHistory,
  fetchChatHistory,
  formatPrice,
  sendChat,
  type ChatResults,
  type ChatTurn,
  type PageContext,
  type User,
} from '../api'
import { useAuth } from '../auth'
import { useChatResults } from '../chatResults'
import HandsomeDan from './HandsomeDan'

// `local` marks messages that exist only in the widget (greeting, errors) and never go to the agent.
type Message = ChatTurn & { results?: ChatResults | null; local?: boolean; error?: boolean }

function greeting(user: User | null, returning: boolean): Message {
  const name = user?.first_name || user?.name.split(' ')[0]
  const content = !user
    ? "Woof! I'm Handsome Dan, Yale's bulldog. Ask me about hoodies, sizes, prices, or gift ideas!"
    : returning
      ? `Welcome back, ${name}! It's Handsome Dan. Our earlier chat is below. What can I fetch for you today?`
      : `Woof, hi ${name}! I'm Handsome Dan, Yale's bulldog. Ask me about hoodies, sizes, prices, or gift ideas!`
  return { role: 'assistant', content, local: true }
}

// What page the shopper is on, so "does this come in pink?" works on a product page.
function pageContext(pathname: string, search: string): PageContext {
  const params = new URLSearchParams(search)
  const pdp = pathname.match(/^\/products\/([^/]+)$/)
  return {
    path: pathname,
    product_id: pdp ? decodeURIComponent(pdp[1]) : null,
    category: pathname === '/products' ? params.get('category') : null,
    search: pathname === '/products' ? params.get('q') : null,
  }
}

// How many earlier turns go to the agent so it can follow the conversation.
const HISTORY_TURNS = 12
// The full set of matches shows on the page; the chat bubble previews the first few.
const CHAT_PREVIEW = 3

// App remounts this with a new key when the shopper logs in or out, so state starts fresh.
export default function ChatWidget() {
  const { user } = useAuth()
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([greeting(user, false)])
  const [loadingHistory, setLoadingHistory] = useState(Boolean(user))
  const [draft, setDraft] = useState('')
  const [waiting, setWaiting] = useState(false)
  const { show, clear } = useChatResults()

  // Logged in: reload this shopper's saved conversation from the database.
  useEffect(() => {
    if (!user) return
    let cancelled = false
    fetchChatHistory()
      .then((saved) => {
        if (cancelled) return
        const restored: Message[] = saved.map((m) => ({
          role: m.role,
          content: m.content,
          results: m.results,
          product_ids: m.results?.products.map((p) => p.product_id),
        }))
        setMessages([greeting(user, restored.length > 0), ...restored])
      })
      .catch(() => {
        if (!cancelled) setMessages([greeting(user, false), { role: 'assistant', content: 'Your saved chat could not be loaded right now.', local: true, error: true }])
      })
      .finally(() => {
        if (!cancelled) setLoadingHistory(false)
      })
    return () => {
      cancelled = true
    }
  }, [user])

  async function clearSaved() {
    if (!window.confirm('Delete your saved chat with Campus Customs? This cannot be undone.')) return
    try {
      await clearChatHistory()
      setMessages([greeting(user, false)])
      clear()
    } catch (err) {
      setMessages((m) => [...m, { role: 'assistant', content: (err as Error).message, local: true, error: true }])
    }
  }
  const inputRef = useRef<HTMLInputElement>(null)
  const logRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (open) inputRef.current?.focus()
  }, [open, waiting])

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, open, waiting])

  async function send(e: FormEvent) {
    e.preventDefault()
    const text = draft.trim()
    if (!text || waiting) return
    // Guests: send recent turns (logged-in history comes from the database on the server).
    const history: ChatTurn[] = user
      ? []
      : messages
          .filter((m) => !m.local && !m.error)
          .slice(-HISTORY_TURNS)
          .map(({ role, content, results, viewing_product_id }) => ({
            role,
            content,
            product_ids: results?.products.map((p) => p.product_id) ?? [],
            viewing_product_id,
          }))
    const page = pageContext(location.pathname, location.search)
    setMessages((m) => [...m, { role: 'user', content: text, viewing_product_id: page.product_id }])
    setDraft('')
    setWaiting(true)
    try {
      const res = await sendChat(text, history, page)
      setMessages((m) => [...m, { role: 'assistant', content: res.reply, results: res.results }])
      if (res.results) show(res.results, text)
    } catch (err) {
      setMessages((m) => [...m, { role: 'assistant', content: (err as Error).message, local: true, error: true }])
    } finally {
      setWaiting(false)
    }
  }

  return (
    <div className="chat">
      {open && (
        <section id="chat-panel" className="chat-panel" aria-label="Chat with Handsome Dan">
          <header className="chat-header">
            <HandsomeDan size={40} className="chat-header-avatar" />
            <div className="chat-header-text">
              <p className="chat-title">Handsome Dan</p>
              <p className="chat-sub">{user ? 'Saved to your account' : 'Log in to save your chat'}</p>
            </div>
            <div className="chat-header-actions">
              {user && messages.some((m) => !m.local) && (
                <button type="button" className="chat-clear" onClick={clearSaved}>
                  Clear chat
                </button>
              )}
              <button type="button" className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
                ×
              </button>
            </div>
          </header>
          <div className="chat-log" ref={logRef} aria-live="polite">
            {loadingHistory && <p className="chat-loading" role="status">Loading your saved chat…</p>}
            {messages.map((m, i) => (
              <div key={i} className={`chat-turn chat-turn-${m.role}`}>
                <div className="chat-bubble-row">
                  {m.role === 'assistant' && <HandsomeDan size={28} className="chat-msg-avatar" />}
                  <div className={`chat-msg chat-${m.role}${m.error ? ' chat-error' : ''}`}>
                    <span className="sr-only">{m.role === 'user' ? 'You said:' : 'Handsome Dan said:'}</span>
                    {m.content}
                  </div>
                </div>
                {m.results && (
                  <>
                    <ul className="chat-products" aria-label="Suggested products">
                      {m.results.products.slice(0, CHAT_PREVIEW).map((p) => (
                        <li key={p.product_id}>
                          <Link to={`/products/${p.product_id}`} className="chat-product">
                            <img src={p.image_url} alt="" />
                            <span className="chat-product-text">
                              <span className="chat-product-name">{p.name}</span>
                              <span className="chat-product-price">
                                {formatPrice(p.price)}
                                {!p.in_stock && ' · Sold out'}
                              </span>
                            </span>
                          </Link>
                        </li>
                      ))}
                    </ul>
                    <button type="button" className="chat-see-all" onClick={() => show(m.results!, '')}>
                      {m.results.products.length > CHAT_PREVIEW
                        ? `See all ${m.results.products.length} on the page ↑`
                        : 'Show on the page ↑'}
                    </button>
                  </>
                )}
              </div>
            ))}
            {waiting && (
              <div className="chat-typing-row">
                <HandsomeDan size={28} className="chat-msg-avatar" />
              <div className="chat-msg chat-assistant chat-typing" role="status">
                <span className="sr-only">Handsome Dan is typing…</span>
                <span aria-hidden="true" className="dot" />
                <span aria-hidden="true" className="dot" />
                <span aria-hidden="true" className="dot" />
              </div>
              </div>
            )}
          </div>
          <form className="chat-form" onSubmit={send}>
            <label htmlFor="chat-input" className="sr-only">Type your message</label>
            <input
              id="chat-input"
              ref={inputRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Ask about our merch…"
              autoComplete="off"
              maxLength={1000}
              disabled={waiting}
            />
            <button type="submit" className="btn" disabled={!draft.trim() || waiting}>
              Send
            </button>
          </form>
        </section>
      )}
      <div className="chat-launcher">
        {!open && (
          // Decorative duplicate of the button below, so a click on Dan opens the chat too.
          <span className="chat-launcher-avatar" aria-hidden="true" onClick={() => setOpen(true)}>
            <HandsomeDan size={56} />
          </span>
        )}
        <button
          type="button"
          className="chat-toggle"
          onClick={() => setOpen((o) => !o)}
          aria-expanded={open}
          aria-controls="chat-panel"
        >
          {open ? (
            <>
              <span aria-hidden="true">×</span> Close
            </>
          ) : (
            'Chat with Handsome Dan'
          )}
        </button>
      </div>
    </div>
  )
}
