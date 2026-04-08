import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import { SearchBar } from './search-bar'
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

describe('SearchBar name input', () => {
  it('renders name input with correct placeholder', () => {
    render(<SearchBar />)
    expect(screen.getByPlaceholderText('Business name...')).toBeInTheDocument()
  })

  it('submits name to store on Enter', () => {
    render(<SearchBar />)
    const input = screen.getByPlaceholderText('Business name...')
    fireEvent.change(input, { target: { value: 'Dominos' } })
    fireEvent.keyDown(input, { key: 'Enter' })
    expect(useSearchStore.getState().name).toBe('Dominos')
  })

  it('submits name to store on blur', () => {
    render(<SearchBar />)
    const input = screen.getByPlaceholderText('Business name...')
    fireEvent.change(input, { target: { value: 'Pizza Hut' } })
    fireEvent.blur(input)
    expect(useSearchStore.getState().name).toBe('Pizza Hut')
  })

  it('sets name to null when input is cleared and blurred', () => {
    useSearchStore.setState({ name: 'Dominos' })
    render(<SearchBar />)
    const input = screen.getByPlaceholderText('Business name...')
    fireEvent.change(input, { target: { value: '' } })
    fireEvent.blur(input)
    expect(useSearchStore.getState().name).toBeNull()
  })
})
