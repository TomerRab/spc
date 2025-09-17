import { GitLabCredentials, GitLabGroup, GitLabProject, CreateProjectRequest } from '@/types/gitlab';
import { config } from '@/config/env';

const getAuthHeader = (credentials: GitLabCredentials) => ({
  'Authorization': `${credentials.token_type} ${credentials.access_token}`,
  'Content-Type': 'application/json',
});

export const gitlabApi = {
  // Get OAuth login URL
  getLoginUrl: async (): Promise<{ login_url: string }> => {
    const response = await fetch(`${config.API_BASE_URL}/login-url`);
    
    if (!response.ok) {
      throw new Error('Failed to get login URL');
    }
    
    return response.json();
  },


  // Get user's GitLab groups (kept for backward compatibility)
  getGroups: async (credentials: GitLabCredentials): Promise<GitLabGroup[]> => {
    const response = await fetch(`${config.API_BASE_URL}/groups`, {
      method: 'GET',
      headers: getAuthHeader(credentials),
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch groups');
    }
    
    const result = await response.json();
    return result.groups;
  },

  // Search GitLab groups with minimum 3-character query
  searchGroups: async (credentials: GitLabCredentials, query: string): Promise<GitLabGroup[]> => {
    if (query.trim().length < 3) {
      return [];
    }

    const response = await fetch(`${config.API_BASE_URL}/groups/search?q=${encodeURIComponent(query)}`, {
      method: 'GET',
      headers: getAuthHeader(credentials),
    });
    
    if (!response.ok) {
      if (response.status === 400) {
        // Handle validation error gracefully
        return [];
      }
      throw new Error('Failed to search groups');
    }
    
    const result = await response.json();
    return result.groups;
  },

  // Keep for future use when we want to add existing repo configuration
  // getGroupProjects: async (credentials: GitLabCredentials, groupId: number): Promise<GitLabProject[]> => {
  //   const response = await fetch(`${config.API_BASE_URL}/gitlab/groups/${groupId}/projects`, {
  //     method: 'POST',
  //     headers: {
  //       'Content-Type': 'application/json',
  //     },
  //     body: JSON.stringify(credentials),
  //   });
  //   
  //   if (!response.ok) {
  //     throw new Error('Failed to fetch group projects');
  //   }
  //   
  //   return response.json();
  // },

  // searchProjects: async (credentials: GitLabCredentials, searchTerm: string, groupId?: number): Promise<GitLabProject[]> => {
  //   const queryParams = new URLSearchParams({
  //     q: searchTerm,
  //     ...(groupId && { group_id: groupId.toString() }),
  //   });

  //   const response = await fetch(`${config.API_BASE_URL}/gitlab/projects/search?${queryParams}`, {
  //     method: 'POST',
  //     headers: {
  //       'Content-Type': 'application/json',
  //     },
  //     body: JSON.stringify(credentials),
  //   });
  //   
  //   if (!response.ok) {
  //     throw new Error('Failed to search projects');
  //   }
  //   
  //   return response.json();
  // },

  // Create project
  createProject: async (projectData: CreateProjectRequest, credentials: GitLabCredentials): Promise<any> => {
    const response = await fetch(`${config.API_BASE_URL}/generate-repo`, {
      method: 'POST',
      headers: getAuthHeader(credentials),
      body: JSON.stringify(projectData),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create project');
    }
    
    return response.json();
  },

  // Keep for future use when we want to add existing repo configuration
  // configureExistingProject: async (configData: ConfigureExistingProjectRequest): Promise<any> => {
  //   const response = await fetch(`${config.API_BASE_URL}/gitlab/configure-existing-project`, {
  //     method: 'POST',
  //     headers: {
  //       'Content-Type': 'application/json',
  //     },
  //     body: JSON.stringify(configData),
  //   });
  //   
  //   if (!response.ok) {
  //     throw new Error('Failed to configure existing project');
  //   }
  //   
  //   return response.json();
  // },
};