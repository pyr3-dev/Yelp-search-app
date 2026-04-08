import { useSearchStore } from '@/store/search-store'
import { BusinessCard } from '@/components/business-card'
import { BusinessCardSkeleton } from '@/components/business-card-skeleton'
import type { BusinessResult, PhotoResult } from '@/types'

const SKELETON_COUNT = 6

interface ResultListProps {
  results: BusinessResult[]
  total: number
  limit: number
  loading: boolean
  photos: PhotoResult[]
}

export function ResultList({ results, total, limit, loading, photos }: ResultListProps) {
  const page = useSearchStore((s) => s.page)
  const setPage = useSearchStore((s) => s.setPage)
  const selectedId = useSearchStore((s) => s.selectedId)
  const selectBusiness = useSearchStore((s) => s.selectBusiness)

  const totalPages = Math.ceil(total / limit)

  return (
    <div className="flex flex-col h-full">
      {/* Scrollable list */}
      <div className="flex-1 overflow-y-auto">
        {loading
          ? Array.from({ length: SKELETON_COUNT }).map((_, i) => (
              <BusinessCardSkeleton key={i} />
            ))
          : results.map((biz) => (
              <BusinessCard
                key={biz.business_id}
                business={biz}
                isSelected={biz.business_id === selectedId}
                onClick={() => selectBusiness(biz.business_id)}
                photos={biz.business_id === selectedId ? photos : []}
              />
            ))}
      </div>

      {/* Pagination */}
      {!loading && totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-2 border-t border-slate-100 shrink-0">
          <span className="text-xs text-slate-400">
            Page {page} of {totalPages}
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => setPage(page - 1)}
              disabled={page === 1}
              className="text-xs border border-slate-200 rounded px-2 py-1 text-slate-500 disabled:opacity-40 hover:bg-slate-50 transition-colors"
            >
              ←
            </button>
            {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
              const p = i + 1
              return (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className={`text-xs border rounded px-2 py-1 transition-colors ${
                    p === page
                      ? 'bg-blue-500 border-blue-500 text-white'
                      : 'border-slate-200 text-slate-500 hover:bg-slate-50'
                  }`}
                >
                  {p}
                </button>
              )
            })}
            <button
              onClick={() => setPage(page + 1)}
              disabled={page === totalPages}
              className="text-xs border border-slate-200 rounded px-2 py-1 text-slate-500 disabled:opacity-40 hover:bg-slate-50 transition-colors"
            >
              →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
