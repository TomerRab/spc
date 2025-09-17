import { Check, ChevronsUpDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { FormControl, FormDescription, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command';
import { cn } from '@/lib/utils';
import { GitLabGroup } from '@/types/gitlab';

interface GroupSelectorProps {
  groups: GitLabGroup[];
  loadingGroups: boolean;
  searchTerm: string;
  searchError: string;
  groupOpen: boolean;
  selectedGroupId: number;
  onSearchChange: (value: string) => void;
  onGroupSelect: (groupId: number) => void;
  onOpenChange: (open: boolean) => void;
  label?: string;
  description?: string;
  placeholder?: string;
}

export const GroupSelector = ({
  groups,
  loadingGroups,
  searchTerm,
  searchError,
  groupOpen,
  selectedGroupId,
  onSearchChange,
  onGroupSelect,
  onOpenChange,
  label = "GitLab Group",
  description = "Type at least 3 characters to search your accessible GitLab groups.",
  placeholder = "Type to search groups..."
}: GroupSelectorProps) => {
  return (
    <FormItem>
      <FormLabel>{label}</FormLabel>
      <Popover open={groupOpen} onOpenChange={onOpenChange}>
        <PopoverTrigger asChild>
          <FormControl>
            <Button
              variant="outline"
              role="combobox"
              aria-expanded={groupOpen}
              className={cn(
                "w-full justify-between",
                !selectedGroupId && "text-muted-foreground"
              )}
              disabled={loadingGroups}
            >
              {selectedGroupId
                ? groups.find((group) => group.id === selectedGroupId)?.full_path
                : loadingGroups ? "Searching groups..." : placeholder
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
              onValueChange={onSearchChange}
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
                    onSelect={() => onGroupSelect(group.id)}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        selectedGroupId === group.id ? "opacity-100" : "opacity-0"
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
      <FormDescription>{description}</FormDescription>
      <FormMessage />
    </FormItem>
  );
};