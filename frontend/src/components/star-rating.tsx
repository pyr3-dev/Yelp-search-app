interface StarRatingProps {
  value: number | null
}

export function StarRating({ value }: StarRatingProps) {
  if (value === null) return null
  return (
    <span className="text-amber-500 font-medium text-sm">★ {value}</span>
  )
}
