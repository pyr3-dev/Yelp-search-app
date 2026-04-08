import api from '@/lib/api'
import type {
  BusinessDetail,
  BusinessSearchParams,
  BusinessSearchResponse,
  PhotoResult,
} from '@/types'

export const fetchBusinesses = async (
  params: BusinessSearchParams,
): Promise<BusinessSearchResponse> => {
  const res = await api.get('businesses', { params })
  return res.data
}

export const fetchBusinessDetail = async (id: string): Promise<BusinessDetail> => {
  const res = await api.get(`businesses/${id}`)
  return res.data
}

export const fetchBusinessPhotos = async (id: string): Promise<PhotoResult[]> => {
  const res = await api.get(`businesses/${id}/photos`)
  return res.data
}
