# Frontend Search UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a split-panel internal ops tool for searching and viewing restaurant details backed by the existing FastAPI `/businesses` API.

**Architecture:** Single React page (`/`) with a left scrollable list and a right detail panel. Zustand manages search params and selected business ID. Plain `useEffect`/`useState` in `SearchPage` handles all data fetching. `RootLayout` owns the top bar (search + filters). React Router wraps the app.

**Tech Stack:** React 19, TypeScript, Vite, Tailwind CSS v4, shadcn/ui (Nova preset), Zustand, Axios, React Router DOM v7, Vitest, @testing-library/react

---

### Task 1: Install dependencies, setup testing, clean up boilerplate

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/vitest.config.ts`
- Create: `frontend/src/test/setup.ts`
- Modify: `frontend/src/index.css` (strip Vite template styles, keep shadcn vars)
- Modify: `frontend/src/App.tsx` (replace with RouterProvider)
- Modify: `frontend/src/App.css` (clear)

- [ ] **Step 1: Install runtime and dev dependencies**

Run from `frontend/`:
```bash
npm install react-router-dom
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

- [ ] **Step 2: Add test script to package.json**

In `frontend/package.json`, add to `"scripts"`:
```json
"test": "vitest"
```

- [ ] **Step 3: Create vitest.config.ts**

```ts
// frontend/vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

- [ ] **Step 4: Create test setup file**

```ts
// frontend/src/test/setup.ts
import '@testing-library/jest-dom'
```

- [ ] **Step 5: Clean up index.css**

Replace `frontend/src/index.css` entirely with the following (keeps shadcn vars, removes Vite template typography/layout styles):

```css
@import "tailwindcss";
@import "tw-animate-css";
@import "shadcn/tailwind.css";
@import "@fontsource-variable/geist";

@custom-variant dark (&:is(.dark *));

:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --radius: 0.625rem;
  --sidebar: oklch(0.985 0 0);
  --sidebar-foreground: oklch(0.145 0 0);
  --sidebar-primary: oklch(0.205 0 0);
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.97 0 0);
  --sidebar-accent-foreground: oklch(0.205 0 0);
  --sidebar-border: oklch(0.922 0 0);
  --sidebar-ring: oklch(0.708 0 0);
}

@theme inline {
  --font-heading: var(--font-sans);
  --font-sans: 'Geist Variable', sans-serif;
  --color-sidebar-ring: var(--sidebar-ring);
  --color-sidebar-border: var(--sidebar-border);
  --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
  --color-sidebar-accent: var(--sidebar-accent);
  --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar: var(--sidebar);
  --color-ring: var(--ring);
  --color-input: var(--input);
  --color-border: var(--border);
  --color-destructive: var(--destructive);
  --color-accent-foreground: var(--accent-foreground);
  --color-accent: var(--accent);
  --color-muted-foreground: var(--muted-foreground);
  --color-muted: var(--muted);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-secondary: var(--secondary);
  --color-primary-foreground: var(--primary-foreground);
  --color-primary: var(--primary);
  --color-popover-foreground: var(--popover-foreground);
  --color-popover: var(--popover);
  --color-card-foreground: var(--card-foreground);
  --color-card: var(--card);
  --color-foreground: var(--foreground);
  --color-background: var(--background);
  --radius-sm: calc(var(--radius) * 0.6);
  --radius-md: calc(var(--radius) * 0.8);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) * 1.4);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.205 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.704 0.191 22.216);
  --border: oklch(1 0 0 / 10%);
  --input: oklch(1 0 0 / 15%);
  --ring: oklch(0.556 0 0);
  --sidebar: oklch(0.205 0 0);
  --sidebar-foreground: oklch(0.985 0 0);
  --sidebar-primary: oklch(0.488 0.243 264.376);
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.269 0 0);
  --sidebar-accent-foreground: oklch(0.985 0 0);
  --sidebar-border: oklch(1 0 0 / 10%);
  --sidebar-ring: oklch(0.556 0 0);
}

@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  html,
  body,
  #root {
    height: 100%;
    margin: 0;
  }
  body {
    @apply bg-background text-foreground font-sans;
  }
}
```

- [ ] **Step 6: Clear App.css**

Replace `frontend/src/App.css` with an empty file (just a newline).

- [ ] **Step 7: Verify dev server starts**

```bash
cd frontend && npm run dev
```
Expected: server starts on `http://localhost:5173`, no compile errors.

- [ ] **Step 8: Commit**

