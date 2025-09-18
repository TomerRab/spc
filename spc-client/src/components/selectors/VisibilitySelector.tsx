import { useMemo } from 'react';
import { FormControl, FormDescription, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { GitLabGroup } from '@/types/gitlab';

interface VisibilitySelectorProps {
  value: string;
  onChange: (value: string) => void;
  selectedGroup?: GitLabGroup;
}

export const VisibilitySelector = ({ value, onChange, selectedGroup }: VisibilitySelectorProps) => {
  const availableVisibilityOptions = useMemo(() => {
    const options = ['private'];
    
    // Only allow internal if the group is not private
    if (selectedGroup && selectedGroup.visibility !== 'private') {
      options.push('internal');
    }
    
    return options;
  }, [selectedGroup]);

  return (
    <FormItem>
      <FormLabel>Project Visibility</FormLabel>
      <Select onValueChange={onChange} value={value}>
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
  );
};