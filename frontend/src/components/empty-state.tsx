interface EmptyStateProps {
  variant: 'idle' | 'no-results'
}

export function EmptyState({ variant }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full py-20 text-slate-400 select-none">
      <span className="text-4xl mb-3">{variant === 'idle' ? '🔍' : '😕'}</span>
      <p className="text-sm font-medium text-slate-500">
        {variant === 'idle' ? 'Search a city to get started' : 'No results found'}
      </p>
      {variant === 'no-results' && (
        <p className="text-xs mt-1 text-slate-400">Try a different city or adjust your filters</p>
      )}
    </div>
  )
}
