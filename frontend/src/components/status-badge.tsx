interface StatusBadgeProps {
  isOpen: boolean | null
}

export function StatusBadge({ isOpen }: StatusBadgeProps) {
  if (isOpen === null) return null
  return isOpen ? (
    <span className="text-xs bg-green-100 text-green-700 rounded px-1.5 py-0.5 font-medium">
      Open
    </span>
  ) : (
    <span className="text-xs bg-red-100 text-red-600 rounded px-1.5 py-0.5 font-medium">
      Closed
    </span>
  )
}
