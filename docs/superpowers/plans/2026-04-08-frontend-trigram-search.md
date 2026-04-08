# Frontend: Name Search + Scope Toggle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose the new backend `name` and `scope` search params in the UI — a business name input next to the city bar and a "Within city / Within 5 miles" pill toggle in the filter row.

**Architecture:** Types updated first, then the store, then components consuming the store, then the page wiring everything to the API. Each layer only depends on the previous one.

**Tech Stack:** React 19, TypeScript, Zustand, Vitest + Testing Library, Tailwind CSS v4, shadcn/ui

---

## File Map

| Action | File | Change |
|---|---|---|
| Modify | `frontend/src/types/index.ts` | Add `name`, `scope`, `'relevance'` to `SearchFilters` and `BusinessSearchParams` |
| Modify | `frontend/src/store/search-store.ts` | Add `name`/`scope` state, default `sortBy` → `'relevance'` |
| Modify | `frontend/src/store/search-store.test.ts` | Update reset state, add name/scope tests |
| Modify | `frontend/src/components/search-bar.tsx` | Add name input alongside city |
| Create | `frontend/src/components/search-bar.test.tsx` | Tests for name input submit behavior |
| Modify | `frontend/src/components/filter-bar.tsx` | Add scope pill toggle, add Relevance to sort dropdown |
| Create | `frontend/src/components/filter-bar.test.tsx` | Tests for scope toggle |
| Modify | `frontend/src/pages/search/index.tsx` | Destructure `name`/`scope` from store, pass to `fetchBusinesses` |

---

## Task 1: Update types

**Files:**
- Modify: `frontend/src/types/index.ts`

- [ ] **Step 1: Update `SearchFilters` and `BusinessSearchParams`**

Open `frontend/src/types/index.ts`. Make these two changes:

Replace `SearchFilters`:
```ts
export type SearchFilters = {
  category: string | null
  minStars: number | null
  name: string | null
  scope: 'city' | 'radius'
  sortBy: 'relevance' | 'stars' | 'review_count' | 'name'
  order: 'asc' | 'desc'
}
```

Replace `BusinessSearchParams`:
```ts
export interface BusinessSearchParams {
  city: string
  category?: string
  min_stars?: number
  name?: string
  scope?: 'city' | 'radius'
  sort_by?: 'relevance' | 'stars' | 'review_count' | 'name'
  order?: 'asc' | 'desc'
  page?: number
  limit?: number
}
```

- [ ] **Step 2: Verify types file parses**

Run from `frontend/`:
```bash
npx tsc --noEmit 2>&1 | grep "types/index"
```

Expected: no errors in `types/index.ts` itself. Errors in `store/search-store.ts` and `filter-bar.tsx` are expected at this stage — those files are updated in Tasks 2 and 4.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types/index.ts
git commit -m "feat: add name, scope, and relevance to frontend search types"
```

---

## Task 2: Update store

**Files:**
- Modify: `frontend/src/store/search-store.ts`
- Modify: `frontend/src/store/search-store.test.ts`

- [ ] **Step 1: Write failing tests for new state fields**

In `frontend/src/store/search-store.test.ts`, update `beforeEach` and add new test block.

Replace the full file with:
```ts
import { describe, it, expect, beforeEach } from 'vitest'
import { useSearchStore } from './search-store'