```bash
git add frontend/
git commit -m "feat: setup vitest, install router, clean up boilerplate"
```

---

### Task 2: Types

**Files:**
- Create: `frontend/src/types/index.ts`

- [ ] **Step 1: Create types file**

```ts
// frontend/src/types/index.ts

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

export interface TipResult {
  id: number
  text: string | null
  date: string | null
  compliment_count: number | null
  user_id: string | null
}

export interface BusinessDetail extends BusinessResult {
  attributes: Record<string, unknown> | null
  hours: Record<string, string> | null
  tips: TipResult[]
  checkin_count: number
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

export type SearchFilters = {
  category: string | null
  minStars: number | null
  sortBy: 'stars' | 'review_count' | 'name'
  order: 'asc' | 'desc'
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/types/index.ts
git commit -m "feat: add shared TypeScript types"
```

---

### Task 3: Services

**Files:**
- Create: `frontend/src/services/businesses.ts`
- Create: `frontend/src/services/businesses.test.ts`

- [ ] **Step 1: Write failing tests**

```ts
// frontend/src/services/businesses.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import api from '@/lib/api'
import {
  fetchBusinesses,
  fetchBusinessDetail,
  fetchBusinessPhotos,
} from './businesses'

vi.mock('@/lib/api')

const mockGet = vi.mocked(api.get)

beforeEach(() => {
  vi.clearAllMocks()
})

describe('fetchBusinesses', () => {
  it('calls /businesses with params and returns data', async () => {
    const payload = { total: 1, page: 1, limit: 20, results: [] }
    mockGet.mockResolvedValue({ data: payload })

    const result = await fetchBusinesses({ city: 'Miami' })

    expect(mockGet).toHaveBeenCalledWith('businesses', { params: { city: 'Miami' } })
    expect(result).toEqual(payload)
  })
})

describe('fetchBusinessDetail', () => {
  it('calls /businesses/:id and returns data', async () => {
    const payload = { business_id: 'abc', name: 'Test' }
    mockGet.mockResolvedValue({ data: payload })

    const result = await fetchBusinessDetail('abc')

    expect(mockGet).toHaveBeenCalledWith('businesses/abc')
    expect(result).toEqual(payload)
  })
})

describe('fetchBusinessPhotos', () => {
  it('calls /businesses/:id/photos and returns data', async () => {
    const payload = [{ photo_id: 'p1', caption: null, label: 'food' }]
    mockGet.mockResolvedValue({ data: payload })

    const result = await fetchBusinessPhotos('abc')

    expect(mockGet).toHaveBeenCalledWith('businesses/abc/photos')
    expect(result).toEqual(payload)
  })
})
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd frontend && npm test
```
Expected: 3 tests fail — "fetchBusinesses/fetchBusinessDetail/fetchBusinessPhotos is not a function"

- [ ] **Step 3: Implement services**

```ts
// frontend/src/services/businesses.ts
import api from '@/lib/api'
import type {
  BusinessDetail,
  BusinessSearchParams,
  BusinessSearchResponse,
  PhotoResult,
} from '@/types'

export const fetchBusinesses = async (
  params: BusinessSearchParams,
): Promise<BusinessSearchResponse> => {
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

- [ ] **Step 4: Run tests to confirm they pass**

```bash
npm test
```
Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/services/
git commit -m "feat: add businesses service with tests"
```

---

### Task 4: Zustand store

**Files:**
- Create: `frontend/src/store/search-store.ts`
- Create: `frontend/src/store/search-store.test.ts`

- [ ] **Step 1: Write failing tests**

