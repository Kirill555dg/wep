import { Label } from "@/shared/ui/label";
import { RadioGroup, RadioGroupItem } from "@/shared/ui/radio-group";
import { FormErrorMessage } from "./FormErrorMessage";
import { FieldError } from "react-hook-form";

type Option = {
  label: string;
  value: string;
};

interface Props {
  label: string;
  name: string;
  value: string;
  error?: FieldError;
  options: Option[];
  onChange: (value: string) => void;
}

export function RadioButtonGroup({ label, name, value, error, options, onChange }: Props) {
  return (
    <div className="space-y-2">
      <Label className="block">{label}</Label>
      <RadioGroup value={value} onValueChange={onChange} className="flex gap-6" name={name}>
        {options.map((opt) => (
          <label key={opt.value} className="flex items-center space-x-2">
            <RadioGroupItem value={opt.value} id={`${name}-${opt.value}`} />
            <span>{opt.label}</span>
          </label>
        ))}
      </RadioGroup>
      <FormErrorMessage error={error} />
    </div>
  );
}
