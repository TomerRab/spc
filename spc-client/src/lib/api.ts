import { GitLabCredentials, GitLabGroup, GitLabProject, CreateProjectRequest } from '@/types/gitlab';
import { config } from '@/config/env';
import { parseAPIError } from '@/utils/errorHandler';

// Timeout configurations (in milliseconds)
const TIMEOUTS = {
  DEFAULT: 30000,      // 30 seconds for normal operations
  PROJECT_CREATE: 120000, // 2 minutes for project creation (long operation)
  GROUP_SEARCH: 15000   // 15 seconds for group search
};

const getAuthHeader = (credentials: GitLabCredentials) => ({
  'Authorization': `${credentials.token_type} ${credentials.access_token}`,
  'Content-Type': 'application/json',
});

const fetchWithTimeout = async (url: string, options: RequestInit, timeout: number): Promise<Response> => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw parseAPIError({
        message: 'Request timeout. The operation took too long to complete. Please try again.',
        status_code: 408
      });
    }
    throw error;
  }
};

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const error = parseAPIError({
      message: errorData.message || response.statusText,
      status_code: response.status,
      details: errorData.details
    });
    throw error;
  }
  return response.json();
};

export const gitlabApi = {
  // Get OAuth login URL
  getLoginUrl: async (): Promise<{ login_url: string }> => {
    try {
      const response = await fetchWithTimeout(`${config.API_BASE_URL}/login-url`, {}, TIMEOUTS.DEFAULT);
      return await handleResponse(response);
    } catch (error) {
      throw parseAPIError(error);
    }
  },


  // Get user's GitLab groups
  getGroups: async (credentials: GitLabCredentials): Promise<GitLabGroup[]> => {
    try {
      const response = await fetchWithTimeout(
        `${config.API_BASE_URL}/groups`,
        {
          method: 'GET',
          headers: getAuthHeader(credentials),
        },
        TIMEOUTS.DEFAULT
      );

      const result = await handleResponse(response);
      return result.groups || [];
    } catch (error) {
      throw parseAPIError(error);
    }
  },

  // Search GitLab groups with minimum 3-character query
  searchGroups: async (credentials: GitLabCredentials, query: string): Promise<GitLabGroup[]> => {
    if (query.trim().length < 3) {
      return [];
    }

    try {
      const response = await fetchWithTimeout(
        `${config.API_BASE_URL}/groups/search?q=${encodeURIComponent(query)}`,
        {
          method: 'GET',
          headers: getAuthHeader(credentials),
        },
        TIMEOUTS.GROUP_SEARCH
      );

      const result = await handleResponse(response);
      return result.groups || [];
    } catch (error) {
      const appError = parseAPIError(error);
      // Handle validation errors gracefully for search
      if (appError.type === 'api' && appError.status_code === 400) {
        return [];
      }
      throw appError;
    }
  },

  // Create project
  createProject: async (projectData: CreateProjectRequest, credentials: GitLabCredentials): Promise<any> => {
    try {
      const response = await fetchWithTimeout(
        `${config.API_BASE_URL}/projects/generate-repo`,
        {
          method: 'POST',
          headers: getAuthHeader(credentials),
          body: JSON.stringify(projectData),
        },
        TIMEOUTS.PROJECT_CREATE
      );

      return await handleResponse(response);
    } catch (error) {
      throw parseAPIError(error);
    }
  },

};