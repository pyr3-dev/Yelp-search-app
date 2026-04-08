import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import { FilterBar } from './filter-bar'
import { useSearchStore } from '@/store/search-store'

beforeEach(() => {
  useSearchStore.setState({
    city: '',
    category: null,
    minStars: null,
    name: null,
    scope: 'city',
    sortBy: 'relevance',
    order: 'desc',
    page: 1,
    selectedId: null,
  })
})

describe('FilterBar scope toggle', () => {
  it('renders both scope buttons', () => {
    render(<FilterBar />)
    expect(screen.getByRole('button', { name: 'Within city' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Within 5 miles' })).toBeInTheDocument()
  })

  it('Within city button has active style by default', () => {
    render(<FilterBar />)
    expect(screen.getByRole('button', { name: 'Within city' }).className).toContain('bg-slate-800')
  })

  it('clicking Within 5 miles sets scope to radius in store', () => {
    render(<FilterBar />)
    fireEvent.click(screen.getByRole('button', { name: 'Within 5 miles' }))
    expect(useSearchStore.getState().scope).toBe('radius')
  })

  it('Within 5 miles button has active style when scope is radius', () => {
    useSearchStore.setState({ scope: 'radius' })
    render(<FilterBar />)
    expect(screen.getByRole('button', { name: 'Within 5 miles' }).className).toContain('bg-slate-800')
  })

  it('clicking Within city sets scope back to city in store', () => {
    useSearchStore.setState({ scope: 'radius' })
    render(<FilterBar />)
    fireEvent.click(screen.getByRole('button', { name: 'Within city' }))
    expect(useSearchStore.getState().scope).toBe('city')
  })
})
