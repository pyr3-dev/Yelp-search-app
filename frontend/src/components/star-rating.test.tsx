import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { StarRating } from './star-rating'

describe('StarRating', () => {
  it('renders the star and value', () => {
    render(<StarRating value={4.5} />)
    expect(screen.getByText('★ 4.5')).toBeInTheDocument()
  })

  it('renders null when value is null', () => {
    const { container } = render(<StarRating value={null} />)
    expect(container.firstChild).toBeNull()
  })
})
