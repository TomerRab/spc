import { Checkbox } from '@/components/ui/checkbox';
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { DEPLOYMENT_SERVERS } from '@/config/project';
import { Control, Path } from 'react-hook-form';
import { ProjectForm } from '@/schemas/projectSchema';

interface ServerSelectionProps {
  control: Control<ProjectForm>;
  serverIds: string[];
  title: string;
  titleColor: string;
  isServerSelected: (serverId: string) => boolean;
  toggleServer: (serverId: string, checked: boolean) => void;
  fieldPrefix: 'openshiftServers' | 'deliveryConfig.deliveryServers';
}

export const ServerSelection = ({
  control,
  serverIds,
  title,
  titleColor,
  isServerSelected,
  toggleServer,
  fieldPrefix
}: ServerSelectionProps) => {
  return (
    <div className="space-y-3">
      <h5 className={`text-sm font-medium ${titleColor}`}>{title}</h5>
      {DEPLOYMENT_SERVERS.filter(server => serverIds.includes(server.id)).map((server) => (
        <div key={server.id} className="space-y-2">
          <div className="flex items-center space-x-2">
            <Checkbox
              id={`server-${server.id}-${fieldPrefix}`}
              checked={isServerSelected(server.id)}
              onCheckedChange={(checked) => toggleServer(server.id, checked as boolean)}
            />
            <Label htmlFor={`server-${server.id}-${fieldPrefix}`}>
              {server.label}
              <span className="ml-2 text-xs text-muted-foreground">
                ({server.description})
              </span>
            </Label>
          </div>
          
          {isServerSelected(server.id) && (
            <FormField
              control={control}
              name={`${fieldPrefix}.${server.id}.namespace` as Path<ProjectForm>}
              render={({ field }) => (
                <FormItem className="ml-6">
                  <FormLabel>Namespace for {server.label}</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder={
                        server.defaultNamespacePrefix 
                          ? `${server.defaultNamespacePrefix}-your-project` 
                          : `${server.id}-namespace`
                      } 
                      {...field} 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          )}
        </div>
      ))}
    </div>
  );
};