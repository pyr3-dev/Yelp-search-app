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
  const { category, minStars, sortBy, order, scope, setFilter } = useSearchStore()
  const [catInput, setCatInput] = useState(category ?? '')

  const submitCategory = () => {
    setFilter({ category: catInput.trim() || null })
  }

  return (
    <div className="flex items-center gap-2 overflow-x-auto scrollbar-none">
      {/* Category */}
      <input
        type="text"
        value={catInput}
        onChange={(e) => setCatInput(e.target.value)}
        onBlur={submitCategory}
        onKeyDown={(e) => e.key === 'Enter' && submitCategory()}
        placeholder="Category"
        className="text-xs border border-slate-200 rounded-md px-2 py-1.5 bg-slate-50 text-slate-700 placeholder:text-slate-400 outline-none focus:ring-2 focus:ring-slate-300 w-28 shrink-0"
      />

      {/* Min Stars */}
      <Select
        value={minStars?.toString() ?? 'any'}
        onValueChange={(v) =>
          setFilter({ minStars: v !== 'any' ? parseFloat(v) : null })
        }
      >
        <SelectTrigger className="h-8 text-xs w-28 shrink-0 bg-slate-50 border-slate-200">
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
          setFilter({ sortBy: v as 'relevance' | 'stars' | 'review_count' | 'name' })
        }
      >
        <SelectTrigger className="h-8 text-xs w-32 shrink-0 bg-slate-50 border-slate-200">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="relevance">Relevance</SelectItem>
          <SelectItem value="stars">Stars</SelectItem>
          <SelectItem value="review_count">Review count</SelectItem>
          <SelectItem value="name">Name</SelectItem>
        </SelectContent>
      </Select>

      {/* Order toggle */}
      <button
        onClick={() => setFilter({ order: order === 'desc' ? 'asc' : 'desc' })}
        className="h-8 px-2.5 text-xs border border-slate-200 rounded-md bg-slate-50 text-slate-600 hover:bg-slate-100 transition-colors shrink-0"
      >
        {order === 'desc' ? '↓ Desc' : '↑ Asc'}
      </button>

      {/* Scope toggle */}
      <div className="flex shrink-0 overflow-hidden rounded-md border border-slate-200 text-xs">
        <button
          onClick={() => setFilter({ scope: null })}
          className={`px-3 py-1.5 transition-colors ${
            scope === null
              ? 'bg-slate-800 text-white'
              : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
          }`}
        >
          Any
        </button>
        <button
          onClick={() => setFilter({ scope: 'city' })}
          className={`px-3 py-1.5 transition-colors ${
            scope === 'city'
              ? 'bg-slate-800 text-white'
              : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
          }`}
        >
          Within city
        </button>
        <button
          onClick={() => setFilter({ scope: 'radius' })}
          className={`px-3 py-1.5 transition-colors ${
            scope === 'radius'
              ? 'bg-slate-800 text-white'
              : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
          }`}
        >
          Within 5 miles
        </button>
      </div>
    </div>
  )
}
