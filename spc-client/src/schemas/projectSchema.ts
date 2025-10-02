import { z } from 'zod';

export const projectSchema = z.object({
  name: z.string()
    .min(1, 'Project name is required')
    .min(2, 'Project name must be at least 2 characters long')
    .max(100, 'Project name must be 100 characters or fewer')
    .regex(/^[a-zA-Z0-9\s\-_\.]+$/, 'Project name contains invalid characters. Please use only letters, numbers, spaces, hyphens, underscores, and periods'),
  groupId: z.number().min(1, 'Group selection is required'),
  projectType: z.string().min(1, 'Project type is required'),
  stack: z.string().optional(),
  visibility: z.enum(['private', 'internal']).default('private'),
  defaultBranch: z.string().default('main'),
  openshiftServers: z.record(z.object({
    namespace: z.string()
      .min(1, 'Namespace is required')
      .regex(/^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$/, 'Namespace must follow Kubernetes naming rules (lowercase letters, numbers, and hyphens only)')
      .max(63, 'Namespace must be 63 characters or fewer')
  })).optional(),
  deliveryConfig: z.object({
    createDelivery: z.boolean().default(false),
    deliveryGroupId: z.number().optional(),
    deliveryName: z.string()
      .regex(/^[a-zA-Z0-9\s\-_\.]*$/, 'Delivery name contains invalid characters. Please use only letters, numbers, spaces, hyphens, underscores, and periods')
      .optional(),
    deliveryServers: z.record(z.object({
      namespace: z.string()
        .min(1, 'Namespace is required')
        .regex(/^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$/, 'Namespace must follow Kubernetes naming rules (lowercase letters, numbers, and hyphens only)')
        .max(63, 'Namespace must be 63 characters or fewer')
    })).optional(),
  }).optional(),
});

export type ProjectForm = z.infer<typeof projectSchema>;