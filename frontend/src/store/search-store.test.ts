import { describe, it, expect, beforeEach } from 'vitest'
import { useSearchStore } from './search-store'

beforeEach(() => {
  useSearchStore.setState({
    city: '',
    category: null,
    minStars: null,
    sortBy: 'stars',
    order: 'desc',
    page: 1,
    selectedId: null,
  })
})

describe('setCity', () => {
  it('sets city and resets page and selectedId', () => {
    useSearchStore.setState({ page: 3, selectedId: 'x' })
    useSearchStore.getState().setCity('Miami')
    const { city, page, selectedId } = useSearchStore.getState()
    expect(city).toBe('Miami')
    expect(page).toBe(1)
    expect(selectedId).toBeNull()
  })
})

describe('setFilter', () => {
  it('merges filter patch and resets page', () => {
    useSearchStore.setState({ page: 2 })
    useSearchStore.getState().setFilter({ minStars: 4, category: 'Mexican' })
    const { minStars, category, page } = useSearchStore.getState()
    expect(minStars).toBe(4)
    expect(category).toBe('Mexican')
    expect(page).toBe(1)
  })
})

describe('setPage', () => {
  it('sets page without touching other state', () => {
    useSearchStore.setState({ city: 'Dallas' })
    useSearchStore.getState().setPage(5)
    const { page, city } = useSearchStore.getState()
    expect(page).toBe(5)
    expect(city).toBe('Dallas')
  })
})

describe('selectBusiness', () => {
  it('sets selectedId', () => {
    useSearchStore.getState().selectBusiness('biz-123')
    expect(useSearchStore.getState().selectedId).toBe('biz-123')
  })

  it('clears selectedId when passed null', () => {
    useSearchStore.setState({ selectedId: 'biz-123' })
    useSearchStore.getState().selectBusiness(null)
    expect(useSearchStore.getState().selectedId).toBeNull()
  })
})
