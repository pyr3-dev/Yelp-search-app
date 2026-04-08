# Frontend Search UI — Design Spec

**Date:** 2026-04-08
**Context:** Internal ops tool for dispatch/operations staff to look up restaurant details before delivery runs. No brand name shown in the UI.

---

## Overview

A single-page React app with a split-panel layout. The left panel shows a searchable, filterable list of businesses. The right panel shows full detail for the selected business. Light theme throughout.

---

## Pages & Routing

One page, one layout. React Router `createBrowserRouter` defined in `main.tsx`.

```
/  →  RootLayout  →  SearchPage
```

**`src/layouts/root-layout.tsx`**
Top bar shell: wordmark ("OPS PORTAL"), city search input, filter controls, result count. Renders `<Outlet />` below. No sidebar, no footer.

**`src/pages/search/index.tsx`**
The entire app view. Manages fetch state (`loading`, `error`, `results`, `total`, `detail`, `photos`). Renders `ResultList` on the left and `DetailPanel` on the right. No separate detail route — the panel opens inline.

**Page-level colocated subcomponents:**
- `src/pages/search/result-list.tsx` — scrollable list + pagination

`RootLayout` owns the top bar and renders `SearchBar` and `FilterBar` directly; both wire to the store internally so the page doesn't need to pass them props.

---

## Components

All filenames kebab-case. Exports PascalCase. `App.tsx` is the only PascalCase filename exception.

### Shared (`src/components/`)

**`business-card.tsx`** — Compound component.
- `BusinessCard` — outer wrapper, handles selected state styling (blue left border, light blue bg)
- `BusinessCard.Photo` — 56×48 thumbnail; neutral placeholder if no photo
- `BusinessCard.Badge` — Open (green) / Closed (red) pill

Props: `business`, `isSelected`, `onClick`

**`detail-panel.tsx`** — Compound component.
- `DetailPanel` — scrollable right pane; shows empty/prompt state when nothing selected
- `DetailPanel.PhotoStrip` — horizontally scrollable row of styled placeholder tiles showing the photo `label` field (e.g. "food", "inside"). The backend returns photo metadata only — no image URL. Hidden if no photos.
- `DetailPanel.Hours` — renders `hours` dict as day/time grid; hidden if null
- `DetailPanel.Stats` — two-up grid: check-in count + lat/lng coordinates
- `DetailPanel.Tips` — list of tip text + like count; hidden if empty

Props: `business` (BusinessDetail | null), `photos` (PhotoResult[]), `loading`

**`star-rating.tsx`** — Renders `★ {value}` in amber. Props: `value: number`.

**`status-badge.tsx`** — Open/Closed pill. Props: `isOpen: boolean | null`.

**`search-bar.tsx`** — City text input. Submits on Enter or click. Props: `onSearch(city: string)`.

**`filter-bar.tsx`** — Three shadcn `Select` dropdowns: Category (free text from results), Min Stars (0.5 increments 1–5), Sort By (Stars / Review Count / Name) + Order toggle. Props: `onFilterChange(filters)`.

**`empty-state.tsx`** — Shown before first search and on zero results. Props: `variant: 'idle' | 'no-results'`.

**`business-card-skeleton.tsx`** — Animated placeholder matching card dimensions. Shown during list fetch.

---

## Services

**`src/services/businesses.ts`**

```ts
export const fetchBusinesses = async (params: BusinessSearchParams): Promise<BusinessSearchResponse> => {
  const res = await api.get('businesses', { params })
  return res.data
}

export const fetchBusinessDetail = async (id: string): Promise<BusinessDetail> => {
  const res = await api.get(`businesses/${id}`)
  return res.data
}

export const fetchBusinessPhotos = async (id: string): Promise<PhotoResult[]> => {
  const res = await api.get(`businesses/${id}/photos`)
  return res.data
}
```

Never call `api` directly from components or store.

---

## State (Zustand)

**`src/store/search-store.ts`**

```ts
interface SearchState {
  city: string
  category: string | null
  minStars: number | null
  sortBy: 'stars' | 'review_count' | 'name'
  order: 'asc' | 'desc'
  page: number
  selectedId: string | null

  setCity: (city: string) => void
  setFilter: (patch: Partial<SearchFilters>) => void
  setPage: (page: number) => void
  selectBusiness: (id: string | null) => void
}
```

Changing `city`, any filter, or sort resets `page` to 1 and `selectedId` to null.

---

## Data Fetching

Plain `useEffect` + `useState` in `SearchPage`. No external data-fetching library.

- **List fetch** — triggered when `city`, `category`, `minStars`, `sortBy`, `order`, or `page` changes. Shows skeleton cards during load.
- **Detail + photos fetch** — triggered when `selectedId` changes. Both calls fire in parallel (`Promise.all`). Photos are lazy — not fetched until a business is selected.
- **Photo thumbnail on card** — `BusinessCard.Photo` is always a styled placeholder box (the backend returns no image URLs). The selected card's placeholder shows the first photo's `label` from the lazy fetch; all other cards show a generic icon.
- **Error handling** — fetch errors set an `error` string shown in place of the list or detail panel.

---

## Types

**`src/types/index.ts`**

```ts
export interface BusinessResult {
  business_id: string
  name: string | null
  address: string | null
  city: string | null
  state: string | null
  stars: number | null
  review_count: number | null
  categories: string[] | null
  latitude: number | null
  longitude: number | null
  is_open: boolean | null
}

export interface BusinessDetail extends BusinessResult {
  attributes: Record<string, unknown> | null
  hours: Record<string, string> | null
  tips: TipResult[]
  checkin_count: number
}

export interface TipResult {
  id: number
  text: string | null
  date: string | null
  compliment_count: number | null
  user_id: string | null
}

export interface PhotoResult {
  photo_id: string
  caption: string | null
  label: string | null
}

export interface BusinessSearchResponse {
  total: number
  page: number
  limit: number
  results: BusinessResult[]
}

export interface BusinessSearchParams {
  city: string
  category?: string
  min_stars?: number
  sort_by?: 'stars' | 'review_count' | 'name'
  order?: 'asc' | 'desc'
  page?: number
  limit?: number
}
```

---

## Folder Structure (final)

```
src/
├── App.tsx
├── main.tsx
├── index.css
├── assets/
├── components/
│   ├── ui/                        # shadcn (auto-generated)
│   ├── business-card.tsx
│   ├── business-card-skeleton.tsx
│   ├── detail-panel.tsx
│   ├── empty-state.tsx
│   ├── filter-bar.tsx
│   ├── search-bar.tsx
│   ├── star-rating.tsx
│   └── status-badge.tsx
├── layouts/
│   └── root-layout.tsx
├── lib/
│   ├── api.ts
│   └── utils.ts
├── pages/
│   └── search/
│       ├── index.tsx
│       └── result-list.tsx
├── services/
│   └── businesses.ts
├── store/
│   └── search-store.ts
└── types/
    └── index.ts
```
