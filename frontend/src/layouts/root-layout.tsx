import { Outlet } from 'react-router-dom'
import { SearchBar } from '@/components/search-bar'
import { FilterBar } from '@/components/filter-bar'

export function RootLayout() {
  return (
    <div className="flex flex-col h-full">
      {/* Top bar */}
      <header className="bg-white border-b border-slate-200 shrink-0">
        {/* Desktop: single row */}
        <div className="hidden md:flex items-center gap-4 px-4 py-2.5">
          <span className="text-xs font-bold tracking-widest text-slate-400 uppercase select-none shrink-0">
            Ops Portal
          </span>
          <SearchBar />
          <FilterBar />
        </div>

        {/* Mobile: stacked */}
        <div className="flex flex-col gap-0 md:hidden">
          <div className="px-3 pt-3 pb-2">
            <SearchBar />
          </div>
          <div className="px-3 pb-2.5">
            <FilterBar />
          </div>
        </div>
      </header>

      {/* Page content */}
      <div className="flex-1 overflow-hidden">
        <Outlet />
      </div>
    </div>
  )
}
