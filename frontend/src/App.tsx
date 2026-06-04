import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import RunsListPage from './pages/RunsListPage';
import RunDetailPage from './pages/RunDetailPage';
import ComparePage from './pages/ComparePage';
import NewRunPage from './pages/NewRunPage';

const qc = new QueryClient({
  defaultOptions: { queries: { staleTime: 5000, retry: 1 } },
});

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<RunsListPage />} />
            <Route path="runs/:id" element={<RunDetailPage />} />
            <Route path="compare" element={<ComparePage />} />
            <Route path="new" element={<NewRunPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
