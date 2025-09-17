import { FormControl, FormDescription, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TECHNOLOGY_STACKS } from '@/config/project';

interface TechnologyStackSelectorProps {
  value?: string;
  onChange: (value: string) => void;
}

export const TechnologyStackSelector = ({ value, onChange }: TechnologyStackSelectorProps) => {
  const selectedStack = TECHNOLOGY_STACKS.find(s => s.id === value);

  return (
    <FormItem>
      <FormLabel>Technology Stack</FormLabel>
      <Select onValueChange={onChange} value={value}>
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
        {selectedStack?.description}
      </FormDescription>
      <FormMessage />
    </FormItem>
  );
};