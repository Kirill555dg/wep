import {QueryClient, QueryClientProvider} from '@tanstack/react-query';
import {ReactQueryDevtools} from '@tanstack/react-query-devtools';
import {BrowserRouter} from 'react-router-dom';
import {Toaster} from '@/shared/ui/toaster';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {staleTime: 5 * 60 * 1000, retry: 1, refetchOnWindowFocus: false},
  },
});

export default function Providers({children}: {children: React.ReactNode}) {
  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        {children}
        <Toaster />
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </BrowserRouter>
  );
}
