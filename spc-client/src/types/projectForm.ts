export interface ServerConfig {
  namespace: string;
}

export interface DeliveryConfig {
  createDelivery: boolean;
  deliveryGroupId?: number;
  deliveryName?: string;
  deliveryServers?: Record<string, ServerConfig>;
}

export interface ProjectFormData {
  name: string;
  groupId: number;
  projectType: string;
  stack?: string;
  visibility: 'private' | 'internal';
  defaultBranch: string;
  openshiftServers?: Record<string, ServerConfig>;
  deliveryConfig?: DeliveryConfig;
}