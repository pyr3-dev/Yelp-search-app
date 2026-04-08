import { useState } from 'react'
import { useSearchStore } from '@/store/search-store'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const MIN_STARS_OPTIONS = ['1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5']

export function FilterBar() {
  const { category, minStars, sortBy, order, setFilter } = useSearchStore()
  const [catInput, setCatInput] = useState(category ?? '')

  const submitCategory = () => {
    setFilter({ category: catInput.trim() || null })
  }

  return (
    <div className="flex items-center gap-2">
      {/* Category */}
      <input
        type="text"
        value={catInput}
        onChange={(e) => setCatInput(e.target.value)}
        onBlur={submitCategory}
        onKeyDown={(e) => e.key === 'Enter' && submitCategory()}
        placeholder="Category"
        className="text-xs border border-slate-200 rounded-md px-2 py-1.5 bg-slate-50 text-slate-700 placeholder:text-slate-400 outline-none focus:ring-2 focus:ring-slate-300 w-28"
      />

      {/* Min Stars */}
      <Select
        value={minStars?.toString() ?? 'any'}
        onValueChange={(v) =>
          setFilter({ minStars: v !== 'any' ? parseFloat(v) : null })
        }
      >
        <SelectTrigger className="h-8 text-xs w-28 bg-slate-50 border-slate-200">
          <SelectValue placeholder="Min stars" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="any">Any stars</SelectItem>
          {MIN_STARS_OPTIONS.map((s) => (
            <SelectItem key={s} value={s}>
              ★ {s}+
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Sort By */}
      <Select
        value={sortBy}
        onValueChange={(v) =>
          setFilter({ sortBy: v as 'stars' | 'review_count' | 'name' })
        }
      >
        <SelectTrigger className="h-8 text-xs w-32 bg-slate-50 border-slate-200">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="stars">Stars</SelectItem>
          <SelectItem value="review_count">Review count</SelectItem>
          <SelectItem value="name">Name</SelectItem>
        </SelectContent>
      </Select>

      {/* Order toggle */}
      <button
        onClick={() => setFilter({ order: order === 'desc' ? 'asc' : 'desc' })}
        className="h-8 px-2.5 text-xs border border-slate-200 rounded-md bg-slate-50 text-slate-600 hover:bg-slate-100 transition-colors"
      >
        {order === 'desc' ? '↓ Desc' : '↑ Asc'}
      </button>
    </div>
  )
}
