// frontend/src/types/index.ts

export interface BusinessResult {
  business_id: string
  name: string | null
  address: string | null
  city: string | null
  state: string | null
  stars: number | null
  review_count: number | null
  categories: string[] | null
  latitude: number | null
  longitude: number | null
  is_open: boolean | null
  first_photo_id: string | null
}

export interface TipResult {
  id: number
  text: string | null
  date: string | null
  compliment_count: number | null
  user_id: string | null
}

export interface BusinessDetail extends BusinessResult {
  attributes: Record<string, unknown> | null
  hours: Record<string, string> | null
  tips: TipResult[]
  checkin_count: number
}

export interface PhotoResult {
  photo_id: string
  caption: string | null
  label: string | null
}

export interface BusinessSearchResponse {
  total: number
  page: number
  limit: number
  results: BusinessResult[]
}

export interface BusinessSearchParams {
  city: string
  category?: string
  min_stars?: number
  sort_by?: 'stars' | 'review_count' | 'name'
  order?: 'asc' | 'desc'
  page?: number
  limit?: number
}

export type SearchFilters = {
  category: string | null
  minStars: number | null
  sortBy: 'stars' | 'review_count' | 'name'
  order: 'asc' | 'desc'
}
