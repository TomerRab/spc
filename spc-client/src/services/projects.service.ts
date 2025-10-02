import { gitlabApi } from '@/lib/api';
import { ProjectForm } from '@/schemas/projectSchema';
import { GitLabCredentials, CreateProjectRequest, CreateProjectResponse } from '@/types/gitlab';

export class ProjectsService {
  static async createProject(credentials: GitLabCredentials, projectData: ProjectForm): Promise<CreateProjectResponse> {
    return gitlabApi.createProject(projectData as CreateProjectRequest, credentials);
  }
}

export const projectsService = new ProjectsService();