beforeEach(() => {
  useSearchStore.setState({
    city: '',
    category: null,
    minStars: null,
    name: null,
    scope: 'city',
    sortBy: 'relevance',
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

  it('sets name via setFilter', () => {
    useSearchStore.getState().setFilter({ name: 'Dominos' })
    expect(useSearchStore.getState().name).toBe('Dominos')
  })

  it('clears name to null via setFilter', () => {
    useSearchStore.setState({ name: 'Dominos' })
    useSearchStore.getState().setFilter({ name: null })
    expect(useSearchStore.getState().name).toBeNull()
  })

  it('sets scope to radius via setFilter', () => {
    useSearchStore.getState().setFilter({ scope: 'radius' })
    expect(useSearchStore.getState().scope).toBe('radius')
  })

  it('resets scope back to city via setFilter', () => {
    useSearchStore.setState({ scope: 'radius' })
    useSearchStore.getState().setFilter({ scope: 'city' })
    expect(useSearchStore.getState().scope).toBe('city')
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

- [ ] **Step 2: Run tests — verify new ones fail**

Run from `frontend/`:
```bash
npx vitest run src/store/search-store.test.ts
```

Expected: the 4 new name/scope tests fail because the store doesn't have those fields yet.

- [ ] **Step 3: Update the store**

Replace `frontend/src/store/search-store.ts` with:
```ts
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
  name: null,
  scope: 'city',
  sortBy: 'relevance',
  order: 'desc',
  page: 1,
  selectedId: null,

  setCity: (city) => set({ city, page: 1, selectedId: null }),
  setFilter: (patch) => set((s) => ({ ...s, ...patch, page: 1 })),
  setPage: (page) => set({ page }),
  selectBusiness: (id) => set({ selectedId: id }),
}))
```

- [ ] **Step 4: Run tests — verify all pass**

```bash
npx vitest run src/store/search-store.test.ts
```

Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/store/search-store.ts frontend/src/store/search-store.test.ts
git commit -m "feat: add name and scope to search store, default sortBy to relevance"
```

---

## Task 3: Update SearchBar with name input

**Files:**
- Modify: `frontend/src/components/search-bar.tsx`
- Create: `frontend/src/components/search-bar.test.tsx`

- [ ] **Step 1: Write failing tests**

Create `frontend/src/components/search-bar.test.tsx`:
```tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import { SearchBar } from './search-bar'
import { useSearchStore } from '@/store/search-store'

beforeEach(() => {
  useSearchStore.setState({
    city: '',
    category: null,
    minStars: null,
    name: null,
    scope: 'city',
    sortBy: 'relevance',
    order: 'desc',
    page: 1,
    selectedId: null,
  })
})

describe('SearchBar name input', () => {
  it('renders name input with correct placeholder', () => {
    render(<SearchBar />)
    expect(screen.getByPlaceholderText('Business name...')).toBeInTheDocument()
  })

  it('submits name to store on Enter', () => {
    render(<SearchBar />)
    const input = screen.getByPlaceholderText('Business name...')
    fireEvent.change(input, { target: { value: 'Dominos' } })
    fireEvent.keyDown(input, { key: 'Enter' })
    expect(useSearchStore.getState().name).toBe('Dominos')
  })

  it('submits name to store on blur', () => {
    render(<SearchBar />)
    const input = screen.getByPlaceholderText('Business name...')
    fireEvent.change(input, { target: { value: 'Pizza Hut' } })
    fireEvent.blur(input)
    expect(useSearchStore.getState().name).toBe('Pizza Hut')
  })

  it('sets name to null when input is cleared and blurred', () => {
    useSearchStore.setState({ name: 'Dominos' })
    render(<SearchBar />)
    const input = screen.getByPlaceholderText('Business name...')
    fireEvent.change(input, { target: { value: '' } })
    fireEvent.blur(input)
    expect(useSearchStore.getState().name).toBeNull()
  })
})
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
npx vitest run src/components/search-bar.test.tsx
```

Expected: all 4 tests fail — no name input exists yet.

- [ ] **Step 3: Update SearchBar**

Replace `frontend/src/components/search-bar.tsx` with:
```tsx
import { useState } from 'react'
import { useSearchStore } from '@/store/search-store'

export function SearchBar() {
  const storeCity = useSearchStore((s) => s.city)
  const storeName = useSearchStore((s) => s.name)
  const setCity = useSearchStore((s) => s.setCity)
  const setFilter = useSearchStore((s) => s.setFilter)
  const [cityValue, setCityValue] = useState(storeCity)
  const [nameValue, setNameValue] = useState(storeName ?? '')

  const submitCity = () => {
    const trimmed = cityValue.trim()
    if (trimmed) setCity(trimmed)
  }

  const submitName = () => {
    setFilter({ name: nameValue.trim() || null })
  }

  return (
    <div className="flex items-center gap-1.5">
      <div className="flex items-center gap-1.5 bg-slate-100 border border-slate-200 rounded-md px-3 py-1.5 w-64 focus-within:ring-2 focus-within:ring-slate-300">
        <span className="text-slate-400 text-sm">🔍</span>
        <input
          type="text"
          value={cityValue}
          onChange={(e) => setCityValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submitCity()}
          onBlur={() => { if (cityValue.trim() !== storeCity) submitCity() }}
          placeholder="Search city..."
          className="bg-transparent text-sm text-slate-700 placeholder:text-slate-400 outline-none w-full"
        />
      </div>
      <div className="flex items-center gap-1.5 bg-slate-100 border border-slate-200 rounded-md px-3 py-1.5 w-56 focus-within:ring-2 focus-within:ring-slate-300">
        <span className="text-slate-400 text-sm">🏪</span>
        <input
          type="text"
          value={nameValue}
          onChange={(e) => setNameValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submitName()}
          onBlur={submitName}
          placeholder="Business name..."
          className="bg-transparent text-sm text-slate-700 placeholder:text-slate-400 outline-none w-full"
        />
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
npx vitest run src/components/search-bar.test.tsx
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/search-bar.tsx frontend/src/components/search-bar.test.tsx
git commit -m "feat: add business name search input to SearchBar"
```

---

## Task 4: Update FilterBar with scope toggle and Relevance sort

**Files:**
- Modify: `frontend/src/components/filter-bar.tsx`
- Create: `frontend/src/components/filter-bar.test.tsx`

- [ ] **Step 1: Write failing tests**

Create `frontend/src/components/filter-bar.test.tsx`:
```tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import { FilterBar } from './filter-bar'
import { useSearchStore } from '@/store/search-store'

beforeEach(() => {
  useSearchStore.setState({
    city: '',
    category: null,
    minStars: null,
    name: null,
    scope: 'city',
    sortBy: 'relevance',
    order: 'desc',
    page: 1,
    selectedId: null,
  })
})

describe('FilterBar scope toggle', () => {
  it('renders both scope buttons', () => {
    render(<FilterBar />)
    expect(screen.getByRole('button', { name: 'Within city' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Within 5 miles' })).toBeInTheDocument()
  })

  it('Within city button has active style by default', () => {
    render(<FilterBar />)
    expect(screen.getByRole('button', { name: 'Within city' }).className).toContain('bg-slate-800')
  })

  it('clicking Within 5 miles sets scope to radius in store', () => {
    render(<FilterBar />)
    fireEvent.click(screen.getByRole('button', { name: 'Within 5 miles' }))
    expect(useSearchStore.getState().scope).toBe('radius')
  })

  it('Within 5 miles button has active style when scope is radius', () => {
    useSearchStore.setState({ scope: 'radius' })
    render(<FilterBar />)
    expect(screen.getByRole('button', { name: 'Within 5 miles' }).className).toContain('bg-slate-800')
  })

  it('clicking Within city sets scope back to city in store', () => {
    useSearchStore.setState({ scope: 'radius' })
    render(<FilterBar />)
    fireEvent.click(screen.getByRole('button', { name: 'Within city' }))
    expect(useSearchStore.getState().scope).toBe('city')
  })
})
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
npx vitest run src/components/filter-bar.test.tsx
```

Expected: all 5 tests fail — no scope toggle exists yet.

- [ ] **Step 3: Update FilterBar**

Replace `frontend/src/components/filter-bar.tsx` with:
```tsx
import { useState } from 'react'
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
  const { category, minStars, sortBy, order, scope, setFilter } = useSearchStore()
  const [catInput, setCatInput] = useState(category ?? '')

  const submitCategory = () => {
    setFilter({ category: catInput.trim() || null })
  }

  return (
    <div className="flex items-center gap-2">
      {/* Category */}
      <input
        type="text"
        value={catInput}
        onChange={(e) => setCatInput(e.target.value)}
        onBlur={submitCategory}
        onKeyDown={(e) => e.key === 'Enter' && submitCategory()}
        placeholder="Category"
        className="text-xs border border-slate-200 rounded-md px-2 py-1.5 bg-slate-50 text-slate-700 placeholder:text-slate-400 outline-none focus:ring-2 focus:ring-slate-300 w-28"
      />

      {/* Min Stars */}
      <Select
        value={minStars?.toString() ?? 'any'}
        onValueChange={(v) =>
          setFilter({ minStars: v !== 'any' ? parseFloat(v) : null })
        }
      >
        <SelectTrigger className="h-8 text-xs w-28 bg-slate-50 border-slate-200">
          <SelectValue placeholder="Min stars" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="any">Any stars</SelectItem>
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
          setFilter({ sortBy: v as 'relevance' | 'stars' | 'review_count' | 'name' })
        }
      >
        <SelectTrigger className="h-8 text-xs w-32 bg-slate-50 border-slate-200">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="relevance">Relevance</SelectItem>
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

      {/* Scope toggle */}
      <div className="ml-auto flex overflow-hidden rounded-md border border-slate-200 text-xs">
        <button
          onClick={() => setFilter({ scope: 'city' })}
          className={`px-3 py-1.5 transition-colors ${
            scope === 'city'
              ? 'bg-slate-800 text-white'
              : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
          }`}
        >
          Within city
        </button>
        <button
          onClick={() => setFilter({ scope: 'radius' })}
          className={`px-3 py-1.5 transition-colors ${
            scope === 'radius'
              ? 'bg-slate-800 text-white'
              : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
          }`}
        >
          Within 5 miles
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
npx vitest run src/components/filter-bar.test.tsx
```

Expected: 5 passed.

- [ ] **Step 5: Run full test suite — verify no regressions**

```bash
npx vitest run
```

Expected: all existing tests pass.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/filter-bar.tsx frontend/src/components/filter-bar.test.tsx
git commit -m "feat: add scope toggle and Relevance sort option to FilterBar"
```

---

## Task 5: Wire name and scope into SearchPage

**Files:**
- Modify: `frontend/src/pages/search/index.tsx`

- [ ] **Step 1: Update SearchPage**

Replace `frontend/src/pages/search/index.tsx` with:
```tsx
import { useEffect, useState } from "react";
import { useSearchStore } from "@/store/search-store";
import {
  fetchBusinesses,
  fetchBusinessDetail,
  fetchBusinessPhotos,
} from "@/services/businesses";
import { ResultList } from "./result-list";
import { DetailPanel } from "@/components/detail-panel";
import { EmptyState } from "@/components/empty-state";
import type { BusinessDetail, BusinessResult, PhotoResult } from "@/types";

const LIMIT = 20;

export function SearchPage() {
  const { city, name, scope, category, minStars, sortBy, order, page, selectedId } =
    useSearchStore();

  // List state
  const [results, setResults] = useState<BusinessResult[]>([]);
  const [total, setTotal] = useState(0);
  const [listLoading, setListLoading] = useState(false);
  const [listError, setListError] = useState<string | null>(null);

  // Detail state
  const [detail, setDetail] = useState<BusinessDetail | null>(null);
  const [photos, setPhotos] = useState<PhotoResult[]>([]);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  // Fetch list when search params change
  useEffect(() => {
    if (!city) return;
    setResults([]);
    setListLoading(true);
    setListError(null);
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
      .then((data) => {
        setResults(data.results);
        setTotal(data.total);
      })
      .catch(() =>
        setListError("Failed to load results. Is the backend running?"),
      )
      .finally(() => setListLoading(false));
  }, [city, name, scope, category, minStars, sortBy, order, page]);

  // Fetch detail + photos when selected business changes
  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      setPhotos([]);
      return;
    }
    setDetailLoading(true);
    setDetailError(null);
    Promise.all([
      fetchBusinessDetail(selectedId),
      fetchBusinessPhotos(selectedId),
    ])
      .then(([d, p]) => {
        setDetail(d);
        setPhotos(p);
      })
      .catch(() => {
        setDetail(null);
        setPhotos([]);
        setDetailError("Failed to load business details.");
      })
      .finally(() => setDetailLoading(false));
  }, [selectedId]);

  const showEmptyList = !city || (!listLoading && results.length === 0);

  return (
    <div className="flex h-full overflow-hidden">
      {/* Left panel */}
      <div className="w-80 border-r border-slate-200 flex flex-col shrink-0 bg-white">
        {showEmptyList && !listLoading ? (
          <EmptyState variant={city ? "no-results" : "idle"} />
        ) : listError ? (
          <div className="p-4 text-xs text-red-500">{listError}</div>
        ) : (
          <ResultList
            results={results}
            total={total}
            limit={LIMIT}
            loading={listLoading}
          />
        )}
      </div>

      {/* Right panel */}
      <div className="flex-1 bg-slate-50 overflow-hidden">
        {detailError ? (
          <div className="flex items-center justify-center h-full text-xs text-red-500">
            {detailError}
          </div>
        ) : (
          <DetailPanel
            business={detail}
            photos={photos}
            loading={detailLoading}
          />
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 3: Run full test suite**

```bash
npx vitest run
```

Expected: all tests pass.

- [ ] **Step 4: Smoke test in browser**

Start the dev server from `frontend/`:
```bash
npm run dev
```

Open http://localhost:5173. Verify:
- Two inputs appear in the top bar: "Search city..." and "Business name..."
- Filter row has "Within city | Within 5 miles" pill at the right end
- Sort dropdown includes "Relevance" as first option
- Searching `city=Phoenix` + `name=Dominos` returns Domino's Pizza
- Toggling to "Within 5 miles" and searching changes the result set

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/search/index.tsx
git commit -m "feat: wire name and scope params from store to fetchBusinesses"
```
