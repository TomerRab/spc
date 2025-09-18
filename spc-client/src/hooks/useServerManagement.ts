import { useState, useCallback } from 'react';
import { UseFormWatch, UseFormSetValue } from 'react-hook-form';
import { ProjectForm } from '@/schemas/projectSchema';

interface UseServerManagementProps {
  watch: UseFormWatch<ProjectForm>;
  setValue: UseFormSetValue<ProjectForm>;
}

export const useServerManagement = ({ watch, setValue }: UseServerManagementProps) => {
  const openshiftServers = watch('openshiftServers') || {};
  const deliveryConfig = watch('deliveryConfig');
  const deliveryServers = deliveryConfig?.deliveryServers || {};

  const isServerSelected = useCallback((serverId: string) => {
    return !!openshiftServers[serverId];
  }, [openshiftServers]);

  const toggleServer = useCallback((serverId: string, checked: boolean) => {
    const currentServers = watch('openshiftServers') || {};
    if (checked) {
      setValue('openshiftServers', {
        ...currentServers,
        [serverId]: { namespace: '' }
      });
    } else {
      const { [serverId]: removed, ...rest } = currentServers;
      setValue('openshiftServers', rest);
    }
  }, [watch, setValue]);

  const isDeliveryServerSelected = useCallback((serverId: string) => {
    return !!deliveryServers[serverId];
  }, [deliveryServers]);

  const toggleDeliveryServer = useCallback((serverId: string, checked: boolean) => {
    const currentConfig = watch('deliveryConfig') || { createDelivery: false, deliveryServers: {} };
    const currentServers = currentConfig.deliveryServers || {};
    
    if (checked) {
      setValue('deliveryConfig.deliveryServers', {
        ...currentServers,
        [serverId]: { namespace: '' }
      });
    } else {
      const { [serverId]: removed, ...rest } = currentServers;
      setValue('deliveryConfig.deliveryServers', rest);
    }
  }, [watch, setValue]);

  return {
    openshiftServers,
    deliveryServers,
    isServerSelected,
    toggleServer,
    isDeliveryServerSelected,
    toggleDeliveryServer
  };
};