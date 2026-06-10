/**
 * Utility to format dates consistently across the application.
 * Handles the common issue where backend might send UTC dates without the 'Z' indicator.
 */

const ensureUTC = (dateStr: string): string => {
  if (!dateStr) return dateStr;
  // If it's an ISO-like string and missing timezone indicator, append 'Z'
  if (dateStr.includes('T') && !dateStr.includes('Z') && !dateStr.includes('+')) {
    return `${dateStr}Z`;
  }
  return dateStr;
};

export const formatDate = (dateStr: string | Date | undefined | null): string => {
  if (!dateStr) return 'Never';
  
  const normalized = typeof dateStr === 'string' ? ensureUTC(dateStr) : dateStr;
  const date = new Date(normalized);
  
  return date.toLocaleString();
};

export const formatTime = (dateStr: string | Date | undefined | null): string => {
  if (!dateStr) return 'Never';
  
  const normalized = typeof dateStr === 'string' ? ensureUTC(dateStr) : dateStr;
  const date = new Date(normalized);
  
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export const formatRelativeTime = (dateStr: string | Date | undefined | null): string => {
  if (!dateStr) return '';
  
  const normalized = typeof dateStr === 'string' ? ensureUTC(dateStr) : dateStr;
  const date = new Date(normalized);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'Just now';
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return `${diffInMinutes.toString()}m ago`;
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours.toString()}h ago`;
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) return `${diffInDays.toString()}d ago`;
  
  return date.toLocaleDateString();
};
