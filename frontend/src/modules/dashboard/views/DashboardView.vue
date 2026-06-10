<script setup lang="ts">
import { computed, ref, watch } from 'vue';

import { 
  Activity, 
  Calendar,
  ChevronLeft,
  ChevronRight,
  CreditCard, 
  Filter, 
  Loader2, 
  ShieldAlert 
} from 'lucide-vue-next';

import { useCardsQuery } from '@/modules/cards';
import { AppNavbar } from '@/shared';

import LogsTable from '../components/LogsTable.vue';
import StatCard from '../components/StatCard.vue';
import { useLogsQuery } from '../composables/useLogsQuery';
import { useSummaryQuery } from '../composables/useSummaryQuery';

const timeRange = ref('day');
const customStartDate = ref('');
const customEndDate = ref('');
const currentPage = ref(1);
const limit = 10;

const filters = computed(() => {
  const now = new Date();
  let startDate: Date | undefined;
  const endDate = new Date();

  switch (timeRange.value) {
    case 'day':
      startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      break;
    case 'week':
      startDate = new Date(now.setDate(now.getDate() - 7));
      break;
    case 'month':
      startDate = new Date(now.setMonth(now.getMonth() - 1));
      break;
    case 'year':
      startDate = new Date(now.setFullYear(now.getFullYear() - 1));
      break;
    case 'custom':
      if (customStartDate.value) startDate = new Date(customStartDate.value);
      if (customEndDate.value) {
        const customEnd = new Date(customEndDate.value);
        endDate.setTime(customEnd.getTime() + 86400000 - 1);
      }
      break;
    case 'all':
    default:
      return {};
  }

  return {
    startDate: startDate?.toISOString(),
    endDate: endDate.toISOString(),
  };
});

const skip = computed(() => (currentPage.value - 1) * limit);

const { data: logsData, isLoading: isLoadingLogs } = useLogsQuery(skip, limit, filters);
const { data: summary, isLoading: isLoadingSummary } = useSummaryQuery(filters);
const { data: cards, isLoading: isLoadingCards } = useCardsQuery();

const logs = computed(() => logsData.value?.items || []);
const totalLogs = computed(() => logsData.value?.total || 0);
const totalPages = computed(() => Math.ceil(totalLogs.value / limit));

const isLoading = computed(() => 
  isLoadingLogs.value || 
  isLoadingSummary.value || 
  isLoadingCards.value
);

// Reset to first page when filters change
watch(timeRange, () => {
  currentPage.value = 1;
});
watch([customStartDate, customEndDate], () => {
  if (timeRange.value === 'custom') currentPage.value = 1;
});
</script>

<template>
  <div class="min-h-screen pb-12 bg-gray-50/50">
    <AppNavbar />

    <main class="max-w-7xl mx-auto px-4">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 pt-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">
            Dashboard
          </h1>
          <p class="text-sm text-gray-500">
            Overview of access control and card metrics.
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-3">
          <div class="relative group">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
              <Filter class="h-4 w-4" />
            </div>
            <select
              v-model="timeRange"
              class="block w-full pl-10 pr-10 py-2 text-sm border-gray-200 bg-white rounded-xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all appearance-none cursor-pointer"
            >
              <option value="day">
                Today
              </option>
              <option value="week">
                Last 7 Days
              </option>
              <option value="month">
                Last 30 Days
              </option>
              <option value="year">
                Last Year
              </option>
              <option value="all">
                All Time
              </option>
              <option value="custom">
                Custom Range
              </option>
            </select>
            <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-gray-400">
              <svg
                class="h-4 w-4 fill-current"
                viewBox="0 0 20 20"
              >
                <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
              </svg>
            </div>
          </div>

          <template v-if="timeRange === 'custom'">
            <div class="flex items-center gap-2 bg-white p-1 rounded-xl shadow-sm border border-gray-100">
              <input
                v-model="customStartDate"
                type="date"
                class="bg-transparent border-none text-xs focus:ring-0 cursor-pointer"
              >
              <span class="text-gray-300">to</span>
              <input
                v-model="customEndDate"
                type="date"
                class="bg-transparent border-none text-xs focus:ring-0 cursor-pointer"
              >
            </div>
          </template>
        </div>
      </div>

      <div
        v-if="isLoading && !summary && !logsData"
        class="flex flex-col items-center justify-center py-24 text-gray-400"
      >
        <Loader2 class="w-12 h-12 animate-spin mb-4 text-blue-600" />
        <p class="font-medium">
          Loading dashboard data...
        </p>
      </div>

      <template v-else>
        <!-- Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <StatCard 
            title="Total Scans" 
            :value="summary?.total_scans || 0" 
            :icon="Activity" 
            color-class="bg-blue-50 text-blue-600"
          />
          <StatCard 
            title="Unknown Attempts" 
            :value="summary?.unknown_scans || 0" 
            :icon="ShieldAlert" 
            color-class="bg-red-50 text-red-600"
          />
          <StatCard 
            title="Registered Cards" 
            :value="cards?.length || 0" 
            :icon="CreditCard" 
            color-class="bg-purple-50 text-purple-600"
          />
        </div>

        <!-- Main Content Section -->
        <div class="grid grid-cols-1 gap-8">
          <section class="space-y-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <Calendar class="h-5 w-5 text-gray-400" />
                <h2 class="text-lg font-bold text-gray-800">
                  Access Logs
                </h2>
              </div>
              <div class="text-xs text-gray-400 font-medium bg-gray-100 px-3 py-1 rounded-full">
                {{ totalLogs }} total entries
              </div>
            </div>
            
            <div class="relative min-h-[400px]">
              <div
                v-if="isLoadingLogs"
                class="absolute inset-0 bg-white/50 backdrop-blur-[1px] flex items-center justify-center z-10 rounded-xl"
              >
                <Loader2 class="h-8 w-8 animate-spin text-blue-600" />
              </div>
              <LogsTable :logs="logs" />
            </div>

            <!-- Pagination -->
            <div
              v-if="totalPages > 1"
              class="flex items-center justify-center gap-2 py-4"
            >
              <button
                :disabled="currentPage === 1"
                class="p-2 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                @click="currentPage--"
              >
                <ChevronLeft class="h-5 w-5" />
              </button>
              
              <div class="flex items-center gap-1">
                <template
                  v-for="page in totalPages"
                  :key="page"
                >
                  <button
                    v-if="page === 1 || page === totalPages || (page >= currentPage - 1 && page <= currentPage + 1)"
                    :class="['w-10 h-10 rounded-xl text-sm font-bold transition-all', currentPage === page ? 'bg-blue-600 text-white shadow-lg shadow-blue-100' : 'bg-white text-gray-600 border border-gray-200 hover:border-blue-400 hover:text-blue-600']"
                    @click="currentPage = page"
                  >
                    {{ page }}
                  </button>
                  <span
                    v-else-if="(page === 2 && currentPage > 3) || (page === totalPages - 1 && currentPage < totalPages - 2)"
                    class="px-1 text-gray-400"
                  >
                    ...
                  </span>
                </template>
              </div>

              <button
                :disabled="currentPage === totalPages"
                class="p-2 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                @click="currentPage++"
              >
                <ChevronRight class="h-5 w-5" />
              </button>
            </div>
          </section>
        </div>
      </template>
    </main>
  </div>
</template>
