import { GitLabGroup, GitLabCredentials } from '@/types/gitlab';
import { gitlabApi } from '@/lib/api';
import { handleAsync, logError } from '@/utils/errorHandler';

export class GroupsService {
  static async getAllGroups(credentials: GitLabCredentials): Promise<GitLabGroup[]> {
    const [response, error] = await handleAsync(
      () => gitlabApi.getGroups(credentials),
      'GroupsService.getAllGroups'
    );
    
    if (error) {
      logError(error, 'Failed to get all groups');
      throw error;
    }
    
    // Handle both old format (direct array) and new format (with wrapper)
    return Array.isArray(response) ? response : response?.groups || [];
  }

  static async searchGroups(credentials: GitLabCredentials, query: string): Promise<GitLabGroup[]> {
    const [response, error] = await handleAsync(
      () => gitlabApi.searchGroups(credentials, query),
      'GroupsService.searchGroups'
    );
    
    if (error) {
      logError(error, `Failed to search groups with query: ${query}`);
      throw error;
    }
    
    // Handle both old format (direct array) and new format (with wrapper)
    return Array.isArray(response) ? response : response?.groups || [];
  }
}

export const groupsService = new GroupsService();