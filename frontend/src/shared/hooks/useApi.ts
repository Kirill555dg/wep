import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryOptions,
  type UseMutationOptions,
} from '@tanstack/react-query'
import type { Options } from '@/shared/api/generated/sdk.gen'
import { client } from '@/shared/api/generated/client.gen'

// Generic query wrapper for @hey-api SDK calls
export function useApiQuery<T>(
  key: string[],
  fetcher: (opts?: Options<T>) => Promise<T>,
  options?: Omit<UseQueryOptions<T, Error, T, string[]>, 'queryKey' | 'queryFn'>,
) {
  return useQuery({
    queryKey: key,
    queryFn: () => fetcher({ client }),
    ...options,
  })
}

// Generic mutation wrapper for @hey-api SDK calls
export function useApiMutation<T, V>(
  mutationFn: (variables: V, opts?: Options<T>) => Promise<T>,
  options?: Omit<UseMutationOptions<T, Error, V>, 'mutationFn'>,
) {
  return useMutation({
    mutationFn: (variables: V) => mutationFn(variables, { client }),
    ...options,
  })
}

// Invalidate helper
export function useInvalidate() {
  const qc = useQueryClient()
  return {
    invalidate: (key: string[]) => qc.invalidateQueries({ queryKey: key }),
  }
}
