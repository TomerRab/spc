import { Control } from 'react-hook-form';
import { ServerSelection } from './ServerSelection';
import { ProjectForm } from '@/schemas/projectSchema';

interface DeploymentConfigProps {
  control: Control<ProjectForm>;
  openshiftServers: Record<string, { namespace: string }>;
  isServerSelected: (serverId: string) => boolean;
  toggleServer: (serverId: string, checked: boolean) => void;
}

export const DeploymentConfig = ({
  control,
  openshiftServers,
  isServerSelected,
  toggleServer
}: DeploymentConfigProps) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium">Deployment Configuration</h3>
      <p className="text-sm text-muted-foreground">
        Select the deployment servers and provide a namespace for each.
      </p>
      
      <div className="space-y-6">
        {/* Production Servers */}
        <ServerSelection
          control={control}
          serverIds={['a', 'b']}
          title="Production Environments"
          titleColor="text-orange-600"
          isServerSelected={isServerSelected}
          toggleServer={toggleServer}
          fieldPrefix="openshiftServers"
        />

        {/* Test/Staging Servers */}
        <ServerSelection
          control={control}
          serverIds={['c', 'd']}
          title="Test/Staging Environments"
          titleColor="text-blue-600"
          isServerSelected={isServerSelected}
          toggleServer={toggleServer}
          fieldPrefix="openshiftServers"
        />
      </div>
    </div>
  );
};