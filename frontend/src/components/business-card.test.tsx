import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { BusinessCard } from './business-card'
import type { BusinessResult, PhotoResult } from '@/types'

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
}

const photos: PhotoResult[] = [{ photo_id: 'p1', caption: null, label: 'food' }]

describe('BusinessCard', () => {
  it('renders business name and address', () => {
    render(
      <BusinessCard business={business} isSelected={false} onClick={vi.fn()} photos={[]} />
    )
    expect(screen.getByText('Test Place')).toBeInTheDocument()
    expect(screen.getByText(/100 Main St/)).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const onClick = vi.fn()
    render(
      <BusinessCard business={business} isSelected={false} onClick={onClick} photos={[]} />
    )
    fireEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it('does not render photo tile when photos is empty', () => {
    render(
      <BusinessCard business={business} isSelected={false} onClick={vi.fn()} photos={[]} />
    )
    expect(screen.queryByTestId('business-card-photo')).not.toBeInTheDocument()
  })

  it('renders photo tile with label when photos exist', () => {
    render(
      <BusinessCard business={business} isSelected={false} onClick={vi.fn()} photos={photos} />
    )
    expect(screen.getByTestId('business-card-photo')).toBeInTheDocument()
    expect(screen.getByText('food')).toBeInTheDocument()
  })
})
