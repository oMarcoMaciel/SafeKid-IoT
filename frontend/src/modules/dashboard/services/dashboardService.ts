import client from '@/infrastructure/api/client';
import type { AccessLog, PaginatedResponse, Summary } from '@/shared';

export interface MetricsFilters {
  startDate?: string;
  endDate?: string;
}

export const fetchLogs = async (skip = 0, limit = 10, filters: MetricsFilters = {}): Promise<PaginatedResponse<AccessLog>> => {
  const params = {
    skip,
    limit,
    start_date: filters.startDate,
    end_date: filters.endDate,
  };
  const response = await client.get('/metrics/logs', { params });
  return response.data;
};

export const fetchSummary = async (filters: MetricsFilters = {}): Promise<Summary> => {
  const params = {
    start_date: filters.startDate,
    end_date: filters.endDate,
  };
  const response = await client.get('/metrics/summary', { params });
  return response.data;
};