```ts
// frontend/src/store/search-store.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { useSearchStore } from './search-store'

beforeEach(() => {
  useSearchStore.setState({
    city: '',
    category: null,
    minStars: null,
    sortBy: 'stars',
    order: 'desc',
    page: 1,
    selectedId: null,
  })
})

describe('setCity', () => {
  it('sets city and resets page and selectedId', () => {
    useSearchStore.setState({ page: 3, selectedId: 'x' })
    useSearchStore.getState().setCity('Miami')
    const { city, page, selectedId } = useSearchStore.getState()
    expect(city).toBe('Miami')
    expect(page).toBe(1)
    expect(selectedId).toBeNull()
  })
})

describe('setFilter', () => {
  it('merges filter patch and resets page', () => {
    useSearchStore.setState({ page: 2 })
    useSearchStore.getState().setFilter({ minStars: 4, category: 'Mexican' })
    const { minStars, category, page } = useSearchStore.getState()
    expect(minStars).toBe(4)
    expect(category).toBe('Mexican')
    expect(page).toBe(1)
  })
})

describe('setPage', () => {
  it('sets page without touching other state', () => {
    useSearchStore.setState({ city: 'Dallas' })
    useSearchStore.getState().setPage(5)
    const { page, city } = useSearchStore.getState()
    expect(page).toBe(5)
    expect(city).toBe('Dallas')
  })
})

describe('selectBusiness', () => {
  it('sets selectedId', () => {
    useSearchStore.getState().selectBusiness('biz-123')
    expect(useSearchStore.getState().selectedId).toBe('biz-123')
  })

  it('clears selectedId when passed null', () => {
    useSearchStore.setState({ selectedId: 'biz-123' })
    useSearchStore.getState().selectBusiness(null)
    expect(useSearchStore.getState().selectedId).toBeNull()
  })
})
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
npm test
```
Expected: 5 tests fail — "useSearchStore is not a function"

- [ ] **Step 3: Implement store**

```ts
// frontend/src/store/search-store.ts
import { create } from 'zustand'
import type { SearchFilters } from '@/types'

interface SearchState extends SearchFilters {
  city: string
  page: number
  selectedId: string | null
  setCity: (city: string) => void
  setFilter: (patch: Partial<SearchFilters>) => void
  setPage: (page: number) => void
  selectBusiness: (id: string | null) => void
}

export const useSearchStore = create<SearchState>((set) => ({
  city: '',
  category: null,
  minStars: null,
  sortBy: 'stars',
  order: 'desc',
  page: 1,
  selectedId: null,

  setCity: (city) => set({ city, page: 1, selectedId: null }),
  setFilter: (patch) => set((s) => ({ ...s, ...patch, page: 1 })),
  setPage: (page) => set({ page }),
  selectBusiness: (id) => set({ selectedId: id }),
}))
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
npm test
```
Expected: 5 tests pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/store/
git commit -m "feat: add search store with tests"
```

---

### Task 5: StarRating and StatusBadge

**Files:**
- Create: `frontend/src/components/star-rating.tsx`
- Create: `frontend/src/components/status-badge.tsx`
- Create: `frontend/src/components/star-rating.test.tsx`
- Create: `frontend/src/components/status-badge.test.tsx`

- [ ] **Step 1: Write failing tests**

```tsx
// frontend/src/components/star-rating.test.tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { StarRating } from './star-rating'

describe('StarRating', () => {
  it('renders the star and value', () => {
    render(<StarRating value={4.5} />)
    expect(screen.getByText('★ 4.5')).toBeInTheDocument()
  })

  it('renders null when value is null', () => {
    const { container } = render(<StarRating value={null} />)
    expect(container.firstChild).toBeNull()
  })
})
```

```tsx
// frontend/src/components/status-badge.test.tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { StatusBadge } from './status-badge'

describe('StatusBadge', () => {
  it('renders Open when isOpen is true', () => {
    render(<StatusBadge isOpen={true} />)
    expect(screen.getByText('Open')).toBeInTheDocument()
  })

  it('renders Closed when isOpen is false', () => {
    render(<StatusBadge isOpen={false} />)
    expect(screen.getByText('Closed')).toBeInTheDocument()
  })

  it('renders nothing when isOpen is null', () => {
    const { container } = render(<StatusBadge isOpen={null} />)
    expect(container.firstChild).toBeNull()
  })
})
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
npm test
```
Expected: 5 tests fail.

- [ ] **Step 3: Implement StarRating**

```tsx
// frontend/src/components/star-rating.tsx

interface StarRatingProps {
  value: number | null
}

export function StarRating({ value }: StarRatingProps) {
  if (value === null) return null
  return (
    <span className="text-amber-500 font-medium text-sm">★ {value}</span>
  )
}
```

- [ ] **Step 4: Implement StatusBadge**

```tsx
// frontend/src/components/status-badge.tsx

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
```

- [ ] **Step 5: Run tests to confirm they pass**

```bash
npm test
```
Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/star-rating.tsx frontend/src/components/status-badge.tsx \
  frontend/src/components/star-rating.test.tsx frontend/src/components/status-badge.test.tsx
git commit -m "feat: add StarRating and StatusBadge components"
```

---

### Task 6: EmptyState and BusinessCardSkeleton

**Files:**
- Create: `frontend/src/components/empty-state.tsx`
- Create: `frontend/src/components/business-card-skeleton.tsx`

