import { Outlet } from 'react-router-dom'
import { SearchBar } from '@/components/search-bar'
import { FilterBar } from '@/components/filter-bar'

export function RootLayout() {
  return (
    <div className="flex flex-col h-full">
      {/* Top bar */}
      <header className="flex items-center gap-4 px-4 py-2.5 bg-white border-b border-slate-200 shrink-0">
        <span className="text-xs font-bold tracking-widest text-slate-400 uppercase select-none">
          Ops Portal
        </span>
        <SearchBar />
        <FilterBar />
      </header>

      {/* Page content */}
      <div className="flex-1 overflow-hidden">
        <Outlet />
      </div>
    </div>
  )
}
