import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { projectSchema, ProjectForm } from '@/schemas/projectSchema';
import { config } from '@/config/env';
import { PROJECT_TYPES } from '@/config/project';

export const useFormValidation = () => {
  const form = useForm<ProjectForm>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      name: '',
      groupId: 0,
      projectType: PROJECT_TYPES[0].id,
      stack: undefined,
      visibility: config.DEFAULT_VISIBILITY,
      defaultBranch: config.DEFAULT_BRANCH,
      openshiftServers: {},
      deliveryConfig: {
        createDelivery: false,
        deliveryGroupId: 0,
        deliveryName: '',
        deliveryServers: {},
      },
    },
  });

  return form;
};