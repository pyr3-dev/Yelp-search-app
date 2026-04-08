export function BusinessCardSkeleton() {
  return (
    <div className="flex gap-3 px-4 py-3 border-b border-slate-100 animate-pulse">
      <div className="w-14 h-12 rounded-md bg-slate-200 shrink-0" />
      <div className="flex-1 space-y-2 py-0.5">
        <div className="h-3 bg-slate-200 rounded w-3/4" />
        <div className="h-2.5 bg-slate-100 rounded w-1/2" />
        <div className="h-2.5 bg-slate-100 rounded w-1/3" />
      </div>
    </div>
  )
}
