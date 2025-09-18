import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { useAuth } from '@/contexts/AuthContext';
import { useGroupSearch } from '@/hooks/useGroupSearch';
import { useProjectForm } from '@/hooks/useProjectForm';
import { useProjectSubmission } from '@/hooks/useProjectSubmission';
import { GroupSelector, ProjectTypeSelector, TechnologyStackSelector, VisibilitySelector } from '@/components/selectors';
import { DeploymentConfig, DeliveryConfig } from '@/components/project-creation';
import { ProjectSuccessDialog } from '@/components/forms';

const CreateProject = () => {
  const navigate = useNavigate();
  const { credentials, logout } = useAuth();
  const [groupOpen, setGroupOpen] = useState(false);
  const [showDeliveryOptions, setShowDeliveryOptions] = useState(false);

  // Group search functionality
  const {
    groups,
    loadingGroups,
    searchTerm,
    searchError,
    handleSearchChange,
  } = useGroupSearch(credentials);

  // Form management
  const {
    form,
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
  } = useProjectForm(groups);

  // Form submission
  const {
    isLoading,
    showSuccess,
    createdProject,
    onSubmit,
    copyToClipboard,
    setShowSuccess
  } = useProjectSubmission(form, credentials);

  // Navigation guard
  useEffect(() => {
    if (!credentials) {
      navigate('/');
      return;
    }
  }, [credentials, navigate]);

  // Update delivery options visibility
  useEffect(() => {
    const shouldShow = projectType === 'microservice';
    setShowDeliveryOptions(shouldShow);
  }, [projectType]);

  // Server selection helpers
  const isServerSelected = (serverKey: string) => !!openshiftServers[serverKey];
  const isDeliveryServerSelected = (serverKey: string) => !!deliveryServers[serverKey];

  const toggleServer = (serverKey: string, checked: boolean) => {
    const currentServers = form.getValues('openshiftServers') || {};
    if (checked) {
      form.setValue('openshiftServers', {
        ...currentServers,
        [serverKey]: { namespace: '' }
      });
    } else {
      const { [serverKey]: removed, ...remainingServers } = currentServers;
      form.setValue('openshiftServers', remainingServers);
    }
  };

  const toggleDeliveryServer = (serverKey: string, checked: boolean) => {
    const currentDeliveryConfig = form.getValues('deliveryConfig') || {};
    const currentServers = currentDeliveryConfig.deliveryServers || {};
    
    if (checked) {
      form.setValue('deliveryConfig', {
        ...currentDeliveryConfig,
        deliveryServers: {
          ...currentServers,
          [serverKey]: { namespace: '' }
        }
      });
    } else {
      const { [serverKey]: removed, ...remainingServers } = currentServers;
      form.setValue('deliveryConfig', {
        ...currentDeliveryConfig,
        deliveryServers: remainingServers
      });
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <Button variant="ghost" onClick={handleLogout} className="flex items-center gap-2">
            <ArrowLeft className="h-4 w-4" />
            Sign Out
          </Button>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <img 
                src="/favicon.svg" 
                alt="Solid Project Creator" 
                className="h-6 w-6"
              />
              <CardTitle>Create New GitLab Project</CardTitle>
            </div>
            <CardDescription>
              Configure your new repository with the tools and settings your team needs
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                {/* Project Name */}
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Project Name</FormLabel>
                      <FormControl>
                        <Input placeholder="my-awesome-project" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Group Selection */}
                <FormField
                  control={form.control}
                  name="groupId"
                  render={({ field }) => (
                    <GroupSelector
                      groups={groups}
                      loadingGroups={loadingGroups}
                      searchTerm={searchTerm}
                      searchError={searchError}
                      groupOpen={groupOpen}
                      selectedGroupId={field.value}
                      onSearchChange={handleSearchChange}
                      onGroupSelect={(groupId) => {
                        field.onChange(groupId);
                        setGroupOpen(false);
                      }}
                      onOpenChange={setGroupOpen}
                    />
                  )}
                />

                {/* Project Type */}
                <FormField
                  control={form.control}
                  name="projectType"
                  render={({ field }) => (
                    <ProjectTypeSelector value={field.value} onChange={field.onChange} />
                  )}
                />

                {/* Technology Stack */}
                {requiresStack && (
                  <FormField
                    control={form.control}
                    name="stack"
                    render={({ field }) => (
                      <TechnologyStackSelector value={field.value} onChange={field.onChange} />
                    )}
                  />
                )}

                {/* Visibility */}
                <FormField
                  control={form.control}
                  name="visibility"
                  render={({ field }) => (
                    <VisibilitySelector 
                      value={field.value} 
                      onChange={field.onChange}
                      selectedGroup={selectedGroup}
                    />
                  )}
                />

                {/* Delivery Configuration */}
                {showDeliveryOptions && (
                  <DeliveryConfig
                    control={form.control}
                    watch={form.watch}
                    groups={groups}
                    loadingGroups={loadingGroups}
                    searchTerm={searchTerm}
                    searchError={searchError}
                    groupOpen={groupOpen}
                    onSearchChange={handleSearchChange}
                    onOpenChange={setGroupOpen}
                    createDelivery={createDelivery}
                    deliveryServers={deliveryServers}
                    isDeliveryServerSelected={isDeliveryServerSelected}
                    toggleDeliveryServer={toggleDeliveryServer}
                    projectType={projectType}
                  />
                )}

                {/* Deployment Configuration */}
                {requiresDeployment && (
                  <DeploymentConfig
                    control={form.control}
                    openshiftServers={openshiftServers}
                    isServerSelected={isServerSelected}
                    toggleServer={toggleServer}
                  />
                )}

                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? 'Creating Project...' : 'Create Project'}
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>

      {/* Success Dialog */}
      <ProjectSuccessDialog
        open={showSuccess}
        onOpenChange={setShowSuccess}
        createdProject={createdProject}
        onCopyToClipboard={copyToClipboard}
      />
    </div>
  );
};

export default CreateProject;