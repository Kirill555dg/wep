import { useQuery } from '@tanstack/react-query'
import { getAuthorStatsApiV1StatsMeGet } from '@/shared/api'
import { client } from '@/shared/api/generated/client.gen'

export function useAuthorStats() {
  return useQuery({
    queryKey: ['author-stats'],
    queryFn: async () => {
      const res = await getAuthorStatsApiV1StatsMeGet({ client })
      return res.data
    },
  })
}
