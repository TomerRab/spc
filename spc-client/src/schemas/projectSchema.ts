import { z } from 'zod';

export const projectSchema = z.object({
  name: z.string().min(1, 'Project name is required'),
  groupId: z.number().min(1, 'Group selection is required'),
  projectType: z.string().min(1, 'Project type is required'),
  stack: z.string().optional(),
  visibility: z.enum(['private', 'internal']).default('private'),
  defaultBranch: z.string().default('main'),
  openshiftServers: z.record(z.object({ 
    namespace: z.string().min(1, 'Namespace is required') 
  })).optional(),
  deliveryConfig: z.object({
    createDelivery: z.boolean().default(false),
    deliveryGroupId: z.number().optional(),
    deliveryName: z.string().optional(),
    deliveryServers: z.record(z.object({ 
      namespace: z.string().min(1, 'Namespace is required') 
    })).optional(),
  }).optional(),
});

export type ProjectForm = z.infer<typeof projectSchema>;