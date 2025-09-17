import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from '@/components/ui/form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { gitlabApi } from '@/lib/api';
import { GitLabGroup, GitLabProject } from '@/types/gitlab';
import { config } from '@/config/env';
import { PROJECT_TYPES, TECHNOLOGY_STACKS, DEPLOYMENT_SERVERS, getProjectTypeById } from '@/config/project';
import { ArrowLeft, GitBranch, Check, ChevronsUpDown, ExternalLink, Copy } from 'lucide-react';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { cn } from '@/lib/utils';
import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import debounce from 'lodash.debounce';

const projectSchema = z.object({
  name: z.string().min(1, 'Project name is required'),
  groupId: z.number().min(1, 'Group selection is required'),
  projectType: z.string().min(1, 'Project type is required'),
  stack: z.string().optional(),
  visibility: z.enum(['private', 'internal']).default('private'),
  defaultBranch: z.string().default('main'),
  openshiftServers: z.record(z.object({ 
    namespace: z.string().min(1, 'Namespace is required') 
  })).optional(),
  deliveryConfig: z.object({
    createDelivery: z.boolean().default(false),
    deliveryGroupId: z.number().optional(),
    deliveryName: z.string().optional(),
    deliveryServers: z.record(z.object({ 
      namespace: z.string().min(1, 'Namespace is required') 
    })).optional(),
  }).optional(),
});

type ProjectForm = z.infer<typeof projectSchema>;

