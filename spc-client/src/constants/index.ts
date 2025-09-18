// Form validation constants
export const FORM_VALIDATION = {
  MIN_SEARCH_LENGTH: 3,
} as const;

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login-url',
    CALLBACK: '/auth/callback',
  },
  GROUPS: {
    LIST: '/groups',
    SEARCH: '/groups/search',
  },
  PROJECTS: {
    CREATE: '/projects/generate-repo',
  },
} as const;