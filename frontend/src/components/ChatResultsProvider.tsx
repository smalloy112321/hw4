import { useCallback, useMemo, useState, type ReactNode } from 'react'
import type { ChatResults } from '../api'
import { ChatResultsContext, type PageResults } from '../chatResults'

export default function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [results, setResults] = useState<PageResults | null>(null)

  const show = useCallback((r: ChatResults, query: string) => {
    setResults({ ...r, query, id: Date.now() })
  }, [])
  const clear = useCallback(() => setResults(null), [])

  const value = useMemo(() => ({ results, show, clear }), [results, show, clear])
  return <ChatResultsContext.Provider value={value}>{children}</ChatResultsContext.Provider>
}