- [ ] **Step 1: Create EmptyState**

```tsx
// frontend/src/components/empty-state.tsx

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
```

- [ ] **Step 2: Create BusinessCardSkeleton**

```tsx
// frontend/src/components/business-card-skeleton.tsx

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
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/empty-state.tsx frontend/src/components/business-card-skeleton.tsx
git commit -m "feat: add EmptyState and BusinessCardSkeleton components"
```

---

### Task 7: SearchBar

**Files:**
- Create: `frontend/src/components/search-bar.tsx`

`SearchBar` reads `city` from the store and calls `setCity` on submit. It keeps a local input value so the user can type freely before submitting.

- [ ] **Step 1: Create SearchBar**

```tsx
// frontend/src/components/search-bar.tsx
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/search-bar.tsx
git commit -m "feat: add SearchBar component"
```

---

### Task 8: FilterBar (install shadcn Select)

**Files:**
- Install: shadcn Select component
- Create: `frontend/src/components/filter-bar.tsx`

`FilterBar` reads from and writes to the store directly. Category is a text input. Min Stars and Sort By use shadcn `Select`. Order is a toggle button.

- [ ] **Step 1: Install shadcn Select**

Run from `frontend/`:
```bash
npx shadcn@latest add select --yes
```
Expected: creates `src/components/ui/select.tsx`.

- [ ] **Step 2: Create FilterBar**

```tsx
// frontend/src/components/filter-bar.tsx
import { useSearchStore } from '@/store/search-store'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const MIN_STARS_OPTIONS = ['1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5']

export function FilterBar() {
  const { category, minStars, sortBy, order, setFilter } = useSearchStore()

  return (
    <div className="flex items-center gap-2">
      {/* Category */}
      <input
        type="text"
        value={category ?? ''}
        onChange={(e) =>
          setFilter({ category: e.target.value.trim() || null })
        }
        placeholder="Category"
        className="text-xs border border-slate-200 rounded-md px-2 py-1.5 bg-slate-50 text-slate-700 placeholder:text-slate-400 outline-none focus:ring-2 focus:ring-slate-300 w-28"
      />

      {/* Min Stars */}
      <Select
        value={minStars?.toString() ?? ''}
        onValueChange={(v) =>
          setFilter({ minStars: v ? parseFloat(v) : null })
        }
      >
        <SelectTrigger className="h-8 text-xs w-28 bg-slate-50 border-slate-200">
          <SelectValue placeholder="Min stars" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="">Any stars</SelectItem>
          {MIN_STARS_OPTIONS.map((s) => (
            <SelectItem key={s} value={s}>
              ★ {s}+
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Sort By */}
      <Select
        value={sortBy}
        onValueChange={(v) =>
          setFilter({ sortBy: v as 'stars' | 'review_count' | 'name' })
        }
      >
        <SelectTrigger className="h-8 text-xs w-32 bg-slate-50 border-slate-200">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="stars">Stars</SelectItem>
          <SelectItem value="review_count">Review count</SelectItem>
          <SelectItem value="name">Name</SelectItem>
        </SelectContent>
      </Select>

      {/* Order toggle */}
      <button
        onClick={() => setFilter({ order: order === 'desc' ? 'asc' : 'desc' })}
        className="h-8 px-2.5 text-xs border border-slate-200 rounded-md bg-slate-50 text-slate-600 hover:bg-slate-100 transition-colors"
      >
        {order === 'desc' ? '↓ Desc' : '↑ Asc'}
      </button>
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/filter-bar.tsx frontend/src/components/ui/select.tsx
git commit -m "feat: add FilterBar with shadcn Select"
```

---

### Task 9: BusinessCard (compound component)

**Files:**
- Create: `frontend/src/components/business-card.tsx`
- Create: `frontend/src/components/business-card.test.tsx`

`BusinessCard.Photo` only renders when `photos` has items. `BusinessCard.Badge` renders Open/Closed. The card highlights when selected (blue left border + light blue bg).

- [ ] **Step 1: Write failing tests**

