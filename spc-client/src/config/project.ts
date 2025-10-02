export interface ProjectTypeConfig {
  id: string;
  label: string;
  description: string;
  requiresStack: boolean;
  requiresDeployment: boolean;
  supportsExistingRepo: boolean;
}

export interface StackConfig {
  id: string;
  label: string;
  description: string;
  fileExtensions: string[];
  defaultFiles: string[];
}

export interface ServerConfig {
  id: string;
  label: string;
  description: string;
  defaultNamespacePrefix?: string;
}

export const PROJECT_TYPES: ProjectTypeConfig[] = [
  {
    id: 'library',
    label: 'Library',
    description: 'A reusable library component',
    requiresStack: true,
    requiresDeployment: false,
    supportsExistingRepo: true,
  },
  {
    id: 'standalone-microservice',
    label: 'Standalone Microservice',
    description: 'Microservice with Helm chart included',
    requiresStack: true,
    requiresDeployment: true,
    supportsExistingRepo: true,
  },
  {
    id: 'microservice',
    label: 'Microservice',
    description: 'Microservice without Helm chart, part of delivery',
    requiresStack: true,
    requiresDeployment: false,
    supportsExistingRepo: true,
  },
  {
    id: 'delivery',
    label: 'Delivery Repo',
    description: 'Deployment repository for managing releases',
    requiresStack: false,
    requiresDeployment: true,
    supportsExistingRepo: false,
  },
];

export const TECHNOLOGY_STACKS: StackConfig[] = [
  {
    id: 'maven',
    label: 'Maven',
    description: 'Java Maven project',
    fileExtensions: ['.java', '.xml'],
    defaultFiles: ['pom.xml', 'src/main/java'],
  },
  {
    id: 'spring',
    label: 'Spring',
    description: 'Spring Boot Java application',
    fileExtensions: ['.java', '.xml', '.yml'],
    defaultFiles: ['pom.xml', 'src/main/java', 'application.yml'],
  },
  {
    id: 'node',
    label: 'Node.js',
    description: 'Node.js backend application',
    fileExtensions: ['.js', '.ts', '.json'],
    defaultFiles: ['package.json', 'src/index.js'],
  },
  {
    id: 'python',
    label: 'Python',
    description: 'Python application',
    fileExtensions: ['.py', '.yml', '.txt'],
    defaultFiles: ['requirements.txt', 'main.py', 'setup.py'],
  },
  {
    id: 'dotnet',
    label: '.NET',
    description: '.NET application',
    fileExtensions: ['.cs', '.csproj', '.sln'],
    defaultFiles: ['Program.cs', 'appsettings.json'],
  },
  {
    id: 'csharp',
    label: 'C#',
    description: 'C# application',
    fileExtensions: ['.cs', '.csproj'],
    defaultFiles: ['Program.cs', 'App.config'],
  },
];

export const DEPLOYMENT_SERVERS: ServerConfig[] = [
  {
    id: 'a',
    label: 'Server A',
    description: 'Production environment',
    defaultNamespacePrefix: 'prod',
  },
  {
    id: 'b',
    label: 'Server B',
    description: 'Production environment',
    defaultNamespacePrefix: 'prod',
  },
  {
    id: 'c',
    label: 'Server C',
    description: 'Test/Staging environment',
    defaultNamespacePrefix: 'test',
  },
  {
    id: 'd',
    label: 'Server D',
    description: 'Test/Staging environment',
    defaultNamespacePrefix: 'test',
  },
];

export const getProjectTypeById = (id: string): ProjectTypeConfig | undefined => {
  return PROJECT_TYPES.find(type => type.id === id);
};

export const getStackById = (id: string): StackConfig | undefined => {
  return TECHNOLOGY_STACKS.find(stack => stack.id === id);
};

export const getServerById = (id: string): ServerConfig | undefined => {
  return DEPLOYMENT_SERVERS.find(server => server.id === id);
};