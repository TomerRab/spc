import { Control, UseFormWatch } from 'react-hook-form';
import { Checkbox } from '@/components/ui/checkbox';
import { FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { GroupSelector } from './GroupSelector';
import { ServerSelection } from './ServerSelection';
import { ProjectForm } from '@/schemas/projectSchema';
import { GitLabGroup } from '@/types/gitlab';

interface DeliveryConfigProps {
  control: Control<ProjectForm>;
  watch: UseFormWatch<ProjectForm>;
  groups: GitLabGroup[];
  loadingGroups: boolean;
  searchTerm: string;
  searchError: string;
  groupOpen: boolean;
  onSearchChange: (value: string) => void;
  onOpenChange: (open: boolean) => void;
  createDelivery: boolean;
  deliveryServers: Record<string, { namespace: string }>;
  isDeliveryServerSelected: (serverId: string) => boolean;
  toggleDeliveryServer: (serverId: string, checked: boolean) => void;
  projectType: string;
}

export const DeliveryConfig = ({
  control,
  watch,
  groups,
  loadingGroups,
  searchTerm,
  searchError,
  groupOpen,
  onSearchChange,
  onOpenChange,
  createDelivery,
  deliveryServers,
  isDeliveryServerSelected,
  toggleDeliveryServer,
  projectType
}: DeliveryConfigProps) => {
  if (projectType !== 'microservice') return null;

  return (
    <div key={`microservice-delivery-${projectType}`} className="space-y-4">
      <FormField
        control={control}
        name="deliveryConfig.createDelivery"
        render={({ field }) => (
          <FormItem className="flex flex-row items-start space-x-3 space-y-0">
            <FormControl>
              <Checkbox
                checked={field.value}
                onCheckedChange={field.onChange}
              />
            </FormControl>
            <div className="space-y-1 leading-none">
              <FormLabel className="font-semibold">
                Create delivery repository
              </FormLabel>
              <FormDescription>
                Create a delivery repository in another group for deploying this microservice
              </FormDescription>
            </div>
          </FormItem>
        )}
      />

      {createDelivery && (
        <div className="ml-6 space-y-4 border-l-2 border-muted pl-4">
          <FormField
            control={control}
            name="deliveryConfig.deliveryGroupId"
            render={({ field }) => (
              <GroupSelector
                groups={groups}
                loadingGroups={loadingGroups}
                searchTerm={searchTerm}
                searchError={searchError}
                groupOpen={groupOpen}
                selectedGroupId={field.value || 0}
                onSearchChange={onSearchChange}
                onGroupSelect={field.onChange}
                onOpenChange={onOpenChange}
                label="Delivery Group"
                description="Select the group where the delivery repository will be created"
                placeholder="Search and select delivery group..."
              />
            )}
          />

          <FormField
            control={control}
            name="deliveryConfig.deliveryName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Delivery Repository Name</FormLabel>
                <FormControl>
                  <Input 
                    placeholder={`${watch('name') || 'project'}-delivery`} 
                    {...field} 
                  />
                </FormControl>
                <FormDescription>
                  Name for the delivery repository (defaults to project-name-delivery)
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="space-y-4">
            <h4 className="text-md font-medium">Delivery Deployment Configuration</h4>
            <p className="text-sm text-muted-foreground">
              Select servers and namespaces for the delivery repository.
            </p>
            
            <div className="space-y-6">
              <ServerSelection
                control={control}
                serverIds={['a', 'b']}
                title="Production Environments"
                titleColor="text-orange-600"
                isServerSelected={isDeliveryServerSelected}
                toggleServer={toggleDeliveryServer}
                fieldPrefix="deliveryConfig.deliveryServers"
              />

              <ServerSelection
                control={control}
                serverIds={['c', 'd']}
                title="Test/Staging Environments"
                titleColor="text-blue-600"
                isServerSelected={isDeliveryServerSelected}
                toggleServer={toggleDeliveryServer}
                fieldPrefix="deliveryConfig.deliveryServers"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};