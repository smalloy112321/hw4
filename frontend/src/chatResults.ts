import { createContext, useContext } from 'react'
import type { ChatResults } from './api'

// Product matches from the latest chat reply, shown on the page by ChatResultsPanel.
export type PageResults = ChatResults & { query: string; id: number }

export type ChatResultsState = {
  results: PageResults | null
  show: (results: ChatResults, query: string) => void
  clear: () => void
}

export const ChatResultsContext = createContext<ChatResultsState | null>(null)

export function useChatResults(): ChatResultsState {
  const ctx = useContext(ChatResultsContext)
  if (!ctx) throw new Error('useChatResults must be used inside <ChatResultsProvider>')
  return ctx
}
