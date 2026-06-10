import { type MaybeRefOrGetter, toValue } from 'vue';

import { useQuery } from '@tanstack/vue-query';

import { DASHBOARD_QUERY_KEYS } from '../constants';
import { fetchLogs, type MetricsFilters } from '../services/dashboardService';

export function useLogsQuery(
  skip: MaybeRefOrGetter<number> = 0,
  limit: MaybeRefOrGetter<number> = 10,
  filters: MaybeRefOrGetter<MetricsFilters> = {}
) {
  return useQuery({
    queryKey: [...DASHBOARD_QUERY_KEYS.LOGS, skip, limit, filters],
    queryFn: () => fetchLogs(toValue(skip), toValue(limit), toValue(filters)),
    refetchInterval: 5000,
  });
}
