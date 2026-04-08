# Frontend: Name Search + Scope Toggle Design

**Date:** 2026-04-08  
**Scope:** Frontend only — `src/types/`, `src/store/`, `src/components/`, `src/pages/`

---

## Overview

Expose two new backend search params in the frontend UI:

1. **`name`** — optional fuzzy business name search field
2. **`scope`** — toggle between `"city"` (string match) and `"radius"` (geocoded 5-mile Haversine filter)

---

## UI Layout (Option A — approved)

### SearchBar

Add a second text input alongside the existing city input. Both sit in a shared flex row:

```
[ 🔍 Search city... ]  [ 🏪 Business name... ]
```

- Name input submits on Enter and onBlur, same pattern as city
- Name clears when city changes (setting city resets name to `""` / null in store)
- Both inputs share the same visual style (border, radius, focus ring)

### FilterBar

Add a segmented pill toggle at the far right end of the filter row:

```
[ Category ] [ Min stars ▾ ] [ Sort ▾ ] [ ↓ Desc ]  [ Within city | Within 5 miles ]
```

- Two segments: "Within city" (default, active) and "Within 5 miles"
- Active segment: dark fill (`bg-slate-800 text-white`)
- Inactive segment: muted text, transparent background
- Clicking the inactive segment switches scope; clicking the active one is a no-op
- Styled to match the existing ↓ Desc button (same border, height, font size)

The Sort dropdown gains a "Relevance" option at the top (new API default).

---

## State Changes

### `src/types/index.ts`

- `SearchFilters`: add `name: string | null`, `scope: 'city' | 'radius'`, widen `sortBy` to include `'relevance'`
- `BusinessSearchParams`: add `name?: string`, `scope?: 'city' | 'radius'`, widen `sort_by` to include `'relevance'`

### `src/store/search-store.ts`

- Add `name: null` and `scope: 'city'` to initial state
- Change `sortBy` default from `'stars'` to `'relevance'`
- No new actions — both fields are set via existing `setFilter`
- `setCity` already resets `page` and `selectedId`; no need to also reset `name` (user may want to keep name filter when switching city)

### `src/services/businesses.ts`

No logic changes — `fetchBusinesses` passes params as-is to axios. Type update covers it.

### `src/pages/search/index.tsx`

Destructure `name` and `scope` from `useSearchStore` and include them in the `fetchBusinesses` call:

```ts
fetchBusinesses({
  city,
  ...(name ? { name } : {}),
  scope,
  ...(category ? { category } : {}),
  ...(minStars != null ? { min_stars: minStars } : {}),
  sort_by: sortBy,
  order,
  page,
  limit: LIMIT,
})
```

---

## File Map

| Action | File | Change |
|---|---|---|
| Modify | `src/types/index.ts` | Add `name`, `scope`, `'relevance'` to `SearchFilters` and `BusinessSearchParams` |
| Modify | `src/store/search-store.ts` | Add `name`/`scope` state, change `sortBy` default to `'relevance'` |
| Modify | `src/components/search-bar.tsx` | Add name input alongside city |
| Modify | `src/components/filter-bar.tsx` | Add scope pill toggle, add Relevance to sort dropdown |
| Modify | `src/pages/search/index.tsx` | Pass `name` and `scope` to `fetchBusinesses` |

---

## Error Handling

- If `scope=radius` and the backend cannot geocode the city, it returns HTTP 422 with `{"detail": "Could not geocode city: ..."}`. The existing error handling in `SearchPage` (`setListError`) will surface this to the user via the existing empty state / error display.
- No frontend-specific geocoding or geo logic — that lives entirely in the backend.

---

## Testing

- Unit test `SearchBar`: name input updates store `name` on Enter/blur
- Unit test `FilterBar`: scope pill toggle updates store `scope`; Relevance appears in sort dropdown
- Existing `search-store.test.ts` should cover new state fields with minimal additions
