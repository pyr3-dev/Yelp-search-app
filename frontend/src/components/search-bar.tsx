import { useState } from 'react'
import { useSearchStore } from '@/store/search-store'

export function SearchBar() {
  const storeCity = useSearchStore((s) => s.city)
  const storeName = useSearchStore((s) => s.name)
  const setCity = useSearchStore((s) => s.setCity)
  const setFilter = useSearchStore((s) => s.setFilter)
  const [cityValue, setCityValue] = useState(storeCity)
  const [nameValue, setNameValue] = useState(storeName ?? '')

  const submitCity = () => {
    const trimmed = cityValue.trim()
    if (trimmed) setCity(trimmed)
  }

  const submitName = () => {
    setFilter({ name: nameValue.trim() || null })
  }

  return (
    <div className="flex items-center gap-1.5">
      <div className="flex items-center gap-1.5 bg-slate-100 border border-slate-200 rounded-md px-3 py-1.5 w-64 focus-within:ring-2 focus-within:ring-slate-300">
        <span className="text-slate-400 text-sm">🔍</span>
        <input
          type="text"
          value={cityValue}
          onChange={(e) => setCityValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submitCity()}
          onBlur={() => { if (cityValue.trim() !== storeCity) submitCity() }}
          placeholder="Search city..."
          className="bg-transparent text-sm text-slate-700 placeholder:text-slate-400 outline-none w-full"
        />
      </div>
      <div className="flex items-center gap-1.5 bg-slate-100 border border-slate-200 rounded-md px-3 py-1.5 w-56 focus-within:ring-2 focus-within:ring-slate-300">
        <span className="text-slate-400 text-sm">🏪</span>
        <input
          type="text"
          value={nameValue}
          onChange={(e) => setNameValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submitName()}
          onBlur={submitName}
          placeholder="Business name..."
          className="bg-transparent text-sm text-slate-700 placeholder:text-slate-400 outline-none w-full"
        />
      </div>
    </div>
  )
}
