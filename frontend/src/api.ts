// Backend client. In dev, Vite proxies /api and /images to FastAPI on port 8000.

export type ProductSummary = {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  price: number
  image_url: string
  in_stock: boolean
  color_family: string | null // main garment color group, e.g. "Navy"
  sizes_in_stock: string[]
}

export const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL'] as const

export type SizeStock = {
  size: string
  quantity: number
  in_stock: boolean
}

export type ProductDetail = ProductSummary & {
  search_tags: string[]
  sizes: SizeStock[]
}

async function getJson<T>(path: string): Promise<T> {
  let res: Response
  try {
    res = await fetch(path)
  } catch {
    throw new Error('Could not reach the store server. Is the backend running?')
  }
  if (res.status === 404) throw new Error('We could not find that item.')
  if (!res.ok) throw new Error(`The store server returned an error (${res.status}).`)
  return res.json() as Promise<T>
}

export function fetchProducts(q?: string): Promise<ProductSummary[]> {
  const query = q ? `?q=${encodeURIComponent(q)}` : ''
  return getJson(`/api/products${query}`)
}

export function fetchProduct(productId: string): Promise<ProductDetail> {
  return getJson(`/api/products/${encodeURIComponent(productId)}`)
}

export function formatPrice(price: number): string {
  return `$${price.toFixed(2)}`
}

// First sentence of the description, capped so cards stay a tidy height.
export function shortDescription(text: string, max = 110): string {
  const first = text.split(/(?<=\.)\s/)[0]
  if (first.length <= max) return first
  return `${first.slice(0, first.lastIndexOf(' ', max))}…`
}

// The catalogue has ~20 garment_type spellings; group them into shopper-friendly categories.
export const CATEGORIES = ['Hoodies', 'Crewnecks', 'Quarter-Zips', 'T-Shirts', 'Jackets & Fleece', 'Long Sleeves'] as const
export type Category = (typeof CATEGORIES)[number]

export function categoryOf(garmentType: string): Category {
  const t = garmentType.toLowerCase()
  if (t.includes('quarter-zip') || t.includes('1/4')) return 'Quarter-Zips'
  if (t.includes('jacket') || t.includes('fleece') || t.includes('full-zip')) return 'Jackets & Fleece'
  if (t.includes('hood')) return 'Hoodies'
  if (t.includes('crewneck') || t.includes('mockneck')) return 'Crewnecks'
  if (t.includes('long-sleeve')) return 'Long Sleeves'
  return 'T-Shirts'
}

// --- Accounts -------------------------------------------------------------------------
// The session lives in an HttpOnly cookie set by the backend; the page never sees a token.

export type User = {
  id: number
  name: string
  first_name: string | null
  last_name: string | null
  email: string
  created_at: string
}

export type RegisterInput = {
  first_name: string
  last_name: string
  email: string
  password: string
}

type ValidationIssue = { msg: string }

async function sendJson<T>(path: string, body?: unknown): Promise<T> {
  let res: Response
  try {
    res = await fetch(path, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new Error('Could not reach the store server. Is the backend running?')
  }
  if (res.status === 204) return undefined as T
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    const detail = data?.detail
    // FastAPI validation errors arrive as a list; show the first message.
    const message = Array.isArray(detail)
      ? (detail[0] as ValidationIssue)?.msg?.replace(/^Value error, /, '')
      : detail
    throw new Error(message || `Something went wrong (${res.status}). Try again.`)
  }
  return data as T
}

export function register(input: RegisterInput): Promise<User> {
  return sendJson('/api/auth/register', input)
}

export function login(email: string, password: string): Promise<User> {
  return sendJson('/api/auth/login', { email, password })
}

export function logout(): Promise<void> {
  return sendJson('/api/auth/logout')
}

export async function fetchCurrentUser(): Promise<User | null> {
  const res = await fetch('/api/auth/me', { credentials: 'same-origin' }).catch(() => null)
  if (!res || !res.ok) return null
  return res.json() as Promise<User>
}

// --- Chat -----------------------------------------------------------------------------

export type ChatTurn = {
  role: 'user' | 'assistant'
  content: string
  product_ids?: string[]
  viewing_product_id?: string | null // user turns: the product page they were on
}

// Where the shopper is when they send a message, so "does this come in pink?" works on a PDP.
export type PageContext = {
  path: string
  product_id: string | null
  category: string | null
  search: string | null
}

// API contract for POST /api/chat: the agent picks matching products, the backend fills in
// each card from the database, and the site renders them (ChatResultsPanel).
export type ChatProductCard = {
  product_id: string
  name: string
  price: number
  image_url: string
  short_description: string
  sizes_in_stock: string[]
  in_stock: boolean
}

export type ChatResults = {
  heading: string
  category: Category | null
  products: ChatProductCard[]
}

export type ChatReply = { reply: string; results: ChatResults | null; tools_used: string[]; saved: boolean }

// Guests send recent turns; for logged-in shoppers the server loads saved history instead.
export function sendChat(message: string, history: ChatTurn[], page: PageContext): Promise<ChatReply> {
  return sendJson('/api/chat', { message, history, page })
}

export type HistoryMessage = {
  role: 'user' | 'assistant'
  content: string
  results: ChatResults | null
  created_at: string
}

export async function fetchChatHistory(): Promise<HistoryMessage[]> {
  const res = await fetch('/api/chat/history', { credentials: 'same-origin' })
  if (!res.ok) throw new Error('Could not load your saved chat.')
  const data = (await res.json()) as { messages: HistoryMessage[] }
  return data.messages
}

export async function clearChatHistory(): Promise<void> {
  const res = await fetch('/api/chat/history', { method: 'DELETE', credentials: 'same-origin' })
  if (!res.ok) throw new Error('Could not clear your chat. Try again.')
}
