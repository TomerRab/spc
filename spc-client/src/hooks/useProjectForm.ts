import { useMemo } from 'react';
import { useWatch } from 'react-hook-form';
import { PROJECT_TYPES, getProjectTypeById } from '@/config/project';
import { ProjectForm } from '@/schemas/projectSchema';
import { GitLabGroup } from '@/types/gitlab';
import { useFormValidation } from './useFormValidation';
import { useServerManagement } from './useServerManagement';

export const useProjectForm = (groups: GitLabGroup[]) => {
  const form = useFormValidation();
  
  // Watch form values
  const projectType = useWatch({ control: form.control, name: 'projectType' });
  const selectedGroupId = useWatch({ control: form.control, name: 'groupId' });
  const deliveryConfig = useWatch({ control: form.control, name: 'deliveryConfig' });

  // Server management
  const serverManagement = useServerManagement({
    watch: form.watch,
    setValue: form.setValue
  });

  // Computed values
  const selectedProjectType = getProjectTypeById(projectType);
  const requiresStack = selectedProjectType?.requiresStack ?? false;
  const requiresDeployment = selectedProjectType?.requiresDeployment ?? false;
  const createDelivery = deliveryConfig?.createDelivery || false;

  const selectedGroup = useMemo(() => {
    return groups.find(group => group.id === selectedGroupId);
  }, [groups, selectedGroupId]);

  return {
    form,
    // Watched values
    projectType,
    selectedGroupId,
    // Server management
    ...serverManagement,
    // Computed values
    selectedProjectType,
    requiresStack,
    requiresDeployment,
    createDelivery,
    selectedGroup,
  };
};