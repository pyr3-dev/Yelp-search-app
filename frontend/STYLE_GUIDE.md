# Frontend Style Guide

## Folder Structure

```
src/
├── assets/
├── components/          # shared, reusable components
│   └── ui/              # shadcn primitives (auto-generated, don't hand-edit)
├── hooks/               # custom React hooks
├── layouts/             # page shell components (nav, sidebar, footer wrappers)
├── lib/
│   ├── api.ts           # axios instance
│   └── utils.ts         # shadcn cn() helper + misc utils
├── pages/               # one folder per route
│   └── dashboard/
│       └── index.tsx
├── services/            # API call functions (consume lib/api.ts)
├── store/               # zustand stores
├── index.css
└── main.tsx
```

---

## File Naming

All files and folders use **kebab-case lowercase**. The only exception is `App.tsx`, which stays PascalCase as the Vite entry-point convention.

```
search-bar.tsx          ✅
business-card.tsx       ✅
App.tsx                 ✅  (exception)
SearchBar.tsx           ❌
businessCard.tsx        ❌
```

Component export names are still PascalCase — only the filename is kebab:

```tsx
// file: src/components/search-bar.tsx
export function SearchBar() { ... }
```

---

## Services

All API calls live in `src/services/`. Each file groups calls by resource. Functions are named exports using `const` arrow functions.

```ts
// src/services/businesses.ts
import api from '@/lib/api'
import type { Business, BusinessSearchParams } from '@/types'

export const fetchBusinesses = async (params: BusinessSearchParams): Promise<Business[]> => {
  const res = await api.get('businesses', { params })
  return res.data
}

export const fetchBusiness = async (id: string): Promise<Business> => {
  const res = await api.get(`businesses/${id}`)
  return res.data
}
```

- Never call `api` directly from a component or store — always go through a service.
- Services return typed data, not raw Axios responses.

---

## Layouts

Layouts live in `src/layouts/`. They own the shell chrome (nav, sidebars, footers) and render `<Outlet />` from React Router for the page content. Do not inline layout structure inside pages.

```tsx
// src/layouts/root-layout.tsx
import { Outlet } from 'react-router-dom'
import { SiteNav } from '@/components/site-nav'

export function RootLayout() {
  return (
    <div className="min-h-screen flex flex-col">
      <SiteNav />
      <main className="flex-1 container mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
```

---

## Pages

Each page lives in its own folder under `src/pages/`. The entry file is always `index.tsx`. Subcomponents used only by that page live in the same folder.

```
src/pages/
├── home/
│   └── index.tsx
├── search/
│   ├── index.tsx
│   └── search-filters.tsx    ← only used by this page
└── business/
    ├── index.tsx
    └── business-hours.tsx
```

Pages are thin: they wire data to layout/components but contain minimal logic.

---

## Components

### Shared components

Reusable components that appear in more than one page go in `src/components/`. Keep them generic — no business-domain assumptions.

### Compound components

Prefer compound component patterns for anything with multiple related sub-parts.

```tsx
// src/components/card.tsx
import { cn } from '@/lib/utils'

function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('rounded-xl border bg-card p-4 shadow-sm', className)} {...props} />
}

function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('mb-2 flex items-start justify-between', className)} {...props} />
}

function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn('font-semibold text-card-foreground', className)} {...props} />
}

function CardBody({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('text-sm text-muted-foreground', className)} {...props} />
}

Card.Header = CardHeader
Card.Title = CardTitle
Card.Body = CardBody

export { Card }
```

Usage:

```tsx
<Card>
  <Card.Header>
    <Card.Title>Joe's Tacos</Card.Title>
  </Card.Header>
  <Card.Body>4.5 ★ · 320 reviews</Card.Body>
</Card>
```

---

## Routing (React Router DOM)

Define routes in `src/main.tsx` using `createBrowserRouter`. Nest page routes under layout routes.

```tsx
// src/main.tsx
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { RootLayout } from '@/layouts/root-layout'
import { HomePage } from '@/pages/home'
import { SearchPage } from '@/pages/search'

const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      { path: '/', element: <HomePage /> },
      { path: '/search', element: <SearchPage /> },
    ],
  },
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)
```

---

## State (Zustand)

Stores live in `src/store/`. One file per domain slice.

```ts
// src/store/search-store.ts
import { create } from 'zustand'

interface SearchState {
  city: string
  category: string
  setCity: (city: string) => void
  setCategory: (category: string) => void
}

export const useSearchStore = create<SearchState>((set) => ({
  city: '',
  category: '',
  setCity: (city) => set({ city }),
  setCategory: (category) => set({ category }),
}))
```

---

## Types

Shared TypeScript types live in `src/types/index.ts`. Co-locate types that are only used in one file.

```ts
// src/types/index.ts
export interface Business {
  business_id: string
  name: string
  city: string
  state: string
  stars: number
  review_count: number
  categories: string[]
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
