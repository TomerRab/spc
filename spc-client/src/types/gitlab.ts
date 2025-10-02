export interface GitLabCredentials {
  access_token: string;
  token_type: string;
  expires_in?: number;
}

export interface GitLabGroup {
  id: number;
  name: string;
  full_path: string;
  visibility: 'private' | 'public' | 'internal';
}

export interface GitLabProject {
  id: number;
  name: string;
  path: string;
  full_path: string;
  web_url: string;
  ssh_url_to_repo: string;
  http_url_to_repo: string;
  visibility: 'private' | 'public' | 'internal';
  created_at: string;
  last_activity_at: string;
}

export interface ServerConfig {
  namespace: string;
}

export interface DeliveryConfig {
  createDelivery: boolean;
  deliveryGroupId: number;
  deliveryName: string;
  deliveryServers: Record<string, ServerConfig>;
}

export interface ProjectConfig {
  name: string;
  groupId: number;
  projectType: string;
  stack?: string;
  visibility?: 'private' | 'internal';
  defaultBranch?: string;
  openshiftServers?: Record<string, ServerConfig>;
  deliveryConfig?: DeliveryConfig;
}

export interface CreateProjectRequest extends ProjectConfig {
  // credentials will be sent as Authorization header instead
}

export interface ProjectRepository {
  title: string;
  description: string;
  url: string;
  action_text: string;
  clone_command: string;
}

export interface LegacyProjectRepository {
  name: string;
  url: string;
}

export interface ProjectSummary {
  message: string;
  repos_created: number;
  total_files: number;
  environments?: string[];
}

export interface CreateProjectResponse {
  summary?: ProjectSummary;
  primary_repos?: ProjectRepository[];
  repositories?: LegacyProjectRepository[];
  next_steps?: string[];
}