```tsx
// frontend/src/components/business-card.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { BusinessCard } from './business-card'
import type { BusinessResult, PhotoResult } from '@/types'

const business: BusinessResult = {
  business_id: 'biz-1',
  name: 'Test Place',
  address: '100 Main St',
  city: 'Miami',
  state: 'FL',
  stars: 4.2,
  review_count: 88,
  categories: ['Italian'],
  latitude: 25.77,
  longitude: -80.19,
  is_open: true,
}

const photos: PhotoResult[] = [{ photo_id: 'p1', caption: null, label: 'food' }]

describe('BusinessCard', () => {
  it('renders business name and address', () => {
    render(
      <BusinessCard business={business} isSelected={false} onClick={vi.fn()} photos={[]} />
    )
    expect(screen.getByText('Test Place')).toBeInTheDocument()
    expect(screen.getByText(/100 Main St/)).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const onClick = vi.fn()
    render(
      <BusinessCard business={business} isSelected={false} onClick={onClick} photos={[]} />
    )
    fireEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it('does not render photo tile when photos is empty', () => {
    render(
      <BusinessCard business={business} isSelected={false} onClick={vi.fn()} photos={[]} />
    )
    expect(screen.queryByTestId('business-card-photo')).not.toBeInTheDocument()
  })

  it('renders photo tile with label when photos exist', () => {
    render(
      <BusinessCard business={business} isSelected={false} onClick={vi.fn()} photos={photos} />
    )
    expect(screen.getByTestId('business-card-photo')).toBeInTheDocument()
    expect(screen.getByText('food')).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
npm test
```
Expected: 4 tests fail.

- [ ] **Step 3: Implement BusinessCard**

```tsx
// frontend/src/components/business-card.tsx
import { cn } from '@/lib/utils'
import type { BusinessResult, PhotoResult } from '@/types'
import { StarRating } from './star-rating'
import { StatusBadge } from './status-badge'

interface BusinessCardProps {
  business: BusinessResult
  isSelected: boolean
  onClick: () => void
  photos: PhotoResult[]
}

function BusinessCardPhoto({ photos }: { photos: PhotoResult[] }) {
  if (photos.length === 0) return null
  const label = photos[0].label ?? '📷'
  return (
    <div
      data-testid="business-card-photo"
      className="w-14 h-12 rounded-md bg-amber-100 shrink-0 flex items-center justify-center"
    >
      <span className="text-xs text-amber-700 font-medium capitalize text-center leading-tight px-1">
        {label}
      </span>
    </div>
  )
}

function BusinessCardBadge({ isOpen }: { isOpen: boolean | null }) {
  return <StatusBadge isOpen={isOpen} />
}

function BusinessCard({ business, isSelected, onClick, photos }: BusinessCardProps) {
  const firstCategory = business.categories?.[0] ?? null

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left flex gap-3 px-4 py-3 border-b border-slate-100 hover:bg-slate-50 transition-colors',
        isSelected && 'bg-blue-50 border-l-2 border-l-blue-500 pl-3.5',
      )}
    >
      <BusinessCard.Photo photos={photos} />
      <div className="flex-1 min-w-0">
        <div className="flex justify-between items-start gap-2 mb-0.5">
          <span
            className={cn(
              'text-sm font-semibold truncate',
              isSelected ? 'text-blue-700' : 'text-slate-900',
            )}
          >
            {business.name ?? '—'}
          </span>
          <StarRating value={business.stars} />
        </div>
        <p className="text-xs text-slate-500 truncate mb-1.5">
          {[business.address, firstCategory].filter(Boolean).join(' · ')}
        </p>
        <div className="flex items-center gap-2">
          <BusinessCard.Badge isOpen={business.is_open} />
          {business.review_count != null && (
            <span className="text-xs text-slate-400">{business.review_count} reviews</span>
          )}
        </div>
      </div>
    </button>
  )
}

BusinessCard.Photo = BusinessCardPhoto
BusinessCard.Badge = BusinessCardBadge

export { BusinessCard }
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
npm test
```
Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/business-card.tsx frontend/src/components/business-card.test.tsx
git commit -m "feat: add BusinessCard compound component with tests"
```

---

### Task 10: DetailPanel (compound component)

**Files:**
- Create: `frontend/src/components/detail-panel.tsx`

`DetailPanel` receives `business: BusinessDetail | null`, `photos: PhotoResult[]`, `loading: boolean`. Sub-components only render when they have data.

Hours format: the backend stores hours as `{"Monday": "11:0-22:0", ...}`. Convert to 12-hour display.

- [ ] **Step 1: Create DetailPanel**

```tsx
// frontend/src/components/detail-panel.tsx
import { Fragment } from 'react'
import type { BusinessDetail, PhotoResult, TipResult } from '@/types'
import { StarRating } from './star-rating'
import { StatusBadge } from './status-badge'

