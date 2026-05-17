import {useQuery} from '@tanstack/react-query';
import {
  getAuthorStatsApiV1StatsMeGet,
  getTestStatsApiV1StatsTestsTestIdGet,
} from '@/shared/api/client/stats';

export function useAuthorStats() {
  return useQuery({
    queryKey: ['author-stats'],
    queryFn: async () => {
      const res = await getAuthorStatsApiV1StatsMeGet();
      if ('data' in res && 'status' in res && res.status >= 200 && res.status < 300) {
        return res.data;
      }
      throw new Error('Failed to load author stats');
    },
  });
}

export function useTestStats(testId: number) {
  return useQuery({
    queryKey: ['test-stats', testId],
    queryFn: async () => {
      const res = await getTestStatsApiV1StatsTestsTestIdGet(testId);
      if ('data' in res && 'status' in res && res.status >= 200 && res.status < 300) {
        return res.data;
      }
      throw new Error('Failed to load test stats');
    },
    enabled: !!testId,
  });
}
