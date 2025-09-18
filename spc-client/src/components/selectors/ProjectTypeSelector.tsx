import { FormControl, FormDescription, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { PROJECT_TYPES, getProjectTypeById } from '@/config/project';

interface ProjectTypeSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export const ProjectTypeSelector = ({ value, onChange }: ProjectTypeSelectorProps) => {
  const selectedProjectType = getProjectTypeById(value);

  return (
    <FormItem>
      <FormLabel>Project Type</FormLabel>
      <FormControl>
        <RadioGroup
          onValueChange={onChange}
          value={value}
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
  );
};