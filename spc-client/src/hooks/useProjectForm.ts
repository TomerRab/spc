import { useState, useEffect, useMemo } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { gitlabApi } from '@/lib/api';
import { config } from '@/config/env';
import { PROJECT_TYPES, getProjectTypeById } from '@/config/project';
import { projectSchema, ProjectForm } from '@/schemas/projectSchema';
import { GitLabGroup } from '@/types/gitlab';

export const useProjectForm = (groups: GitLabGroup[]) => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { credentials, logout } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [createdProject, setCreatedProject] = useState<any>(null);

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

  // Watch form values
  const projectType = useWatch({ control: form.control, name: 'projectType' });
  const selectedGroupId = useWatch({ control: form.control, name: 'groupId' });
  const openshiftServers = useWatch({ control: form.control, name: 'openshiftServers' }) || {};
  const deliveryConfig = useWatch({ control: form.control, name: 'deliveryConfig' });
  const createDelivery = deliveryConfig?.createDelivery || false;
  const deliveryServers = deliveryConfig?.deliveryServers || {};

  const selectedProjectType = getProjectTypeById(projectType);
  const requiresStack = selectedProjectType?.requiresStack ?? false;
  const requiresDeployment = selectedProjectType?.requiresDeployment ?? false;

  // Find selected group
  const selectedGroup = useMemo(() => {
    return groups.find(group => group.id === selectedGroupId);
  }, [groups, selectedGroupId]);

  // Reset delivery config when project type changes
  useEffect(() => {
    if (projectType !== 'microservice') {
      form.setValue('deliveryConfig.createDelivery', false);
      form.setValue('deliveryConfig.deliveryGroupId', 0);
      form.setValue('deliveryConfig.deliveryName', '');
      form.setValue('deliveryConfig.deliveryServers', {});
    }
  }, [projectType, form]);

  // Reset visibility if group becomes private
  useEffect(() => {
    const currentVisibility = form.getValues('visibility');
    if (selectedGroup?.visibility === 'private' && currentVisibility === 'internal') {
      form.setValue('visibility', 'private');
    }
  }, [selectedGroup, form]);

  return {
    form,
    isLoading,
    showSuccess,
    createdProject,
    projectType,
    selectedGroupId,
    openshiftServers,
    deliveryConfig,
    createDelivery,
    deliveryServers,
    selectedProjectType,
    requiresStack,
    requiresDeployment,
    selectedGroup,
    setShowSuccess,
    setIsLoading,
    setCreatedProject,
    credentials,
    navigate,
    logout,
    toast
  };
};