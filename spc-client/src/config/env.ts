interface Config {
  API_BASE_URL: string;
  DEFAULT_BRANCH: string;
  DEFAULT_VISIBILITY: 'private' | 'internal';
  SEARCH_DEBOUNCE_MS: number;
  SEARCH_MIN_CHARS: number;
  COMMON_GROUPS_LIMIT: number;
  SEARCH_RESULTS_LIMIT: number;
}

const getConfig = (): Config => {
  return {
    API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    DEFAULT_BRANCH: import.meta.env.VITE_DEFAULT_BRANCH || 'main',
    DEFAULT_VISIBILITY: (import.meta.env.VITE_DEFAULT_VISIBILITY as 'private' | 'internal') || 'private',
    SEARCH_DEBOUNCE_MS: parseInt(import.meta.env.VITE_SEARCH_DEBOUNCE_MS || '300'),
    SEARCH_MIN_CHARS: parseInt(import.meta.env.VITE_SEARCH_MIN_CHARS || '3'),
    COMMON_GROUPS_LIMIT: parseInt(import.meta.env.VITE_COMMON_GROUPS_LIMIT || '200'),
    SEARCH_RESULTS_LIMIT: parseInt(import.meta.env.VITE_SEARCH_RESULTS_LIMIT || '50'),
  };
};

export const config = getConfig();