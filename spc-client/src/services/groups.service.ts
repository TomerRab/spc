import { gitlabApi } from '@/lib/api';
import { GitLabGroup } from '@/types/gitlab';
import { API_ENDPOINTS } from '@/constants';

export class GroupsService {
  static async getAllGroups(token: string): Promise<{ groups: GitLabGroup[] }> {
    return gitlabApi.get(API_ENDPOINTS.GROUPS.LIST, {
      headers: { Authorization: `Bearer ${token}` }
    });
  }

  static async searchGroups(token: string, query: string): Promise<{ groups: GitLabGroup[] }> {
    return gitlabApi.get(`${API_ENDPOINTS.GROUPS.SEARCH}?q=${encodeURIComponent(query)}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
  }
}

export const groupsService = new GroupsService();