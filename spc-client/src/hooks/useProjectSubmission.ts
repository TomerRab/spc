import { useState } from 'react';
import { UseFormReturn } from 'react-hook-form';
import { useToast } from '@/hooks/use-toast';
import { GitLabCredentials } from '@/types/gitlab';
import { gitlabApi } from '@/lib/api';
import { ProjectForm } from '@/schemas/projectSchema';

export const useProjectSubmission = (
  form: UseFormReturn<ProjectForm>,
  credentials: GitLabCredentials | null
) => {
  const [isLoading, setIsLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [createdProject, setCreatedProject] = useState<any>(null);
  const { toast } = useToast();

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: 'Copied to clipboard!',
        description: 'Command copied successfully',
      });
    } catch (error) {
      toast({
        title: 'Failed to copy',
        description: 'Please copy manually',
        variant: 'destructive',
      });
    }
  };

  const onSubmit = async (data: ProjectForm) => {
    if (!credentials) return;
    
    setIsLoading(true);
    try {
      // Filter out servers without namespaces
      const validServers: Record<string, { namespace: string }> = {};
      if (data.openshiftServers) {
        Object.entries(data.openshiftServers).forEach(([key, server]) => {
          if (server && server.namespace && server.namespace.trim()) {
            validServers[key] = { namespace: server.namespace.trim() };
          }
        });
      }

      // Process delivery server configuration
      const validDeliveryServers: Record<string, { namespace: string }> = {};
      if (data.deliveryConfig?.deliveryServers) {
        Object.entries(data.deliveryConfig.deliveryServers).forEach(([key, server]) => {
          if (server && server.namespace && server.namespace.trim()) {
            validDeliveryServers[key] = { namespace: server.namespace.trim() };
          }
        });
      }

      // Create project data
      const projectData = {
        name: data.name,
        groupId: data.groupId,
        projectType: data.projectType,
        stack: data.stack || undefined,
        visibility: data.visibility,
        defaultBranch: data.defaultBranch,
        openshiftServers: Object.keys(validServers).length > 0 ? validServers : undefined,
        deliveryConfig: data.deliveryConfig?.createDelivery ? {
          createDelivery: true,
          deliveryGroupId: data.deliveryConfig.deliveryGroupId || 0,
          deliveryName: data.deliveryConfig.deliveryName || `${data.name}-delivery`,
          deliveryServers: Object.keys(validDeliveryServers).length > 0 ? validDeliveryServers : {}
        } : undefined,
      };

      const result = await gitlabApi.createProject(projectData, credentials);
      
      // Store result and show success dialog
      setCreatedProject(result);
      setShowSuccess(true);
      form.reset();
      
    } catch (error: any) {
      console.error('Project creation error:', error);
      
      let errorMessage = 'Please check your configuration and try again';
      
      // Extract error message from API response
      if (error?.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error?.message) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      }
      
      toast({
        title: 'Failed to create project',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    showSuccess,
    createdProject,
    onSubmit,
    copyToClipboard,
    setShowSuccess
  };
};