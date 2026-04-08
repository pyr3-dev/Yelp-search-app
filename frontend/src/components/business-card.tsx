import { cn } from '@/lib/utils'
import type { BusinessResult, PhotoResult } from '@/types'
import { StarRating } from './star-rating'
import { StatusBadge } from './status-badge'

interface BusinessCardProps {
  business: BusinessResult
  isSelected: boolean
  onClick: () => void
  photos: PhotoResult[]
}

function BusinessCardPhoto({ photos }: { photos: PhotoResult[] }) {
  if (photos.length === 0) return null
  const label = photos[0].label
  return (
    <div
      data-testid="business-card-photo"
      className="w-14 h-12 rounded-md bg-amber-100 shrink-0 flex items-center justify-center"
    >
      <span className="text-xs text-amber-700 font-medium capitalize text-center leading-tight px-1">
        {label}
      </span>
    </div>
  )
}

function BusinessCardBadge({ isOpen }: { isOpen: boolean | null }) {
  return <StatusBadge isOpen={isOpen} />
}

function BusinessCard({ business, isSelected, onClick, photos }: BusinessCardProps) {
  const firstCategory = business.categories?.[0] ?? null

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left flex gap-3 px-4 py-3 border-b border-slate-100 hover:bg-slate-50 transition-colors',
        isSelected && 'bg-blue-50 border-l-2 border-l-blue-500',
      )}
    >
      <BusinessCard.Photo photos={photos} />
      <div className="flex-1 min-w-0">
        <div className="flex justify-between items-start gap-2 mb-0.5">
          <span
            className={cn(
              'text-sm font-semibold truncate',
              isSelected ? 'text-blue-700' : 'text-slate-900',
            )}
          >
            {business.name ?? '—'}
          </span>
          <StarRating value={business.stars} />
        </div>
        <p className="text-xs text-slate-500 truncate mb-1.5">
          {[business.address, firstCategory].filter(Boolean).join(' · ')}
        </p>
        <div className="flex items-center gap-2">
          <BusinessCard.Badge isOpen={business.is_open} />
          {business.review_count != null && (
            <span className="text-xs text-slate-400">{business.review_count} reviews</span>
          )}
        </div>
      </div>
    </button>
  )
}

BusinessCard.Photo = BusinessCardPhoto
BusinessCard.Badge = BusinessCardBadge

export { BusinessCard }
