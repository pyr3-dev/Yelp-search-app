import { Fragment } from 'react'
import type { BusinessDetail, PhotoResult, TipResult } from '@/types'
import { StarRating } from './star-rating'
import { StatusBadge } from './status-badge'

// Convert "11:0" or "11:00" → "11:00 AM"
function to12h(time: string): string {
  const [hStr, mStr] = time.split(':')
  const h = parseInt(hStr, 10)
  const m = parseInt(mStr ?? '0', 10)
  const period = h >= 12 ? 'PM' : 'AM'
  const hour = h % 12 || 12
  return `${hour}:${String(m).padStart(2, '0')} ${period}`
}

function formatHours(raw: string): string {
  const [start, end] = raw.split('-')
  return `${to12h(start)} – ${to12h(end)}`
}

const DAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

// Sub-components

function PhotoStrip({ photos }: { photos: PhotoResult[] }) {
  if (photos.length === 0) return null
  return (
    <div className="flex gap-2 px-4 pt-4 overflow-x-auto">
      {photos.map((p) => (
        <div
          key={p.photo_id}
          className="min-w-[90px] h-16 rounded-lg bg-amber-100 flex items-center justify-center shrink-0"
        >
          <span className="text-xs text-amber-700 font-medium capitalize text-center px-2 leading-tight">
            {p.label ?? p.caption ?? '📷'}
          </span>
        </div>
      ))}
    </div>
  )
}

function Hours({ hours }: { hours: Record<string, string> | null }) {
  if (!hours) return null
  const days = DAY_ORDER.filter((d) => hours[d])
  if (days.length === 0) return null
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-3">
      <p className="text-xs font-semibold text-slate-900 mb-2">Hours</p>
      <dl className="grid grid-cols-[72px_1fr] gap-y-1">
        {days.map((day) => (
          <Fragment key={day}>
            <dt className="text-xs text-slate-500">{day.slice(0, 3)}</dt>
            <dd className="text-xs text-slate-900">{formatHours(hours[day])}</dd>
          </Fragment>
        ))}
      </dl>
    </div>
  )
}

function Stats({
  checkinCount,
  latitude,
  longitude,
}: {
  checkinCount: number
  latitude: number | null
  longitude: number | null
}) {
  return (
    <div className="grid grid-cols-2 gap-3">
      <div className="bg-white border border-slate-200 rounded-lg p-3">
        <p className="text-xs text-slate-500 mb-1">Check-ins</p>
        <p className="text-base font-bold text-slate-900">
          {checkinCount.toLocaleString()}
        </p>
      </div>
      <div className="bg-white border border-slate-200 rounded-lg p-3">
        <p className="text-xs text-slate-500 mb-1">Coordinates</p>
        {latitude != null && longitude != null ? (
          <>
            <p className="text-xs font-semibold text-slate-900">
              {latitude.toFixed(4)}° N
            </p>
            <p className="text-xs text-slate-500">{Math.abs(longitude).toFixed(4)}° W</p>
          </>
        ) : (
          <p className="text-xs text-slate-400">—</p>
        )}
      </div>
    </div>
  )
}

function Tips({ tips }: { tips: TipResult[] }) {
  if (tips.length === 0) return null
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-3">
      <p className="text-xs font-semibold text-slate-900 mb-2">Tips</p>
      <ul className="space-y-2">
        {tips.map((tip) => (
          <li
            key={tip.id}
            className="text-xs text-slate-600 border-b border-slate-100 pb-2 last:border-0 last:pb-0"
          >
            "{tip.text}"
            {tip.compliment_count != null && tip.compliment_count > 0 && (
              <span className="ml-2 text-slate-400">— {tip.compliment_count} likes</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}

// Main compound component

interface DetailPanelProps {
  business: BusinessDetail | null
  photos: PhotoResult[]
  loading: boolean
}

function DetailPanel({ business, photos, loading }: DetailPanelProps) {
  if (!business && !loading) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400 text-sm select-none">
        Select a business to view details
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400 text-sm animate-pulse select-none">
        Loading…
      </div>
    )
  }

  if (!business) return null

  const firstCategory = business.categories?.[0] ?? null
  const otherCategories = business.categories?.slice(1) ?? []

  return (
    <div className="h-full overflow-y-auto">
      <DetailPanel.PhotoStrip photos={photos} />

      <div className="px-4 py-3 space-y-3">
        {/* Header */}
        <div className="flex justify-between items-start gap-3">
          <div>
            <h2 className="text-base font-bold text-slate-900 leading-tight mb-0.5">
              {business.name ?? '—'}
            </h2>
            <p className="text-xs text-slate-500">
              {[business.address, business.city, business.state]
                .filter(Boolean)
                .join(', ')}
              {business.is_open !== null && (
                <>
                  {' · '}
                  <StatusBadge isOpen={business.is_open} />
                </>
              )}
            </p>
          </div>
          <div className="text-right shrink-0">
            <StarRating value={business.stars} />
            {business.review_count != null && (
              <p className="text-xs text-slate-400 mt-0.5">
                {business.review_count} reviews
              </p>
            )}
          </div>
        </div>

        {/* Categories */}
        {(firstCategory || otherCategories.length > 0) && (
          <div className="flex flex-wrap gap-1.5">
            {[firstCategory, ...otherCategories].filter(Boolean).map((cat) => (
              <span
                key={cat}
                className="text-xs bg-sky-100 text-sky-700 rounded px-2 py-0.5"
              >
                {cat}
              </span>
            ))}
          </div>
        )}

        <DetailPanel.Hours hours={business.hours} />
        <DetailPanel.Stats
          checkinCount={business.checkin_count}
          latitude={business.latitude}
          longitude={business.longitude}
        />
        <DetailPanel.Tips tips={business.tips} />
      </div>
    </div>
  )
}

DetailPanel.PhotoStrip = PhotoStrip
DetailPanel.Hours = Hours
DetailPanel.Stats = Stats
DetailPanel.Tips = Tips

export { DetailPanel }