const CreateProject = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { credentials, logout } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [groups, setGroups] = useState<GitLabGroup[]>([]);
  const [loadingGroups, setLoadingGroups] = useState(false);
  const [groupOpen, setGroupOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);
  const [createdProject, setCreatedProject] = useState<any>(null);
  const [searchError, setSearchError] = useState<string>('');
  const searchCache = useRef<Record<string, GitLabGroup[]>>({});

  const form = useForm<ProjectForm>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      name: '',
      groupId: 0,
      projectType: PROJECT_TYPES[0].id,
      stack: undefined, // Explicitly set as undefined instead of empty string
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

  // Use useWatch for more reliable reactivity
  const projectType = useWatch({ control: form.control, name: 'projectType' });
  const selectedGroupId = useWatch({ control: form.control, name: 'groupId' });
  const openshiftServers = useWatch({ control: form.control, name: 'openshiftServers' }) || {};
  const deliveryConfig = useWatch({ control: form.control, name: 'deliveryConfig' });
  const createDelivery = deliveryConfig?.createDelivery || false;
  const deliveryServers = deliveryConfig?.deliveryServers || {};
  
  const selectedProjectType = getProjectTypeById(projectType);
  const requiresStack = selectedProjectType?.requiresStack ?? false;
  const requiresDeployment = selectedProjectType?.requiresDeployment ?? false;
  
  // Find selected group and determine available visibility options
  const selectedGroup = useMemo(() => {
    return groups.find(group => group.id === selectedGroupId);
  }, [groups, selectedGroupId]);
  
  const availableVisibilityOptions = useMemo(() => {
    const options = ['private'];
    
    // Only allow internal if the group is not private
    if (selectedGroup && selectedGroup.visibility !== 'private') {
      options.push('internal');
    }
    
    return options;
  }, [selectedGroup]);
  
  // State to track if we should show delivery options
  const [showDeliveryOptions, setShowDeliveryOptions] = useState(
    PROJECT_TYPES[0].id === 'microservice'
  );
  
  // Update showDeliveryOptions when projectType changes
  useEffect(() => {
    const shouldShow = projectType === 'microservice';
    setShowDeliveryOptions(shouldShow);
  }, [projectType]);

  // Reset delivery config when project type changes away from microservice
  useEffect(() => {
    if (projectType !== 'microservice') {
      form.setValue('deliveryConfig.createDelivery', false);
      form.setValue('deliveryConfig.deliveryGroupId', 0);
      form.setValue('deliveryConfig.deliveryName', '');
      form.setValue('deliveryConfig.deliveryServers', {});
    }
  }, [projectType, form]);

  // Reset visibility to private if the selected group is private and current visibility is internal
  useEffect(() => {
    const currentVisibility = form.getValues('visibility');
    if (selectedGroup?.visibility === 'private' && currentVisibility === 'internal') {
      form.setValue('visibility', 'private');
    }
  }, [selectedGroup, form]);

  const isServerSelected = (serverKey: string) => {
    return !!openshiftServers[serverKey];
  };

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

  const isDeliveryServerSelected = (serverKey: string) => {
    return !!deliveryServers[serverKey];
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


  // Debounced search function
  const debouncedSearch = useMemo(
    () => debounce(async (query: string) => {
      if (!credentials) return;
      
      const trimmedQuery = query.trim();
      
      // Clear results if query is too short
      if (trimmedQuery.length < 3) {
        setGroups([]);
        setSearchError('');
        setLoadingGroups(false);
        return;
      }

      // Check local cache first
      if (searchCache.current[trimmedQuery]) {
        setGroups(searchCache.current[trimmedQuery]);
        setSearchError('');
        setLoadingGroups(false);
        return;
      }

      setLoadingGroups(true);
      setSearchError('');
      
      try {
        const results = await gitlabApi.searchGroups(credentials, trimmedQuery);
        setGroups(results);
        // Cache the results
        searchCache.current[trimmedQuery] = results;
        
        if (results.length === 0) {
          setSearchError('No groups found matching your search');
        }
      } catch (error) {
        console.error('Failed to search groups:', error);
        setSearchError('Failed to search groups. Please try again.');
        setGroups([]);
        toast({
          title: 'Search failed',
          description: 'Unable to search groups. Please check your connection.',
          variant: 'destructive',
        });
      } finally {
        setLoadingGroups(false);
      }
    }, 300),
    [credentials, toast]
  );

  // Handle search input changes
  const handleSearchChange = useCallback((value: string) => {
    setSearchTerm(value);
    debouncedSearch(value);
  }, [debouncedSearch]);

  // Clean up debounce on unmount
  useEffect(() => {
    return () => {
      debouncedSearch.cancel();
    };
  }, [debouncedSearch]);

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


  useEffect(() => {
    if (!credentials) {
      navigate('/');
      return;
    }
    // No longer loading groups on mount - they load on search
  }, [credentials, navigate]);


  const onSubmit = async (data: ProjectForm) => {
    if (!credentials) return;
    
    setIsLoading(true);
    try {
      // Filter out servers without namespaces and ensure namespace is not empty
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



      // Create new project
      const projectData = {
        name: data.name,
        groupId: data.groupId,
        projectType: data.projectType,
        stack: data.stack || undefined, // Ensure we don't send empty strings
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

                <FormField
                  control={form.control}
                  name="groupId"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>GitLab Group</FormLabel>
                      <Popover open={groupOpen} onOpenChange={setGroupOpen}>
                        <PopoverTrigger asChild>
                          <FormControl>
                            <Button
                              variant="outline"
                              role="combobox"
                              aria-expanded={groupOpen}
                              className={cn(
                                "w-full justify-between",
                                !field.value && "text-muted-foreground"
                              )}
                              disabled={loadingGroups}
                            >
                              {field.value
                                ? groups.find((group) => group.id === field.value)?.full_path
                                : loadingGroups ? "Searching groups..." : "Type to search groups..."
                              }
                              <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                            </Button>
                          </FormControl>
                        </PopoverTrigger>
                        <PopoverContent className="w-full p-0">
                          <Command>
                            <CommandInput 
                              placeholder="Type at least 3 characters to search..." 
                              value={searchTerm}
                              onValueChange={handleSearchChange}
                            />
                            <CommandList>
                              <CommandEmpty>
                                {loadingGroups ? (
                                  <div className="flex items-center justify-center p-4">
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                                    <span className="ml-2">Searching groups...</span>
                                  </div>
                                ) : searchTerm.length < 3 ? (
                                  "Type at least 3 characters to search groups"
                                ) : searchError ? (
                                  searchError
                                ) : (
                                  "No groups found matching your search"
                                )}
                              </CommandEmpty>
                              <CommandGroup>
                                {groups.map((group) => (
                                  <CommandItem
                                    key={group.id}
                                    value={group.full_path}
                                    onSelect={() => {
                                      field.onChange(group.id);
                                      setGroupOpen(false);
                                      setSearchTerm('');
                                    }}
                                  >
                                    <Check
                                      className={cn(
                                        "mr-2 h-4 w-4",
                                        field.value === group.id ? "opacity-100" : "opacity-0"
                                      )}
                                    />
                                    {group.full_path}
                                  </CommandItem>
                                ))}
                              </CommandGroup>
                            </CommandList>
                          </Command>
                        </PopoverContent>
                      </Popover>
                      <FormDescription>
                        Type at least 3 characters to search your accessible GitLab groups.
                      </FormDescription>  
                      <FormMessage />
                    </FormItem>
                  )}
                />


                <FormField
                  control={form.control}
                  name="projectType"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Project Type</FormLabel>
                      <FormControl>
                        <RadioGroup
                          onValueChange={field.onChange}
                          value={field.value}
                          className="grid grid-cols-2 gap-4"
                        >
                          {PROJECT_TYPES.map((type) => (
                            <div key={type.id} className="flex items-center space-x-2">
                              <RadioGroupItem value={type.id} id={type.id} />
                              <Label htmlFor={type.id}>{type.label}</Label>
                            </div>
                          ))}
                        </RadioGroup>
                      </FormControl>
                      <FormDescription>
                        {selectedProjectType?.description}
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {requiresStack && (
                  <FormField
                    control={form.control}
                    name="stack"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Technology Stack</FormLabel>
                        <Select onValueChange={field.onChange} value={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select technology stack" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {TECHNOLOGY_STACKS.map((stack) => (
                              <SelectItem key={stack.id} value={stack.id}>
                                {stack.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormDescription>
                          {field.value && TECHNOLOGY_STACKS.find(s => s.id === field.value)?.description}
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                )}

                <FormField
                  control={form.control}
                  name="visibility"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Project Visibility</FormLabel>
                      <Select onValueChange={field.onChange} value={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select visibility" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="private">Private</SelectItem>
                          {availableVisibilityOptions.includes('internal') && (
                            <SelectItem value="internal">Internal</SelectItem>
                          )}
                        </SelectContent>
                      </Select>
                      <FormDescription>
                        {selectedGroup?.visibility === 'private' && (
                          <span className="text-amber-600">
                            Internal visibility not available for private groups
                          </span>
                        )}
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />


                {showDeliveryOptions && (
                  <div key={`microservice-delivery-${projectType}`} className="space-y-4">
                    <FormField
                      control={form.control}
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
                          control={form.control}
                          name="deliveryConfig.deliveryGroupId"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Delivery Group</FormLabel>
                              <Popover>
                                <PopoverTrigger asChild>
                                  <FormControl>
                                    <Button
                                      variant="outline"
                                      role="combobox"
                                      className={cn(
                                        "w-full justify-between",
                                        !field.value && "text-muted-foreground"
                                      )}
                                    >
                                      {field.value
                                        ? groups.find((group) => group.id === field.value)?.full_path
                                        : "Search and select delivery group..."
                                      }
                                      <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                                    </Button>
                                  </FormControl>
                                </PopoverTrigger>
                                <PopoverContent className="w-full p-0">
                                  <Command>
                                    <CommandInput 
                                      placeholder="Type at least 3 characters to search..." 
                                      value={searchTerm}
                                      onValueChange={handleSearchChange}
                                    />
                                    <CommandList>
                                      <CommandEmpty>
                                        {loadingGroups ? (
                                          <div className="flex items-center justify-center p-4">
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                                            <span className="ml-2">Searching groups...</span>
                                          </div>
                                        ) : searchTerm.length < 3 ? (
                                          "Type at least 3 characters to search groups"
                                        ) : searchError ? (
                                          searchError
                                        ) : (
                                          "No groups found matching your search"
                                        )}
                                      </CommandEmpty>
                                      <CommandGroup>
                                        {groups.map((group) => (
                                          <CommandItem
                                            key={group.id}
                                            value={group.full_path}
                                            onSelect={() => {
                                              field.onChange(group.id);
                                            }}
                                          >
                                            <Check
                                              className={cn(
                                                "mr-2 h-4 w-4",
                                                field.value === group.id ? "opacity-100" : "opacity-0"
                                              )}
                                            />
                                            {group.full_path}
                                          </CommandItem>
                                        ))}
                                      </CommandGroup>
                                    </CommandList>
                                  </Command>
                                </PopoverContent>
                              </Popover>
                              <FormDescription>
                                Select the group where the delivery repository will be created
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        <FormField
                          control={form.control}
                          name="deliveryConfig.deliveryName"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Delivery Repository Name</FormLabel>
                              <FormControl>
                                <Input 
                                  placeholder={`${form.watch('name') || 'project'}-delivery`} 
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
                          <p className="text-sm text-muted-foreground">Select servers and namespaces for the delivery repository.</p>
                          
                          <div className="space-y-6">
                            {/* Production Servers */}
                            <div className="space-y-3">
                              <h5 className="text-sm font-medium text-orange-600">Production Environments</h5>
                              {DEPLOYMENT_SERVERS.filter(server => ['a', 'b'].includes(server.id)).map((server) => (
                                <div key={server.id} className="space-y-2">
                                  <div className="flex items-center space-x-2">
                                    <Checkbox
                                      id={`delivery-server-${server.id}`}
                                      checked={isDeliveryServerSelected(server.id)}
                                      onCheckedChange={(checked) => toggleDeliveryServer(server.id, checked as boolean)}
                                    />
                                    <Label htmlFor={`delivery-server-${server.id}`}>
                                      {server.label}
                                      <span className="ml-2 text-xs text-muted-foreground">
                                        ({server.description})
                                      </span>
                                    </Label>
                                  </div>
                                  
                                  {isDeliveryServerSelected(server.id) && (
                                    <FormField
                                      control={form.control}
                                      name={`deliveryConfig.deliveryServers.${server.id}.namespace`}
                                      render={({ field }) => (
                                        <FormItem className="ml-6">
                                          <FormLabel>Namespace for {server.label}</FormLabel>
                                          <FormControl>
                                            <Input 
                                              placeholder={server.defaultNamespacePrefix ? `${server.defaultNamespacePrefix}-your-project` : `${server.id}-namespace`} 
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

                            {/* Test/Staging Servers */}
                            <div className="space-y-3">
                              <h5 className="text-sm font-medium text-blue-600">Test/Staging Environments</h5>
                              {DEPLOYMENT_SERVERS.filter(server => ['c', 'd'].includes(server.id)).map((server) => (
                                <div key={server.id} className="space-y-2">
                                  <div className="flex items-center space-x-2">
                                    <Checkbox
                                      id={`delivery-server-${server.id}`}
                                      checked={isDeliveryServerSelected(server.id)}
                                      onCheckedChange={(checked) => toggleDeliveryServer(server.id, checked as boolean)}
                                    />
                                    <Label htmlFor={`delivery-server-${server.id}`}>
                                      {server.label}
                                      <span className="ml-2 text-xs text-muted-foreground">
                                        ({server.description})
                                      </span>
                                    </Label>
                                  </div>
                                  
                                  {isDeliveryServerSelected(server.id) && (
                                    <FormField
                                      control={form.control}
                                      name={`deliveryConfig.deliveryServers.${server.id}.namespace`}
                                      render={({ field }) => (
                                        <FormItem className="ml-6">
                                          <FormLabel>Namespace for {server.label}</FormLabel>
                                          <FormControl>
                                            <Input 
                                              placeholder={server.defaultNamespacePrefix ? `${server.defaultNamespacePrefix}-your-project` : `${server.id}-namespace`} 
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
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}



                {requiresDeployment && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Deployment Configuration</h3>
                    <p className="text-sm text-muted-foreground">Select the deployment servers and provide a namespace for each.</p>
                    
                    <div className="space-y-6">
                      {/* Production Servers */}
                      <div className="space-y-3">
                        <h4 className="text-md font-medium text-orange-600">Production Environments</h4>
                        {DEPLOYMENT_SERVERS.filter(server => ['a', 'b'].includes(server.id)).map((server) => (
                          <div key={server.id} className="space-y-2">
                            <div className="flex items-center space-x-2">
                              <Checkbox
                                id={`server-${server.id}`}
                                checked={isServerSelected(server.id)}
                                onCheckedChange={(checked) => toggleServer(server.id, checked as boolean)}
                              />
                              <Label htmlFor={`server-${server.id}`}>
                                {server.label}
                                <span className="ml-2 text-xs text-muted-foreground">
                                  ({server.description})
                                </span>
                              </Label>
                            </div>
                            
                            {isServerSelected(server.id) && (
                              <FormField
                                control={form.control}
                                name={`openshiftServers.${server.id}.namespace`}
                                render={({ field }) => (
                                  <FormItem className="ml-6">
                                    <FormLabel>Namespace for {server.label}</FormLabel>
                                    <FormControl>
                                      <Input 
                                        placeholder={server.defaultNamespacePrefix ? `${server.defaultNamespacePrefix}-your-project` : `${server.id}-namespace`} 
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

                      {/* Test/Staging Servers */}
                      <div className="space-y-3">
                        <h4 className="text-md font-medium text-blue-600">Test/Staging Environments</h4>
                        {DEPLOYMENT_SERVERS.filter(server => ['c', 'd'].includes(server.id)).map((server) => (
                          <div key={server.id} className="space-y-2">
                            <div className="flex items-center space-x-2">
                              <Checkbox
                                id={`server-${server.id}`}
                                checked={isServerSelected(server.id)}
                                onCheckedChange={(checked) => toggleServer(server.id, checked as boolean)}
                              />
                              <Label htmlFor={`server-${server.id}`}>
                                {server.label}
                                <span className="ml-2 text-xs text-muted-foreground">
                                  ({server.description})
                                </span>
                              </Label>
                            </div>
                            
                            {isServerSelected(server.id) && (
                              <FormField
                                control={form.control}
                                name={`openshiftServers.${server.id}.namespace`}
                                render={({ field }) => (
                                  <FormItem className="ml-6">
                                    <FormLabel>Namespace for {server.label}</FormLabel>
                                    <FormControl>
                                      <Input 
                                        placeholder={server.defaultNamespacePrefix ? `${server.defaultNamespacePrefix}-your-project` : `${server.id}-namespace`} 
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
                    </div>
                  </div>
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
      <Dialog open={showSuccess} onOpenChange={setShowSuccess}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-green-600">
              <Check className="h-6 w-6" />
              Project Created Successfully! 🎉
            </DialogTitle>
            <DialogDescription>
              Your project has been created with all the necessary templates and configurations.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Project Summary */}
            {createdProject?.summary && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-green-600 font-medium">{createdProject.summary.message}</span>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                  <div>Repositories: <span className="font-medium">{createdProject.summary.repos_created}</span></div>
                  <div>Files Created: <span className="font-medium">{createdProject.summary.total_files}</span></div>
                  {createdProject.summary.environments && (
                    <div className="col-span-2">
                      Environments: <span className="font-medium">{createdProject.summary.environments.join(', ')}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Repository Links */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Repository Links</h3>
              
              {createdProject?.primary_repos ? (
                createdProject.primary_repos.map((repo: any, index: number) => (
                  <div key={index} className="border rounded-lg p-6 bg-white shadow-sm">
                    <div className="flex items-center gap-3 mb-3">
                      <h4 className="text-xl font-semibold">{repo.title}</h4>
                    </div>
                    <p className="text-gray-600 mb-4">{repo.description}</p>
                    
                    <div className="space-y-3">
                      <div className="flex items-center gap-3 flex-wrap">
                        <Button asChild className="bg-blue-600 hover:bg-blue-700">
                          <a 
                            href={repo.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="flex items-center gap-2"
                          >
                            <ExternalLink className="h-4 w-4" />
                            Open Repository
                          </a>
                        </Button>
                        <span className="text-sm text-gray-500">({repo.action_text})</span>
                      </div>
                      
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <label className="text-sm font-medium text-gray-700">Clone Command:</label>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => copyToClipboard(repo.clone_command)}
                            className="flex items-center gap-1"
                          >
                            <Copy className="h-3 w-3" />
                            Copy
                          </Button>
                        </div>
                        <code className="block bg-gray-100 p-3 rounded text-sm font-mono break-all">
                          {repo.clone_command}
                        </code>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                // Fallback for old API response format
                createdProject?.repositories?.map((repo: any, index: number) => (
                  <div key={index} className="border rounded-lg p-6 bg-white shadow-sm">
                    <div className="flex items-center gap-3 mb-3">
                      <h4 className="text-lg font-semibold">{repo.name}</h4>
                    </div>
                    <div className="flex items-center gap-3">
                      <Button asChild className="bg-blue-600 hover:bg-blue-700">
                        <a 
                          href={repo.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="flex items-center gap-2"
                        >
                          <ExternalLink className="h-4 w-4" />
                          Open Repository
                        </a>
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Next Steps */}
            {createdProject?.next_steps && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-800 mb-2">Next Steps:</h4>
                <ol className="list-decimal list-inside space-y-1 text-sm text-blue-700">
                  {createdProject.next_steps.map((step: string, index: number) => (
                    <li key={index}>{step}</li>
                  ))}
                </ol>
              </div>
            )}
          </div>

          <div className="flex justify-end mt-6">
            <Button onClick={() => setShowSuccess(false)} className="px-8">
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CreateProject;