import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { type LucideIcon } from "lucide-react";
import { FieldError } from "react-hook-form";
import { FormErrorMessage } from "./FormErrorMessage";

type Props = {
  id: string;
  label: string;
  placeholder?: string;
  type?: string;
  icon: LucideIcon;
  error?: FieldError;
  registerProps: any;
};

export function FormFieldWithIcon({ id, label, placeholder, type = "text", icon: Icon, error, registerProps }: Props) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{label}</Label>
      <div className="relative">
        <Icon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
        <Input id={id} placeholder={placeholder} type={type} className="pl-10" {...registerProps} />
      </div>
      <FormErrorMessage error={error} />
    </div>
  );
}
