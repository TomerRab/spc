import { gitlabApi } from '@/lib/api';
import { ProjectForm } from '@/schemas/projectSchema';
import { GitLabCredentials, CreateProjectRequest } from '@/types/gitlab';

export class ProjectsService {
  static async createProject(credentials: GitLabCredentials, projectData: ProjectForm): Promise<any> {
    return gitlabApi.createProject(projectData as CreateProjectRequest, credentials);
  }
}

export const projectsService = new ProjectsService();