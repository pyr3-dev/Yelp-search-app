import { useState } from 'react'
import { useSearchStore } from '@/store/search-store'

export function SearchBar() {
  const storeCity = useSearchStore((s) => s.city)
  const setCity = useSearchStore((s) => s.setCity)
  const [value, setValue] = useState(storeCity)

  const submit = () => {
    const trimmed = value.trim()
    if (trimmed) setCity(trimmed)
  }

  return (
    <div className="flex items-center gap-1.5 bg-slate-100 border border-slate-200 rounded-md px-3 py-1.5 w-64 focus-within:ring-2 focus-within:ring-slate-300">
      <span className="text-slate-400 text-sm">🔍</span>
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && submit()}
        onBlur={submit}
        placeholder="Search city..."
        className="bg-transparent text-sm text-slate-700 placeholder:text-slate-400 outline-none w-full"
      />
    </div>
  )
}
