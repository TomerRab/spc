import { useState, useMemo, useCallback, useEffect, useRef } from 'react';
import debounce from 'lodash.debounce';
import { GitLabGroup, GitLabCredentials } from '@/types/gitlab';
import { gitlabApi } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export const useGroupSearch = (credentials: GitLabCredentials | null) => {
  const [groups, setGroups] = useState<GitLabGroup[]>([]);
  const [loadingGroups, setLoadingGroups] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchError, setSearchError] = useState<string>('');
  const searchCache = useRef<Record<string, GitLabGroup[]>>({});
  const { toast } = useToast();

  // Debounced search function
  const debouncedSearch = useMemo(
    () => debounce(async (query: string) => {
      if (!credentials) return;
      
      const trimmedQuery = query.trim();
      
      // Clear results if query is too short
      if (trimmedQuery.length < 3) {
        setGroups([]);
        setSearchError('');
        setLoadingGroups(false);
        return;
      }

      // Check local cache first
      if (searchCache.current[trimmedQuery]) {
        setGroups(searchCache.current[trimmedQuery]);
        setSearchError('');
        setLoadingGroups(false);
        return;
      }

      setLoadingGroups(true);
      setSearchError('');
      
      try {
        const results = await gitlabApi.searchGroups(credentials, trimmedQuery);
        setGroups(results);
        // Cache the results
        searchCache.current[trimmedQuery] = results;
        
        if (results.length === 0) {
          setSearchError('No groups found matching your search');
        }
      } catch (error) {
        console.error('Failed to search groups:', error);
        setSearchError('Failed to search groups. Please try again.');
        setGroups([]);
        toast({
          title: 'Search failed',
          description: 'Unable to search groups. Please check your connection.',
          variant: 'destructive',
        });
      } finally {
        setLoadingGroups(false);
      }
    }, 300),
    [credentials, toast]
  );

  // Handle search input changes
  const handleSearchChange = useCallback((value: string) => {
    setSearchTerm(value);
    debouncedSearch(value);
  }, [debouncedSearch]);

  // Clean up debounce on unmount
  useEffect(() => {
    return () => {
      debouncedSearch.cancel();
    };
  }, [debouncedSearch]);

  return {
    groups,
    loadingGroups,
    searchTerm,
    searchError,
    handleSearchChange,
  };
};