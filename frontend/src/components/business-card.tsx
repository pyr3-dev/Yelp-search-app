import { cn } from '@/lib/utils'
import type { BusinessResult } from '@/types'
import { StarRating } from './star-rating'
import { StatusBadge } from './status-badge'

interface BusinessCardProps {
  business: BusinessResult
  isSelected: boolean
  onClick: () => void
}

function BusinessCardPhoto({ business }: { business: BusinessResult }) {
  if (!business.first_photo_id) return null
  return (
    <img
      data-testid="business-card-photo"
      src={`/api/photos/${business.first_photo_id}`}
      alt={business.name ?? ''}
      className="w-20 h-16 rounded-md shrink-0 object-cover bg-slate-100"
      onError={(e) => { e.currentTarget.style.display = 'none' }}
    />
  )
}

function BusinessCardBadge({ isOpen }: { isOpen: boolean | null }) {
  return <StatusBadge isOpen={isOpen} />
}

function BusinessCard({ business, isSelected, onClick }: BusinessCardProps) {
  const firstCategory = business.categories?.[0] ?? null

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left flex gap-3 px-4 py-3 border-b border-slate-100 hover:bg-slate-50 transition-colors',
        isSelected && 'bg-blue-50 border-l-2 border-l-blue-500',
      )}
    >
      <BusinessCard.Photo business={business} />
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
          {[business.address, business.city, firstCategory].filter(Boolean).join(' · ')}
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
