import { FieldError } from "react-hook-form";

type Props = {
  error?: FieldError;
};

export function FormErrorMessage({ error }: Props) {
  if (!error?.message) return null;

  return <p className="text-sm text-red-600">{error.message}</p>;
}
