import { type MaybeRefOrGetter, toValue } from 'vue';

import { useQuery } from '@tanstack/vue-query';

import { DASHBOARD_QUERY_KEYS } from '../constants';
import { fetchSummary, type MetricsFilters } from '../services/dashboardService';

export function useSummaryQuery(filters: MaybeRefOrGetter<MetricsFilters> = {}) {
  return useQuery({
    queryKey: [...DASHBOARD_QUERY_KEYS.SUMMARY, filters],
    queryFn: () => fetchSummary(toValue(filters)),
    refetchInterval: 5000,
  });
}
