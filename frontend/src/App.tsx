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
