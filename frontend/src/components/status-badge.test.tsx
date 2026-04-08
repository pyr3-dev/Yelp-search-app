import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { StatusBadge } from './status-badge'

describe('StatusBadge', () => {
  it('renders Open when isOpen is true', () => {
    render(<StatusBadge isOpen={true} />)
    expect(screen.getByText('Open')).toBeInTheDocument()
  })

  it('renders Closed when isOpen is false', () => {
    render(<StatusBadge isOpen={false} />)
    expect(screen.getByText('Closed')).toBeInTheDocument()
  })

  it('renders nothing when isOpen is null', () => {
    const { container } = render(<StatusBadge isOpen={null} />)
    expect(container.firstChild).toBeNull()
  })
})
