import { create } from 'zustand'
import { customObjectsApi } from '../api/customObjects'
import type { CustomObject } from '../api/types'

interface CustomObjectsState {
  objects: CustomObject[]
  loading: boolean
  lastFetched: number | null
  fetch: () => Promise<void>
  reset: () => void
}

export const useCustomObjectsStore = create<CustomObjectsState>((set, get) => ({
  objects: [],
  loading: false,
  lastFetched: null,

  fetch: async () => {
    // Throttle: skip if fetched within the last 30 seconds
    const now = Date.now()
    if (get().loading) return
    if (get().lastFetched && now - (get().lastFetched ?? 0) < 30_000) return

    set({ loading: true })
    try {
      const data = await customObjectsApi.list({ is_active: true, limit: 200 })
      set({ objects: data.items, lastFetched: now })
    } catch {
      // Non-fatal — sidebar simply won't show custom objects
    } finally {
      set({ loading: false })
    }
  },

  reset: () => set({ objects: [], lastFetched: null }),
}))
