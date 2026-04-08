import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { BusinessCard } from './business-card'
import type { BusinessResult } from '@/types'

const business: BusinessResult = {
  business_id: 'biz-1',
  name: 'Test Place',
  address: '100 Main St',
  city: 'Miami',
  state: 'FL',
  stars: 4.2,
  review_count: 88,
  categories: ['Italian'],
  latitude: 25.77,
  longitude: -80.19,
  is_open: true,
  first_photo_id: null,
}

const businessWithPhoto: BusinessResult = { ...business, first_photo_id: 'p1' }

describe('BusinessCard', () => {
  it('renders business name and address', () => {
    render(<BusinessCard business={business} isSelected={false} onClick={vi.fn()} />)
    expect(screen.getByText('Test Place')).toBeInTheDocument()
    expect(screen.getByText(/100 Main St/)).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const onClick = vi.fn()
    render(<BusinessCard business={business} isSelected={false} onClick={onClick} />)
    fireEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it('does not render photo when first_photo_id is null', () => {
    render(<BusinessCard business={business} isSelected={false} onClick={vi.fn()} />)
    expect(screen.queryByTestId('business-card-photo')).not.toBeInTheDocument()
  })

  it('renders photo when first_photo_id is set', () => {
    render(<BusinessCard business={businessWithPhoto} isSelected={false} onClick={vi.fn()} />)
    const img = screen.getByTestId('business-card-photo')
    expect(img).toBeInTheDocument()
    expect(img).toHaveAttribute('src', '/api/photos/p1')
  })

  it('applies selected styles when isSelected is true', () => {
    render(<BusinessCard business={business} isSelected={true} onClick={vi.fn()} />)
    const btn = screen.getByRole('button')
    expect(btn.className).toContain('bg-blue-50')
    expect(btn.className).toContain('border-l-blue-500')
  })
})
