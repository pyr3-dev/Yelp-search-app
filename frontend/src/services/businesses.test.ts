import { describe, it, expect, vi, beforeEach } from 'vitest'
import api from '@/lib/api'
import {
  fetchBusinesses,
  fetchBusinessDetail,
  fetchBusinessPhotos,
} from './businesses'

vi.mock('@/lib/api')

const mockGet = vi.mocked(api.get)

beforeEach(() => {
  vi.clearAllMocks()
})

describe('fetchBusinesses', () => {
  it('calls /businesses with params and returns data', async () => {
    const payload = { total: 1, page: 1, limit: 20, results: [] }
    mockGet.mockResolvedValue({ data: payload })

    const result = await fetchBusinesses({ city: 'Miami' })

    expect(mockGet).toHaveBeenCalledWith('businesses', { params: { city: 'Miami' } })
    expect(result).toEqual(payload)
  })
})

describe('fetchBusinessDetail', () => {
  it('calls /businesses/:id and returns data', async () => {
    const payload = { business_id: 'abc', name: 'Test' }
    mockGet.mockResolvedValue({ data: payload })

    const result = await fetchBusinessDetail('abc')

    expect(mockGet).toHaveBeenCalledWith('businesses/abc')
    expect(result).toEqual(payload)
  })
})

describe('fetchBusinessPhotos', () => {
  it('calls /businesses/:id/photos and returns data', async () => {
    const payload = [{ photo_id: 'p1', caption: null, label: 'food' }]
    mockGet.mockResolvedValue({ data: payload })

    const result = await fetchBusinessPhotos('abc')

    expect(mockGet).toHaveBeenCalledWith('businesses/abc/photos')
    expect(result).toEqual(payload)
  })
})
