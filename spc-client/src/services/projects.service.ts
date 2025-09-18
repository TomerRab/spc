import { gitlabApi } from '@/lib/api';
import { ProjectForm } from '@/schemas/projectSchema';
import { API_ENDPOINTS } from '@/constants';

export class ProjectsService {
  static async createProject(token: string, projectData: ProjectForm): Promise<any> {
    return gitlabApi.post(API_ENDPOINTS.PROJECTS.CREATE, projectData, {
      headers: { Authorization: `Bearer ${token}` }
    });
  }
}

export const projectsService = new ProjectsService();