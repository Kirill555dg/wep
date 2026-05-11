import { Controller } from "react-hook-form";
import { Checkbox } from "@/shared/ui/checkbox";
import { Label } from "@/shared/ui/label";

type Props = {
  name: string;
  control: any;
  label: string;
};

export function FormCheckbox({ name, control, label }: Props) {
  return (
    <div className="flex items-center space-x-2">
      <Controller
        name={name}
        control={control}
        render={({ field }) => <Checkbox id={name} checked={field.value} onCheckedChange={field.onChange} />}
      />
      <Label htmlFor={name} className="text-sm cursor-pointer">
        {label}
      </Label>
    </div>
  );
}