// Convert "11:0" or "11:00" → "11:00 AM"
function to12h(time: string): string {
  const [hStr, mStr] = time.split(':')
  const h = parseInt(hStr, 10)
  const m = parseInt(mStr ?? '0', 10)
  const period = h >= 12 ? 'PM' : 'AM'
  const hour = h % 12 || 12
  return `${hour}:${String(m).padStart(2, '0')} ${period}`
}

function formatHours(raw: string): string {
  const [start, end] = raw.split('-')
  return `${to12h(start)} – ${to12h(end)}`
}

const DAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

// Sub-components

function PhotoStrip({ photos }: { photos: PhotoResult[] }) {
  if (photos.length === 0) return null
  return (
    <div className="flex gap-2 px-4 pt-4 overflow-x-auto">
      {photos.map((p) => (
        <div
          key={p.photo_id}
          className="min-w-[90px] h-16 rounded-lg bg-amber-100 flex items-center justify-center shrink-0"
        >
          <span className="text-xs text-amber-700 font-medium capitalize text-center px-2 leading-tight">
            {p.label ?? p.caption ?? '📷'}
          </span>
        </div>
      ))}
    </div>
  )
}

function Hours({ hours }: { hours: Record<string, string> | null }) {
  if (!hours) return null
  const days = DAY_ORDER.filter((d) => hours[d])
  if (days.length === 0) return null
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-3">
      <p className="text-xs font-semibold text-slate-900 mb-2">Hours</p>
      <dl className="grid grid-cols-[72px_1fr] gap-y-1">
        {days.map((day) => (
          <Fragment key={day}>
            <dt className="text-xs text-slate-500">{day.slice(0, 3)}</dt>
            <dd className="text-xs text-slate-900">{formatHours(hours[day])}</dd>
          </Fragment>
        ))}
      </dl>
    </div>
  )
}

function Stats({
  checkinCount,
  latitude,
  longitude,
}: {
  checkinCount: number
  latitude: number | null
  longitude: number | null
}) {
  return (
    <div className="grid grid-cols-2 gap-3">
      <div className="bg-white border border-slate-200 rounded-lg p-3">
        <p className="text-xs text-slate-500 mb-1">Check-ins</p>
        <p className="text-base font-bold text-slate-900">
          {checkinCount.toLocaleString()}
        </p>
      </div>
      <div className="bg-white border border-slate-200 rounded-lg p-3">
        <p className="text-xs text-slate-500 mb-1">Coordinates</p>
        {latitude != null && longitude != null ? (
          <>
            <p className="text-xs font-semibold text-slate-900">
              {latitude.toFixed(4)}° N
            </p>
            <p className="text-xs text-slate-500">{Math.abs(longitude).toFixed(4)}° W</p>
          </>
        ) : (
          <p className="text-xs text-slate-400">—</p>
        )}
      </div>
    </div>
  )
}

