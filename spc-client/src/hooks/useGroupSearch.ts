import { useState, useMemo, useCallback, useEffect, useRef } from 'react';
import debounce from 'lodash.debounce';
import { GitLabGroup, GitLabCredentials } from '@/types/gitlab';
import { GroupsService } from '@/services';
import { FORM_VALIDATION } from '@/constants';
import { useToast } from '@/hooks/use-toast';
import { formatErrorMessage, isAuthError, AppError } from '@/utils/errorHandler';
import { config } from '@/config/env';

interface CacheEntry {
  data: GitLabGroup[];
  timestamp: number;
}

const CACHE_TTL = 5 * 60 * 1000; // 5 minutes
const MAX_CACHE_SIZE = 50; // Maximum number of cached entries
const DEBOUNCE_MS = config.SEARCH_DEBOUNCE_MS;

export const useGroupSearch = (credentials: GitLabCredentials | null) => {
  const [groups, setGroups] = useState<GitLabGroup[]>([]);
  const [loadingGroups, setLoadingGroups] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchError, setSearchError] = useState<string>('');
  const searchCache = useRef<Record<string, CacheEntry>>({});
  const { toast } = useToast();

  const cleanExpiredCache = useCallback(() => {
    const now = Date.now();
    const cache = searchCache.current;
    
    Object.keys(cache).forEach(key => {
      if (now - cache[key].timestamp > CACHE_TTL) {
        delete cache[key];
      }
    });
  }, []);

  const addToCache = useCallback((key: string, data: GitLabGroup[]) => {
    const cache = searchCache.current;
    
    // Clean expired entries first
    cleanExpiredCache();
    
    // If cache is full, remove oldest entry
    if (Object.keys(cache).length >= MAX_CACHE_SIZE) {
      const oldestKey = Object.keys(cache).reduce((oldest, key) => 
        cache[key].timestamp < cache[oldest].timestamp ? key : oldest
      );
      delete cache[oldestKey];
    }
    
    cache[key] = {
      data,
      timestamp: Date.now()
    };
  }, [cleanExpiredCache]);

  const getFromCache = useCallback((key: string): GitLabGroup[] | null => {
    const entry = searchCache.current[key];
    if (!entry) return null;
    
    // Check if entry is expired
    if (Date.now() - entry.timestamp > CACHE_TTL) {
      delete searchCache.current[key];
      return null;
    }
    
    return entry.data;
  }, []);

  const debouncedSearch = useMemo(
    () => debounce(async (query: string) => {
      if (!credentials?.access_token) return;
      
      const trimmedQuery = query.trim();
      
      if (trimmedQuery.length < FORM_VALIDATION.MIN_SEARCH_LENGTH) {
        setGroups([]);
        setSearchError('');
        setLoadingGroups(false);
        return;
      }

      // Client-side input validation for security
      if (trimmedQuery.length > 100) {
        setSearchError('Search query must be 100 characters or less');
        setGroups([]);
        setLoadingGroups(false);
        return;
      }

      // Check for potentially dangerous characters
      const sanitizedPattern = /^[a-zA-Z0-9\s\-_]+$/;
      if (!sanitizedPattern.test(trimmedQuery)) {
        setSearchError('Search query contains invalid characters. Please use only letters, numbers, spaces, hyphens, and underscores.');
        setGroups([]);
        setLoadingGroups(false);
        return;
      }

      // Check cache first
      const cachedGroups = getFromCache(trimmedQuery);
      if (cachedGroups) {
        setGroups(cachedGroups);
        setSearchError('');
        setLoadingGroups(false);
        return;
      }

      setLoadingGroups(true);
      setSearchError('');
      
      try {
        const groups = await GroupsService.searchGroups(credentials, trimmedQuery);
        setGroups(groups);
        addToCache(trimmedQuery, groups);
        
        if (groups.length === 0) {
          setSearchError('No groups found matching your search');
        }
      } catch (error: unknown) {
        const appError = error as AppError;
        const errorMessage = formatErrorMessage(appError);
        
        setSearchError(errorMessage);
        setGroups([]);
        
        // Only show toast for non-validation errors
        if (!(appError.type === 'api' && appError.status_code === 400)) {
          toast({
            title: isAuthError(appError) ? 'Authentication Error' : 'Search Failed',
            description: errorMessage,
            variant: 'destructive',
          });
        }
      } finally {
        setLoadingGroups(false);
      }
    }, DEBOUNCE_MS),
    [credentials, toast, getFromCache, addToCache]
  );

  const handleSearchChange = useCallback((value: string) => {
    setSearchTerm(value);
    debouncedSearch(value);
  }, [debouncedSearch]);

  useEffect(() => {
    // Clean expired cache entries periodically
    const intervalId = setInterval(cleanExpiredCache, 60000); // Every minute
    
    return () => {
      debouncedSearch.cancel();
      clearInterval(intervalId);
      // Clear cache on unmount to prevent memory leaks
      searchCache.current = {};
    };
  }, [debouncedSearch, cleanExpiredCache]);

  return {
    groups,
    loadingGroups,
    searchTerm,
    searchError,
    handleSearchChange,
  };
};