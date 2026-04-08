import { create } from 'zustand'
import type { SearchFilters } from '@/types'

interface SearchState extends SearchFilters {
  city: string
  page: number
  selectedId: string | null
  setCity: (city: string) => void
  setFilter: (patch: Partial<SearchFilters>) => void
  setPage: (page: number) => void
  selectBusiness: (id: string | null) => void
}

export const useSearchStore = create<SearchState>((set) => ({
  city: '',
  category: null,
  minStars: null,
  sortBy: 'stars',
  order: 'desc',
  page: 1,
  selectedId: null,

  setCity: (city) => set({ city, page: 1, selectedId: null }),
  setFilter: (patch) => set((s) => ({ ...s, ...patch, page: 1 })),
  setPage: (page) => set({ page }),
  selectBusiness: (id) => set({ selectedId: id }),
}))