function Tips({ tips }: { tips: TipResult[] }) {
  if (tips.length === 0) return null
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-3">
      <p className="text-xs font-semibold text-slate-900 mb-2">Tips</p>
      <ul className="space-y-2">
        {tips.map((tip) => (
          <li
            key={tip.id}
            className="text-xs text-slate-600 border-b border-slate-100 pb-2 last:border-0 last:pb-0"
          >
            "{tip.text}"
            {tip.compliment_count != null && tip.compliment_count > 0 && (
              <span className="ml-2 text-slate-400">— {tip.compliment_count} likes</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}

// Main compound component

interface DetailPanelProps {
  business: BusinessDetail | null
  photos: PhotoResult[]
  loading: boolean
}

function DetailPanel({ business, photos, loading }: DetailPanelProps) {
  if (!business && !loading) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400 text-sm select-none">
        Select a business to view details
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400 text-sm animate-pulse select-none">
        Loading…
      </div>
    )
  }

  if (!business) return null

  const firstCategory = business.categories?.[0] ?? null
  const otherCategories = business.categories?.slice(1) ?? []

  return (
    <div className="h-full overflow-y-auto">
      <DetailPanel.PhotoStrip photos={photos} />

      <div className="px-4 py-3 space-y-3">
        {/* Header */}
        <div className="flex justify-between items-start gap-3">
          <div>
            <h2 className="text-base font-bold text-slate-900 leading-tight mb-0.5">
              {business.name ?? '—'}
            </h2>
            <p className="text-xs text-slate-500">
              {[business.address, business.city, business.state]
                .filter(Boolean)
                .join(', ')}
              {business.is_open !== null && (
                <>
                  {' · '}
                  <StatusBadge isOpen={business.is_open} />
                </>
              )}
            </p>
          </div>
          <div className="text-right shrink-0">
            <StarRating value={business.stars} />
            {business.review_count != null && (
              <p className="text-xs text-slate-400 mt-0.5">
                {business.review_count} reviews
              </p>
            )}
          </div>
        </div>

        {/* Categories */}
        {(firstCategory || otherCategories.length > 0) && (
          <div className="flex flex-wrap gap-1.5">
            {[firstCategory, ...otherCategories].filter(Boolean).map((cat) => (
              <span
                key={cat}
                className="text-xs bg-sky-100 text-sky-700 rounded px-2 py-0.5"
              >
                {cat}
              </span>
            ))}
          </div>
        )}

        <DetailPanel.Hours hours={business.hours} />
        <DetailPanel.Stats
          checkinCount={business.checkin_count}
          latitude={business.latitude}
          longitude={business.longitude}
        />
        <DetailPanel.Tips tips={business.tips} />
      </div>
    </div>
  )
}

DetailPanel.PhotoStrip = PhotoStrip
DetailPanel.Hours = Hours
DetailPanel.Stats = Stats
DetailPanel.Tips = Tips

export { DetailPanel }
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/detail-panel.tsx
git commit -m "feat: add DetailPanel compound component"
```

---

### Task 11: ResultList

**Files:**
- Create: `frontend/src/pages/search/result-list.tsx`

Reads `page`, `setPage`, `selectedId`, `selectBusiness` from the store. Receives `results`, `total`, `limit`, `loading`, `photos` as props.

- [ ] **Step 1: Create ResultList**

```tsx
// frontend/src/pages/search/result-list.tsx
import { useSearchStore } from '@/store/search-store'
import { BusinessCard } from '@/components/business-card'
import { BusinessCardSkeleton } from '@/components/business-card-skeleton'
import type { BusinessResult, PhotoResult } from '@/types'

const SKELETON_COUNT = 6

interface ResultListProps {
  results: BusinessResult[]
  total: number
  limit: number
  loading: boolean
  photos: PhotoResult[]
}

export function ResultList({ results, total, limit, loading, photos }: ResultListProps) {
  const page = useSearchStore((s) => s.page)
  const setPage = useSearchStore((s) => s.setPage)
  const selectedId = useSearchStore((s) => s.selectedId)
  const selectBusiness = useSearchStore((s) => s.selectBusiness)

  const totalPages = Math.ceil(total / limit)

  return (
    <div className="flex flex-col h-full">
      {/* Scrollable list */}
      <div className="flex-1 overflow-y-auto">
        {loading
          ? Array.from({ length: SKELETON_COUNT }).map((_, i) => (
              <BusinessCardSkeleton key={i} />
            ))
          : results.map((biz) => (
              <BusinessCard
                key={biz.business_id}
                business={biz}
                isSelected={biz.business_id === selectedId}
                onClick={() => selectBusiness(biz.business_id)}
                photos={biz.business_id === selectedId ? photos : []}
              />
            ))}
      </div>

      {/* Pagination */}
      {!loading && totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-2 border-t border-slate-100 shrink-0">
          <span className="text-xs text-slate-400">
            Page {page} of {totalPages}
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => setPage(page - 1)}
              disabled={page === 1}
              className="text-xs border border-slate-200 rounded px-2 py-1 text-slate-500 disabled:opacity-40 hover:bg-slate-50 transition-colors"
            >
              ←
            </button>
            {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
              const p = i + 1
              return (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className={`text-xs border rounded px-2 py-1 transition-colors ${
                    p === page
                      ? 'bg-blue-500 border-blue-500 text-white'
                      : 'border-slate-200 text-slate-500 hover:bg-slate-50'
                  }`}
                >
                  {p}
                </button>
              )
            })}
            <button
              onClick={() => setPage(page + 1)}
              disabled={page === totalPages}
              className="text-xs border border-slate-200 rounded px-2 py-1 text-slate-500 disabled:opacity-40 hover:bg-slate-50 transition-colors"
            >
              →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/search/result-list.tsx
git commit -m "feat: add ResultList with pagination"
```

---

### Task 12: SearchPage

**Files:**
- Create: `frontend/src/pages/search/index.tsx`

Owns all fetch state. Triggers list fetch when store params change. Triggers detail + photos fetch when `selectedId` changes.

- [ ] **Step 1: Create SearchPage**

```tsx
// frontend/src/pages/search/index.tsx
import { useEffect, useState } from 'react'
import { useSearchStore } from '@/store/search-store'
import {
  fetchBusinesses,
  fetchBusinessDetail,
  fetchBusinessPhotos,
} from '@/services/businesses'
import { ResultList } from './result-list'
import { DetailPanel } from '@/components/detail-panel'
import { EmptyState } from '@/components/empty-state'
import type { BusinessDetail, BusinessResult, PhotoResult } from '@/types'

const LIMIT = 20

export function SearchPage() {
  const { city, category, minStars, sortBy, order, page, selectedId } =
    useSearchStore()

  // List state
  const [results, setResults] = useState<BusinessResult[]>([])
  const [total, setTotal] = useState(0)
  const [listLoading, setListLoading] = useState(false)
  const [listError, setListError] = useState<string | null>(null)

  // Detail state
  const [detail, setDetail] = useState<BusinessDetail | null>(null)
  const [photos, setPhotos] = useState<PhotoResult[]>([])
  const [detailLoading, setDetailLoading] = useState(false)

  // Fetch list when search params change
  useEffect(() => {
    if (!city) return
    setListLoading(true)
    setListError(null)
    fetchBusinesses({
      city,
      ...(category ? { category } : {}),
      ...(minStars != null ? { min_stars: minStars } : {}),
      sort_by: sortBy,
      order,
      page,
      limit: LIMIT,
    })
      .then((data) => {
        setResults(data.results)
        setTotal(data.total)
      })
      .catch(() => setListError('Failed to load results. Is the backend running?'))
      .finally(() => setListLoading(false))
  }, [city, category, minStars, sortBy, order, page])

  // Fetch detail + photos when selected business changes
  useEffect(() => {
    if (!selectedId) {
      setDetail(null)
      setPhotos([])
      return
    }
    setDetailLoading(true)
    Promise.all([fetchBusinessDetail(selectedId), fetchBusinessPhotos(selectedId)])
      .then(([d, p]) => {
        setDetail(d)
        setPhotos(p)
      })
      .catch(() => {
        setDetail(null)
        setPhotos([])
      })
      .finally(() => setDetailLoading(false))
  }, [selectedId])

  const showEmptyList = !city || (!listLoading && results.length === 0)

  return (
    <div className="flex h-full overflow-hidden">
      {/* Left panel */}
      <div className="w-80 border-r border-slate-200 flex flex-col shrink-0 bg-white">
        {showEmptyList && !listLoading ? (
          <EmptyState variant={city ? 'no-results' : 'idle'} />
        ) : listError ? (
          <div className="p-4 text-xs text-red-500">{listError}</div>
        ) : (
          <ResultList
            results={results}
            total={total}
            limit={LIMIT}
            loading={listLoading}
            photos={photos}
          />
        )}
      </div>

      {/* Right panel */}
      <div className="flex-1 bg-slate-50 overflow-hidden">
        <DetailPanel
          business={detail}
          photos={photos}
          loading={detailLoading}
        />
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/search/index.tsx
git commit -m "feat: add SearchPage with list and detail data fetching"
```

---

### Task 13: RootLayout and wire app

**Files:**
- Create: `frontend/src/layouts/root-layout.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/main.tsx`

- [ ] **Step 1: Create RootLayout**

```tsx
// frontend/src/layouts/root-layout.tsx
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
```

- [ ] **Step 2: Rewrite App.tsx**

```tsx
// frontend/src/App.tsx
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { RootLayout } from './layouts/root-layout'
import { SearchPage } from './pages/search'

const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      { path: '/', element: <SearchPage /> },
    ],
  },
])

function App() {
  return <RouterProvider router={router} />
}

export default App
```

- [ ] **Step 3: Simplify main.tsx**

```tsx
// frontend/src/main.tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

- [ ] **Step 4: Run dev server and smoke-test**

```bash
cd frontend && npm run dev
```

Open `http://localhost:5173`. Expected:
- Top bar shows "OPS PORTAL", search input, filter controls
- Main area shows "Search a city to get started"
- Type a city (e.g. "Phoenix") in the search box and press Enter
- Left panel populates with business cards
- Clicking a card loads detail on the right with hours, stats, and tips

- [ ] **Step 5: Run all tests**

```bash
npm test
```
Expected: all tests pass with no errors.

- [ ] **Step 6: Final commit**

```bash
git add frontend/src/layouts/root-layout.tsx frontend/src/App.tsx frontend/src/main.tsx
git commit -m "feat: wire RootLayout, router, and complete search UI"
```
